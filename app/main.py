from fastapi import FastAPI, Depends
from app.database import engine, Base
from app.routers import user, auth, tweet
from app.utils.dependencies import get_current_user
from app.models.user import User

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Twitter Clone")

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(tweet.router)

@app.get("/")
def root():
    return {"message": "Twitter Clone API"}


@app.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username}
