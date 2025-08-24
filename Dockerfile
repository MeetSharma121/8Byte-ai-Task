FROM apache/airflow:2.5.1

USER root

# Install additional dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Copy requirements file
COPY requirements.txt /requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /requirements.txt

# Create directories for scripts and logs
RUN mkdir -p /opt/airflow/scripts /opt/airflow/logs

# Set working directory
WORKDIR /opt/airflow