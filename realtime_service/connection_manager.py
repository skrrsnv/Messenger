from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}
        self.connection_users: dict[WebSocket, int] = {}
        self.typing_users: dict[int, set[int]] = {}

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
            
    def set_typing(
        self,
        conversation_id: int,
        user_id: int,
        is_typing: bool,
    ):
        users = self.typing_users.setdefault(
            conversation_id,
            set(),
        )

        if is_typing:
            users.add(user_id)
        else:
            users.discard(user_id)

        if not users:
            self.typing_users.pop(conversation_id, None)

    def clear_typing_on_disconnect(
        self,
        conversation_id: int,
        websocket: WebSocket,
    ) -> int | None:
        user_id = self.connection_users.get(websocket)

        if user_id is None:
            return None

        other_connections = [
            connection
            for connection in self.active_connections.get(
                conversation_id, []
            )
            if connection is not websocket
            and self.connection_users.get(connection) == user_id
        ]

        if other_connections:
            return None

        users = self.typing_users.get(conversation_id, set())

        if user_id in users:
            users.discard(user_id)

            if not users:
                self.typing_users.pop(conversation_id, None)

            return user_id

        return None
    
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