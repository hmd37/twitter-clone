from pydantic import BaseModel


class FollowResponse(BaseModel):
    id: int
    username: str
    bio: str | None

    model_config = {"from_attributes": True}


class FollowStatsResponse(BaseModel):
    username: str
    following_count: int
    followers_count: int
