# Dockerfile for GORE_OS ETL Environment
# Provides Python 3.11 + Postgres client dependencies

FROM python:3.11-slim

# Install system dependencies for psycopg2 and building
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY etl/requirements.txt ./etl/requirements.txt
RUN pip install --no-cache-dir -r etl/requirements.txt

# Copy ETL source code and model (needed for schema generation/mapping)
COPY etl/ ./etl/
COPY model/ ./model/

# Create a placeholder for the app's db schema if needed
# COPY src/db/schema/ ./src/db/schema/

# Keep the container alive for manual script execution or cron jobs
CMD ["tail", "-f", "/dev/null"]
