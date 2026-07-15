# Local Development Setup Script
# This script sets up and runs the Shopify SEO SaaS locally

Write-Host "🚀 Shopify SEO SaaS - Local Development Setup" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python version
Write-Host "Step 1: Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ Found: $pythonVersion" -ForegroundColor Green
    
    if ($pythonVersion -notmatch "3\.1[2-9]") {
        Write-Host "  ⚠️  Warning: Python 3.12+ is recommended" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ Python not found. Please install Python 3.12+" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Check if virtual environment exists
Write-Host "Step 2: Setting up virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "  ✅ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "  Creating virtual environment..." -ForegroundColor Gray
    python -m venv .venv
    Write-Host "  ✅ Virtual environment created" -ForegroundColor Green
}
Write-Host ""

# Step 3: Activate virtual environment and install dependencies
Write-Host "Step 3: Installing dependencies..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes..." -ForegroundColor Gray

# Activate venv and install
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "  ❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: Check Ollama
Write-Host "Step 4: Checking Ollama models..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
    $models = $response.models
    
    if ($models.Count -eq 0) {
        Write-Host "  ⚠️  No Ollama models found!" -ForegroundColor Yellow
        Write-Host "  Please run: ollama pull llama3.2 && ollama pull nomic-embed-text" -ForegroundColor Yellow
    } else {
        Write-Host "  ✅ Ollama is running with $($models.Count) model(s)" -ForegroundColor Green
        foreach ($model in $models) {
            Write-Host "     - $($model.name)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "  ⚠️  Ollama is not running on localhost:11434" -ForegroundColor Yellow
    Write-Host "  AI features will not work. Please start Ollama." -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Check PostgreSQL
Write-Host "Step 5: Checking PostgreSQL..." -ForegroundColor Yellow
Write-Host "  You need PostgreSQL running on localhost:5432" -ForegroundColor Gray
Write-Host "  Database: seo_db, User: seo_user, Password: 123456789" -ForegroundColor Gray
Write-Host ""
Write-Host "  Options to run PostgreSQL:" -ForegroundColor Cyan
Write-Host "    A) Use Docker: docker run -d --name seo_postgres -e POSTGRES_USER=seo_user -e POSTGRES_PASSWORD=123456789 -e POSTGRES_DB=seo_db -p 5432:5432 postgres:16-alpine" -ForegroundColor White
Write-Host "    B) Use Docker Compose: docker compose up -d db" -ForegroundColor White
Write-Host "    C) Use local PostgreSQL installation" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter when PostgreSQL is running"
Write-Host ""

# Step 6: Check Qdrant
Write-Host "Step 6: Checking Qdrant..." -ForegroundColor Yellow
Write-Host "  You need Qdrant running on localhost:6333" -ForegroundColor Gray
Write-Host ""
Write-Host "  Options to run Qdrant:" -ForegroundColor Cyan
Write-Host "    A) Use Docker: docker run -d --name seo_qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant:v1.12.5" -ForegroundColor White
Write-Host "    B) Use Docker Compose: docker compose up -d qdrant" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter when Qdrant is running"
Write-Host ""

# Step 7: Run migrations
Write-Host "Step 7: Running database migrations..." -ForegroundColor Yellow
alembic upgrade head
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Migrations completed" -ForegroundColor Green
} else {
    Write-Host "  ❌ Migration failed. Check database connection." -ForegroundColor Red
    Write-Host ""
    Write-Host "  Quick fix: Run PostgreSQL with Docker:" -ForegroundColor Yellow
    Write-Host "    docker compose up -d db" -ForegroundColor White
    exit 1
}
Write-Host ""

# Step 8: Start the server
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "🎉 Setup complete! Starting the server..." -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "API will be available at:" -ForegroundColor Cyan
Write-Host "  • Main API:     http://localhost:8000" -ForegroundColor White
Write-Host "  • Swagger Docs: http://localhost:8000/api/v1/docs" -ForegroundColor White
Write-Host "  • ReDoc:        http://localhost:8000/api/v1/redoc" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
