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

# Copy and make the startup script executable
COPY backend/start.sh ./start.sh
RUN chmod +x ./start.sh

# Render assigns PORT dynamically (default 10000 on free tier)
EXPOSE 10000

# Use start.sh: seeds in background, uvicorn starts immediately
CMD ["./start.sh"]
