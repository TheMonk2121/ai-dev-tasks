#!/usr/bin/env python3
"""
Bootstrap module for evaluation scripts to ensure proper import paths.
"""

import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Global observability initialization guard
_OBS_INIT = False


def init_obs():
    """Initialize observability with guard against multiple initialization."""
    global _OBS_INIT
    if _OBS_INIT:
        return
    try:
        from scripts.monitoring.observability import init_observability

        init_observability(service="ai-dev-tasks")
        print("🔍 Observability initialized for service: ai-dev-tasks")
    except Exception as e:
        print(f"⚠️  Observability initialization failed: {e}")
        print("   Continuing without observability - evaluation will run but without telemetry")
    _OBS_INIT = True
