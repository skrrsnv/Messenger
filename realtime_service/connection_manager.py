from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(
        self,
        conversation_id: int,
        websocket: WebSocket,
    ):
        await websocket.accept()

        self.active_connections.setdefault(
            conversation_id,
            [],
        ).append(websocket)

    def disconnect(
        self,
        conversation_id: int,
        websocket: WebSocket,
    ):
        connections = self.active_connections.get(
            conversation_id,
            [],
        )

        if websocket in connections:
            connections.remove(websocket)

        if not connections:
            self.active_connections.pop(
                conversation_id,
                None,
            )