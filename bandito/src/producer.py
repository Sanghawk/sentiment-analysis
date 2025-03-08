import logging
import time
import requests
import pika
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PGManager.PGManager import PGManager  # import our DB manager
import os
from dotenv import load_dotenv

# Load environment variables (ensure you have a .env file if needed)
load_dotenv()

# PostgreSQL configuration (adjust your environment variables as needed)
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')




class SitemapCrawler:
    """
    A crawler that extracts sitemap page links, fetches all links from those pages,
    and pushes new links to RabbitMQ for further processing while caching page URLs.
    
    The cache (stored in a PostgreSQL table) prevents re-queuing links that have already been processed.
    """

    def __init__(self, base_url, sitemap_start, rabbitmq_host='rabbitmq', delay=5):
        """
        :param base_url: The base URL of the website.
        :param sitemap_start: The sitemap path (from the base URL) to start extraction.
        :param rabbitmq_host: RabbitMQ server host.
        :param delay: Delay (in seconds) between requests.
        """
        self.base_url = base_url
        self.sitemap_start = sitemap_start
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; SitemapCrawler/1.0)"})
        
        # Setup RabbitMQ connection
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='sitemap_links')
        
        # Configure logging (this configuration applies to all imported modules)
        logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
        
        # Initialize the database manager and load the URL cache.
        self.db = PGManager(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)
        self.db.connect()
        self.db.create_table_if_not_exists()
        # Load cached page_urls from the database and store them in a set.
        self.cached_urls = set(self.db.get_article_field_list("page_url"))
        logging.info(f"Initialized URL cache with {len(self.cached_urls)} URLs.")

    def get_sitemap_links(self):
        """Extracts all sitemap page links from the base sitemap page."""
        starting_sitemap = f'{self.base_url}{self.sitemap_start}'
        logging.info(f"Fetching sitemap index: {starting_sitemap}")
        response = self.session.get(starting_sitemap)
        if response.status_code != 200:
            logging.error(f"Failed to fetch sitemap index: {starting_sitemap}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        sitemap_links = []
        try:
            section = soup.find("section", attrs={"data-module-name": "section"})
            if section:
                nav = section.find("nav", attrs={"role": "navigation"})
                if nav:
                    a_tags = nav.find_all("a", href=True)
                    sitemap_links = [urljoin(self.base_url, a["href"]) for a in a_tags]
        except Exception as e:
            logging.error(f"Error extracting sitemap links: {e}")
        
        return sitemap_links

    def process_sitemap(self, sitemap_url):
        """Fetches links from a given sitemap page and pushes new ones to RabbitMQ."""
        logging.info(f"Processing sitemap: {sitemap_url}")
        response = self.session.get(sitemap_url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch sitemap: {sitemap_url}")
            return
        
        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        try:
            section_tags = soup.find_all("section", attrs={"data-module-name": "section"})
            # Adjust the following parsing logic as needed for your sitemap page structure.
            link_grid = section_tags[0].find("div", recursive=False).find_all("div", recursive=False)[1]
            a_tags = link_grid.find_all("a", href=True)
            for a in a_tags:
                href = a["href"].strip()
                links.append(f'{self.base_url}{href}')
        except Exception as e:
            logging.info(f"[process_sitemap error] {sitemap_url} -> {e}")
            logging.info("Issue with parsing the sitemap links")
        
        # For each link, check the cache; if it's new, push to RabbitMQ and cache it.
        for link in links:
            self.cache_and_push(link)
        
        time.sleep(self.delay)

    def cache_and_push(self, link):
        """
        Checks if the link is already cached. If not, pushes it to RabbitMQ and
        caches it in the database.
        """
        if link in self.cached_urls:
            logging.info(f"Link already cached, skipping: {link}")
            return
        
        self.push_to_rabbitmq(link)
        self.cached_urls.add(link)

    def push_to_rabbitmq(self, link):
        """Pushes an extracted link to the RabbitMQ queue."""
        logging.info(f"Pushing to RabbitMQ: {link}")
        self.channel.basic_publish(exchange='', routing_key='sitemap_links', body=link)


    def run(self):
        """Main execution loop for sitemap crawling."""
        while True:
            sitemap_links = self.get_sitemap_links()
            for sitemap_link in sitemap_links:
                self.process_sitemap(sitemap_link)
            logging.info("Restarting sitemap extraction cycle...")
            time.sleep(self.delay)


if __name__ == "__main__":
    crawler = SitemapCrawler(base_url="https://www.coindesk.com", sitemap_start="/sitemap/1", rabbitmq_host="rabbitmq")
    try:
        crawler.run()
    except KeyboardInterrupt:
        logging.info("Shutting down crawler.")
        crawler.connection.close()
        if crawler.db.conn:
            crawler.db.conn.close()