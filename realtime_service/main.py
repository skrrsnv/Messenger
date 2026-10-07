from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


@app.websocket("/ws/chat/{conversation_id}/")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: int,
):
    await websocket.accept()

    print(
        f"Client connected to conversation {conversation_id}"
    )

    try:
        while True:
            message = await websocket.receive_text()

            print(
                f"Message in conversation {conversation_id}: {message}"
            )

    except WebSocketDisconnect:
        print(
            f"Client disconnected from conversation {conversation_id}"
        )