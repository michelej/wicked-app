#!/bin/bash
# Script to run MongoDB locally using Docker

echo "Starting MongoDB with Docker..."

docker run -d \
  --name wicked-mongodb \
  -p 27017:27017 \
  -v "$(pwd)/database/data:/data/db" \
  -e MONGO_INITDB_DATABASE=wicked_db \
  mongo:7.0

if [ $? -eq 0 ]; then
    echo "MongoDB started successfully on port 27017"
    echo "Connection string: mongodb://localhost:27017"
else
    echo "Failed to start MongoDB. It may already be running."
    echo "Try: docker start wicked-mongodb"
fi
