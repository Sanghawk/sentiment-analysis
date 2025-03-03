"""
database.py
-----------
Sets up the database engine and session for the FastAPI application using SQLAlchemy.
This example uses the async engine/session pattern introduced in SQLAlchemy 1.4+.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .config import settings

# For async connections, the URL scheme is usually 'postgresql+asyncpg://'
# If you're using the default psycopg, you might need 'postgresql+psycopg://'
# Make sure your DATABASE_URL matches the async driver if you want truly async DB operations
ASYNC_DB_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(ASYNC_DB_URL, echo=False)

# Create an async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    """
    Base declarative class for SQLAlchemy models to inherit from.
    """
    pass

async def init_db():
    """
    Utility function to initialize the database (create tables, if needed).
    Ideally used for migrations via Alembic, but can be used for quick setups.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
