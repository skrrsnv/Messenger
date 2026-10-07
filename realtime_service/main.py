from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .connection_manager import ConnectionManager

app = FastAPI()

manager = ConnectionManager()


@app.websocket("/ws/conversations/{conversation_id}/")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: int,
):
    await manager.connect(
        conversation_id,
        websocket,
    )

    print(
        f"Client connected to conversation {conversation_id}"
    )

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(
            conversation_id,
            websocket,
        )

        print(
            f"Client disconnected from conversation {conversation_id}"
        )