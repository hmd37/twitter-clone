import redis
import os
from dotenv import load_dotenv

load_dotenv()

client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)


def set_verification_code(email: str, code: str, expiry_seconds: int = 900):
    key = f"verify:{email}"
    client.set(key, code, ex=expiry_seconds)


def get_verification_code(email: str) -> str | None:
    key = f"verify:{email}"
    return client.get(key)


def delete_verification_code(email: str):
    key = f"verify:{email}"
    client.delete(key)