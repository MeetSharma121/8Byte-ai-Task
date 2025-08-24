#!/usr/bin/env python3
"""
Script to fetch stock market data from Yahoo Finance API and store it in PostgreSQL.
"""
import os
import sys
import logging
import traceback
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import psycopg2
from psycopg2 import sql

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('stock_data_fetcher')

def get_db_connection():
    """
    Create a connection to the PostgreSQL database.
    Returns a connection object.
    """
    try:
        conn = psycopg2.connect(
            host="postgres",
            database=os.environ.get("POSTGRES_DB", "airflow"),
            user=os.environ.get("POSTGRES_USER", "airflow"),
            password=os.environ.get("POSTGRES_PASSWORD", "airflow"),
            port=5432
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

def create_tables_if_not_exist(conn):
    """
    Create the necessary tables if they don't exist.
    """
    try:
        with conn.cursor() as cur:
            # Create stock_data table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS stock_data (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    date DATE NOT NULL,
                    open NUMERIC(10, 2),
                    high NUMERIC(10, 2),
                    low NUMERIC(10, 2),
                    close NUMERIC(10, 2),
                    volume BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                );
            """)
            
            # Create stock_metadata table for tracking last update
            cur.execute("""
                CREATE TABLE IF NOT EXISTS stock_metadata (
                    symbol VARCHAR(10) PRIMARY KEY,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            logger.info("Tables created or already exist")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating tables: {e}")
        raise

def fetch_stock_data(symbol, start_date, end_date):
    """
    Fetch stock data from Yahoo Finance API.
    Returns a pandas DataFrame with the stock data.
    """
    try:
        logger.info(f"Fetching data for {symbol} from {start_date} to {end_date}")
        stock = yf.Ticker(symbol)
        data = stock.history(start=start_date, end=end_date)
        
        if data.empty:
            logger.warning(f"No data returned for {symbol}")
            return None
        
        # Reset index to make date a column and rename columns
        data = data.reset_index()
        data.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)
        
        # Add symbol column
        data['symbol'] = symbol
        
        # Select only the columns we need
        data = data[['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']]
        
        return data
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return None

def insert_stock_data(conn, data):
    """
    Insert stock data into the PostgreSQL database.
    """
    if data is None or data.empty:
        logger.warning("No data to insert")
        return 0
    
    rows_inserted = 0
    try:
        with conn.cursor() as cur:
            for _, row in data.iterrows():
                try:
                    # Use ON CONFLICT to handle duplicate entries
                    cur.execute("""
                        INSERT INTO stock_data 
                        (symbol, date, open, high, low, close, volume)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (symbol, date) 
                        DO UPDATE SET
                            open = EXCLUDED.open,
                            high = EXCLUDED.high,
                            low = EXCLUDED.low,
                            close = EXCLUDED.close,
                            volume = EXCLUDED.volume,
                            created_at = CURRENT_TIMESTAMP
                    """, (
                        row['symbol'],
                        row['date'],
                        row['open'],
                        row['high'],
                        row['low'],
                        row['close'],
                        row['volume']
                    ))
                    rows_inserted += 1
                except Exception as e:
                    logger.error(f"Error inserting row {row}: {e}")
                    # Continue with next row instead of failing the entire batch
                    continue
            
            # Update metadata table with last update time
            cur.execute("""
                INSERT INTO stock_metadata (symbol, last_updated)
                VALUES (%s, CURRENT_TIMESTAMP)
                ON CONFLICT (symbol) 
                DO UPDATE SET last_updated = CURRENT_TIMESTAMP
            """, (data['symbol'].iloc[0],))
            
            conn.commit()
            logger.info(f"Inserted {rows_inserted} rows for {data['symbol'].iloc[0]}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    
    return rows_inserted

def main():
    """
    Main function to fetch and store stock data.
    """
    # Get stock symbols from environment variable
    symbols = os.environ.get("STOCK_SYMBOLS", "AAPL,MSFT,GOOGL").split(",")
    
    # Calculate date range (last 7 days by default)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Format dates for Yahoo Finance API
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    try:
        # Get database connection
        conn = get_db_connection()
        
        # Create tables if they don't exist
        create_tables_if_not_exist(conn)
        
        total_rows_inserted = 0
        
        # Process each symbol
        for symbol in symbols:
            symbol = symbol.strip()
            try:
                # Fetch data
                data = fetch_stock_data(symbol, start_date_str, end_date_str)
                
                # Insert data into database
                if data is not None and not data.empty:
                    rows = insert_stock_data(conn, data)
                    total_rows_inserted += rows
                else:
                    logger.warning(f"No data to insert for {symbol}")
            except Exception as e:
                logger.error(f"Error processing symbol {symbol}: {e}")
                logger.error(traceback.format_exc())
                # Continue with next symbol instead of failing the entire batch
                continue
        
        logger.info(f"Total rows inserted: {total_rows_inserted}")
        
        # Close connection
        conn.close()
        
        return total_rows_inserted
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
        return 0

if __name__ == "__main__":
    main()