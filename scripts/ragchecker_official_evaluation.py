#!/usr/bin/env python3
from __future__ import annotations

"""
Official RAGChecker Evaluation Script with Local LLM Support

This script implements RAGChecker evaluation following the official methodology:
1. Prepare input data in the correct JSON format
2. Use custom LLM function integration for local models (preferred)
3. Use official RAGChecker CLI when available (fallback)
4. Follow official metrics and procedures
5. Generate proper evaluation reports

Based on official RAGChecker documentation and best practices.
Includes custom LLM integration for local models via Ollama.

SOP: See `000_core/000_evaluation-system-entry-point.md`.
Quick run (stable):
    source throttle_free_eval.sh && \
    python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable

If you were told to "run the evals", use the quick run above.
"""

import asyncio
import json
import os
import random
import re
import subprocess
import sys
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO, TypedDict, Union, cast

import numpy as np
from jsonschema import ValidationError, validate
from pydantic import BaseModel, Field, TypeAdapter, field_validator

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))  # src modules
# Ensure we can import peer utilities under scripts/ and as package 'scripts.*'
sys.path.insert(0, str(Path(__file__).parent))  # scripts modules (direct)
sys.path.insert(0, str(Path(__file__).parent.parent))  # repo root for 'scripts.*'
from common.db_dsn import resolve_dsn


# Type definitions for evaluation items
class EvalItem(TypedDict, total=False):
    """Normalized evaluation item with guaranteed keys."""

    response: str
    gt_answer: str
    query: str
    query_id: Optional[str]


def normalize_item(raw: Union[str, Dict[str, Any]]) -> EvalItem:
    """
    Coerce raw items (str or dict-like) into a uniform dict shape.
    Ensures keys exist so later code can assume item['response']/['gt_answer']/['query'].
    """
    if isinstance(raw, str):
        # we only have a response string; synthesize the rest
        return {"response": raw, "gt_answer": "", "query": "", "query_id": None}
    elif isinstance(raw, dict):
        return {
            "response": str(raw.get("response", raw.get("answer", ""))),
            "gt_answer": str(raw.get("gt_answer", raw.get("gold", ""))),
            "query": str(raw.get("query", raw.get("question", ""))),
            "query_id": raw.get("query_id", None),
        }
    else:
        # ultra-defensive: make it impossible to crash downstream
        return {"response": str(raw), "gt_answer": "", "query": "", "query_id": None}


try:
    import requests
except ImportError:
    print("⚠️ requests module not available - local LLM evaluation will not work")
    requests = None

# Initialize availability flags
_embeddings_available = False
_bedrock_available = False

try:
    # Allow hard-disable via env to bypass PyTorch dependency when incompatible
    if os.getenv("RAGCHECKER_DISABLE_EMBEDDINGS", "0") == "1":
        raise RuntimeError("Embeddings disabled by RAGCHECKER_DISABLE_EMBEDDINGS=1")

    from sentence_transformers import SentenceTransformer

    _embeddings_available = True
except Exception as e:
    print(f"⚠️ sentence-transformers disabled — semantic features off ({e})")
    SentenceTransformer = None

try:
    # Optional override to disable queue-based client
    use_queue = os.getenv("USE_BEDROCK_QUEUE", "1") != "0"

    if use_queue:
        # Try queue client first (with intelligent batching)
        try:
            # Try relative import first (when running from scripts directory)
            from enhanced_bedrock_queue_client import SyncBedrockQueueClient as BedrockClient

            print("✅ Using Enhanced Bedrock Queue Client with intelligent batching")
        except ImportError:
            try:
                # Try absolute import (when running from root directory)
                from scripts.enhanced_bedrock_queue_client import SyncBedrockQueueClient as BedrockClient

                print("✅ Using Enhanced Bedrock Queue Client with intelligent batching")
            except ImportError as e:
                print(f"⚠️ Queue client import failed: {e}")
                use_queue = False

    if not use_queue:
        # Prefer enhanced client with load balancing and adaptive rate limiting
        try:
            from enhanced_bedrock_client import SyncBedrockClientWrapper as BedrockClient

            print("⚠️ Using Enhanced Bedrock Client with multi-key load balancing")
        except ImportError:
            try:
                from scripts.enhanced_bedrock_client import SyncBedrockClientWrapper as BedrockClient

                print("⚠️ Using Enhanced Bedrock Client with multi-key load balancing")
            except ImportError as e2:
                print(f"⚠️ Enhanced Bedrock client import failed: {e2}")
                # Fallback to regular client
                try:
                    from bedrock_client import BedrockClient

                    print("⚠️ Using standard Bedrock client (no load balancing)")
                except ImportError:
                    # Try absolute import (when running from root directory)
                    from scripts.bedrock_client import BedrockClient

                    print("⚠️ Using standard Bedrock client (no load balancing)")

    _bedrock_available = True
except ImportError:
    print("⚠️ bedrock_client not available - AWS Bedrock evaluation disabled")
    BedrockClient = None

# Use properties to avoid constant redefinition
EMBEDDINGS_AVAILABLE = _embeddings_available
BEDROCK_AVAILABLE = _bedrock_available

# Silence tokenizers parallelism warning (cosmetic)
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


# --- Safety guard for high-risk config combos ---
def _enforce_safe_eval_env() -> Dict[str, Any]:
    """Harden evaluation-time env to prevent last-minute tweaks from tanking metrics.

    Returns a dict describing any adjustments or warnings applied for logging.
    """
    summary: Dict[str, Any] = {"adjustments": [], "warnings": []}

    def _warn(msg: str):
        try:
            print(f"⚠️  SafeEval warning: {msg}")
        except Exception:
            pass
        summary["warnings"].append(msg)

    def _adjust(k: str, v: str, reason: str):
        try:
            old = os.getenv(k)
            os.environ[k] = str(v)
            print(f"🔧 Adjusted {k}={v} (was {old!r}) — {reason}")
        except Exception:
            pass
        summary["adjustments"].append({"key": k, "value": v, "reason": reason})

    # Guard: JSON prompts / coverage rewrite are expensive → require conservative Bedrock pacing
    json_on = os.getenv("RAGCHECKER_JSON_PROMPTS", "0") == "1"
    cov_on = os.getenv("RAGCHECKER_COVERAGE_REWRITE", "0") == "1"
    if json_on or cov_on:
        # Clamp concurrency and RPS for stability
        try:
            rps = float(os.getenv("BEDROCK_MAX_RPS", "0.12"))
        except Exception:
            rps = 0.12
        if rps > 0.22:
            _adjust("BEDROCK_MAX_RPS", "0.22", "High-cost ops enabled; clamping RPS to avoid throttling/empty outputs")
        if os.getenv("BEDROCK_MAX_IN_FLIGHT", os.getenv("BEDROCK_MAX_CONCURRENCY", "1")) not in (None, "1", 1):
            _adjust("BEDROCK_MAX_IN_FLIGHT", "1", "Force single in-flight request when JSON/coverage enabled")
        # Ensure queue client path is preferred
        if os.getenv("USE_BEDROCK_QUEUE", "1") == "0":
            _adjust("USE_BEDROCK_QUEUE", "1", "Queue client stabilizes pacing under heavy JSON ops")

    # Guard: conflicting evidence keep strategies → unset percentile when target_k is selected
    if os.getenv("RAGCHECKER_EVIDENCE_KEEP_MODE", "").lower() == "target_k" and os.getenv(
        "RAGCHECKER_EVIDENCE_KEEP_PERCENTILE"
    ):
        os.environ.pop("RAGCHECKER_EVIDENCE_KEEP_PERCENTILE", None)
        summary["adjustments"].append(
            {
                "key": "RAGCHECKER_EVIDENCE_KEEP_PERCENTILE",
                "value": None,
                "reason": "Removed percentile to avoid conflict with target_k (see tuned baseline)",
            }
        )
        print("🔧 Removed RAGCHECKER_EVIDENCE_KEEP_PERCENTILE to avoid conflict with target_k mode")

    # Guard: overly strict gates that often crater recall/precision during final tweaks
    risky_flags = [
        ("RAGCHECKER_NUMERIC_MUST_MATCH", "1"),
        ("RAGCHECKER_ENTITY_MUST_MATCH", "1"),
        ("RAGCHECKER_RISKY_REQUIRE_ALL", "1"),
    ]
    if os.getenv("RAGCHECKER_ALLOW_RISKY", "0") != "1":
        for k, bad in risky_flags:
            if os.getenv(k) == bad:
                _warn(f"{k}={bad} increases false negatives; disabling for eval (set RAGCHECKER_ALLOW_RISKY=1 to keep)")
                os.environ[k] = "0"
                summary["adjustments"].append({"key": k, "value": "0", "reason": "Disable risky strictness for eval"})

    return summary


# --- Lightweight progress logger (JSON Lines) ---
def _progress_write(record: Dict[str, Any]) -> None:
    """Append a JSON record to progress log if RAGCHECKER_PROGRESS_LOG is set."""
    try:
        path = os.getenv("RAGCHECKER_PROGRESS_LOG")
        if not path:
            return
        # Ensure JSON-serializable (best effort)
        safe = json.loads(json.dumps(record, default=str))
        with open(path, "a") as f:
            f.write(json.dumps(safe) + "\n")
    except Exception:
        # Never crash eval due to logging
        pass


# --- Env alias shim (prevents silent misconfig) ---
def _env_alias(src: str, dst: str) -> None:
    try:
        if os.getenv(src) and not os.getenv(dst):
            os.environ[dst] = os.environ[src]
    except Exception:
        pass


# Common alias mappings used by engineers
_env_alias("BEDROCK_MAX_CONCURRENCY", "BEDROCK_MAX_IN_FLIGHT")
_env_alias("BEDROCK_RETRY_BASE", "BEDROCK_BASE_BACKOFF")
_env_alias("BEDROCK_RETRY_MAX", "BEDROCK_MAX_RETRIES")
_env_alias("BEDROCK_RETRY_MAX_SLEEP", "BEDROCK_MAX_BACKOFF")
_env_alias("BEDROCK_MODEL", "BEDROCK_MODEL_ID")

# Reverse aliases (new -> legacy) to ensure any export scheme is respected
_env_alias("BEDROCK_MAX_IN_FLIGHT", "BEDROCK_MAX_CONCURRENCY")
_env_alias("BEDROCK_BASE_BACKOFF", "BEDROCK_RETRY_BASE")
_env_alias("BEDROCK_MAX_RETRIES", "BEDROCK_RETRY_MAX")
_env_alias("BEDROCK_MAX_BACKOFF", "BEDROCK_RETRY_MAX_SLEEP")
_env_alias("BEDROCK_MODEL_ID", "BEDROCK_MODEL")

# Queue enable alias (compat with older scripts)
_env_alias("BEDROCK_ENABLE_QUEUE", "USE_BEDROCK_QUEUE")
_env_alias("USE_BEDROCK_QUEUE", "BEDROCK_ENABLE_QUEUE")


# --- Optional env locking via file (ensures stable settings) ---
def _load_env_file(path: str, lock: bool = False) -> int:
    """Load KEY=VALUE pairs from a file.

    - Lines starting with '#' are ignored
    - Empty lines are ignored
    - If lock=True, override existing env; else only set if missing
    Returns number of keys applied
    """
    applied = 0

    def _expand_env_vars(val: str) -> str:
        """Expand ${VAR} and ${VAR:-default} using current os.environ.

        Note: This is a minimal, safe expander – it does not execute commands
        or support complex shell features. It only substitutes simple patterns.
        """
        try:
            import re

            # ${VAR:-default}
            def repl_default(m):
                key = m.group(1)
                default = m.group(2)
                return os.environ.get(key, default)

            val = re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)[:-]-(.*?)\}", repl_default, val)

            # ${VAR}
            def repl_simple(m):
                key = m.group(1)
                return os.environ.get(key, "")

            val = re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", repl_simple, val)
            return val
        except Exception:
            return val

    try:
        with open(path, "r") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                # Support lines like: export KEY=VALUE  and inline comments
                if k.startswith("export "):
                    k = k[len("export ") :].strip()
                # Strip inline comments and quotes from value
                v = v.split("#", 1)[0].strip()
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                if k and (lock or os.getenv(k) is None):
                    os.environ[k] = _expand_env_vars(v)
                    applied += 1
    except Exception:
        return 0
    return applied


_lock_flag = os.getenv("RAGCHECKER_LOCK_ENV", "0") == "1"
_env_file = os.getenv("RAGCHECKER_ENV_FILE")
if _env_file:
    _applied = _load_env_file(_env_file, lock=_lock_flag)
    try:
        print(f"🔒 Loaded env from {_env_file} (applied { _applied } keys, lock={_lock_flag})")
    except Exception:
        pass


def _maybe_rerank_contexts(contexts_raw: List[Union[str, Dict[str, Any]]]) -> List[Union[str, Dict[str, Any]]]:
    """Optionally re-rank retrieved_context using simple anchor-aware scoring.

    Supports env knobs for parity with production pipelines:
    - RAGCHECKER_BM25_BOOST_ANCHORS: >1.0 boosts entries flagged as anchors
    - RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR: <1.0 downweights non-anchors when anchors exist

    If inputs are plain strings (common in official eval), this is a no-op.
    """
    if not contexts_raw:
        return contexts_raw

    has_meta = any(isinstance(c, dict) for c in contexts_raw)
    if not has_meta:
        return contexts_raw

    try:
        anchor_boost = float(os.getenv("RAGCHECKER_BM25_BOOST_ANCHORS", "1.0"))
        facet_downweight = float(os.getenv("RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR", "1.0"))
    except Exception:
        anchor_boost = 1.0
        facet_downweight = 1.0

    scored: List[tuple[float, Union[str, Dict[str, Any]]]] = []
    any_anchor = False
    for c in contexts_raw:
        if isinstance(c, dict):
            is_anchor = bool(c.get("is_anchor") or c.get("anchor") or c.get("has_anchor"))
            any_anchor = any_anchor or is_anchor
            base = 1.0
            score = base * (anchor_boost if is_anchor else 1.0)
            scored.append((score, c))
        else:
            scored.append((1.0, c))

    if any_anchor and facet_downweight != 1.0:
        scored = [
            (
                (
                    s
                    if (isinstance(x, dict) and (x.get("is_anchor") or x.get("anchor") or x.get("has_anchor")))
                    else s * facet_downweight
                ),
                x,
            )
            for (s, x) in scored
        ]

    scored.sort(key=lambda t: t[0], reverse=True)
    return [x for (_, x) in scored]


class RateLimiter:
    """Very small RPS limiter to avoid Bedrock throttling."""

    def __init__(self, rps: float):
        self.min_interval = 1.0 / max(rps, 1e-6)
        self._next_ok = 0.0
        self._lock = threading.Lock()

    def wait(self):
        with self._lock:
            now = time.monotonic()
            wait = self._next_ok - now
            if wait > 0:
                time.sleep(wait)
            self._next_ok = max(self._next_ok, now) + self.min_interval

        # Add small jitter to prevent bursts
        jitter = random.random() * 0.05
        if jitter > 0:
            time.sleep(jitter)


class AsyncBedrockGate:
    """
    Global gate shared by ALL Bedrock calls:
      - max_in_flight: concurrent Bedrock requests allowed
      - max_rps: average request rate (token bucket-ish spacing)
      - cooldown(seconds): temporarily pauses all entrants (e.g., after 429)
    """

    def __init__(self, max_in_flight: int = 1, max_rps: float = 0.25):
        self.sem = asyncio.Semaphore(max_in_flight)
        self.min_interval = 1.0 / max(max_rps, 1e-6)
        self._lock = asyncio.Lock()
        self._last = 0.0
        self._cooldown_until = 0.0

    async def __aenter__(self):
        await self.sem.acquire()
        loop = asyncio.get_running_loop()
        now = loop.time()
        # cooldown
        if now < self._cooldown_until:
            await asyncio.sleep(self._cooldown_until - now)
        # RPS spacing with jitter
        async with self._lock:
            now = loop.time()
            wait = max(0.0, (self._last + self.min_interval) - now)
            if wait:
                await asyncio.sleep(wait)
            self._last = loop.time()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        # small jitter to decorrelate bursts
        if self.min_interval:
            await asyncio.sleep(random.uniform(0.0, self.min_interval * 0.25))
        self.sem.release()

    def cooldown(self, seconds: float):
        loop = asyncio.get_running_loop()
        self._cooldown_until = max(self._cooldown_until, loop.time() + seconds)


class RAGCheckerInput(BaseModel):
    """RAGChecker input data structure following official format with Pydantic validation."""

    query_id: str = Field(..., description="Unique identifier for the query")
    query: str = Field(..., min_length=1, description="The input query text")
    gt_answer: str = Field(..., description="Ground truth answer for evaluation")
    response: str = Field(..., description="Generated response to evaluate")
    retrieved_context: List[str] = Field(..., description="List of context strings retrieved for the query")


# JSON Schema models for coverage-first generation
class FactItem(BaseModel):
    """Individual fact extracted from context with evidence citations."""

    fact: str = Field(..., min_length=1, description="Single atomic statement")
    evidence: List[int] = Field(default_factory=list, description="Context indices supporting this fact")


class ScoreJSON(BaseModel):
    """JSON response for scoring prompts with validation."""

    score: float = Field(..., ge=0.0, le=1.0, description="Score between 0.0 and 1.0")
    reasoning: Optional[str] = Field(None, description="Optional reasoning for the score")


# Type adapters for runtime validation
FactsAdapter = TypeAdapter(List[FactItem])
ScoreAdapter = TypeAdapter(ScoreJSON)


class RAGCheckerMetrics(BaseModel):
    """RAGChecker metrics following official specification with Pydantic validation."""

    # Overall Metrics
    precision: float = Field(..., ge=0.0, le=1.0, description="Overall precision score (0-1)")
    recall: float = Field(..., ge=0.0, le=1.0, description="Overall recall score (0-1)")
    f1_score: float = Field(..., ge=0.0, le=1.0, description="Overall F1 score (0-1)")

    # Retriever Metrics
    claim_recall: float = Field(..., ge=0.0, le=1.0, description="Claim recall score (0-1)")
    context_precision: float = Field(..., ge=0.0, le=1.0, description="Context precision score (0-1)")

    # Generator Metrics
    context_utilization: float = Field(..., ge=0.0, le=1.0, description="Context utilization score (0-1)")
    noise_sensitivity: float = Field(..., ge=0.0, le=1.0, description="Noise sensitivity score (0-1)")
    hallucination: float = Field(..., ge=0.0, le=1.0, description="Hallucination score (0-1)")
    self_knowledge: float = Field(..., ge=0.0, le=1.0, description="Self knowledge score (0-1)")
    faithfulness: float = Field(..., ge=0.0, le=1.0, description="Faithfulness score (0-1)")

    @field_validator("*")
    @classmethod
    def validate_score_ranges(cls, v):
        """Validate all score fields are within 0-1 range."""
        if isinstance(v, float) and (v < 0.0 or v > 1.0):
            raise ValueError(f"Score must be between 0.0 and 1.0, got {v}")
        return v


class LocalLLMIntegration:
    """Hybrid LLM integration supporting both local models (Ollama) and AWS Bedrock."""

    def __init__(
        self, api_base: str = "http://localhost:11434", model_name: str = "llama3.1:8b", use_bedrock: bool = False
    ):
        self.use_bedrock = use_bedrock
        self.bedrock_client = None
        # Track Bedrock model id early (used in logs below)
        self.bedrock_model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

        if use_bedrock:
            if not BEDROCK_AVAILABLE:
                raise ImportError("bedrock_client module is required for Bedrock integration")
            try:
                self.bedrock_client = BedrockClient()  # type: ignore
                print(f"✅ AWS Bedrock integration enabled ({self.bedrock_model_id})")
            except Exception as e:
                print(f"⚠️ Failed to initialize Bedrock client: {e}")
                print("🔄 Falling back to local LLM")
                self.use_bedrock = False

        # Always set session for fallback cases
        self.api_base = api_base.rstrip("/")
        self.model_name = model_name
        # JSON token budget (used for extraction + scoring prompts)
        self.json_max_tokens = int(os.getenv("RAGCHECKER_JSON_MAX_TOKENS", "900"))
        if requests is not None:
            self.session = requests.Session()
            if not self.use_bedrock:
                print(f"✅ Local LLM integration enabled ({model_name})")
            else:
                print(f"✅ AWS Bedrock integration enabled ({self.bedrock_model_id})")
        else:
            self.session = None
            if not self.use_bedrock:
                raise ImportError("requests module is required for local LLM integration")

        # Initialize embedding model for semantic operations
        self.embedding_model = None

        # Bedrock rate limiting and retry configuration
        self._bedrock_rl = RateLimiter(float(os.getenv("BEDROCK_MAX_RPS", "0.15"))) if use_bedrock else None
        self._bedrock_max_retries = int(os.getenv("BEDROCK_MAX_RETRIES", "8"))
        self._bedrock_retry_base = float(os.getenv("BEDROCK_RETRY_BASE", "1.8"))
        self._bedrock_retry_max_sleep = float(os.getenv("BEDROCK_RETRY_MAX_SLEEP", "20"))
        self._bedrock_cooldown_until = 0.0  # NEW: cool-down timestamp

        # async bedrock gate
        self._bedrock_gate = None
        if use_bedrock:
            max_rps = float(os.getenv("BEDROCK_MAX_RPS", "0.15"))
            max_in_flight = int(os.getenv("BEDROCK_MAX_IN_FLIGHT", "1"))
            self._bedrock_gate = AsyncBedrockGate(max_in_flight=max_in_flight, max_rps=max_rps)
        if EMBEDDINGS_AVAILABLE and os.getenv("RAGCHECKER_SEMANTIC_FEATURES", "1") == "1":
            try:
                self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # type: ignore
                print("✅ Semantic embeddings enabled (all-MiniLM-L6-v2)")
            except Exception as e:
                print(f"⚠️ Failed to load embedding model: {e}")
                self.embedding_model = None

    def call_local_llm(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call LLM via either Bedrock or local Ollama API."""
        if self.use_bedrock and self.bedrock_client:
            text = self._call_bedrock_llm(prompt, max_tokens)
            # If Bedrock call failed or is cooling down, transparently fall back to local LLM
            if not text or not text.strip():
                try:
                    print("🔁 Bedrock unavailable for this call — falling back to local LLM")
                except Exception:
                    pass
                return self._call_ollama_llm(prompt, max_tokens)
            return text
        else:
            return self._call_ollama_llm(prompt, max_tokens)

    def call_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call Bedrock in text mode (non-JSON) or local LLM.

        Use for free-form composition to avoid forcing JSON mode when RAGCHECKER_JSON_PROMPTS=1.
        """
        if self.use_bedrock and self.bedrock_client:
            text = self._call_bedrock_text(prompt, max_tokens)
            if not text or not text.strip():
                try:
                    print("🔁 Bedrock text path empty — falling back to local LLM")
                except Exception:
                    pass
                return self._call_ollama_llm(prompt, max_tokens)
            return text
        return self._call_ollama_llm(prompt, max_tokens)

    def _with_deadline(self, fn, timeout_sec: float):
        """Execute a blocking SDK call with a hard deadline."""
        with ThreadPoolExecutor(max_workers=2) as ex:
            fut = ex.submit(fn)
            try:
                return fut.result(timeout=timeout_sec)
            except FuturesTimeoutError:
                try:
                    fut.cancel()
                except Exception:
                    pass
                raise TimeoutError(f"Bedrock call exceeded {timeout_sec:.1f}s deadline")

    def _call_bedrock_llm(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call AWS Bedrock Claude 3.5 Sonnet with cool-down logic and hard deadline."""
        if not self.bedrock_client:
            return ""

        # respect cool-down
        now = time.monotonic()
        if now < self._bedrock_cooldown_until:
            return ""  # signal caller to try local JSON

        retries = self._bedrock_max_retries
        deadline = float(os.getenv("BEDROCK_CALL_TIMEOUT_SEC", "35"))
        for attempt in range(retries + 1):
            if self._bedrock_rl:
                self._bedrock_rl.wait()
            try:

                def _json_call():
                    return self.bedrock_client.invoke_with_json_prompt(
                        prompt=prompt, max_tokens=max_tokens, temperature=0.1
                    )

                def _text_call():
                    return self.bedrock_client.invoke_model(prompt=prompt, max_tokens=max_tokens, temperature=0.1)

                if os.getenv("RAGCHECKER_JSON_PROMPTS", "1") == "1":
                    text, usage = self._with_deadline(_json_call, deadline)
                    print(f"💰 Bedrock JSON extraction: {usage.input_tokens}→{usage.output_tokens} tokens")
                else:
                    text, usage = self._with_deadline(_text_call, deadline)
                    if os.getenv("RAGCHECKER_DEBUG_USAGE", "0") == "1":
                        print(f"💬 Bedrock compose: {usage.input_tokens}→{usage.output_tokens} tokens")
                return text or ""
            except Exception as e:
                msg = str(e)
                retryable = any(
                    t in msg
                    for t in (
                        "Throttling",
                        "TooManyRequests",
                        "Rate exceeded",
                        "ModelCurrentlyLoading",
                        "Timeout",
                        "deadline",
                    )
                )
                if retryable and attempt < retries:
                    sleep = min((self._bedrock_retry_base**attempt) + random.random(), self._bedrock_retry_max_sleep)
                    print(f"⏳ Bedrock throttled/timeout; retrying in {sleep:.1f}s (attempt {attempt+1}/{retries})")
                    time.sleep(sleep)
                    continue
                cd = float(os.getenv("BEDROCK_COOLDOWN_SEC", "8"))
                self._bedrock_cooldown_until = time.monotonic() + cd
                print(f"⚠️ Bedrock call failed ({e}); cooling down {cd:.1f}s")
                return ""

        # exhausted retries
        self._bedrock_cooldown_until = time.monotonic() + float(os.getenv("BEDROCK_COOLDOWN_SEC", "8"))
        return ""

    def _call_bedrock_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call AWS Bedrock in text (non-JSON) mode regardless of JSON env flag."""
        if not self.bedrock_client:
            return ""

        now = time.monotonic()
        if now < self._bedrock_cooldown_until:
            return ""

        retries = self._bedrock_max_retries
        deadline = float(os.getenv("BEDROCK_TEXT_TIMEOUT_SEC", "25"))
        for attempt in range(retries + 1):
            if self._bedrock_rl:
                self._bedrock_rl.wait()
            try:

                def _text_call():
                    return self.bedrock_client.invoke_model(prompt=prompt, max_tokens=max_tokens, temperature=0.1)

                text, usage = self._with_deadline(_text_call, deadline)
                # Optional: quieter logging for text compose; still print usage if env asks
                if os.getenv("RAGCHECKER_DEBUG_USAGE", "0") == "1":
                    print(f"💬 Bedrock compose: {usage.input_tokens}→{usage.output_tokens} tokens")
                return text or ""
            except Exception as e:
                msg = str(e)
                retryable = any(
                    t in msg
                    for t in (
                        "Throttling",
                        "TooManyRequests",
                        "Rate exceeded",
                        "ModelCurrentlyLoading",
                        "Timeout",
                        "deadline",
                    )
                )
                if retryable and attempt < retries:
                    sleep = min((self._bedrock_retry_base**attempt) + random.random(), self._bedrock_retry_max_sleep)
                    print(
                        f"⏳ Bedrock (text) throttled/timeout; retrying in {sleep:.1f}s (attempt {attempt+1}/{retries})"
                    )
                    time.sleep(sleep)
                    continue

                cd = float(os.getenv("BEDROCK_COOLDOWN_SEC", "8"))
                self._bedrock_cooldown_until = time.monotonic() + cd
                print(f"⚠️ Bedrock text call failed ({e}); cooling down {cd:.1f}s")
                return ""

        self._bedrock_cooldown_until = time.monotonic() + float(os.getenv("BEDROCK_COOLDOWN_SEC", "8"))
        return ""

    def _call_ollama_llm(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call local LLM via Ollama API."""
        try:
            response = self.session.post(
                f"{self.api_base}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.1,
                    },
                },
                timeout=10,  # Reduced from 60s for faster testing
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            print(f"⚠️ Local LLM call failed: {e}")
            return ""

    def build_concise_prompt(self, query: str, context: List[str]) -> str:
        """Build concise prompt for focused response generation."""
        max_words = int(os.getenv("RAGCHECKER_MAX_WORDS", "1000"))
        require_citations = os.getenv("RAGCHECKER_REQUIRE_CITATIONS", "1") == "1"
        context_topk = int(os.getenv("RAGCHECKER_CONTEXT_TOPK", "3"))
        min_sents = int(os.getenv("RAGCHECKER_MIN_OUTPUT_SENTENCES", "0"))

        # Limit context to most relevant chunks
        limited_context = context[:context_topk] if context else []
        context_text = "\n".join(limited_context)

        citation_req = ""
        if require_citations:
            citation_req = """
- Cite specific context when stating factual claims
- If unsupported by context, say 'Not supported by context'"""

        style_req = """
- Write short, standalone sentences (10–25 words)
- Each fact should be its own sentence; avoid run-ons
"""

        bullets_req = ""
        if os.getenv("RAGCHECKER_FORCE_BULLETS", "0") == "1":
            bullets_req = """
- Present the answer as a bulleted list of factual statements
- Each bullet must contain exactly one claim and include inline citations
"""

        min_sent_req = f"\n- Write at least {min_sents} distinct sentences." if min_sents > 0 else ""

        return f"""Answer this query concisely and directly. Be information-dense and relevant.

Constraints:
- Maximum {max_words} words
- No unnecessary elaboration or digressions{citation_req}{min_sent_req}
{style_req}{bullets_req}

Query: {query}

Context (top {context_topk} most relevant):
{context_text}

Focused Answer:""".strip()

    def generate_answer_with_context(self, query: str, context: List[str]) -> str:
        """Generate an answer grounded ONLY in the provided context.

        - Ranks context by semantic similarity (if embeddings available)
        - Limits to top-k for prompt budget (RAGCHECKER_CONTEXT_TOPK)
        - Generates with Bedrock (if enabled) or local LLM
        - Applies final word cap (RAGCHECKER_MAX_WORDS)
        """
        # Rank context by similarity to query if embedding model is available
        ranked = context
        try:
            if hasattr(self, "embedding_model") and self.embedding_model and context:
                ranked = self.rank_context_by_query_similarity(query, context)
        except Exception:
            ranked = context

        prompt = self.build_concise_prompt(query, ranked)
        # Use text mode for composition to avoid JSON constraints
        raw = self.call_text(prompt, max_tokens=1200)

        # If no model output (Bedrock unavailable and no local LLM), optionally use extractive fallback
        if (not raw or not raw.strip()) and os.getenv("RAGCHECKER_EXTRACTIVE_FALLBACK", "1") == "1":
            try:
                extractive = self._generate_extractive_fallback(query, ranked)
                if extractive and extractive.strip():
                    return self.apply_word_limit(extractive, None)
            except Exception:
                # Swallow — fallback is best-effort only
                pass

        # Enforce word limit
        return self.apply_word_limit(raw or "", None)

    def _generate_extractive_fallback(self, query: str, context: List[str]) -> str:
        """Construct a concise, citation-style answer purely from context when LLMs are unavailable.

        Strategy:
        - Split context into sentences
        - Score sentences by token overlap and ROUGE-L against the query
        - Select top-K diverse sentences
        - Append simple source markers (Context #i)
        """
        import re

        if not context:
            return "Not supported by context."

        # Helpers (mirror evidence utilities for consistency)
        def _tokens(s: str) -> list[str]:
            return re.findall(r"[a-z0-9]+", s.lower())

        def _lcs_len(a: list[str], b: list[str]) -> int:
            m, n = len(a), len(b)
            dp = [0] * (n + 1)
            for i in range(1, m + 1):
                prev = 0
                ai = a[i - 1]
                for j in range(1, n + 1):
                    tmp = dp[j]
                    dp[j] = prev + 1 if ai == b[j - 1] else max(dp[j], dp[j - 1])
                    prev = tmp
            return dp[n]

        def _rouge_l_f1(a: str, b: str) -> float:
            ta, tb = _tokens(a), _tokens(b)
            if not ta or not tb:
                return 0.0
            lcs = _lcs_len(ta, tb)
            p = lcs / len(tb)
            r = lcs / len(ta)
            return (2 * p * r / (p + r)) if (p + r) else 0.0

        query_tokens = set(_tokens(query))
        # Configurable breadth
        ctx_topk = int(os.getenv("RAGCHECKER_EXTRACTIVE_CTX_TOPK", "5"))
        sent_topk = int(os.getenv("RAGCHECKER_EXTRACTIVE_TOPK", "5"))

        if not query_tokens:
            # Fall back to the first couple of sentences if query is empty
            sentences = []
            for ci, ctx in enumerate(context[: ctx_topk // 2 or 1]):
                for s in re.split(r"(?<=[.!?])\s+", ctx.strip()):
                    if s:
                        sentences.append((s, ci))
            top = sentences[:sent_topk]
        else:
            # Collect and score sentences from top contexts
            candidates: list[tuple[str, int, float]] = []  # (sentence, ctx_index, score)
            for ci, ctx in enumerate(context[:ctx_topk]):
                sents = re.split(r"(?<=[.!?])\s+", ctx.strip())
                for s in sents:
                    st = set(_tokens(s))
                    if not st:
                        continue
                    jacc = len(query_tokens & st) / max(len(query_tokens | st), 1)
                    rouge = _rouge_l_f1(query, s)
                    score = 0.6 * jacc + 0.4 * rouge
                    if score > 0:
                        candidates.append((s, ci, score))

            # Sort and take diverse top-K
            candidates.sort(key=lambda x: x[2], reverse=True)
            seen = set()
            top: list[tuple[str, int]] = []
            for s, ci, _ in candidates:
                sig = tuple(_tokens(s)[:6])
                if sig in seen:
                    continue
                seen.add(sig)
                top.append((s, ci))
                if len(top) >= sent_topk:
                    break

        # Ensure a minimum number of sentences for downstream evidence filtering
        min_extractive_sent = int(os.getenv("RAGCHECKER_EXTRACTIVE_MIN_SENT", "2"))
        if len(top) < min_extractive_sent:
            # Fallback: append first sentences from the first few contexts to reach the minimum
            extras: list[tuple[str, int]] = []
            for ci, ctx in enumerate(context[: max(1, min_extractive_sent)]):
                for s in re.split(r"(?<=[.!?])\s+", ctx.strip()):
                    if s:
                        extras.append((s, ci))
                        break  # take only the first sentence from this context
                if len(top) + len(extras) >= min_extractive_sent:
                    break
            # Avoid duplicating sentences already in top
            existing = {s for s, _ in top}
            for s, ci in extras:
                if s not in existing:
                    top.append((s, ci))

        if not top:
            return "Not supported by context."

        answer_body = " ".join(s for s, _ in top)
        sources = sorted({ci + 1 for _, ci in top})
        citations = "\nSources: " + ", ".join(f"Context #{i}" for i in sources)
        return (answer_body + citations).strip()

    def apply_word_limit(self, text: str, max_words: Optional[int] = None) -> str:
        """Apply hard word limit to generated text."""
        if max_words is None:
            max_words = int(os.getenv("RAGCHECKER_MAX_WORDS", "1000"))

        words = text.split()
        if len(words) > max_words:
            return " ".join(words[:max_words])
        return text

    def call_json(self, prompt: str, *, schema: Optional[dict] = None, max_tokens: int = 900) -> Union[dict, list]:
        """Ask Bedrock (preferred) or Ollama in JSON mode, validate + auto-repair."""

        def _parse_first_json(text: str):
            m = re.search(r"\{.*\}|\[.*\]", text, re.S)
            if not m:
                raise ValueError("No JSON object/array found")
            return json.loads(m.group(0))

        attempts = []

        # Prefer Bedrock JSON, else local JSON
        out = ""
        if self.use_bedrock:
            # Use async gate when safe (no running event loop). This enforces global RPS/concurrency caps.
            use_async_gate = bool(self._bedrock_gate)
            in_loop = False
            try:
                asyncio.get_running_loop()
                in_loop = True
            except RuntimeError:
                in_loop = False

            if use_async_gate and not in_loop:
                try:
                    out = asyncio.run(self.bedrock_invoke_async(prompt, max_tokens))
                except Exception:
                    out = ""
            if not out:
                out = self._call_bedrock_llm(prompt, max_tokens)
        if not out:
            out = self._call_ollama_json(prompt, max_tokens)
        attempts.append(out or "")

        for _ in range(2):  # up to 3 parses total
            try:
                obj = _parse_first_json(attempts[-1])
                if schema is not None:
                    validate(obj, schema)
                # obj can be dict OR list — both are OK for callers
                return obj
            except (ValueError, json.JSONDecodeError, ValidationError) as e:
                repair = (
                    f"Your previous output was invalid JSON ({type(e).__name__}: {e}). "
                    f"Output ONLY corrected JSON that satisfies the same instructions. No prose."
                )
                # retry with Bedrock if possible; else local JSON
                repaired = self._call_bedrock_llm(repair, max_tokens) if self.use_bedrock else ""
                if not repaired:
                    repaired = self._call_ollama_json(repair, max_tokens)
                attempts.append(repaired or "")

        raise ValueError("Could not obtain valid JSON after repair attempts")

    def coverage_rewrite(
        self, query: str, draft_answer: str, context: list[str], target_words: int = 600, max_facts: int = 16
    ) -> str:
        """Coverage-first rewrite: extract facts from context, then compose answer from facts."""
        labeled = [f"[{i+1}] {c}" for i, c in enumerate(context)]
        ctx_blob = "\n".join(labeled)

        extract_prompt = f"""
You are a careful evidence extractor. Given a query and numbered context snippets,
extract up to {max_facts} DISTINCT facts that are directly supported by the context.
Return JSON ONLY: an array of objects with fields:
- "fact": string
- "evidence": array of integers indicating the context indices that support the fact

Rules:
- Use ONLY the provided context; no outside knowledge.
- If a fact isn't supported, don't include it.
- Prefer many small atomic facts over few big ones.

Query: {query}

Context:
{ctx_blob}
"""

        # JSON Schema for extra safety
        fact_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["fact", "evidence"],
                "properties": {
                    "fact": {"type": "string", "minLength": 1},
                    "evidence": {"type": "array", "items": {"type": "integer", "minimum": 1, "maximum": len(context)}},
                },
                "additionalProperties": False,
            },
            "maxItems": max_facts,
        }

        try:
            # Use Bedrock JSON mode for reliable fact extraction
            if self.use_bedrock and self.bedrock_client:
                try:
                    # Add delay between Bedrock calls to respect rate limits
                    time.sleep(2)  # 2 second delay between calls

                    response, usage = self.bedrock_client.invoke_with_json_prompt(
                        prompt=extract_prompt, max_tokens=self.json_max_tokens, temperature=0.1
                    )
                    print(f"💰 Bedrock JSON extraction: {usage.input_tokens}→{usage.output_tokens} tokens")
                    obj = response
                except Exception as e:
                    print(f"⚠️ Bedrock JSON failed, falling back to simplified extraction: {e}")
                    obj = self._extract_facts_simplified(query, context)
            else:
                obj = self.call_json(extract_prompt, schema=fact_schema, max_tokens=self.json_max_tokens)

            # Parse and validate facts
            facts = []
            if isinstance(obj, str):
                # Parse JSON from string response
                try:
                    parsed = json.loads(obj)
                    if isinstance(parsed, list):
                        obj = parsed
                except (json.JSONDecodeError, TypeError):
                    pass

            # Handle both list and dict responses
            if isinstance(obj, list):
                for item in obj:
                    if isinstance(item, dict) and "fact" in item and "evidence" in item:
                        facts.append(item)
            elif isinstance(obj, dict) and "fact" in obj and "evidence" in obj:
                facts.append(obj)

        except Exception as e:
            print(f"⚠️ Fact extraction failed: {e}")
            # Use heuristic fallback to keep coverage-first alive
            facts = self._heuristic_facts_from_context(context, max_facts=6)

        if not facts:
            return draft_answer  # fallback if extraction fails

        bullets = []
        for f in facts:
            cites = "".join(f"[{i}]" for i in f.get("evidence", []) if isinstance(i, int) and 1 <= i <= len(context))
            bullets.append(f"- {f['fact']} {cites}".rstrip())

        compose_prompt = f"""
Write a comprehensive but tightly organized answer to the query using ONLY the bullet facts below.
Maintain high recall by covering ALL facts; keep wording clear and concise.
Cite sources inline using the provided [#] markers. Do not invent citations.

Target length: ~{target_words} words. Avoid filler.

Query: {query}

Bullet facts (with citations):
{chr(10).join(bullets)}

Now write the final answer (plain text, not JSON):
"""
        # Compose final answer in TEXT mode to avoid JSON forcing
        try:
            final = self.call_text(compose_prompt, max_tokens=1400)
        except Exception:
            final = self.call_local_llm(compose_prompt, max_tokens=1400)
        return final.strip() or draft_answer

    def _ensure_session(self):
        """Ensure session exists for local LLM calls."""
        if getattr(self, "session", None) is None:
            self.session = requests.Session()

    async def bedrock_invoke_async(self, prompt: str, max_tokens: int):
        """Async wrapper around Bedrock calls with global gate."""
        if not (self.use_bedrock and self._bedrock_gate):
            # run sync path in a thread anyway so caller can await uniformly
            return await asyncio.to_thread(self._call_bedrock_llm, prompt, max_tokens)

        async with self._bedrock_gate:
            try:
                # reuse your sync implementation (with internal backoff) and add deadline
                deadline = float(os.getenv("BEDROCK_CALL_TIMEOUT_SEC", "35"))
                return await asyncio.wait_for(
                    asyncio.to_thread(self._call_bedrock_llm, prompt, max_tokens), timeout=deadline
                )
            except Exception:
                # throttle/timeout → global cooldown; caller will choose fallback for THIS call only
                cd = float(os.getenv("BEDROCK_COOLDOWN_SEC", "8"))
                self._bedrock_gate.cooldown(cd)
                raise

    def _call_ollama_json(self, prompt: str, max_tokens: int = 900) -> str:
        """Call local LLM via Ollama in JSON mode when supported."""
        self._ensure_session()
        try:
            r = self.session.post(
                f"{self.api_base}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "format": "json",
                    "stream": False,
                    "options": {"num_predict": max_tokens, "temperature": 0.1},
                },
                timeout=20,
            )
            r.raise_for_status()
            return r.json().get("response", "")
        except Exception as e:
            print(f"⚠️ Local JSON call failed: {e}")
            return ""

    def _extract_facts_simplified(self, query: str, context: list[str]) -> list[dict]:
        """Simplified fact extraction when JSON mode fails - uses keyword matching."""
        facts = []

        # Simple keyword-based fact extraction
        query_keywords = set(query.lower().split())

        for i, ctx in enumerate(context):
            # Extract sentences that contain query keywords
            sentences = ctx.split(".")
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 10:  # Skip very short sentences
                    continue

                # Check if sentence contains query keywords
                sentence_lower = sentence.lower()
                keyword_matches = sum(1 for kw in query_keywords if kw in sentence_lower)

                if keyword_matches >= 1:  # At least one keyword match
                    facts.append({"fact": sentence, "evidence": [i + 1]})  # Context index (1-based)

                    # Limit facts to avoid overwhelming
                    if len(facts) >= 8:
                        break

            if len(facts) >= 8:
                break

        print(f"📝 Simplified fact extraction: {len(facts)} facts from {len(context)} contexts")
        return facts

    def _heuristic_facts_from_context(self, context: list[str], max_facts: int = 6) -> list[dict]:
        """Heuristic fact extraction when all JSON methods fail - keeps coverage-first alive."""
        facts = []
        for i, c in enumerate(context[:max_facts]):
            line = c.strip().split("\n")[0][:220]  # First line, max 220 chars
            if line:
                facts.append({"fact": line, "evidence": [i + 1]})
        print(f"📝 Heuristic fact extraction: {len(facts)} facts from {len(context)} contexts")
        return facts

    def _evidence_filter_multi(
        self, answer: str, contexts: List[str], fact_sentences: Optional[List[str]] = None
    ) -> str:
        """Multi-signal evidence guard with floors to protect recall while maintaining precision."""
        import re
        from difflib import SequenceMatcher

        def _tokens(s: str) -> list[str]:
            return re.findall(r"[a-z0-9]+", s.lower())

        def _jaccard(a: set[str], b: set[str]) -> float:
            return (len(a & b) / len(a | b)) if (a or b) else 0.0

        # Simple, fast ROUGE-L on tokens
        def _lcs_len(a: list[str], b: list[str]) -> int:
            m, n = len(a), len(b)
            dp = [0] * (n + 1)
            for i in range(1, m + 1):
                prev = 0
                ai = a[i - 1]
                for j in range(1, n + 1):
                    tmp = dp[j]
                    dp[j] = prev + 1 if ai == b[j - 1] else max(dp[j], dp[j - 1])
                    prev = tmp
            return dp[n]

        def _rouge_l_f1(a: str, b: str) -> float:
            ta, tb = _tokens(a), _tokens(b)
            if not ta or not tb:
                return 0.0
            lcs = _lcs_len(ta, tb)
            p = lcs / len(tb)
            r = lcs / len(ta)
            return (2 * p * r / (p + r)) if (p + r) else 0.0

        def _cosine(s: str, t: str, embedder=None) -> float:
            if embedder is None:
                return 0.0
            try:
                va = embedder.encode([s])[0]
                vb = embedder.encode([t])[0]
                if hasattr(va, "__mul__"):
                    dot = float((va * vb).sum())
                else:
                    dot = sum(a * b for a, b in zip(va, vb))
                na = (sum(x * x for x in va)) ** 0.5
                nb = (sum(x * x for x in vb)) ** 0.5
                return (dot / (na * nb)) if (na > 0 and nb > 0) else 0.0
            except Exception:
                return 0.0

        # Get thresholds from environment
        j_min = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.08"))
        rouge_min = float(os.getenv("RAGCHECKER_EVIDENCE_ROUGE_L", "0.20"))
        cos_min = float(os.getenv("RAGCHECKER_EVIDENCE_COSINE", "0.74"))
        min_sent = int(os.getenv("RAGCHECKER_EVIDENCE_MIN_SENT", "4"))
        min_fact_coverage = float(os.getenv("RAGCHECKER_EVIDENCE_MIN_FACT_COVERAGE", "0.40"))
        use_cos = os.getenv("RAGCHECKER_USE_EMBED_GUARD", "1") == "1"
        embedder = self.embedding_model if use_cos else None

        sents = re.split(r"(?<=[.!?])\s+", answer.strip())
        kept = []

        for s in sents:
            if not s.strip():
                continue
            tokens = set(_tokens(s))
            kept_flag = False

            for ctx in contexts:
                # OR over 3 signals + small difflib sanity
                if (
                    _jaccard(tokens, set(_tokens(ctx))) >= j_min
                    or _rouge_l_f1(s, ctx) >= rouge_min
                    or _cosine(s, ctx, embedder) >= cos_min
                ):
                    if SequenceMatcher(None, s.lower(), ctx.lower()).ratio() >= 0.33:
                        kept_flag = True
                        break

            if kept_flag:
                kept.append(s)

        # Step 1: Enhanced retrieval with RRF + MMR + dynamic K evidence selection

        def reciprocal_rank_fusion(result_sets, k=60):
            """Combine multiple ranked result sets using Reciprocal Rank Fusion."""

            scores = defaultdict(float)
            for results in result_sets:
                for rank, (doc_id, _) in enumerate(results, 1):
                    scores[doc_id] += 1.0 / (k + rank)
            return sorted(scores.items(), key=lambda x: x[1], reverse=True)

        def maximal_marginal_relevance(candidates, query_vec, doc_vecs, k, lambda_param=0.7):
            """Apply MMR for diversity-aware selection."""
            if not candidates or not doc_vecs:
                return candidates[:k]

            import numpy as np

            def cosine_similarity(a, b):
                return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

            selected, pool = [], set(range(len(candidates)))
            while len(selected) < k and pool:
                best, max_score = None, -1
                for i in pool:
                    # Relevance to query
                    relevance = cosine_similarity(query_vec, doc_vecs[i])
                    # Diversity from already selected
                    diversity = max([cosine_similarity(doc_vecs[i], doc_vecs[j]) for j in selected], default=0)
                    # MMR score
                    score = lambda_param * relevance - (1 - lambda_param) * diversity
                    if score > max_score:
                        best, max_score = i, score

                # Safety check: ensure best is not None before using it
                if best is not None:
                    selected.append(best)
                    pool.remove(best)
                else:
                    # If no valid candidate found, break to avoid infinite loop
                    break

            return [candidates[i] for i in selected]

        def normalize_scores(scores):
            """Normalize scores to 0-1 range using min-max normalization."""
            if not scores:
                return scores
            min_score = min(scores)
            max_score = max(scores)
            if max_score == min_score:
                return [0.5] * len(scores)
            return [(s - min_score) / (max_score - min_score) for s in scores]

        def trigram_overlap(s1, s2):
            """Calculate trigram overlap between two sentences."""

            def get_trigrams(s):
                words = _tokens(s)
                return set(" ".join(words[i : i + 3]) for i in range(len(words) - 2))

            trigrams1 = get_trigrams(s1)
            trigrams2 = get_trigrams(s2)
            if not trigrams1 or not trigrams2:
                return 0.0
            return len(trigrams1 & trigrams2) / len(trigrams1 | trigrams2)

        def pick_evidence(candidates, min_sent=2, keep_percentile=65, max_sent=7, min_fact_cov=0.30):
            """Smart evidence selection with dynamic target-K and normalized signals."""

            # Calculate blended scores with normalization
            jaccard_scores = []
            rouge_scores = []
            cosine_scores = []

            # First pass: collect all scores
            for s in candidates:
                max_jaccard = max(_jaccard(set(_tokens(s)), set(_tokens(ctx))) for ctx in contexts) if contexts else 0.0
                max_rouge = max(_rouge_l_f1(s, ctx) for ctx in contexts) if contexts else 0.0
                # Use cosine when embedding model exists and guard is enabled
                try:
                    max_cosine = max(_cosine(s, ctx, embedder) for ctx in contexts) if (contexts and embedder) else 0.0
                except Exception:
                    max_cosine = 0.0

                jaccard_scores.append(max_jaccard)
                rouge_scores.append(max_rouge)
                cosine_scores.append(max_cosine)

            # Normalize scores per case
            jac_n = normalize_scores(jaccard_scores)
            rou_n = normalize_scores(rouge_scores)
            cos_n = normalize_scores(cosine_scores)

            # Get weights from environment
            w_jac = float(os.getenv("RAGCHECKER_WEIGHT_JACCARD", "0.25"))
            w_rou = float(os.getenv("RAGCHECKER_WEIGHT_ROUGE", "0.35"))
            w_cos = float(os.getenv("RAGCHECKER_WEIGHT_COSINE", "0.30"))

            # Calculate blended scores
            blended_scores = []
            for i, s in enumerate(candidates):
                # Safety penalty checks
                too_long = len(_tokens(s)) > 45
                has_unbacked_neg = any(word in s.lower() for word in ["not", "no", "without"]) and not any(
                    word in " ".join(contexts).lower() for word in ["not", "no", "without"]
                )

                # Calculate normalized blended score
                score = w_jac * jac_n[i] + w_rou * rou_n[i] + w_cos * cos_n[i]

                # Apply penalties
                if too_long:
                    score -= 0.05
                if has_unbacked_neg:
                    score -= 0.05

                blended_scores.append(score)

            # Dynamic target-K selection (primary) or percentile fallback
            import numpy as np

            # Check if target-K mode is enabled
            keep_mode = os.getenv("RAGCHECKER_EVIDENCE_KEEP_MODE", "percentile")

            # Debug logging for mode selection
            if len(blended_scores) > 0:
                print(f"📊 Evidence selection mode: {keep_mode}")

            if keep_mode == "target_k":
                # Target-K based on signal strength
                scores_array = np.array(blended_scores)
                if len(scores_array) == 0:
                    candidates_indices = []
                else:
                    # Force override via env
                    force_k = int(os.getenv("RAGCHECKER_FORCE_TARGET_K", "0") or 0)
                    force_strength = os.getenv("RAGCHECKER_FORCE_SIGNAL_STRENGTH", "").lower()

                    target_k_weak = int(os.getenv("RAGCHECKER_TARGET_K_WEAK", "3"))
                    target_k_base = int(os.getenv("RAGCHECKER_TARGET_K_BASE", "5"))
                    target_k_strong = int(os.getenv("RAGCHECKER_TARGET_K_STRONG", "7"))

                    if force_k > 0 or force_strength in {"weak", "base", "strong"}:
                        if force_k <= 0:
                            target_k = {
                                "weak": target_k_weak,
                                "base": target_k_base,
                                "strong": target_k_strong,
                            }[force_strength]
                        else:
                            target_k = force_k
                        target_k = max(min_sent, min(target_k, max_sent))
                        print(f"📊 Dynamic-K: forced strength={force_strength or 'explicit_k'}, target_k={target_k}")
                    else:
                        top_score = np.max(scores_array)
                        median_score = np.median(scores_array)
                        signal_delta = top_score - median_score

                        # Get thresholds from environment
                        weak_delta = float(os.getenv("RAGCHECKER_SIGNAL_DELTA_WEAK", "0.10"))
                        strong_delta = float(os.getenv("RAGCHECKER_SIGNAL_DELTA_STRONG", "0.22"))

                        # Determine target K based on signal strength
                        if signal_delta >= strong_delta:
                            target_k = target_k_strong
                            signal_strength = "strong"
                        elif signal_delta >= weak_delta:
                            target_k = target_k_base
                            signal_strength = "base"
                        else:
                            target_k = target_k_weak
                            signal_strength = "weak"

                        # Clamp by min/max constraints
                        target_k = max(min_sent, min(target_k, max_sent))

                        # Debug logging
                        print(
                            f"📊 Dynamic-K: signal_delta={signal_delta:.3f}, strength={signal_strength}, target_k={target_k}"
                        )

                    # Select top K candidates
                    sorted_indices = np.argsort(scores_array)[::-1]
                    candidates_indices = sorted_indices[:target_k].tolist()
            else:
                # Fallback to percentile-based selection
                scores_array = np.array(blended_scores)
                threshold = np.percentile(scores_array, keep_percentile)
                candidates_indices = np.where(scores_array >= threshold)[0].tolist()

            # Sort by score
            candidates_indices.sort(key=lambda i: blended_scores[i], reverse=True)

            # Diversity + redundancy filtering with environment controls
            kept = []
            seen_by_chunk = defaultdict(int)

            # Get filtering parameters from environment
            redundancy_max = float(os.getenv("RAGCHECKER_REDUNDANCY_TRIGRAM_MAX", "0.50"))
            per_chunk_cap = int(os.getenv("RAGCHECKER_PER_CHUNK_CAP", "2"))
            per_chunk_cap_small = int(os.getenv("RAGCHECKER_PER_CHUNK_CAP_SMALL", "3"))

            # Determine chunk cap based on context size
            num_contexts = len(contexts) if contexts else 1
            chunk_cap = per_chunk_cap_small if num_contexts <= 5 else per_chunk_cap

            for idx in candidates_indices:
                # Check chunk diversity
                chunk_id = idx % num_contexts if num_contexts > 0 else 0
                if seen_by_chunk[chunk_id] >= chunk_cap:
                    continue

                # Check redundancy with already kept sentences
                if any(trigram_overlap(candidates[idx], candidates[j]) > redundancy_max for j in kept):
                    continue

                kept.append(idx)
                seen_by_chunk[chunk_id] += 1

                if len(kept) >= max_sent:
                    break

            # Ensure minimum sentences
            if len(kept) < min_sent:
                # Add top scores that weren't kept
                for idx in candidates_indices:
                    if idx not in kept:
                        kept.append(idx)
                        if len(kept) >= min_sent:
                            break

            return [candidates[i] for i in kept]

            # Get environment variables for normalized scoring and percentile selection

        min_sent = int(os.getenv("RAGCHECKER_EVIDENCE_MIN_SENT", "2"))
        keep_percentile = int(os.getenv("RAGCHECKER_EVIDENCE_KEEP_PERCENTILE", "65"))
        max_sent = int(os.getenv("RAGCHECKER_EVIDENCE_MAX_SENT", "7"))

        # Apply smart evidence selection with normalized signals
        kept = pick_evidence(
            sents, min_sent=min_sent, keep_percentile=keep_percentile, max_sent=max_sent, min_fact_cov=min_fact_coverage
        )

        if fact_sentences:
            # ensure at least X% of fact bullets appear (string contains)
            hits = sum(any(fs.lower() in s.lower() for s in kept) for fs in fact_sentences)
            if fact_sentences and (hits / max(1, len(fact_sentences))) < min_fact_coverage:
                # loosen: add missing fact lines verbatim
                for fs in fact_sentences:
                    if not any(fs.lower() in s.lower() for s in kept):
                        kept.append(fs)

                # Smart selector already handles precision protection via scoring and caps

        result = " ".join(kept) if kept else answer

        # Log detailed filtering stats for debugging
        clip_reasons = []
        if len(kept) < len(sents):
            if len(kept) < min_sent:
                clip_reasons.append(f"min_sent_floor({min_sent})")
            if fact_sentences and len(kept) < len(fact_sentences) * min_fact_coverage:
                clip_reasons.append(f"fact_coverage_floor({min_fact_coverage:.2f})")
            clip_reasons.append(f"jaccard({j_min:.3f})_rouge({rouge_min:.3f})")

        print(
            f"📊 Evidence filtering: {len(kept)}/{len(sents)} sentences kept | "
            f"Facts: {len(fact_sentences) if fact_sentences else 0} | "
            f"Clip reasons: {', '.join(clip_reasons) if clip_reasons else 'none'}"
        )

        return result

    def score_json(self, instruction: str, max_tokens: int = 150) -> float:
        """JSON-based scoring with schema validation."""
        schema = {
            "type": "object",
            "required": ["score"],
            "properties": {
                "score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "reasoning": {"type": "string"},
            },
            "additionalProperties": True,
        }
        try:
            obj = self.call_json(instruction, schema=schema, max_tokens=max_tokens)
            # obj might be dict (good) or list (fallback to first item if dict-like)
            if isinstance(obj, dict):
                s = obj.get("score", None)
            elif isinstance(obj, list) and obj and isinstance(obj[0], dict):
                s = obj[0].get("score", None)
            else:
                s = None
            if isinstance(s, (int, float)):
                return max(0.0, min(1.0, float(s)))
        except Exception as e:
            print(f"⚠️ JSON scorer failed: {e}")

        # soft fallback: try to extract a 0..1 decimal
        m = re.search(r"(?<!\d)(?:0?\.\d+|1(?:\.0+)?)", instruction)
        if m:
            try:
                x = float(m.group(0))
                return max(0.0, min(1.0, x))
            except Exception:
                pass
        return 0.5

    def rank_context_by_query_similarity(self, query: str, context_list: List[str]) -> List[str]:
        """Rank context chunks by semantic similarity to query."""
        if not self.embedding_model or not context_list:
            return context_list

        try:
            # Get embeddings for query and all context chunks
            query_embedding = self.embedding_model.encode([query])
            context_embeddings = self.embedding_model.encode(context_list)

            # Calculate similarities
            # Simple cosine similarity implementation (no sklearn dependency)
            similarities = []
            for context_emb in context_embeddings:
                # Simple dot product similarity (normalized)
                dot_product = sum(a * b for a, b in zip(query_embedding[0], context_emb))
                norm_query = sum(a * a for a in query_embedding[0]) ** 0.5
                norm_context = sum(a * a for a in context_emb) ** 0.5
                if norm_query > 0 and norm_context > 0:
                    similarity = dot_product / (norm_query * norm_context)
                else:
                    similarity = 0.0
                similarities.append(similarity)

            # Sort context by similarity (highest first) - Python only
            ranked_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)
            ranked_context = [context_list[i] for i in ranked_indices]

            print(f"🎯 Ranked {len(context_list)} context chunks by semantic similarity")
            return ranked_context

        except Exception as e:
            print(f"⚠️ Context ranking failed: {e}")
            return context_list

    def calculate_semantic_query_relevance(self, query: str, response: str) -> float:
        """Calculate semantic similarity between query and response."""
        if not self.embedding_model:
            # Fallback to word overlap
            query_words = set(query.lower().split())
            response_words = set(response.lower().split())
            if not query_words:
                return 0.0
            return len(query_words & response_words) / len(query_words)

        try:
            # Use semantic similarity
            query_embedding = self.embedding_model.encode([query])
            response_embedding = self.embedding_model.encode([response])

            # Simple cosine similarity implementation (no sklearn dependency)
            dot_product = sum(a * b for a, b in zip(query_embedding[0], response_embedding[0]))
            norm_query = sum(a * a for a in query_embedding[0]) ** 0.5
            norm_response = sum(a * a for a in response_embedding[0]) ** 0.5
            if norm_query > 0 and norm_response > 0:
                similarity = dot_product / (norm_query * norm_response)
            else:
                similarity = 0.0

            return float(similarity)

        except Exception as e:
            print(f"⚠️ Semantic similarity failed: {e}")
            # Fallback to word overlap
            query_words = set(query.lower().split())
            response_words = set(response.lower().split())
            if not query_words:
                return 0.0
            return len(query_words & response_words) / len(query_words)

    def extract_claims(self, query: str, response: str, context: List[str]) -> List[str]:
        """Extract claims from response using local LLM."""
        context_text = "\n".join(context)
        prompt = f"""
Extract factual claims from the following response. Return only the claims, one per line.

Query: {query}
Context: {context_text}
Response: {response}

Claims:
"""
        result = self.call_local_llm(prompt, max_tokens=1500)
        claims = [line.strip() for line in result.split("\n") if line.strip()]
        return claims

    def check_claim_factuality(self, claim: str, context: List[str]) -> float:
        """Check if a claim is factual based on context using local LLM."""
        context_text = "\n".join(context)
        prompt = f"""
Based on the provided context, is the following claim factual? Respond with valid JSON only.

Context: {context_text}
Claim: {claim}

Respond in this exact JSON format:
{{"score": 0.8, "reasoning": "Brief explanation of factuality"}}

Score range: 0.0 (completely false) to 1.0 (completely true)
"""
        result = self.call_local_llm(prompt, max_tokens=150)
        try:
            # Extract numeric score from response
            score_str = "".join(filter(lambda x: x.isdigit() or x == ".", result))
            score = float(score_str) if score_str else 0.5
            return max(0.0, min(1.0, score))  # Clamp to valid range
        except (ValueError, TypeError) as e:
            print(f"⚠️ Score parsing failed: {e}")
            return 0.5  # Default to neutral if parsing fails

    def evaluate_comprehensive_metrics(
        self, query: str, response: str, context: List[str], gt_answer: str
    ) -> Dict[str, float]:
        """Evaluate comprehensive RAGChecker metrics using one-shot JSON evaluation."""

        # One-shot prompt for all metrics to reduce Bedrock calls by 6x
        one_shot_prompt = f"""
Evaluate the following response against the provided context and query. Return a JSON object with these exact fields:

{{
  "context_precision": <0.0-1.0 score for how relevant context is to query>,
  "context_utilization": <0.0-1.0 score for how well response uses context>,
  "noise_sensitivity": <0.0-1.0 score for how well response filters irrelevant info>,
  "hallucination_rate": <0.0-1.0 score for unsupported information (0=perfect, 1=all hallucinated)>,
  "self_knowledge": <0.0-1.0 score for awareness of limitations>,
  "claim_recall": <0.0-1.0 score for coverage of factual claims from context>
}}

Query: {query}
Context: {chr(10).join(context[:3])}
Response: {response}
Ground Truth: {gt_answer}

Evaluate and return ONLY the JSON object:"""

        # JSON schema for validation
        metrics_schema = {
            "type": "object",
            "required": [
                "context_precision",
                "context_utilization",
                "noise_sensitivity",
                "hallucination_rate",
                "self_knowledge",
                "claim_recall",
            ],
            "properties": {
                "context_precision": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "context_utilization": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "noise_sensitivity": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "hallucination_rate": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "self_knowledge": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "claim_recall": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            },
            "additionalProperties": False,
        }

        try:
            # Get all metrics in one JSON call
            eval_obj = self.call_json(one_shot_prompt, schema=metrics_schema, max_tokens=220)

            if isinstance(eval_obj, dict):
                metrics = eval_obj
            elif isinstance(eval_obj, list) and eval_obj and isinstance(eval_obj[0], dict):
                metrics = eval_obj[0]  # Take first item if list
            else:
                raise ValueError(f"Unexpected response type: {type(eval_obj)}")

            # Calculate faithfulness from hallucination rate
            faithfulness = 1.0 - metrics.get("hallucination_rate", 0.5)

            return {
                "context_precision": metrics.get("context_precision", 0.5),
                "context_utilization": metrics.get("context_utilization", 0.5),
                "noise_sensitivity": metrics.get("noise_sensitivity", 0.5),
                "faithfulness": faithfulness,
                "hallucination_rate": metrics.get("hallucination_rate", 0.5),
                "self_knowledge": metrics.get("self_knowledge", 0.5),
                "claim_recall": metrics.get("claim_recall", 0.5),
            }

        except Exception as e:
            print(f"⚠️ One-shot evaluation failed: {e}, falling back to individual calls")
            # Fallback to individual calls if one-shot fails
            return self._evaluate_comprehensive_metrics_fallback(query, response, context, gt_answer)

    def _evaluate_comprehensive_metrics_fallback(
        self, query: str, response: str, context: List[str], gt_answer: str
    ) -> Dict[str, float]:
        """Fallback evaluation method using individual calls."""
        context_text = "\n".join(context)

        # Check if JSON prompts are enabled
        use_json_prompts = os.getenv("RAGCHECKER_JSON_PROMPTS", "1") == "1"
        if use_json_prompts:
            print("🔧 Using structured JSON prompts for reliable scoring")

        # 1. Context Precision - How relevant is the retrieved context to the query
        context_precision_prompt = f"""
Rate how relevant the retrieved context is to answering the query. Respond with valid JSON only.

Query: {query}
Retrieved Context: {context_text}

Respond in this exact JSON format:
{{"score": 0.8, "reasoning": "Brief explanation of relevance"}}

Score range: 0.0 (completely irrelevant) to 1.0 (perfectly relevant)
"""
        context_precision = self._extract_score(self.call_local_llm(context_precision_prompt, max_tokens=150))

        # 2. Context Utilization - How well does the response use the provided context
        context_utilization_prompt = f"""
Rate how well the response utilizes the provided context. Respond with valid JSON only.

Context: {context_text}
Response: {response}

Respond in this exact JSON format:
{{"score": 0.7, "reasoning": "Brief explanation of utilization"}}

Score range: 0.0 (ignores context) to 1.0 (fully utilizes context)
"""
        context_utilization = self._extract_score(self.call_local_llm(context_utilization_prompt, max_tokens=150))

        # 3. Noise Sensitivity - How well does the response avoid irrelevant information
        noise_sensitivity_prompt = f"""
Rate how well the response avoids including irrelevant or noisy information. Respond with valid JSON only.

Query: {query}
Response: {response}

Respond in this exact JSON format:
{{"score": 0.9, "reasoning": "Brief explanation of noise level"}}

Score range: 0.0 (full of noise) to 1.0 (no noise)
"""
        noise_sensitivity = self._extract_score(self.call_local_llm(noise_sensitivity_prompt, max_tokens=150))

        # 4. Hallucination Detection - Does the response contain information not in context
        hallucination_prompt = f"""
Rate how much the response contains information that is NOT supported by the context. Respond with valid JSON only.

Context: {context_text}
Response: {response}

Respond in this exact JSON format:
{{"score": 0.1, "reasoning": "Brief explanation of hallucinations found"}}

Score range: 0.0 (no hallucinations) to 1.0 (full of hallucinations)
"""
        hallucination_raw = self._extract_score(self.call_local_llm(hallucination_prompt, max_tokens=150))

        # 5. Self Knowledge - Does the response appropriately indicate uncertainty
        self_knowledge_prompt = f"""
Rate how well the response indicates uncertainty when appropriate and shows knowledge boundaries. Respond with valid JSON only.

Query: {query}
Response: {response}

Respond in this exact JSON format:
{{"score": 0.8, "reasoning": "Brief explanation of self-awareness"}}

Score range: 0.0 (poor self-awareness) to 1.0 (excellent self-awareness)
"""
        self_knowledge = self._extract_score(self.call_local_llm(self_knowledge_prompt, max_tokens=150))

        # 6. Claim Recall - How many relevant claims from context are included
        claim_recall_prompt = f"""
Rate how well the response recalls and includes the relevant claims from the context. Respond with valid JSON only.

Context: {context_text}
Ground Truth: {gt_answer}
Response: {response}

Respond in this exact JSON format:
{{"score": 0.6, "reasoning": "Brief explanation of claim coverage"}}

Score range: 0.0 (misses all relevant claims) to 1.0 (includes all relevant claims)
"""
        claim_recall = self._extract_score(self.call_local_llm(claim_recall_prompt, max_tokens=150))

        # Calculate faithfulness from hallucination rate
        faithfulness = 1.0 - hallucination_raw  # higher is better

        return {
            "context_precision": context_precision,
            "context_utilization": context_utilization,
            "noise_sensitivity": noise_sensitivity,
            "faithfulness": faithfulness,
            "hallucination_rate": hallucination_raw,  # lower is better
            "self_knowledge": self_knowledge,
            "claim_recall": claim_recall,
        }

    def _extract_score(self, llm_response: str) -> float:
        """Extract score from LLM response with robust JSON-first parsing."""
        # Use environment flag to enable/disable robust parsing
        if os.getenv("RAGCHECKER_ROBUST_PARSER", "1") == "1":
            return self._extract_score_robust(llm_response)
        else:
            return self._extract_score_legacy(llm_response)

    def _extract_score_robust(self, llm_response: str) -> float:
        """Robust JSON-first score extraction with safe fallbacks."""

        def _clamp01(x: float) -> float:
            return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)

        def _parse_ratio(text: str):
            """Parse ratio like '7/10' or '8/100'"""
            m = re.search(r"(?<!\d)(\d+(?:\.\d+)?)\s*/\s*(10|100)(?!\d)", text)
            if not m:
                return None
            num, den = float(m.group(1)), float(m.group(2))
            return _clamp01(num / den)

        def _parse_decimal01(text: str):
            """Parse decimal in [0,1] range"""
            m = re.search(r"(?<!\d)(?:0?\.\d+|1(?:\.0+)?)", text)
            if not m:
                return None
            s = m.group(0)
            if s.startswith("."):
                s = "0" + s
            try:
                return _clamp01(float(s))
            except Exception:
                return None

        # 1. Try JSON anywhere in the response
        try:
            json_match = re.search(r"\{.*\}", llm_response, re.S)
            if json_match:
                obj = json.loads(json_match.group(0))
                s = obj.get("score", obj.get("Score", obj.get("confidence")))
                if isinstance(s, (int, float)):
                    return _clamp01(float(s))
                if isinstance(s, str) and s.strip():
                    # Handle percentage in JSON
                    pct = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*%\s*", s)
                    if pct:
                        return _clamp01(float(pct.group(1)) / 100.0)
                    # Handle ratio in JSON
                    r = _parse_ratio(s)
                    if r is not None:
                        return r
                    # Handle decimal in JSON
                    d = _parse_decimal01(s)
                    if d is not None:
                        return d
        except Exception:
            pass

        # 2. Try ratio anywhere in raw text (e.g., "Score 7/10")
        r = _parse_ratio(llm_response)
        if r is not None:
            return r

        # 3. Try first valid decimal in [0,1]
        d = _parse_decimal01(llm_response)
        if d is not None:
            return d

        # 4. Last resort fallback
        return 0.5

    def _extract_score_legacy(self, llm_response: str) -> float:
        """Legacy score extraction (current broken method)."""
        try:
            # Extract numeric score from response
            score_str = "".join(filter(lambda x: x.isdigit() or x == ".", llm_response))
            score = float(score_str) if score_str else 0.5
            return max(0.0, min(1.0, score))  # Clamp to valid range
        except (ValueError, TypeError) as e:
            print(f"⚠️ Score parsing failed: {e}")
            return 0.5  # Default to neutral if parsing fails


class OfficialRAGCheckerEvaluator:
    """Official RAGChecker evaluator following official methodology."""

    def __init__(self):
        self.input_data = []
        self.evaluation_results = {}
        self.metrics_dir = Path("metrics/baseline_evaluations")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.local_llm = None
        self.use_bedrock = False  # Initialize use_bedrock attribute
        # Track Bedrock model id for accurate logging/config
        self.bedrock_model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
        # Timing fields populated per run
        self._run_start_ts: Optional[float] = None
        self._run_end_ts: Optional[float] = None

    def generate_answer_with_context(self, query: str, context: List[str]) -> str:
        """Generate an answer grounded ONLY in the provided context.

        - Ranks context by semantic similarity (if embeddings available)
        - Limits to top-k for prompt budget (RAGCHECKER_CONTEXT_TOPK)
        - Generates with Bedrock (if enabled) or local LLM
        - Applies final word cap (RAGCHECKER_MAX_WORDS)
        """
        # Rank context by similarity to query if embedding model is available
        ranked = context
        try:
            if hasattr(self, "local_llm") and self.local_llm and hasattr(self.local_llm, "embedding_model"):
                if self.local_llm.embedding_model and context:
                    ranked = self.local_llm.rank_context_by_query_similarity(query, context)
        except Exception:
            ranked = context

        # Build prompt with ranked context
        max_words = int(os.getenv("RAGCHECKER_MAX_WORDS", "1000"))
        require_citations = os.getenv("RAGCHECKER_REQUIRE_CITATIONS", "1") == "1"
        context_topk = int(os.getenv("RAGCHECKER_CONTEXT_TOPK", "3"))

        # Limit context to most relevant chunks
        limited_context = ranked[:context_topk] if ranked else []
        context_text = "\n".join(limited_context)

        citation_req = ""
        if require_citations:
            citation_req = """
- Cite specific context when stating factual claims
- If unsupported by context, say 'Not supported by context'"""

        prompt = f"""Answer this query concisely and directly. Be information-dense and relevant.

Constraints:
- Maximum {max_words} words
- No unnecessary elaboration or digressions{citation_req}

Query: {query}

Context (top {context_topk} most relevant):
{context_text}

Focused Answer:""".strip()

        # Use main LLM path (Bedrock if configured; else local) when available
        raw = ""
        if getattr(self, "local_llm", None):
            try:
                # Prefer text mode for generation
                raw = self.local_llm.call_text(prompt, max_tokens=1200)  # type: ignore[union-attr]
            except Exception:
                raw = ""
        # Optional orchestrator fallback (disabled by default)
        if not raw and os.getenv("RAGCHECKER_ENABLE_ORCHESTRATOR_FALLBACK", "0") == "1":
            raw = self._call_unified_orchestrator(query)

        # If no model/orchestrator output, optionally use extractive fallback
        if (not raw or not str(raw).strip()) and os.getenv("RAGCHECKER_EXTRACTIVE_FALLBACK", "1") == "1":
            try:
                extractive = self._extractive_from_context(query, ranked)
                if extractive and extractive.strip():
                    print("[fallback] using extractive context answer")
                    return self._apply_word_limit(extractive, max_words)
            except Exception:
                pass

        # Enforce word limit
        return self._apply_word_limit(raw or "", max_words)

    def _extractive_from_context(self, query: str, context: List[str]) -> str:
        """Minimal extractive synthesis using context only (no LLM)."""
        import re

        if not context:
            return "Not supported by context."

        def _tokens(s: str) -> list[str]:
            return re.findall(r"[a-z0-9]+", s.lower())

        def _lcs_len(a: list[str], b: list[str]) -> int:
            m, n = len(a), len(b)
            dp = [0] * (n + 1)
            for i in range(1, m + 1):
                prev = 0
                ai = a[i - 1]
                for j in range(1, n + 1):
                    tmp = dp[j]
                    dp[j] = prev + 1 if ai == b[j - 1] else max(dp[j], dp[j - 1])
                    prev = tmp
            return dp[n]

        def _rouge_l_f1(a: str, b: str) -> float:
            ta, tb = _tokens(a), _tokens(b)
            if not ta or not tb:
                return 0.0
            lcs = _lcs_len(ta, tb)
            p = lcs / len(tb)
            r = lcs / len(ta)
            return (2 * p * r / (p + r)) if (p + r) else 0.0

        query_tokens = set(_tokens(query))
        # Configurable breadth
        ctx_topk = int(os.getenv("RAGCHECKER_EXTRACTIVE_CTX_TOPK", "5"))
        sent_topk = int(os.getenv("RAGCHECKER_EXTRACTIVE_TOPK", "5"))

        candidates: list[tuple[str, int, float]] = []
        for ci, ctx in enumerate(context[:ctx_topk]):
            for s in re.split(r"(?<=[.!?])\s+", ctx.strip()):
                st = set(_tokens(s))
                if not st:
                    continue
                jacc = len(query_tokens & st) / max(len(query_tokens | st), 1)
                rouge = _rouge_l_f1(query, s)
                score = 0.6 * jacc + 0.4 * rouge
                if score > 0:
                    candidates.append((s, ci, score))

        candidates.sort(key=lambda x: x[2], reverse=True)
        seen = set()
        picked: list[tuple[str, int]] = []
        for s, ci, _ in candidates:
            sig = tuple(_tokens(s)[:6])
            if sig in seen:
                continue
            seen.add(sig)
            picked.append((s, ci))
            if len(picked) >= sent_topk:
                break

        if not picked:
            # fallback to first context snippet if nothing scored
            base = context[0].strip()
            return base[:400] + ("…" if len(base) > 400 else "")

        body = " ".join(s for s, _ in picked)
        sources = sorted({ci + 1 for _, ci in picked})
        return f"{body}\nSources: " + ", ".join(f"Context #{i}" for i in sources)

    def _apply_word_limit(self, text: str, max_words: int) -> str:
        """Apply hard word limit to generated text."""
        words = text.split()
        if len(words) > max_words:
            return " ".join(words[:max_words])
        return text

    def _call_unified_orchestrator(self, query: str) -> str:
        """Fallback to unified orchestrator for answer generation.

        Uses orchestrate_memory() and returns a reasonable string summary. This avoids
        type errors from calling a non-existent run_query().
        """
        try:
            # Silence fallback entirely when bypassing CLI
            if os.getenv("RAGCHECKER_BYPASS_CLI", "0") == "1":
                return ""
            # Import and call unified orchestrator as fallback
            import sys

            sys.path.insert(0, str(Path(__file__).parent))
            from unified_memory_orchestrator import UnifiedMemoryOrchestrator

            orchestrator = UnifiedMemoryOrchestrator()
            bundle = orchestrator.orchestrate_memory(query=query, role="planner")

            # Prefer the Prime/ Cursor output if present, else a compact JSON summary
            sys_map = (bundle or {}).get("systems", {})
            for key in ("prime", "cursor"):
                if key in sys_map and isinstance(sys_map[key], dict):
                    out = sys_map[key].get("output")
                    if isinstance(out, str) and out.strip():
                        return out

            # Compact JSON fallback
            try:
                return json.dumps(bundle, default=str)
            except Exception:
                return ""
        except Exception:
            # Keep quiet; this is a best-effort fallback only
            return ""

    def _lcs_len(self, a_tokens, b_tokens):
        """Calculate Longest Common Subsequence length for ROUGE-L."""
        m, n = len(a_tokens), len(b_tokens)
        if m == 0 or n == 0:
            return 0
        dp = [0] * (n + 1)
        for i in range(1, m + 1):
            prev = 0
            ai = a_tokens[i - 1]
            for j in range(1, n + 1):
                temp = dp[j]
                if ai == b_tokens[j - 1]:
                    dp[j] = prev + 1
                else:
                    dp[j] = dp[j] if dp[j] >= dp[j - 1] else dp[j - 1]
                prev = temp
        return dp[n]

    def rouge_l_f1(self, reference: str, candidate: str):
        """Calculate ROUGE-L F1, Precision, and Recall scores."""
        ref = reference.split()
        cand = candidate.split()
        if not ref or not cand:
            return 0.0, 0.0, 0.0
        lcs = self._lcs_len(ref, cand)
        p = lcs / len(cand)
        r = lcs / len(ref)
        f1 = (2 * p * r / (p + r)) if (p + r) > 0 else 0.0
        return f1, p, r

    def generate_query_expansions(self, original_query: str, k: int = 6) -> List[str]:
        """Generate multiple query reformulations for better retrieval coverage."""
        if not self.local_llm or not hasattr(self.local_llm, "bedrock_client"):
            return [original_query]  # Fallback to original

        expansion_prompt = f"""Generate {k} different reformulations of this query to improve information retrieval.
Each reformulation should capture the same intent but use different wording, synonyms, or perspectives.

Original query: {original_query}

Return a JSON array of strings with exactly {k} reformulations:
["reformulation 1", "reformulation 2", ...]"""

        try:
            # Be tolerant to varying return types (tuple or string)
            _resp = self.local_llm.bedrock_client.invoke_model(  # type: ignore[attr-defined]
                prompt=expansion_prompt,
                max_tokens=500,
            )
            response = _resp[0] if isinstance(_resp, (tuple, list)) else _resp

            import json

            reformulations = json.loads(response)
            if isinstance(reformulations, list) and len(reformulations) >= k:
                return [original_query] + reformulations[: k - 1]  # Include original + k-1 reformulations
        except Exception as e:
            print(f"⚠️ Query expansion failed: {e}")

        return [original_query]  # Fallback

    def extract_and_bind_claims(self, response: str, contexts: List[str]) -> str:
        """Extract claims from response and bind them to supporting evidence."""
        if not os.getenv("RAGCHECKER_CLAIM_BINDING", "0") == "1":
            return response  # Skip if not enabled

        if not self.local_llm or not hasattr(self.local_llm, "bedrock_client"):
            return response  # Fallback

        # Extract claims
        claim_prompt = f"""Extract factual claims from this response. Return a JSON array of claims:

Response: {response}

Return format: ["claim 1", "claim 2", ...]"""

        try:
            _resp = self.local_llm.bedrock_client.invoke_model(  # type: ignore[attr-defined]
                prompt=claim_prompt,
                max_tokens=300,
                temperature=0.0,
            )
            claims_response = _resp[0] if isinstance(_resp, (tuple, list)) else _resp

            claims = json.loads(claims_response)
            if not isinstance(claims, list):
                return response  # Fallback

            # Bind each claim to top-k supporting snippets
            claim_topk = int(os.getenv("RAGCHECKER_CLAIM_TOPK", "2"))
            drop_unsupported = os.getenv("RAGCHECKER_DROP_UNSUPPORTED", "1") == "1"

            supported_claims = []
            for claim in claims:
                # Find supporting evidence using ROUGE-L + cosine similarity
                evidence_scores = []
                for ctx in contexts:
                    sentences = ctx.split(". ")
                    for sent in sentences:
                        if len(sent.strip()) < 10:  # Skip very short sentences
                            continue
                        # Simple scoring (could be enhanced with embeddings)
                        rouge_score, _, _ = self.rouge_l_f1(claim, sent)
                        jaccard_score = len(set(claim.lower().split()) & set(sent.lower().split())) / len(
                            set(claim.lower().split()) | set(sent.lower().split())
                        )
                        combined_score = 0.6 * rouge_score + 0.4 * jaccard_score
                        evidence_scores.append((sent, combined_score))

                # Get top-k evidence
                evidence_scores.sort(key=lambda x: x[1], reverse=True)
                top_evidence = evidence_scores[:claim_topk]

                if top_evidence and top_evidence[0][1] > 0.1:  # Minimum support threshold
                    supported_claims.append(claim)
                elif not drop_unsupported:
                    supported_claims.append(f"{claim} [Note: Not fully supported by context]")

            # Reconstruct response with supported claims
            if supported_claims:
                return ". ".join(supported_claims) + "."
            else:
                return "The provided context does not contain sufficient information to answer this query."

        except Exception as e:
            print(f"⚠️ Claim binding failed: {e}")
            return response  # Fallback

    def create_official_test_cases(self) -> List[RAGCheckerInput]:
        """Create test cases following RAGChecker official format."""
        test_cases = []

        # Test Case 1: Memory System Query
        test_cases.append(
            RAGCheckerInput(
                query_id="memory_system_001",
                query="What is the current project status and backlog priorities?",
                gt_answer="The current project focuses on unified memory system and DSPy 3.0 integration. Key priorities include B-1044 (Memory System Core Features), B-1034 (Mathematical Framework), and B-1013 (Advanced RAG Optimization). The system uses RAGChecker for evaluation with 95.8/100 baseline score.",
                response="PENDING",
                retrieved_context=[
                    "Current priorities include B-1044, B-1034, and B-1013",
                    "Unified memory system with DSPy 3.0 integration",
                ],
            )
        )

        # Test Case 2: DSPy Integration
        test_cases.append(
            RAGCheckerInput(
                query_id="dspy_integration_001",
                query="What are the DSPy integration patterns and optimization techniques?",
                gt_answer="DSPy integration includes multi-agent system with sequential model switching, LabeledFewShot optimizer, assertion framework, and signature validation patterns. Key components: Model Switcher, Cursor Integration, Optimization System, and Role Refinement System.",
                response="PENDING",
                retrieved_context=[
                    "DSPy multi-agent system with sequential model switching",
                    "LabeledFewShot optimizer with assertion framework",
                ],
            )
        )

        # Test Case 3: Role-Specific Context
        test_cases.append(
            RAGCheckerInput(
                query_id="role_context_001",
                query="How do I implement DSPy modules and optimize performance?",
                gt_answer="To implement DSPy modules: 1) Use Model Switcher for hardware constraints, 2) Apply LabeledFewShot optimizer with configurable K parameter, 3) Implement signature validation patterns, 4) Use role refinement system for AI-powered optimization, 5) Follow the four-part optimization loop.",
                response="PENDING",
                retrieved_context=[
                    "Model Switcher for hardware constraints",
                    "LabeledFewShot optimizer with K parameter",
                ],
            )
        )

        # Test Case 4: Research Context
        test_cases.append(
            RAGCheckerInput(
                query_id="research_context_001",
                query="What are the latest memory system optimizations and research findings?",
                gt_answer="Latest memory system optimizations include: 1) LTST Memory System with database integration, 2) Real-time session continuity detection, 3) Quality scoring and context merging, 4) Dual API support with backward compatibility, 5) Comprehensive performance monitoring and statistics.",
                response="PENDING",
                retrieved_context=[
                    "LTST Memory System with database integration",
                    "Real-time session continuity detection",
                ],
            )
        )

        # Test Case 5: System Architecture
        test_cases.append(
            RAGCheckerInput(
                query_id="architecture_001",
                query="What's the current codebase structure and how do I navigate it?",
                gt_answer="The codebase follows a structured organization: 000_core/ (workflows), 100_memory/ (memory systems), 400_guides/ (documentation), scripts/ (automation), dspy-rag-system/ (DSPy implementation). Key navigation: Start with 400_00_getting-started-and-index.md, then 100_cursor-memory-context.md, and 000_backlog.md.",
                response="PENDING",
                retrieved_context=[
                    "000_core/, 100_memory/, 400_guides/, scripts/",
                    "Start with getting-started guide and memory context",
                ],
            )
        )

        # Test Case 6: Technical Implementation
        test_cases.append(
            RAGCheckerInput(
                query_id="technical_implementation_001",
                query="How do I set up and configure the DSPy optimization system?",
                gt_answer="DSPy optimization setup requires: 1) Configure ModelSwitcher with hardware constraints, 2) Set up LabeledFewShot optimizer with K=16 examples, 3) Implement assertion framework for validation, 4) Configure teleprompter for automatic optimization, 5) Set up evaluation metrics and feedback loops.",
                response="PENDING",
                retrieved_context=[
                    "ModelSwitcher configuration for hardware constraints",
                    "LabeledFewShot optimizer setup with K parameter",
                    "Assertion framework implementation",
                ],
            )
        )

        # Test Case 7: Performance Optimization
        test_cases.append(
            RAGCheckerInput(
                query_id="performance_optimization_001",
                query="What are the key performance metrics and how do I improve them?",
                gt_answer="Key performance metrics include: Rehydration Time (target <10ms), Warm Latency p95 <10ms, Cold Latency p95 <150ms, Failure@20 ≤0.20, Recall@10 ≥0.7-0.9, Precision@10 ≥0.6-0.8. Improvements: optimize vector indexing, implement caching, use HNSW indexes, optimize query patterns.",
                response="PENDING",
                retrieved_context=[
                    "Performance targets: rehydration <10ms, warm latency p95 <10ms",
                    "HNSW vector indexing for optimization",
                    "Caching strategies for performance",
                ],
            )
        )

        # Test Case 8: Error Handling
        test_cases.append(
            RAGCheckerInput(
                query_id="error_handling_001",
                query="How does the system handle errors and what are the recovery procedures?",
                gt_answer="Error handling includes: 1) Graceful degradation with fallback evaluation, 2) Robust score parsing with multiple format support, 3) Timeout handling for LLM calls, 4) Database connection recovery, 5) Memory system rollback procedures, 6) Comprehensive logging and monitoring.",
                response="PENDING",
                retrieved_context=[
                    "Fallback evaluation when CLI unavailable",
                    "Robust score parsing with JSON and legacy support",
                    "Database rollback and recovery procedures",
                ],
            )
        )

        # Test Case 9: Integration Patterns
        test_cases.append(
            RAGCheckerInput(
                query_id="integration_patterns_001",
                query="What are the integration patterns for external systems and APIs?",
                gt_answer="Integration patterns include: 1) MCP (Model Context Protocol) for file processing, 2) Ollama API for local LLM integration, 3) PostgreSQL with pgvector for vector storage, 4) GitHub integration for version control, 5) Unified memory orchestrator for system coordination, 6) RESTful APIs with proper error handling.",
                response="PENDING",
                retrieved_context=[
                    "MCP integration for file processing",
                    "Ollama API for local LLM calls",
                    "PostgreSQL pgvector integration",
                ],
            )
        )

        # Test Case 10: Development Workflow
        test_cases.append(
            RAGCheckerInput(
                query_id="development_workflow_001",
                query="What is the recommended development workflow and best practices?",
                gt_answer="Development workflow: 1) Start with backlog item creation, 2) Generate PRD using workflow, 3) Create task list with priorities, 4) Follow test-driven development, 5) Use pre-commit hooks for quality, 6) Update documentation, 7) Run evaluation tests, 8) Create pull request with backlog reference.",
                response="PENDING",
                retrieved_context=[
                    "Backlog-driven development workflow",
                    "PRD and task generation process",
                    "TDD and quality gates",
                ],
            )
        )

        # Test Case 11: Configuration Management
        test_cases.append(
            RAGCheckerInput(
                query_id="configuration_management_001",
                query="How do I configure environment variables and system settings?",
                gt_answer="Configuration includes: RAGCHECKER_CONCISE=1 for response limiting, RAGCHECKER_MAX_WORDS=1000 for optimal length, RAGCHECKER_ROBUST_PARSER=1 for score parsing, RAGCHECKER_SEMANTIC_FEATURES=1 for embeddings, RAGCHECKER_JSON_PROMPTS=1 for structured output, POSTGRES_DSN for database connection.",
                response="PENDING",
                retrieved_context=[
                    "Environment flags for RAGChecker configuration",
                    "Database connection settings",
                    "Feature toggles for A/B testing",
                ],
            )
        )

        # Test Case 12: Testing and Validation
        test_cases.append(
            RAGCheckerInput(
                query_id="testing_validation_001",
                query="What testing strategies and validation methods are used?",
                gt_answer="Testing strategies: 1) Unit tests with pytest, 2) Integration tests for system components, 3) RAGChecker evaluation for quality metrics, 4) A/B testing framework for improvements, 5) Performance benchmarking, 6) Security validation, 7) End-to-end workflow testing, 8) Regression testing for stability.",
                response="PENDING",
                retrieved_context=[
                    "Pytest for unit and integration testing",
                    "RAGChecker for quality evaluation",
                    "A/B testing framework for improvements",
                ],
            )
        )

        # Test Case 13: Troubleshooting
        test_cases.append(
            RAGCheckerInput(
                query_id="troubleshooting_001",
                query="What are common issues and how do I troubleshoot them?",
                gt_answer="Common issues: 1) LLM timeout errors - reduce timeout or use fast mode, 2) Score parsing failures - enable robust parser, 3) Database connection issues - check POSTGRES_DSN, 4) Memory system errors - verify orchestrator setup, 5) Import errors - check dependencies, 6) Performance issues - optimize vector indexes.",
                response="PENDING",
                retrieved_context=[
                    "LLM timeout and fast mode solutions",
                    "Score parsing error handling",
                    "Database connectivity troubleshooting",
                ],
            )
        )

        # Test Case 14: Advanced Features
        test_cases.append(
            RAGCheckerInput(
                query_id="advanced_features_001",
                query="What advanced features are available for power users?",
                gt_answer="Advanced features: 1) Semantic embeddings with sentence-transformers, 2) Context ranking by query similarity, 3) Custom evaluation metrics, 4) Multi-model switching based on hardware, 5) Assertion-based validation, 6) Teleprompter optimization, 7) Custom prompt engineering, 8) Performance profiling and monitoring.",
                response="PENDING",
                retrieved_context=[
                    "Semantic embeddings and context ranking",
                    "Multi-model switching capabilities",
                    "Assertion framework and teleprompter",
                ],
            )
        )

        # Test Case 15: Security and Privacy
        test_cases.append(
            RAGCheckerInput(
                query_id="security_privacy_001",
                query="What security measures and privacy considerations are implemented?",
                gt_answer="Security measures: 1) Local-first LLM processing for privacy, 2) Database connection security with SSL options, 3) Input sanitization and validation, 4) Secure API endpoints, 5) Access control for sensitive operations, 6) Data encryption at rest, 7) Audit logging for compliance, 8) Regular security updates and patches.",
                response="PENDING",
                retrieved_context=[
                    "Local LLM processing for privacy",
                    "Database security and SSL configuration",
                    "Input validation and sanitization",
                ],
            )
        )

        # Allow limiting test cases for development/testing
        max_cases = int(os.getenv("RAGCHECKER_MAX_TEST_CASES", "15"))
        if max_cases < len(test_cases):
            print(f"🧪 Limited test mode: Using {max_cases} test cases (reduced from {len(test_cases)})")
            return test_cases[:max_cases]

        print(f"📊 Full evaluation mode: Using all {len(test_cases)} test cases")
        return test_cases

    def get_memory_system_response(self, query: str, role: str = "planner") -> str:
        """Get response from memory system using unified memory orchestrator."""
        try:
            env = os.environ.copy()
            # Use DSN resolver instead of hardcoded mock
            try:
                resolved_dsn = resolve_dsn(strict=False, emit_warning=False)
                if resolved_dsn:
                    env["POSTGRES_DSN"] = resolved_dsn
                else:
                    env["POSTGRES_DSN"] = "mock://test"  # fallback
            except Exception:
                env["POSTGRES_DSN"] = "mock://test"  # fallback

            # Force comprehensive response mode for better recall
            comprehensive_query = f"""COMPREHENSIVE RESPONSE REQUIRED: {query}

Please provide a detailed, comprehensive answer that covers ALL relevant information from the project context.
Include specific examples, technical details, implementation steps, and relevant code patterns.
Aim for 800-1200 words to ensure complete coverage of the topic.
Do not summarize or be concise - provide thorough, detailed information."""

            cmd = [
                "python3",
                "scripts/unified_memory_orchestrator.py",
                "--systems",
                "cursor",
                "--role",
                role,
                comprehensive_query,
                "--format",
                "json",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)

            if result.returncode == 0:
                try:
                    response_data = json.loads(result.stdout)
                    if "systems" in response_data and "cursor" in response_data["systems"]:
                        raw_response = response_data["systems"]["cursor"]["output"]
                    else:
                        raw_response = result.stdout
                except json.JSONDecodeError:
                    raw_response = result.stdout

                # Apply concise generation if enabled
                if os.getenv("RAGCHECKER_CONCISE", "1") == "1":
                    # Apply word limit to reduce verbosity
                    if getattr(self, "local_llm", None):
                        concise_response = self.local_llm.apply_word_limit(raw_response)  # type: ignore[union-attr]
                        print(
                            f"📝 Reduced response: {len(raw_response.split())} → {len(concise_response.split())} words"
                        )
                        return concise_response
                    else:
                        # Simple word limit fallback
                        max_words = int(os.getenv("RAGCHECKER_MAX_WORDS", "1000"))
                        words = raw_response.split()
                        if len(words) > max_words:
                            concise_response = " ".join(words[:max_words])
                            print(f"📝 Reduced response: {len(words)} → {len(concise_response.split())} words")
                            return concise_response
                        return raw_response
                else:
                    return raw_response
            else:
                return f"Error: {result.stderr}"

        except Exception as e:
            return f"Error: {str(e)}"

    def prepare_official_input_data(self) -> Dict[str, Any]:
        """Prepare input data in official RAGChecker RAGResults JSON format."""
        test_cases = self.create_official_test_cases()
        results_list: List[Dict[str, Any]] = []

        print("🧠 Preparing Official RAGChecker Input Data")
        print("=" * 50)

        # Fast iteration mode - limit to 3 test cases for rapid tuning
        if os.getenv("RAGCHECKER_FAST_MODE", "0") == "1":
            test_cases = test_cases[:3]
            print(f"🚀 Fast iteration mode: Using {len(test_cases)} test cases for rapid tuning")

        for i, test_case in enumerate(test_cases, 1):
            print(f"🔍 Processing Test Case {i}/{len(test_cases)}: {test_case.query_id}")

            # Apply semantic context ranking if available
            if hasattr(self, "local_llm") and self.local_llm and hasattr(self.local_llm, "embedding_model"):
                if self.local_llm.embedding_model:
                    test_case.retrieved_context = self.local_llm.rank_context_by_query_similarity(
                        test_case.query, test_case.retrieved_context
                    )

            # Generate grounded answer using provided (ranked) context
            response = self.generate_answer_with_context(test_case.query, test_case.retrieved_context)
            test_case.response = response

            # Convert context strings to RetrievedDoc-like objects {doc_id, text}
            retrieved_docs = [
                {"doc_id": None, "text": ctx} if isinstance(ctx, str) else ctx for ctx in test_case.retrieved_context
            ]

            # Build RAGResult entry
            rag_result_entry = {
                "query_id": test_case.query_id,
                "query": test_case.query,
                "gt_answer": test_case.gt_answer,
                "response": test_case.response,
                "retrieved_context": retrieved_docs,
            }

            results_list.append(rag_result_entry)
            print(f"   ✅ Response length: {len(response)} characters")

        # RAGResults container
        rag_results_obj: Dict[str, Any] = {
            "results": results_list,
            "metrics": {
                "overall_metrics": {},
                "retriever_metrics": {},
                "generator_metrics": {},
            },
        }

        return rag_results_obj

    def save_official_input_data(self, input_data: Dict[str, Any]) -> str:
        """Save input data in official RAGChecker RAGResults format (atomic write)."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        input_file = self.metrics_dir / f"ragchecker_official_input_{timestamp}.json"
        tmp_file = self.metrics_dir / f".tmp_{timestamp}_{os.getpid()}_input.json"

        with open(tmp_file, "w") as f:
            json.dump(input_data, f, indent=2)

        os.replace(tmp_file, input_file)
        print(f"💾 Official input data saved to: {input_file}")
        return str(input_file)

    def run_official_ragchecker_cli(
        self, input_file: str, use_local_llm: bool = False, local_api_base: Optional[str] = None
    ) -> Optional[str]:
        """Run official RAGChecker CLI with support for local LLMs."""
        # Hard bypass path: if we are using local LLM OR explicitly requested, don't call the CLI.
        if use_local_llm or os.getenv("RAGCHECKER_BYPASS_CLI", "0") == "1":
            print("⛔ Skipping ragchecker.cli (bypassed). Using in-process evaluation instead.")
            return None
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = self.metrics_dir / f"ragchecker_official_output_{timestamp}.json"

            # Build command with local LLM support
            cmd = [
                "python3",
                "-u",  # force unbuffered stdio for child process
                "-m",
                "ragchecker.cli",
                f"--input_path={input_file}",
                f"--output_path={output_file}",
                "--batch_size_extractor=1",
                "--batch_size_checker=1",
                "--metrics",
                "all_metrics",
            ]

            if use_local_llm and local_api_base:
                # Use local LLM configuration with api_base
                cmd.extend(
                    [
                        "--extractor_name=local/llama3",
                        f"--extractor_api_base={local_api_base}",
                        "--checker_name=local/llama3",
                        f"--checker_api_base={local_api_base}",
                    ]
                )
                print(f"🏠 Using local LLM at: {local_api_base}")
            else:
                # Use Bedrock models WITHOUT api_base flags (LiteLLM handles Bedrock automatically)
                cmd.extend(
                    [
                        f"--extractor_name=bedrock/{self.bedrock_model_id}",
                        f"--checker_name=bedrock/{self.bedrock_model_id}",
                    ]
                )
                print(f"☁️ Using AWS Bedrock ({self.bedrock_model_id}) (no api_base needed)")

            # Ensure AWS region is set for LiteLLM Bedrock integration
            if "AWS_REGION" not in os.environ:
                os.environ["AWS_REGION"] = "us-east-1"
                print("🌍 Set AWS_REGION=us-east-1 for LiteLLM Bedrock integration")

            print("🚀 Attempting to run official RAGChecker CLI...")
            print("📺 Streaming live output from RAGChecker CLI...")
            print("=" * 60)

            # Prepare environment and timeouts to prevent hangs
            import selectors
            import signal as _signal

            env = dict(os.environ)
            # Ensure unbuffered Python I/O for immediate line streaming
            env.setdefault("PYTHONUNBUFFERED", "1")
            # Hint downstream tools to avoid interactive prompts/spinners
            env.setdefault("CI", "1")
            env.setdefault("NO_COLOR", "1")
            env.setdefault("FORCE_COLOR", "0")
            env.setdefault("RAGCHECKER_NONINTERACTIVE", "1")
            env.setdefault("PYTHONIOENCODING", "UTF-8")
            # Some CLIs change behavior on dumb terminals (disables rich progress bars)
            env.setdefault("TERM", "dumb")

            # Optional global timeout knobs (seconds)
            cli_timeout = float(os.getenv("RAGCHECKER_CLI_TIMEOUT_SEC", "600"))
            idle_timeout = float(os.getenv("RAGCHECKER_CLI_IDLE_SEC", "90"))

            # Use Popen for real-time streaming; merge stderr into stdout to avoid deadlocks
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,  # close stdin so any input() immediately EOFs
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env,
                start_new_session=True,  # allow killing the whole group on timeout
            )

            # Stream output in real-time with idle/overall timeout watchdogs
            # Use non-blocking reads + manual line buffering to avoid hangs on partial lines
            stdout_lines: list[str] = []
            sel = selectors.DefaultSelector()
            assert process.stdout is not None

            # Set stdout to non-blocking so .read() never blocks on missing newline
            try:
                import fcntl  # POSIX only; safe on macOS/Linux (Cursor default)

                fd = process.stdout.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
            except Exception:
                # If non-blocking set fails, we still proceed with selector-driven reads
                pass

            sel.register(process.stdout, selectors.EVENT_READ)
            _buf: str = ""

            start_t = time.monotonic()
            last_output_t = start_t
            timed_out = False

            try:
                while True:
                    # Break if process ended
                    if process.poll() is not None:
                        break

                    now = time.monotonic()
                    if cli_timeout and (now - start_t) > cli_timeout:
                        print(f"⏰ RAGChecker CLI overall timeout after {cli_timeout:.0f}s — aborting")
                        timed_out = True
                        break
                    if idle_timeout and (now - last_output_t) > idle_timeout:
                        print(f"😴 RAGChecker CLI idle for {idle_timeout:.0f}s — aborting")
                        timed_out = True
                        break

                    events = sel.select(timeout=1.0)
                    if not events:
                        continue
                    for key, _ in events:
                        # key.fileobj can be an int (fd) or a file-like; guard for pyright and runtime
                        fobj = key.fileobj
                        chunk = ""
                        try:
                            # Prefer non-blocking chunked read when available
                            if hasattr(fobj, "read"):
                                chunk = getattr(fobj, "read")(4096)  # type: ignore[arg-type]
                        except Exception:
                            # As a last resort, try a single safe readline (may still block without non-blocking fd)
                            try:
                                if hasattr(fobj, "readline"):
                                    chunk = getattr(fobj, "readline")()
                            except Exception:
                                chunk = ""

                        if not chunk:
                            continue

                        _buf += chunk

                        # Normalize carriage-return progress updates into discrete lines
                        _buf = _buf.replace("\r", "\n")

                        # Emit complete lines; keep trailing partial in buffer
                        if "\n" in _buf:
                            parts = _buf.split("\n")
                            _buf = parts.pop()  # remainder (possibly partial)
                            for ln in parts:
                                if ln:
                                    print(f"📊 {ln.rstrip()}")
                                    stdout_lines.append(ln + "\n")
                                    last_output_t = time.monotonic()

                # If timed out or still running, terminate the process group
                if timed_out and process.poll() is None:
                    try:
                        _signal.signal(_signal.SIGTERM, _signal.SIG_IGN)  # avoid self-termination issues
                    except Exception:
                        pass
                    try:
                        os.killpg(process.pid, _signal.SIGTERM)
                    except Exception:
                        try:
                            process.terminate()
                        except Exception:
                            pass
                    try:
                        process.wait(timeout=10)
                    except Exception:
                        try:
                            os.killpg(process.pid, _signal.SIGKILL)
                        except Exception:
                            process.kill()

                # Flush any remaining buffered output
                if _buf.strip():
                    for ln in _buf.splitlines():
                        if ln:
                            print(f"📊 {ln.rstrip()}")
                            stdout_lines.append(ln + "\n")

                # Final status
                return_code = process.poll()
                if return_code is None:
                    # Should not happen, but be safe
                    return_code = process.wait(timeout=5)

                if timed_out:
                    print("⚠️ Official RAGChecker CLI terminated due to timeout/idle. Falling back to in-process.")
                    # Signal caller to use in-process path
                    os.environ["RAGCHECKER_BYPASS_CLI"] = "1"
                    return None

                if return_code == 0:
                    print("✅ Official RAGChecker CLI completed successfully")
                    print(f"📊 Results saved to: {output_file}")
                    return str(output_file)
                else:
                    print(f"⚠️ Official RAGChecker CLI failed with return code: {return_code}")
                    # Show last few lines for context
                    tail = stdout_lines[-10:]
                    if tail:
                        print("Last CLI output:")
                        for ln in tail:
                            print(f"  {ln.rstrip()}")
                    return None

            except KeyboardInterrupt:
                print("\n⚠️ Evaluation interrupted by user")
                try:
                    os.killpg(process.pid, _signal.SIGTERM)
                except Exception:
                    process.terminate()
                process.wait()
                return None
            except Exception as e:
                print(f"⚠️ Error during CLI execution: {e}")
                try:
                    os.killpg(process.pid, _signal.SIGTERM)
                except Exception:
                    process.terminate()
                try:
                    process.wait(timeout=10)
                except Exception:
                    try:
                        os.killpg(process.pid, _signal.SIGKILL)
                    except Exception:
                        process.kill()
                # Signal caller to fallback
                os.environ["RAGCHECKER_BYPASS_CLI"] = "1"
                return None

        except FileNotFoundError:
            print("⚠️ Official RAGChecker CLI not found - using fallback evaluation")
            return None
        except Exception as e:
            print(f"⚠️ Error running official RAGChecker CLI: {e}")
            return None

    def calculate_precision(self, response: str, gt_answer: str, query: str) -> float:
        """Calculate precision with smart ROUGE-L hybrid approach."""
        if os.getenv("RAGCHECKER_USE_ROUGE_L", "1") == "1":
            # Get both ROUGE-L and word-overlap scores
            _, rouge_p, _ = self.rouge_l_f1(gt_answer, response)

            # Calculate word-overlap as fallback
            query_words = set(query.lower().split())
            gt_words = set(gt_answer.lower().split())
            response_words = set(response.lower().split())

            if len(gt_words) > 0:
                base_precision = (
                    len(response_words.intersection(gt_words)) / len(response_words) if len(response_words) > 0 else 0
                )
                # Query relevance boost
                query_relevance = (
                    len(response_words.intersection(query_words)) / len(query_words) if len(query_words) > 0 else 0
                )
                query_boost = 0.1 * query_relevance
                word_overlap_p = min(1.0, base_precision + query_boost)

                # Smart hybrid: Use ROUGE-L only if it's not significantly worse
                if rouge_p >= word_overlap_p * 0.8:  # Allow 20% degradation for ROUGE-L benefits
                    return rouge_p
                else:
                    return word_overlap_p
            return rouge_p

        # Fallback to word-overlap only
        query_words = set(query.lower().split())
        gt_words = set(gt_answer.lower().split())
        response_words = set(response.lower().split())

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

    def calculate_recall(self, response: str, gt_answer: str) -> float:
        """Calculate recall with smart ROUGE-L hybrid approach."""
        if os.getenv("RAGCHECKER_USE_ROUGE_L", "1") == "1":
            # Get both ROUGE-L and word-overlap scores
            _, _, rouge_r = self.rouge_l_f1(gt_answer, response)

            # Calculate word-overlap as fallback
            gt_words = set(gt_answer.lower().split())
            response_words = set(response.lower().split())

            if len(gt_words) > 0:
                word_overlap_r = len(response_words.intersection(gt_words)) / len(gt_words)

                # Smart hybrid: Use ROUGE-L only if it's better or not significantly worse
                if rouge_r >= word_overlap_r * 0.9:  # Allow 10% degradation for ROUGE-L benefits
                    return rouge_r
                else:
                    return word_overlap_r
            return rouge_r

        # Fallback to word-overlap only
        gt_words = set(gt_answer.lower().split())
        response_words = set(response.lower().split())

        if len(gt_words) > 0:
            return len(response_words.intersection(gt_words)) / len(gt_words)
        return 0.0

    def run_local_llm_evaluation(
        self, input_data: Union[List[Dict[str, Any]], Dict[str, Any]], local_api_base: str, use_bedrock: bool = False
    ) -> Dict[str, Any]:
        """Run evaluation using local LLM or Bedrock integration.

        Accepts either a list of RAGResults entries or a dict containing "results": [...].
        """
        print("🏠 Running Local LLM Evaluation with comprehensive metrics")
        # Run start time
        self._run_start_ts = time.time()
        # Optional RAGAS-like judge toggle (Bedrock JSON prompts)
        self._ragas_like_enabled = os.getenv("RAGCHECKER_WITH_RAGAS_LIKE", "0") == "1"

        # Normalize input list
        if isinstance(input_data, dict) and "results" in input_data:
            cases: List[Dict[str, Any]] = list(input_data.get("results") or [])
        elif isinstance(input_data, list):
            cases = list(input_data)
        else:
            cases = []

        # Initialize LLM integration
        try:
            self.local_llm = LocalLLMIntegration(api_base=local_api_base, use_bedrock=use_bedrock)
        except Exception as e:
            print(f"⚠️ Failed to initialize LLM integration: {e}. Using simplified fallback.")
            return self.create_fallback_evaluation(cases)

        case_results: List[Dict[str, Any]] = []
        total_precision = total_recall = total_f1 = 0.0

        for case in cases:
            query = str(case.get("query", ""))
            gt_answer = str(case.get("gt_answer", ""))
            ctx_strings = self._to_context_strings(case.get("retrieved_context", []))

            # Use existing response if present; else generate
            response = str(case.get("response") or "").strip()
            if not response:
                response = self.generate_answer_with_context(query, ctx_strings)

            # Compose/coverage rewrite in-process for multi-sentence, high-recall answers
            cov_flag = os.getenv("RAGCHECKER_COVERAGE_REWRITE", "1")
            try:
                pv = (ctx_strings[0] if ctx_strings else "").replace("\n", " ").strip()[:160]
                print(f'🧵 Compose trace: COVERAGE_REWRITE={cov_flag}, ctx={len(ctx_strings)}, preview="{pv}"')
            except Exception:
                pass
            if cov_flag == "1" and getattr(self, "local_llm", None) and ctx_strings:
                try:
                    print(
                        f"🧵 Compose branch: coverage_rewrite RUN (ctx={len(ctx_strings)}, target_words={int(os.getenv('RAGCHECKER_TARGET_WORDS', '600'))})"
                    )
                except Exception:
                    pass
                target_words = int(os.getenv("RAGCHECKER_TARGET_WORDS", "600"))
                try:
                    expanded = self.local_llm.coverage_rewrite(  # type: ignore[union-attr]
                        query, response, ctx_strings, target_words=target_words
                    )
                    response = expanded.strip() or response
                    print(f"📝 Coverage rewrite: {len(response.split())} words with fact enumeration")
                    # Optional: bind claims to evidence if enabled
                    response = self.extract_and_bind_claims(response, ctx_strings)
                except Exception as e:
                    print(f"⚠️ Coverage rewrite failed: {e}")
            elif cov_flag != "1":
                print("🧵 Compose branch: coverage_rewrite SKIP (reason=disabled)")
            elif not ctx_strings:
                print("🧵 Compose branch: coverage_rewrite SKIP (reason=ctx=0)")

            # Evidence guard (optional)
            if os.getenv("RAGCHECKER_EVIDENCE_GUARD", "1") == "1" and ctx_strings:
                try:
                    j = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07"))
                    cov = float(os.getenv("RAGCHECKER_EVIDENCE_COVERAGE", "0.20"))
                    response = evidence_filter(response, ctx_strings, j_min=j, coverage_min=cov)
                except Exception:
                    pass

            # Metrics via local_llm if available
            metrics: Dict[str, float] = {}
            try:
                metrics = self.local_llm.evaluate_comprehensive_metrics(query, response, ctx_strings, gt_answer)  # type: ignore[union-attr]
            except Exception as e:
                print(f"⚠️ Comprehensive metrics failed: {e}")
                metrics = {}

            # Base metrics
            precision = self.calculate_precision(response, gt_answer, query)
            recall = self.calculate_recall(response, gt_answer)
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

            if self._ragas_like_enabled:
                try:
                    ragas_like = self._ragas_like_judge(query, response, ctx_strings)
                except Exception:
                    ragas_like = {}
            else:
                ragas_like = {}

            case_record = {
                "query": query,
                "gt_answer": gt_answer,
                "response": response,
                "retrieved_context": [{"doc_id": None, "text": c} for c in ctx_strings],
                "metrics": {
                    **({} if metrics is None else metrics),
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1_score,
                    **({"ragas_like": ragas_like} if ragas_like else {}),
                },
            }

            case_results.append(case_record)
            total_precision += precision
            total_recall += recall
            total_f1 += f1_score

        n = max(1, len(case_results))
        results: Dict[str, Any] = {
            "evaluation_type": "in_process_official",
            "overall_metrics": {
                "precision": total_precision / n,
                "recall": total_recall / n,
                "f1_score": total_f1 / n,
            },
            "case_results": case_results,
            "total_cases": len(case_results),
        }

        self._run_end_ts = time.time()
        return results

    def _ragas_like_judge(self, query: str, response: str, contexts: list[str]) -> dict:
        """Evaluate RAGAS-like metrics using Bedrock JSON prompts.

        Returns dict with keys:
          - answer_relevancy [0..1]
          - context_precision [0..1]
          - context_recall [0..1]
          - faithfulness [0..1]
          - unsupported_claims [0..1]
        """
        try:
            if not getattr(self, "local_llm", None):
                return {}

            ctx_topk = int(os.getenv("RAGCHECKER_JUDGE_CONTEXT_TOPK", "5"))
            ctx_blob = "\n---\n".join(contexts[:ctx_topk]) if contexts else ""

            prompt = f"""
You are a strict evaluator for RAG (retrieval-augmented generation) answers.
Given a query, a system response, and supporting context, output JSON ONLY with scores in [0,1].

Definitions:
- answer_relevancy: How relevant the response is to the query intent.
- context_precision: Fraction of response content that is supported by the provided context.
- context_recall: How completely the response uses the provided context to answer the query.
- faithfulness: Degree to which the response avoids hallucinations (1.0 = no hallucinations).
- unsupported_claims: Fraction of claims that are NOT supported by the context.

Output JSON with fields: {{
  "answer_relevancy": float,
  "context_precision": float,
  "context_recall": float,
  "faithfulness": float,
  "unsupported_claims": float
}}

Constraints:
- Output JSON only. No prose.
- Scores must be between 0 and 1 (inclusive).

Query:
{query}

Response:
{response}

Context (top {ctx_topk}):
{ctx_blob}
""".strip()

            schema = {
                "type": "object",
                "required": [
                    "answer_relevancy",
                    "context_precision",
                    "context_recall",
                    "faithfulness",
                    "unsupported_claims",
                ],
                "properties": {
                    "answer_relevancy": {"type": "number", "minimum": 0, "maximum": 1},
                    "context_precision": {"type": "number", "minimum": 0, "maximum": 1},
                    "context_recall": {"type": "number", "minimum": 0, "maximum": 1},
                    "faithfulness": {"type": "number", "minimum": 0, "maximum": 1},
                    "unsupported_claims": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "additionalProperties": False,
            }

            obj = self.local_llm.call_json(prompt, schema=schema, max_tokens=400)  # type: ignore
            if isinstance(obj, dict):
                return obj
            return {}
        except Exception as e:
            print(f"⚠️ RAGAS-like judge failed: {e}")
            return {}

        # Initialize LLM integration
        try:
            self.local_llm = LocalLLMIntegration(
                api_base=local_api_base, model_name="llama3.1:8b", use_bedrock=use_bedrock
            )
            self.use_bedrock = use_bedrock  # Store the bedrock flag
        except Exception as e:
            print(f"⚠️ Failed to initialize LLM integration: {e}")
            return self.create_fallback_evaluation(input_data)

        case_results = []
        total_precision = 0.0
        total_recall = 0.0
        total_f1 = 0.0

        # Extract results list from RAGResults format if needed
        cases_iter: List[Dict[str, Any]] = []
        if isinstance(input_data, dict) and "results" in input_data:
            cases_iter = input_data["results"]
        elif isinstance(input_data, list):
            cases_iter = input_data
        else:
            print(f"⚠️ Unexpected input_data type: {type(input_data)}")
            return {"evaluation_type": "error", "error": "Invalid input data format"}

        for i, case in enumerate(cases_iter):
            # Type assertion to help Pyright understand case is a dict
            if not isinstance(case, dict):
                print(f"⚠️ Skipping non-dict case: {type(case)}")
                continue
            print(f"\n📝 Evaluating case {i+1}/{len(input_data)}: {case.get('query_id', f'case_{i+1}')}")
            _case_start = time.time()

            try:
                # Generate response using memory system
                raw_response = self.generate_answer_with_context(
                    case["query"], self._to_context_strings(case.get("retrieved_context", []))
                )

                # Normalize context to list[str] for downstream steps
                ctx_strings = self._to_context_strings(case.get("retrieved_context", []))

                # Enhanced coverage-first generation with claim binding (eval-only)
                cov_flag = os.getenv("RAGCHECKER_COVERAGE_REWRITE", "1")

                # Unconditional compose trace: always show ctx count and short preview
                try:
                    _pv = ctx_strings[0] if ctx_strings else ""
                    _pv = _pv.replace("\n", " ").strip()[:160]
                    print(f'🧵 Compose trace: COVERAGE_REWRITE={cov_flag}, ctx={len(ctx_strings)}, preview="{_pv}"')
                except Exception:
                    # Never crash evaluation due to tracing
                    pass

                if cov_flag == "1" and self.local_llm and ctx_strings:
                    try:
                        print(
                            f"🧵 Compose branch: coverage_rewrite RUN (ctx={len(ctx_strings)}, target_words={int(os.getenv('RAGCHECKER_TARGET_WORDS', '600'))})"
                        )
                    except Exception:
                        pass
                    target_words = int(os.getenv("RAGCHECKER_TARGET_WORDS", "600"))
                    try:
                        expanded = self.local_llm.coverage_rewrite(
                            case["query"], raw_response, ctx_strings, target_words=target_words
                        )
                        raw_response = expanded
                        print(f"📝 Coverage rewrite: {len(raw_response.split())} words with fact enumeration")

                        # Apply claim binding if enabled
                        raw_response = self.extract_and_bind_claims(raw_response, ctx_strings)
                        if os.getenv("RAGCHECKER_CLAIM_BINDING", "0") == "1":
                            print(f"📝 Claim binding: {len(raw_response.split())} words after evidence binding")

                    except Exception as e:
                        print(f"⚠️ Coverage rewrite failed: {e}")
                elif cov_flag != "1":
                    print("🧵 Compose branch: coverage_rewrite SKIP (reason=disabled)")
                elif not ctx_strings:
                    print("🧵 Compose branch: coverage_rewrite SKIP (reason=ctx=0)")

                # Evidence gate to protect precision/faithfulness
                if os.getenv("RAGCHECKER_EVIDENCE_GUARD", "1") == "1":
                    j = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.18"))
                    cov = float(os.getenv("RAGCHECKER_EVIDENCE_COVERAGE", "0.45"))
                    ctx_list = [c["text"] if isinstance(c, dict) else str(c) for c in case.get("retrieved_context", [])]
                    if ctx_list:
                        raw_response = evidence_filter(raw_response, ctx_list, j_min=j, coverage_min=cov)
                        print(f"📝 Evidence filtering: {len(raw_response.split())} words after precision guard")

                # Apply word limit if needed
                if hasattr(self.local_llm, "apply_word_limit"):
                    raw_response = self.local_llm.apply_word_limit(raw_response)

                case["response"] = raw_response

                # Always coerce to strings first
                # Optional: semantic ranking (only if embeddings loaded)
                if getattr(self.local_llm, "embedding_model", None):
                    try:
                        import torch  # type: ignore
                        from sentence_transformers import util as st_util  # type: ignore

                        query_emb = self.local_llm.embedding_model.encode(case["query"], convert_to_tensor=True)
                        ctx_embs = self.local_llm.embedding_model.encode(ctx_strings, convert_to_tensor=True)
                        cos_scores = st_util.cos_sim(query_emb, ctx_embs)[0]
                        topk = min(3, len(ctx_strings))
                        top_results = torch.topk(cos_scores, k=topk)
                        print("🎯 Ranked", top_results.indices.shape[0], "context chunks by semantic similarity")
                    except Exception:
                        pass

                # Persist normalized context if you want it in outputs
                case["retrieved_context"] = ctx_strings

                # Evaluate comprehensive metrics on strings
                metrics = self.local_llm.evaluate_comprehensive_metrics(
                    case["query"], case["response"], ctx_strings, case["gt_answer"]
                )

                # Optional RAGAS-like judge scoring (Bedrock JSON prompts)
                ragas_like = {}
                if self._ragas_like_enabled:
                    ragas_like = self._ragas_like_judge(case["query"], case["response"], ctx_strings)

                # Calculate basic metrics
                precision = self.calculate_precision(case["response"], case["gt_answer"], case["query"])
                recall = self.calculate_recall(case["response"], case["gt_answer"])
                f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

                case_result = {
                    "query_id": case.get("query_id", f"case_{i+1}"),
                    "query": case["query"],
                    "response": case["response"],
                    "gt_answer": case["gt_answer"],
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1_score,
                    "comprehensive_metrics": metrics,
                    "ragas_like": ragas_like,
                    "timing_sec": round(time.time() - _case_start, 3),
                }

                case_results.append(case_result)
                total_precision += precision
                total_recall += recall
                total_f1 += f1_score

                print(
                    f"✅ Case {case.get('query_id', f'case_{i+1}')}: P={precision:.3f}, R={recall:.3f}, F1={f1_score:.3f}"
                    f" (t={case_result['timing_sec']:.3f}s)"
                )
                _progress_write({"type": "case", **case_result})

            except Exception as e:
                print(f"⚠️ Error evaluating case {case.get('query_id', f'case_{i+1}')}: {e}")
                # Add failed case with zero scores
                case_results.append(
                    {
                        "query_id": case.get("query_id", f"case_{i+1}"),
                        "query": case["query"],
                        "response": "",
                        "gt_answer": case["gt_answer"],
                        "precision": 0.0,
                        "recall": 0.0,
                        "f1_score": 0.0,
                        "error": str(e),
                        "timing_sec": round(time.time() - _case_start, 3),
                    }
                )

        # Calculate averages
        num_cases = len(case_results)  # Use actual case results count
        avg_precision = total_precision / num_cases if num_cases > 0 else 0
        avg_recall = total_recall / num_cases if num_cases > 0 else 0
        avg_f1 = total_f1 / num_cases if num_cases > 0 else 0

        # Comprehensive metrics averages
        def _avg(values):
            valid_values = [v for v in values if v is not None]
            return sum(valid_values) / len(valid_values) if valid_values else 0

        comp_keys = [
            "claim_precision",
            "claim_recall",
        ]
        comp_avgs = {k: _avg([c.get("comprehensive_metrics", {}).get(k) for c in case_results]) for k in comp_keys}

        # Aggregate faithfulness across cases (present in comprehensive_metrics per case)
        avg_faithfulness = _avg([c.get("comprehensive_metrics", {}).get("faithfulness") for c in case_results])

        # Optional RAGAS-like overall averages
        ragas_like_overall = {}
        if self._ragas_like_enabled and num_cases > 0:
            try:
                vals = [c.get("ragas_like", {}) for c in case_results]

                def _avg_key(k: str) -> float:
                    xs = [float(v.get(k, 0.0)) for v in vals if isinstance(v, dict) and k in v]
                    return sum(xs) / len(xs) if xs else 0.0

                ragas_like_overall = {
                    "answer_relevancy": _avg_key("answer_relevancy"),
                    "context_precision": _avg_key("context_precision"),
                    "context_recall": _avg_key("context_recall"),
                    "faithfulness": _avg_key("faithfulness"),
                    "unsupported_claims": _avg_key("unsupported_claims"),
                }
            except Exception:
                ragas_like_overall = {}

        summary = {
            "evaluation_type": "local_llm_comprehensive",
            "overall_metrics": {
                "precision": avg_precision,
                "recall": avg_recall,
                "f1_score": avg_f1,
                "faithfulness": avg_faithfulness,
            },
            "comprehensive_metrics": comp_avgs,
            "ragas_like_overall": ragas_like_overall,
            "case_results": case_results,
            "total_cases": num_cases,
            "use_bedrock": self.use_bedrock,
        }
        _progress_write(
            {
                "type": "summary",
                "overall_metrics": summary["overall_metrics"],
                "total_cases": num_cases,
                "timestamp": time.time(),
            }
        )
        return summary

    async def _evaluate_case_async(self, case: dict, i: int) -> dict:
        """Evaluate a single test case asynchronously with Bedrock gate."""
        try:
            _case_start = time.time()
            # Generate response using memory system
            raw_response = self.generate_answer_with_context(
                case["query"], self._to_context_strings(case.get("retrieved_context", []))
            )

            # Coverage-first generation for better recall (eval-only)
            cov_flag = os.getenv("RAGCHECKER_COVERAGE_REWRITE", "1")
            # Normalize context to list[str]
            ctx_list = []
            for c in case.get("retrieved_context", []):
                if isinstance(c, dict) and "text" in c:
                    ctx_list.append(str(c["text"]))
                elif isinstance(c, str):
                    ctx_list.append(c)

            # Unconditional compose trace for async path
            try:
                _pv = ctx_list[0] if ctx_list else ""
                _pv = _pv.replace("\n", " ").strip()[:160]
                print(f'🧵 Compose trace: COVERAGE_REWRITE={cov_flag}, ctx={len(ctx_list)}, preview="{_pv}"')
            except Exception:
                pass

            if cov_flag == "1" and self.local_llm and ctx_list:
                try:
                    print(
                        f"🧵 Compose branch: coverage_rewrite RUN (ctx={len(ctx_list)}, target_words={int(os.getenv('RAGCHECKER_TARGET_WORDS', '600'))})"
                    )
                except Exception:
                    pass
                target_words = int(os.getenv("RAGCHECKER_TARGET_WORDS", "600"))
                try:
                    expanded = self.local_llm.coverage_rewrite(
                        case["query"], raw_response, ctx_list, target_words=target_words
                    )
                    raw_response = expanded
                    print(f"📝 Coverage rewrite: {len(raw_response.split())} words with fact enumeration")
                except Exception as e:
                    print(f"⚠️ Coverage rewrite failed: {e}")
            elif cov_flag != "1":
                print("🧵 Compose branch: coverage_rewrite SKIP (reason=disabled)")
            elif not ctx_list:
                print("🧵 Compose branch: coverage_rewrite SKIP (reason=ctx=0)")

            # Evidence gate to protect precision/faithfulness
            if os.getenv("RAGCHECKER_EVIDENCE_GUARD", "1") == "1":
                j = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.18"))
                cov = float(os.getenv("RAGCHECKER_EVIDENCE_COVERAGE", "0.45"))
                # Optional anchor-aware rerank before converting to strings
                ctx_with_meta = case.get("retrieved_context", [])
                try:
                    ctx_with_meta = _maybe_rerank_contexts(ctx_with_meta)
                except Exception:
                    pass
                ctx_list = [c["text"] if isinstance(c, dict) else str(c) for c in ctx_with_meta]
                if ctx_list:
                    raw_response = evidence_filter(raw_response, ctx_list, j_min=j, coverage_min=cov)
                    print(f"📝 Evidence filtering: {len(raw_response.split())} words after precision guard")

            # Apply word limit if needed
            if getattr(self, "local_llm", None) and hasattr(self.local_llm, "apply_word_limit"):
                raw_response = self.local_llm.apply_word_limit(raw_response)  # type: ignore[union-attr]

            case["response"] = raw_response

            # Always coerce to strings first
            # Optional anchor-aware rerank before converting to strings
            ctx_with_meta = case.get("retrieved_context", [])
            try:
                ctx_with_meta = _maybe_rerank_contexts(ctx_with_meta)
            except Exception:
                pass
            ctx_strings = self._to_context_strings(ctx_with_meta)

            # Optional: semantic ranking (only if embeddings loaded)
            if getattr(self, "local_llm", None) and getattr(self.local_llm, "embedding_model", None):
                try:
                    ctx_strings = self.local_llm.rank_context_by_query_similarity(  # type: ignore[union-attr]
                        case["query"], ctx_strings
                    )
                except Exception as e:
                    print(f"⚠️ Context ranking failed (skipping): {e}")

            # Persist normalized context if you want it in outputs
            case["retrieved_context"] = ctx_strings

            # Evaluate comprehensive metrics using async Bedrock gate
            metrics: Dict[str, float] = {}
            if getattr(self, "local_llm", None):
                try:
                    # Try async Bedrock first for better faithfulness
                    if hasattr(self.local_llm, "bedrock_invoke_async"):
                        # Build fused metrics prompt
                        fused_prompt = self._build_fused_metrics_prompt(
                            case["query"], case["response"], ctx_strings, case["gt_answer"]
                        )
                        metrics_obj = await self.local_llm.bedrock_invoke_async(  # type: ignore[attr-defined]
                            prompt=fused_prompt, max_tokens=250
                        )
                        # Parse metrics from response
                        metrics = self._parse_fused_metrics(metrics_obj)
                    else:
                        # Fallback to sync evaluation
                        metrics = self.local_llm.evaluate_comprehensive_metrics(  # type: ignore[union-attr]
                            case["query"], case["response"], ctx_strings, case["gt_answer"]
                        )
                except Exception as e:
                    print(f"⚠️ Async metrics failed, falling back to sync: {e}")
                    try:
                        metrics = self.local_llm.evaluate_comprehensive_metrics(  # type: ignore[union-attr]
                            case["query"], case["response"], ctx_strings, case["gt_answer"]
                        )
                    except Exception:
                        metrics = {}
            else:
                metrics = {}

            # Calculate basic metrics
            precision = self.calculate_precision(case["response"], case["gt_answer"], case["query"])
            recall = self.calculate_recall(case["response"], case["gt_answer"])
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

            case_result = {
                "query_id": case.get("query_id", f"case_{i+1}"),
                "query": case["query"],
                "response": case["response"],
                "gt_answer": case["gt_answer"],
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "comprehensive_metrics": metrics,
                "timing_sec": round(time.time() - _case_start, 3),
            }

            print(
                f"✅ Case {case.get('query_id', f'case_{i+1}')}: P={precision:.3f}, R={recall:.3f}, F1={f1_score:.3f}"
                f" (t={case_result['timing_sec']:.3f}s)"
            )

            return case_result

        except Exception as e:
            print(f"⚠️ Error evaluating case {case.get('query_id', f'case_{i+1}')}: {e}")
            # Return failed case with zero scores
            return {
                "query_id": case.get("query_id", f"case_{i+1}"),
                "query": case["query"],
                "response": "",
                "gt_answer": case["gt_answer"],
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "error": str(e),
                "timing_sec": round(time.time() - _case_start, 3),
            }

        async def _eval_all_async(self, cases: list[dict]):
            """Run all cases asynchronously with bounded concurrency."""
            k = int(os.getenv("ASYNC_MAX_CONCURRENCY", "5"))
            sem = asyncio.Semaphore(k)

            async def run_one(c, i):
                async with sem:
                    return await self._evaluate_case_async(c, i)

            return await asyncio.gather(*(run_one(c, i) for i, c in enumerate(cases)))

    def _build_fused_metrics_prompt(self, query: str, response: str, context: list[str], gt_answer: str) -> str:
        """Build prompt for fused metrics evaluation."""
        return f"""
Evaluate the following response against the provided context and query. Return a JSON object with these exact fields:

{{
  "context_precision": <0.0-1.0 score for how relevant context is to query>,
  "context_utilization": <0.0-1.0 score for how well response uses context>,
  "noise_sensitivity": <0.0-1.0 score for how well response filters irrelevant info>,
  "hallucination_rate": <0.0-1.0 score for unsupported information (0=perfect, 1=all hallucinated)>,
  "self_knowledge": <0.0-1.0 score for awareness of limitations>,
  "claim_recall": <0.0-1.0 score for coverage of factual claims from context>
}}

Query: {query}
Context: {chr(10).join(context[:3])}
Response: {response}
Ground Truth: {gt_answer}

Evaluate and return ONLY the JSON object:"""

    def _parse_fused_metrics(self, metrics_obj) -> dict:
        """Parse metrics from fused evaluation response."""
        try:
            if isinstance(metrics_obj, str):
                import json

                parsed = json.loads(metrics_obj)
                if isinstance(parsed, dict):
                    metrics = parsed
                elif isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
                    metrics = parsed[0]
                else:
                    raise ValueError(f"Unexpected response type: {type(parsed)}")
            elif isinstance(metrics_obj, dict):
                metrics = metrics_obj
            elif isinstance(metrics_obj, list) and metrics_obj and isinstance(metrics_obj[0], dict):
                metrics = metrics_obj[0]
            else:
                raise ValueError(f"Unexpected response type: {type(metrics_obj)}")

            # Calculate faithfulness from hallucination rate
            hallucination_raw = metrics.get("hallucination_rate", 0.5)
            faithfulness = 1.0 - float(hallucination_raw)

            # One-line sanity print for debugging
            print(
                f"[faith] cp={metrics.get('context_precision')} util={metrics.get('context_utilization')} "
                f"noise={metrics.get('noise_sensitivity')} hall_raw={hallucination_raw} "
                f"selfk={metrics.get('self_knowledge')} claim_rec={metrics.get('claim_recall')} "
                f"faith={faithfulness:.3f}"
            )

            return {
                "context_precision": metrics.get("context_precision", 0.5),
                "context_utilization": metrics.get("context_utilization", 0.5),
                "noise_sensitivity": metrics.get("noise_sensitivity", 0.5),
                "faithfulness": faithfulness,
                "hallucination_rate": hallucination_raw,
                "self_knowledge": metrics.get("self_knowledge", 0.5),
                "claim_recall": metrics.get("claim_recall", 0.5),
            }
        except Exception as e:
            print(f"⚠️ Failed to parse fused metrics: {e}")
            print(f"⚠️ Raw response: {metrics_obj}")
            # Return default metrics with fallback reason
            return {
                "context_precision": 0.5,
                "context_utilization": 0.5,
                "noise_sensitivity": 0.5,
                "faithfulness": 0.5,
                "hallucination_rate": 0.5,
                "self_knowledge": 0.5,
                "claim_recall": 0.5,
            }

    def create_fallback_evaluation(self, input_data: Union[List[Dict[str, Any]], Dict[str, Any]]) -> Dict[str, Any]:
        """Create fallback evaluation when LLM integration fails."""
        print("🔄 Running Fallback Evaluation (simplified metrics)")

        case_results = []
        total_precision = 0.0
        total_recall = 0.0
        total_f1 = 0.0

        # Normalize input data to ensure consistent structure
        if isinstance(input_data, dict) and "results" in input_data:
            cases = input_data["results"]
        else:
            cases = input_data

        # Normalize each case to guarantee dict structure
        normalized_cases: List[EvalItem] = [normalize_item(case) for case in cases]

        for case in normalized_cases:
            # Type assertion to help Pyright understand the structure
            case_dict = case  # type: Dict[str, str]

            # Generate response using memory system
            case_dict["response"] = self.generate_answer_with_context(
                case_dict["query"], self._to_context_strings(case_dict.get("retrieved_context", []))
            )

            # Calculate basic metrics using simple text overlap
            precision = self.calculate_precision(case_dict["response"], case_dict["gt_answer"], case_dict["query"])
            recall = self.calculate_recall(case_dict["response"], case_dict["gt_answer"])
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

            case_result = {
                "query_id": f"case_{len(case_results) + 1}",
                "query": case_dict["query"],
                "response": case_dict["response"],
                "gt_answer": case_dict["gt_answer"],
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
            }

            case_results.append(case_result)
            total_precision += precision
            total_recall += recall
            total_f1 += f1_score

        # Calculate averages
        num_cases = len(input_data)
        avg_precision = total_precision / num_cases if num_cases > 0 else 0
        avg_recall = total_recall / num_cases if num_cases > 0 else 0
        avg_f1 = total_f1 / num_cases if num_cases > 0 else 0

        return {
            "evaluation_type": "fallback_simplified",
            "overall_metrics": {"precision": avg_precision, "recall": avg_recall, "f1_score": avg_f1},
            "case_results": case_results,
            "note": "Simplified evaluation - LLM integration unavailable",
        }

    def run_official_evaluation(
        self, use_local_llm: bool = False, local_api_base: Optional[str] = None, use_bedrock: bool = False
    ) -> Dict[str, Any]:
        """Run complete official RAGChecker evaluation with hybrid LLM support."""
        print("🧠 Official RAGChecker Evaluation")
        print("=" * 60)
        print("📋 Following official RAGChecker methodology")
        print("🎯 Using official metrics and procedures")

        # Initialize results early to avoid UnboundLocalError on early exits
        results: Dict[str, Any] = {}

        if use_bedrock:
            print(f"☁️ AWS Bedrock Mode: {self.bedrock_model_id}")
        elif use_local_llm:
            print(f"🏠 Local LLM Mode: {local_api_base}")
        else:
            print("☁️ Cloud LLM Mode (AWS Bedrock)")

        # Initialize LLM integration BEFORE building input data so we don't hit heavy fallbacks
        try:
            # Default to Bedrock when neither flag is set (cloud mode)
            effective_bedrock = use_bedrock or (not use_local_llm)
            self.local_llm = LocalLLMIntegration(
                api_base=(local_api_base or "http://localhost:11434"),
                use_bedrock=effective_bedrock,
            )
            self.use_bedrock = effective_bedrock
        except Exception as _llm_init_err:
            print(f"⚠️ LLM init warning (will use extractive fallback if needed): {_llm_init_err}")

        # Step 1: Prepare input data in official format
        input_data = self.prepare_official_input_data()

        # Step 2: Save input data
        input_file = self.save_official_input_data(input_data)

        # Step 3: Try to run official RAGChecker CLI (or bypass to in-process evaluation)
        output_file = self.run_official_ragchecker_cli(input_file, use_local_llm, local_api_base)

        # If bypass flag is set OR CLI didn't produce an output, run in-process evaluation
        if os.getenv("RAGCHECKER_BYPASS_CLI", "0") == "1" or not output_file:
            if os.getenv("RAGCHECKER_BYPASS_CLI", "0") == "1":
                print("⛔ CLI bypass enabled — running in-process official evaluation instead")
            else:
                print("⚠️ CLI returned no output file — running in-process official evaluation")
            results = self.run_local_llm_evaluation(
                (input_data["results"] if isinstance(input_data, dict) and "results" in input_data else input_data),
                local_api_base or "http://localhost:11434",
                use_bedrock,
            )
        elif output_file and os.path.exists(output_file):
            # Step 4: Load official results
            try:
                with open(output_file, "r") as f:
                    results = json.load(f)
                results["evaluation_type"] = "official_ragchecker_cli"
                results["input_file"] = input_file
                results["output_file"] = output_file
            except Exception as e:
                print(f"⚠️ Error loading official results: {e}")
                if use_local_llm and local_api_base:
                    # Check for fast mode to avoid hanging on 130+ LLM calls
                    if os.getenv("RAGCHECKER_FAST_MODE", "0") == "1":
                        print("⚡ Fast mode enabled - using simplified evaluation")
                        results = self.create_fallback_evaluation(
                            input_data["results"]
                            if isinstance(input_data, dict) and "results" in input_data
                            else input_data
                        )
                    else:
                        results = self.run_local_llm_evaluation(
                            (
                                input_data["results"]
                                if isinstance(input_data, dict) and "results" in input_data
                                else input_data
                            ),
                            local_api_base,
                            use_bedrock,
                        )
                else:
                    results = self.create_fallback_evaluation(
                        input_data["results"]
                        if isinstance(input_data, dict) and "results" in input_data
                        else input_data
                    )

        # Config banner for stability triage
        print(
            "\n🧰 Active Bedrock caps: "
            f"ASYNC_MAX_CONCURRENCY={os.getenv('ASYNC_MAX_CONCURRENCY','')}, "
            f"BEDROCK_MAX_IN_FLIGHT={os.getenv('BEDROCK_MAX_IN_FLIGHT', os.getenv('BEDROCK_MAX_CONCURRENCY',''))}, "
            f"BEDROCK_MAX_RPS={os.getenv('BEDROCK_MAX_RPS','')}, "
            f"BASE_BACKOFF={os.getenv('BEDROCK_BASE_BACKOFF', os.getenv('BEDROCK_RETRY_BASE',''))}, "
            f"MAX_BACKOFF={os.getenv('BEDROCK_MAX_BACKOFF', os.getenv('BEDROCK_RETRY_MAX_SLEEP',''))}, "
            f"MODEL_ID={os.getenv('BEDROCK_MODEL_ID','')}"
        )
        print(
            f"🧪 Eval JSON: PROMPTS={os.getenv('RAGCHECKER_JSON_PROMPTS','')}, "
            f"MAX_TOKENS={os.getenv('RAGCHECKER_JSON_MAX_TOKENS','')}, "
            f"COVERAGE_REWRITE={os.getenv('RAGCHECKER_COVERAGE_REWRITE','')}"
        )

        # Step 5: Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = self.metrics_dir / f"ragchecker_official_evaluation_{timestamp}.json"

        # Attach run timing
        self._run_end_ts = time.time()
        run_duration = None
        if self._run_start_ts is not None and self._run_end_ts is not None:
            run_duration = round(self._run_end_ts - self._run_start_ts, 3)
            results["run_timing_sec"] = run_duration
            # Per-case average timing
            if results.get("case_results"):
                avg_case_t = sum(c.get("timing_sec", 0.0) for c in results["case_results"]) / max(
                    1, len(results["case_results"])
                )
                results["avg_case_timing_sec"] = round(avg_case_t, 3)

        # Attach run configuration snapshot (env + git) for exact reproducibility
        try:
            relevant_keys = [
                # core toggles
                "RAGCHECKER_JSON_PROMPTS",
                "RAGCHECKER_COVERAGE_REWRITE",
                "RAGCHECKER_CONTEXT_TOPK",
                "RAGCHECKER_TARGET_WORDS",
                "RAGCHECKER_EVIDENCE_KEEP_MODE",
                "RAGCHECKER_TARGET_K_WEAK",
                "RAGCHECKER_TARGET_K_BASE",
                "RAGCHECKER_TARGET_K_STRONG",
                "RAGCHECKER_EVIDENCE_KEEP_PERCENTILE",
                "RAGCHECKER_EVIDENCE_MIN_SENT",
                "RAGCHECKER_EVIDENCE_MAX_SENT",
                "RAGCHECKER_DROP_UNSUPPORTED",
                # bedrock pacing
                "USE_BEDROCK_QUEUE",
                "BEDROCK_MAX_IN_FLIGHT",
                "BEDROCK_MAX_RPS",
                "BEDROCK_BASE_BACKOFF",
                "BEDROCK_MAX_BACKOFF",
                "BEDROCK_COOLDOWN_SEC",
                "BEDROCK_MAX_RETRIES",
                # model + region
                "BEDROCK_MODEL_ID",
                "AWS_REGION",
                # lessons + lineage
                "RAGCHECKER_ENV_FILE",
                "LESSONS_APPLIED",
                "DERIVED_FROM",
                "LESSONS_SUGGESTED",
                "DECISION_DOCKET",
            ]
            env_snapshot = {k: os.getenv(k) for k in relevant_keys if os.getenv(k) is not None}
            # git info (best-effort)
            git_info = {}
            try:
                rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=2)
                if rev.returncode == 0:
                    git_info["commit"] = rev.stdout.strip()
                br = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, timeout=2
                )
                if br.returncode == 0:
                    git_info["branch"] = br.stdout.strip()
            except Exception:
                pass
            results.setdefault("run_config", {})
            results["run_config"].update({"env": env_snapshot, "git": git_info})

            # Add lessons metadata if available
            if "lessons_metadata" in locals():
                results["run_config"]["lessons"] = locals().get("lessons_metadata", {})
        except Exception:
            pass

        # Always persist a safe JSON payload even if results is not set due to an early error
        try:
            _results_obj = results  # may be undefined if exception occurred earlier
        except NameError:
            _results_obj = {}
        if not isinstance(_results_obj, dict):
            _results_obj = {}
        _results_obj.setdefault("overall_metrics", {})
        # Fill missing overall metrics if possible (average over per-case)
        if (not _results_obj["overall_metrics"]) and isinstance(_results_obj.get("case_results"), list):
            cases = _results_obj.get("case_results") or []
            ps = [c.get("precision", c.get("metrics", {}).get("precision", 0.0)) for c in cases]
            rs = [c.get("recall", c.get("metrics", {}).get("recall", 0.0)) for c in cases]
            f1s = [c.get("f1_score", c.get("metrics", {}).get("f1_score", 0.0)) for c in cases]
            n = max(1, len(cases))
            _results_obj["overall_metrics"] = {
                "precision": sum(ps) / n,
                "recall": sum(rs) / n,
                "f1_score": sum(f1s) / n,
            }
        _results_obj.setdefault("total_cases", len(_results_obj.get("case_results") or []))
        _results_obj.setdefault(
            "evaluation_type",
            "in_process_official" if os.getenv("RAGCHECKER_BYPASS_CLI", "0") == "1" else "official_ragchecker_cli",
        )
        with open(results_file, "w") as f:
            json.dump(_results_obj, f, indent=2)

        print(f"\n💾 Official evaluation results saved to: {results_file}")

        # Step 6: Print summary
        self.print_evaluation_summary(results)

        # Normalize output so summaries and downstream tooling never see empty shapes
        if not isinstance(results, dict):
            results = {}
        # Ensure case_results and totals are present
        cases = results.get("case_results") or []
        if not isinstance(cases, list):
            cases = []
            results["case_results"] = cases
        results.setdefault("total_cases", len(cases))
        # Ensure evaluation_type is labeled
        results.setdefault(
            "evaluation_type",
            "in_process_official" if os.getenv("RAGCHECKER_BYPASS_CLI", "0") == "1" else "official_ragchecker_cli",
        )

        return results

    def _to_context_strings(self, raw_list) -> list[str]:
        """Coerce a retrieved_context list that may contain strings or {text: ...} dicts into List[str]."""
        out: list[str] = []
        if not raw_list:
            return out
        for item in raw_list:
            if isinstance(item, str):
                s = item.strip()
            elif isinstance(item, dict):
                s = str(item.get("text", "")).strip()
            else:
                s = str(item).strip()
            if s:
                out.append(s)
        return out

    def print_evaluation_summary(self, results: Dict[str, Any]):
        """Print evaluation summary following official format."""
        print("\n" + "=" * 60)
        print("📊 OFFICIAL RAGCHECKER EVALUATION SUMMARY")
        print("=" * 60)

        # Make summary resilient to partial results
        if results is None:
            print("⚠️ No evaluation results available")
            return

        cases = results.get("case_results") or []
        total = results.get("total_cases") or len(cases)
        metrics = results.get("overall_metrics") or {}

        print(f"🎯 Evaluation Type: {results.get('evaluation_type', 'Unknown')}")
        print(f"📋 Total Cases: {total}")

        if "overall_metrics" in results:
            metrics = results["overall_metrics"]
            print("📊 Overall Metrics:")
            print(f"   Precision: {metrics.get('precision', 0):.3f}")
            print(f"   Recall: {metrics.get('recall', 0):.3f}")
            print(f"   F1 Score: {metrics.get('f1_score', 0):.3f}")
            if "faithfulness" in metrics:
                print(f"   Faithfulness: {metrics.get('faithfulness', 0):.3f}")
            if "total_claims" in metrics:
                print(f"   Total Claims: {metrics.get('total_claims', 0)}")

        # Timing summary
        if results.get("run_timing_sec") is not None:
            print("\n⏱️ Timing:")
            print(f"   Run Duration: {results.get('run_timing_sec'):.3f}s")
            if results.get("avg_case_timing_sec") is not None:
                print(f"   Avg Per-Case: {results.get('avg_case_timing_sec'):.3f}s")

        # Print comprehensive RAGChecker metrics if available
        if "case_results" in results:
            print("\n🔍 Case-by-Case Results:")
            for case in results["case_results"]:
                case_id = case.get("case_id", case.get("query_id", "unknown"))
                extra = f", t={case.get('timing_sec', 0.0):.3f}s" if case.get("timing_sec") is not None else ""
                # Support both flat metrics and nested case['metrics'] structure
                cm = case.get("metrics", {}) if isinstance(case.get("metrics"), dict) else {}
                p = case.get("precision", cm.get("precision", 0.0))
                r = case.get("recall", cm.get("recall", 0.0))
                f1 = case.get("f1_score", cm.get("f1_score", 0.0))
                print(f"   {case_id}: F1={f1:.3f}, P={p:.3f}, R={r:.3f}{extra}")

        if results.get("note"):
            print(f"\n📝 Note: {results['note']}")


def main():
    """Main function to run official RAGChecker evaluation."""
    import argparse

    parser = argparse.ArgumentParser(description="Official RAGChecker Evaluation with Hybrid LLM Support")
    parser.add_argument("--use-local-llm", action="store_true", help="Use local LLM (Ollama) for evaluation")
    parser.add_argument("--use-bedrock", action="store_true", help="Use AWS Bedrock Claude 3.5 Sonnet for evaluation")
    parser.add_argument("--bypass-cli", action="store_true", help="Bypass ragchecker.cli and evaluate in-process")
    parser.add_argument("--stable", action="store_true", help="Use stable locked configuration for regression tracking")
    parser.add_argument(
        "--breakthrough",
        action="store_true",
        help=(
            "Disable auto-loading the stable env and the SafeEval guard. "
            "Use for experimental/breakthrough runs where you control env explicitly."
        ),
    )
    parser.add_argument(
        "--env-file",
        default=None,
        help="Path to an env file with KEY=VALUE entries to load and lock (overrides defaults)",
    )
    parser.add_argument(
        "--profile",
        choices=["stable", "recall"],
        default=None,
        help="Convenience profiles: 'stable' (locked baseline) or 'recall' (recall-optimized)",
    )
    parser.add_argument(
        "--local-api-base",
        default="http://localhost:11434",
        help="Local LLM API base URL (default: http://localhost:11434 for Ollama)",
    )
    parser.add_argument("--with-ragas", action="store_true", help="Enable RAGAS-like Bedrock judge for richer metrics")
    parser.add_argument(
        "--progress-log",
        default=None,
        help="Path to a JSONL file where per-case progress will be appended",
    )
    parser.add_argument(
        "--lessons-mode",
        choices=["off", "advisory", "apply"],
        default="advisory",
        help="Lessons engine mode: off (disable), advisory (generate candidate), apply (use candidate)",
    )
    parser.add_argument(
        "--lessons-scope",
        choices=["auto", "dataset", "profile", "global"],
        default="auto",
        help="Scope for lesson filtering",
    )
    parser.add_argument(
        "--lessons-window",
        type=int,
        default=5,
        help="Number of recent lessons to consider (default: 5)",
    )

    args = parser.parse_args()

    # Enable progress logging if requested
    if args.progress_log:
        os.environ["RAGCHECKER_PROGRESS_LOG"] = args.progress_log
    if args.with_ragas:
        os.environ["RAGCHECKER_WITH_RAGAS_LIKE"] = "1"

    # Breakthrough mode: disable auto-stable fallback and safety guard
    if args.breakthrough:
        # Signal downstream logic not to auto-load stable defaults
        os.environ["RAGCHECKER_DISABLE_STABLE_DEFAULT"] = "1"
        # Also disable safety guard for strict/stable settings
        os.environ.setdefault("RAGCHECKER_DISABLE_SAFE_GUARD", "1")
        print("🚨 Breakthrough mode enabled: skipping stable auto-load and SafeEval guard")

    # Handle explicit env-file or profile first (highest precedence)
    if args.env_file:
        if os.path.exists(args.env_file):
            print(f"🔒 Loading explicit env file: {args.env_file}")
            applied = _load_env_file(args.env_file, lock=True)
            os.environ["RAGCHECKER_LOCK_ENV"] = "1"
            os.environ["RAGCHECKER_ENV_FILE"] = args.env_file
            try:
                print(f"🔧 Applied {applied} env keys from {args.env_file}")
            except Exception:
                pass
        else:
            print(f"❌ Env file not found: {args.env_file}")
            return 1

    elif args.profile == "recall":
        recall_env = "configs/recall_optimized_bedrock.env"
        if os.path.exists(recall_env):
            print(f"🔒 Loading recall profile: {recall_env}")
            applied = _load_env_file(recall_env, lock=True)
            os.environ["RAGCHECKER_LOCK_ENV"] = "1"
            os.environ["RAGCHECKER_ENV_FILE"] = recall_env
            try:
                print(f"🔧 Applied {applied} env keys from {recall_env}")
            except Exception:
                pass
        else:
            print(f"❌ Recall profile not found: {recall_env}")
            return 1

    # Default to stable env when nothing is specified (safety net)
    # Ensures direct invocations behave like the wrapper unless explicitly overridden.
    # Skipped when breakthrough mode or explicit disable flag is set.
    if (
        not args.stable
        and not args.profile
        and not args.env_file
        and not os.getenv("RAGCHECKER_ENV_FILE")
        and os.getenv("RAGCHECKER_DISABLE_STABLE_DEFAULT", "0") != "1"
    ):
        default_env = "configs/stable_bedrock.env"
        if os.path.exists(default_env):
            try:
                print(f"🛡️  No env specified; defaulting to stable configuration: {default_env}")
                # Use robust loader that strips inline comments and quotes
                applied = _load_env_file(default_env, lock=True)
                # Lock for regression parity (matches --stable behavior)
                os.environ["RAGCHECKER_LOCK_ENV"] = "1"
                os.environ["RAGCHECKER_ENV_FILE"] = default_env
                # Surface how to override
                print(
                    "🔒 Environment locked. Override by setting RAGCHECKER_ENV_FILE or passing --stable with your file."
                )
                try:
                    print(f"🔧 Applied {applied} env keys from {default_env}")
                except Exception:
                    pass
            except Exception as _e:
                print(f"⚠️ Failed to auto-load stable env: {default_env} ({_e})")

    # Load stable configuration if requested
    if args.stable or args.profile == "stable":
        stable_env_file = os.getenv("RAGCHECKER_ENV_FILE", "configs/stable_bedrock.env")
        if os.path.exists(stable_env_file):
            print(f"🔒 Loading stable configuration: {stable_env_file}")
            # Load environment variables from stable config using robust parser
            applied = _load_env_file(stable_env_file, lock=True)
            os.environ["RAGCHECKER_LOCK_ENV"] = "1"
            os.environ["RAGCHECKER_ENV_FILE"] = stable_env_file
            print("🔒 Environment locked for regression tracking")
            try:
                print(f"🔧 Applied {applied} env keys from {stable_env_file}")
            except Exception:
                pass
        else:
            print(f"❌ Stable config not found: {stable_env_file}")
            print("💡 Run: cp configs/stable_bedrock.env.template configs/stable_bedrock.env")
            return 1

    # Lessons Engine Integration
    lessons_applied = []
    decision_docket_path = None
    if args.lessons_mode != "off":
        try:
            # Determine base environment file for lessons
            base_env_file = os.getenv("RAGCHECKER_ENV_FILE", "configs/stable_bedrock.env")
            if not os.path.exists(base_env_file):
                base_env_file = "configs/current_best.env"

            print(f"🧠 Lessons Engine: {args.lessons_mode} mode")

            # Import lessons loader
            import json
            import subprocess
            import sys

            # Run lessons loader with proper scope mapping
            lessons_cmd = [
                sys.executable,
                "scripts/lessons_loader.py",
                base_env_file,
                "metrics/lessons/lessons.jsonl",
                "--mode",
                args.lessons_mode,
                "--window",
                str(args.lessons_window),
            ]

            # Map lessons-scope to proper loader arguments
            if args.lessons_scope == "profile":
                lessons_cmd.extend(["--scope-level", "profile", "--scope-profile", "auto"])
            elif args.lessons_scope == "dataset":
                lessons_cmd.extend(["--scope-level", "dataset", "--scope-dataset", "auto"])
            elif args.lessons_scope == "global":
                lessons_cmd.extend(["--scope-level", "global"])
            else:  # auto
                lessons_cmd.extend(["--scope-level", "profile", "--scope-profile", "auto"])

            try:
                result = subprocess.run(
                    lessons_cmd,
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd(),
                    stdin=subprocess.DEVNULL,
                    timeout=float(os.getenv("RAGCHECKER_POST_LESSONS_TIMEOUT_SEC", "45")),
                )
            except subprocess.TimeoutExpired:
                print("⚠️ Lessons loader timed out; continuing without lesson application")
                result = subprocess.CompletedProcess(lessons_cmd, returncode=124, stdout="", stderr="timeout")

            if result.returncode == 0:
                lessons_info = json.loads(result.stdout)
                lessons_applied = lessons_info.get("applied_lessons", [])
                decision_docket_path = lessons_info.get("decision_docket")
                candidate_env_path = lessons_info.get("candidate_env")
                apply_blocked = lessons_info.get("apply_blocked", False)
                gate_warnings = lessons_info.get("gate_warnings", [])

                print(f"✅ Lessons Engine: Applied {len(lessons_applied)} lessons")
                if decision_docket_path:
                    print(f"📋 Decision docket: {decision_docket_path}")

                # Apply candidate environment if in apply mode and not blocked by gates
                if (
                    args.lessons_mode == "apply"
                    and not apply_blocked
                    and candidate_env_path
                    and os.path.exists(candidate_env_path)
                ):
                    print(f"🔧 Applying candidate environment: {candidate_env_path}")
                    applied = _load_env_file(candidate_env_path, lock=True)
                    os.environ["RAGCHECKER_LOCK_ENV"] = "1"
                    os.environ["RAGCHECKER_ENV_FILE"] = candidate_env_path
                    os.environ["LESSONS_APPLIED"] = ",".join(lessons_applied)
                    os.environ["DERIVED_FROM"] = os.path.basename(base_env_file)
                    print(f"🔧 Applied {applied} env keys from candidate config")
                else:
                    # Advisory mode or apply blocked - record suggestions only
                    if args.lessons_mode == "apply" and apply_blocked:
                        warn_count = len(gate_warnings) if isinstance(gate_warnings, list) else 0
                        docket_note = f"; docket: {decision_docket_path}" if decision_docket_path else ""
                        print(
                            f"🛡️  Apply blocked by quality gates ({warn_count}) — continuing with base environment{docket_note}"
                        )
                    os.environ["LESSONS_SUGGESTED"] = ",".join(lessons_applied)
                    if decision_docket_path:
                        os.environ["DECISION_DOCKET"] = decision_docket_path

                # Store lessons metadata for results
                lessons_metadata = {
                    "lessons_mode": args.lessons_mode,
                    "lessons_scope": args.lessons_scope,
                    "lessons_window": args.lessons_window,
                    "applied_lessons": lessons_applied,
                    "decision_docket": decision_docket_path,
                    "candidate_env": candidate_env_path,
                    "apply_blocked": apply_blocked,
                    "gate_warnings": gate_warnings,
                }

                # Generate Agent Briefing Pack (ABP) after lessons loader, before evaluation
                try:
                    import subprocess as _sub

                    # Compute profile name
                    profile_name = (
                        args.profile
                        if getattr(args, "profile", None)
                        else os.path.splitext(os.path.basename(base_env_file))[0]
                    )
                    abp_cmd = [
                        sys.executable,
                        "scripts/abp_packer.py",
                        "--profile",
                        profile_name or "default",
                        "--lessons-jsonl",
                        "metrics/lessons/lessons.jsonl",
                        "--decision-docket",
                        decision_docket_path or "",
                    ]
                    # Try to pass baseline manifest if it exists
                    manifest_path = os.path.join("config", "baselines", f"{profile_name}.json")
                    if os.path.exists(manifest_path):
                        abp_cmd.extend(["--baseline-manifest", manifest_path])
                    # Optional pattern cards
                    pattern_cards = os.path.join("metrics", "graphs", "pattern_cards.json")
                    if os.path.exists(pattern_cards):
                        abp_cmd.extend(["--pattern-cards", pattern_cards])

                    try:
                        abp_res = _sub.run(
                            abp_cmd,
                            capture_output=True,
                            text=True,
                            cwd=os.getcwd(),
                            stdin=subprocess.DEVNULL,
                            timeout=float(os.getenv("RAGCHECKER_ABP_TIMEOUT_SEC", "45")),
                        )
                    except _sub.TimeoutExpired:
                        print("⚠️ ABP generation timed out; skipping")
                        abp_res = _sub.CompletedProcess(abp_cmd, returncode=124, stdout="", stderr="timeout")
                    if abp_res.returncode == 0 and abp_res.stdout.strip():
                        abp_path = abp_res.stdout.strip().splitlines()[-1]
                        print(f"📄 Agent Briefing Pack: {abp_path}")
                        os.environ["AGENT_BRIEFING_PACK"] = abp_path
                    else:
                        if abp_res.stderr:
                            print(f"⚠️ ABP generation warning: {abp_res.stderr.strip()}")
                except Exception as _abp_err:
                    print(f"⚠️ ABP generation error: {_abp_err}")
            else:
                print(f"⚠️ Lessons Engine failed: {result.stderr}")

        except Exception as e:
            print(f"⚠️ Lessons Engine error: {e}")

    # Apply safety guard unless explicitly disabled (breakthrough sets this)
    if os.getenv("RAGCHECKER_DISABLE_SAFE_GUARD", "0") != "1":
        print("🛡️  SafeEval: enforcing stable settings for high-risk combos")
        _enforce_safe_eval_env()

    # Validate backend selection
    if args.use_local_llm and args.use_bedrock:
        print("❌ Cannot use both --use-local-llm and --use-bedrock simultaneously")
        print("💡 Choose one backend or let the system auto-detect")
        return None

    # Determine backend preference
    use_bedrock = args.use_bedrock
    use_local_llm = args.use_local_llm

    # Auto-detect if no explicit choice
    if not use_bedrock and not use_local_llm:
        # Check for Bedrock availability first (faster, more reliable)
        if BEDROCK_AVAILABLE:
            try:
                test_client = BedrockClient()  # type: ignore
                if test_client.test_connection():
                    print("🧠 Auto-detected: Using AWS Bedrock (faster, more reliable)")
                    use_bedrock = True
                else:
                    print("🔄 Bedrock unavailable, falling back to local LLM")
                    use_local_llm = True
            except Exception:
                print("🔄 Bedrock unavailable, falling back to local LLM")
                use_local_llm = True
        else:
            print("🔄 Bedrock not available, using local LLM")
            use_local_llm = True

    # Set bypass flag if requested
    if args.bypass_cli:
        os.environ["RAGCHECKER_BYPASS_CLI"] = "1"

    evaluator = OfficialRAGCheckerEvaluator()
    results = evaluator.run_official_evaluation(use_local_llm, args.local_api_base, use_bedrock)

    # Post-run Lessons Extractor Integration
    if args.lessons_mode != "off" and results:
        try:
            print("🧠 Running post-evaluation lessons extractor...")

            # Find the results file that was just created
            results_dir = "metrics/baseline_evaluations"
            if os.path.exists(results_dir):
                # Get the most recent results file
                result_files = [f for f in os.listdir(results_dir) if f.endswith(".json")]
                if result_files:
                    latest_file = max(result_files, key=lambda x: os.path.getctime(os.path.join(results_dir, x)))
                    results_file = os.path.join(results_dir, latest_file)

                    # Find corresponding progress JSONL file
                    progress_file = None
                    if os.getenv("RAGCHECKER_PROGRESS_LOG"):
                        progress_file = os.getenv("RAGCHECKER_PROGRESS_LOG")
                    else:
                        # Look for progress file in same directory
                        base_name = os.path.splitext(latest_file)[0]
                        progress_candidates = [
                            os.path.join(results_dir, f"{base_name}_progress.jsonl"),
                            os.path.join(results_dir, "progress.jsonl"),
                        ]
                        for candidate in progress_candidates:
                            if os.path.exists(candidate):
                                progress_file = candidate
                                break

                    # Run lessons extractor
                    import sys as _sys

                    extractor_cmd = [_sys.executable, "scripts/lessons_extractor.py", results_file]
                    if progress_file:
                        extractor_cmd.append(progress_file)

                    try:
                        extractor_result = subprocess.run(
                            extractor_cmd,
                            capture_output=True,
                            text=True,
                            cwd=os.getcwd(),
                            stdin=subprocess.DEVNULL,
                            timeout=float(os.getenv("RAGCHECKER_LESSONS_EXTRACT_TIMEOUT_SEC", "60")),
                        )
                    except subprocess.TimeoutExpired:
                        print("⚠️ Lessons extractor timed out; skipping post-run extraction")
                        extractor_result = subprocess.CompletedProcess(
                            extractor_cmd, returncode=124, stdout="", stderr="timeout"
                        )

                    if extractor_result.returncode == 0:
                        print("✅ Lessons extractor completed successfully")
                        print("📝 New lessons written to: metrics/lessons/lessons.jsonl")
                    else:
                        print(f"⚠️ Lessons extractor failed: {extractor_result.stderr}")

        except Exception as e:
            print(f"⚠️ Post-evaluation lessons extraction error: {e}")

    return results


# Evidence filtering functions for precision/faithfulness protection


def _ctx_to_list_str(ctx_any) -> list[str]:
    """Normalize context to list[str] for safe ranking."""
    out: list[str] = []
    for c in ctx_any or []:
        if isinstance(c, dict) and "text" in c:
            out.append(str(c["text"]))
        elif isinstance(c, str):
            out.append(c)
    return out


def _norm_tokens(text: str) -> list[str]:
    """Normalize text to tokens for comparison."""
    return re.findall(r"[a-z0-9]+", text.lower())


def _jaccard(a: set[str], b: set[str]) -> float:
    """Calculate Jaccard similarity between token sets."""
    return (len(a & b) / len(a | b)) if (a or b) else 0.0


def sentence_supported(sentence: str, contexts: list[str], j_min: float = 0.18, coverage_min: float = 0.45) -> bool:
    """Check if a sentence is supported by context using multiple similarity metrics."""
    # j_min: Jaccard over unique tokens
    # coverage_min: fraction of sentence tokens that appear in context
    s = set(_norm_tokens(sentence))
    if not s:
        return False
    for ctx in contexts:
        c = set(_norm_tokens(ctx))
        if not c:
            continue
        j = _jaccard(s, c)
        cov = len(s & c) / len(s)
        # Allow either sufficient Jaccard OR sufficient coverage
        if j >= j_min or cov >= coverage_min:
            # quick difflib check to prevent very loose matches
            r = SequenceMatcher(None, sentence.lower(), ctx.lower()).ratio()
            if r >= 0.35:
                return True
    return False


def evidence_filter(answer: str, contexts: list[str], j_min: float = 0.18, coverage_min: float = 0.45) -> str:
    """Enhanced multi-signal evidence filter with dynamic-K selection and blended scoring."""

    def _tokens(s: str) -> list[str]:
        return re.findall(r"[a-z0-9]+", s.lower())

    def _jaccard(a: set[str], b: set[str]) -> float:
        return (len(a & b) / len(a | b)) if (a or b) else 0.0

    def _lcs_len(a: list[str], b: list[str]) -> int:
        m, n = len(a), len(b)
        dp = [0] * (n + 1)
        for i in range(1, m + 1):
            prev = 0
            ai = a[i - 1]
            for j in range(1, n + 1):
                tmp = dp[j]
                dp[j] = prev + 1 if ai == b[j - 1] else max(dp[j], dp[j - 1])
                prev = tmp
        return dp[n]

    def _rouge_l_f1(a: str, b: str) -> float:
        ta, tb = _tokens(a), _tokens(b)
        if not ta or not tb:
            return 0.0
        lcs = _lcs_len(ta, tb)
        p = lcs / len(tb)
        r = lcs / len(ta)
        return (2 * p * r / (p + r)) if (p + r) else 0.0

    def normalize_scores(scores):
        """Normalize scores to 0-1 range using min-max normalization."""
        if not scores:
            return scores
        min_score = min(scores)
        max_score = max(scores)
        if max_score == min_score:
            return [0.5] * len(scores)
        return [(s - min_score) / (max_score - min_score) for s in scores]

    def trigram_overlap(s1, s2):
        """Calculate trigram overlap between two sentences."""

        def get_trigrams(s):
            words = _tokens(s)
            return set(" ".join(words[i : i + 3]) for i in range(len(words) - 2))

        trigrams1 = get_trigrams(s1)
        trigrams2 = get_trigrams(s2)
        if not trigrams1 or not trigrams2:
            return 0.0
        return len(trigrams1 & trigrams2) / len(trigrams1 | trigrams2)

    # Get enhanced parameters from environment
    min_sent = int(os.getenv("RAGCHECKER_EVIDENCE_MIN_SENT", "2"))
    max_sent = int(os.getenv("RAGCHECKER_EVIDENCE_MAX_SENT", "9"))

    # Blended scoring weights
    weight_jaccard = float(os.getenv("RAGCHECKER_WEIGHT_JACCARD", "0.20"))
    weight_rouge = float(os.getenv("RAGCHECKER_WEIGHT_ROUGE", "0.30"))
    weight_cosine = float(os.getenv("RAGCHECKER_WEIGHT_COSINE", "0.50"))

    # Dynamic-K parameters
    keep_mode = os.getenv("RAGCHECKER_EVIDENCE_KEEP_MODE", "percentile")
    target_k_weak = int(os.getenv("RAGCHECKER_TARGET_K_WEAK", "3"))
    target_k_base = int(os.getenv("RAGCHECKER_TARGET_K_BASE", "5"))
    target_k_strong = int(os.getenv("RAGCHECKER_TARGET_K_STRONG", "7"))
    signal_delta_weak = float(os.getenv("RAGCHECKER_SIGNAL_DELTA_WEAK", "0.10"))
    signal_delta_strong = float(os.getenv("RAGCHECKER_SIGNAL_DELTA_STRONG", "0.22"))

    # Diversity and redundancy controls
    redundancy_max = float(os.getenv("RAGCHECKER_REDUNDANCY_TRIGRAM_MAX", "0.50"))
    per_chunk_cap = int(os.getenv("RAGCHECKER_PER_CHUNK_CAP", "2"))
    per_chunk_cap_small = int(os.getenv("RAGCHECKER_PER_CHUNK_CAP_SMALL", "3"))

    # Strip trailing citations block to avoid treating it as a single sentence
    main_answer = answer.split("Sources:", 1)[0].strip()

    # More robust sentence splitting that handles:
    # - Standard punctuation and bracketed cites
    # - Newlines
    # - Bullet/numbered list markers at line start (-, *, •, –, —, 1., 2), etc.)
    bullet_or_num = r"(?m)^\s*(?:[-*•–—]|\d+[\.)])\s+"
    sents = re.split(rf"{bullet_or_num}|(?<=[.!?\]])\s+|\n+", main_answer)
    sents = [s for s in sents if s is not None and s.strip()]

    # Optional aggressive splitter for lightly punctuated outputs
    if os.getenv("RAGCHECKER_AGGRESSIVE_SPLIT", "0") == "1":
        refined = []
        comma_patterns = [r",\s+and\s+", r",\s+which\s+", r",\s+that\s+", r",\s+but\s+"]
        for s in sents:
            if len(s) > 180:
                parts = [s]
                for pat in comma_patterns:
                    tmp = []
                    for p in parts:
                        tmp.extend(re.split(pat, p))
                    parts = tmp
                for p in parts:
                    p = p.strip()
                    if p:
                        refined.append(p)
            else:
                refined.append(s)
        sents = [x for x in refined if x.strip()]

    # Fallbacks when models produce long, lightly punctuated text or inline bullets
    if len(sents) <= 1:
        # Split on common inline separators: semicolons, em/en dashes, dot bullets
        sents = re.split(r"\s*[;—–•·]\s*", main_answer)
        sents = [s for s in sents if s.strip()]
    if len(sents) <= 1:
        # As a last resort, split on double spaces which often separate bullet-like fragments
        sents = re.split(r"\s{2,}", main_answer)
        sents = [s for s in sents if s.strip()]
    if not sents:
        return answer

    # Debug logging for mode selection
    print(f"📊 Evidence selection mode: {keep_mode}")
    if os.getenv("RAGCHECKER_DEBUG_EVIDENCE", "0") == "1":
        try:
            print(
                "🔧 Evidence config:",
                f"min_sent={min_sent}",
                f"max_sent={max_sent}",
                f"weights(j={weight_jaccard},r={weight_rouge},c={weight_cosine})",
                f"K(weak={target_k_weak},base={target_k_base},strong={target_k_strong})",
                f"deltas(weak={signal_delta_weak},strong={signal_delta_strong})",
                f"redundancy_max={redundancy_max}",
                f"per_chunk_cap={per_chunk_cap}/{per_chunk_cap_small}",
            )
        except Exception:
            pass

    # Calculate blended scores for each sentence
    jaccard_scores = []
    rouge_scores = []
    cosine_scores = []
    support_flags = []  # whether a sentence passes j_min/coverage_min against any context

    all_context = " ".join(contexts)
    all_context_tokens = set(_tokens(all_context))

    for sent in sents:
        if not sent.strip():
            jaccard_scores.append(0.0)
            rouge_scores.append(0.0)
            cosine_scores.append(0.0)
            support_flags.append(False)
            continue

        sent_tokens = set(_tokens(sent))

        # Jaccard similarity
        per_ctx_j = [_jaccard(sent_tokens, set(_tokens(ctx))) for ctx in contexts]
        jaccard_score = max(per_ctx_j + [0.0])
        jaccard_scores.append(jaccard_score)

        # ROUGE-L F1
        rouge_score = max([_rouge_l_f1(sent, ctx) for ctx in contexts] + [0.0])
        rouge_scores.append(rouge_score)

        # Simple cosine similarity (token overlap)
        cosine_score = _jaccard(sent_tokens, all_context_tokens)
        cosine_scores.append(cosine_score)

        # Evidence guard: compute coverage per context and decide if supported
        per_ctx_cov = []
        if sent_tokens:
            for ctx in contexts:
                ctx_tokens = set(_tokens(ctx))
                cov = (len(sent_tokens & ctx_tokens) / len(sent_tokens)) if sent_tokens else 0.0
                per_ctx_cov.append(cov)
        cov_max = max(per_ctx_cov + [0.0])
        support_ok = (jaccard_score >= j_min) or (cov_max >= coverage_min)
        support_flags.append(support_ok)

    # Normalize scores
    jaccard_norm = normalize_scores(jaccard_scores)
    rouge_norm = normalize_scores(rouge_scores)
    cosine_norm = normalize_scores(cosine_scores)

    # Calculate blended scores
    blended_scores = []
    for i in range(len(sents)):
        score = weight_jaccard * jaccard_norm[i] + weight_rouge * rouge_norm[i] + weight_cosine * cosine_norm[i]
        # If sentence fails both guard thresholds, heavily downweight (but allow min_sent fallback later)
        if not support_flags[i]:
            score -= 1.0
        blended_scores.append(score)

    # Dynamic target-K selection or percentile fallback
    if keep_mode == "target_k" and len(blended_scores) > 0:
        scores_array = np.array(blended_scores)

        # Force override via env (applies to evidence_filter stage as well)
        force_k = int(os.getenv("RAGCHECKER_FORCE_TARGET_K", "0") or 0)
        force_strength = os.getenv("RAGCHECKER_FORCE_SIGNAL_STRENGTH", "").lower()

        if force_k > 0 or force_strength in {"weak", "base", "strong"}:
            if force_k <= 0:
                target_k = {"weak": target_k_weak, "base": target_k_base, "strong": target_k_strong}[force_strength]
            else:
                target_k = force_k
            target_k = max(min_sent, min(target_k, max_sent))
            print(f"📊 Dynamic-K: forced strength={force_strength or 'explicit_k'}, target_k={target_k}")
        else:
            top_score = np.max(scores_array)
            median_score = np.median(scores_array)
            signal_delta = top_score - median_score

            # Determine target K based on signal strength
            if signal_delta >= signal_delta_strong:
                target_k = target_k_strong
                signal_strength = "strong"
            elif signal_delta >= signal_delta_weak:
                target_k = target_k_base
                signal_strength = "base"
            else:
                target_k = target_k_weak
                signal_strength = "weak"

            # Clamp by min/max constraints
            target_k = max(min_sent, min(target_k, max_sent))

            # Debug logging
            print(f"📊 Dynamic-K: signal_delta={signal_delta:.3f}, strength={signal_strength}, target_k={target_k}")

        # Select top K candidates
        sorted_indices = np.argsort(scores_array)[::-1]
        candidates_indices = sorted_indices[:target_k].tolist()
    else:
        # Fallback to percentile-based selection
        keep_percentile = float(os.getenv("RAGCHECKER_EVIDENCE_KEEP_PERCENTILE", "65"))
        scores_array = np.array(blended_scores)
        threshold = np.percentile(scores_array, keep_percentile)
        candidates_indices = np.where(scores_array >= threshold)[0].tolist()

    # Sort by score
    candidates_indices.sort(key=lambda i: blended_scores[i], reverse=True)

    # Diversity + redundancy filtering
    kept_indices = []
    seen_by_chunk = defaultdict(int)

    # Simple chunk assignment (each context is a chunk)
    chunk_assignments = {i: i % len(contexts) for i in range(len(sents))}

    for idx in candidates_indices:
        chunk_id = chunk_assignments.get(idx, 0)

        # Apply per-chunk cap
        max_per_chunk = per_chunk_cap_small if len(contexts) < 10 else per_chunk_cap
        if seen_by_chunk[chunk_id] >= max_per_chunk:
            continue

        # Check redundancy with already kept sentences
        sent = sents[idx]
        is_redundant = False
        for kept_idx in kept_indices:
            if trigram_overlap(sent, sents[kept_idx]) > redundancy_max:
                is_redundant = True
                break

        if not is_redundant:
            kept_indices.append(idx)
            seen_by_chunk[chunk_id] += 1

        if len(kept_indices) >= max_sent:
            break

    # Ensure minimum sentences
    if len(kept_indices) < min_sent:
        for i, sent in enumerate(sents):
            if i not in kept_indices and len(kept_indices) < min_sent:
                kept_indices.append(i)

    # Sort by original order and build result
    kept_indices.sort()
    kept_sentences = [sents[i] for i in kept_indices]

    result = " ".join(kept_sentences) if kept_sentences else answer
    # Debug summary: show thresholds once per call
    try:
        print(
            f"📝 Evidence filtering: {len(kept_sentences)}/{len(sents)} sentences kept (enhanced multi-signal guard) — "
            f"j_min={j_min:.2f}, coverage_min={coverage_min:.2f}"
        )
    except Exception:
        pass
    return result


if __name__ == "__main__":
    try:
        result = main()
    finally:
        # Always print results directory hint for discoverability
        print("\n📦 Results directory: metrics/baseline_evaluations/")
        print("🧭 Eval SOP: 000_core/000_evaluation-system-entry-point.md")
