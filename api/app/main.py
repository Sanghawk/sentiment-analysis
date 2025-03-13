"""
main.py
-------
Entry point of the FastAPI application. It creates the FastAPI app instance,
includes routers, and starts the server. This file is referenced by uvicorn
when the container starts.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, articles, article_chunks


def create_app() -> FastAPI:
    """
    Application factory to create a FastAPI instance.
    """
    app = FastAPI(
        title="Crypto News Sentiment Analysis API",
        description="Provides endpoints to manage and retrieve crypto news articles, with sentiment analysis features.",
        version="1.0.0"
    )

    # Define the list of origins allowed to make requests.
    origins = [
        "http://localhost:3000",
        # Add other origins as needed.
    ]


    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,            # Allowed origins, or ["*"] to allow all origins.
        allow_credentials=True,           # Whether to allow cookies and authentication.
        allow_methods=["*"],              # Allows all HTTP methods.
        allow_headers=["*"],              # Allows all headers.
    )


    # Include your routers
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(articles.router, prefix="/articles", tags=["articles"])

    # Register the new article_chunks router
    app.include_router(article_chunks.router, prefix="/article_chunks", tags=["article_chunks"])

    return app

# Create a global instance of the app
app = create_app()
