from __future__ import annotations
import os
from typing import Any
    import logfire
from typing import Any, Dict, List, Optional, Union
"""Logfire/observability initializer used across entrypoints.

Keeps configuration centralized and optional. If a Logfire token is present,
we emit traces and instrument Pydantic AI; otherwise, we no-op.
"""



try:
except Exception:  # pragma: no cover - optional dependency
    logfire = None  # type: ignore[assignment]


def init_observability(service_name: str = "ai-dev-tasks", environment: str | None = None) -> dict[str, Any]:
    """Initialize Logfire if available and token is present.

    Returns a dict describing initialization outcome for callers/tests.
    """
    env = environment or os.getenv("APP_ENV", "dev")
    token_present = bool(os.getenv("LOGFIRE_API_KEY") or os.getenv("APP_OBS__LOGFIRE_TOKEN"))

    if logfire is None or not token_present:
        return {"enabled": False, "reason": "no-logfire-or-token"}

    try:
        logfire.configure(
            send_to_logfire="if-token-present",
            environment=env,
            service_name=service_name,
        )
        # Instrument all Pydantic AI agents/models if imported anywhere
        try:
            logfire.instrument_pydantic_ai()  # type: ignore[attr-defined]
        except Exception:
            # Safe to continue even if pydantic-ai is not present
            pass
        return {"enabled": True, "environment": env}
    except Exception as e:  # pragma: no cover - defensive
        return {"enabled": False, "reason": str(e)}
