from utils.ArticleProcessor import ArticleProcessor
from utils.PGManager import PGManager
from utils.S3Manager import S3Manager
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI
import os
import gzip
load_dotenv()
# ----------------------- Example Usage -----------------------

def format_datetime(dt: datetime) -> str:
    return dt.strftime("%B %-dth, %Y, %-I:%M%p %Z").lower()

if __name__ == "__main__":


    # Replace these parameters with your database credentials.
    db = PGManager(
        host=os.getenv("POSTGRES_HOST"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=5432
    )

    try:
        # Connect to the database.
        db.connect()

        # # delete article_chunks
        # db.delete("article_chunks", {"article"})
        create_chunks_sql = """
        CREATE TABLE IF NOT EXISTS article_chunks (
            id SERIAL PRIMARY KEY,
            article_id INTEGER NOT NULL REFERENCES articles(id),
            chunk_text TEXT NOT NULL,
            token_size INTEGER NOT NULL,
            embedding vector(1536) NOT NULL,
            UNIQUE (article_id, chunk_text, token_size)
        );
        """
        db.execute(create_chunks_sql)

        s3_client = S3Manager(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name="us-west-1"
        )
        statement = """
            SELECT id, article_s3_url, content_title, publish_datetime, og_description FROM articles 
            WHERE article_s3_url IS NOT NULL 
            AND embedding IS NOT NULL
            AND EXTRACT(YEAR FROM publish_datetime) = 2025
            ORDER BY publish_datetime DESC;
        """
        articles = db.query(query=statement)
        # print(len(articles))
        for article in articles:
            print(f'Loading sentence embedding for: {article["id"]}')
            # print(format_datetime(article["publish_datetime"]))
            article_s3_url = article["article_s3_url"]
            # Extract bucket and key from the S3 URL
            bucket_name = article_s3_url.split("/")[2]
            file_key = "/".join(article_s3_url.split("/")[3:])

            # Download and extract content
            response = s3_client.s3_client.get_object(Bucket=bucket_name, Key=file_key)
            with gzip.GzipFile(fileobj=response["Body"]) as f:
                raw_content = f.read().decode("utf-8")

        
            # Create an instance of the ArticleProcessor with the desired token limits.
            processor = ArticleProcessor(lower_bound=50, upper_bound=200)
        
            # Step 1: Clean the raw article text.
            cleaned_article = processor.clean_article_text(raw_content)
        
            # Step 2: Split the cleaned article into individual sentences.
            sentences = processor.split_into_sentences(cleaned_article)
            
            # Step 3: Build text chunks from the list of sentences while ensuring balanced punctuation and token count constraints.
            chunks = processor.sentence_to_chunks(sentences)

            # Generate embeddings per chunk
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            response = client.embeddings.create(input=chunks, model="text-embedding-3-small")

            insert_sql = "INSERT INTO article_chunks (article_id, chunk_text, token_size, embedding) VALUES (%s, %s, %s, %s)"
            for chunk, item in zip(chunks, response.data):
                # print(chunk, item.embedding)
                data = { 
                    "article_id": article["id"],
                    "chunk_text": chunk,
                    "token_size": processor.token_count(chunk),
                    "embedding": item.embedding
                }
                try:
                    db.create(table="article_chunks", data=data)
                except:
                    print("didnt work")

            
            # db_chunks = db.read("article_chunks")
            # for row in db_chunks:
            #     print(row)
        

    finally:
        # Disconnect from the database.
        db.disconnect()
