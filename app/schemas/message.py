from pydantic import BaseModel
from datetime import datetime


class MessageResponse(BaseModel):
    id: int
    content: str
    is_read: bool
    created_at: datetime
    sender_id: int
    receiver_id: int

    model_config = {"from_attributes": True}


class ConversationUser(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}