"""
main.py
-------
Entry point of the FastAPI application. It creates the FastAPI app instance,
includes routers, and starts the server. This file is referenced by uvicorn
when the container starts.
"""

from fastapi import FastAPI
from .routers import auth, articles

def create_app() -> FastAPI:
    """
    Application factory to create a FastAPI instance.
    """
    app = FastAPI(
        title="Crypto News Sentiment Analysis API",
        description="Provides endpoints to manage and retrieve crypto news articles, with sentiment analysis features.",
        version="1.0.0"
    )

    # Include your routers
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(articles.router, prefix="/articles", tags=["articles"])

    return app

# Create a global instance of the app
app = create_app()
