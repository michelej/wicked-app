# Script to run the Vue.js frontend locally
Write-Host "Starting Vue.js Frontend..." -ForegroundColor Green

Set-Location frontend

# Check if .env exists, if not create from example
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
}

# Check if node_modules exists
if (-not (Test-Path node_modules)) {
    Write-Host "Installing dependencies with npm..." -ForegroundColor Cyan
    npm install
}

# Run the application
Write-Host "Starting Vite dev server..." -ForegroundColor Green
npm run dev
