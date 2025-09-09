# 300_evals/tools/run.py
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional

# Optional Typer import with graceful fallback for library use without CLI deps
try:
    import typer  # type: ignore

    _HAS_TYPER = True
except Exception:  # pragma: no cover - only hit if typer isn't installed
    _HAS_TYPER = False

    class _TyperStub:  # minimal shim for direct function imports
        class BadParameter(Exception):
            pass

        def __call__(self, *_, **__):
            pass

        def command(self, *_, **__):
            def _decorator(f):
                return f

            return _decorator

    typer = _TyperStub()  # type: ignore

from src.config.resolve import effective_rerank_config

try:
    from src.settings import load_eval_settings
except Exception:
    load_eval_settings = None  # type: ignore

try:
    # Typed result/summary contracts
    from pydantic import TypeAdapter

    from src.schemas.eval import CaseResult, EvaluationRun, RerankerConfig
except Exception:
    TypeAdapter = None  # type: ignore
    CaseResult = None  # type: ignore
    EvaluationRun = None  # type: ignore
    RerankerConfig = None  # type: ignore

from ..ssot.registry_core import SUITE
from .audit import append_changelog, repo_head

LAYER_DIR = Path("configs/evals_layers")
LATEST_DIR = Path("metrics/latest")
LATEST_DIR.mkdir(parents=True, exist_ok=True)

app = typer.Typer() if _HAS_TYPER else typer  # type: ignore


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


def _latest_summary_for_pass(pass_name: str) -> Optional[Path]:
    """Find the most recent summary.json for a given pass by folder mtime."""
    hist = Path("metrics/history")
    candidates = sorted(
        [p for p in hist.glob(f"{pass_name}_*/summary.json")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _run_ablation_suite_impl(suite: str, seed: int, concurrency: int):
    """Runs reranker_ablation_off and _on and writes a comparison artifact."""
    if suite != SUITE.id:
        raise typer.BadParameter(f"Unknown suite '{suite}'. Expected '{SUITE.id}'.")

    off_id = "reranker_ablation_off"
    on_id = "reranker_ablation_on"

    # Run OFF then ON via implementation (avoid decorator typing noise for type checkers)
    run_impl(suite=suite, pass_id=off_id, out=str(""), seed=seed, concurrency=concurrency)
    run_impl(suite=suite, pass_id=on_id, out=str(""), seed=seed, concurrency=concurrency)

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


def run_impl(
    suite: str,
    pass_id: str,
    out: str = "",
    seed: Optional[int] = None,
    concurrency: Optional[int] = None,
) -> None:
    # Currently we only support the single SSOT suite defined in registry_core
    if suite != SUITE.id:
        raise typer.BadParameter(f"Unknown suite '{suite}'. Expected '{SUITE.id}'.")
    s = SUITE
    # Alias: run both reranker ablation passes and write compare.json
    if pass_id == "reranker_ablation_suite":
        # Delegate to the orchestration function using current defaults
        _run_ablation_suite_impl(suite=suite, seed=seed or 42, concurrency=concurrency or 3)
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
    # Preserve explicit user/profile selections from parent env over layer defaults
    for k in ("EVAL_PROFILE", "EVAL_DRIVER", "RAGCHECKER_USE_REAL_RAG", "POSTGRES_DSN"):
        if k in os.environ:
            env_full[k] = os.environ[k]

    # Log the normalized effective reranker configuration at run start
    try:
        print("[config] reranker:", json.dumps(effective_rerank_config()))
    except Exception:
        pass

    # Standardize artifact output path per pass/run
    run_out = Path(out) if out else Path(f"metrics/history/{p.id}_{int(time.time())}")
    run_out.mkdir(parents=True, exist_ok=True)
    artifact_path = str(run_out / "summary.json")  # we'll try to fill this

    # Optionally load typed settings for visibility
    try:
        if load_eval_settings is not None:
            _settings = load_eval_settings()
            # Avoid printing secrets; just show profile/driver
            print(
                f"[settings] profile={_settings.EVAL_PROFILE} driver={_settings.EVAL_DRIVER} concurrency={_settings.EVAL_CONCURRENCY}"
            )
    except Exception:
        pass

    # Dispatch to the right script (your real paths)
    if p.run.kind == "ragchecker":
        # RagChecker relies primarily on env. Provide explicit outdir for artifacts.
        python_bin = sys.executable or "python3"
        try:
            subprocess.run([python_bin, p.run.script, "--outdir", str(run_out)], check=True, env=env_full)
        except subprocess.CalledProcessError:
            # Continue and record a placeholder so the pipeline stays informative
            _write_latest_metrics(p.id, {"artifact_path": artifact_path})
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

            # Produce typed summary.json when DTOs available; else mirror raw
            if TypeAdapter and CaseResult and EvaluationRun and RerankerConfig:
                try:
                    case_dicts = data.get("case_results") or data.get("cases") or []
                    cases = TypeAdapter(list[CaseResult]).validate_python(case_dicts)  # type: ignore

                    # Build reranker config from environment
                    rr_cfg = RerankerConfig(
                        enable=os.getenv("RERANK_ENABLE", "1") == "1",
                        model=os.getenv("RERANK_MODEL", "bge-reranker-base"),
                        input_topk=int(os.getenv("RERANK_POOL", "60")),
                        keep=int(os.getenv("RERANK_TOPN", "18")),
                        batch=int(os.getenv("RERANK_BATCH", "8")),
                        device=os.getenv("TORCH_DEVICE", "cpu"),
                        cache=bool(os.getenv("RERANK_CACHE_BACKEND", "1")),
                    )

                    from datetime import datetime

                    erun = EvaluationRun(
                        profile=os.getenv("EVAL_PROFILE", "default"),
                        driver=os.getenv("EVAL_DRIVER", "ragchecker"),
                        reranker=rr_cfg,
                        seed=int(os.getenv("SEED", "0")) or None,
                        started_at=datetime.fromtimestamp(found_path.stat().st_mtime).isoformat(),
                        finished_at=datetime.now().isoformat(),
                        overall=overall,
                        artifact_paths={
                            "results_json": str(found_path),
                            "run_dir": str(run_out),
                        },
                    )
                    (run_out / "summary.json").write_text(erun.model_dump_json(indent=2, exclude_none=True))
                except Exception:
                    (run_out / "summary.json").write_text(json.dumps(data, indent=2))
            else:
                # Fallback: mirror raw
                (run_out / "summary.json").write_text(json.dumps(data, indent=2))
            _write_latest_metrics(p.id, payload)

            # Guarded timeseries sink into evaluation_metrics hypertable (Timescale/PG)
            try:
                import uuid
                from datetime import datetime

                import psycopg

                if os.getenv("EVAL_TIMESERIES_SINK", "0") == "1" and os.getenv("POSTGRES_DSN"):
                    run_uuid = uuid.uuid4()
                    with psycopg.connect(os.getenv("POSTGRES_DSN")) as conn:
                        with conn.cursor() as cur:
                            cur.execute(
                                """
                                INSERT INTO evaluation_metrics
                                  (ts, run_id, profile, pass_id, f1, precision, recall, faithfulness, artifact_path, git_sha)
                                VALUES
                                  (now(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (
                                    run_uuid,
                                    os.getenv("EVAL_PROFILE", "default"),
                                    p.id,
                                    payload.get("f1"),
                                    payload.get("precision"),
                                    payload.get("recall"),
                                    payload.get("faithfulness"),
                                    str(found_path),
                                    repo_head().get("sha"),
                                ),
                            )
            except Exception:
                pass
        else:
            # Minimal placeholder
            _write_latest_metrics(p.id, {"artifact_path": artifact_path})
    elif p.run.kind == "calibrate":
        python_bin = sys.executable or "python3"
        subprocess.run([python_bin, p.run.script] + p.run.args, check=True, env=env_full)
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
        python_bin = sys.executable or "python3"
        subprocess.run([python_bin, p.run.script] + p.run.args, check=True, env=env_full)
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


@app.command()
def run(
    suite: str = typer.Option(..., "--suite", "-s", help="Evaluation suite id (e.g., 300_core)"),
    pass_id: str = typer.Option(..., "--pass", "-p", help="Evaluation pass id"),
    out: str = typer.Option("", "--out", help="Optional output directory for artifacts"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Optional random seed to export as SEED/FEW_SHOT_SEED"),
    concurrency: Optional[int] = typer.Option(
        None, "--concurrency", help="Optional max workers to export as MAX_WORKERS"
    ),
) -> None:
    # Delegate to implementation (keeps internal calls type-checkable)
    run_impl(suite=suite, pass_id=pass_id, out=(out or ""), seed=seed, concurrency=concurrency)


if __name__ == "__main__":
    app()


@app.command()
def run_ablation_suite(
    suite: str = typer.Option(..., "--suite", "-s", help="Evaluation suite id (e.g., 300_core)"),
    seed: int = typer.Option(42, "--seed", help="Random seed for both passes"),
    concurrency: int = typer.Option(3, "--concurrency", help="Concurrency for both passes"),
):
    """Runs reranker_ablation_off and _on and writes a comparison artifact."""
    _run_ablation_suite_impl(suite=suite, seed=seed, concurrency=concurrency)


def main():  # legacy-compat import hook
    app()
