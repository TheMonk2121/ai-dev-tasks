# 300_evals/tools/run.py
import json
import os
import subprocess
import time
from pathlib import Path


import typer

from ..ssot.registry_core import SUITE

LAYER_DIR = Path("configs/evals_layers")
LATEST_DIR = Path("metrics/latest")
LATEST_DIR.mkdir(parents=True, exist_ok=True)

app = typer.Typer()


def _load_layer(name: str) -> dict[str, str]:
    env = {}
    f = LAYER_DIR / f"{name}.env"
    if f.exists():
        for line in f.read_text().splitlines():
            s = line.strip()
            if s and not s.startswith("#") and "=" in s:
                k, v = s.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def _materialize_env(layers, overrides) -> dict[str, str]:
    env: dict[str, str] = {}
    for layer in layers:
        env.update(_load_layer(layer))
    env.update({k: str(v) for k, v in overrides.items()})
    # Guardrails: keep stable behavior unless explicit
    if env.get("RATE_LIMIT_PROFILE", "stable") == "stable":
        env.setdefault("MAX_WORKERS", "3")
    return env


def _write_latest_metrics(pass_id: str, payload: dict):
    # Standard JSON the generator expects
    p = LATEST_DIR / "metrics.json"
    existing = json.loads(p.read_text()) if p.exists() else {}
    payload = dict(payload)
    payload.setdefault("timestamp", time.strftime("%Y-%m-%dT%H:%M:%S"))
    existing[pass_id] = payload
    p.write_text(json.dumps(existing, indent=2))


@app.command()
def run(suite: str, pass_: str):
    s = SUITE
    p = next(x for x in s.passes if x.id == pass_)
    env = _materialize_env(p.config_layers, p.config.model_dump())
    env_full = {**os.environ, **env}

    # Standardize artifact output path per pass/run
    run_out = Path(f"metrics/history/{p.id}_{int(time.time())}")
    run_out.mkdir(parents=True, exist_ok=True)
    artifact_path = str(run_out / "summary.json")  # we'll try to fill this

    # Dispatch to the right script (your real paths)
    if p.run.kind == "ragchecker":
        # RagChecker relies primarily on env. Keep CLI clean.
        subprocess.run(["python", p.run.script], check=True, env=env_full)
        # Try to find ragchecker's metrics file; otherwise leave a minimal stub.
        # If your script already writes JSON, point to it here.
        found = None
        for cand in ["metrics/ragchecker_summary.json", "metrics/summary.json", "metrics/latest_run.json"]:
            if Path(cand).exists():
                found = cand
                break
        if found:
            # copy to our run_out
            data = json.loads(Path(found).read_text())
            (run_out / "summary.json").write_text(json.dumps(data, indent=2))
            _write_latest_metrics(p.id, {**data, "artifact_path": artifact_path})
        else:
            # minimal placeholder (you can patch ragchecker to emit a file)
            _write_latest_metrics(p.id, {"artifact_path": artifact_path})
    elif p.run.kind == "calibrate":
        subprocess.run(["python", p.run.script] + p.run.args, check=True, env=env_full)
        _write_latest_metrics(p.id, {"artifact_path": artifact_path})
    elif p.run.kind == "reader_debug":
        subprocess.run(["python", p.run.script] + p.run.args, check=True, env=env_full)
        _write_latest_metrics(p.id, {"artifact_path": artifact_path})

    # Re-render docs with new latest metrics
    subprocess.run(["python", "-m", "300_evals.tools.report"], check=True)


if __name__ == "__main__":
    app()
