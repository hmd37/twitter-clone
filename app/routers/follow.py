from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.follow import Follow
from app.models.tweet import Tweet
from app.models.user import User
from app.schemas.follow import FollowResponse, FollowStatsResponse
from app.schemas.tweet import TweetResponse
from app.utils.dependencies import get_current_user, get_db, require_current_user

router = APIRouter(tags=["Follows"])


@router.post("/users/{username}/follow", status_code=status.HTTP_204_NO_CONTENT)
def follow_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user)
):
    target = db.query(User).filter(User.username == username).first()

    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if target.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot follow yourself")

    already_following = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == target.id
    ).first()

    if already_following:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already following this user")

    follow = Follow(follower_id=current_user.id, following_id=target.id)
    db.add(follow)
    db.commit()


@router.delete("/users/{username}/follow", status_code=status.HTTP_204_NO_CONTENT)
def unfollow_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user)
):
    target = db.query(User).filter(User.username == username).first()

    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == target.id
    ).first()

    if not follow:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not following this user")

    db.delete(follow)
    db.commit()


@router.get("/users/{username}/following", response_model=list[FollowResponse])
def get_following(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user.following


@router.get("/users/{username}/followers", response_model=list[FollowResponse])
def get_followers(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user.followers


@router.get("/users/{username}/stats", response_model=FollowStatsResponse)
def get_follow_stats(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return FollowStatsResponse(
        username=user.username,
        following_count=len(user.following),
        followers_count=len(user.followers)
    )


@router.get("/feed", response_model=list[TweetResponse])
def get_feed(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    following_ids = [u.id for u in current_user.following]

    if not following_ids:
        return []

    tweets = (
        db.query(Tweet)
        .filter(Tweet.user_id.in_(following_ids))
        .order_by(Tweet.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return tweets