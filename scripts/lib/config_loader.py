#!/usr/bin/env python3
"""
Evaluation Profile Configuration Loader

Provides deterministic config resolution with preflight checks to prevent
"accidentally-synthetic" baselines. Single source of truth for evaluation
profiles: real, gold, mock.
"""

from __future__ import annotations

import argparse
import os
import sys
import textwrap
from pathlib import Path


try:
    from src.settings import EvalSettings
except Exception:
    EvalSettings = None  # type: ignore

VALID_PROFILES = {"real", "gold", "mock"}


def _parse_env_file(p: Path) -> dict[str, str]:
    """Parse environment file into key-value dictionary."""
    if not p.exists():
        sys.exit(f"❌ Missing profile file: {p}")
    out: dict[str, str] = {}
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip()
    return out


def load_profile_env(profile: str) -> dict[str, str]:
    """Load environment variables from profile file."""
    base = Path(__file__).resolve().parent.parent
    env_path = base / "configs" / "profiles" / f"{profile}.env"
    return _parse_env_file(env_path)


def apply_env(d: dict[str, str]) -> None:
    """Apply environment variables to current process."""
    for k, v in d.items():
        os.environ[k] = v


def resolve_config(argv=None):
    """
    Resolve evaluation configuration with deterministic precedence:
    1. CLI flags (highest precedence)
    2. Profile file configs
    3. Process env (for CI secrets only)
    4. Hardcoded safe defaults

    Returns (profile, resolved_config_dict)
    """
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--profile", choices=sorted(VALID_PROFILES))
    p.add_argument("--driver", choices=["dspy_rag", "synthetic"])
    p.add_argument("--use-real-rag", type=int, choices=[0, 1])
    p.add_argument("--postgres-dsn")
    p.add_argument("--concurrency", type=int)
    args, _ = p.parse_known_args(argv)

    profile = args.profile or os.environ.get("EVAL_PROFILE")
    if not profile:
        msg = textwrap.dedent(
            """
        ❌ No profile selected.
           Use one of:
             --profile real   (baseline/tuning on real RAG)
             --profile gold   (real RAG + gold cases)
             --profile mock   (infra tests only)
        """
        ).strip()
        sys.exit(msg)
    if profile not in VALID_PROFILES:
        sys.exit(f"❌ Invalid --profile {profile}; choose from {sorted(VALID_PROFILES)}")

    # 1) Profile file → base
    base = load_profile_env(profile)
    # Always export the resolved profile name so downstream runners can honor it
    base["EVAL_PROFILE"] = profile

    # 2) CLI overrides (only the blessed few)
    if args.driver:
        base["EVAL_DRIVER"] = args.driver
    if args.use_real_rag is not None:
        base["RAGCHECKER_USE_REAL_RAG"] = str(args.use_real_rag)
    if args.postgres_dsn:
        base["POSTGRES_DSN"] = args.postgres_dsn
    if args.concurrency is not None:
        base["EVAL_CONCURRENCY"] = str(args.concurrency)

    # 3) Allow CI secrets to flow through without changing core logic
    keep_existing = {"POSTGRES_DSN", "OPENAI_API_KEY", "BEDROCK_REGION", "BEDROCK_ACCESS_KEY", "BEDROCK_SECRET_KEY"}
    for k in keep_existing:
        if k in os.environ and k not in base:
            base[k] = os.environ[k]

    # 4) Derived invariants (hard rules)
    if profile == "mock":
        base["EVAL_DRIVER"] = "synthetic"
        base["RAGCHECKER_USE_REAL_RAG"] = "0"
        base.setdefault("POSTGRES_DSN", "mock://test")
        base.setdefault("EVAL_CONCURRENCY", "3")  # low-concurrency default
    else:
        base["EVAL_DRIVER"] = "dspy_rag"
        base["RAGCHECKER_USE_REAL_RAG"] = "1"
        base.setdefault("EVAL_CONCURRENCY", "8")  # safe default; bump in nightly

    # 5) Preflight gates (refuse foot-guns)
    if profile in {"real", "gold"}:
        if base.get("EVAL_DRIVER") != "dspy_rag":
            sys.exit("❌ Real/gold require EVAL_DRIVER=dspy_rag (synthetic refused).")
        dsn = base.get("POSTGRES_DSN", "")
        if dsn.startswith("mock://"):
            sys.exit("❌ Real/gold require a real POSTGRES_DSN (not mock://).")

    apply_env(base)

    # Produce typed settings instance for downstream callers (optional)
    try:
        if EvalSettings is not None:
            _ = EvalSettings()  # instantiate to validate env
    except Exception as e:
        print(f"⚠️ EvalSettings validation failed: {e}")

    # 6) Friendly banner
    banner = f"""
    ▶ Profile: {profile}
       EVAL_DRIVER={base.get("EVAL_DRIVER")}
       RAGCHECKER_USE_REAL_RAG={base.get("RAGCHECKER_USE_REAL_RAG")}
       POSTGRES_DSN={base.get("POSTGRES_DSN", "<unset>")}
       EVAL_CONCURRENCY={base.get("EVAL_CONCURRENCY", "<unset>")}
    """.rstrip()
    print(banner)
    return profile, base


if __name__ == "__main__":
    # Test the loader
    try:
        profile, config = resolve_config()
        print(f"✅ Profile '{profile}' resolved successfully")
    except SystemExit as e:
        print(f"❌ Configuration failed: {e}")
        sys.exit(1)
