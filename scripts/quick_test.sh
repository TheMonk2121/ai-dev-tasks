#!/bin/bash
# Quick Test Runner

echo "🧪 Running quick tests..."

# Run linting
uvx ruff check .

# Run tests
uv run pytest tests/ -v --tb=short

# Run type checking
uv run python -m pyright

echo "✅ Quick tests completed!"
