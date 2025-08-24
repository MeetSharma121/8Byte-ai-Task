"""
Database models and query functions for the Stock Market Data API.
"""
import logging
from datetime import datetime

def get_stock_data(conn, symbol=None, page=1, per_page=100):
    """
    Get stock data with pagination.
    
    Args:
        conn: Database connection
        symbol: Optional stock symbol to filter by
        page: Page number (1-indexed)
        per_page: Number of items per page
    
    Returns:
        List of stock data dictionaries
    """
    offset = (page - 1) * per_page
    
    try:
        with conn.cursor() as cur:
            if symbol:
                query = """
                    SELECT id, symbol, date, open, high, low, close, volume
                    FROM stock_data
                    WHERE symbol = %s
                    ORDER BY date DESC
                    LIMIT %s OFFSET %s
                """
                cur.execute(query, (symbol, per_page, offset))
            else:
                query = """
                    SELECT id, symbol, date, open, high, low, close, volume
                    FROM stock_data
                    ORDER BY date DESC, symbol
                    LIMIT %s OFFSET %s
                """
                cur.execute(query, (per_page, offset))
            
            results = cur.fetchall()
            return [dict(row) for row in results]
    except Exception as e:
        logging.error(f"Database error in get_stock_data: {e}")
        return []

def get_stock_symbols(conn):
    """
    Get all unique stock symbols in the database.
    
    Args:
        conn: Database connection
    
    Returns:
        List of stock symbols
    """
    try:
        with conn.cursor() as cur:
            query = """
                SELECT DISTINCT symbol
                FROM stock_data
                ORDER BY symbol
            """
            cur.execute(query)
            results = cur.fetchall()
            return [row['symbol'] for row in results]
    except Exception as e:
        logging.error(f"Database error in get_stock_symbols: {e}")
        return []

def get_stock_data_by_date_range(conn, symbol, start_date=None, end_date=None):
    """
    Get stock data for a specific symbol within a date range.
    
    Args:
        conn: Database connection
        symbol: Stock symbol
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD)
    
    Returns:
        List of stock data dictionaries
    """
    try:
        with conn.cursor() as cur:
            params = [symbol]
            query = """
                SELECT id, symbol, date, open, high, low, close, volume
                FROM stock_data
                WHERE symbol = %s
            """
            
            if start_date:
                query += " AND date >= %s"
                params.append(datetime.strptime(start_date, '%Y-%m-%d').date())
            
            if end_date:
                query += " AND date <= %s"
                params.append(datetime.strptime(end_date, '%Y-%m-%d').date())
            
            query += " ORDER BY date"
            
            cur.execute(query, params)
            results = cur.fetchall()
            return [dict(row) for row in results]
    except Exception as e:
        logging.error(f"Database error in get_stock_data_by_date_range: {e}")
        return []

def get_stock_statistics(conn, symbol):
    """
    Get statistical information about a stock.
    
    Args:
        conn: Database connection
        symbol: Stock symbol
    
    Returns:
        Dictionary with statistical information
    """
    try:
        with conn.cursor() as cur:
            query = """
                SELECT 
                    symbol,
                    COUNT(*) as data_points,
                    MIN(date) as first_date,
                    MAX(date) as last_date,
                    AVG(close) as avg_close,
                    MIN(low) as min_price,
                    MAX(high) as max_price,
                    AVG(volume) as avg_volume
                FROM stock_data
                WHERE symbol = %s
                GROUP BY symbol
            """
            cur.execute(query, (symbol,))
            result = cur.fetchone()
            return dict(result) if result else None
    except Exception as e:
        logging.error(f"Database error in get_stock_statistics: {e}")
        return None