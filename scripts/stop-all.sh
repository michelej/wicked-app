#!/bin/bash
# Script to stop all services

echo "Stopping all Wicked App services..."

# Stop MongoDB container
echo "Stopping MongoDB container..."
docker stop wicked-mongodb 2>/dev/null

if [ $? -eq 0 ]; then
    echo "MongoDB stopped successfully"
else
    echo "MongoDB container not running or already stopped"
fi

echo -e "\nNote: Backend and Frontend processes should be stopped manually in their respective terminal windows."
echo "Press Ctrl+C in each terminal window to stop them."
