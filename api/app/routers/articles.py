from openai import OpenAI
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy import select, and_, or_
from sqlalchemy.future import select
from typing import Optional
from datetime import date
import boto3
from botocore.exceptions import ClientError
from starlette.concurrency import run_in_threadpool
from ..config import settings
from ..database import AsyncSessionLocal
from ..models import Article
from ..schemas import (
    ArticleCreate,
    ArticleResponse,
    ArticleContentResponse,
    PaginatedArticles,
    ArticleSearchResult,
    PaginatedArticleSearchResults
)
import gzip

# Generate embeddings per chunk
client = OpenAI(api_key=settings.OPENAI_API_KEY)
embedding_model = "text-embedding-3-small"

router = APIRouter()

# Initialize the S3 client at module level (ensure your settings has the AWS credentials and bucket)
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

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


@router.get("/{article_id:int}", response_model=ArticleResponse)
async def get_article(article_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.get("/{article_id:int}/s3", response_model=ArticleContentResponse)
async def fetch_article_from_s3(article_id: int, db: AsyncSession = Depends(get_db)):
    """
    Fetch an article object from AWS S3 using the provided article_key.
    Expects the article object to be stored as JSON in S3.
    """
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    article_s3_url = article.article_s3_url
    if not article_s3_url:
        raise HTTPException(status_code=404, detail="Article has no s3 object stored")
    
    bucket_name = article_s3_url.split("/")[2]
    file_key = "/".join(article_s3_url.split("/")[3:])

    try:
        # Wrap the blocking S3 call inside a synchronous function
        def fetch():
            response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
            # Read the response body and decode from bytes to a UTF-8 string
            with gzip.GzipFile(fileobj=response["Body"]) as f:
                raw_content = f.read().decode("utf-8")
            return raw_content
        
        # Run the blocking call in a thread pool
        content = await run_in_threadpool(fetch)

        return {
            "text": content
        }

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == "NoSuchKey":
            raise HTTPException(status_code=404, detail="Article not found in S3")
        else:
            raise HTTPException(status_code=500, detail=f"Error fetching article: {e}")

@router.get("/search_by_similarity", response_model=PaginatedArticleSearchResults)
async def search_articles_by_similarity(
    db: AsyncSession = Depends(get_db),
    # Paginations
    page: int = Query(1, ge=1, description="Page number, must be >= 1"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    # Filters
    q: str = Query(..., description="Query text to embed for similarity search"),
):
    """
    Retrieve a paginated, list of articles by similarity
    """

    # 1) Generate embedding for the user query
    response = client.embeddings.create(input=q, model=embedding_model)
    query_embedding = response.data[0].embedding  # list of floats

    stmt = (
        select(
            Article,
            # Label distance so we can return it if we want
            (Article.embedding.cosine_distance(query_embedding)).label("distance")
        )
        .order_by("distance")  # ascending distance => most similar first
    )

    # Pagination offset
    offset = (page - 1) * page_size

    # Count total
    total_stmt = select(func.count(Article.id))
    total_count = await db.scalar(total_stmt)

    # Fetch subset
    stmt = stmt.offset(offset).limit(page_size)
    results = await db.execute(stmt)
    rows = results.all()  # each row: (Article, distance)

    items = []
    for (article, distance) in rows:
       items.append(
           ArticleSearchResult(
               article=ArticleResponse.from_orm(article),
               distance=distance
            )
        ) 
       
    return {
        "items": items,
        "total": total_count,
        "page": page,
        "page_size": page_size,
    } 