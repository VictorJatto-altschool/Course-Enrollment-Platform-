from typing import cast

from email_validator import EmailNotValidError, validate_email
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth.password import hash_password, verify_password
from app.models.user import User

def create_user(db: Session, name: str, email: str, password: str, role: str) -> User:
    try:
        # Avoid DNS deliverability checks; tests and offline environments should still work.
        email = validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Invalid email")

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    if role not in ["student", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    user = User(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email_or_username: str, password: str) -> User:
    # OAuth2PasswordRequestForm calls the identifier field "username".
    # In this app we use email as the identifier, so treat it as an email.
    try:
        email_or_username = validate_email(
            email_or_username,
            check_deliverability=False,
        ).normalized
    except EmailNotValidError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = db.query(User).filter(User.email == email_or_username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    is_active = cast(bool, user.is_active)
    if is_active is False:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    hashed_password = cast(str, user.hashed_password)
    if not verify_password(password, hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user
