"""
schemas.py
----------
Defines Pydantic models (schemas) for request and response validation.
"""

from typing import Optional
from pydantic import BaseModel
from datetime import datetime

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