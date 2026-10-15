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
)
from .redis_subscriber import redis_event_listener


manager = ConnectionManager()

REDIS_URL = os.environ["REDIS_URL"]
CHANNEL = "chat.events"

async def publish_typing_event(
    event_type: str,
    conversation_id: int,
    user_id: int,
):
    client = redis.from_url(
        REDIS_URL,
        decode_responses=True,
    )

    try:
        event = {
            "type": event_type,
            "conversation_id": conversation_id,
            "user_id": user_id,
        }

        await client.publish(
            CHANNEL,
            json.dumps(event),
        )
    finally:
        await client.aclose()
        

@asynccontextmanager
async def lifespan(app: FastAPI):
    subscriber_task = asyncio.create_task(
        redis_event_listener(manager)
    )

    try:
        yield
    finally:
        subscriber_task.cancel()

        with suppress(asyncio.CancelledError):
            await subscriber_task


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

    await manager.connect(conversation_id, websocket, user_id)

    print(
        f"User {user_id} connected "
        f"to conversation {conversation_id}"
    )
    
    
    try:
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
                    await publish_typing_event(
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

                continue

            await websocket.send_json({
                "type": "error",
                "detail": "Unsupported event type.",
            })

    except WebSocketDisconnect:
        pass

    finally:
        manager.disconnect(conversation_id, websocket)

        print(
            f"User {user_id} disconnected "
            f"from conversation {conversation_id}"
        )
