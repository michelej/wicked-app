# Script to run the FastAPI backend locally
Write-Host "Starting FastAPI Backend..." -ForegroundColor Green

Set-Location backend

# Check if .env exists, if not create from example
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
}

# Check if Poetry is installed
if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
    Write-Host "Poetry not found. Installing Poetry..." -ForegroundColor Yellow
    pip install poetry
}

# Install dependencies
Write-Host "Installing dependencies with Poetry..." -ForegroundColor Cyan
poetry install

# Run the application
Write-Host "Starting FastAPI server..." -ForegroundColor Green
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
