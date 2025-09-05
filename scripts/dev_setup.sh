#!/bin/bash
# Development Environment Setup

echo "🚀 Setting up development environment..."

# Install dependencies
uv sync --extra dev

# Run pre-commit install
uv run pre-commit install

# Run system health check
uv run python scripts/system_health_check.py

echo "✅ Development environment ready!"
