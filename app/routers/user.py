from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User
from app.utils.hashing import hash_password
from app.utils.dependencies import get_db
from app.utils.email import send_verification_email
from app.utils.redis import set_verification_code
import random

router = APIRouter(prefix="/users", tags=["Users"])


def generate_verification_code() -> str:
    return str(random.randint(100000, 999999))


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
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

    background_tasks.add_task(
        send_verification_email,
        email=new_user.email,
        username=new_user.username,
        code=code
    )

    return new_user