#!/bin/bash

# Restart script for E-commerce Policy Analyzer

set -e

# Go to project root (directory of this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "♻️  Restarting E-commerce Policy Analyzer..."

echo "🛑 Stopping existing services..."
# Kill backend and common frontend processes (ignore errors if not running)
pkill -f "python main.py" 2>/dev/null || true
pkill -f "node_modules/react-scripts/scripts/start.js" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
pkill -f "serve -s build" 2>/dev/null || true
pkill -f "http-server build" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true

echo "🔓 Freeing ports 8000 and 3000 if in use..."
if command -v lsof >/dev/null 2>&1; then
  for PORT in 8000 3000; do
    PORT_PIDS=$(lsof -ti :"$PORT" 2>/dev/null || true)
    if [ -n "$PORT_PIDS" ]; then
      echo "⚡ Killing PIDs on port $PORT: $PORT_PIDS"
      kill -9 $PORT_PIDS 2>/dev/null || true
    fi
  done
else
  fuser -k 8000/tcp 2>/dev/null || true
  fuser -k 3000/tcp 2>/dev/null || true
fi

sleep 2

echo "🚀 Starting services..."
./start.sh

exit 0


