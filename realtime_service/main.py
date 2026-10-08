from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .connection_manager import ConnectionManager
from .django_client import is_conversation_member, validate_token

app = FastAPI()

manager = ConnectionManager()


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
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(conversation_id, websocket)

        print(
            f"User {user_id} disconnected "
            f"from conversation {conversation_id}"
        )