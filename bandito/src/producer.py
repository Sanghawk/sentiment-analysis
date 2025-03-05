import logging
import time
import requests
import pika
from bs4 import BeautifulSoup
from urllib.parse import urljoin



class SitemapCrawler:
    """
    A crawler that extracts sitemap page links, fetches all links from those pages,
    and pushes them to RabbitMQ for further processing.
    """

    def __init__(self, base_url, sitemap_start, rabbitmq_host='rabbitmq', delay=60):
        """
        :param base_url: The URL of the website's sitemap index.
        :param rabbitmq_host: RabbitMQ server host.
        :param delay: Time (in seconds) to sleep after each request to avoid being blocked.
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
        
        # Logging setup
        logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)

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
        """Fetches links from a given sitemap page and pushes them to RabbitMQ."""
        logging.info(f"Processing sitemap: {sitemap_url}")
        response = self.session.get(sitemap_url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch sitemap: {sitemap_url}")
            return
        
        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        try:
            section_tags = soup.find_all("section", attrs={"data-module-name": "section"})
            link_grid = section_tags[0].find("div", recursive=False).find_all("div", recursive=False)[1]
            a_tags = link_grid.find_all("a", href=True)
            for a in a_tags:
                href = a["href"].strip()
                links.append(f'{self.base_url}{href}')
        except Exception as e:
            logging.info(f"[process_sitemap error] {sitemap_url} -> {e}")
            logging.info("Issue with parsing the sitemap links")
        
        
        for link in links:
            self.push_to_rabbitmq(link)
        
        time.sleep(self.delay)

    def push_to_rabbitmq(self, link):
        """Pushes extracted links to RabbitMQ queue."""
        logging.info(f"Pushing to RabbitMQ: {link}")
        self.channel.basic_publish(exchange='', routing_key='sitemap_links', body=link)

    def run(self):
        """Main execution loop."""
        while True:
            sitemap_links = self.get_sitemap_links()
            for sitemap_link in sitemap_links:
                self.process_sitemap(sitemap_link)
            logging.info("Restarting sitemap extraction cycle...")
            time.sleep(self.delay)
            return

if __name__ == "__main__":
    crawler = SitemapCrawler(base_url="https://www.coindesk.com", sitemap_start="/sitemap/1", rabbitmq_host="rabbitmq")
    try:
        crawler.run()
    except KeyboardInterrupt:
        logging.info("Shutting down crawler.")
        crawler.connection.close()
