#!/usr/bin/env bash
# Setup script for Model Switcher
# Installs Ollama and pulls required models for the DSPy multi-agent system.

set -e

echo "🚀 Setting up Model Switcher for DSPy Multi-Agent System..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "📦 Installing Ollama..."

    # Install Ollama on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        echo "❌ Ollama installation not supported on this OS"
        echo "Please install Ollama manually: https://ollama.ai/download"
        exit 1
    fi
else
    echo "✅ Ollama already installed"
fi

# Start Ollama service
echo "🔧 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to start
echo "⏳ Waiting for Ollama to start..."
sleep 5

# Pull required models
echo "📥 Pulling required models..."

echo "   Pulling Llama 3.1 8B (for planning, research, reasoning)..."
ollama pull llama3.1:8b

echo "   Pulling Mistral 7B (for fast completions, rapid prototyping)..."
ollama pull mistral:7b

echo "   Pulling Phi-3.5 3.8B (for large context tasks)..."
ollama pull phi3.5:3.8b

# Test models
echo "🧪 Testing models..."

echo "   Testing Llama 3.1 8B..."
ollama run llama3.1:8b "Hello, I'm Llama 3.1 8B. Ready for planning and reasoning tasks!"

echo "   Testing Mistral 7B..."
ollama run mistral:7b "Hello, I'm Mistral 7B. Ready for fast completions!"

echo "   Testing Phi-3.5 3.8B..."
ollama run phi3.5:3.8b "Hello, I'm Phi-3.5 3.8B. Ready for large context tasks!"

# List available models
echo "📋 Available models:"
ollama list

echo ""
echo "✅ Model Switcher setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Run the test script: python test_model_switcher.py"
echo "2. Integrate with your DSPy system"
echo "3. Update B-1003 with model switching capabilities"
echo ""
echo "💡 Usage examples:"
echo "   ollama run llama3.1:8b 'Plan a Python project'"
echo "   ollama run mistral:7b 'Write a quick function'"
echo "   ollama run phi3.5:3.8b 'Analyze this large document'"
echo ""
echo "🔧 To stop Ollama: kill $OLLAMA_PID"
