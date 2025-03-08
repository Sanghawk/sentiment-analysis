import pika
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import logging
import signal
from requests.adapters import HTTPAdapter, Retry
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv
import gzip
from datetime import datetime

# Import the PostgresManager class from the separate module
from PGManager.PGManager import PGManager

# Load environment variables from .env file
load_dotenv()

# Configure logging (this configuration applies to all modules)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# RabbitMQ setup
RABBITMQ_HOST = "rabbitmq"
QUEUE_NAME = "sitemap_links"

# Allowed domains
ALLOWED_DOMAINS = {"www.coindesk.com"}

# Configure session with retries
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))
session.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; CoinDeskCrawler/1.0; +https://www.example.com/bot-info)"
})

# Graceful shutdown flag and signal handler
should_exit = False
def signal_handler(sig, frame):
    global should_exit
    logging.info("Received shutdown signal. Exiting gracefully...")
    should_exit = True

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# AWS S3 configuration
S3_BUCKET_NAME = 'sentiment-articles'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION_NAME = 'us-west-1'  # or your AWS region

# PostgreSQL configuration
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')


# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------
def combine_date_time(date_str: str, time_str: str):
    """
    Combine a date string (yyyymmdd) and time string (HH:MM)
    into a Python datetime object.
    
    Returns None if either input is missing or improperly formatted.
    """
    try:
        if not date_str or not time_str:
            return None
        date_str = date_str.strip()
        time_str = time_str.strip()
        formatted_date = f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}"
        dt_str = f"{formatted_date} {time_str}"
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    except (ValueError, IndexError):
        logging.error(f"Invalid date/time format: '{date_str}', '{time_str}'")
        return None

def upload_to_s3(article_content: str, publish_dt, content_id):
    """
    Compress article_content and upload it to AWS S3.
    
    The S3 key is built based on the publish date:
      s3://S3_BUCKET_NAME/coindesk/YYYY/MM/DD/coindesk_article_{content_id}.txt.gz
    
    Returns:
        tuple: (s3_url, original_size, compressed_size) or (None, 0, 0) on failure.
    """
    if not article_content:
        return None, 0, 0

    if not publish_dt:
        publish_dt = datetime.now()
    
    year_str = publish_dt.strftime('%Y')
    month_str = publish_dt.strftime('%m')
    day_str = publish_dt.strftime('%d')
    s3_key = f"coindesk/{year_str}/{month_str}/{day_str}/coindesk_article_{content_id}.txt.gz"
    
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
        logging.error(f"Failed to upload article content to S3: {e}")
        return None, 0, 0


# ------------------------------------------------------------------------------
# Main Processing Functions
# ------------------------------------------------------------------------------
def process_url(coindesk_sitemap_link: str) -> None:
    """
    Process a given URL:
      - Connect to the database using PostgresManager.
      - Ensure the articles table exists.
      - Check for duplicate entries.
      - Fetch the page, extract metadata and content.
      - Upload article content to S3.
      - Insert the article record into the database.
    """
    try:
        # Use the PostgresManager as a context manager
        with PGManager(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD) as db:
            db.create_table_if_not_exists()

            if db.article_exists(coindesk_sitemap_link):
                logging.info(f"{coindesk_sitemap_link} already exists in the articles table.")
                return

            parsed = urlparse(coindesk_sitemap_link)
            if parsed.netloc not in ALLOWED_DOMAINS:
                logging.info(f"Domain {parsed.netloc} not allowed. Skipping URL: {coindesk_sitemap_link}")
                return

            try:
                response = session.get(coindesk_sitemap_link, timeout=10)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed for {coindesk_sitemap_link}: {e}")
                return

            soup = BeautifulSoup(response.text, "html.parser")

            # Ensure the article is English and of the correct type
            page_category = soup.find("meta", attrs={"name": "page_category"})
            content_language = soup.find("meta", attrs={"name": "content_language"})
            if not (page_category and page_category.get("content") == "article_page" and
                    content_language and content_language.get("content") == "en"):
                logging.info(f"Not an English article. Skipping: {coindesk_sitemap_link}")
                return

            data = {}
            meta_tags = [
                "page_url", "authors", "content_id", "content_language", "content_title",
                "content_tier", "content_type", "content_vertical", "create_date",
                "create_time", "display_date", "display_time", "last_modified_date",
                "last_modified_time", "page_category", "publish_date", "publish_time", "tags"
            ]
            for tag in meta_tags:
                meta = soup.find("meta", attrs={"name": tag})
                data[tag] = meta["content"] if meta else None

            og_tags = ["og:title", "og:description", "og:site_name"]
            for tag in og_tags:
                meta = soup.find("meta", attrs={"property": tag})
                data[tag] = meta["content"] if meta else None

            article_body = soup.find("div", attrs={"data-module-name": "article-body"})
            data["article_content"] = article_body.get_text(separator=" ") if article_body else ""

            logging.info(f"Extracted article: {data.get('og:title', 'Unknown Title')}")

            display_datetime = combine_date_time(data.get('display_date'), data.get('display_time'))
            last_modified_datetime = combine_date_time(data.get('last_modified_date'), data.get('last_modified_time'))
            publish_datetime = combine_date_time(data.get('publish_date'), data.get('publish_time'))
            create_datetime = combine_date_time(data.get('create_date'), data.get('create_time'))

            s3_url, original_size, compressed_size = upload_to_s3(
                data["article_content"], 
                publish_datetime, 
                data["content_id"]
            )

            article_data = {
                'display_datetime':       display_datetime,
                'last_modified_datetime': last_modified_datetime,
                'publish_datetime':       publish_datetime,
                'create_datetime':        create_datetime,
                'content_vertical':       data.get('content_vertical'),
                'og_description':         data.get('og:description'),
                'content_type':           data.get('content_type'),
                'page_url':               data.get('page_url'),
                'og_title':               data.get('og:title'),
                'content_title':          data.get('content_title'),
                'og_site_name':           data.get('og:site_name'),
                'tags':                   data.get('tags'),
                'authors':                data.get('authors'),
                'content_tier':           data.get('content_tier'),
                'article_s3_url':         s3_url
            }

            db.insert_article(article_data)

            # Adaptive delay to prevent IP blocking
            time.sleep(min(5, max(1, len(data["article_content"]) // 500)))
    except Exception as e:
        logging.error(f"Error processing URL {coindesk_sitemap_link}: {e}")


def callback(ch, method, properties, body):
    """RabbitMQ message handler."""
    coindesk_sitemap_link = body.decode()
    logging.info(f"Processing {coindesk_sitemap_link}")
    try:
        process_url(coindesk_sitemap_link)
    except Exception as e:
        logging.error(f"Error processing URL {coindesk_sitemap_link}: {e}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer():
    """Start RabbitMQ consumer with automatic reconnection."""
    global should_exit
    while not should_exit:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
            logging.info(" [*] Waiting for messages. To exit, press CTRL+C")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            logging.error("Lost connection to RabbitMQ. Reconnecting in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    start_consumer()
