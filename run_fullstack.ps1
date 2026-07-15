# Full Stack Local Development Script
# Runs both Backend (FastAPI) and Frontend (Next.js) locally

Write-Host "🚀 Shopify SEO SaaS - Full Stack Development" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Check if frontend/.env exists
if (-not (Test-Path "frontend/.env")) {
    Write-Host "Creating frontend/.env file..." -ForegroundColor Yellow
    Copy-Item "frontend/.env.example" "frontend/.env"
    Write-Host "  ✅ Frontend .env created" -ForegroundColor Green
}

# Step 1: Start Dependencies
Write-Host "Step 1: Starting dependencies (PostgreSQL, Qdrant, Ollama)..." -ForegroundColor Yellow
Write-Host ""

# Check Ollama
Write-Host "  Checking Ollama..." -ForegroundColor Gray
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
    $models = $response.models
    
    $hasLLM = $false
    $hasEmbed = $false
    
    foreach ($model in $models) {
        if ($model.name -like "llama*" -or $model.name -like "mistral*") {
            $hasLLM = $true
        }
        if ($model.name -like "nomic-embed-text*") {
            $hasEmbed = $true
        }
    }
    
    if ($hasLLM -and $hasEmbed) {
        Write-Host "  ✅ Ollama ready with required models" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Ollama missing required models" -ForegroundColor Yellow
        if (-not $hasLLM) {
            Write-Host "     Run: ollama pull llama3.2" -ForegroundColor Yellow
        }
        if (-not $hasEmbed) {
            Write-Host "     Run: ollama pull nomic-embed-text" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "  ❌ Ollama not running on localhost:11434" -ForegroundColor Red
    Write-Host "     Please start Ollama first" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Starting PostgreSQL and Qdrant..." -ForegroundColor Gray
docker compose up -d db qdrant

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Docker services started" -ForegroundColor Green
} else {
    Write-Host "  ❌ Failed to start Docker services" -ForegroundColor Red
    Write-Host "     Make sure Docker Desktop is running" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "  Waiting for services to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Step 2: Setup Backend
Write-Host "Step 2: Setting up backend..." -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path ".venv")) {
    Write-Host "  Creating virtual environment..." -ForegroundColor Gray
    python -m venv .venv
}

Write-Host "  Activating virtual environment..." -ForegroundColor Gray
& .\.venv\Scripts\Activate.ps1

Write-Host "  Installing backend dependencies..." -ForegroundColor Gray
pip install --upgrade pip -q
pip install -e ".[dev]" -q

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Backend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ❌ Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "  Running database migrations..." -ForegroundColor Gray
alembic upgrade head

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Database migrations completed" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Migration failed (might be okay if already up to date)" -ForegroundColor Yellow
}

# Step 3: Setup Frontend
Write-Host ""
Write-Host "Step 3: Setting up frontend..." -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path "frontend/node_modules")) {
    Write-Host "  Installing frontend dependencies..." -ForegroundColor Gray
    Set-Location frontend
    npm install
    Set-Location ..
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Frontend dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Failed to install frontend dependencies" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✅ Frontend dependencies already installed" -ForegroundColor Green
}

# Step 4: Start Services
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "🎉 Setup complete! Starting servers..." -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "Services will be available at:" -ForegroundColor Cyan
Write-Host "  • Backend API:       http://localhost:8000" -ForegroundColor White
Write-Host "  • API Docs:          http://localhost:8000/api/v1/docs" -ForegroundColor White
Write-Host "  • Frontend:          http://localhost:3000" -ForegroundColor White
Write-Host "  • Qdrant Dashboard:  http://localhost:6333/dashboard" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all servers" -ForegroundColor Gray
Write-Host ""

Start-Sleep -Seconds 2

# Start backend in background
Write-Host "Starting backend server..." -ForegroundColor Yellow
$backend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -PassThru

Start-Sleep -Seconds 3

# Start frontend in background
Write-Host "Starting frontend server..." -ForegroundColor Yellow
$frontend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev" -PassThru

Write-Host ""
Write-Host "✅ Both servers are starting in separate windows!" -ForegroundColor Green
Write-Host ""
Write-Host "Backend PID: $($backend.Id)" -ForegroundColor Gray
Write-Host "Frontend PID: $($frontend.Id)" -ForegroundColor Gray
Write-Host ""
Write-Host "To stop servers:" -ForegroundColor Yellow
Write-Host "  - Close the terminal windows" -ForegroundColor White
Write-Host "  - Or run: Stop-Process -Id $($backend.Id),$($frontend.Id)" -ForegroundColor White
Write-Host ""
Write-Host "Opening frontend in browser in 5 seconds..." -ForegroundColor Cyan
Start-Sleep -Seconds 5
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Press Enter to stop all servers and exit..." -ForegroundColor Yellow
Read-Host

# Cleanup
Write-Host "Stopping servers..." -ForegroundColor Yellow
Stop-Process -Id $backend.Id -ErrorAction SilentlyContinue
Stop-Process -Id $frontend.Id -ErrorAction SilentlyContinue
Write-Host "✅ Servers stopped" -ForegroundColor Green
