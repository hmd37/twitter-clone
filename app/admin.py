from sqladmin import ModelView

from app.models.follow import Follow
from app.models.like import Like
from app.models.message import Message
from app.models.tweet import Tweet
from app.models.user import User


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.username,
        User.email,
        User.is_verified,
        User.is_active,
        User.created_at,
    ]


class TweetAdmin(ModelView, model=Tweet):
    column_list = [Tweet.id, Tweet.content, Tweet.user_id, Tweet.created_at]


class FollowAdmin(ModelView, model=Follow):
    column_list = [Follow.follower_id, Follow.following_id, Follow.created_at]


class LikeAdmin(ModelView, model=Like):
    column_list = [Like.user_id, Like.tweet_id, Like.created_at]


class MessageAdmin(ModelView, model=Message):
    column_list = [
        Message.id,
        Message.sender_id,
        Message.receiver_id,
        Message.content,
        Message.is_read,
        Message.created_at,
    ]
