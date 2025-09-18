from __future__ import annotations

import argparse
import json
import os
import sys
import sys as _sys
from pathlib import Path
from typing import Any, Optional, Union

import boto3
import httpx

# FIXME: Update this import path after reorganization
# from scripts.utils.http_client import create_client, get_with_backoff  # type: ignore[import-untyped]

#!/usr/bin/env python3

# Ensure project root is on sys.path for utility imports
_sys.path.append(str(Path(__file__).resolve().parents[1]))


def _print_result(ok: bool, details: dict[str, Any]) -> None:
    result = {
        "ok": ok,
        "details": details,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


def smoke_ollama(model: str | None, mode: str) -> int:
    base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    try:
        with create_client(timeout_seconds=5.0) as client:
            resp = get_with_backoff(client, f"{base_url}/api/tags")
            data: Any = resp.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            ok = bool(models)
            details = {"provider": "ollama", "endpoint": f"{base_url}/api/tags", "models": models[:10]}
            # Optional quick model presence check
            if model:
                details["model_requested"] = model
                details["model_available"] = model in models
                ok = ok and (model in models)
            _print_result(ok, details)
            return 0 if ok else 2
    except Exception as exc:  # noqa: BLE001
        _print_result(False, {"provider": "ollama", "error": str(exc)})
        return 2


def smoke_bedrock(model: str | None, mode: str) -> int:
    # Meta mode: verify required env and model id provided
    if mode == "meta":
        ok = bool(os.getenv("AWS_REGION")) and bool(model)
        _print_result(
            ok,
            {
                "provider": "bedrock",
                "mode": "meta",
                "AWS_REGION_present": bool(os.getenv("AWS_REGION")),
                "model_id_present": bool(model),
            },
        )
        return 0 if ok else 2

    # Live mode: attempt a minimal invoke if boto3 is available
    try:

        region: Any = os.getenv("AWS_REGION")
        if not region or not model:
            _print_result(False, {"provider": "bedrock", "error": "Missing AWS_REGION or model id"})
            return 2
        client: Any = boto3.client("bedrock-runtime", region_name=region)
        # Minimal Anthropic-style request body; model-specific schema may vary
        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": [{"type": "text", "text": "ping"}]}],
            }
        )
        resp: Any = client.invoke_model(modelId=model, body=body)
        ok = resp.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200
        _print_result(ok, {"provider": "bedrock", "mode": "live", "status": resp.get("ResponseMetadata", {})})
        return 0 if ok else 2
    except ModuleNotFoundError:
        _print_result(False, {"provider": "bedrock", "error": "boto3 not installed; use --mode meta or install boto3"})
        return 2
    except Exception as exc:  # noqa: BLE001
        _print_result(False, {"provider": "bedrock", "mode": "live", "error": str(exc)})
        return 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Provider smoke test (meta/live)")
    parser.add_argument("--provider", required=True, choices=["ollama", "bedrock"], help="Provider to check")
    parser.add_argument("--model", required=False, help="Model id/name to verify")
    parser.add_argument("--mode", default="meta", choices=["meta", "live"], help="Check mode")
    args: Any = parser.parse_args()

    if args.provider == "ollama":
        return smoke_ollama(args.model, args.mode)
    if args.provider == "bedrock":
        return smoke_bedrock(args.model, args.mode)
    print(json.dumps({"ok": False, "error": "unsupported provider"}))
    return 2


if __name__ == "__main__":
    sys.exit(main())
