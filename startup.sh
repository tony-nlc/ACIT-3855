#!/bin/bash
source venv/bin/activate
docker compose up

python storage/drop_tables.py
python storage/create_tables.py
echo "Starting Receiver..."
python receiver/receiver.py &

echo "Starting Processing..."
python processing/processing.py &

echo "Starting Storage..."
python storage/storage.py &

echo "All services started."
