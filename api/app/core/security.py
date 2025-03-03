"""
security.py
-----------
Contains utilities for handling JWT token creation and verification, as well
as password hashing and verification (if needed).
"""

import time
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from ..config import settings

# Create a password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Creates a JWT access token with an optional expiration time in minutes.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = int(time.time()) + (expires_delta * 60)
    else:
        expire = int(time.time()) + (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a given plain-text password against a stored hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Returns the bcrypt hash of the given password.
    """
    return pwd_context.hash(password)
