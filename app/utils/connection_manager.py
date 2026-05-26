import json
import os

import redis.asyncio as aioredis
from dotenv import load_dotenv
from fastapi import WebSocket

load_dotenv()

REDIS_URL = f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/2"


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

    async def publish(self, user_id: int, message: dict):
        async with aioredis.from_url(REDIS_URL) as r:
            await r.publish(f"user:{user_id}", json.dumps(message))

    async def subscribe(self, user_id: int):
        async with aioredis.from_url(REDIS_URL) as r:
            pubsub = r.pubsub()
            await pubsub.subscribe(f"user:{user_id}")
            print(f"subscribed to channel user:{user_id}")
            async for raw in pubsub.listen():
                if raw["type"] == "message":
                    message = json.loads(raw["data"])
                    await self.send_to_user(user_id, message)


manager = ConnectionManager()