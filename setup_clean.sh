#!/bin/bash
# Kill any running python app
pkill -f "python app.py" || true
lsof -ti:5000 | xargs kill -9 || true
sleep 2

# Reset DB explicitly to ensure schema is correct
./venv/bin/python reset_db.py

# Start app in background
./venv/bin/python app.py > app.log 2>&1 &
APP_PID=$!
echo "App started with PID $APP_PID"
sleep 5

# Init DB (fetches schedule)
curl http://127.0.0.1:5000/api/init

echo "Waiting for scheduler to pick up jobs (or use manual trigger)..."


