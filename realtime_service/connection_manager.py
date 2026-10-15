from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}
        self.connection_users: dict[WebSocket, int] = {}

    async def connect(
        self,
        conversation_id: int,
        websocket: WebSocket,
        user_id: int,
    ):
        await websocket.accept()

        self.active_connections.setdefault(
            conversation_id,
            [],
        ).append(websocket)
        
        self.connection_users[websocket] = user_id

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
            
        self.connection_users.pop(websocket, None)

        if not connections:
            self.active_connections.pop(
                conversation_id,
                None,
            )
    
    async def broadcast_json(
        self,
        conversation_id: int,
        message: dict,
        exclude: WebSocket | None = None,
    ):
        connections = self.active_connections.get(
            conversation_id,
            [],
        )

        for websocket in connections.copy():
            if websocket is exclude:
                continue
            
            try:
                await websocket.send_json(message)
            except (WebSocketDisconnect, RuntimeError):
                self.disconnect(conversation_id, websocket)