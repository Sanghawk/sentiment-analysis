"""
models.py
---------
Contains SQLAlchemy models for database tables. Each class inherits from 'Base'.
"""

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, UniqueConstraint
from pgvector.sqlalchemy import Vector
from .database import Base

class Article(Base):
    """
    Represents an article in the 'articles' table.
    """
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    display_datetime = Column(DateTime, nullable=True)
    last_modified_datetime = Column(DateTime, nullable=True)
    publish_datetime = Column(DateTime, nullable=True)
    create_datetime = Column(DateTime, nullable=True)
    content_vertical = Column(Text, nullable=True)
    og_description = Column(Text, nullable=True)
    content_type = Column(Text, nullable=True)
    page_url = Column(Text, nullable=True)
    og_title = Column(Text, nullable=True)
    content_title = Column(Text, nullable=True)
    og_site_name = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)
    authors = Column(Text, nullable=True)
    content_tier = Column(Text, nullable=True)
    article_s3_url = Column(Text, nullable=True)
    embedding = Column(Vector(1536), nullable=True)

    # Additional columns and relationships can be added here as needed.

class ArticleChunk(Base):
    """
    Represents a chunk of an article, mapped to the article_chunks table.
    """
    __tablename__ = "article_chunks"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    token_size = Column(Integer, nullable=False)
    embedding = Column(Vector(1536), nullable=True)

    # The UNIQUE constraint (article_id, chunk_text, token_size) is defined at the DB level
    # but you could add a __table_args__ for it if you want:
    __table_args__ = (UniqueConstraint('article_id', 'chunk_text', 'token_size'),)