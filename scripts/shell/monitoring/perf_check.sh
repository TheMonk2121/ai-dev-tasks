#!/bin/bash
# Performance Check

echo "📊 Running performance checks..."

# Monitor UV performance
python scripts/uv_performance_monitor.py

# Check dependencies
python scripts/uv_dependency_manager.py --analyze

# Security scan
python scripts/uv_dependency_manager.py --security

echo "✅ Performance checks completed!"
