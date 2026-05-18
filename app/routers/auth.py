from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.token import Token
from app.utils.hashing import verify_password
from app.utils.jwt import create_access_token
from app.utils.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=token, token_type="bearer")


from app.utils.redis import get_verification_code, delete_verification_code
from app.models.user import User


@router.post("/verify-email")
def verify_email(email: str, code: str, db: Session = Depends(get_db)):
    stored_code = get_verification_code(email)

    if not stored_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code expired or not found"
        )

    if stored_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_verified = True
    db.commit()

    delete_verification_code(email)

    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(email: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )

    from app.utils.redis import set_verification_code
    from app.utils.email import send_verification_email
    from app.routers.user import generate_verification_code

    code = generate_verification_code()
    set_verification_code(email=email, code=code)

    background_tasks.add_task(
        send_verification_email,
        email=user.email,
        username=user.username,
        code=code
    )

    return {"message": "Verification code resent"}