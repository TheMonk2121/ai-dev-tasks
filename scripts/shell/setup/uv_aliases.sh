#!/bin/bash
# UV Workflow Aliases

alias uvd='uv sync --extra dev'
alias uvt='uv run pytest'
alias uvl='uv run python -m lint'
alias uvf='uvx black . && uvx isort .'
alias uvs='uv run python scripts/system_health_check.py'
alias uvp='uv run python scripts/uv_performance_monitor.py'
