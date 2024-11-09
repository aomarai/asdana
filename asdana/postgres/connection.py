"""
Generic module for handling the connection to Postgres databases with asyncpg.
"""

import asyncpg


class PostgresConnection:
    """
    Class for handling the connection to the Postgres database.
    """

    def __init__(
        self, user: str, password: str, database: str, host: str, port: str | int
    ):  # pylint: disable=too-many-arguments, too-many-positional-arguments
        """
        Initializes the PostgresConnection instance.

        :param user: The username for the database.
        :param password: The password for the database.
        :param database: The name of the database.
        :param host: The host of the database.
        :param port: The port of the database.
        """
        self.pool = None
        self.user = user
        self.password = password
        self.database = database
        self.host = host
        self.port = port

    async def __aenter__(self):
        """
        Asynchronous context manager entry. Connects to the database.
        :return: The PostgresConnection instance.
        """
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """
        Asynchronous context manager exit. Disconnects from the database.
        :param exc_type: The exception type.
        :param exc: The exception instance.
        :param tb: The traceback object.
        :return: None
        """
        await self.disconnect()

    async def connect(self):
        """
        Connects to the Postgres database.
        :return: None
        """
        min_size = 1
        max_size = 10

        try:
            self.pool = await asyncpg.create_pool(
                user=self.user,
                password=self.password,
                database=self.database,
                host=self.host,
                port=self.port,
                min_size=min_size,
                max_size=max_size,
            )
        except asyncpg.PostgresError as e:
            print(f"Failed to create connection pool: {e}")
            raise

    async def disconnect(self):
        """
        Disconnects from the Postgres database.
        :return: None
        """
        if self.pool:
            try:
                await self.pool.close()
            except asyncpg.PostgresError as e:
                print(f"Failed to close connection pool: {e}")
                raise

    async def execute(self, query: str, *args):
        """
        Executes a query on the database.
        :param query: The query to execute.
        :param args: The arguments to pass to the query.
        :return: The result of the query.
        """
        async with self.pool.acquire() as connection:
            try:
                return await connection.execute(query, *args)
            except asyncpg.PostgresError as e:
                print(f"Failed to execute query: {e}")
                raise

    async def fetch(self, query: str, *args):
        """
        Fetches multiple rows from the database.
        :param query: The query to execute.
        :param args: The arguments to pass to the query.
        :return: The result of the query.
        """
        async with self.pool.acquire() as connection:
            try:
                return await connection.fetch(query, *args)
            except asyncpg.PostgresError as e:
                print(f"Failed to fetch query: {e}")
                raise

    async def fetchrow(self, query: str, *args):
        """
        Fetches a single row from the database.
        :param query: The query to execute.
        :param args: The arguments to pass to the query.
        :return: The result of the query.
        """
        async with self.pool.acquire() as connection:
            try:
                return await connection.fetchrow(query, *args)
            except asyncpg.PostgresError as e:
                print(f"Failed to fetch row: {e}")
                raise

    async def fetchval(self, query: str, *args):
        """
        Fetches a single value from the database.
        :param query: The query to execute.
        :param args: The arguments to pass to the query.
        :return: The result of the query.
        """
        async with self.pool.acquire() as connection:
            try:
                return await connection.fetchval(query, *args)
            except asyncpg.PostgresError as e:
                print(f"Failed to fetch value: {e}")
                raise
