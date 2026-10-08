
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import UserModel


def get_user_or_404(db: Session, user_id: int) -> UserModel:
    user = db.get(UserModel, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    return user


def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
    return db.scalars(select(UserModel).where(UserModel.email == email.lower())).first()


def ensure_unique_email(db: Session, email: str, exclude_id: Optional[int] = None) -> None:
    query = select(UserModel).where(func.lower(UserModel.email) == email.lower())
    if exclude_id is not None:
        query = query.where(UserModel.user_id != exclude_id)
    if db.scalars(query).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{email}' is already registered",
        )
