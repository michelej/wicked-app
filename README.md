# Wicked App

A full-stack application with FastAPI, MongoDB, and Vue.js.

## Architecture

- **Backend**: FastAPI with Poetry (Python 3.11)
- **Database**: MongoDB
- **Frontend**: Vue.js 3 with Pinia, PrimeVue, and Vite

## Quick Start with Docker Compose

### Prerequisites

- Docker and Docker Compose installed

### Run All Services

```bash
docker-compose up -d
```

This will start all three services:
- MongoDB: http://localhost:27017
- Backend API: http://localhost:8000
- Frontend: http://localhost:5173

### Stop All Services

```bash
docker-compose down
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### Rebuild Services

```bash
# Rebuild all
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build backend
```

## Local Development

Each service can be run independently for local development.

### 1. MongoDB

**Option A: Using Docker**
```bash
docker run -d --name wicked-mongodb -p 27017:27017 mongo:latest
```

**Option B: Local Installation**
- Install MongoDB from https://www.mongodb.com/try/download/community
- Start MongoDB service

### 2. Backend

```bash
cd backend

# Install Poetry if not already installed
pip install poetry

# Install dependencies
poetry install

# Copy environment file
cp .env.example .env

# Run the application
poetry run uvicorn main:app --reload
```

Backend will be available at http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Run the application
npm run dev
```

Frontend will be available at http://localhost:5173

## Running Individual Services with Docker

### MongoDB Only

```bash
docker-compose up -d mongodb
```

### Backend Only

```bash
# Make sure MongoDB is running first
docker-compose up -d mongodb
docker-compose up -d backend
```

### Frontend Only

```bash
# Make sure Backend is running first
docker-compose up -d mongodb backend
docker-compose up -d frontend
```

## Project Structure

```
wicked-app/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # API routes
│   │   └── core/        # Core configuration
│   ├── main.py          # Application entry point
│   ├── pyproject.toml   # Poetry dependencies
│   ├── Dockerfile
│   └── README.md
├── database/            # MongoDB configuration
│   ├── init-mongo.js    # Database initialization script
│   └── README.md
├── frontend/            # Vue.js application
│   ├── src/
│   │   ├── views/       # View components
│   │   ├── stores/      # Pinia stores
│   │   ├── services/    # API services
│   │   └── router/      # Vue Router
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── README.md
└── docker-compose.yml   # Docker Compose configuration
```

## Environment Variables

### Backend (.env)
- `MONGODB_URL`: MongoDB connection string
- `MONGODB_DB_NAME`: Database name
- `API_HOST`: API host
- `API_PORT`: API port
- `CORS_ORIGINS`: Allowed CORS origins

### Frontend (.env)
- `VITE_API_URL`: Backend API URL

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/items` - Get all items
- `POST /api/items` - Create new item
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## Development Tools

### Backend
```bash
cd backend

# Format code
poetry run black .

# Lint code
poetry run ruff check .

# Run tests
poetry run pytest
```

### Frontend
```bash
cd frontend

# Lint code
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

## Troubleshooting

### Port Already in Use

If you get port conflicts, you can modify the ports in `docker-compose.yml` or stop the conflicting services.

### MongoDB Connection Issues

Ensure MongoDB is running and accessible. Check the `MONGODB_URL` in your backend `.env` file.

### Frontend Cannot Connect to Backend

- Verify the backend is running
- Check `VITE_API_URL` in frontend `.env` file
- For Docker, ensure all services are on the same network

## Production Deployment

For production deployment:

1. Update environment variables
2. Build production images:
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```
3. Use a reverse proxy (nginx) for routing
4. Enable HTTPS/SSL
5. Set up proper authentication and authorization
6. Configure database backups

## License

MIT
