import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.enums import UserRole

PHONE_PATTERN = re.compile(r"^\+?[0-9]{10,15}$")


def validate_password_strength(value: str) -> str:
    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[A-Za-z]", value):
        raise ValueError("Password must contain at least one letter")
    if not re.search(r"[0-9]", value):
        raise ValueError("Password must contain at least one digit")
    return value


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone_number: Optional[str] = None
    role: UserRole = UserRole.USER

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Full name cannot be empty")
        return v

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().replace(" ", "").replace("-", "")
        if not v:
            return None
        if not PHONE_PATTERN.match(v):
            raise ValueError("Phone number must be 10-15 digits (optional leading +)")
        return v


class UserRegister(UserBase):
    password: str = Field(..., max_length=64)

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        return validate_password_strength(v)


class UserUpdate(UserBase):
    """Profile update. Password is changed through its own endpoint."""


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class PasswordChange(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., max_length=64)

    @field_validator("new_password")
    @classmethod
    def check_password(cls, v: str) -> str:
        return validate_password_strength(v)


class UserResponse(BaseModel):
    """Never includes the password or its hash."""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    full_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    role: UserRole
    created_date: datetime


class LoginResponse(BaseModel):
    message: str
    user: UserResponse


class MessageResponse(BaseModel):
    message: str
