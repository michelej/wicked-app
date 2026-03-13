# 🚀 Quick Start Guide

Welcome to Wicked App! This guide will help you get up and running quickly.

## Choose Your Method

### Option 1: Docker Compose (Recommended)

The easiest way to run all services together:

```bash
docker-compose up -d
```

**Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MongoDB: mongodb://localhost:27017

**Stop all services:**
```bash
docker-compose down
```

---

### Option 2: Local Development

Run each service individually for development.

#### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (for MongoDB)

#### Quick Start (Windows)

```powershell
# Start all services at once
.\scripts\start-all.ps1
```

Or start individually:
```powershell
# Terminal 1: MongoDB
.\scripts\start-mongodb.ps1

# Terminal 2: Backend
.\scripts\start-backend.ps1

# Terminal 3: Frontend
.\scripts\start-frontend.ps1
```

#### Quick Start (Linux/Mac)

```bash
# Make scripts executable first
chmod +x scripts/*.sh

# Start all services at once
./scripts/start-all.sh
```

Or start individually:
```bash
# Terminal 1: MongoDB
./scripts/start-mongodb.sh

# Terminal 2: Backend
./scripts/start-backend.sh

# Terminal 3: Frontend
./scripts/start-frontend.sh
```

---

## What's Included?

### Backend (FastAPI)
- RESTful API with FastAPI
- MongoDB integration with Motor
- Poetry for dependency management
- Auto-generated API documentation
- CORS enabled for frontend

### Database (MongoDB)
- NoSQL database
- Sample data initialization
- Docker-based deployment

### Frontend (Vue.js)
- Vue 3 with Composition API
- Pinia for state management
- PrimeVue UI components
- Vite for fast development
- Axios for API calls

---

## First Steps

1. **Start the application** using one of the methods above

2. **Open the frontend** at http://localhost:5173

3. **Try the API** at http://localhost:8000/docs

4. **Add some items** using the frontend interface

---

## Troubleshooting

### Port Already in Use
If ports 8000, 5173, or 27017 are already in use, you can:
- Stop the conflicting service
- Modify the ports in `docker-compose.yml` or `.env` files

### MongoDB Connection Failed
- Make sure Docker is running
- Check that MongoDB container is healthy: `docker ps`
- Verify the connection string in `backend/.env`

### Frontend Can't Connect to Backend
- Ensure backend is running on port 8000
- Check `VITE_API_URL` in `frontend/.env`
- Verify CORS settings in `backend/app/core/config.py`

---

## Next Steps

- Read detailed documentation in [README.md](README.md)
- Explore the API documentation at http://localhost:8000/docs
- Check individual service READMEs in `backend/`, `frontend/`, and `database/` folders
- Customize the application to fit your needs

---

## Useful Commands

### Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend

# Rebuild and start
docker-compose up -d --build

# Stop and remove everything
docker-compose down -v
```

### Development
```bash
# Backend
cd backend
poetry install          # Install dependencies
poetry run pytest       # Run tests
poetry run black .      # Format code

# Frontend
cd frontend
npm install            # Install dependencies
npm run dev           # Start dev server
npm run build         # Build for production
npm run lint          # Lint code
```

---

**Happy coding! 🎉**
