import pika
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import logging
import json
import signal
import sys
from requests.adapters import HTTPAdapter, Retry

# Configure logging
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

# Graceful shutdown flag
should_exit = False

def signal_handler(sig, frame):
    global should_exit
    logging.info("Received shutdown signal. Exiting gracefully...")
    should_exit = True

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def process_url(coindesk_sitemap_link):
    """Process a URL: Fetch, Parse, Extract Metadata"""
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

    # Check if it’s an English article
    page_category = soup.find("meta", attrs={"name": "page_category"})
    content_language = soup.find("meta", attrs={"name": "content_language"})

    if not (page_category and page_category.get("content") == "article_page" and
            content_language and content_language.get("content") == "en"):
        logging.info(f"Not an English article. Skipping: {coindesk_sitemap_link}")
        return

    # Extract metadata
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

    # Extract article text
    article_body = soup.find("div", attrs={"data-module-name": "article-body"})
    data["article_content"] = article_body.get_text(separator=" ") if article_body else ""

    logging.info(f"Extracted article: {data.get('og:title', 'Unknown Title')}")
    
    # Convert extracted data to JSON
    article_json = json.dumps(data, indent=2)
    logging.info(f"Extracted Data: {article_json}")

    # TODO: gotta figure out where to put the data now.

    # Delay to prevent IP blocking (adaptive)
    time.sleep(min(5, max(1, len(data["article_content"]) // 500)))  # Adjust sleep dynamically

def callback(ch, method, properties, body):
    """RabbitMQ message handler."""
    coindesk_sitemap_link = body.decode()
    logging.info(f"Processing {coindesk_sitemap_link}")

    try:
        process_url(coindesk_sitemap_link)
    except Exception as e:
        logging.error(f"Error processing URL {coindesk_sitemap_link}: {e}")
    
    # Acknowledge message after processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer():
    """Start RabbitMQ consumer with automatic reconnection."""
    global should_exit
    while not should_exit:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME)
            channel.basic_qos(prefetch_count=1)  # Prevent overwhelming one consumer
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

            logging.info(" [*] Waiting for messages. To exit, press CTRL+C")
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError:
            logging.error("Lost connection to RabbitMQ. Reconnecting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    start_consumer()
