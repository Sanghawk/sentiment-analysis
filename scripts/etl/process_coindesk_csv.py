import os
import csv
# Increase CSV field size limit to handle large fields
csv.field_size_limit(2**31 - 1)
import logging
from datetime import datetime
import psycopg2
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv
import gzip

load_dotenv()

# ------------------------------------------------------------------------------
# Setup Logging
# ------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ------------------------------------------------------------------------------
# Configuration (edit these to match your environment)
# ------------------------------------------------------------------------------
CSV_FILE_PATH = './data/coindesk_sm_101-200.csv'

# AWS S3 configuration
S3_BUCKET_NAME = 'sentiment-articles'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION_NAME = 'us-west-1'  # or your AWS region

# PostgreSQL configuration
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')

# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------
def combine_date_time(date_str, time_str):
    """
    Combine a date string (yyyymmdd) and time string (HH:MM)
    into a Python datetime object.
    
    If either date_str or time_str is missing or invalid,
    return None to signify an invalid date.
    """
    try:
        if not date_str or not time_str:
            return None
        
        # Handle potential zero-padding or missing leading zeros
        date_str = date_str.strip()
        time_str = time_str.strip()
        
        # Convert yyyymmdd to yyyy-mm-dd (for easier parsing)
        formatted_date = f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}"
        
        # Combine and parse
        dt_str = f"{formatted_date} {time_str}"
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    except (ValueError, IndexError):
        logging.error(f"Invalid date/time format: '{date_str}', '{time_str}'")
        return None

def get_db_connection():
    """
    Create and return a new PostgreSQL database connection.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except psycopg2.Error as e:
        logging.error(f"Error connecting to PostgreSQL: {str(e)}")
        return None

def create_table_if_not_exists(conn):
    """
    Create the `articles` table if it does not already exist.
    Excluding the article_content column, but including article_s3_url.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS articles (
        id SERIAL PRIMARY KEY,
        display_datetime TIMESTAMP NULL,
        last_modified_datetime TIMESTAMP NULL,
        publish_datetime TIMESTAMP NULL,
        create_datetime TIMESTAMP NULL,
        content_vertical TEXT NULL,
        og_description TEXT NULL,
        content_type TEXT NULL,
        page_url TEXT NULL,
        og_title TEXT NULL,
        content_title TEXT NULL,
        og_site_name TEXT NULL,
        tags TEXT NULL,
        authors TEXT NULL,
        content_tier TEXT NULL,
        article_s3_url TEXT NULL
    );
    """
    try:
        with conn.cursor() as cur:
            cur.execute(create_table_query)
        conn.commit()
        logging.info("Table 'articles' ensured to exist.")
    except psycopg2.Error as e:
        logging.error(f"Error creating articles table: {str(e)}")
        conn.rollback()

def article_exists(conn, page_url):
    """
    Return True if an article with the given page_url already exists.
    """
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM articles WHERE page_url = %s", (page_url,))
            (count,) = cur.fetchone()
            return count > 0
    except psycopg2.Error as e:
        logging.error(f"Error checking existing article: {str(e)}")
        return False

def insert_article(conn, article_data):
    """
    Insert a single article row into the `articles` table.
    `article_data` is a dict with all relevant fields.
    """
    insert_query = """
    INSERT INTO articles (
        display_datetime,
        last_modified_datetime,
        publish_datetime,
        create_datetime,
        content_vertical,
        og_description,
        content_type,
        page_url,
        og_title,
        content_title,
        og_site_name,
        tags,
        authors,
        content_tier,
        article_s3_url
    )
    VALUES (%(display_datetime)s,
            %(last_modified_datetime)s,
            %(publish_datetime)s,
            %(create_datetime)s,
            %(content_vertical)s,
            %(og_description)s,
            %(content_type)s,
            %(page_url)s,
            %(og_title)s,
            %(content_title)s,
            %(og_site_name)s,
            %(tags)s,
            %(authors)s,
            %(content_tier)s,
            %(article_s3_url)s
    );
    """
    try:
        with conn.cursor() as cur:
            cur.execute(insert_query, article_data)
        conn.commit()
        logging.info(f"Inserted article: {article_data.get('og_title')} (URL: {article_data.get('page_url')})")
    except psycopg2.Error as e:
        logging.error(f"Error inserting article into PostgreSQL: {str(e)}")
        conn.rollback()

def upload_to_s3(article_content, publish_dt, content_id):
    """
    Compress the article_content text (via gzip) and upload to S3.
    Use a structured file path based on the publish date:
        s3://my-bucket/articles/YYYY/MM/DD/article_{content_id}.txt.gz
    
    Returns:
      - (s3_url, original_size, compressed_size)
      - (None, 0, 0) if there's nothing to upload or upload fails.
    """
    if not article_content:
        # Nothing to upload
        return None, 0, 0
    
    if not publish_dt:
        # If there's no publish_dt, we fallback to a default path
        publish_dt = datetime.now()
    
    # Construct S3 key (path)
    year_str = publish_dt.strftime('%Y')
    month_str = publish_dt.strftime('%m')
    day_str = publish_dt.strftime('%d')
    s3_key = f"articles/{year_str}/{month_str}/{day_str}/article_{content_id}.txt.gz"
    
    # Encode + compress the content
    original_bytes = article_content.encode('utf-8')
    compressed_content = gzip.compress(original_bytes)
    
    try:
        s3_client = boto3.client(
            's3',
            region_name=AWS_REGION_NAME,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=compressed_content,
            ContentType='text/plain',
            ContentEncoding='gzip'
        )
        
        s3_url = f"s3://{S3_BUCKET_NAME}/{s3_key}"
        return s3_url, len(original_bytes), len(compressed_content)
    
    except (BotoCoreError, ClientError) as e:
        logging.error(f"Failed to upload article content to S3: {str(e)}")
        return None, 0, 0

# ------------------------------------------------------------------------------
# Main Processing Function
# ------------------------------------------------------------------------------
def process_csv():
    conn = get_db_connection()
    if not conn:
        logging.error("Database connection not established. Exiting.")
        return
    
    # Ensure table exists
    create_table_if_not_exists(conn)

    total_uncompressed_size = 0
    total_compressed_size = 0

    with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        logging.info("Starting CSV processing...")

        for row_idx, row in enumerate(reader, start=1):
            try:
                content_id = row.get('content_id') or str(row_idx)
                page_url = row.get('page_url')
                
                # Skip if page_url is missing
                if not page_url:
                    logging.info(f"Row {row_idx}: Missing page_url, skipping...")
                    continue

                # -------------------------------------------------------------
                # Prevent duplicates by checking if this page_url already exists
                # -------------------------------------------------------------
                if article_exists(conn, page_url):
                    logging.info(f"Row {row_idx}: Duplicate page_url '{page_url}', skipping...")
                    continue

                # -------------------------------------------------------------
                # Combine date/time fields
                # -------------------------------------------------------------
                display_datetime = combine_date_time(row.get('display_date'), row.get('display_time'))
                last_modified_datetime = combine_date_time(row.get('last_modified_date'), row.get('last_modified_time'))
                publish_datetime = combine_date_time(row.get('publish_date'), row.get('publish_time'))
                create_datetime = combine_date_time(row.get('create_date'), row.get('create_time'))

                # -------------------------------------------------------------
                # Upload compressed content to S3
                # -------------------------------------------------------------
                article_content = row.get('article_content', '')
                s3_url, original_size, compressed_size = upload_to_s3(
                    article_content, 
                    publish_datetime, 
                    content_id
                )
                total_uncompressed_size += original_size
                total_compressed_size += compressed_size

                # -------------------------------------------------------------
                # Prepare data for insertion
                # -------------------------------------------------------------
                article_data = {
                    'display_datetime':       display_datetime,
                    'last_modified_datetime': last_modified_datetime,
                    'publish_datetime':       publish_datetime,
                    'create_datetime':        create_datetime,
                    'content_vertical':       row.get('content_vertical'),
                    'og_description':         row.get('og:description'),
                    'content_type':           row.get('content_type'),
                    'page_url':               page_url,
                    'og_title':               row.get('og:title'),
                    'content_title':          row.get('content_title'),
                    'og_site_name':           row.get('og:site_name'),
                    'tags':                   row.get('tags'),
                    'authors':                row.get('authors'),
                    'content_tier':           row.get('content_tier'),
                    'article_s3_url':         s3_url
                }

                insert_article(conn, article_data)

            except Exception as e:
                logging.error(f"Error processing row {row_idx}: {str(e)}")

    conn.close()
    logging.info("Finished processing CSV.")

    # ------------------------------------------------------------------------------
    # Show how much storage space was saved by using compression
    # ------------------------------------------------------------------------------
    if total_uncompressed_size > 0:
        bytes_saved = total_uncompressed_size - total_compressed_size
        pct_saved = (bytes_saved / total_uncompressed_size) * 100
        logging.info(
            f"Compression saved {bytes_saved} bytes "
            f"({pct_saved:.2f}% reduction) "
            f"out of {total_uncompressed_size} total bytes."
        )
    else:
        logging.info("No article content found; no compression savings to report.")

# ------------------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    process_csv()
