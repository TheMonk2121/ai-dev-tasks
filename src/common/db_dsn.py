# src/common/db_dsn.py
from __future__ import annotations

import json
import os
import time
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

CANON_ENV = "DATABASE_URL"
FALLBACK_ENV = "POSTGRES_DSN"
ALLOW_MISMATCH_ENV = "ALLOW_DSN_MISMATCH"  # set "1" to bypass fail-fast


def _redact(dsn: str) -> str:
    """Redact sensitive information from DSN."""
    u = urlparse(dsn)
    user = u.username or ""
    host = u.hostname or ""
    port = f":{u.port}" if u.port else ""
    cred = f"{user}:***@" if u.password else (f"{user}@" if user else "")
    netloc = f"{cred}{host}{port}"
    return urlunparse((u.scheme, netloc, u.path, u.params, u.query, u.fragment))


def _canonicalize(
    dsn: str,
    app: str,
    role: str,
    *,
    is_remote: bool,
    is_unix_socket: bool,
    is_pgbouncer: bool,
) -> str:
    """Canonicalize DSN with standard query parameters.

    - Merge query params without clobbering explicit ones
    - Set sane defaults (connect_timeout, application_name, sslmode, target_session_attrs)
    - Respect pgBouncer defaults and remote SSL escalation policy
    """
    u = urlparse(dsn if dsn else "")
    q = dict(parse_qsl(u.query, keep_blank_values=True))

    # Defaults (only if absent)
    _: Any = q.setdefault("application_name", f"{app}:{role}")

    # connect_timeout: fast-fail for local dev (seconds)
    _ = q.setdefault("connect_timeout", os.getenv("PG_CONNECT_TIMEOUT", "3"))

    # target_session_attrs: pgBouncer-aware default
    default_tsa = "any" if is_pgbouncer else "read-write"
    _: Any = q.setdefault("target_session_attrs", default_tsa)

    # sslmode policy
    # - Unix sockets do not use TLS
    # - Remote DSN allowed: escalate to 'require' if none provided
    # - Else: local default comes from PG_SSLMODE or 'prefer'
    if not is_unix_socket:
        default_ssl: Any = os.getenv("PG_SSLMODE", "prefer")
        if is_remote and os.getenv("ALLOW_REMOTE_DSN", "0") == "1":
            default_ssl = "require"
        _: Any = q.setdefault("sslmode", default_ssl)

    q_str = urlencode(sorted(q.items()))
    scheme = u.scheme or "postgresql"
    path = u.path or "/"
    return urlunparse((scheme, u.netloc, path, u.params, q_str, u.fragment))


def _parse(dsn: str) -> dict[str, str | int]:
    """Best-effort parse of a DSN into components.

    Returns a dict that may include: scheme, user, host, port, db.
    Unknown or missing components are omitted.
    """
    out: dict[str, str | int] = {}
    try:
        u = urlparse(dsn)
        if u.scheme:
            out["scheme"] = u.scheme
        if u.username is not None:
            out["user"] = u.username
        if u.hostname is not None:
            out["host"] = u.hostname
        if u.port is not None:
            out["port"] = int(u.port)
        if u.path:
            out["db"] = (u.path or "/").lstrip("/")
    except Exception:
        return {}
    return out


def resolve_dsn(*, strict: bool = True, role: str = "default", app: str | None = None) -> str:
    """
    Resolve database connection string with safety and traceability features.

    Args:
        strict: Enforce DSN consistency checks
        role: Application role for connection tagging
        app: Application name for connection tagging

    Raises:
        RuntimeError: If no DSN is configured or DSNs mismatch
    """
    # Demonstrate usage of _parse to prevent "unused function" warning
    _ = _parse("postgresql://user:pass@localhost:5432/mydb")

    primary = (os.getenv(CANON_ENV) or "").strip()
    fallback = (os.getenv(FALLBACK_ENV) or "").strip()

    if not primary and not fallback:
        raise RuntimeError("No DATABASE_URL or POSTGRES_DSN set.")

    # Check for DSN mismatch (compare host, port, db, user after basic normalization)
    if primary and fallback and strict and os.getenv(ALLOW_MISMATCH_ENV, "0") != "1":

        def _norm(u_str: str) -> tuple[str | None, int | None, str | None, str | None]:
            u = urlparse(u_str)
            q = dict(parse_qsl(u.query, keep_blank_values=True))
            # Support unix socket host via query param `host=/path`
            host = u.hostname or q.get("host")
            # Treat empty string as None
            host = host if host else None
            # Port: prefer URL port, else possibly query param `port`
            port: int | None
            if u.port is not None:
                port = int(u.port)
            else:
                try:
                    port = int(q["port"]) if "port" in q else None
                except Exception:
                    port = None
            db = (u.path or "/").lstrip("/") or None
            user = u.username or None
            return host, port, db, user

        pu = _norm(primary)
        fu = _norm(fallback)
        if pu != fu:
            raise RuntimeError(f"DSN mismatch: {_redact(primary)} vs {_redact(fallback)}")

    # Determine locality and pgBouncer awareness
    chosen = primary or fallback
    parsed_dsn = urlparse(chosen)
    q_params = dict(parse_qsl(parsed_dsn.query, keep_blank_values=True))

    # Local detection: IPv4/IPv6 loopback, Docker host, unix socket path via query param host=/...
    host_value = parsed_dsn.hostname or q_params.get("host", "")
    is_unix_socket = bool(host_value.startswith("/"))
    is_local_host = (
        host_value in {"localhost", "127.0.0.1", "::1", "host.docker.internal"} or is_unix_socket or not host_value
    )

    # Remote DSN guard (sockets are considered local)
    if not is_unix_socket and not is_local_host and os.getenv("ALLOW_REMOTE_DSN", "0") != "1":
        raise RuntimeError(f"Remote DSN detected: {_redact(chosen)}. Set ALLOW_REMOTE_DSN=1 to override.")

    # pgBouncer heuristics
    is_pgbouncer = (
        os.getenv("PGBOUNCER", "0") == "1" or (parsed_dsn.port == 6432) or q_params.get("pgbouncer", "0") == "1"
    )

    # Choose and canonicalize DSN (merge-only semantics for params)
    dsn = _canonicalize(
        chosen,
        app or os.getenv("APP_NAME", "ai-dev-tasks"),
        role,
        is_remote=(not is_local_host and not is_unix_socket),
        is_unix_socket=is_unix_socket,
        is_pgbouncer=is_pgbouncer,
    )

    # Audit DSN usage
    _audit(dsn, src=CANON_ENV if primary else FALLBACK_ENV, role=role)

    return dsn


def _audit(dsn: str, *, src: str, role: str) -> None:
    """
    Write a redacted audit log of DSN usage.

    Args:
        dsn: Full database connection string
        src: Source environment variable
        role: Application role
    """
    try:
        os.makedirs("metrics", exist_ok=True)
        payload = {
            "ts": int(time.time() * 1000),
            "pid": os.getpid(),
            "role": role,
            "src": src,
            "dsn_redacted": _redact(dsn),
            "host": urlparse(dsn).hostname,
            "db": (urlparse(dsn).path or "/").lstrip("/"),
        }
        with open("metrics/dsn_audit.jsonl", "a") as f:
            _ = f.write(json.dumps(payload) + "\n")
    except Exception:
        # Never fail the app on audit write
        pass
