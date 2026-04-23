#!/bin/bash

echo "Starting application with database initialization..."

# Wait for database to be ready (especially for PostgreSQL on Render)
echo "Waiting for database to be ready..."
python -c "
import time
import os
from app.database import engine
from sqlalchemy import text

max_retries = 30
retry_interval = 2

for i in range(max_retries):
    try:
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print('Database is ready!')
        break
    except Exception as e:
        print(f'Database connection attempt {i+1}/{max_retries} failed: {e}')
        if i < max_retries - 1:
            time.sleep(retry_interval)
        else:
            print('Database not ready after maximum retries')
            exit(1)
"

# Initialize database
echo "Initializing database..."
python -c "
from app.db_init import initialize_database
if initialize_database():
    print('Database initialization successful')
else:
    print('Database initialization failed')
    exit(1)
"

# Start the application
echo "Starting FastAPI application..."
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
