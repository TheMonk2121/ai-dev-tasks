# src/common/db_dsn.py
import json
import os
import sys
from typing import Optional
from urllib.parse import urlparse

CANON_ENV = "DATABASE_URL"  # canonical
FALLBACK_ENV = "POSTGRES_DSN"  # temporary fallback during transition


def _parse(dsn: str) -> dict[str, str | int]:
    """Parse DSN into components for comparison.

    Returns a mapping with keys: scheme, user, host, port, db.
    Returns an empty dict on parse failure.
    """
    try:
        u = urlparse(dsn)
        return {
            "scheme": u.scheme,
            "user": (u.username or ""),
            "host": (u.hostname or ""),
            "port": (u.port or 5432),
            "db": (u.path or "").lstrip("/"),
        }
    except Exception:
        return {}


def resolve_dsn(strict: bool = True, emit_warning: bool = True) -> str | None:
    """
    Resolve database connection string with fallback logic.

    Args:
        strict: If True, raise RuntimeError when no DSN found
        emit_warning: If True, print warnings to stderr

    Returns:
        Resolved DSN string, or None if not found and not strict.
    """
    primary = os.getenv(CANON_ENV, "").strip()
    fallback = os.getenv(FALLBACK_ENV, "").strip()
    chosen = primary or fallback

    if not chosen:
        msg = f"Neither {CANON_ENV} nor {FALLBACK_ENV} set."
        if strict:
            raise RuntimeError(msg)
        if emit_warning:
            print(f"[DSN] WARN: {msg}", file=sys.stderr)
        return None

    # Parse for mismatch detection
    p = _parse(primary) if primary else {}
    f = _parse(fallback) if fallback else {}

    # Check for host/db mismatches
    mismatch = bool(primary and fallback and (p.get("host"), p.get("db")) != (f.get("host"), f.get("db")))

    # Build audit info
    audit = {
        "env": {CANON_ENV: primary, FALLBACK_ENV: fallback},
        "chosen": chosen,
        "mismatch_host_db": mismatch,
        "primary_parsed": p,
        "fallback_parsed": f,
    }

    # Warn on mismatches
    if emit_warning and mismatch:
        print(
            f"[DSN] WARN: {CANON_ENV} and {FALLBACK_ENV} disagree on host/db: "
            f"{p.get('host')}/{p.get('db')} vs {f.get('host')}/{f.get('db')}",
            file=sys.stderr,
        )

    # Write audit artifact (tolerate failures)
    try:
        with open("dsn_audit.json", "w") as fjson:
            json.dump(audit, fjson, indent=2)
    except Exception:
        pass

    return chosen
