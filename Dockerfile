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

# Force Python stdout to be unbuffered so seed logs appear in Render immediately
ENV PYTHONUNBUFFERED=1

# Render assigns PORT dynamically (default 10000 on free tier)
EXPOSE 10000

# Seed DB first (fast bulk inserts ~30-60s), then start API server.
CMD ["sh", "-c", "python -u seed_if_empty.py && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]



