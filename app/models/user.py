from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    bio: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    tweets: Mapped[list["Tweet"]] = relationship("Tweet", back_populates="author")  # type: ignore

    following: Mapped[list["User"]] = relationship(
        "User",
        secondary="followers",
        primaryjoin="User.id == Follow.follower_id",
        secondaryjoin="User.id == Follow.following_id",
        back_populates="followers",
    )
    followers: Mapped[list["User"]] = relationship(
        "User",
        secondary="followers",
        primaryjoin="User.id == Follow.following_id",
        secondaryjoin="User.id == Follow.follower_id",
        back_populates="following",
    )

    liked_tweets: Mapped[list["Tweet"]] = relationship(  # type: ignore
        "Tweet", secondary="likes", back_populates="liked_by"
    )
