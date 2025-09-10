#!/usr/bin/env python3
"""
Clean RAGChecker Evaluation Harness with Real DSPy RAG Integration

This is a clean implementation that:
1. Uses real DSPy RAG system instead of synthetic data
2. Implements RRF fusion + cross-encoder reranking
3. Provides oracle metrics and retrieval snapshots
4. Includes progress logging and proper breadcrumbs
"""

import argparse
import importlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Setup observability if available
try:
    from scripts.observability import (
        get_logfire,
        log_eval_metrics,
        log_reader_span,
        log_retrieval_span,
        log_scoring_span,
    )

    logfire = get_logfire()
except Exception:
    logfire = None
from typing import Any

# Bootstrap sys.path relative to this file so imports work regardless of CWD
try:
    _ROOT = Path(__file__).resolve().parents[1]  # repository root
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))
    # DSPy modules moved to main src directory
    _DSPY_SRC = _ROOT / "src"
    if _DSPY_SRC.exists() and str(_DSPY_SRC) not in sys.path:
        sys.path.insert(0, str(_DSPY_SRC))
except Exception:
    pass

# Import profile configuration loader
from scripts.lib.config_loader import resolve_config

try:
    from src.settings import load_eval_settings
except Exception:
    load_eval_settings = None  # type: ignore

try:
    # Pydantic DTOs for stable artifacts
    from src.schemas.eval import EvaluationRun, RerankerConfig
except Exception:
    EvaluationRun = None  # type: ignore
    RerankerConfig = None  # type: ignore

# Apply safe PyTorch import patch first (before any PyTorch imports)
try:
    import safe_pytorch_import

    print("✅ Applied safe PyTorch import patch for Python 3.12 compatibility")
except ImportError:
    pass

try:
    from litellm_compatibility_shim import patch_litellm_imports

    patch_litellm_imports()
except ImportError:
    pass

# Add DSPy RAG system to path (env override still respected)
dspy_rag_path = os.getenv("DSPY_RAG_PATH", "src")
if dspy_rag_path and dspy_rag_path not in sys.path:
    sys.path.insert(0, dspy_rag_path)

# Optional: import reranker env shim globally so it's available where needed
try:
    from src.rag import reranker_env as RENV  # type: ignore
except Exception:  # noqa: F401 - keep a sentinel for type checkers
    RENV = None  # type: ignore

# Reader + snippetizer
try:
    from dspy_modules.reader.program import ExtractiveReader
    from dspy_modules.reader.snippetizer import select_snippets

    READER_AVAILABLE = True
except Exception as e:
    # Catch broad exceptions to avoid sandbox issues (e.g., diskcache sqlite errors)
    print(f"⚠️ ExtractiveReader not available: {e}")
    READER_AVAILABLE = False

OPS_TAGS = {"meta_ops", "ops_health"}


def _assemble_passages(retrieval_rows, q, tag):
    """Assemble passages using snippetizer for crisp sentences."""
    passages = []
    for r in retrieval_rows:
        chunk = r.get("content", "")
        # 6 high-signal sentences per chunk, biasing paths/functions
        if READER_AVAILABLE:
            passages.extend(select_snippets(chunk, q, k=6))
        else:
            # Fallback to simple chunk splitting
            passages.append(chunk)
        if len(passages) >= 30:  # keep context tight
            break
    return passages


def load_cases_any(path: str):
    """Load cases from either JSON or JSONL format using Pydantic Evals framework."""
    import warnings

    # Issue deprecation warning
    warnings.warn(
        "load_cases_any is deprecated. Use scripts.migrate_to_pydantic_evals.load_eval_cases instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    # Use the new Pydantic Evals framework
    from scripts.migrate_to_pydantic_evals import load_eval_cases

    # Convert to legacy format for compatibility
    cases = load_eval_cases(path)
    return [case.model_dump() for case in cases]


class DspyRagDriver:
    """Driver for real DSPy RAG system integration."""

    def __init__(self):
        rag_path = os.getenv("DSPY_RAG_PATH", "src")
        if rag_path and rag_path not in sys.path:
            sys.path.insert(0, rag_path)

        # Apply litellm compatibility shim
        try:
            from litellm_compatibility_shim import patch_litellm_imports

            patch_litellm_imports()
        except ImportError:
            pass

        # Import with proper path handling
        try:
            import dspy

            rp = importlib.import_module("dspy_modules.rag_pipeline")
            from dspy_modules.vector_store import HybridVectorStore

            # Configure DSPy with language model and a stable completion adapter
            model_name = os.getenv("DSPY_MODEL", "anthropic.claude-3-haiku-20240307-v1:0")
            try:
                from dspy.adapters import CompletionAdapter  # type: ignore

                dspy.configure(lm=dspy.LM(model_name), adapter=CompletionAdapter())
            except Exception:
                # Fallback: configure without explicit adapter (keeps previous behavior)
                dspy.configure(lm=dspy.LM(model_name))

            # Initialize with proper retriever and database connection
            # Respect POSTGRES_DSN if provided; fall back to a local default for dev
            db_connection = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
            retriever = HybridVectorStore(db_connection)
            self.module = rp.RAGModule(retriever=retriever)
        except Exception as e:
            print(f"Failed to import DSPy RAG module: {e}")
            raise

    def answer(self, question: str) -> dict:
        """Get answer from real DSPy RAG system."""
        t0 = time.time()
        out = self.module(question)  # Returns dict[str, Any]
        ans_text = out.get("answer", "") if isinstance(out, dict) else str(out)
        citations = out.get("citations", []) if isinstance(out, dict) else []
        snapshot = getattr(self.module, "_last_retrieval_snapshot", []) or []
        used_ctx = getattr(self.module, "used_contexts", []) or []

        # Tripwire: log counts to catch truncation
        print(f"[DSPy] used_ctx={len(used_ctx)} snapshot={len(snapshot)}")
        if used_ctx:
            print(f"[DSPy] First 3 text lengths: {[len(u.get('text', '')) for u in used_ctx[:3]]}")

        # Assert variant consistency for evaluations
        self._assert_variant(used_ctx)

        max_cands = int(os.getenv("SAVE_CANDIDATES_MAX", "60"))
        return {
            "answer": ans_text,
            "citations": citations,
            "retrieval_candidates": snapshot[:max_cands],
            "retrieved_context": used_ctx,
            "latency_sec": round(time.time() - t0, 3),
        }

    def _assert_variant(self, used_ctx):
        """Assert that retrieved contexts have proper variant identification."""
        # Allow disabling during evaluations via env flag
        import os

        if os.getenv("EVAL_DISABLE_VARIANT_ASSERT", "0") == "1":
            return
        if not used_ctx:
            return

        # Check for missing variant identification
        bad = [
            c
            for c in used_ctx
            if not (c.get("meta", {}).get("ingest_run_id") or c.get("ingest_run_id") or c.get("fp", {}).get("run"))
        ]
        if bad:
            raise RuntimeError("Retrieved contexts lack ingest_run_id/chunk_variant; likely old data source.")

        # Optional: enforce expected run
        want = os.getenv("INGEST_RUN_ID")
        if want:
            for c in used_ctx[:12]:
                run_id = c.get("ingest_run_id") or c.get("meta", {}).get("ingest_run_id") or c.get("fp", {}).get("run")
                if run_id != want:
                    raise RuntimeError(f"Mismatch: contexts not from run {want}, got {run_id}")


def _make_eval_driver():
    """Create evaluation driver based on environment configuration."""
    use_real = (
        os.getenv("EVAL_DRIVER", "").lower() in ("dspy_rag", "dspy", "rag")
        or os.getenv("RAGCHECKER_USE_REAL_RAG") == "1"
    )
    if use_real:
        try:
            # Try to initialize the real DSPy RAG driver
            return DspyRagDriver(), "dspy_rag"
        except Exception as e:
            print(f"⚠️ Failed to init DspyRagDriver: {e}")
            print("⚠️ Falling back to synthetic evaluation with proper infrastructure")
            return None, "synthetic_infrastructure"
    return None, "synthetic"


class CleanRAGCheckerEvaluator:
    """Clean RAGChecker evaluator with real DSPy RAG integration."""

    def __init__(self):
        self.metrics_dir = Path("metrics/baseline_evaluations")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self._eval_path_tag = "unknown"
        self._progress_fh = None
        self._progress_path = None

    def _progress_open(self, path: str):
        """Open progress logging file."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._progress_path = path
        self._progress_fh = open(path, "a", encoding="utf-8", buffering=1)

    def _progress_write(self, rec: dict):
        """Write progress record to JSONL."""
        if not getattr(self, "_progress_fh", None):
            p = os.getenv("RAGCHECKER_PROGRESS_LOG")
            if p:
                self._progress_open(p)
            else:
                return
        self._progress_fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def _tok(self, s: str) -> list[str]:
        """Tokenize text for Jaccard similarity."""
        import re

        return re.findall(r"[a-z0-9]+", (s or "").lower())

    def _jac(self, a: list[str], b: list[str]) -> float:
        """Calculate Jaccard similarity."""
        A, B = set(a), set(b)
        return (len(A & B) / len(A | B)) if (A or B) else 0.0

    def _split_sents_light(self, text: str) -> list[str]:
        """Light sentence splitting."""
        import re

        if not text:
            return []
        s = text.split("Sources:", 1)[0].strip()
        sents = re.split(r"(?<=[\.\?\!])\s+(?=[A-Z0-9])", s)
        if len(sents) <= 1:
            sents = re.split(r"\s*[;—–•·]\s*", s)
        if len(sents) <= 1:
            sents = re.split(r"\s{2,}", s)
        return [x.strip() for x in sents if x.strip()]

    def _extract_ctx_strings(self, rc):
        """Extract context strings from retrieved context with dual-text support."""
        out = []
        if isinstance(rc, list):
            for d in rc:
                if isinstance(d, dict):
                    # Handle dual-text storage: prefer bm25_text for retrieval
                    s = d.get("text") or d.get("bm25_text") or d.get("embedding_text") or ""
                    if s:
                        out.append(s)
                else:
                    out.append(str(d))
        return out

    def _compute_oracle_from_payload(self, case: dict) -> dict:
        """Compute oracle metrics from case payload."""
        j_ctx_min = float(os.getenv("ORACLE_CTX_J_MIN", "0.28"))
        j_sent_min = float(os.getenv("ORACLE_SENT_J_MIN", "0.32"))
        gt = self._tok(case.get("gt_answer", ""))
        ctx_strings = self._extract_ctx_strings(case.get("retrieved_context", []))
        ans_sents = self._split_sents_light(case.get("response", ""))
        ctx_j = [self._jac(self._tok(c), gt) for c in ctx_strings]
        sent_j = [self._jac(self._tok(s), gt) for s in ans_sents]
        retrieval_hit = any(
            (j >= j_ctx_min) or (((case.get("gt_answer") or "").lower()) in (c or "").lower())
            for j, c in zip(ctx_j, ctx_strings)
        )
        gold_sent_idxs = [i for i, j in enumerate(sent_j) if j >= j_sent_min]
        return {
            "oracle_retrieval_hit": bool(retrieval_hit),
            "oracle_reader_used_gold": bool(gold_sent_idxs),
            "oracle_reader_gold_sent_indices": gold_sent_idxs[:8],
            "oracle_ctx_count": len(ctx_strings),
            "oracle_answer_sent_count": len(ans_sents),
            "oracle_ctx_j_max": (max(ctx_j) if ctx_j else 0.0),
            "oracle_sent_j_max": (max(sent_j) if sent_j else 0.0),
        }

    def _compute_faithfulness(self, answer: str, retrieved_context: list) -> float:
        """Estimate faithfulness via max Jaccard between answer sentences and context.

        Relies on this class's lightweight tokenization and sentence splitting to avoid
        extra dependencies. Returns a value in [0,1].
        """
        ans_sents = self._split_sents_light(answer)
        ctx_strings = self._extract_ctx_strings(retrieved_context)
        if not ans_sents or not ctx_strings:
            return 0.0
        best = 0.0
        for s in ans_sents:
            ts = self._tok(s)
            for c in ctx_strings:
                tc = self._tok(c)
                if not ts or not tc:
                    continue
                j = self._jac(ts, tc)
                if j > best:
                    best = j
        return best

    def _normalize_case_result_for_save(self, case: dict) -> dict:
        """Ensure oracle fields exist at top-level and inside metrics.oracle."""
        case = dict(case)  # shallow copy

        # compute if missing
        needs_oracle = not any(k.startswith("oracle_") for k in case.keys())
        if needs_oracle:
            oracle = self._compute_oracle_from_payload(case)
            case.update(oracle)
        else:
            # already present (from earlier path)
            oracle = {k: case[k] for k in list(case.keys()) if k.startswith("oracle_")}

        # Mirror into metrics.oracle to survive schema sanitizers
        metrics = dict(case.get("metrics", {}))
        metrics_oracle = dict(metrics.get("oracle", {}))
        metrics_oracle.update(oracle)
        metrics["oracle"] = metrics_oracle

        # Mirror file-oracle if present
        file_oracle_keys = (
            "file_oracle_prefilter_hit",
            "file_oracle_postfilter_hit",
            "file_oracle_reader_used",
        )
        if any(k in case for k in file_oracle_keys):
            metrics_file_oracle = dict(metrics.get("file_oracle", {}))
            for k in file_oracle_keys:
                if k in case:
                    metrics_file_oracle[k] = case[k]
            metrics["file_oracle"] = metrics_file_oracle
        case["metrics"] = metrics

        return case

    def _normalize_path(self, p: str) -> str:
        import re

        if not p:
            return ""
        p = p.strip().split("#", 1)[0]  # drop fragment
        p = p.replace("\\", "/")  # windows → posix
        p = re.sub(r"/{2,}", "/", p)  # squeeze slashes
        return p

    def _filename_of(self, d: dict) -> str:
        """Extract normalized filename/path from snapshot/context entries with robust fallbacks."""
        try:
            if not isinstance(d, dict):
                return ""
            m = d
            fn = (
                m.get("filename")
                or (m.get("meta") or {}).get("filename")
                or m.get("src")  # treat src as filename fallback
                or (m.get("meta") or {}).get("src")
                or m.get("source_document")
                or m.get("document_path")
                or ""
            )
            return self._normalize_path(fn)
        except Exception:
            return ""

    def _match_expected(self, fn: str, expected_files: list[str]) -> bool:
        """Match filename against expected files using exact path OR basename (case-insensitive)."""
        import os

        if not fn or not expected_files:
            return False
        fn_norm = self._normalize_path(fn).lower()
        fn_base = os.path.basename(fn_norm)
        exp_norm = {self._normalize_path(x).lower() for x in expected_files}
        exp_bases = {os.path.basename(x) for x in exp_norm}
        return (fn_norm in exp_norm) or (fn_base in exp_bases) or any(fn_norm.endswith("/" + b) for b in exp_bases)

    def _compute_file_oracle(self, case: dict) -> dict:
        """Compute file-oracle signals using expected_files list in the gold case."""
        exp = case.get("expected_files") or []
        snap = case.get("retrieval_snapshot") or []
        used = case.get("retrieved_context") or []
        cits = case.get("citations") or []

        pref = any(self._match_expected(self._filename_of(x), exp) for x in snap)
        post = any(self._match_expected(self._filename_of(x), exp) for x in used)
        read = any(self._match_expected(x, exp) for x in cits)

        return {
            "file_oracle_prefilter_hit": bool(pref),
            "file_oracle_postfilter_hit": bool(post),
            "file_oracle_reader_used": bool(read),
        }

    def _parse_citations_from_answer(self, answer: str) -> list[str]:
        import re

        if not answer:
            return []
        m = re.search(r"CITATIONS:\s*(.+)$", answer, flags=re.IGNORECASE | re.DOTALL)
        if not m:
            return []
        lines = [ln.strip("-•* \t") for ln in m.group(1).splitlines() if ln.strip()]
        cites: list[str] = []
        for ln in lines:
            tok = ln.split()[0] if " " in ln else ln
            cites.append(self._normalize_path(tok))
        return cites

    def _save_results(self, results: dict, out_path: str):
        """Save results with oracle normalization and breadcrumbs."""
        # normalize all cases regardless of origin path
        cr = results.get("case_results") or results.get("cases") or []
        results["case_results"] = [self._normalize_case_result_for_save(c) for c in cr]

        # include path/schema breadcrumbs
        results.setdefault("schema_version", 2)
        results.setdefault("eval_path", getattr(self, "_eval_path_tag", "unknown"))

        # Add tech manifest
        results["tech_manifest"] = {
            "eval_driver": getattr(self, "_eval_path_tag", "unknown"),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dspy_rag_path": os.getenv("DSPY_RAG_PATH", "src"),
            "fusion_enabled": os.getenv("RERANK_ENABLE", "1") == "1",
            "retrieval_topk_vec": int(os.getenv("RETR_TOPK_VEC", "140")),
            "retrieval_topk_bm25": int(os.getenv("RETR_TOPK_BM25", "140")),
        }

        # Include resolved reranker config
        try:
            if RENV is not None:
                results["reranker_config"] = {
                    "enable": int(getattr(RENV, "RERANK_ENABLE", False)),
                    "model": getattr(RENV, "RERANKER_MODEL", None),
                    "input_topk": getattr(RENV, "RERANK_INPUT_TOPK", None),
                    "keep": getattr(RENV, "RERANK_KEEP", None),
                    "batch": getattr(RENV, "RERANK_BATCH", None),
                    "device": getattr(RENV, "TORCH_DEVICE", None),
                    "cache": getattr(RENV, "RERANK_CACHE_BACKEND", None),
                }
        except Exception:
            pass

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    def _calculate_precision(self, response: str, gt_answer: str, query: str) -> float:
        """Calculate precision with word overlap."""
        query_words = set((query or "").lower().split())
        gt_words = set((gt_answer or "").lower().split())
        response_words = set((response or "").lower().split())

        if len(gt_words) > 0:
            base_precision = (
                len(response_words.intersection(gt_words)) / len(response_words) if len(response_words) > 0 else 0
            )
            # Query relevance boost
            query_relevance = (
                len(response_words.intersection(query_words)) / len(query_words) if len(query_words) > 0 else 0
            )
            query_boost = 0.1 * query_relevance
            return min(1.0, base_precision + query_boost)
        return 0.0

    def _calculate_recall(self, response: str, gt_answer: str) -> float:
        """Calculate recall with word overlap."""
        gt_words = set((gt_answer or "").lower().split())
        response_words = set((response or "").lower().split())

        if len(gt_words) > 0:
            return len(response_words.intersection(gt_words)) / len(gt_words)
        return 0.0

    def run_evaluation(
        self, cases_file: str, outdir: str, use_bedrock: bool = False, reader=None, args=None
    ) -> dict[str, Any]:
        """Run evaluation with real DSPy RAG system."""
        start_wall = datetime.now()
        print("📊 EVALUATION SUMMARY (CLEAN HARNESS)")
        print("=" * 60)

        # Set evaluation path tag
        driver, tag = _make_eval_driver()

        # Hard gate: Stop synthetic fallback if real RAG is requested
        use_real = (
            (load_eval_settings().EVAL_DRIVER.lower() in ("dspy_rag", "dspy", "rag") if load_eval_settings else False)
            or os.getenv("EVAL_DRIVER", "").lower() in ("dspy_rag", "dspy", "rag")
            or os.getenv("RAGCHECKER_USE_REAL_RAG") == "1"
        )
        if use_real and tag != "dspy_rag":
            raise RuntimeError("Evaluation requested real DSPy RAG, but driver is synthetic. Aborting.")

        self._eval_path_tag = tag
        if driver:
            print(f"🔗 Using real DSPy RAG system (driver: {tag})")
        else:
            print(f"⚠️ Using synthetic evaluation (driver: {tag})")

        # Open progress logging if enabled
        progress_log = os.getenv("RAGCHECKER_PROGRESS_LOG")
        if progress_log:
            self._progress_open(progress_log)

        # Load test cases using new gold loader or legacy method
        if cases_file:
            # Legacy mode - use old loader
            cases = load_cases_any(cases_file)
        else:
            # New mode - use gold loader
            from src.utils.gold_loader import filter_cases, load_gold_cases, stratified_sample

            gold_file = os.getenv("GOLD_FILE", getattr(args, "gold_file", "evals/gold/v1/gold_cases.jsonl"))
            gold_profile = os.getenv("GOLD_PROFILE", getattr(args, "gold_profile", None))
            gold_tags = os.getenv("GOLD_TAGS", getattr(args, "gold_tags", None))
            gold_mode = os.getenv("GOLD_MODE", getattr(args, "gold_mode", None))
            gold_size = int(os.getenv("GOLD_SIZE", str(getattr(args, "gold_size", 0) or 0)) or 0) or None
            seed = int(os.getenv("SEED", str(getattr(args, "seed", 1337))))

            cases = load_gold_cases(gold_file)

            if gold_profile:
                # Profile-guided sampling using manifest next to gold file
                import json

                manifest_path = Path(gold_file).parent / "manifest.json"
                view = json.loads(manifest_path.read_text())["views"][gold_profile]
                cases = stratified_sample(
                    cases, strata=view["strata"], size=view["size"], seed=view["seed"], mode=view.get("mode")
                )
            else:
                # Direct filtering
                tags = gold_tags.split(",") if isinstance(gold_tags, str) and gold_tags else None
                cases = filter_cases(cases, include_tags=tags, mode=gold_mode, size=gold_size, seed=seed)

            # Convert GoldCase objects to dict format for compatibility
            cases = [
                {
                    "query": case.query,
                    "gt_answer": case.gt_answer,
                    "expected_files": case.expected_files,
                    "globs": case.globs,
                    "expected_decisions": case.expected_decisions,
                    "tags": case.tags,
                    "id": case.id,
                    "mode": case.mode,
                }
                for case in cases
            ]

        print(f"📋 Loaded {len(cases)} test cases")

        case_results = []
        total_precision = total_recall = total_f1 = 0.0

        for i, case in enumerate(cases, 1):
            print(f"🔍 Processing case {i}/{len(cases)}: {case.get('query', '')[:50]}...")

            query = case.get("query", "")
            gt_answer = case.get("gt_answer", "")

            # Generate response using driver
            if driver:
                resp = driver.answer(query)
                retrieval_candidates = resp["retrieval_candidates"]
                retrieved_context = resp["retrieved_context"]
                latency = resp["latency_sec"]

                # Log retrieval span
                if logfire:
                    log_retrieval_span(logfire, query, len(retrieval_candidates), latency * 1000)

                # Use extractive reader if available
                if reader and READER_AVAILABLE:
                    tag = case.get("tag", "general")
                    passages = _assemble_passages(retrieved_context, query, tag)
                    # Tag-aware override example (ops-focused abstain is slightly stricter)
                    if tag in OPS_TAGS and hasattr(reader, "answerable_threshold"):
                        reader.answerable_threshold = max(reader.answerable_threshold, 0.12)
                    try:
                        out = reader(question=query, passages=passages, tag=tag)
                        response = out.get("answer", "NOT_ANSWERABLE")

                        # Log reader span
                        if logfire:
                            log_reader_span(logfire, query, len(response), True)
                    except Exception as e:
                        print(f"⚠️ Reader invocation failed ({e}); falling back to generator answer")
                        response = resp["answer"]

                        # Log reader failure
                        if logfire:
                            log_reader_span(logfire, query, len(response), False)
                else:
                    response = resp["answer"]
            else:
                # Enhanced synthetic response that simulates real RAG structure
                response = f"Based on the available documentation, {query.lower()}. This response is generated using the DSPy RAG system with fusion adapter and cross-encoder reranking."

                # Simulate retrieval candidates (fusion adapter output)
                retrieval_candidates = [
                    {
                        "id": f"doc_{i}",
                        "src": "bm25" if i % 2 == 0 else "vec",
                        "score": 0.9 - i * 0.1,
                        "score_ce": 0.85 - i * 0.05,
                        "text": f"Relevant document {i} content about {query[:20]}...",
                    }
                    for i in range(25)  # Simulate 25 candidates from fusion
                ]

                # Simulate retrieved context (what gets passed to reader)
                retrieved_context = [
                    {
                        "doc_id": f"doc_{i}",
                        "text": f"Context document {i} about {query[:20]}...",
                        "score": 0.8 - i * 0.05,
                        "source": "fusion",
                        "meta": {},
                    }
                    for i in range(12)  # Simulate 12 documents passed to reader
                ]
                latency = 0.5

            # Calculate metrics
            precision = self._calculate_precision(response, gt_answer, query)
            recall = self._calculate_recall(response, gt_answer)
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            faithfulness = self._compute_faithfulness(response, retrieved_context)

            # Create case result
            case_result = {
                "query_id": case.get("query_id", f"case_{i}"),
                "query": query,
                "response": response,
                "gt_answer": gt_answer,
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "retrieved_context": retrieved_context,
                "retrieval_candidates": retrieval_candidates,
                "retrieval_snapshot": retrieval_candidates,  # For oracle metrics
                "expected_files": case.get("expected_files", []),  # Copy expected_files from input case
                "timing_sec": latency,
                "metrics": {
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1_score,
                    "faithfulness": faithfulness,
                },
            }

            # Attach citations if available from driver output
            if driver and isinstance(resp, dict):
                if resp.get("citations"):
                    case_result["citations"] = list(resp.get("citations") or [])
            if not case_result.get("citations"):
                case_result["citations"] = self._parse_citations_from_answer(case_result.get("response", ""))

            # Compute and attach file-oracle signals when expected_files present
            try:
                # expected_files live on the input gold case row
                ef = case.get("expected_files")
                if ef:
                    file_oracle = self._compute_file_oracle(
                        {
                            **case_result,
                            "expected_files": ef,
                        }
                    )
                    case_result.update(file_oracle)
                    # Also mirror under metrics.file_oracle now; _normalize will ensure persistence
                    fr = dict(case_result.get("metrics", {}))
                    fr["file_oracle"] = {k: case_result[k] for k in file_oracle.keys()}
                    case_result["metrics"] = fr
            except Exception:
                pass

            case_results.append(case_result)
            total_precision += precision
            total_recall += recall
            total_f1 += f1_score

            # Log scoring span
            if logfire:
                case_id = case.get("id", f"case_{i}")
                log_scoring_span(logfire, case_id, precision, recall, f1_score)
            try:
                _ = total_faithfulness
            except NameError:
                total_faithfulness = 0.0
            total_faithfulness += faithfulness

            # Progress logging
            try:
                self._progress_write({"type": "case", "query": query, "timing_sec": latency})
            except Exception:
                pass

        # Calculate overall metrics
        n = max(1, len(case_results))
        results = {
            "evaluation_type": "clean_harness_real_rag",
            "overall_metrics": {
                "precision": total_precision / n,
                "recall": total_recall / n,
                "f1_score": total_f1 / n,
                "faithfulness": (total_faithfulness / n) if n else 0.0,
            },
            "case_results": case_results,
            "total_cases": len(case_results),
        }

        # Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        out_file = Path(outdir) / f"ragchecker_clean_evaluation_{timestamp}.json"
        self._save_results(results, str(out_file))

        print(f"✅ Evaluation complete. Results saved to: {out_file}")
        print(f"📊 Overall metrics: P={total_precision/n:.3f}, R={total_recall/n:.3f}, F1={total_f1/n:.3f}")

        # Log overall metrics
        if logfire:
            log_eval_metrics(
                logfire,
                {
                    "precision": total_precision / n,
                    "recall": total_recall / n,
                    "f1_score": total_f1 / n,
                    "faithfulness": total_faithfulness / n,
                    "total_cases": n,
                },
            )

        # Emit summary artifact using Pydantic model (stable contract) if available
        try:
            if EvaluationRun is not None and RerankerConfig is not None:
                # Build reranker config from env/optional RENV, falling back to defaults
                rr_cfg = {
                    "enable": (
                        int(getattr(RENV, "RERANK_ENABLE", int(os.getenv("RERANK_ENABLE", "1")))) == 1
                        if RENV is not None
                        else (os.getenv("RERANK_ENABLE", "1") == "1")
                    ),
                    "model": (
                        getattr(RENV, "RERANKER_MODEL", os.getenv("RERANK_MODEL", "bge-reranker-base"))
                        if RENV is not None
                        else os.getenv("RERANK_MODEL", "bge-reranker-base")
                    ),
                    "input_topk": (
                        getattr(RENV, "RERANK_INPUT_TOPK", int(os.getenv("RERANK_POOL", "60")))
                        if RENV is not None
                        else int(os.getenv("RERANK_POOL", "60"))
                    ),
                    "keep": (
                        getattr(RENV, "RERANK_KEEP", int(os.getenv("RERANK_TOPN", "18")))
                        if RENV is not None
                        else int(os.getenv("RERANK_TOPN", "18"))
                    ),
                    "batch": (
                        getattr(RENV, "RERANK_BATCH", int(os.getenv("RERANK_BATCH", "8")))
                        if RENV is not None
                        else int(os.getenv("RERANK_BATCH", "8"))
                    ),
                    "device": os.getenv("TORCH_DEVICE", "cpu"),
                    "cache": bool(os.getenv("RERANK_CACHE_BACKEND", "1")),
                }
                erun = EvaluationRun(
                    profile=os.getenv("EVAL_PROFILE", "default"),
                    pass_id=os.getenv("EVAL_PASS_ID", "default"),
                    driver=tag,
                    reranker=RerankerConfig(**rr_cfg),
                    seed=int(os.getenv("SEED", str(getattr(args, "seed", 0) or 0))) or None,
                    started_at=start_wall,
                    finished_at=datetime.now(),
                    overall=results.get("overall_metrics", {}),
                    artifact_paths={
                        "results_json": str(out_file),
                    },
                )
                (Path(outdir) / "evaluation_run.json").write_text(erun.model_dump_json(indent=2, exclude_none=True))
        except Exception as e:
            # Do not fail the run if summary emission fails
            print(f"⚠️ Failed to emit EvaluationRun summary: {e}")

        return results


def _build_reader(args):
    """Build reader based on CLI arguments."""
    if args.reader == "extractive":
        if not READER_AVAILABLE:
            print("⚠️ Falling back: ExtractiveReader unavailable; proceeding without reader module.")
            return None
        return ExtractiveReader(answerable_threshold=args.answerable_threshold)
    # (Keep old reader as fallback)
    try:
        from dspy_modules.reader.legacy_program import LegacyGenerativeReader

        return LegacyGenerativeReader()
    except ImportError:
        # Fallback to basic reader if legacy not available
        print("⚠️ Using basic fallback reader")
        return None


def main():
    """Main entry point."""
    # Resolve profile + env and refuse foot-guns up front
    profile, resolved = resolve_config()

    # Optional: branch guard (block mock on main)
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
        if branch == "main" and profile == "mock":
            raise SystemExit("❌ Refusing to run mock profile on main branch.")
    except Exception:
        pass

    # Concurrency default from env; your executor can read this
    try:
        _typed = load_eval_settings() if load_eval_settings else None
        default_cc = str(getattr(_typed, "EVAL_CONCURRENCY", "") or resolved.get("EVAL_CONCURRENCY", "3"))
    except Exception:
        default_cc = resolved.get("EVAL_CONCURRENCY", "3")
    os.environ.setdefault("EVAL_CONCURRENCY", default_cc)
    concurrency = int(os.environ["EVAL_CONCURRENCY"])
    print(f"▶ Using concurrency={concurrency}")

    parser = argparse.ArgumentParser(description="Clean RAGChecker Evaluation Harness")
    parser.add_argument("--cases", help="Path to JSONL test cases file (legacy)")
    parser.add_argument("--gold-file", default="evals/gold/v1/gold_cases.jsonl", help="Path to gold cases file")
    parser.add_argument("--gold-profile", default=None, help="Evaluation profile (ops_smoke, repo_gold, decision_only)")
    parser.add_argument("--gold-tags", default=None, help="Comma-separated tags to include")
    parser.add_argument("--gold-mode", default=None, help="Mode filter (retrieval, reader, decision)")
    parser.add_argument("--gold-size", type=int, default=None, help="Number of cases to sample")
    parser.add_argument("--seed", type=int, default=1337, help="Random seed for sampling")
    parser.add_argument("--concurrency", type=int, default=3, help="Number of concurrent workers")
    parser.add_argument("--outdir", required=True, help="Output directory for results")
    parser.add_argument("--use-bedrock", action="store_true", help="Use Bedrock (placeholder)")
    parser.add_argument("--stable", action="store_true", help="Use stable config (placeholder)")
    parser.add_argument("--bypass-cli", action="store_true", help="Bypass CLI (placeholder)")
    parser.add_argument(
        "--reader", choices=["extractive", "generative"], default="extractive", help="Reader mode. Default: extractive."
    )
    parser.add_argument(
        "--answerable-threshold", type=float, default=0.12, help="Reader abstain threshold (tag overrides may apply)."
    )

    args = parser.parse_args()

    # Build reader based on CLI arguments
    reader = _build_reader(args)

    evaluator = CleanRAGCheckerEvaluator()
    results = evaluator.run_evaluation(args.cases, args.outdir, args.use_bedrock, reader=reader, args=args)

    # After computing final scores, create profile-aware output directory
    from datetime import datetime

    # Extract metrics from results
    overall_metrics = results.get("overall_metrics", {})
    f1_micro = overall_metrics.get("f1", 0.0)
    precision_micro = overall_metrics.get("precision", 0.0)
    recall_micro = overall_metrics.get("recall", 0.0)

    # Create profile-aware run tag
    run_tag = (
        f"{datetime.now():%Y%m%d_%H%M%S}"
        f"__{profile}"
        f"__driver-{os.environ.get('EVAL_DRIVER', '?')}"
        f"__f1-{f1_micro:.3f}__p-{precision_micro:.3f}__r-{recall_micro:.3f}"
    )

    # Create new output directory with profile information
    profile_outdir = Path("metrics") / "runs" / run_tag
    profile_outdir.mkdir(parents=True, exist_ok=True)

    # Write provenance information
    provenance = {
        "profile": profile,
        "scores": {"micro": {"f1": f1_micro, "precision": precision_micro, "recall": recall_micro}},
        "env": {
            "EVAL_DRIVER": os.environ.get("EVAL_DRIVER"),
            "RAGCHECKER_USE_REAL_RAG": os.environ.get("RAGCHECKER_USE_REAL_RAG"),
            "POSTGRES_DSN": os.environ.get("POSTGRES_DSN", "<unset>")[:32] + "…",  # redact
            "EVAL_CONCURRENCY": os.environ.get("EVAL_CONCURRENCY"),
        },
        "timestamp": datetime.now().isoformat(),
        "original_outdir": args.outdir,
    }

    (profile_outdir / "summary.json").write_text(json.dumps(provenance, indent=2))

    # Copy original results to profile directory
    original_results_file = Path(args.outdir) / "ragchecker_clean_evaluation_results.json"
    if original_results_file.exists():
        import shutil

        shutil.copy2(original_results_file, profile_outdir / "evaluation_results.json")

    print(f"📦 Profile artifacts → {profile_outdir}")
    print(f"📦 Original artifacts → {args.outdir}")

    return results


if __name__ == "__main__":
    result = main()
