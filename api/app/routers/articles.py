from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy import select, and_, or_
from sqlalchemy.future import select
from typing import Optional
from datetime import date

from ..config import settings
from ..database import AsyncSessionLocal
from ..models import Article
from ..schemas import (
    ArticleCreate,
    ArticleResponse,
    PaginatedArticles,
)

router = APIRouter()

# Dependency for getting DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/", response_model=PaginatedArticles)
async def list_articles(
    # Session
    db: AsyncSession = Depends(get_db),
    # Pagination
    page: int = Query(1, ge=1, description="Page number, must be >= 1"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    # Filters
    id: Optional[int] = Query(None, description="Filter by specific article ID"),
    content_title: Optional[str] = Query(None, description="Search by content title (partial match)"),
    og_title: Optional[str] = Query(None, description="Search by OG title (partial match)"),
    authors: Optional[str] = Query(None, description="Filter articles by author name"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated or partial match)"),
    content_vertical: Optional[str] = Query(None, description="Filter by content vertical"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    content_tier: Optional[str] = Query(None, description="Filter by content tier"),
    publish_date_from: Optional[date] = Query(None, description="Get articles published after this date"),
    publish_date_to: Optional[date] = Query(None, description="Get articles published before this date"),
    last_modified_from: Optional[date] = Query(None, description="Get articles modified after this date"),
    last_modified_to: Optional[date] = Query(None, description="Get articles modified before this date"),
    # Sorting
    sort_by: Optional[str] = Query(
        None,
        regex="^(publish_datetime|last_modified_datetime|content_title)$",
        description="Sort by: publish_datetime, last_modified_datetime, or content_title",
    ),
    order: Optional[str] = Query(
        None,
        regex="^(asc|desc)$",
        description="Sorting order: asc or desc"
    )
):
    """
    Retrieve a paginated, filterable list of articles.
    Supports many optional query parameters for filtering and sorting.
    """
    # Base query
    stmt = select(Article)

    # Build dynamic filter conditions
    conditions = []

    if id is not None:
        conditions.append(Article.id == id)
    if content_title:
        # partial match on content_title
        conditions.append(Article.content_title.ilike(f"%{content_title}%"))
    if og_title:
        conditions.append(Article.og_title.ilike(f"%{og_title}%"))
    if authors:
        # partial match on authors
        conditions.append(Article.authors.ilike(f"%{authors}%"))
    if tags:
        # Example approach (simple partial match) on tags column
        # For more advanced logic, parse tags and build multiple conditions
        conditions.append(Article.tags.ilike(f"%{tags}%"))
    if content_vertical:
        conditions.append(Article.content_vertical == content_vertical)
    if content_type:
        conditions.append(Article.content_type == content_type)
    if content_tier:
        conditions.append(Article.content_tier == content_tier)
    if publish_date_from:
        conditions.append(Article.publish_datetime >= publish_date_from)
    if publish_date_to:
        conditions.append(Article.publish_datetime <= publish_date_to)
    if last_modified_from:
        conditions.append(Article.last_modified_datetime >= last_modified_from)
    if last_modified_to:
        conditions.append(Article.last_modified_datetime <= last_modified_to)

    # Apply filtering
    if conditions:
        stmt = stmt.where(and_(*conditions))

    # Sorting logic
    if sort_by is not None:
        sort_column = {
            "publish_datetime": Article.publish_datetime,
            "last_modified_datetime": Article.last_modified_datetime,
            "content_title": Article.content_title,
        }[sort_by]

        if order == "desc":
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())

    # Calculate offset for pagination
    offset = (page - 1) * page_size

    # Count total
    total_stmt = select(func.count(Article.id))
    if conditions:
        total_stmt = total_stmt.where(and_(*conditions))
    total_count = await db.scalar(total_stmt)

    # Fetch subset of articles with offset/limit
    stmt = stmt.offset(offset).limit(page_size)
    results = await db.execute(stmt)
    articles = results.scalars().all()

    return {
        "items": articles,
        "total": total_count,
        "page": page,
        "page_size": page_size,
    }


@router.post("/", response_model=ArticleResponse)
async def create_article(article_data: ArticleCreate, db: AsyncSession = Depends(get_db)):
    new_article = Article(**article_data.dict())
    db.add(new_article)
    await db.commit()
    await db.refresh(new_article)
    return new_article


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
