from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.like import Like
from app.models.tweet import Tweet
from app.models.user import User
from app.utils.dependencies import get_current_user, get_db

router = APIRouter(tags=["Likes"])


@router.post("/tweets/{tweet_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def like_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tweet = db.query(Tweet).filter(Tweet.id == tweet_id).first()

    if not tweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tweet not found"
        )

    already_liked = (
        db.query(Like)
        .filter(Like.user_id == current_user.id, Like.tweet_id == tweet_id)
        .first()
    )

    if already_liked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already liked this tweet"
        )

    like = Like(user_id=current_user.id, tweet_id=tweet_id)
    db.add(like)
    db.commit()


@router.delete("/tweets/{tweet_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    like = (
        db.query(Like)
        .filter(Like.user_id == current_user.id, Like.tweet_id == tweet_id)
        .first()
    )

    if not like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not liked this tweet",
        )

    db.delete(like)
    db.commit()
