#!/bin/bash

# Quick Start Script for Enhanced Bedrock Client
# This script helps you get the enhanced Bedrock client running quickly

set -e

echo "🚀 Enhanced Bedrock Client Quick Start"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -f "scripts/enhanced_bedrock_client.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected files: scripts/enhanced_bedrock_client.py"
    exit 1
fi

echo "✅ Project structure verified"
echo ""

# Check Python environment
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check virtual environment
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    if [ -f "venv/bin/activate" ]; then
        # shellcheck source=/dev/null
        source venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ Error: venv/bin/activate not found"
        exit 1
    fi
else
    echo "⚠️ No virtual environment found. Creating one..."
    python3 -m venv venv
    if [ -f "venv/bin/activate" ]; then
        # shellcheck source=/dev/null
        source venv/bin/activate
        echo "✅ Virtual environment created and activated"
    else
        echo "❌ Error: Failed to create virtual environment"
        exit 1
    fi
fi

echo ""

# Install required dependencies
echo "📦 Installing required dependencies..."
pip install boto3 botocore asyncio
echo "✅ Dependencies installed"
echo ""

# Check AWS credentials
echo "🔑 Checking AWS credentials..."
if [ -z "$AWS_ACCESS_KEY_ID" ] && [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "⚠️ AWS credentials not found in environment variables"
    echo "   Please set the following variables:"
    echo "   export AWS_ACCESS_KEY_ID='your_access_key'"
    echo "   export AWS_SECRET_ACCESS_KEY='your_secret_key'"
    echo "   export AWS_REGION='us-east-1'"
    echo ""
    echo "   Or copy and edit the configuration template:"
    echo "   cp config/enhanced_bedrock_config.env .env"
    echo "   nano .env"
    echo ""
    read -r -p "Press Enter after setting credentials, or Ctrl+C to exit..."
else
    echo "✅ AWS credentials found"
    echo "   Access Key: ${AWS_ACCESS_KEY_ID:0:8}..."
    echo "   Region: ${AWS_REGION:-'not set'}"
fi

echo ""

# Test the enhanced client
echo "🧪 Testing Enhanced Bedrock Client..."
echo ""

if python3 scripts/test_enhanced_bedrock.py; then
    echo ""
    echo "🎉 Enhanced Bedrock Client is working!"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Review the test results above"
    echo "   2. Configure additional API keys if needed (optional)"
    echo "   3. Integrate with RAGChecker:"
    echo "      python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli"
    echo "   4. Monitor performance improvements"
    echo ""
    echo "📚 For detailed integration instructions, see:"
    echo "   400_guides/400_enhanced-bedrock-ragchecker-integration.md"
    echo ""
else
    echo ""
    echo "❌ Enhanced Bedrock Client test failed"
    echo ""
    echo "🔍 Troubleshooting:"
    echo "   1. Check AWS credentials and permissions"
    echo "   2. Verify Bedrock service access in your region"
    echo "   3. Check network connectivity"
    echo "   4. Review error messages above"
    echo ""
    echo "📚 For help, see the troubleshooting guide in:"
    echo "   400_guides/400_enhanced-bedrock-ragchecker-integration.md"
    echo ""
    exit 1
fi

echo "✨ Quick start completed successfully!"
echo "   You're now ready to use the Enhanced Bedrock Client with RAGChecker"
