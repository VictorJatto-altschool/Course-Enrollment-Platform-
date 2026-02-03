from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional

from app.auth.password import validate_password_strength

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str  # "student" or "admin"

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        validate_password_strength(value)
        return value

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str
