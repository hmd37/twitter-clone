from fastapi import Depends, FastAPI
from sqladmin import Admin

from app.admin import FollowAdmin, LikeAdmin, MessageAdmin, TweetAdmin, UserAdmin
from app.database import engine
from app.models.user import User
from app.routers import auth, chat, follow, like, tweet, user
from app.utils.dependencies import require_current_user

app = FastAPI(title="Twitter Clone")
admin = Admin(app, engine)

# setup admin
admin.add_view(UserAdmin)
admin.add_view(TweetAdmin)
admin.add_view(FollowAdmin)
admin.add_view(LikeAdmin)
admin.add_view(MessageAdmin)

# setup routers
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(tweet.router)
app.include_router(follow.router)
app.include_router(like.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"message": "Twitter Clone API"}


@app.get("/me")
def me(current_user: User = Depends(require_current_user)):
    return {"id": current_user.id, "username": current_user.username}
