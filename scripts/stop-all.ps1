# Script to stop all services
Write-Host "Stopping all Wicked App services..." -ForegroundColor Yellow

# Stop MongoDB container
Write-Host "Stopping MongoDB container..." -ForegroundColor Cyan
docker stop wicked-mongodb 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "MongoDB stopped successfully" -ForegroundColor Green
} else {
    Write-Host "MongoDB container not running or already stopped" -ForegroundColor Yellow
}

Write-Host "`nNote: Backend and Frontend processes should be stopped manually in their respective terminal windows." -ForegroundColor Cyan
Write-Host "Press Ctrl+C in each terminal window to stop them." -ForegroundColor Cyan
