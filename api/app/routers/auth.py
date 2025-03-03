"""
auth.py
-------
Authentication-related endpoints (login, signup, token generation, etc.).
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from ..core.security import create_access_token

router = APIRouter()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    An example login endpoint that returns a JWT token upon valid credentials.
    In a real app, you'd verify the user from the database first.
    """
    username = form_data.username
    password = form_data.password

    # Example logic (this should be replaced with real credential checks):
    if username == "admin" and password == "pass":
        # Create token
        access_token = create_access_token({"sub": username})
        return {"access_token": access_token, "token_type": "bearer"}

    # If invalid credentials
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )
