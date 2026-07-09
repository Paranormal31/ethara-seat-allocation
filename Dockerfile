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

# Render assigns PORT dynamically (default 10000 on free tier)
EXPOSE 10000

# On startup: seed DB in background (so uvicorn opens port immediately to satisfy Render healthcheck)
# and use exec so uvicorn runs as PID 1 to receive signals correctly.
CMD ["sh", "-c", "python seed_if_empty.py & exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]

