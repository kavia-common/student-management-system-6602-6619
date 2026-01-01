import os
import psycopg2
from contextlib import contextmanager

from dotenv import load_dotenv

load_dotenv()

# Provides a context manager for PostgreSQL connections
# PUBLIC_INTERFACE
@contextmanager
def get_db():
    """
    Context manager to get a PostgreSQL DB connection using environment variables.
    Yields a cursor, cleans up afterward.
    Requires the following env vars:
      - POSTGRES_URL
      - POSTGRES_USER
      - POSTGRES_PASSWORD
      - POSTGRES_DB
      - POSTGRES_PORT
    """
    db_url = os.environ.get("POSTGRES_URL")
    db_user = os.environ.get("POSTGRES_USER")
    db_password = os.environ.get("POSTGRES_PASSWORD")
    db_name = os.environ.get("POSTGRES_DB")
    db_port = os.environ.get("POSTGRES_PORT")
    conn = None
    try:
        conn = psycopg2.connect(
            host=db_url,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port,
        )
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            cur.close()
            conn.close()
