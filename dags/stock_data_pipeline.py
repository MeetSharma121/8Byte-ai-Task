"""
Airflow DAG for fetching stock market data and storing it in PostgreSQL.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
import sys
import os

# Add scripts directory to path
sys.path.append('/opt/airflow/scripts')

# Import the fetch_stock_data script
from fetch_stock_data import main as fetch_stock_data_main

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 1, 1),
}

# Create the DAG
dag = DAG(
    'stock_data_pipeline',
    default_args=default_args,
    description='A DAG to fetch and store stock market data',
    schedule_interval='0 0 * * *',  # Run daily at midnight
    catchup=False,
    tags=['stock', 'data', 'pipeline'],
)

# Task to ensure the database tables exist
create_tables = PostgresOperator(
    task_id='create_tables',
    postgres_conn_id='postgres_default',
    sql="""
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
    
    CREATE TABLE IF NOT EXISTS stock_metadata (
        symbol VARCHAR(10) PRIMARY KEY,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    dag=dag,
)

# Task to fetch and store stock data
fetch_stock_data = PythonOperator(
    task_id='fetch_stock_data',
    python_callable=fetch_stock_data_main,
    dag=dag,
)

# Task to log the completion of the pipeline
log_completion = BashOperator(
    task_id='log_completion',
    bash_command='echo "Stock data pipeline completed at $(date)"',
    dag=dag,
)

# Define task dependencies
create_tables >> fetch_stock_data >> log_completion