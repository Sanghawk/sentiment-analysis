import psycopg2
from psycopg2.extras import RealDictCursor

class PGManager:
    """
    A class to connect to a PostgreSQL database and perform CRUD operations.

    Attributes:
        host (str): Database host address.
        database (str): Database name.
        user (str): Database user.
        password (str): Password for the user.
        port (int): Database port number (default is 5432).
        conn (psycopg2.extensions.connection): The database connection object.
        cursor (psycopg2.extensions.cursor): The database cursor object.
    """
    def __init__(self, host: str, database: str, user: str, password: str, port: int = 5432):
        """
        Initializes the PostgresDB instance with connection parameters.

        Args:
            host (str): Database host address.
            database (str): Database name.
            user (str): Database user.
            password (str): Password for the user.
            port (int, optional): Database port number. Defaults to 5432.
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.conn = None
        self.cursor = None

    def connect(self):
        """
        Establishes a connection to the PostgreSQL database and creates a cursor.
        Uses RealDictCursor so that query results are returned as dictionaries.
        """
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("Connection to the database was successful.")
        except psycopg2.Error as e:
            print("Error connecting to PostgreSQL database:", e)
            raise

    def disconnect(self):
        """
        Closes the cursor and database connection.
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Disconnected from the database.")
    
    def execute(self, statement: str) -> None:
        try:
            self.cursor.execute(statement)
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()

    def create(self, table: str, data: dict) -> dict:
        """
        Inserts a new record into the specified table.

        Args:
            table (str): The table name.
            data (dict): A dictionary mapping column names to values for the new record.

        Returns:
            dict: The inserted record (as returned by the RETURNING clause).
        """
        columns = data.keys()
        values = list(data.values())
        placeholders = ', '.join(['%s'] * len(values))
        col_names = ', '.join(columns)
        query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders}) RETURNING *;"
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.fetchone()
        except psycopg2.Error as e:
            self.conn.rollback()
            print("Error in CREATE operation:", e)
            raise

    def read(self, table: str, conditions: dict = None, columns: str = '*') -> list:
        """
        Retrieves records from the specified table.

        Args:
            table (str): The table name.
            conditions (dict, optional): A dictionary mapping column names to values for the WHERE clause.
            columns (str, optional): Columns to select, default is '*' (all columns).

        Returns:
            list: A list of dictionaries representing the rows.
        """
        query = f"SELECT {columns} FROM {table}"
        values = []
        if conditions:
            cond_clause = " AND ".join([f"{col} = %s" for col in conditions.keys()])
            query += " WHERE " + cond_clause
            values = list(conditions.values())
        try:
            self.cursor.execute(query, values)
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print("Error in READ operation:", e)
            raise

    def update(self, table: str, data: dict, conditions: dict) -> dict:
        """
        Updates records in the specified table.

        Args:
            table (str): The table name.
            data (dict): A dictionary mapping column names to new values.
            conditions (dict): A dictionary mapping column names to values for the WHERE clause.

        Returns:
            dict: The updated record (as returned by the RETURNING clause).
        """
        set_clause = ", ".join([f"{col} = %s" for col in data.keys()])
        cond_clause = " AND ".join([f"{col} = %s" for col in conditions.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {cond_clause} RETURNING *;"
        values = list(data.values()) + list(conditions.values())
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.fetchone()
        except psycopg2.Error as e:
            self.conn.rollback()
            print("Error in UPDATE operation:", e)
            raise

    def delete(self, table: str, conditions: dict) -> dict:
        """
        Deletes records from the specified table.

        Args:
            table (str): The table name.
            conditions (dict): A dictionary mapping column names to values for the WHERE clause.

        Returns:
            dict: The deleted record (as returned by the RETURNING clause).
        """
        cond_clause = " AND ".join([f"{col} = %s" for col in conditions.keys()])
        query = f"DELETE FROM {table} WHERE {cond_clause} RETURNING *;"
        values = list(conditions.values())
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.fetchone()
        except psycopg2.Error as e:
            self.conn.rollback()
            print("Error in DELETE operation:", e)
            raise
    
    def query(self, query: str, params: tuple = None) -> list:
        """
        Executes an arbitrary SQL query with optional parameters.

        Args:
            query (str): The SQL query to be executed.
            params (tuple, optional): A tuple of parameters to be used in the query. Defaults to None.

        Returns:
            list: List of result rows (each row as a dictionary) if the query returns rows, 
                  or an empty list if no rows are returned.
        """
        try:
            self.cursor.execute(query, params)
            # Check if the query is a SELECT statement
            if query.strip().lower().startswith("select"):
                return self.cursor.fetchall()
            else:
                self.conn.commit()
                return []
        except psycopg2.Error as e:
            self.conn.rollback()
            print("Error executing query:", e)
            raise

