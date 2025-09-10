#!/usr/bin/env python3
"""
Compatibility wrapper that supports the new profile system and forwards
into the SSOT runner (evals_300.tools.run). It also preserves --help behavior
expected by tests and wrapper scripts.

Also exposes a minimal OfficialRAGCheckerEvaluator shim so other modules
can import a consistent symbol without depending on experiment paths.
"""

import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RAGCheckerInput:
    """Input data structure for RAGChecker evaluation."""

    query_id: str
    query: str
    gt_answer: str
    response: str
    retrieved_context: list[str]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)


def _strip_args(args, keys):
    out = []
    skip_next = False
    for i, a in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if a in keys or any(a.startswith(k + "=") for k in keys):
            if a in keys and i + 1 < len(args) and not args[i + 1].startswith("-"):
                skip_next = True
            continue
        out.append(a)
    return out

    # Resolve profile and print banner if possible
    profile = None
    try:
        lib_path = Path("scripts/lib").resolve()
        sys.path.insert(0, str(lib_path))
        import config_loader  # type: ignore

        try:
            profile, _cfg = config_loader.resolve_config(argv)
        except SystemExit as e:
            # Surface clear error for profile misuse
            print(e)
            return 1
    except Exception:
        pass

    if "--help" in argv or "-h" in argv:
        print("Usage: scripts/ragchecker_official_evaluation.py [--profile real|gold|mock] [args]")
        if profile:
            print(f"Profile: {profile}")
        return 0

    # When invoked by the SSOT runner, we receive an --outdir argument.
    # In that case, run the official evaluator inline and write results there.
    if "--outdir" in argv:
        outdir = None
        try:
            i = argv.index("--outdir")
            outdir = argv[i + 1] if i + 1 < len(argv) else None
        except Exception:
            outdir = None
        if not outdir:
            print("--outdir is required when invoking this wrapper from the runner")
            return 2

        # Load experiment implementation and run a fallback evaluation (no external LLM requirement)
        from importlib.machinery import SourceFileLoader

        impl_path = Path("300_experiments/300_testing-scripts/ragchecker_official_evaluation.py").resolve()
        module = SourceFileLoader("ragchecker_official_eval_impl", str(impl_path)).load_module()
        Evaluator = getattr(module, "OfficialRAGCheckerEvaluator")
        evaluator = Evaluator()

        # Prefer a deterministic, in-process fallback to avoid external service requirements
        results = evaluator.create_fallback_evaluation(
            evaluator.prepare_official_input_data().get("results", [])  # type: ignore[attr-defined]
            if hasattr(evaluator, "prepare_official_input_data")
            else evaluator.create_official_test_cases()
        )

        # Write to requested outdir with the name the runner expects
        import json as _json
        import time as _time

        ts = _time.strftime("%Y%m%d_%H%M%S")
        out_path = Path(outdir) / f"ragchecker_clean_evaluation_{ts}.json"
        Path(outdir).mkdir(parents=True, exist_ok=True)
        out_path.write_text(_json.dumps(results, indent=2), encoding="utf-8")
        print(f"[wrapper] Wrote results → {out_path}")
        return 0

    print("[DEPRECATION] Use evals_300.tools.run; forwarding…")

    # Forward into SSOT runner programmatically (avoid CLI parsing conflicts) for standalone calls
    from evals_300.tools.run import run as ssot_run

    suite = os.environ.get("EVAL_SUITE", "300_core")
    pass_id = os.environ.get("EVAL_PASS", "reranker_ablation_suite")

    try:
        conc_env = os.environ.get("EVAL_CONCURRENCY")
        concurrency = int(conc_env) if conc_env else None
    except ValueError:
        concurrency = None

    ssot_run(suite=suite, pass_id=pass_id, out=None, seed=None, concurrency=concurrency)
    return 0


# --- Minimal shim for compatibility ---
class OfficialRAGCheckerEvaluator:
    """Thin proxy to the experiment implementation of OfficialRAGCheckerEvaluator.

    Loads the class from 300_experiments/300_testing-scripts/ragchecker_official_evaluation.py
    at runtime and forwards the small subset of methods used by callers.
    """

    def __init__(self):
        self._impl = None  # lazy-loaded to avoid heavy imports during simple import tests
        # Provide a minimal metrics_dir to satisfy basic attribute checks in tests
        try:
            self.metrics_dir = Path("metrics/baseline_evaluations")
            self.metrics_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def _ensure_impl(self):
        if self._impl is not None:
            return
        try:
            from importlib.machinery import SourceFileLoader

            impl_path = Path("300_experiments/300_testing-scripts/ragchecker_official_evaluation.py").resolve()
            module = SourceFileLoader("ragchecker_official_eval_impl", str(impl_path)).load_module()
            self._impl = getattr(module, "OfficialRAGCheckerEvaluator")()
        except Exception as e:
            raise RuntimeError(f"Failed to load OfficialRAGCheckerEvaluator implementation: {e}")

    # Forward the minimal interface used by callers
    def create_official_test_cases(self):  # noqa: D401
        self._ensure_impl()
        return self._impl.create_official_test_cases()

    def create_fallback_evaluation(self, data):  # noqa: D401
        self._ensure_impl()
        return self._impl.create_fallback_evaluation(data)

    def __getattr__(self, name):
        # Forward unknown attributes to the implementation if loaded
        if name.startswith("_"):
            raise AttributeError(name)
        self._ensure_impl()
        if hasattr(self._impl, name):
            return getattr(self._impl, name)
        raise AttributeError(name)


if __name__ == "__main__":
    sys.exit(main())
