# Restart Backend Script

Write-Host "🔄 Restarting Backend..." -ForegroundColor Cyan

# Stop any running Python processes
Write-Host "⏹️  Stopping existing backend processes..." -ForegroundColor Yellow
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*seo*"} | Stop-Process -Force
Start-Sleep -Seconds 2

# Verify Docker containers are running
Write-Host "🐳 Checking Docker containers..." -ForegroundColor Yellow
$postgres = docker ps --filter name=seo_postgres --format "{{.Status}}"
$qdrant = docker ps --filter name=seo_qdrant --format "{{.Status}}"

if (-not $postgres) {
    Write-Host "❌ PostgreSQL not running! Starting containers..." -ForegroundColor Red
    docker compose up -d db qdrant
    Start-Sleep -Seconds 5
} else {
    Write-Host "✅ PostgreSQL: $postgres" -ForegroundColor Green
    Write-Host "✅ Qdrant: $qdrant" -ForegroundColor Green
}

# Start backend server
Write-Host "🚀 Starting backend server..." -ForegroundColor Green
Write-Host "   Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   API Docs: http://localhost:8000/api/v1/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

.venv/Scripts/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
