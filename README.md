# Dockerized Stock Market Data Pipeline with Airflow

This project implements a Dockerized data pipeline using Apache Airflow to automatically fetch, parse, and store stock market data from a public API into a PostgreSQL database.

## Features

- Scheduled data fetching from Yahoo Finance API
- Automated data processing and storage in PostgreSQL
- Comprehensive error handling and missing data management
- Fully containerized with Docker and Docker Compose
- Secure credential management using environment variables

## Prerequisites

- Docker and Docker Compose installed on your system
- Internet connection to access the Yahoo Finance API

## Project Structure

```
.
├── README.md
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── dags/
│   └── stock_data_pipeline.py
└── scripts/
    └── fetch_stock_data.py
```

## Setup Instructions

1. Clone this repository
2. Copy `.env.example` to `.env` and fill in your configuration values
3. Build and start the containers:

```bash
docker-compose up -d
```

4. Access the Airflow web interface at http://localhost:8080
   - Username: airflow
   - Password: airflow

5. The DAG will run automatically according to the schedule (daily by default)

## Configuration

You can configure the following parameters in the `.env` file:

- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password
- `POSTGRES_DB`: PostgreSQL database name
- `STOCK_SYMBOLS`: Comma-separated list of stock symbols to track (e.g., AAPL,MSFT,GOOGL)

## Stopping the Pipeline

To stop the pipeline and shut down all containers:

```bash
docker-compose down
```

## Extending the Pipeline

To track additional stocks, simply update the `STOCK_SYMBOLS` environment variable in the `.env` file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.