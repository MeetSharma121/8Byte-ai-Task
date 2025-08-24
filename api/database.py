"""
Database connection module for the Stock Market Data API.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """
    Create a connection to the PostgreSQL database.
    Returns a connection object.
    """
    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        database=os.environ.get("POSTGRES_DB", "airflow"),
        user=os.environ.get("POSTGRES_USER", "airflow"),
        password=os.environ.get("POSTGRES_PASSWORD", "airflow"),
        port=5432,
        cursor_factory=RealDictCursor
    )
    return conn

def close_db_connection(conn):
    """
    Close the database connection.
    """
    if conn:
        conn.close()