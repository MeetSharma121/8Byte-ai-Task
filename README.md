# 🚀 Advanced Dockerized Stock Market Data Pipeline 📊

This enterprise-grade project implements a comprehensive data engineering solution for fetching, processing, storing, and visualizing stock market data. Built with scalability, resilience, and observability in mind, this system leverages modern technologies to provide a complete end-to-end solution. ✨

## ✅ Key Features

- 🔄 **Orchestrated Data Pipeline**: Automated workflow using Apache Airflow with scheduled execution
- ⚡ **Real-time Data Access**: RESTful API with Redis caching for high-performance data retrieval
- 📈 **Advanced Visualization**: Interactive Grafana dashboards for data analysis and monitoring
- 👁️ **Complete Observability**: Prometheus metrics collection for system monitoring
- 🔧 **High Scalability**: Distributed architecture with separate services for different concerns
- 🔒 **Enterprise Security**: Environment-based configuration and secure credential management
- 🛡️ **Fault Tolerance**: Comprehensive error handling and recovery mechanisms

## 🏗️ Architecture

The system is built using a microservices architecture with the following components:

- 🌪️ **Airflow**: Orchestrates the data pipeline and schedules data fetching
- 🐘 **PostgreSQL**: Stores the stock market data in a structured format
- 🔴 **Redis**: Provides caching for API responses to improve performance
- 🌐 **Flask API**: Exposes RESTful endpoints for data access with Swagger documentation
- 📊 **Grafana**: Provides interactive dashboards for data visualization
- 📡 **Prometheus**: Collects and stores metrics for monitoring system performance

## 📋 Prerequisites

- 🐳 Docker and Docker Compose installed on your system
- 🌐 Internet connection to access the Yahoo Finance API

## 📁 Project Structure

```
.
├── README.md
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.api
├── requirements.txt
├── requirements.api.txt
├── .env.example
├── dags/
│   └── stock_data_pipeline.py
├── scripts/
│   └── fetch_stock_data.py
├── api/
│   ├── app.py
│   ├── database.py
│   └── models.py
├── grafana/
│   ├── dashboards/
│   │   └── stock_dashboard.json
│   └── provisioning/
│       ├── dashboards/
│       │   └── dashboards.yml
│       └── datasources/
│           └── datasource.yml
└── prometheus/
    └── prometheus.yml
```

## 🚀 Setup Instructions

1. 📥 Clone this repository
2. 📝 Copy `.env.example` to `.env` and fill in your configuration values
3. 🏗️ Build and start the containers:

```bash
docker-compose up -d
```

4. 🌐 Access the following interfaces:
   - 🌪️ **Airflow**: http://localhost:8080 (Username: airflow, Password: airflow)
   - 📚 **API Documentation**: http://localhost:5000/docs
   - 📊 **Grafana Dashboards**: http://localhost:3000 (Username: admin, Password: admin)
   - 📡 **Prometheus Metrics**: http://localhost:9090

5. ⏱️ The data pipeline will run automatically according to the schedule (daily by default)

## 🔌 API Endpoints

The system provides a RESTful API for accessing stock data:

- 📋 `GET /stocks/`: List all stock data with pagination
- 🏷️ `GET /stocks/symbols`: List all available stock symbols
- 📈 `GET /stocks/{symbol}`: Get the latest stock data for a specific symbol
- 📅 `GET /stocks/{symbol}/history`: Get historical stock data for a specific symbol

## 📊 Monitoring and Visualization

The system includes comprehensive monitoring and visualization capabilities:

- 📊 **Grafana Dashboards**: Pre-configured dashboards for stock price trends, volume analysis, and system metrics
- 📡 **Prometheus Metrics**: Real-time monitoring of API performance, data pipeline execution, and system health

## ⚙️ Configuration

You can configure the following parameters in the `.env` file:

- 👤 `POSTGRES_USER`: PostgreSQL username
- 🔑 `POSTGRES_PASSWORD`: PostgreSQL password
- 💾 `POSTGRES_DB`: PostgreSQL database name
- 🏢 `STOCK_SYMBOLS`: Comma-separated list of stock symbols to track (e.g., AAPL,MSFT,GOOGL)
- 👤 `GRAFANA_USER`: Grafana admin username
- 🔑 `GRAFANA_PASSWORD`: Grafana admin password

## 🔧 Extending the System

### 📊 Adding New Data Sources

To add new data sources, create a new Python module in the `scripts` directory and update the Airflow DAG to include the new data fetching task.

### 🎨 Creating Custom Visualizations

You can create Grafana dashboards by importing JSON definitions or using the Grafana UI to build new visualizations.

### 📈 Scaling the System

The system can be scaled horizontally by:
- ➕ Adding more worker nodes for Airflow
- 🔄 Implementing database sharding for PostgreSQL
- 🚀 Setting up Redis clustering for improved caching performance

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## Happy Coding🚀🚀
