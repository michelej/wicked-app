#!/bin/bash
# Script to run the Vue.js frontend locally

echo "Starting Vue.js Frontend..."

cd frontend || exit

# Check if .env exists, if not create from example
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
fi

# Check if node_modules exists
if [ ! -d node_modules ]; then
    echo "Installing dependencies with npm..."
    npm install
fi

# Run the application
echo "Starting Vite dev server..."
npm run dev
