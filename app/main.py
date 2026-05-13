from fastapi import Depends, FastAPI

from app.models.user import User
from app.routers import auth, follow, like, tweet, user
from app.utils.dependencies import get_current_user, require_current_user

app = FastAPI(title="Twitter Clone")

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(tweet.router)
app.include_router(follow.router)
app.include_router(like.router)


@app.get("/")
def root():
    return {"message": "Twitter Clone API"}


@app.get("/me")
def me(current_user: User = Depends(require_current_user)):
    return {"id": current_user.id, "username": current_user.username}
