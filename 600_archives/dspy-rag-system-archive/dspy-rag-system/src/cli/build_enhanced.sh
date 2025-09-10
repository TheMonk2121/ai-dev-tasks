#!/bin/bash
# Build script for enhanced Go CLI with crash prevention

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UTILS_DIR="${SCRIPT_DIR}/../utils"

echo "🔧 Building Enhanced Go CLI Memory System..."

# Check if Go is installed
if ! command -v go &> /dev/null; then
    echo "❌ Go is not installed. Please install Go 1.21 or later."
    exit 1
fi

# Check Go version
GO_VERSION=$(go version | awk '{print $3}' | sed 's/go//')
REQUIRED_VERSION="1.21"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$GO_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Go version $GO_VERSION is too old. Please install Go $REQUIRED_VERSION or later."
    exit 1
fi

echo "✅ Go version: $GO_VERSION"

# Initialize Go module if needed
if [ ! -f "${UTILS_DIR}/go.mod" ]; then
    echo "📦 Initializing Go module..."
    cd "$UTILS_DIR"
    go mod init github.com/ai-dev-tasks/dspy-rag-system/src/utils
    go mod tidy
fi

# Build the enhanced CLI
echo "🔨 Building enhanced CLI..."
cd "$SCRIPT_DIR"

# Build with optimizations and crash prevention
go build -ldflags="-s -w" -o memory_rehydration_cli_enhanced \
    -tags="crash_prevention,memory_monitoring" \
    memory_rehydration_cli_enhanced.go

# Also build the original CLI for comparison
go build -ldflags="-s -w" -o memory_rehydration_cli \
    memory_rehydration_cli.go

echo "✅ Build complete!"
echo ""
echo "📁 Generated binaries:"
echo "  - memory_rehydration_cli_enhanced (with crash prevention)"
echo "  - memory_rehydration_cli (original)"
echo ""
echo "🚀 Usage:"
echo "  ./memory_rehydration_cli_enhanced --query 'your query'"
echo "  ./memory_rehydration_cli_enhanced --query 'your query' --json"
echo ""
echo "🛡️  Enhanced features:"
echo "  - Connection pooling with health checks"
echo "  - Memory monitoring and limits"
echo "  - Graceful shutdown handling"
echo "  - Panic recovery and error retry"
echo "  - Resource limiting and timeouts"
echo "  - Signal handling (SIGINT, SIGTERM)"

