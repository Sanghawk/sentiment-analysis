# postgres_manager.py
import psycopg2
import logging

logger = logging.getLogger(__name__)

class PGManager:
    """
    A class to manage a PostgreSQL database connection and operations.
    
    This class encapsulates connection management, table creation,
    record existence checking, insertion of article data, and fetching
    lists of article field values.
    """
    # Define a whitelist of allowed article fields
    ALLOWED_FIELDS = {
        'id',
        'display_datetime',
        'last_modified_datetime',
        'publish_datetime',
        'create_datetime',
        'content_vertical',
        'og_description',
        'content_type',
        'page_url',
        'og_title',
        'content_title',
        'og_site_name',
        'tags',
        'authors',
        'content_tier',
        'article_s3_url'
    }

    def __init__(self, host: str, port: str, dbname: str, user: str, password: str) -> None:
        self.host = host
        self.port = int(port) if port else 5432  # Default to port 5432 if none provided
        self.dbname = dbname
        self.user = user
        self.password = password
        self.conn = None

    def connect(self) -> None:
        """Establish a connection to the PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password
            )
            logger.info("Successfully connected to PostgreSQL database.")
        except psycopg2.Error as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")
            raise

    def __enter__(self):
        """Enable use as a context manager."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure the database connection is closed."""
        if self.conn:
            self.conn.close()
            logger.info("PostgreSQL connection closed.")

    def create_table_if_not_exists(self) -> None:
        """
        Create the `articles` table if it does not already exist.
        The table excludes the article_content column, but includes article_s3_url.
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
            with self.conn.cursor() as cur:
                cur.execute(create_table_query)
            self.conn.commit()
            logger.info("Table 'articles' ensured to exist.")
        except psycopg2.Error as e:
            logger.error(f"Error creating articles table: {e}")
            self.conn.rollback()

    def article_exists(self, page_url: str) -> bool:
        """
        Check if an article with the given page_url already exists in the database.
        
        Returns:
            bool: True if the article exists, False otherwise.
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM articles WHERE page_url = %s", (page_url,))
                (count,) = cur.fetchone()
                return count > 0
        except psycopg2.Error as e:
            logger.error(f"Error checking existing article: {e}")
            return False

    def insert_article(self, article_data: dict) -> None:
        """
        Insert a new article record into the articles table.
        
        Args:
            article_data (dict): A dictionary containing article fields.
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
            with self.conn.cursor() as cur:
                cur.execute(insert_query, article_data)
            self.conn.commit()
            logger.info(f"Inserted article: {article_data.get('og_title')} (URL: {article_data.get('page_url')})")
        except psycopg2.Error as e:
            logger.error(f"Error inserting article into PostgreSQL: {e}")
            self.conn.rollback()

    def get_article_field_list(self, field: str) -> list:
        """
        Retrieve a list of values for the specified article field from the articles table.
        
        Args:
            field (str): The column name to retrieve values from (e.g., 'page_url').
        
        Returns:
            list: A list of values for the given field. If an error occurs, returns an empty list.
        
        Raises:
            ValueError: If the provided field is not in the list of allowed fields.
        """
        if field not in self.ALLOWED_FIELDS:
            raise ValueError(f"Field '{field}' is not a valid article field.")

        query = f"SELECT {field} FROM articles;"
        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
            # Each row is a tuple with a single element
            return [row[0] for row in result]
        except psycopg2.Error as e:
            logger.error(f"Error fetching field '{field}' from articles: {e}")
            return []
