from pydantic import BaseModel
from datetime import datetime


class TweetCreate(BaseModel):
    content: str


class TweetAuthor(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}


class TweetResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: TweetAuthor
    like_count: int
    is_liked: bool = False

    model_config = {"from_attributes": True}
