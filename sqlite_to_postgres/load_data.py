import sqlite3
from collections.abc import Generator
from contextlib import closing, contextmanager
from dataclasses import astuple, fields
import logging
from venv import logger
import psycopg2
import settings
from psycopg2.extras import DictCursor
from psycopg2.extensions import connection as _connection
from sqlite_to_postgres.load_data_classes import load_tables


@contextmanager
def conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class SQLiteExtractor:
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.cursor = connection.cursor()

    def extract_movies(self):
        for table in load_tables:
            data_class = load_tables[table]
            self.cursor.execute(f'SELECT * FROM {table};')
            while data := self.cursor.fetchmany(20):
                yield {table: [data_class(*row) for row in data]}


class PostgresSaver:
    def __init__(self, connection: _connection):
        try:
            self.logger = logger
        except NameError:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(self.__class__.__name__)

        self.connection = connection
        self.cursor = connection.cursor()

    def __del__(self):
        if hasattr(self, 'connection'):
            self.logger.info(f"Closing connection to DB")
            self.connection.close()


    def save_all_data(self, gen_data: Generator, chunk_size: int = 10):
        self.logger.info(f"Starting to save all data, {chunk_size=}")
        for data in gen_data:
            table = tuple(data.keys())[0]
            data_class = load_tables[table]
            cur_tables = data[table]
            column_names = [field.name for field in fields(data_class)]
            column_names_str = ','.join(column_names)
            col_count = ', '.join(['%s'] * len(column_names))
            for i in range(0, len(cur_tables), chunk_size):
                chang_query = cur_tables[i:i + chunk_size]
                values = ','.join(self.cursor.mogrify(f'({col_count})', astuple(item)).decode() for item in chang_query)
                query = (f'INSERT INTO content.{table} ({column_names_str}) VALUES {values} '
                         f'ON CONFLICT DO NOTHING;')
                self.logger.debug(f"SQL query: {query}")
                self.cursor.execute(query)
                self.connection.commit()
        self.logger.info(f"Data saved successfully")




def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_extractor = SQLiteExtractor(connection)

    data = sqlite_extractor.extract_movies()
    postgres_saver.save_all_data(data, chunk_size=10)


if __name__ == '__main__':
    with (conn_context(settings.SQLITE_PATH) as sqlite_conn,
          closing(psycopg2.connect(**settings.DSL, cursor_factory=DictCursor)) as postgres_conn):
        load_from_sqlite(sqlite_conn, postgres_conn)

