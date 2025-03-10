"""
schemas.py
----------
Defines Pydantic models (schemas) for request and response validation.
"""

from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

"""
------------------------------------------------------------------------------
    articles
------------------------------------------------------------------------------
"""
class ArticleCreate(BaseModel):
    # unchanged from before
    display_datetime: Optional[datetime] = None
    last_modified_datetime: Optional[datetime] = None
    publish_datetime: Optional[datetime] = None
    create_datetime: Optional[datetime] = None
    content_vertical: Optional[str] = None
    og_description: Optional[str] = None
    content_type: Optional[str] = None
    page_url: Optional[str] = None
    og_title: Optional[str] = None
    content_title: Optional[str] = None
    og_site_name: Optional[str] = None
    tags: Optional[str] = None
    authors: Optional[str] = None
    content_tier: Optional[str] = None
    article_s3_url: Optional[str] = None

class ArticleResponse(ArticleCreate):
    id: int

    class Config:
        orm_mode = True

class PaginatedArticles(BaseModel):
    """
    Generic pagination schema for listing Articles.
    """
    items: list[ArticleResponse]
    total: int               # total number of items
    page: int                # current page number
    page_size: int           # items per page
"""
------------------------------------------------------------------------------
    articles search
------------------------------------------------------------------------------
"""
class ArticleSearchResult(BaseModel):
    article: ArticleResponse
    distance: float


class PaginatedArticleSearchResults(BaseModel):

    items: List[ArticleSearchResult]
    total: int
    page: int
    page_size: int
"""
------------------------------------------------------------------------------
    article_chunks
------------------------------------------------------------------------------
"""
class ArticleChunkCreate(BaseModel):
    """
    Schema for creating a new article chunk.
    """
    article_id: int
    chunk_text: str
    token_size: int
    # embedding is typically generated asynchronously, so you may or may not allow it directly in create

class ArticleChunkResponse(ArticleChunkCreate):
    """
    Schema for reading article chunk data.
    Includes the ID and possibly the embedding if you want to expose it.
    """
    id: int

    class Config:
        orm_mode = True

class PaginatedArticleChunks(BaseModel):
    """
    A paginated response schema for listing article chunks.
    """
    items: List[ArticleChunkResponse]
    total: int
    page: int
    page_size: int


"""
------------------------------------------------------------------------------
    article_chunks search 
------------------------------------------------------------------------------
"""

class ArticleChunkSearchResult(BaseModel):
    chunk: ArticleChunkResponse
    distance: float

class ArticleChunkSearchResponse(BaseModel):
    query: str
    top_k: int
    results: List[ArticleChunkSearchResult]
    
    class Config:
        orm_mode = True

class PaginatedArticleChunkSearchResults(BaseModel):

    items: List[ArticleChunkSearchResult]
    total: int
    page: int
    page_size: int