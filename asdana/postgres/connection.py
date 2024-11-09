import asyncpg
import os


class PostgresConnection:
    """
    Class for handling the connection to the postgres database.
    """

    def __init__(self):
        self.connection = None

    async def connect(
        self,
        user: str = os.getenv("DB_USER"),
        password: str = os.getenv("DB_PASSWORD"),
        database: str = os.getenv("DB_NAME"),
        host: str = os.getenv("DB_HOST"),
        port: int | str = os.getenv("DB_PORT"),
        *args,
        **kwargs,
    ):
        """
        Connects to the postgres database.
        :param user: The database user.
        :param password: The database password.
        :param database: The database name.
        :param host: The database host.
        :param port: The database port.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: None
        """
        try:
            self.connection = await asyncpg.connect(
                user=user,
                password=password,
                database=database,
                host=host,
                port=port,
                *args,
                **kwargs,
            )
        except asyncpg.PostgresError as e:
            print(f"Failed to connect to the database: {e}")
            raise

    async def disconnect(self):
        """
        Disconnects from the postgres database.
        :return: None
        """
        if self.connection:
            try:
                await self.connection.close()
            except asyncpg.PostgresError as e:
                print(f"Failed to disconnect from the database: {e}")
                raise

    async def execute(self, query: str, *args):
        """
        Executes a query on the postgres database.
        :param query: The query to execute.
        :param args: The arguments to pass to the query.
        :return: The result of the query.
        """
        try:
            return await self.connection.execute(query, *args)
        except asyncpg.PostgresError as e:
            print(f"Failed to execute query: {e}")
            raise

    async def fetch(self, query: str, *args):
        """
        Fetches a query from the postgres database.
        :param query: The query to fetch.
        :param args: The arguments to pass to the query.
        :return: The result of the query.
        """
        try:
            return await self.connection.fetch(query, *args)
        except asyncpg.PostgresError as e:
            print(f"Failed to fetch query: {e}")
            raise

    async def fetchrow(self, query: str, *args):
        """
        Fetches a row from the postgres database.
        :param query: The query to fetch the row from.
        :param args: The arguments to pass to the query.
        :return: The row fetched from the query.
        """
        try:
            return await self.connection.fetchrow(query, *args)
        except asyncpg.PostgresError as e:
            print(f"Failed to fetch row: {e}")
            raise

    async def fetchval(self, query: str, *args):
        """
        Fetches a value from the postgres database.
        :param query: The query to fetch the value from.
        :param args: The arguments to pass to the query.
        :return: The value fetched from the query.
        """
        try:
            return await self.connection.fetchval(query, *args)
        except asyncpg.PostgresError as e:
            print(f"Failed to fetch value: {e}")
            raise
