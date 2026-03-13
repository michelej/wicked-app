#!/bin/bash
# Script to start all services locally

echo "Starting all Wicked App services..."
echo "========================================"

# Start MongoDB
echo -e "\n1. Starting MongoDB..."
./scripts/start-mongodb.sh

sleep 3

# Start Backend in new terminal
echo -e "\n2. Starting Backend (new terminal)..."
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "./scripts/start-backend.sh; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -e "./scripts/start-backend.sh" &
else
    echo "Please run ./scripts/start-backend.sh in a new terminal"
fi

sleep 5

# Start Frontend in new terminal
echo -e "\n3. Starting Frontend (new terminal)..."
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "./scripts/start-frontend.sh; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -e "./scripts/start-frontend.sh" &
else
    echo "Please run ./scripts/start-frontend.sh in a new terminal"
fi

echo -e "\n========================================"
echo "All services started!"
echo -e "\nServices:"
echo "  - MongoDB:  mongodb://localhost:27017"
echo "  - Backend:  http://localhost:8000"
echo "  - Frontend: http://localhost:5173"
echo -e "\nAPI Documentation:"
echo "  - Swagger UI: http://localhost:8000/docs"
echo "  - ReDoc:      http://localhost:8000/redoc"
