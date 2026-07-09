# ==========================================
# Ethara Backend — for Render deployment
# Frontend is deployed separately on Vercel.
# ==========================================
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for psycopg2 (PostgreSQL driver)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ ./

# Expose the port Render assigns via $PORT env var
EXPOSE 8000

# On startup: seed if DB is empty, then launch API server
CMD ["sh", "-c", "python seed_if_empty.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
