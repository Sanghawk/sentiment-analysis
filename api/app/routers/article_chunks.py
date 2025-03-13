from openai import OpenAI
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_, text
from datetime import date

from ..database import AsyncSessionLocal
from ..models import ArticleChunk
from ..schemas import (
    ArticleChunkCreate,
    ArticleChunkResponse,
    PaginatedArticleChunks,
    ArticleChunkSearchResult,
    ArticleChunkSearchResponse,
    PaginatedArticleChunkSearchResults
)
from ..config import settings
router = APIRouter()

# Generate embeddings per chunk
client = OpenAI(api_key=settings.OPENAI_API_KEY)
embedding_model = "text-embedding-3-small"

# Dependency: get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=ArticleChunkResponse)
async def create_article_chunk(
    chunk_data: ArticleChunkCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new article chunk in the database.
    """
    # If embedding is not provided in chunk_data, you might generate it or handle it in a separate flow
    new_chunk = ArticleChunk(**chunk_data.dict())
    db.add(new_chunk)
    await db.commit()
    await db.refresh(new_chunk)
    return new_chunk

@router.get("/{chunk_id:int}", response_model=ArticleChunkResponse)
async def get_article_chunk(
    chunk_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a single article chunk by ID.
    """
    result = await db.execute(select(ArticleChunk).where(ArticleChunk.id == chunk_id))
    chunk = result.scalar_one_or_none()
    if not chunk:
        raise HTTPException(status_code=404, detail="Article chunk not found")
    return chunk

@router.get("/", response_model=PaginatedArticleChunks)
async def list_article_chunks(
    db: AsyncSession = Depends(get_db),
    # Pagination
    page: int = Query(1, ge=1, description="Page number, must be >= 1"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    # Filters
    article_id: Optional[int] = Query(None, description="Filter by article_id"),
    min_token_size: Optional[int] = Query(None, description="Filter by minimum token size"),
    max_token_size: Optional[int] = Query(None, description="Filter by maximum token size"),
    chunk_text: Optional[str] = Query(None, description="Partial match on chunk_text"),
    # Sorting
    sort_by: Optional[str] = Query(
        None, 
        regex="^(id|article_id|token_size)$",
        description="Sort by: id, article_id, or token_size"
    ),
    order: Optional[str] = Query(
        None,
        regex="^(asc|desc)$",
        description="Sorting order: asc or desc"
    )
):
    """
    Retrieve a paginated, filterable, and sortable list of article chunks.
    """
    stmt = select(ArticleChunk)
    conditions = []

    # Build filter conditions
    if article_id is not None:
        conditions.append(ArticleChunk.article_id == article_id)
    if min_token_size is not None:
        conditions.append(ArticleChunk.token_size >= min_token_size)
    if max_token_size is not None:
        conditions.append(ArticleChunk.token_size <= max_token_size)
    if chunk_text:
        conditions.append(ArticleChunk.chunk_text.ilike(f"%{chunk_text}%"))

    # Apply filtering
    if conditions:
        stmt = stmt.where(and_(*conditions))

    # Sorting logic
    if sort_by is not None:
        sort_column_map = {
            "id": ArticleChunk.id,
            "article_id": ArticleChunk.article_id,
            "token_size": ArticleChunk.token_size,
        }
        sort_column = sort_column_map[sort_by]
        if order == "desc":
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())

    # Pagination offset
    offset = (page - 1) * page_size

    # Count total
    total_stmt = select(func.count(ArticleChunk.id))
    if conditions:
        total_stmt = total_stmt.where(and_(*conditions))
    total_count = await db.scalar(total_stmt)

    # Fetch subset
    stmt = stmt.offset(offset).limit(page_size)
    results = await db.execute(stmt)
    chunks = results.scalars().all()

    return {
        "items": chunks,
        "total": total_count,
        "page": page,
        "page_size": page_size,
    }

@router.get("/search_by_similarity", response_model=PaginatedArticleChunkSearchResults)
async def search_chunks_by_similarity(
    db: AsyncSession = Depends(get_db),
    # Pagination
    page: int = Query(1, ge=1, description="Page number, must be >= 1"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    # Filters
    q: str = Query(..., description="Query text to embed for similarity search"),
    article_id: Optional[int] = Query(None, description="Filter by article_id"),
):
    """
    Retrieve a paginated list of article chunks by similarity
    """
    # 1) Generate embedding for the user query
    response = client.embeddings.create(input=q, model=embedding_model)
    query_embedding = response.data[0].embedding  # list of floats

    # 2) Build the query with similarity calculation
    stmt = (
        select(
            ArticleChunk,
            (ArticleChunk.embedding.cosine_distance(query_embedding)).label("distance")
        )
        .order_by("distance")  # ascending distance => most similar first
    )

    # 3) Conditionally add the filter if article_id is provided
    if article_id is not None:
        stmt = stmt.where(ArticleChunk.article_id == article_id)

    # 4) Calculate pagination offset
    offset = (page - 1) * page_size

    # 5) Count total matching items, applying the same filter if necessary
    total_stmt = select(func.count(ArticleChunk.id))
    if article_id is not None:
        total_stmt = total_stmt.where(ArticleChunk.article_id == article_id)
    total_count = await db.scalar(total_stmt)

    # 6) Apply pagination limits
    stmt = stmt.offset(offset).limit(page_size)
    results = await db.execute(stmt)
    rows = results.all()  # each row: (ArticleChunk, distance)

    # 7) Build response items
    items = [
        ArticleChunkSearchResult(
            chunk=ArticleChunkResponse.from_orm(chunk),
            distance=distance
        )
        for chunk, distance in rows
    ]

    return {
        "items": items,
        "total": total_count,
        "page": page,
        "page_size": page_size,
    }
