#!/bin/bash
# Ollama Setup Script for Shopify SEO SaaS
# Run this script to download required models

echo "🚀 Shopify SEO SaaS - Ollama Setup"
echo "=================================================="
echo ""

# Check if Ollama is running
echo "Checking Ollama status..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is running on http://localhost:11434"
    echo ""
else
    echo "❌ Ollama is not running or not accessible"
    echo "Please start Ollama and run this script again"
    exit 1
fi

# List current models
echo "Current installed models:"
response=$(curl -s http://localhost:11434/api/tags)
models=$(echo $response | grep -o '"name":"[^"]*"' | cut -d'"' -f4)

if [ -z "$models" ]; then
    echo "  No models installed yet"
else
    echo "$models" | while read model; do
        echo "  - $model"
    done
fi
echo ""

# Check required models
required_models=("llama3.2" "nomic-embed-text")
missing_models=()

for required in "${required_models[@]}"; do
    if ! echo "$models" | grep -q "$required"; then
        missing_models+=("$required")
    fi
done

if [ ${#missing_models[@]} -eq 0 ]; then
    echo "✅ All required models are installed!"
    echo ""
    echo "You can now start the application with:"
    echo "  docker compose up --build"
    exit 0
fi

# Download missing models
echo "⚠️  Missing required models:"
for model in "${missing_models[@]}"; do
    echo "  - $model"
done
echo ""

read -p "Would you like to download the missing models now? (Y/N): " response
echo ""

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "📥 Downloading required models..."
    echo "This may take a few minutes depending on your internet connection"
    echo ""
    
    for model in "${missing_models[@]}"; do
        echo "Downloading $model..."
        ollama pull "$model"
        echo ""
    done
    
    echo "✅ Setup complete!"
    echo ""
    echo "You can now start the application with:"
    echo "  docker compose up --build"
else
    echo "Setup cancelled. To download models manually, run:"
    for model in "${missing_models[@]}"; do
        echo "  ollama pull $model"
    done
fi

echo ""
echo "For more information, see OLLAMA_SETUP.md"
