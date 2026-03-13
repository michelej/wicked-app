# MongoDB Configuration

MongoDB database service for Wicked App.

## Local Development

### Using Docker

```bash
docker run -d \
  --name wicked-mongodb \
  -p 27017:27017 \
  -v $(pwd)/data:/data/db \
  -e MONGO_INITDB_DATABASE=wicked_db \
  mongo:7.0
```

### Using Local MongoDB Installation

If you have MongoDB installed locally:

```bash
# Start MongoDB service
# Windows:
net start MongoDB

# Linux/Mac:
sudo systemctl start mongod
```

### Connect to MongoDB

```bash
# Using MongoDB Shell
mongosh mongodb://localhost:27017/wicked_db

# Or with Docker:
docker exec -it wicked-mongodb mongosh
```

## Data Persistence

When running with Docker Compose, data is persisted in a Docker volume named `mongodb_data`.

When running locally with the above command, data is stored in `./data` directory.

## Initialization

The `init-mongo.js` script runs automatically when the container is first created if using Docker Compose. It:
- Creates the `wicked_db` database
- Creates the `items` collection
- Inserts sample data
- Creates indexes

## Backup and Restore

### Backup

```bash
docker exec wicked-mongodb mongodump --out /backup
docker cp wicked-mongodb:/backup ./backup
```

### Restore

```bash
docker cp ./backup wicked-mongodb:/backup
docker exec wicked-mongodb mongorestore /backup
```
