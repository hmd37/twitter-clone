from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"user {user_id} connected. active: {list(self.active_connections.keys())}")

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)
        print(f"user {user_id} disconnected. active: {list(self.active_connections.keys())}")

    async def send_to_user(self, user_id: int, message: dict):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json(message)


manager = ConnectionManager()