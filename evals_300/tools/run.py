# 300_evals/tools/run.py
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Optional

import typer

from ..ssot.registry_core import SUITE
from .audit import append_changelog, repo_head
from src.config.resolve import effective_rerank_config

LAYER_DIR = Path("configs/evals_layers")
LATEST_DIR = Path("metrics/latest")
LATEST_DIR.mkdir(parents=True, exist_ok=True)

app = typer.Typer()


def _load_layer(name: str) -> Dict[str, str]:
    env = {}
    f = LAYER_DIR / f"{name}.env"
    if f.exists():
        for line in f.read_text().splitlines():
            s = line.strip()
            if s and not s.startswith("#") and "=" in s:
                k, v = s.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def _materialize_env(layers, overrides) -> Dict[str, str]:
    env: Dict[str, str] = {}
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
def run(
    suite: str = typer.Option(..., "--suite", "-s", help="Evaluation suite id (e.g., 300_core)"),
    pass_id: str = typer.Option(..., "--pass", "-p", help="Evaluation pass id"),
    out: str = typer.Option(None, "--out", help="Optional output directory for artifacts"),
    seed: int = typer.Option(None, "--seed", help="Optional random seed to export as SEED/FEW_SHOT_SEED"),
    concurrency: int = typer.Option(None, "--concurrency", help="Optional max workers to export as MAX_WORKERS"),
):
    # Currently we only support the single SSOT suite defined in registry_core
    if suite != SUITE.id:
        raise typer.BadParameter(f"Unknown suite '{suite}'. Expected '{SUITE.id}'.")
    s = SUITE
    # Alias: run both reranker ablation passes and write compare.json
    if pass_id == "reranker_ablation_suite":
        # Delegate to the orchestration command using current defaults
        run_ablation_suite(suite=suite, seed=seed or 42, concurrency=concurrency or 3)
        return
    try:
        p = next(x for x in s.passes if x.id == pass_id)
    except StopIteration:
        raise typer.BadParameter(f"Unknown pass '{pass_id}'. Choose one of: {[x.id for x in s.passes]}")
    env = _materialize_env(p.config_layers, p.config.model_dump())
    if seed is not None:
        env["SEED"] = str(seed)
        env.setdefault("FEW_SHOT_SEED", str(seed))
    if concurrency is not None:
        env["MAX_WORKERS"] = str(concurrency)
    env_full = {**os.environ, **env}

    # Log the normalized effective reranker configuration at run start
    try:
        print("[config] reranker:", json.dumps(effective_rerank_config()))
    except Exception:
        pass

    # Standardize artifact output path per pass/run
    run_out = Path(out) if out else Path(f"metrics/history/{p.id}_{int(time.time())}")
    run_out.mkdir(parents=True, exist_ok=True)
    artifact_path = str(run_out / "summary.json")  # we'll try to fill this

    # Dispatch to the right script (your real paths)
    if p.run.kind == "ragchecker":
        # RagChecker relies primarily on env. Provide explicit outdir for artifacts.
        subprocess.run(["python3", p.run.script, "--outdir", str(run_out)], check=True, env=env_full)
        # Find the evaluation result JSON written by the script in our run_out
        jsons = sorted(run_out.glob("ragchecker_clean_evaluation_*.json"))
        if jsons:
            found_path = jsons[-1]
            data = json.loads(found_path.read_text())
            # Normalize metric keys for our manifest/csv
            overall = data.get("overall_metrics", {})
            payload = {
                "precision": overall.get("precision"),
                "recall": overall.get("recall"),
                "f1": overall.get("f1_score"),
                "faithfulness": overall.get("faithfulness"),
                "artifact_path": str(found_path),
            }
            # Also mirror a generic summary.json for convenience
            (run_out / "summary.json").write_text(json.dumps(data, indent=2))
            _write_latest_metrics(p.id, payload)
        else:
            # Minimal placeholder
            _write_latest_metrics(p.id, {"artifact_path": artifact_path})
    elif p.run.kind == "calibrate":
        subprocess.run(["python3", p.run.script] + p.run.args, check=True, env=env_full)
        # Normalize output location to metrics/calibration/thresholds.json if present
        src = Path("evals/answerability_calibration_results.json")
        calib_dir = Path("metrics/calibration")
        calib_dir.mkdir(parents=True, exist_ok=True)
        dst = calib_dir / "thresholds.json"
        if src.exists():
            dst.write_text(src.read_text())
            _write_latest_metrics(p.id, {"artifact_path": str(dst)})
        else:
            _write_latest_metrics(p.id, {"artifact_path": artifact_path})
    elif p.run.kind == "reader_debug":
        subprocess.run(["python", p.run.script] + p.run.args, check=True, env=env_full)
        _write_latest_metrics(p.id, {"artifact_path": artifact_path})

    # Changelog entry (append-only)
    head = repo_head()
    latest = json.loads((LATEST_DIR / "metrics.json").read_text()).get(p.id, {})
    append_changelog(
        {
            "type": "run",
            "suite": s.id,
            "pass": p.id,
            "git": head,
            "env": env,
            "results": {
                k: latest.get(k) for k in ["f1", "precision", "recall", "faithfulness", "timestamp", "artifact_path"]
            },
        }
    )

    # Re-render docs with new latest metrics
    subprocess.run(["python3", "-m", "evals_300.tools.report"], check=True)


if __name__ == "__main__":
    app()


def _latest_summary_for_pass(pass_name: str) -> Optional[Path]:
    """Find the most recent summary.json for a given pass by folder mtime."""
    hist = Path("metrics/history")
    candidates = sorted(
        [p for p in hist.glob(f"{pass_name}_*/summary.json")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


@app.command()
def run_ablation_suite(
    suite: str = typer.Option(..., "--suite", "-s", help="Evaluation suite id (e.g., 300_core)"),
    seed: int = typer.Option(42, "--seed", help="Random seed for both passes"),
    concurrency: int = typer.Option(3, "--concurrency", help="Concurrency for both passes"),
):
    """Runs reranker_ablation_off and _on and writes a comparison artifact."""
    if suite != SUITE.id:
        raise typer.BadParameter(f"Unknown suite '{suite}'. Expected '{SUITE.id}'.")

    off_id = "reranker_ablation_off"
    on_id = "reranker_ablation_on"

    # Run OFF then ON
    run(suite=suite, pass_id=off_id, seed=seed, concurrency=concurrency)
    run(suite=suite, pass_id=on_id, seed=seed, concurrency=concurrency)

    off_p = _latest_summary_for_pass(off_id)
    on_p = _latest_summary_for_pass(on_id)

    def _metrics(p: Optional[Path]) -> dict:
        if not p or not p.exists():
            return {}
        data = json.loads(p.read_text())
        overall = data.get("overall_metrics", {})
        return {
            "micro_precision": overall.get("precision"),
            "micro_recall": overall.get("recall"),
            "micro_f1": overall.get("f1_score"),
            # Macro placeholders; if available in future summaries, will be included
            "macro_f1": overall.get("f1_score"),
        }

    off_m = _metrics(off_p)
    on_m = _metrics(on_p)
    compare = {
        "off": off_m,
        "on": on_m,
        "delta": {
            "micro_f1": (on_m.get("micro_f1") or 0) - (off_m.get("micro_f1") or 0),
            "micro_precision": (on_m.get("micro_precision") or 0) - (off_m.get("micro_precision") or 0),
            "micro_recall": (on_m.get("micro_recall") or 0) - (off_m.get("micro_recall") or 0),
            "macro_f1": (on_m.get("macro_f1") or 0) - (off_m.get("macro_f1") or 0),
        },
    }

    out_dir = Path("metrics/reranker_ablation")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "compare.json").write_text(json.dumps(compare, indent=2))
    print(f"wrote ablation compare → {out_dir / 'compare.json'}")


def main():  # legacy-compat import hook
    app()
