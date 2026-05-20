import random

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.tasks.email_tasks import send_verification_email_task
from app.utils.dependencies import get_db
from app.utils.hashing import hash_password
from app.utils.redis import set_verification_code

router = APIRouter(prefix="/users", tags=["Users"])


def generate_verification_code() -> str:
    return str(random.randint(100000, 999999))


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(User)
        .filter((User.username == user_data.username) | (User.email == user_data.email))
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    code = generate_verification_code()
    set_verification_code(email=new_user.email, code=code)

    send_verification_email_task.delay(
        email=new_user.email, username=new_user.username, code=code
    )

    return new_user
