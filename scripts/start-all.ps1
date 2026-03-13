# Script to start all services locally
Write-Host "Starting all Wicked App services..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# Start MongoDB
Write-Host "`n1. Starting MongoDB..." -ForegroundColor Yellow
& "$PSScriptRoot\start-mongodb.ps1"

Start-Sleep -Seconds 3

# Start Backend in new window
Write-Host "`n2. Starting Backend (new window)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-File", "$PSScriptRoot\start-backend.ps1"

Start-Sleep -Seconds 5

# Start Frontend in new window
Write-Host "`n3. Starting Frontend (new window)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-File", "$PSScriptRoot\start-frontend.ps1"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "All services started!" -ForegroundColor Green
Write-Host "`nServices:" -ForegroundColor Cyan
Write-Host "  - MongoDB:  mongodb://localhost:27017" -ForegroundColor White
Write-Host "  - Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  - Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "`nAPI Documentation:" -ForegroundColor Cyan
Write-Host "  - Swagger UI: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - ReDoc:      http://localhost:8000/redoc" -ForegroundColor White
