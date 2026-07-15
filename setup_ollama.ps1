# Ollama Setup Script for Shopify SEO SaaS
# Run this script to download required models

Write-Host "🚀 Shopify SEO SaaS - Ollama Setup" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

# Check if Ollama is running
Write-Host "Checking Ollama status..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
    Write-Host "✅ Ollama is running on http://localhost:11434" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Ollama is not running or not accessible" -ForegroundColor Red
    Write-Host "Please start Ollama and run this script again" -ForegroundColor Red
    exit 1
}

# List current models
Write-Host "Current installed models:" -ForegroundColor Yellow
$models = $response.models
if ($models.Count -eq 0) {
    Write-Host "  No models installed yet" -ForegroundColor Gray
} else {
    foreach ($model in $models) {
        Write-Host "  - $($model.name)" -ForegroundColor Green
    }
}
Write-Host ""

# Check if required models are installed
$requiredModels = @("llama3.2", "nomic-embed-text")
$missingModels = @()

foreach ($required in $requiredModels) {
    $found = $false
    foreach ($model in $models) {
        if ($model.name -like "$required*") {
            $found = $true
            break
        }
    }
    if (-not $found) {
        $missingModels += $required
    }
}

if ($missingModels.Count -eq 0) {
    Write-Host "✅ All required models are installed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now start the application with:" -ForegroundColor Cyan
    Write-Host "  docker compose up --build" -ForegroundColor White
    exit 0
}

# Download missing models
Write-Host "⚠️  Missing required models:" -ForegroundColor Yellow
foreach ($model in $missingModels) {
    Write-Host "  - $model" -ForegroundColor Red
}
Write-Host ""

Write-Host "Would you like to download the missing models now? (Y/N)" -ForegroundColor Cyan
$response = Read-Host

if ($response -eq "Y" -or $response -eq "y") {
    Write-Host ""
    Write-Host "📥 Downloading required models..." -ForegroundColor Cyan
    Write-Host "This may take a few minutes depending on your internet connection" -ForegroundColor Gray
    Write-Host ""
    
    foreach ($model in $missingModels) {
        Write-Host "Downloading $model..." -ForegroundColor Yellow
        
        # Try to find ollama.exe
        $ollamaPath = $null
        $possiblePaths = @(
            "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe",
            "$env:ProgramFiles\Ollama\ollama.exe",
            "$env:USERPROFILE\AppData\Local\Programs\Ollama\ollama.exe"
        )
        
        foreach ($path in $possiblePaths) {
            if (Test-Path $path) {
                $ollamaPath = $path
                break
            }
        }
        
        if ($ollamaPath) {
            Write-Host "Found Ollama at: $ollamaPath" -ForegroundColor Gray
            & $ollamaPath pull $model
        } else {
            Write-Host "Could not find ollama.exe automatically." -ForegroundColor Yellow
            Write-Host "Please run manually in a new terminal:" -ForegroundColor Yellow
            Write-Host "  ollama pull $model" -ForegroundColor White
        }
        Write-Host ""
    }
    
    Write-Host "✅ Setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now start the application with:" -ForegroundColor Cyan
    Write-Host "  docker compose up --build" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "Setup cancelled. To download models manually, run:" -ForegroundColor Yellow
    foreach ($model in $missingModels) {
        Write-Host "  ollama pull $model" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "For more information, see OLLAMA_SETUP.md" -ForegroundColor Gray
