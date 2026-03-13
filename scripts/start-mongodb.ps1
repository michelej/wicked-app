# Script to run MongoDB locally using Docker
Write-Host "Starting MongoDB with Docker..." -ForegroundColor Green

docker run -d `
  --name wicked-mongodb `
  -p 27017:27017 `
  -v ${PWD}/database/data:/data/db `
  -e MONGO_INITDB_DATABASE=wicked_db `
  mongo:7.0

if ($LASTEXITCODE -eq 0) {
    Write-Host "MongoDB started successfully on port 27017" -ForegroundColor Green
    Write-Host "Connection string: mongodb://localhost:27017" -ForegroundColor Cyan
} else {
    Write-Host "Failed to start MongoDB. It may already be running." -ForegroundColor Yellow
    Write-Host "Try: docker start wicked-mongodb" -ForegroundColor Cyan
}
