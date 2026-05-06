from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.tweet import Tweet
from app.models.user import User
from app.schemas.tweet import TweetCreate, TweetResponse
from app.utils.dependencies import get_db, get_current_user

router = APIRouter(prefix="/tweets", tags=["Tweets"])


@router.post("/", response_model=TweetResponse, status_code=status.HTTP_201_CREATED)
def create_tweet(
    tweet_data: TweetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if len(tweet_data.content) > 280:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tweet cannot exceed 280 characters"
        )

    tweet = Tweet(content=tweet_data.content, user_id=current_user.id)
    db.add(tweet)
    db.commit()
    db.refresh(tweet)

    return tweet


@router.get("/", response_model=list[TweetResponse])
def get_tweets(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    tweets = db.query(Tweet).order_by(Tweet.created_at.desc()).offset(skip).limit(limit).all()
    return tweets


@router.get("/{tweet_id}", response_model=TweetResponse)
def get_tweet(tweet_id: int, db: Session = Depends(get_db)):
    tweet = db.query(Tweet).filter(Tweet.id == tweet_id).first()

    if not tweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found"
        )

    return tweet


@router.delete("/{tweet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tweet(
    tweet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tweet = db.query(Tweet).filter(Tweet.id == tweet_id).first()

    if not tweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found"
        )

    if tweet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own tweets"
        )

    db.delete(tweet)
    db.commit()