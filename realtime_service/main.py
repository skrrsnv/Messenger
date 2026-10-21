import os
import redis.asyncio as redis
import asyncio
from contextlib import asynccontextmanager, suppress
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .connection_manager import ConnectionManager
from .django_client import (
    is_conversation_member,
    validate_token,
    create_message,
    get_user_conversation_ids,
    persist_last_seen,
)
from .redis_subscriber import redis_event_listener
from uuid import uuid4

from .presence import PresenceService


manager = ConnectionManager()

REDIS_URL = os.environ["REDIS_URL"]
CHANNEL = "chat.events"

async def publish_typing_event(
    client: redis.Redis,
    event_type: str,
    conversation_id: int,
    user_id: int,
):
    event = {
        "type": event_type,
        "conversation_id": conversation_id,
        "user_id": user_id,
    }

    await client.publish(
        CHANNEL,
        json.dumps(event),
    )
        


async def publish_presence_event(
    client: redis.Redis,
    user_id: int,
    status: str,
    conversation_ids: list[int],
    last_seen: str | None = None,
):
    for conversation_id in conversation_ids:
        event = {
            "type": "presence.update",
            "conversation_id": conversation_id,
            "user_id": user_id,
            "status": status,
            "last_seen": last_seen,
        }

        await client.publish(
            CHANNEL,
            json.dumps(event),
        )



@asynccontextmanager
async def lifespan(app: FastAPI):
    client = redis.from_url(
        REDIS_URL,
        decode_responses=True,
    )
    app.state.redis = client

    subscriber_task = asyncio.create_task(
        redis_event_listener(manager, client)
    )

    try:
        yield
    finally:
        subscriber_task.cancel()

        with suppress(asyncio.CancelledError):
            await subscriber_task

        await client.aclose()



app = FastAPI(lifespan=lifespan)


@app.websocket("/ws/conversations/{conversation_id}/")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: int,
):
    token = websocket.query_params.get("token")

    if token is None:
        await websocket.close(code=1008)
        return

    user_id = await validate_token(token)

    if user_id is None:
        await websocket.close(code=1008)
        return
    
    is_member = await is_conversation_member(
        conversation_id=conversation_id,
        user_id=user_id,
    )

    if not is_member:
        await websocket.close(code=1008)
        return
    
    client: redis.Redis = websocket.app.state.redis
    presence = PresenceService(client)
    connection_id = str(uuid4())

    await manager.connect(conversation_id, websocket, user_id)
    
    presence_registered = False

    try:
        became_online = await presence.connect(
            user_id,
            connection_id,
        )
        presence_registered = True

        if became_online:
            try:
                conversation_ids = await get_user_conversation_ids(
                    user_id
                )
                await publish_presence_event(
                    client=client,
                    user_id=user_id,
                    status="online",
                    conversation_ids=conversation_ids,
                )
            except Exception:
                import logging
                logging.getLogger(__name__).exception(
                    "Failed to publish online presence"
                )

        print(
            f"User {user_id} connected "
            f"to conversation {conversation_id}"
        )

        while True:
            raw_data = await websocket.receive_text()

            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "detail": "Invalid JSON.",
                })
                continue

            if not isinstance(data, dict):
                await websocket.send_json({
                    "type": "error",
                    "detail": "Event must be a JSON object.",
                })
                continue

            event_type = data.get("type")

            if event_type in ("typing.start", "typing.stop"):
                try:
                    manager.set_typing(
                        conversation_id,
                        user_id,
                        event_type == "typing.start",
                    )
                    await publish_typing_event(
                        client=client,
                        event_type=event_type,
                        conversation_id=conversation_id,
                        user_id=user_id,
                    )
                except Exception:
                    print("Error publishing typing event")
                    await websocket.send_json({
                        "type": "error",
                        "detail": "Unable to publish typing event.",
                    })

                continue

            if event_type == "message.send":
                text = data.get("text")

                if not isinstance(text, str) or not text.strip():
                    await websocket.send_json({
                        "type": "error",
                        "detail": "Message text cannot be empty.",
                    })
                    continue

                try:
                    message = await create_message(
                        conversation_id=conversation_id,
                        text=text,
                        user_access_token=token,
                    )
                except Exception:
                    print("Error communicating with Django")
                    await websocket.send_json({
                        "type": "error",
                        "detail": "Unable to save message.",
                    })
                    continue

                if message is None:
                    await websocket.send_json({
                        "type": "error",
                        "detail": "Unable to save message.",
                    })
                continue

            await websocket.send_json({
                "type": "error",
                "detail": "Unsupported event type.",
            })

    except WebSocketDisconnect:
        pass

    finally:
        try:
            typing_user_id = manager.clear_typing_on_disconnect(
                conversation_id,
                websocket,
            )

            manager.disconnect(conversation_id, websocket)

            if typing_user_id is not None:
                try:
                    await publish_typing_event(
                        client=client,
                        event_type="typing.stop",
                        conversation_id=conversation_id,
                        user_id=typing_user_id,
                    )
                except Exception:
                    print("Error publishing typing.stop on disconnect")

            if presence_registered:
                became_offline = await presence.disconnect(
                user_id,
                connection_id,
                )

                if became_offline:
                    try:
                        last_seen = await persist_last_seen(user_id)
                        conversation_ids = await get_user_conversation_ids(
                        user_id
                        )

                        await publish_presence_event(
                            client=client,
                            user_id=user_id,
                            status="offline",
                            conversation_ids=conversation_ids,
                            last_seen=last_seen,
                        )
                    except Exception:
                        import logging
                        logging.getLogger(__name__).exception(
                            "Failed to persist or publish offline presence"
                        )

        finally:
            manager.disconnect(conversation_id, websocket)

            print(
                f"User {user_id} disconnected "
                f"from conversation {conversation_id}"
            )
