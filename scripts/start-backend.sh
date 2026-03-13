#!/bin/bash
# Script to run the FastAPI backend locally

echo "Starting FastAPI Backend..."

cd backend || exit

# Check if .env exists, if not create from example
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
fi

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing Poetry..."
    pip install poetry
fi

# Install dependencies
echo "Installing dependencies with Poetry..."
poetry install

# Run the application
echo "Starting FastAPI server..."
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
