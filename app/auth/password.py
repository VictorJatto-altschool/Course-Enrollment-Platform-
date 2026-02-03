from passlib.context import CryptContext

import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


_COMMON_PASSWORDS = {
    "password",
    "password123",
    "12345678",
    "qwerty123",
    "letmein",
    "admin123",
}


def validate_password_strength(password: str) -> None:
    """Raise ValueError if the password is too weak.

    Policy:
    - at least 8 characters
    - at least one lowercase, one uppercase, one digit, one symbol
    - no whitespace
    - not a common password
    """

    if password is None:
        raise ValueError("Password is required")

    if any(ch.isspace() for ch in password):
        raise ValueError("Password must not contain whitespace")

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")

    if password.lower() in _COMMON_PASSWORDS:
        raise ValueError("Password is too common")

    if re.search(r"[a-z]", password) is None:
        raise ValueError("Password must include a lowercase letter")
    if re.search(r"[A-Z]", password) is None:
        raise ValueError("Password must include an uppercase letter")
    if re.search(r"\d", password) is None:
        raise ValueError("Password must include a number")
    if re.search(r"[^A-Za-z0-9]", password) is None:
        raise ValueError("Password must include a symbol")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
