# Wicked App - Backend

FastAPI backend service with MongoDB integration.

## Prerequisites

- Python 3.11+
- Poetry
- MongoDB (if running locally)

## Local Development

### Install Dependencies

```bash
# Install Poetry if not already installed
pip install poetry

# Install dependencies
poetry install
```

### Configuration

Copy `.env.example` to `.env` and configure your environment variables:

```bash
cp .env.example .env
```

### Run Locally

Make sure MongoDB is running locally (or update MONGODB_URL in .env), then:

```bash
# Activate Poetry shell
poetry shell

# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

### API Documentation

Once running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker

### Build Image

```bash
docker build -t wicked-backend .
```

### Run Container

```bash
docker run -p 8000:8000 --env-file .env wicked-backend
```

## Testing

```bash
poetry run pytest
```

## Format Code

```bash
poetry run black .
poetry run ruff check .
```
