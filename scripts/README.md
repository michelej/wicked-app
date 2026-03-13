# Wicked App - Local Development Scripts

This directory contains scripts to help you run the application services locally.

## Windows (PowerShell)

### Start Individual Services

```powershell
# Start MongoDB
.\scripts\start-mongodb.ps1

# Start Backend
.\scripts\start-backend.ps1

# Start Frontend
.\scripts\start-frontend.ps1
```

### Start All Services

```powershell
# Starts all three services (MongoDB, Backend, Frontend)
.\scripts\start-all.ps1
```

### Stop All Services

```powershell
.\scripts\stop-all.ps1
```

## Linux/Mac (Bash)

### Make Scripts Executable

```bash
chmod +x scripts/*.sh
```

### Start Individual Services

```bash
# Start MongoDB
./scripts/start-mongodb.sh

# Start Backend
./scripts/start-backend.sh

# Start Frontend
./scripts/start-frontend.sh
```

### Start All Services

```bash
# Starts all three services (MongoDB, Backend, Frontend)
./scripts/start-all.sh
```

### Stop All Services

```bash
./scripts/stop-all.sh
```

## What Each Script Does

### start-mongodb
- Starts MongoDB in a Docker container
- Exposes port 27017
- Creates a data volume for persistence
- Initializes the database with sample data

### start-backend
- Creates `.env` file if it doesn't exist
- Installs Poetry if needed
- Installs Python dependencies
- Starts the FastAPI server on port 8000

### start-frontend
- Creates `.env` file if it doesn't exist
- Installs npm dependencies if needed
- Starts the Vite dev server on port 5173

### start-all
- Starts MongoDB
- Opens Backend in a new terminal window
- Opens Frontend in a new terminal window
- Displays service URLs

### stop-all
- Stops the MongoDB Docker container
- Provides instructions for stopping Backend and Frontend

## Notes

- **Windows**: Scripts automatically open new PowerShell windows for Backend and Frontend
- **Linux/Mac**: Scripts try to use `gnome-terminal` or `xterm` for new windows
- If automatic terminal opening doesn't work, manually run the individual scripts in separate terminals
- Make sure Docker is running before starting MongoDB
- Backend requires MongoDB to be running first
- Frontend requires Backend to be running for full functionality
