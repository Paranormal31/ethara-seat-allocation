#!/bin/sh
set -e

echo "==> Starting Ethara backend..."
echo "==> PORT is: "

# Run DB seed in background so the port opens immediately
echo "==> Running seed check in background..."
python seed_if_empty.py &

# Start uvicorn immediately (Render needs a port open fast)
echo "==> Launching uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 
