from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.enums import UserRole
from app.models import UserModel
from app.schemas import MessageResponse, PasswordChange, UserResponse, UserUpdate
from app.security import hash_password, verify_password
from app.services import ensure_unique_email, get_user_or_404

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserResponse])
def get_users(
    role: Optional[UserRole] = Query(default=None, description="Filter by role"),
    name: Optional[str] = Query(default=None, min_length=1, description="Search by name (partial, case-insensitive)"),
    db: Session = Depends(get_db),
):
    query = select(UserModel)
    if role is not None:
        query = query.where(UserModel.role == role.value)
    if name is not None:
        query = query.where(func.lower(UserModel.full_name).like(f"%{name.strip().lower()}%"))
    return db.scalars(query.order_by(UserModel.user_id)).all()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return get_user_or_404(db, user_id)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = get_user_or_404(db, user_id)
    ensure_unique_email(db, payload.email, exclude_id=user_id)
    user.full_name = payload.full_name
    user.email = payload.email
    user.phone_number = payload.phone_number
    user.role = payload.role.value
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}/password", response_model=MessageResponse)
def change_password(user_id: int, payload: PasswordChange, db: Session = Depends(get_db)):
    user = get_user_or_404(db, user_id)
    if not verify_password(payload.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Old password is incorrect",
        )
    if verify_password(payload.new_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the old password",
        )
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_or_404(db, user_id)
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully"}
