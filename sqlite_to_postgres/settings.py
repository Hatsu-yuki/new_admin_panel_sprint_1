import os

from dotenv import load_dotenv

load_dotenv()

SQLITE_PATH = os.environ.get('SQLITE_PATH')

DSL = {
    'dbname': os.environ.get('POSTGRES_DB_NAME'),
    'user': os.environ.get('POSTGRES_DB_USER'),
    'password': os.environ.get('POSTGRES_DB_PASSWORD'),
    'host': os.environ.get('POSTGRES_HOST', '127.0.0.1'),
    'port': os.environ.get('POSTGRES_PORT', 5432),
}

