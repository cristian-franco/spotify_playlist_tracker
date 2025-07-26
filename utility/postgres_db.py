from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from config import postgres_local
import pandas as pd


class PostgresDB():
    """
    Class to interact with the postgres database
    """
    def __init__(self):
        url = URL.create(
            drivername="postgresql",
            username=postgres_local["user"],
            password=postgres_local.get("password", ""),
            host=postgres_local["host"],
            port=postgres_local["port"],
            database=postgres_local["database"]
        )

        self.engine = create_engine(url)

    def execute_query(
        self,
        sql_query: str
    ):
        try:
            df = pd.read_sql(sql_query, self.engine)
            return df
        except Exception as e:
            print(f"Error executing query: {e}")
            return None

    def close_connection(self):
        self.engine.dispose()
        print("Connection closed.")
