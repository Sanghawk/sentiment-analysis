"""
config.py
---------
Manages the configuration of the FastAPI application, reading from environment
variables (e.g., .env file). This is helpful to keep secrets, DB URLs, etc. out
of the codebase.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Settings:
    """
    Settings class to store environment variables and other constants.
    """
    PROJECT_NAME: str = "crypto_sentiment"
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # e.g., 30 minutes
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")

settings = Settings()
