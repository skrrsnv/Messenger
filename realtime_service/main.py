import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .connection_manager import ConnectionManager
from .django_client import (
    is_conversation_member,
    validate_token,
    create_message,
)
from .redis_subscriber import redis_event_listener


manager = ConnectionManager()

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

    await manager.connect(conversation_id, websocket)

    print(
        f"User {user_id} connected "
        f"to conversation {conversation_id}"
    )

    try:
        while True:
            text = await websocket.receive_text()
            
            if not text.strip():
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

    except WebSocketDisconnect:
        pass

    finally:
        manager.disconnect(conversation_id, websocket)

        print(
            f"User {user_id} disconnected "
            f"from conversation {conversation_id}"
        )