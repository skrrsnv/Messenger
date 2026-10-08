from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .auth import decode_access_token
from .connection_manager import ConnectionManager

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

    try:
        user_id = decode_access_token(token)
    except Exception:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, conversation_id)

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