from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UserModel
from app.schemas import LoginResponse, UserLogin, UserRegister, UserResponse
from app.security import DUMMY_HASH, hash_password, verify_password
from app.services import ensure_unique_email, get_user_by_email

router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    ensure_unique_email(db, payload.email)
    user = UserModel(
        full_name=payload.full_name,
        email=payload.email,
        phone_number=payload.phone_number,
        password_hash=hash_password(payload.password),
        role=payload.role.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=LoginResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)

    if user is None:
        # Do the same amount of work as a real check, so timing doesn't leak
        # whether the email exists.
        verify_password(payload.password, DUMMY_HASH)
        valid = False
    else:
        valid = verify_password(payload.password, user.password_hash)

    if not valid:
        # Same message for both cases: don't reveal which part was wrong.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return {"message": "Login successful", "user": user}
