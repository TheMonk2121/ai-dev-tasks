# Focused Configuration Migration Report

This report focuses on project-specific configuration patterns that need migration.

## Project Environment Variables
Total unique environment variables: 284

### APP_* variables (1)
- `APP_ENV`

### AWS_* variables (8)
- `AWS_ACCESS_KEY_ID`
- `AWS_ACCESS_KEY_ID_1`
- `AWS_ACCESS_KEY_ID_2`
- `AWS_PROFILE`
- `AWS_REGION`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SECRET_ACCESS_KEY_1`
- `AWS_SECRET_ACCESS_KEY_2`

### CHUNK_* variables (4)
- `CHUNK_PROCESSING_TIMEOUT`
- `CHUNK_SIZE`
- `CHUNK_VARIANT`
- `CHUNK_VERSION`

### DB_* variables (5)
- `DB_CONNECT_TIMEOUT`
- `DB_DRIVER`
- `DB_POOL_TIMEOUT`
- `DB_READ_TIMEOUT`
- `DB_WRITE_TIMEOUT`

### DSPY_* variables (2)
- `DSPY_MODEL`
- `DSPY_RAG_PATH`

### EVAL_* variables (11)
- `EVAL_CASES_FILE`
- `EVAL_CONCURRENCY`
- `EVAL_COT`
- `EVAL_DISABLE_CACHE`
- `EVAL_DISABLE_VARIANT_ASSERT`
- `EVAL_DRIVER`
- `EVAL_MODE`
- `EVAL_PASS`
- `EVAL_PATH`
- `EVAL_STRICT_ARRAYS`
- `EVAL_SUITE`

### HTTP_* variables (3)
- `HTTP_CONNECT_TIMEOUT`
- `HTTP_READ_TIMEOUT`
- `HTTP_TOTAL_TIMEOUT`

### LLM_* variables (3)
- `LLM_REQUEST_TIMEOUT`
- `LLM_STREAM_TIMEOUT`
- `LLM_TIMEOUT_SEC`

### OTHER* variables (246)
- `AUTO_REHYDRATE`
- `BASELINE_METRICS_FILE`
- `BEDROCK_BASE_BACKOFF`
- `BEDROCK_BASE_RPS`
- `BEDROCK_CALL_TIMEOUT_SEC`
- `BEDROCK_CONNECT_TIMEOUT`
- `BEDROCK_COOLDOWN_SEC`
- `BEDROCK_MAX_BACKOFF`
- `BEDROCK_MAX_IN_FLIGHT`
- `BEDROCK_MAX_RETRIES`
- `BEDROCK_MAX_RPS`
- `BEDROCK_MODEL_ID`
- `BEDROCK_OUTER_RETRIES`
- `BEDROCK_QUEUE_BASE_DELAY`
- `BEDROCK_QUEUE_BATCH_SIZE`
- `BEDROCK_QUEUE_BATCH_WINDOW`
- `BEDROCK_RETRY_BASE`
- `BEDROCK_RETRY_MAX_SLEEP`
- `BM25_MIN`
- `BM25_TEXT_FIELD`
- `BM25_TRIGRAM_FALLBACK`
- `CACHE_DISABLED`
- `CACHE_ENABLED_PROD`
- `CANDIDATE_FILE`
- `CASES_FILE`
- `COLD_START_WVEC_BOOST`
- `CONFIG_HASH`
- `CONTEXT_DOCS_MAX`
- `CONTEXT_MAX_CHARS`
- `COS_FLOOR`
- `COT_FLAG`
- `COVERAGE_MIN`
- `DATABASE_URL`
- `DATASET_HAS_GOLD`
- `DATASET_VERSION`
- `DECISION_TRIGRAM_ENABLED`
- `DEFAULT_ACTIVE_AGENT`
- `DEPLOY_DISABLE_NEW_CONFIG`
- `EMBEDDING_MODEL`
- `EMBEDDING_PROVIDER`
- `EMBEDDING_TEXT_FIELD`
- `EMBED_BATCH`
- `EMBED_DIM`
- `EMBED_MODEL`
- `ENVIRONMENT`
- `F1_MIN`
- `FAITHFULNESS_MIN`
- `FAST_MODE`
- `FEW_SHOT_IDS`
- `FEW_SHOT_K`
- `FILE_ORACLE_PREFILTER_MIN`
- `FILE_ORACLE_READER_MIN`
- `FILE_UPLOAD_TIMEOUT`
- `FUSED_MIN`
- `FUSE_TAIL_KEEP`
- `FUSION_DEVICE`
- `FUSION_FEATURE_SPEC`
- `FUSION_HEAD_ENABLE`
- `FUSION_HEAD_PATH`
- `FUSION_HIDDEN`
- `FUSION_METHOD`
- `GATE_COVER_MIN`
- `GATE_TOPK`
- `GATE_TOPK_MIN_HIT`
- `GENERATION_MODEL`
- `GENERATION_PROVIDER`
- `GOLD_FILE`
- `GOLD_MODE`
- `GOLD_PROFILE`
- `GOLD_SIZE`
- `GOLD_TAGS`
- `HEALTH_CHECK_CONFIG`
- `HEALTH_CHECK_DB`
- `HEALTH_CHECK_ENV`
- `HEALTH_CHECK_INDEX`
- `HEALTH_CHECK_MODELS`
- `HEALTH_CHECK_PREFIX_LEAKAGE`
- `HEALTH_CHECK_RESOURCES`
- `HEALTH_CHECK_TIMEOUT`
- `HEALTH_CHECK_TOKEN_BUDGET`
- `HINT_PREFETCH_LIMIT`
- `HOSTNAME`
- `HYBRID_DEBUG_NS`
- `HYBRID_USE_WRAPPER`
- `INGEST_RUN_ID`
- `IVFFLAT_LISTS`
- `LATENCY_MAX`
- `LATEST_METRICS_FILE`
- `LATEST_READER_FILE`
- `LITELLM_MAX_RETRIES`
- `LITELLM_TIMEOUT`
- `LOG_FILE`
- `LOG_LEVEL`
- `MAX_PER_TAG`
- `MAX_READER_REG_DROP`
- `MAX_READ_WEEKLY_DRIFT`
- `MAX_REG_DROP`
- `MAX_RETR_WEEKLY_DRIFT`
- `MAX_TOKENS`
- `MEMORY_HEALTHCHECK_OFFLINE`
- `MEMORY_VERIFY_SESSION`
- `MEMORY_VERIFY_USER`
- `METRICS_TIMEOUT`
- `MIGRATION_TEST_MODE`
- `MISTRAL_7B_URL`
- `MMR_ALPHA`
- `MONITORING_URL`
- `NS_RESERVED`
- `ORACLE_CTX_J_MIN`
- `ORACLE_RETRIEVAL_HIT_MIN`
- `ORACLE_SENT_J_MIN`
- `OUT_FILE`
- `PATH`
- `PDF_PROCESSING_TIMEOUT`
- `PER_FILE_CAP`
- `PGDATABASE`
- `PGHOST`
- `PGPASSWORD`
- `PGPORT`
- `PGUSER`
- `PGVECTOR_OPS`
- `PIPELINE_WORKERS`
- `POOL_NS`
- `PORT`
- `PRECISION_MIN`
- `PREFILTER_MIN_MICRO`
- `PREFILTER_MIN_TAG`
- `PREFIX_GUARD_ENABLED`
- `PROMPT_AUDIT`
- `PYTHON`
- `PYTHONPATH`
- `Q`
- `RAGCHECKER_BM25_BOOST_ANCHORS`
- `RAGCHECKER_BORDERLINE_BAND`
- `RAGCHECKER_BYPASS_CLI`
- `RAGCHECKER_CE_RERANK_ENABLE`
- `RAGCHECKER_CE_RERANK_TOPN`
- `RAGCHECKER_CE_WEIGHT`
- `RAGCHECKER_CLAIM_CONFIDENCE_ENABLED`
- `RAGCHECKER_CLAIM_CONFIDENCE_WEIGHTS`
- `RAGCHECKER_CLAIM_TOPK`
- `RAGCHECKER_CONTEXT_TOPK`
- `RAGCHECKER_COSINE_FLOOR`
- `RAGCHECKER_CROSS_ENCODER_CACHE`
- `RAGCHECKER_CROSS_ENCODER_ENABLED`
- `RAGCHECKER_CROSS_ENCODER_TOP_N`
- `RAGCHECKER_CROSS_ENCODER_WEIGHT`
- `RAGCHECKER_DISABLE_EMBEDDINGS`
- `RAGCHECKER_ENTITY_MUST_MATCH`
- `RAGCHECKER_EVIDENCE_COVERAGE`
- `RAGCHECKER_EVIDENCE_JACCARD`
- `RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR`
- `RAGCHECKER_FAST_MODE`
- `RAGCHECKER_HAIKU_FLOORS`
- `RAGCHECKER_JUDGE_MODE`
- `RAGCHECKER_MIN_WORDS_AFTER_BINDING`
- `RAGCHECKER_MMR_LAMBDA`
- `RAGCHECKER_NLI_ENABLE`
- `RAGCHECKER_NLI_ON_BORDERLINE`
- `RAGCHECKER_NLI_P_THRESHOLD`
- `RAGCHECKER_NUMERIC_MUST_MATCH`
- `RAGCHECKER_NUM_WORKERS`
- `RAGCHECKER_PER_CHUNK_CAP`
- `RAGCHECKER_PER_DOC_LINE_CAP`
- `RAGCHECKER_PROGRESS_LOG`
- `RAGCHECKER_REDUNDANCY_TRIGRAM_MAX`
- `RAGCHECKER_RETRIEVAL_HYBRID`
- `RAGCHECKER_REWRITE_AGREE_STRONG`
- `RAGCHECKER_REWRITE_K`
- `RAGCHECKER_REWRITE_KEEP`
- `RAGCHECKER_REWRITE_YIELD_MIN`
- `RAGCHECKER_ROUTE_BM25_MARGIN`
- `RAGCHECKER_RRF_K`
- `RAGCHECKER_TARGET_K_STRONG`
- `RAGCHECKER_TARGET_K_WEAK`
- `RAGCHECKER_USE_MMR`
- `RAGCHECKER_USE_REAL_RAG`
- `RAGCHECKER_USE_RRF`
- `RANDOM_SEED`
- `READER_ABSTAIN`
- `READER_BASELINE_FILE`
- `READER_CMD`
- `READER_COMPACT`
- `READER_ENFORCE_SPAN`
- `READER_FAIL_ON_MISSING_ID`
- `READER_GOLD_FILE`
- `READER_ID_MAP`
- `READER_LEFTOVER`
- `READER_MIN_F1_MICRO`
- `READER_MIN_F1_TAG`
- `READER_OUT`
- `READER_PRECHECK`
- `READER_PRECHECK_MIN_OVERLAP`
- `READER_SRC`
- `READER_USED_GOLD_MIN`
- `RECALL_MIN`
- `REHYDRATE_DEDUPE`
- `REHYDRATE_EXPAND_QUERY`
- `REHYDRATE_MINUTES`
- `REHYDRATE_STABILITY`
- `RERANKER_CACHE_DIR`
- `RERANKER_CACHE_ENABLED`
- `RERANKER_ENABLED`
- `RERANKER_MODEL`
- `RERANKER_PREWARM`
- `RERANK_BATCH`
- `RERANK_ENABLE`
- `RERANK_INPUT_TOPK`
- `RERANK_KEEP`
- `RERANK_MODEL`
- `RERANK_POOL`
- `RERANK_TOPN`
- `RETRIEVER_LIMITS_FILE`
- `RETRIEVER_WEIGHTS_FILE`
- `RETR_TOPK_BM25`
- `RETR_TOPK_OTHER`
- `RETR_TOPK_VEC`
- `ROUGE_FLOOR`
- `RRF_K`
- `SAVE_CANDIDATES_MAX`
- `SECRETS_DIR`
- `SECURITY_MAX_FILE_MB`
- `SEED`
- `SHELL`
- `SNAPSHOT_MAX_ITEMS`
- `SNAPSHOT_MIN`
- `STARTUP_TIMEOUT`
- `TAG`
- `TEMPERATURE`
- `TITLE_TRIGRAM_FALLBACK`
- `TOKEN_PACK_BUDGET`
- `TOKEN_PACK_ENABLE`
- `TOKEN_PACK_FAMILY`
- `TOKEN_PACK_LLAMA_PATH`
- `TOKEN_PACK_MODEL`
- `TOKEN_PACK_RESERVE`
- `TORCH_DEVICE`
- `USER`
- `VALIDATE_CANDIDATES`
- `VAR`
- `VEC_MIN`
- `VENV_DISABLE_IMPORT_CHECK`
- `VENV_REQUIRED_PACKAGES`
- `VENV_VALIDATE_MINIMAL`
- `VIRTUAL_ENV`
- `YI_CODER_URL`

### POSTGRES_* variables (1)
- `POSTGRES_DSN`

## os.getenv() Calls to Migrate
Total os.getenv calls: 521

### scripts/_ragchecker_eval_impl.py
- Line 53: `DSPY_RAG_PATH`
  ```python
  # Add DSPy RAG system to path (env override still respected)
dspy_rag_path = os.getenv("DSPY_RAG_PATH", "src")
if dspy_rag_path and dspy_rag_path not in sys.path:
    sys.path.insert(0, dspy_rag_path)
  ```
- Line 114: `DSPY_RAG_PATH`
  ```python
  def __init__(self):
        rag_path = os.getenv("DSPY_RAG_PATH", "src")
        if rag_path and rag_path not in sys.path:
            sys.path.insert(0, rag_path)
  ```
- Line 134: `DSPY_MODEL`
  ```python
  # Configure DSPy with language model
            model_name = os.getenv("DSPY_MODEL", "anthropic.claude-3-haiku-20240307-v1:0")
            dspy.configure(lm=dspy.LM(model_name))
  ```
- Line 162: `SAVE_CANDIDATES_MAX`
  ```python
  self._assert_variant(used_ctx)

        max_cands = int(os.getenv("SAVE_CANDIDATES_MAX", "60"))
        return {
            "answer": ans_text,
  ```
- Line 176: `EVAL_DISABLE_VARIANT_ASSERT`
  ```python
  import os

        if os.getenv("EVAL_DISABLE_VARIANT_ASSERT", "0") == "1":
            return
        if not used_ctx:
  ```
- Line 191: `INGEST_RUN_ID`
  ```python
  # Optional: enforce expected run
        want = os.getenv("INGEST_RUN_ID")
        if want:
            for c in used_ctx[:12]:
  ```
- Line 202: `EVAL_DRIVER`
  ```python
  """Create evaluation driver based on environment configuration."""
    use_real = (
        os.getenv("EVAL_DRIVER", "").lower() in ("dspy_rag", "dspy", "rag")
        or os.getenv("RAGCHECKER_USE_REAL_RAG") == "1"
    )
  ```
- Line 203: `RAGCHECKER_USE_REAL_RAG`
  ```python
  use_real = (
        os.getenv("EVAL_DRIVER", "").lower() in ("dspy_rag", "dspy", "rag")
        or os.getenv("RAGCHECKER_USE_REAL_RAG") == "1"
    )
    if use_real:
  ```
- Line 235: `RAGCHECKER_PROGRESS_LOG`
  ```python
  """Write progress record to JSONL."""
        if not getattr(self, "_progress_fh", None):
            p = os.getenv("RAGCHECKER_PROGRESS_LOG")
            if p:
                self._progress_open(p)
  ```
- Line 283: `ORACLE_CTX_J_MIN`
  ```python
  def _compute_oracle_from_payload(self, case: dict) -> dict:
        """Compute oracle metrics from case payload."""
        j_ctx_min = float(os.getenv("ORACLE_CTX_J_MIN", "0.28"))
        j_sent_min = float(os.getenv("ORACLE_SENT_J_MIN", "0.32"))
        gt = self._tok(case.get("gt_answer", ""))
  ```
- Line 284: `ORACLE_SENT_J_MIN`
  ```python
  """Compute oracle metrics from case payload."""
        j_ctx_min = float(os.getenv("ORACLE_CTX_J_MIN", "0.28"))
        j_sent_min = float(os.getenv("ORACLE_SENT_J_MIN", "0.32"))
        gt = self._tok(case.get("gt_answer", ""))
        ctx_strings = self._extract_ctx_strings(case.get("retrieved_context", []))
  ```
- Line 449: `DSPY_RAG_PATH`
  ```python
  "eval_driver": getattr(self, "_eval_path_tag", "unknown"),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dspy_rag_path": os.getenv("DSPY_RAG_PATH", "src"),
            "fusion_enabled": os.getenv("RERANK_ENABLE", "1") == "1",
            "retrieval_topk_vec": int(os.getenv("RETR_TOPK_VEC", "140")),
  ```
- Line 450: `RERANK_ENABLE`
  ```python
  "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dspy_rag_path": os.getenv("DSPY_RAG_PATH", "src"),
            "fusion_enabled": os.getenv("RERANK_ENABLE", "1") == "1",
            "retrieval_topk_vec": int(os.getenv("RETR_TOPK_VEC", "140")),
            "retrieval_topk_bm25": int(os.getenv("RETR_TOPK_BM25", "140")),
  ```
- Line 451: `RETR_TOPK_VEC`
  ```python
  "dspy_rag_path": os.getenv("DSPY_RAG_PATH", "src"),
            "fusion_enabled": os.getenv("RERANK_ENABLE", "1") == "1",
            "retrieval_topk_vec": int(os.getenv("RETR_TOPK_VEC", "140")),
            "retrieval_topk_bm25": int(os.getenv("RETR_TOPK_BM25", "140")),
        }
  ```
- Line 452: `RETR_TOPK_BM25`
  ```python
  "fusion_enabled": os.getenv("RERANK_ENABLE", "1") == "1",
            "retrieval_topk_vec": int(os.getenv("RETR_TOPK_VEC", "140")),
            "retrieval_topk_bm25": int(os.getenv("RETR_TOPK_BM25", "140")),
        }
  ```
- Line 514: `EVAL_DRIVER`
  ```python
  # Hard gate: Stop synthetic fallback if real RAG is requested
        use_real = (
            os.getenv("EVAL_DRIVER", "").lower() in ("dspy_rag", "dspy", "rag")
            or os.getenv("RAGCHECKER_USE_REAL_RAG") == "1"
        )
  ```
- Line 515: `RAGCHECKER_USE_REAL_RAG`
  ```python
  use_real = (
            os.getenv("EVAL_DRIVER", "").lower() in ("dspy_rag", "dspy", "rag")
            or os.getenv("RAGCHECKER_USE_REAL_RAG") == "1"
        )
        if use_real and tag != "dspy_rag":
  ```
- Line 527: `RAGCHECKER_PROGRESS_LOG`
  ```python
  # Open progress logging if enabled
        progress_log = os.getenv("RAGCHECKER_PROGRESS_LOG")
        if progress_log:
            self._progress_open(progress_log)
  ```
- Line 539: `GOLD_FILE`
  ```python
  from src.utils.gold_loader import filter_cases, load_gold_cases, stratified_sample

            gold_file = os.getenv("GOLD_FILE", getattr(args, "gold_file", "evals/gold/v1/gold_cases.jsonl"))
            gold_profile = os.getenv("GOLD_PROFILE", getattr(args, "gold_profile", None))
            gold_tags = os.getenv("GOLD_TAGS", getattr(args, "gold_tags", None))
  ```
- Line 540: `GOLD_PROFILE`
  ```python
  gold_file = os.getenv("GOLD_FILE", getattr(args, "gold_file", "evals/gold/v1/gold_cases.jsonl"))
            gold_profile = os.getenv("GOLD_PROFILE", getattr(args, "gold_profile", None))
            gold_tags = os.getenv("GOLD_TAGS", getattr(args, "gold_tags", None))
            gold_mode = os.getenv("GOLD_MODE", getattr(args, "gold_mode", None))
  ```
- Line 541: `GOLD_TAGS`
  ```python
  gold_file = os.getenv("GOLD_FILE", getattr(args, "gold_file", "evals/gold/v1/gold_cases.jsonl"))
            gold_profile = os.getenv("GOLD_PROFILE", getattr(args, "gold_profile", None))
            gold_tags = os.getenv("GOLD_TAGS", getattr(args, "gold_tags", None))
            gold_mode = os.getenv("GOLD_MODE", getattr(args, "gold_mode", None))
            gold_size = int(os.getenv("GOLD_SIZE", str(getattr(args, "gold_size", 0) or 0)) or 0) or None
  ```
- Line 542: `GOLD_MODE`
  ```python
  gold_profile = os.getenv("GOLD_PROFILE", getattr(args, "gold_profile", None))
            gold_tags = os.getenv("GOLD_TAGS", getattr(args, "gold_tags", None))
            gold_mode = os.getenv("GOLD_MODE", getattr(args, "gold_mode", None))
            gold_size = int(os.getenv("GOLD_SIZE", str(getattr(args, "gold_size", 0) or 0)) or 0) or None
            seed = int(os.getenv("SEED", str(getattr(args, "seed", 1337))))
  ```
- Line 543: `GOLD_SIZE`
  ```python
  gold_tags = os.getenv("GOLD_TAGS", getattr(args, "gold_tags", None))
            gold_mode = os.getenv("GOLD_MODE", getattr(args, "gold_mode", None))
            gold_size = int(os.getenv("GOLD_SIZE", str(getattr(args, "gold_size", 0) or 0)) or 0) or None
            seed = int(os.getenv("SEED", str(getattr(args, "seed", 1337))))
  ```
- Line 544: `SEED`
  ```python
  gold_mode = os.getenv("GOLD_MODE", getattr(args, "gold_mode", None))
            gold_size = int(os.getenv("GOLD_SIZE", str(getattr(args, "gold_size", 0) or 0)) or 0) or None
            seed = int(os.getenv("SEED", str(getattr(args, "seed", 1337))))

            cases = load_gold_cases(gold_file)
  ```
- Line 761: `EVAL_CONCURRENCY`
  ```python
  # Concurrency default from env; your executor can read this
    os.environ.setdefault("EVAL_CONCURRENCY", resolved.get("EVAL_CONCURRENCY", "3"))
    concurrency = int(os.environ["EVAL_CONCURRENCY"])
    print(f"▶ Using concurrency={concurrency}")
  ```
- Line 805: `EVAL_DRIVER`
  ```python
  f"{datetime.now():%Y%m%d_%H%M%S}"
        f"__{profile}"
        f"__driver-{os.environ.get('EVAL_DRIVER', '?')}"
        f"__f1-{f1_micro:.3f}__p-{precision_micro:.3f}__r-{recall_micro:.3f}"
    )
  ```
- Line 818: `EVAL_DRIVER`
  ```python
  "scores": {"micro": {"f1": f1_micro, "precision": precision_micro, "recall": recall_micro}},
        "env": {
            "EVAL_DRIVER": os.environ.get("EVAL_DRIVER"),
            "RAGCHECKER_USE_REAL_RAG": os.environ.get("RAGCHECKER_USE_REAL_RAG"),
            "POSTGRES_DSN": os.environ.get("POSTGRES_DSN", "<unset>")[:32] + "…",  # redact
  ```
- Line 819: `RAGCHECKER_USE_REAL_RAG`
  ```python
  "env": {
            "EVAL_DRIVER": os.environ.get("EVAL_DRIVER"),
            "RAGCHECKER_USE_REAL_RAG": os.environ.get("RAGCHECKER_USE_REAL_RAG"),
            "POSTGRES_DSN": os.environ.get("POSTGRES_DSN", "<unset>")[:32] + "…",  # redact
            "EVAL_CONCURRENCY": os.environ.get("EVAL_CONCURRENCY"),
  ```
- Line 820: `POSTGRES_DSN`
  ```python
  "EVAL_DRIVER": os.environ.get("EVAL_DRIVER"),
            "RAGCHECKER_USE_REAL_RAG": os.environ.get("RAGCHECKER_USE_REAL_RAG"),
            "POSTGRES_DSN": os.environ.get("POSTGRES_DSN", "<unset>")[:32] + "…",  # redact
            "EVAL_CONCURRENCY": os.environ.get("EVAL_CONCURRENCY"),
        },
  ```
- Line 821: `EVAL_CONCURRENCY`
  ```python
  "RAGCHECKER_USE_REAL_RAG": os.environ.get("RAGCHECKER_USE_REAL_RAG"),
            "POSTGRES_DSN": os.environ.get("POSTGRES_DSN", "<unset>")[:32] + "…",  # redact
            "EVAL_CONCURRENCY": os.environ.get("EVAL_CONCURRENCY"),
        },
        "timestamp": datetime.now().isoformat(),
  ```

### scripts/audit_gold_spans.py
- Line 21: `CASES_FILE`
  ```python
  from dspy_modules.retriever.rerank import mmr_rerank, per_file_cap

CASES = os.getenv("CASES_FILE", "evals/gold_cases.json")
GOLD = os.getenv("READER_GOLD_FILE", "evals/reader_gold_comprehensive.jsonl")
  ```
- Line 22: `READER_GOLD_FILE`
  ```python
  CASES = os.getenv("CASES_FILE", "evals/gold_cases.json")
GOLD = os.getenv("READER_GOLD_FILE", "evals/reader_gold_comprehensive.jsonl")
  ```

### scripts/backfill_embeddings.py
- Line 11: `POSTGRES_DSN`
  ```python
  from sentence_transformers import SentenceTransformer

DSN = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
MODEL_NAME = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")  # 384-dim, fast, great for code+docs
BATCH = int(os.getenv("EMBED_BATCH", "64"))
  ```
- Line 12: `EMBED_MODEL`
  ```python
  DSN = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
MODEL_NAME = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")  # 384-dim, fast, great for code+docs
BATCH = int(os.getenv("EMBED_BATCH", "64"))
  ```
- Line 13: `EMBED_BATCH`
  ```python
  DSN = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
MODEL_NAME = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")  # 384-dim, fast, great for code+docs
BATCH = int(os.getenv("EMBED_BATCH", "64"))
  ```

### scripts/backfill_section_titles.py
- Line 70: `POSTGRES_DSN`
  ```python
  def main() -> int:
    dsn = os.environ.get("POSTGRES_DSN")
    if not dsn:
        print("❌ POSTGRES_DSN not set", file=sys.stderr)
  ```

### scripts/backup_system.py
- Line 48: `USER`
  ```python
  "timestamp": self.timestamp,
            "description": description,
            "created_by": os.getenv("USER", "unknown"),
            "hostname": os.getenv("HOSTNAME", "unknown"),
            "tables_backed_up": [],
  ```
- Line 49: `HOSTNAME`
  ```python
  "description": description,
            "created_by": os.getenv("USER", "unknown"),
            "hostname": os.getenv("HOSTNAME", "unknown"),
            "tables_backed_up": [],
            "backup_files": [],
  ```

### scripts/baseline_version_manager.py
- Line 52: `BEDROCK_MODEL_ID`
  ```python
  # Get current environment settings
    bedrock_model = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    max_rps = os.getenv("BEDROCK_MAX_RPS", "0.15")
  ```
- Line 53: `AWS_REGION`
  ```python
  # Get current environment settings
    bedrock_model = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    max_rps = os.getenv("BEDROCK_MAX_RPS", "0.15")
  ```
- Line 54: `BEDROCK_MAX_RPS`
  ```python
  bedrock_model = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    max_rps = os.getenv("BEDROCK_MAX_RPS", "0.15")

    milestone_content = f"""# 🎯 NEW BASELINE MILESTONE: {timestamp}
  ```
- Line 120: `BEDROCK_MODEL_ID`
  ```python
  locked_file = Path(f"metrics/baseline_evaluations/BASELINE_LOCKED_{timestamp}.md")

    bedrock_model = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    max_rps = os.getenv("BEDROCK_MAX_RPS", "0.15")
  ```
- Line 121: `AWS_REGION`
  ```python
  bedrock_model = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    max_rps = os.getenv("BEDROCK_MAX_RPS", "0.15")
  ```
- Line 122: `BEDROCK_MAX_RPS`
  ```python
  bedrock_model = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    max_rps = os.getenv("BEDROCK_MAX_RPS", "0.15")

    locked_content = f"""# 🔒 BASELINE LOCKED: {timestamp}
  ```
- Line 138: `BEDROCK_COOLDOWN_SEC`
  ```python
  **Rate Limit**: `{max_rps} RPS`
**Concurrency**: `1`
**Cooldown**: `{os.getenv("BEDROCK_COOLDOWN_SEC", "30")}s`

## 📊 **Baseline Results**
  ```

### scripts/bedrock_client.py
- Line 309: `BEDROCK_OUTER_RETRIES`
  ```python
  import random

        outer_retries = int(os.getenv("BEDROCK_OUTER_RETRIES", "6"))
        base = float(os.getenv("BEDROCK_RETRY_BASE", "1.6"))
        max_sleep = float(os.getenv("BEDROCK_RETRY_MAX_SLEEP", "14"))
  ```
- Line 310: `BEDROCK_RETRY_BASE`
  ```python
  outer_retries = int(os.getenv("BEDROCK_OUTER_RETRIES", "6"))
        base = float(os.getenv("BEDROCK_RETRY_BASE", "1.6"))
        max_sleep = float(os.getenv("BEDROCK_RETRY_MAX_SLEEP", "14"))
  ```
- Line 311: `BEDROCK_RETRY_MAX_SLEEP`
  ```python
  outer_retries = int(os.getenv("BEDROCK_OUTER_RETRIES", "6"))
        base = float(os.getenv("BEDROCK_RETRY_BASE", "1.6"))
        max_sleep = float(os.getenv("BEDROCK_RETRY_MAX_SLEEP", "14"))

        last_err = None
  ```

### scripts/bedrock_openai_shim.py
- Line 30: `BEDROCK_MAX_RPS`
  ```python
  # Initialize rate limiter with conservative defaults
rate_limiter = RateLimiter(float(os.getenv("BEDROCK_MAX_RPS", "0.22")))

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")
  ```
- Line 32: `BEDROCK_MODEL_ID`
  ```python
  rate_limiter = RateLimiter(float(os.getenv("BEDROCK_MAX_RPS", "0.22")))

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")
REGION = os.getenv("AWS_REGION", "us-east-1")
brt = boto3.client("bedrock-runtime", region_name=REGION)
  ```
- Line 33: `AWS_REGION`
  ```python
  MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")
REGION = os.getenv("AWS_REGION", "us-east-1")
brt = boto3.client("bedrock-runtime", region_name=REGION)
  ```
- Line 100: `PORT`
  ```python
  if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", "8089")))
  ```

### scripts/bedrock_setup_guide.py
- Line 191: `AWS_ACCESS_KEY_ID`
  ```python
  # Check if credentials exist
    has_credentials = (
        os.environ.get("AWS_ACCESS_KEY_ID")
        or os.environ.get("AWS_PROFILE")
        or (Path.home() / ".aws" / "credentials").exists()
  ```
- Line 192: `AWS_PROFILE`
  ```python
  has_credentials = (
        os.environ.get("AWS_ACCESS_KEY_ID")
        or os.environ.get("AWS_PROFILE")
        or (Path.home() / ".aws" / "credentials").exists()
    )
  ```

### scripts/cache_invalidation_system.py
- Line 35: `POSTGRES_DSN`
  ```python
  # Database configuration - simplified for this script
def get_database_url():
    return os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
  ```

### scripts/calibrate_answerable_threshold.py
- Line 101: `CASES_FILE`
  ```python
  def main():
    # Load dev cases
    cases_file = os.getenv("CASES_FILE", "evals/gold_cases.json")
    gold_file = os.getenv("READER_GOLD_FILE", "evals/reader_gold_comprehensive.jsonl")
  ```
- Line 102: `READER_GOLD_FILE`
  ```python
  # Load dev cases
    cases_file = os.getenv("CASES_FILE", "evals/gold_cases.json")
    gold_file = os.getenv("READER_GOLD_FILE", "evals/reader_gold_comprehensive.jsonl")

    cases = json.load(open(cases_file, encoding="utf-8"))
  ```

### scripts/ci_evaluation_pipeline.py
- Line 21: `POSTGRES_DSN`
  ```python
  # Set database connection
    os.environ["POSTGRES_DSN"] = "postgresql://danieljacobs@localhost:5432/ai_agency?sslmode=disable"

    # Ensure virtual environment is active
  ```
- Line 24: `VIRTUAL_ENV`
  ```python
  # Ensure virtual environment is active
    if not os.environ.get("VIRTUAL_ENV"):
        print("⚠️ Virtual environment not detected, attempting to activate...")
        venv_path = Path(".venv")
  ```
- Line 138: `VIRTUAL_ENV`
  ```python
  "environment": {
            "python_version": sys.version,
            "virtual_env": os.environ.get("VIRTUAL_ENV"),
            "postgres_dsn_set": bool(os.environ.get("POSTGRES_DSN")),
        },
  ```
- Line 139: `POSTGRES_DSN`
  ```python
  "python_version": sys.version,
            "virtual_env": os.environ.get("VIRTUAL_ENV"),
            "postgres_dsn_set": bool(os.environ.get("POSTGRES_DSN")),
        },
        "results": results,
  ```

### scripts/ci_gate_reader.py
- Line 22: `READER_GOLD_FILE`
  ```python
  from evals.load_cases import load_eval_cases

READER_GOLD = os.getenv("READER_GOLD_FILE", "evals/reader_gold.jsonl")
READER_ID_MAP = os.getenv("READER_ID_MAP")  # optional mapping of old_id -> new_id during migration
# Default to the new extractive reader CLI if not provided
  ```
- Line 23: `READER_ID_MAP`
  ```python
  READER_GOLD = os.getenv("READER_GOLD_FILE", "evals/reader_gold.jsonl")
READER_ID_MAP = os.getenv("READER_ID_MAP")  # optional mapping of old_id -> new_id during migration
# Default to the new extractive reader CLI if not provided
# You can still override via: export READER_CMD="python3 scripts/run_dspy_reader.py" (or custom)
  ```
- Line 26: `READER_CMD`
  ```python
  # Default to the new extractive reader CLI if not provided
# You can still override via: export READER_CMD="python3 scripts/run_dspy_reader.py" (or custom)
READER_CMD = os.getenv("READER_CMD", "python3 scripts/run_extractive_reader.py")
ALPHA = float(os.getenv("MMR_ALPHA", "0.85"))
PER_FILE_CAP = int(os.getenv("PER_FILE_CAP", "5"))
  ```
- Line 27: `MMR_ALPHA`
  ```python
  # You can still override via: export READER_CMD="python3 scripts/run_dspy_reader.py" (or custom)
READER_CMD = os.getenv("READER_CMD", "python3 scripts/run_extractive_reader.py")
ALPHA = float(os.getenv("MMR_ALPHA", "0.85"))
PER_FILE_CAP = int(os.getenv("PER_FILE_CAP", "5"))
  ```
- Line 28: `PER_FILE_CAP`
  ```python
  READER_CMD = os.getenv("READER_CMD", "python3 scripts/run_extractive_reader.py")
ALPHA = float(os.getenv("MMR_ALPHA", "0.85"))
PER_FILE_CAP = int(os.getenv("PER_FILE_CAP", "5"))

MIN_F1_MICRO = float(os.getenv("READER_MIN_F1_MICRO", "0.35"))
  ```
- Line 30: `READER_MIN_F1_MICRO`
  ```python
  PER_FILE_CAP = int(os.getenv("PER_FILE_CAP", "5"))

MIN_F1_MICRO = float(os.getenv("READER_MIN_F1_MICRO", "0.35"))
MIN_F1_TAG = float(os.getenv("READER_MIN_F1_TAG", "0.25"))
MAX_REG_DROP = float(os.getenv("MAX_READER_REG_DROP", "0.05"))
  ```
- Line 31: `READER_MIN_F1_TAG`
  ```python
  MIN_F1_MICRO = float(os.getenv("READER_MIN_F1_MICRO", "0.35"))
MIN_F1_TAG = float(os.getenv("READER_MIN_F1_TAG", "0.25"))
MAX_REG_DROP = float(os.getenv("MAX_READER_REG_DROP", "0.05"))
FAIL_ON_MISSING = bool(int(os.getenv("READER_FAIL_ON_MISSING_ID", "1")))
  ```
- Line 32: `MAX_READER_REG_DROP`
  ```python
  MIN_F1_MICRO = float(os.getenv("READER_MIN_F1_MICRO", "0.35"))
MIN_F1_TAG = float(os.getenv("READER_MIN_F1_TAG", "0.25"))
MAX_REG_DROP = float(os.getenv("MAX_READER_REG_DROP", "0.05"))
FAIL_ON_MISSING = bool(int(os.getenv("READER_FAIL_ON_MISSING_ID", "1")))
  ```
- Line 33: `READER_FAIL_ON_MISSING_ID`
  ```python
  MIN_F1_TAG = float(os.getenv("READER_MIN_F1_TAG", "0.25"))
MAX_REG_DROP = float(os.getenv("MAX_READER_REG_DROP", "0.05"))
FAIL_ON_MISSING = bool(int(os.getenv("READER_FAIL_ON_MISSING_ID", "1")))

BASELINE_FILE = os.getenv("READER_BASELINE_FILE", "evals/baseline_reader_metrics.json")
  ```
- Line 35: `READER_BASELINE_FILE`
  ```python
  FAIL_ON_MISSING = bool(int(os.getenv("READER_FAIL_ON_MISSING_ID", "1")))

BASELINE_FILE = os.getenv("READER_BASELINE_FILE", "evals/baseline_reader_metrics.json")
OUT_FILE = os.getenv("LATEST_READER_FILE", "evals/latest_reader_metrics.json")
  ```
- Line 36: `LATEST_READER_FILE`
  ```python
  BASELINE_FILE = os.getenv("READER_BASELINE_FILE", "evals/baseline_reader_metrics.json")
OUT_FILE = os.getenv("LATEST_READER_FILE", "evals/latest_reader_metrics.json")
  ```
- Line 147: `READER_COMPACT`
  ```python
  rows = per_file_cap(rows, cap=PER_FILE_CAP)[: lim["topk"]]
        context, _meta = build_reader_context(
            rows, case.query, case.tag, compact=bool(int(os.getenv("READER_COMPACT", "1")))
        )
        pred = run_reader_cmd(case.query, context, case.tag, case.id)
  ```

### scripts/ci_gate_retrieval.py
- Line 18: `PREFILTER_MIN_MICRO`
  ```python
  from evals.load_cases import load_eval_cases

PREFILTER_MIN_MICRO = float(os.getenv("PREFILTER_MIN_MICRO", "0.85"))
PREFILTER_MIN_TAG = float(os.getenv("PREFILTER_MIN_TAG", "0.75"))
MAX_REG_DROP = float(os.getenv("MAX_REG_DROP", "0.05"))
  ```
- Line 19: `PREFILTER_MIN_TAG`
  ```python
  PREFILTER_MIN_MICRO = float(os.getenv("PREFILTER_MIN_MICRO", "0.85"))
PREFILTER_MIN_TAG = float(os.getenv("PREFILTER_MIN_TAG", "0.75"))
MAX_REG_DROP = float(os.getenv("MAX_REG_DROP", "0.05"))
K_CAP = int(os.getenv("PER_FILE_CAP", "5"))
  ```
- Line 20: `MAX_REG_DROP`
  ```python
  PREFILTER_MIN_MICRO = float(os.getenv("PREFILTER_MIN_MICRO", "0.85"))
PREFILTER_MIN_TAG = float(os.getenv("PREFILTER_MIN_TAG", "0.75"))
MAX_REG_DROP = float(os.getenv("MAX_REG_DROP", "0.05"))
K_CAP = int(os.getenv("PER_FILE_CAP", "5"))
ALPHA = float(os.getenv("MMR_ALPHA", "0.85"))
  ```
- Line 21: `PER_FILE_CAP`
  ```python
  PREFILTER_MIN_TAG = float(os.getenv("PREFILTER_MIN_TAG", "0.75"))
MAX_REG_DROP = float(os.getenv("MAX_REG_DROP", "0.05"))
K_CAP = int(os.getenv("PER_FILE_CAP", "5"))
ALPHA = float(os.getenv("MMR_ALPHA", "0.85"))
  ```
- Line 22: `MMR_ALPHA`
  ```python
  MAX_REG_DROP = float(os.getenv("MAX_REG_DROP", "0.05"))
K_CAP = int(os.getenv("PER_FILE_CAP", "5"))
ALPHA = float(os.getenv("MMR_ALPHA", "0.85"))

BASELINE_FILE = os.getenv("BASELINE_METRICS_FILE", "evals/baseline_metrics.json")
  ```
- Line 24: `BASELINE_METRICS_FILE`
  ```python
  ALPHA = float(os.getenv("MMR_ALPHA", "0.85"))

BASELINE_FILE = os.getenv("BASELINE_METRICS_FILE", "evals/baseline_metrics.json")
OUT_FILE = os.getenv("LATEST_METRICS_FILE", "evals/latest_retrieval_metrics.json")
  ```
- Line 25: `LATEST_METRICS_FILE`
  ```python
  BASELINE_FILE = os.getenv("BASELINE_METRICS_FILE", "evals/baseline_metrics.json")
OUT_FILE = os.getenv("LATEST_METRICS_FILE", "evals/latest_retrieval_metrics.json")
  ```
- Line 63: `CASES_FILE`
  ```python
  if __name__ == "__main__":
    cases_file = os.getenv("CASES_FILE", "evals/gold_cases.json")
    dataset = os.path.splitext(os.path.basename(cases_file))[0].replace("_cases", "")
    cases = load_eval_cases(dataset)
  ```

### scripts/comprehensive_system_monitor.py
- Line 274: `DATABASE_URL`
  ```python
  def __init__(self):
        self.db_monitor = DatabaseHealthMonitor(
            os.getenv("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency")
        )
        self.pipeline_monitor = PipelinePerformanceMonitor()
  ```

### scripts/convert_eval_gold_to_jsonl.py
- Line 34: `GOLD_FILE`
  ```python
  merged.update(GOLD)
    merged.update(ADDITIONAL_GOLD)
    out_path = os.getenv("GOLD_FILE", str(ROOT / "evals" / "gold.jsonl"))
    pathlib.Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
  ```

### scripts/create_launchd_maintenance.py
- Line 35: `PATH`
  ```python
  "KeepAlive": False,
        "EnvironmentVariables": {
            "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
            "PYTHONUNBUFFERED": "1",
        },
  ```

### scripts/cross_encoder_reranker.py
- Line 30: `RAGCHECKER_CROSS_ENCODER_TOP_N`
  ```python
  # Configuration from environment (support both legacy and CE_* names)
        top_n_str = os.getenv("RAGCHECKER_CROSS_ENCODER_TOP_N") or os.getenv("RAGCHECKER_CE_RERANK_TOPN") or "50"
        weight_str = os.getenv("RAGCHECKER_CROSS_ENCODER_WEIGHT") or os.getenv("RAGCHECKER_CE_WEIGHT") or "0.15"
        self.top_n = int(top_n_str)
  ```
- Line 30: `RAGCHECKER_CE_RERANK_TOPN`
  ```python
  # Configuration from environment (support both legacy and CE_* names)
        top_n_str = os.getenv("RAGCHECKER_CROSS_ENCODER_TOP_N") or os.getenv("RAGCHECKER_CE_RERANK_TOPN") or "50"
        weight_str = os.getenv("RAGCHECKER_CROSS_ENCODER_WEIGHT") or os.getenv("RAGCHECKER_CE_WEIGHT") or "0.15"
        self.top_n = int(top_n_str)
  ```
- Line 31: `RAGCHECKER_CROSS_ENCODER_WEIGHT`
  ```python
  # Configuration from environment (support both legacy and CE_* names)
        top_n_str = os.getenv("RAGCHECKER_CROSS_ENCODER_TOP_N") or os.getenv("RAGCHECKER_CE_RERANK_TOPN") or "50"
        weight_str = os.getenv("RAGCHECKER_CROSS_ENCODER_WEIGHT") or os.getenv("RAGCHECKER_CE_WEIGHT") or "0.15"
        self.top_n = int(top_n_str)
        self.weight = float(weight_str)
  ```
- Line 31: `RAGCHECKER_CE_WEIGHT`
  ```python
  # Configuration from environment (support both legacy and CE_* names)
        top_n_str = os.getenv("RAGCHECKER_CROSS_ENCODER_TOP_N") or os.getenv("RAGCHECKER_CE_RERANK_TOPN") or "50"
        weight_str = os.getenv("RAGCHECKER_CROSS_ENCODER_WEIGHT") or os.getenv("RAGCHECKER_CE_WEIGHT") or "0.15"
        self.top_n = int(top_n_str)
        self.weight = float(weight_str)
  ```
- Line 34: `RAGCHECKER_CROSS_ENCODER_CACHE`
  ```python
  self.top_n = int(top_n_str)
        self.weight = float(weight_str)
        self.cache_enabled = os.getenv("RAGCHECKER_CROSS_ENCODER_CACHE", "1") == "1"

        # Initialize model if enabled (accept either env flag)
  ```
- Line 37: `RAGCHECKER_CROSS_ENCODER_ENABLED`
  ```python
  # Initialize model if enabled (accept either env flag)
        enabled_flag = os.getenv("RAGCHECKER_CROSS_ENCODER_ENABLED", "0")
        enabled_alias = os.getenv("RAGCHECKER_CE_RERANK_ENABLE", "0")
        if enabled_flag == "1" or enabled_alias == "1":
  ```
- Line 38: `RAGCHECKER_CE_RERANK_ENABLE`
  ```python
  # Initialize model if enabled (accept either env flag)
        enabled_flag = os.getenv("RAGCHECKER_CROSS_ENCODER_ENABLED", "0")
        enabled_alias = os.getenv("RAGCHECKER_CE_RERANK_ENABLE", "0")
        if enabled_flag == "1" or enabled_alias == "1":
            self._initialize_model()
  ```
- Line 215: `RAGCHECKER_EVIDENCE_JACCARD`
  ```python
  # Apply threshold
        threshold = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07"))
        return combined_score >= threshold
  ```
- Line 257: `RAGCHECKER_CROSS_ENCODER_ENABLED`
  ```python
  # Enable cross-encoder
    os.environ["RAGCHECKER_CROSS_ENCODER_ENABLED"] = "1"

    reranker = CrossEncoderReranker()
  ```

### scripts/cursor_ai_integration_framework.py
- Line 425: `DEFAULT_ACTIVE_AGENT`
  ```python
  # Set native AI as default
        default_agent = os.getenv("DEFAULT_ACTIVE_AGENT", AgentType.NATIVE_AI.value)
        try:
            parsed = AgentType(default_agent)
  ```

### scripts/cursor_memory_rehydrate.py
- Line 134: `REHYDRATE_STABILITY`
  ```python
  "--stability",
        type=float,
        default=float(os.getenv("REHYDRATE_STABILITY", "0.6")),
        help="Stability knob (0.0-1.0, default 0.6)",
    )
  ```
- Line 141: `REHYDRATE_DEDUPE`
  ```python
  "--dedupe",
        choices=["file", "file+overlap"],
        default=os.getenv("REHYDRATE_DEDUPE", "file+overlap"),
        help="Deduplication mode (default: file+overlap)",
    )
  ```
- Line 147: `REHYDRATE_EXPAND_QUERY`
  ```python
  "--expand-query",
        choices=["off", "auto"],
        default=os.getenv("REHYDRATE_EXPAND_QUERY", "auto"),
        help="Query expansion mode (default: auto)",
    )
  ```

### scripts/day0_sanity_checklist.py
- Line 88: `POSTGRES_DSN`
  ```python
  # Check for least-privilege DB user
        postgres_dsn = os.getenv("POSTGRES_DSN", "")
        is_least_priv = "eval_user" in postgres_dsn or "readonly" in postgres_dsn
  ```
- Line 103: `INGEST_RUN_ID`
  ```python
  def _check_active_pointer(self) -> Dict[str, Any]:
        """Check active pointer / run-id logging."""
        ingest_run_id = os.getenv("INGEST_RUN_ID")
        config_hash = os.getenv("CONFIG_HASH")
  ```
- Line 104: `CONFIG_HASH`
  ```python
  """Check active pointer / run-id logging."""
        ingest_run_id = os.getenv("INGEST_RUN_ID")
        config_hash = os.getenv("CONFIG_HASH")

        # Check if active pointer file exists
  ```
- Line 126: `EVAL_DISABLE_CACHE`
  ```python
  def _check_cache_stance(self) -> Dict[str, Any]:
        """Check cache stance configuration."""
        eval_disable_cache = os.getenv("EVAL_DISABLE_CACHE", "0")
        cache_enabled_prod = os.getenv("CACHE_ENABLED_PROD", "1")
  ```
- Line 127: `CACHE_ENABLED_PROD`
  ```python
  """Check cache stance configuration."""
        eval_disable_cache = os.getenv("EVAL_DISABLE_CACHE", "0")
        cache_enabled_prod = os.getenv("CACHE_ENABLED_PROD", "1")

        # Eval cache should be disabled
  ```
- Line 145: `RERANKER_PREWARM`
  ```python
  def _check_reranker_prewarm(self) -> Dict[str, Any]:
        """Check reranker prewarm configuration."""
        reranker_prewarm = os.getenv("RERANKER_PREWARM", "0")
        reranker_model = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")
  ```
- Line 146: `RERANK_MODEL`
  ```python
  """Check reranker prewarm configuration."""
        reranker_prewarm = os.getenv("RERANKER_PREWARM", "0")
        reranker_model = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")

        # Check if prewarm is enabled
  ```
- Line 165: `DEPLOY_DISABLE_NEW_CONFIG`
  ```python
  def _check_kill_switch(self) -> Dict[str, Any]:
        """Check kill switch configuration."""
        deploy_disable = os.getenv("DEPLOY_DISABLE_NEW_CONFIG", "0")
        kill_switch_doc = Path("docs/kill_switch.md")
  ```

### scripts/db_smoke_check.py
- Line 52: `DATABASE_URL`
  ```python
  def ensure_setup() -> None:
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        print("[WARN] DATABASE_URL not set; using pool env. Make sure db_pool can resolve.")
  ```

### scripts/documentation_indexer.py
- Line 525: `DATABASE_URL`
  ```python
  else:
        # Try to get from environment or use default
        db_url = os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")

    # Initialize indexer
  ```

### scripts/documentation_retrieval_cli.py
- Line 45: `DATABASE_URL`
  ```python
  def __init__(self, db_connection_string: str = None):
        if db_connection_string is None:
            db_connection_string = os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")

        self.db_conn_str = db_connection_string
  ```
- Line 314: `DATABASE_URL`
  ```python
  # Initialize CLI
    db_url = args.db_url or os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")
    cli = DocumentationRetrievalCLI(db_url)
  ```

### scripts/drift_detector.py
- Line 12: `MAX_RETR_WEEKLY_DRIFT`
  ```python
  READ_BASE = "evals/baseline_reader_metrics.json"

MAX_RETR_DRIFT = float(os.getenv("MAX_RETR_WEEKLY_DRIFT", "0.02"))
MAX_READ_DRIFT = float(os.getenv("MAX_READ_WEEKLY_DRIFT", "0.03"))
  ```
- Line 13: `MAX_READ_WEEKLY_DRIFT`
  ```python
  MAX_RETR_DRIFT = float(os.getenv("MAX_RETR_WEEKLY_DRIFT", "0.02"))
MAX_READ_DRIFT = float(os.getenv("MAX_READ_WEEKLY_DRIFT", "0.03"))
  ```

### scripts/end_to_end_system_validation.py
- Line 512: `DATABASE_URL`
  ```python
  def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency")
        self.validators = {
            "database": DatabaseLayerValidator(self.database_url),
  ```

### scripts/enhanced_bedrock_client.py
- Line 327: `BEDROCK_MODEL_ID`
  ```python
  """
        # Model ID override from environment
        self.model_id = os.getenv("BEDROCK_MODEL_ID", model_id)
        self.max_retries = max_retries
        self.timeout = timeout
  ```
- Line 330: `BEDROCK_CONNECT_TIMEOUT`
  ```python
  self.max_retries = max_retries
        self.timeout = timeout
        self.connect_timeout = int(os.getenv("BEDROCK_CONNECT_TIMEOUT", "30"))
        self.usage_log_file = usage_log_file or "metrics/enhanced_bedrock_usage.json"
  ```
- Line 352: `BEDROCK_BASE_RPS`
  ```python
  self.load_balancer = MultiKeyLoadBalancer(api_keys)
        self.rate_limiter = AdaptiveRateLimiter(
            base_rps=float(os.getenv("BEDROCK_BASE_RPS", "0.5")), max_rps=float(os.getenv("BEDROCK_MAX_RPS", "2.0"))
        )
  ```
- Line 352: `BEDROCK_MAX_RPS`
  ```python
  self.load_balancer = MultiKeyLoadBalancer(api_keys)
        self.rate_limiter = AdaptiveRateLimiter(
            base_rps=float(os.getenv("BEDROCK_BASE_RPS", "0.5")), max_rps=float(os.getenv("BEDROCK_MAX_RPS", "2.0"))
        )
  ```
- Line 392: `AWS_ACCESS_KEY_ID`
  ```python
  if not api_keys:
            # Fallback to single key
            primary_key = os.getenv("AWS_ACCESS_KEY_ID", "")
            primary_secret = os.getenv("AWS_SECRET_ACCESS_KEY", "")
            primary_region = os.getenv("AWS_REGION", "us-east-1")
  ```
- Line 393: `AWS_SECRET_ACCESS_KEY`
  ```python
  # Fallback to single key
            primary_key = os.getenv("AWS_ACCESS_KEY_ID", "")
            primary_secret = os.getenv("AWS_SECRET_ACCESS_KEY", "")
            primary_region = os.getenv("AWS_REGION", "us-east-1")
  ```
- Line 394: `AWS_REGION`
  ```python
  primary_key = os.getenv("AWS_ACCESS_KEY_ID", "")
            primary_secret = os.getenv("AWS_SECRET_ACCESS_KEY", "")
            primary_region = os.getenv("AWS_REGION", "us-east-1")

            if primary_key and primary_secret and primary_key != "your_primary_access_key_here":
  ```
- Line 791: `AWS_ACCESS_KEY_ID_1`
  ```python
  {
                "key_id": "key_1",
                "access_key": os.getenv("AWS_ACCESS_KEY_ID_1", ""),
                "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY_1", ""),
                "region": "us-east-1",
  ```
- Line 792: `AWS_SECRET_ACCESS_KEY_1`
  ```python
  "key_id": "key_1",
                "access_key": os.getenv("AWS_ACCESS_KEY_ID_1", ""),
                "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY_1", ""),
                "region": "us-east-1",
            },
  ```
- Line 797: `AWS_ACCESS_KEY_ID_2`
  ```python
  {
                "key_id": "key_2",
                "access_key": os.getenv("AWS_ACCESS_KEY_ID_2", ""),
                "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY_2", ""),
                "region": "us-west-2",
  ```
- Line 798: `AWS_SECRET_ACCESS_KEY_2`
  ```python
  "key_id": "key_2",
                "access_key": os.getenv("AWS_ACCESS_KEY_ID_2", ""),
                "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY_2", ""),
                "region": "us-west-2",
            },
  ```

### scripts/enhanced_bedrock_queue_client.py
- Line 57: `BEDROCK_MAX_RETRIES`
  ```python
  # Retry and backoff configuration (tunable via env)
        self.max_retries = int(os.getenv("BEDROCK_MAX_RETRIES", "6"))
        self.base_backoff = float(os.getenv("BEDROCK_BASE_BACKOFF", "1.5"))
        self.max_backoff = float(os.getenv("BEDROCK_MAX_BACKOFF", "12.0"))
  ```
- Line 58: `BEDROCK_BASE_BACKOFF`
  ```python
  # Retry and backoff configuration (tunable via env)
        self.max_retries = int(os.getenv("BEDROCK_MAX_RETRIES", "6"))
        self.base_backoff = float(os.getenv("BEDROCK_BASE_BACKOFF", "1.5"))
        self.max_backoff = float(os.getenv("BEDROCK_MAX_BACKOFF", "12.0"))
  ```
- Line 59: `BEDROCK_MAX_BACKOFF`
  ```python
  self.max_retries = int(os.getenv("BEDROCK_MAX_RETRIES", "6"))
        self.base_backoff = float(os.getenv("BEDROCK_BASE_BACKOFF", "1.5"))
        self.max_backoff = float(os.getenv("BEDROCK_MAX_BACKOFF", "12.0"))

        # Smart timing parameters (conservative defaults)
  ```
- Line 62: `BEDROCK_QUEUE_BASE_DELAY`
  ```python
  # Smart timing parameters (conservative defaults)
        self.base_delay = float(os.getenv("BEDROCK_QUEUE_BASE_DELAY", "1.5"))  # Base delay between requests
        self.batch_size = int(os.getenv("BEDROCK_QUEUE_BATCH_SIZE", "1"))  # Process up to N requests in a batch
        self.batch_window = float(os.getenv("BEDROCK_QUEUE_BATCH_WINDOW", "1.5"))  # Time window for batching
  ```
- Line 63: `BEDROCK_QUEUE_BATCH_SIZE`
  ```python
  # Smart timing parameters (conservative defaults)
        self.base_delay = float(os.getenv("BEDROCK_QUEUE_BASE_DELAY", "1.5"))  # Base delay between requests
        self.batch_size = int(os.getenv("BEDROCK_QUEUE_BATCH_SIZE", "1"))  # Process up to N requests in a batch
        self.batch_window = float(os.getenv("BEDROCK_QUEUE_BATCH_WINDOW", "1.5"))  # Time window for batching
  ```
- Line 64: `BEDROCK_QUEUE_BATCH_WINDOW`
  ```python
  self.base_delay = float(os.getenv("BEDROCK_QUEUE_BASE_DELAY", "1.5"))  # Base delay between requests
        self.batch_size = int(os.getenv("BEDROCK_QUEUE_BATCH_SIZE", "1"))  # Process up to N requests in a batch
        self.batch_window = float(os.getenv("BEDROCK_QUEUE_BATCH_WINDOW", "1.5"))  # Time window for batching

        # Rate limit tracking
  ```
- Line 79: `BEDROCK_MODEL_ID`
  ```python
  logger.info(f"IntelligentBedrockQueue initialized with {len(api_keys)} keys")
        try:
            model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")
            logger.info(f"Bedrock model configured: {model_id}")
        except Exception:
  ```
- Line 241: `AWS_REGION`
  ```python
  # Create Bedrock client (use explicit creds if provided; otherwise default chain)
            config = Config(
                region_name=key_config.get("region", os.getenv("AWS_REGION", "us-east-1")),
                retries={"max_attempts": 0},  # we implement retries ourselves
                read_timeout=30,
  ```
- Line 250: `AWS_REGION`
  ```python
  "service_name": "bedrock-runtime",
                "config": config,
                "region_name": key_config.get("region", os.getenv("AWS_REGION", "us-east-1")),
            }
            # Only pass keys if present; else let boto3 resolve credentials
  ```
- Line 271: `BEDROCK_MODEL_ID`
  ```python
  # Make the request
                response = client.invoke_model(
                    modelId=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
                    body=json.dumps(request_body),
                    contentType="application/json",
  ```
- Line 452: `AWS_REGION`
  ```python
  if not api_keys:
            # Fall back to default boto3 credential chain; require only region
            region = os.getenv("AWS_REGION", "us-east-1")
            logger.warning("No explicit AWS access keys found in env; falling back to default boto3 credentials chain")
            api_keys = [
  ```

### scripts/eval_manifest_generator.py
- Line 62: `EMBEDDING_MODEL`
  ```python
  """Capture model configuration and IDs."""
        return {
            "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            "rerank_model": os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base"),
            "generation_model": os.getenv("GENERATION_MODEL", "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0"),
  ```
- Line 63: `RERANK_MODEL`
  ```python
  return {
            "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            "rerank_model": os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base"),
            "generation_model": os.getenv("GENERATION_MODEL", "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0"),
            "embedding_provider": os.getenv("EMBEDDING_PROVIDER", "local"),
  ```
- Line 64: `GENERATION_MODEL`
  ```python
  "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            "rerank_model": os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base"),
            "generation_model": os.getenv("GENERATION_MODEL", "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0"),
            "embedding_provider": os.getenv("EMBEDDING_PROVIDER", "local"),
            "generation_provider": os.getenv("GENERATION_PROVIDER", "bedrock"),
  ```
- Line 65: `EMBEDDING_PROVIDER`
  ```python
  "rerank_model": os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base"),
            "generation_model": os.getenv("GENERATION_MODEL", "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0"),
            "embedding_provider": os.getenv("EMBEDDING_PROVIDER", "local"),
            "generation_provider": os.getenv("GENERATION_PROVIDER", "bedrock"),
            "model_versions": {
  ```
- Line 66: `GENERATION_PROVIDER`
  ```python
  "generation_model": os.getenv("GENERATION_MODEL", "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0"),
            "embedding_provider": os.getenv("EMBEDDING_PROVIDER", "local"),
            "generation_provider": os.getenv("GENERATION_PROVIDER", "bedrock"),
            "model_versions": {
                "embedding": self._get_model_version(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")),
  ```
- Line 68: `EMBEDDING_MODEL`
  ```python
  "generation_provider": os.getenv("GENERATION_PROVIDER", "bedrock"),
            "model_versions": {
                "embedding": self._get_model_version(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")),
                "rerank": self._get_model_version(os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")),
            },
  ```
- Line 69: `RERANK_MODEL`
  ```python
  "model_versions": {
                "embedding": self._get_model_version(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")),
                "rerank": self._get_model_version(os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")),
            },
        }
  ```
- Line 78: `RETR_TOPK_VEC`
  ```python
  # Retrieval Configuration
            "retrieval": {
                "topk_vec": int(os.getenv("RETR_TOPK_VEC", "140")),
                "topk_bm25": int(os.getenv("RETR_TOPK_BM25", "140")),
                "topk_other": int(os.getenv("RETR_TOPK_OTHER", "0")),
  ```
- Line 79: `RETR_TOPK_BM25`
  ```python
  "retrieval": {
                "topk_vec": int(os.getenv("RETR_TOPK_VEC", "140")),
                "topk_bm25": int(os.getenv("RETR_TOPK_BM25", "140")),
                "topk_other": int(os.getenv("RETR_TOPK_OTHER", "0")),
                "fusion_method": os.getenv("FUSION_METHOD", "RRF"),
  ```
- Line 80: `RETR_TOPK_OTHER`
  ```python
  "topk_vec": int(os.getenv("RETR_TOPK_VEC", "140")),
                "topk_bm25": int(os.getenv("RETR_TOPK_BM25", "140")),
                "topk_other": int(os.getenv("RETR_TOPK_OTHER", "0")),
                "fusion_method": os.getenv("FUSION_METHOD", "RRF"),
                "rrf_k": int(os.getenv("RRF_K", "60")),
  ```
- Line 81: `FUSION_METHOD`
  ```python
  "topk_bm25": int(os.getenv("RETR_TOPK_BM25", "140")),
                "topk_other": int(os.getenv("RETR_TOPK_OTHER", "0")),
                "fusion_method": os.getenv("FUSION_METHOD", "RRF"),
                "rrf_k": int(os.getenv("RRF_K", "60")),
            },
  ```
- Line 82: `RRF_K`
  ```python
  "topk_other": int(os.getenv("RETR_TOPK_OTHER", "0")),
                "fusion_method": os.getenv("FUSION_METHOD", "RRF"),
                "rrf_k": int(os.getenv("RRF_K", "60")),
            },
            # Reranking Configuration
  ```
- Line 86: `RERANK_ENABLE`
  ```python
  # Reranking Configuration
            "reranking": {
                "enabled": os.getenv("RERANK_ENABLE", "1") == "1",
                "model": os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base"),
                "pool_size": int(os.getenv("RERANK_POOL", "60")),
  ```
- Line 87: `RERANK_MODEL`
  ```python
  "reranking": {
                "enabled": os.getenv("RERANK_ENABLE", "1") == "1",
                "model": os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base"),
                "pool_size": int(os.getenv("RERANK_POOL", "60")),
                "topn": int(os.getenv("RERANK_TOPN", "18")),
  ```
- Line 88: `RERANK_POOL`
  ```python
  "enabled": os.getenv("RERANK_ENABLE", "1") == "1",
                "model": os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base"),
                "pool_size": int(os.getenv("RERANK_POOL", "60")),
                "topn": int(os.getenv("RERANK_TOPN", "18")),
            },
  ```
- Line 89: `RERANK_TOPN`
  ```python
  "model": os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base"),
                "pool_size": int(os.getenv("RERANK_POOL", "60")),
                "topn": int(os.getenv("RERANK_TOPN", "18")),
            },
            # Context Configuration
  ```
- Line 93: `CONTEXT_DOCS_MAX`
  ```python
  # Context Configuration
            "context": {
                "max_docs": int(os.getenv("CONTEXT_DOCS_MAX", "12")),
                "max_chars": int(os.getenv("CONTEXT_MAX_CHARS", "1600")),
                "tail_keep": int(os.getenv("FUSE_TAIL_KEEP", "0")),
  ```
- Line 94: `CONTEXT_MAX_CHARS`
  ```python
  "context": {
                "max_docs": int(os.getenv("CONTEXT_DOCS_MAX", "12")),
                "max_chars": int(os.getenv("CONTEXT_MAX_CHARS", "1600")),
                "tail_keep": int(os.getenv("FUSE_TAIL_KEEP", "0")),
            },
  ```
- Line 95: `FUSE_TAIL_KEEP`
  ```python
  "max_docs": int(os.getenv("CONTEXT_DOCS_MAX", "12")),
                "max_chars": int(os.getenv("CONTEXT_MAX_CHARS", "1600")),
                "tail_keep": int(os.getenv("FUSE_TAIL_KEEP", "0")),
            },
            # Performance Configuration
  ```
- Line 99: `PIPELINE_WORKERS`
  ```python
  # Performance Configuration
            "performance": {
                "workers": int(os.getenv("PIPELINE_WORKERS", "2")),
                "max_in_flight": int(os.getenv("BEDROCK_MAX_IN_FLIGHT", "1")),
                "max_rps": float(os.getenv("BEDROCK_MAX_RPS", "0.12")),
  ```
- Line 100: `BEDROCK_MAX_IN_FLIGHT`
  ```python
  "performance": {
                "workers": int(os.getenv("PIPELINE_WORKERS", "2")),
                "max_in_flight": int(os.getenv("BEDROCK_MAX_IN_FLIGHT", "1")),
                "max_rps": float(os.getenv("BEDROCK_MAX_RPS", "0.12")),
                "timeout_sec": int(os.getenv("BEDROCK_CALL_TIMEOUT_SEC", "35")),
  ```
- Line 101: `BEDROCK_MAX_RPS`
  ```python
  "workers": int(os.getenv("PIPELINE_WORKERS", "2")),
                "max_in_flight": int(os.getenv("BEDROCK_MAX_IN_FLIGHT", "1")),
                "max_rps": float(os.getenv("BEDROCK_MAX_RPS", "0.12")),
                "timeout_sec": int(os.getenv("BEDROCK_CALL_TIMEOUT_SEC", "35")),
            },
  ```
- Line 102: `BEDROCK_CALL_TIMEOUT_SEC`
  ```python
  "max_in_flight": int(os.getenv("BEDROCK_MAX_IN_FLIGHT", "1")),
                "max_rps": float(os.getenv("BEDROCK_MAX_RPS", "0.12")),
                "timeout_sec": int(os.getenv("BEDROCK_CALL_TIMEOUT_SEC", "35")),
            },
        }
  ```
- Line 119: `INGEST_RUN_ID`
  ```python
  """Capture data configuration and run IDs."""
        return {
            "ingest_run_id": os.getenv("INGEST_RUN_ID", "unknown"),
            "chunk_variant": os.getenv("CHUNK_VARIANT", "default"),
            "dataset_version": os.getenv("DATASET_VERSION", "latest"),
  ```
- Line 120: `CHUNK_VARIANT`
  ```python
  return {
            "ingest_run_id": os.getenv("INGEST_RUN_ID", "unknown"),
            "chunk_variant": os.getenv("CHUNK_VARIANT", "default"),
            "dataset_version": os.getenv("DATASET_VERSION", "latest"),
            "eval_cases_file": os.getenv("EVAL_CASES_FILE", "datasets/eval_cases.jsonl"),
  ```
- Line 121: `DATASET_VERSION`
  ```python
  "ingest_run_id": os.getenv("INGEST_RUN_ID", "unknown"),
            "chunk_variant": os.getenv("CHUNK_VARIANT", "default"),
            "dataset_version": os.getenv("DATASET_VERSION", "latest"),
            "eval_cases_file": os.getenv("EVAL_CASES_FILE", "datasets/eval_cases.jsonl"),
            "data_checksum": self._get_data_checksum(),
  ```
- Line 122: `EVAL_CASES_FILE`
  ```python
  "chunk_variant": os.getenv("CHUNK_VARIANT", "default"),
            "dataset_version": os.getenv("DATASET_VERSION", "latest"),
            "eval_cases_file": os.getenv("EVAL_CASES_FILE", "datasets/eval_cases.jsonl"),
            "data_checksum": self._get_data_checksum(),
        }
  ```
- Line 129: `EVAL_DRIVER`
  ```python
  """Capture evaluation configuration."""
        return {
            "eval_driver": os.getenv("EVAL_DRIVER", "dspy_rag"),
            "use_real_rag": os.getenv("RAGCHECKER_USE_REAL_RAG", "1") == "1",
            "bypass_cli": os.getenv("RAGCHECKER_BYPASS_CLI", "1") == "1",
  ```
- Line 130: `RAGCHECKER_USE_REAL_RAG`
  ```python
  return {
            "eval_driver": os.getenv("EVAL_DRIVER", "dspy_rag"),
            "use_real_rag": os.getenv("RAGCHECKER_USE_REAL_RAG", "1") == "1",
            "bypass_cli": os.getenv("RAGCHECKER_BYPASS_CLI", "1") == "1",
            "disable_embeddings": os.getenv("RAGCHECKER_DISABLE_EMBEDDINGS", "1") == "1",
  ```
- Line 131: `RAGCHECKER_BYPASS_CLI`
  ```python
  "eval_driver": os.getenv("EVAL_DRIVER", "dspy_rag"),
            "use_real_rag": os.getenv("RAGCHECKER_USE_REAL_RAG", "1") == "1",
            "bypass_cli": os.getenv("RAGCHECKER_BYPASS_CLI", "1") == "1",
            "disable_embeddings": os.getenv("RAGCHECKER_DISABLE_EMBEDDINGS", "1") == "1",
            "progress_log": os.getenv("RAGCHECKER_PROGRESS_LOG", "metrics/baseline_evaluations/progress.jsonl"),
  ```
- Line 132: `RAGCHECKER_DISABLE_EMBEDDINGS`
  ```python
  "use_real_rag": os.getenv("RAGCHECKER_USE_REAL_RAG", "1") == "1",
            "bypass_cli": os.getenv("RAGCHECKER_BYPASS_CLI", "1") == "1",
            "disable_embeddings": os.getenv("RAGCHECKER_DISABLE_EMBEDDINGS", "1") == "1",
            "progress_log": os.getenv("RAGCHECKER_PROGRESS_LOG", "metrics/baseline_evaluations/progress.jsonl"),
            "save_candidates_max": int(os.getenv("SAVE_CANDIDATES_MAX", "20")),
  ```
- Line 133: `RAGCHECKER_PROGRESS_LOG`
  ```python
  "bypass_cli": os.getenv("RAGCHECKER_BYPASS_CLI", "1") == "1",
            "disable_embeddings": os.getenv("RAGCHECKER_DISABLE_EMBEDDINGS", "1") == "1",
            "progress_log": os.getenv("RAGCHECKER_PROGRESS_LOG", "metrics/baseline_evaluations/progress.jsonl"),
            "save_candidates_max": int(os.getenv("SAVE_CANDIDATES_MAX", "20")),
            "snapshot_max_items": int(os.getenv("SNAPSHOT_MAX_ITEMS", "50")),
  ```
- Line 134: `SAVE_CANDIDATES_MAX`
  ```python
  "disable_embeddings": os.getenv("RAGCHECKER_DISABLE_EMBEDDINGS", "1") == "1",
            "progress_log": os.getenv("RAGCHECKER_PROGRESS_LOG", "metrics/baseline_evaluations/progress.jsonl"),
            "save_candidates_max": int(os.getenv("SAVE_CANDIDATES_MAX", "20")),
            "snapshot_max_items": int(os.getenv("SNAPSHOT_MAX_ITEMS", "50")),
        }
  ```
- Line 135: `SNAPSHOT_MAX_ITEMS`
  ```python
  "progress_log": os.getenv("RAGCHECKER_PROGRESS_LOG", "metrics/baseline_evaluations/progress.jsonl"),
            "save_candidates_max": int(os.getenv("SAVE_CANDIDATES_MAX", "20")),
            "snapshot_max_items": int(os.getenv("SNAPSHOT_MAX_ITEMS", "50")),
        }
  ```
- Line 143: `DSPY_RAG_PATH`
  ```python
  "python_version": os.sys.version,
            "platform": os.name,
            "dspy_rag_path": os.getenv("DSPY_RAG_PATH", "src"),
            "database_url": self._mask_sensitive_data(os.getenv("DATABASE_URL", "postgresql://***")),
            "aws_region": os.getenv("AWS_REGION", "us-east-1"),
  ```
- Line 144: `DATABASE_URL`
  ```python
  "platform": os.name,
            "dspy_rag_path": os.getenv("DSPY_RAG_PATH", "src"),
            "database_url": self._mask_sensitive_data(os.getenv("DATABASE_URL", "postgresql://***")),
            "aws_region": os.getenv("AWS_REGION", "us-east-1"),
            "environment": os.getenv("ENVIRONMENT", "development"),
  ```
- Line 145: `AWS_REGION`
  ```python
  "dspy_rag_path": os.getenv("DSPY_RAG_PATH", "src"),
            "database_url": self._mask_sensitive_data(os.getenv("DATABASE_URL", "postgresql://***")),
            "aws_region": os.getenv("AWS_REGION", "us-east-1"),
            "environment": os.getenv("ENVIRONMENT", "development"),
        }
  ```
- Line 146: `ENVIRONMENT`
  ```python
  "database_url": self._mask_sensitive_data(os.getenv("DATABASE_URL", "postgresql://***")),
            "aws_region": os.getenv("AWS_REGION", "us-east-1"),
            "environment": os.getenv("ENVIRONMENT", "development"),
        }
  ```
- Line 152: `PRECISION_MIN`
  ```python
  """Capture quality gate thresholds."""
        return {
            "precision_min": float(os.getenv("PRECISION_MIN", "0.20")),
            "recall_min": float(os.getenv("RECALL_MIN", "0.45")),
            "f1_min": float(os.getenv("F1_MIN", "0.22")),
  ```
- Line 153: `RECALL_MIN`
  ```python
  return {
            "precision_min": float(os.getenv("PRECISION_MIN", "0.20")),
            "recall_min": float(os.getenv("RECALL_MIN", "0.45")),
            "f1_min": float(os.getenv("F1_MIN", "0.22")),
            "latency_max": float(os.getenv("LATENCY_MAX", "30.0")),
  ```
- Line 154: `F1_MIN`
  ```python
  "precision_min": float(os.getenv("PRECISION_MIN", "0.20")),
            "recall_min": float(os.getenv("RECALL_MIN", "0.45")),
            "f1_min": float(os.getenv("F1_MIN", "0.22")),
            "latency_max": float(os.getenv("LATENCY_MAX", "30.0")),
            "faithfulness_min": float(os.getenv("FAITHFULNESS_MIN", "0.60")),
  ```
- Line 155: `LATENCY_MAX`
  ```python
  "recall_min": float(os.getenv("RECALL_MIN", "0.45")),
            "f1_min": float(os.getenv("F1_MIN", "0.22")),
            "latency_max": float(os.getenv("LATENCY_MAX", "30.0")),
            "faithfulness_min": float(os.getenv("FAITHFULNESS_MIN", "0.60")),
            "oracle_retrieval_hit_min": float(os.getenv("ORACLE_RETRIEVAL_HIT_MIN", "0.85")),
  ```
- Line 156: `FAITHFULNESS_MIN`
  ```python
  "f1_min": float(os.getenv("F1_MIN", "0.22")),
            "latency_max": float(os.getenv("LATENCY_MAX", "30.0")),
            "faithfulness_min": float(os.getenv("FAITHFULNESS_MIN", "0.60")),
            "oracle_retrieval_hit_min": float(os.getenv("ORACLE_RETRIEVAL_HIT_MIN", "0.85")),
            "reader_used_gold_min": float(os.getenv("READER_USED_GOLD_MIN", "0.70")),
  ```
- Line 157: `ORACLE_RETRIEVAL_HIT_MIN`
  ```python
  "latency_max": float(os.getenv("LATENCY_MAX", "30.0")),
            "faithfulness_min": float(os.getenv("FAITHFULNESS_MIN", "0.60")),
            "oracle_retrieval_hit_min": float(os.getenv("ORACLE_RETRIEVAL_HIT_MIN", "0.85")),
            "reader_used_gold_min": float(os.getenv("READER_USED_GOLD_MIN", "0.70")),
        }
  ```
- Line 158: `READER_USED_GOLD_MIN`
  ```python
  "faithfulness_min": float(os.getenv("FAITHFULNESS_MIN", "0.60")),
            "oracle_retrieval_hit_min": float(os.getenv("ORACLE_RETRIEVAL_HIT_MIN", "0.85")),
            "reader_used_gold_min": float(os.getenv("READER_USED_GOLD_MIN", "0.70")),
        }
  ```
- Line 164: `TEMPERATURE`
  ```python
  """Capture deterministic evaluation settings."""
        return {
            "temperature": float(os.getenv("TEMPERATURE", "0.0")),
            "disable_cache": os.getenv("EVAL_DISABLE_CACHE", "1") == "1",
            "prompt_audit": os.getenv("PROMPT_AUDIT", "1") == "1",
  ```
- Line 165: `EVAL_DISABLE_CACHE`
  ```python
  return {
            "temperature": float(os.getenv("TEMPERATURE", "0.0")),
            "disable_cache": os.getenv("EVAL_DISABLE_CACHE", "1") == "1",
            "prompt_audit": os.getenv("PROMPT_AUDIT", "1") == "1",
            "few_shot_ids": os.getenv("FEW_SHOT_IDS", "").split(",") if os.getenv("FEW_SHOT_IDS") else [],
  ```
- Line 166: `PROMPT_AUDIT`
  ```python
  "temperature": float(os.getenv("TEMPERATURE", "0.0")),
            "disable_cache": os.getenv("EVAL_DISABLE_CACHE", "1") == "1",
            "prompt_audit": os.getenv("PROMPT_AUDIT", "1") == "1",
            "few_shot_ids": os.getenv("FEW_SHOT_IDS", "").split(",") if os.getenv("FEW_SHOT_IDS") else [],
            "prompt_hash": self._get_prompt_hash(),
  ```
- Line 167: `FEW_SHOT_IDS`
  ```python
  "disable_cache": os.getenv("EVAL_DISABLE_CACHE", "1") == "1",
            "prompt_audit": os.getenv("PROMPT_AUDIT", "1") == "1",
            "few_shot_ids": os.getenv("FEW_SHOT_IDS", "").split(",") if os.getenv("FEW_SHOT_IDS") else [],
            "prompt_hash": self._get_prompt_hash(),
            "cot_flag": os.getenv("COT_FLAG", "0") == "1",
  ```
- Line 167: `FEW_SHOT_IDS`
  ```python
  "disable_cache": os.getenv("EVAL_DISABLE_CACHE", "1") == "1",
            "prompt_audit": os.getenv("PROMPT_AUDIT", "1") == "1",
            "few_shot_ids": os.getenv("FEW_SHOT_IDS", "").split(",") if os.getenv("FEW_SHOT_IDS") else [],
            "prompt_hash": self._get_prompt_hash(),
            "cot_flag": os.getenv("COT_FLAG", "0") == "1",
  ```
- Line 169: `COT_FLAG`
  ```python
  "few_shot_ids": os.getenv("FEW_SHOT_IDS", "").split(",") if os.getenv("FEW_SHOT_IDS") else [],
            "prompt_hash": self._get_prompt_hash(),
            "cot_flag": os.getenv("COT_FLAG", "0") == "1",
            "seed": int(os.getenv("RANDOM_SEED", "42")),
        }
  ```
- Line 170: `RANDOM_SEED`
  ```python
  "prompt_hash": self._get_prompt_hash(),
            "cot_flag": os.getenv("COT_FLAG", "0") == "1",
            "seed": int(os.getenv("RANDOM_SEED", "42")),
        }
  ```
- Line 176: `HEALTH_CHECK_ENV`
  ```python
  """Capture health check configuration."""
        return {
            "env_validation": os.getenv("HEALTH_CHECK_ENV", "1") == "1",
            "index_present": os.getenv("HEALTH_CHECK_INDEX", "1") == "1",
            "token_budget": os.getenv("HEALTH_CHECK_TOKEN_BUDGET", "1") == "1",
  ```
- Line 177: `HEALTH_CHECK_INDEX`
  ```python
  return {
            "env_validation": os.getenv("HEALTH_CHECK_ENV", "1") == "1",
            "index_present": os.getenv("HEALTH_CHECK_INDEX", "1") == "1",
            "token_budget": os.getenv("HEALTH_CHECK_TOKEN_BUDGET", "1") == "1",
            "prefix_leakage": os.getenv("HEALTH_CHECK_PREFIX_LEAKAGE", "1") == "1",
  ```
- Line 178: `HEALTH_CHECK_TOKEN_BUDGET`
  ```python
  "env_validation": os.getenv("HEALTH_CHECK_ENV", "1") == "1",
            "index_present": os.getenv("HEALTH_CHECK_INDEX", "1") == "1",
            "token_budget": os.getenv("HEALTH_CHECK_TOKEN_BUDGET", "1") == "1",
            "prefix_leakage": os.getenv("HEALTH_CHECK_PREFIX_LEAKAGE", "1") == "1",
            "database_connectivity": os.getenv("HEALTH_CHECK_DB", "1") == "1",
  ```
- Line 179: `HEALTH_CHECK_PREFIX_LEAKAGE`
  ```python
  "index_present": os.getenv("HEALTH_CHECK_INDEX", "1") == "1",
            "token_budget": os.getenv("HEALTH_CHECK_TOKEN_BUDGET", "1") == "1",
            "prefix_leakage": os.getenv("HEALTH_CHECK_PREFIX_LEAKAGE", "1") == "1",
            "database_connectivity": os.getenv("HEALTH_CHECK_DB", "1") == "1",
            "model_availability": os.getenv("HEALTH_CHECK_MODELS", "1") == "1",
  ```
- Line 180: `HEALTH_CHECK_DB`
  ```python
  "token_budget": os.getenv("HEALTH_CHECK_TOKEN_BUDGET", "1") == "1",
            "prefix_leakage": os.getenv("HEALTH_CHECK_PREFIX_LEAKAGE", "1") == "1",
            "database_connectivity": os.getenv("HEALTH_CHECK_DB", "1") == "1",
            "model_availability": os.getenv("HEALTH_CHECK_MODELS", "1") == "1",
        }
  ```
- Line 181: `HEALTH_CHECK_MODELS`
  ```python
  "prefix_leakage": os.getenv("HEALTH_CHECK_PREFIX_LEAKAGE", "1") == "1",
            "database_connectivity": os.getenv("HEALTH_CHECK_DB", "1") == "1",
            "model_availability": os.getenv("HEALTH_CHECK_MODELS", "1") == "1",
        }
  ```
- Line 189: `USER`
  ```python
  "git_commit": self._get_git_commit(),
            "git_branch": self._get_git_branch(),
            "user": os.getenv("USER", "unknown"),
            "hostname": os.getenv("HOSTNAME", "unknown"),
            "pid": os.getpid(),
  ```
- Line 190: `HOSTNAME`
  ```python
  "git_branch": self._get_git_branch(),
            "user": os.getenv("USER", "unknown"),
            "hostname": os.getenv("HOSTNAME", "unknown"),
            "pid": os.getpid(),
            "working_directory": os.getcwd(),
  ```
- Line 204: `EVAL_CASES_FILE`
  ```python
  def _get_data_checksum(self) -> str:
        """Get data checksum for reproducibility."""
        eval_file = os.getenv("EVAL_CASES_FILE", "datasets/eval_cases.jsonl")
        if os.path.exists(eval_file):
            with open(eval_file, "rb") as f:
  ```

### scripts/eval_optimization_suite.py
- Line 42: `EVAL_DISABLE_CACHE`
  ```python
  # Set global determinism
    os.environ["EVAL_DISABLE_CACHE"] = "1"
    os.environ["EVAL_PATH"] = "dspy_rag"
    os.environ["INGEST_RUN_ID"] = f"{config.chunk_version}-{config.get_config_hash()[:8]}"
  ```
- Line 43: `EVAL_PATH`
  ```python
  # Set global determinism
    os.environ["EVAL_DISABLE_CACHE"] = "1"
    os.environ["EVAL_PATH"] = "dspy_rag"
    os.environ["INGEST_RUN_ID"] = f"{config.chunk_version}-{config.get_config_hash()[:8]}"
    os.environ["CHUNK_VERSION"] = config.chunk_version
  ```
- Line 44: `INGEST_RUN_ID`
  ```python
  os.environ["EVAL_DISABLE_CACHE"] = "1"
    os.environ["EVAL_PATH"] = "dspy_rag"
    os.environ["INGEST_RUN_ID"] = f"{config.chunk_version}-{config.get_config_hash()[:8]}"
    os.environ["CHUNK_VERSION"] = config.chunk_version
    os.environ["CONFIG_HASH"] = config.get_config_hash()
  ```
- Line 45: `CHUNK_VERSION`
  ```python
  os.environ["EVAL_PATH"] = "dspy_rag"
    os.environ["INGEST_RUN_ID"] = f"{config.chunk_version}-{config.get_config_hash()[:8]}"
    os.environ["CHUNK_VERSION"] = config.chunk_version
    os.environ["CONFIG_HASH"] = config.get_config_hash()
  ```
- Line 46: `CONFIG_HASH`
  ```python
  os.environ["INGEST_RUN_ID"] = f"{config.chunk_version}-{config.get_config_hash()[:8]}"
    os.environ["CHUNK_VERSION"] = config.chunk_version
    os.environ["CONFIG_HASH"] = config.get_config_hash()

    print("✅ Determinism switches configured")
  ```

### scripts/focused_config_migration.py
- Line 105: `VAR`
  ```python
  def _find_env_var_references(self, content: str):
        """Find environment variable references in the content."""
        # Look for patterns like os.environ['VAR'] or os.environ.get('VAR')
        patterns = [
            r'os\.environ\[["\']([^"\']+)["\']\]',
  ```
- Line 105: `VAR`
  ```python
  def _find_env_var_references(self, content: str):
        """Find environment variable references in the content."""
        # Look for patterns like os.environ['VAR'] or os.environ.get('VAR')
        patterns = [
            r'os\.environ\[["\']([^"\']+)["\']\]',
  ```

### scripts/freeze_baseline_artifacts.py
- Line 172: `CONFIG_HASH`
  ```python
  # Get current environment variables
        config_vars = {
            "CONFIG_HASH": config_hash or os.getenv("CONFIG_HASH", "unknown"),
            "INGEST_RUN_ID": ingest_run_id or os.getenv("INGEST_RUN_ID", "unknown"),
            "TIMESTAMP": self.timestamp,
  ```
- Line 173: `INGEST_RUN_ID`
  ```python
  config_vars = {
            "CONFIG_HASH": config_hash or os.getenv("CONFIG_HASH", "unknown"),
            "INGEST_RUN_ID": ingest_run_id or os.getenv("INGEST_RUN_ID", "unknown"),
            "TIMESTAMP": self.timestamp,
            "EVAL_DISABLE_CACHE": os.getenv("EVAL_DISABLE_CACHE", "1"),
  ```
- Line 175: `EVAL_DISABLE_CACHE`
  ```python
  "INGEST_RUN_ID": ingest_run_id or os.getenv("INGEST_RUN_ID", "unknown"),
            "TIMESTAMP": self.timestamp,
            "EVAL_DISABLE_CACHE": os.getenv("EVAL_DISABLE_CACHE", "1"),
            "FEW_SHOT_K": os.getenv("FEW_SHOT_K", "0"),
            "EVAL_COT": os.getenv("EVAL_COT", "0"),
  ```
- Line 176: `FEW_SHOT_K`
  ```python
  "TIMESTAMP": self.timestamp,
            "EVAL_DISABLE_CACHE": os.getenv("EVAL_DISABLE_CACHE", "1"),
            "FEW_SHOT_K": os.getenv("FEW_SHOT_K", "0"),
            "EVAL_COT": os.getenv("EVAL_COT", "0"),
            "TEMPERATURE": os.getenv("TEMPERATURE", "0"),
  ```
- Line 177: `EVAL_COT`
  ```python
  "EVAL_DISABLE_CACHE": os.getenv("EVAL_DISABLE_CACHE", "1"),
            "FEW_SHOT_K": os.getenv("FEW_SHOT_K", "0"),
            "EVAL_COT": os.getenv("EVAL_COT", "0"),
            "TEMPERATURE": os.getenv("TEMPERATURE", "0"),
        }
  ```
- Line 178: `TEMPERATURE`
  ```python
  "FEW_SHOT_K": os.getenv("FEW_SHOT_K", "0"),
            "EVAL_COT": os.getenv("EVAL_COT", "0"),
            "TEMPERATURE": os.getenv("TEMPERATURE", "0"),
        }
  ```

### scripts/game_day_drills.py
- Line 385: `PREFIX_GUARD_ENABLED`
  ```python
  try:
            # Check if prefix guard is enabled in configuration
            prefix_guard_enabled = os.getenv("PREFIX_GUARD_ENABLED", "1") == "1"

            return {"success": True, "prefix_guard_enabled": prefix_guard_enabled, "passed": prefix_guard_enabled}
  ```

### scripts/gate_and_promote.py
- Line 104: `DATASET_HAS_GOLD`
  ```python
  # Check if this is a gold dataset
        has_gold = os.getenv("DATASET_HAS_GOLD", "1") == "1"

        # F1 Score Check (only for gold datasets with few-shot)
  ```
- Line 118: `FILE_ORACLE_PREFILTER_MIN`
  ```python
  foru = 0.0

            fop_min = float(os.getenv("FILE_ORACLE_PREFILTER_MIN", "0.85"))
            foru_min = float(os.getenv("FILE_ORACLE_READER_MIN", "0.70"))
  ```
- Line 119: `FILE_ORACLE_READER_MIN`
  ```python
  fop_min = float(os.getenv("FILE_ORACLE_PREFILTER_MIN", "0.85"))
            foru_min = float(os.getenv("FILE_ORACLE_READER_MIN", "0.70"))

            checks["file_oracle_prefilter"] = {
  ```
- Line 220: `SNAPSHOT_MIN`
  ```python
  "metric": "snapshot_breadth",
                "value": snap_max,
                "threshold": int(os.getenv("SNAPSHOT_MIN", "30")),
                "passed": snap_max >= int(os.getenv("SNAPSHOT_MIN", "30")),
                "message": f"Snapshot max {snap_max} {'≥' if snap_max >= int(os.getenv('SNAPSHOT_MIN', '30')) else '<'} min {os.getenv('SNAPSHOT_MIN', '30')}",
  ```
- Line 221: `SNAPSHOT_MIN`
  ```python
  "value": snap_max,
                "threshold": int(os.getenv("SNAPSHOT_MIN", "30")),
                "passed": snap_max >= int(os.getenv("SNAPSHOT_MIN", "30")),
                "message": f"Snapshot max {snap_max} {'≥' if snap_max >= int(os.getenv('SNAPSHOT_MIN', '30')) else '<'} min {os.getenv('SNAPSHOT_MIN', '30')}",
            }
  ```
- Line 222: `SNAPSHOT_MIN`
  ```python
  "threshold": int(os.getenv("SNAPSHOT_MIN", "30")),
                "passed": snap_max >= int(os.getenv("SNAPSHOT_MIN", "30")),
                "message": f"Snapshot max {snap_max} {'≥' if snap_max >= int(os.getenv('SNAPSHOT_MIN', '30')) else '<'} min {os.getenv('SNAPSHOT_MIN', '30')}",
            }
  ```
- Line 222: `SNAPSHOT_MIN`
  ```python
  "threshold": int(os.getenv("SNAPSHOT_MIN", "30")),
                "passed": snap_max >= int(os.getenv("SNAPSHOT_MIN", "30")),
                "message": f"Snapshot max {snap_max} {'≥' if snap_max >= int(os.getenv('SNAPSHOT_MIN', '30')) else '<'} min {os.getenv('SNAPSHOT_MIN', '30')}",
            }
  ```
- Line 229: `COVERAGE_MIN`
  ```python
  "metric": "query_coverage",
                "value": cov,
                "threshold": float(os.getenv("COVERAGE_MIN", "0.70")),
                "passed": cov >= float(os.getenv("COVERAGE_MIN", "0.70")),
                "message": f"Query coverage {cov:.2f} {'≥' if cov >= float(os.getenv('COVERAGE_MIN', '0.70')) else '<'} min {os.getenv('COVERAGE_MIN', '0.70')}",
  ```
- Line 230: `COVERAGE_MIN`
  ```python
  "value": cov,
                "threshold": float(os.getenv("COVERAGE_MIN", "0.70")),
                "passed": cov >= float(os.getenv("COVERAGE_MIN", "0.70")),
                "message": f"Query coverage {cov:.2f} {'≥' if cov >= float(os.getenv('COVERAGE_MIN', '0.70')) else '<'} min {os.getenv('COVERAGE_MIN', '0.70')}",
            }
  ```
- Line 231: `COVERAGE_MIN`
  ```python
  "threshold": float(os.getenv("COVERAGE_MIN", "0.70")),
                "passed": cov >= float(os.getenv("COVERAGE_MIN", "0.70")),
                "message": f"Query coverage {cov:.2f} {'≥' if cov >= float(os.getenv('COVERAGE_MIN', '0.70')) else '<'} min {os.getenv('COVERAGE_MIN', '0.70')}",
            }
  ```
- Line 231: `COVERAGE_MIN`
  ```python
  "threshold": float(os.getenv("COVERAGE_MIN", "0.70")),
                "passed": cov >= float(os.getenv("COVERAGE_MIN", "0.70")),
                "message": f"Query coverage {cov:.2f} {'≥' if cov >= float(os.getenv('COVERAGE_MIN', '0.70')) else '<'} min {os.getenv('COVERAGE_MIN', '0.70')}",
            }
  ```
- Line 239: `BM25_MIN`
  ```python
  "metric": "bm25_breadth",
                    "value": bm25_hits,
                    "threshold": int(os.getenv("BM25_MIN", "50")),
                    "passed": bm25_hits >= int(os.getenv("BM25_MIN", "50")),
                    "message": f"BM25 breadth {bm25_hits} {'≥' if bm25_hits >= int(os.getenv('BM25_MIN', '50')) else '<'} min {os.getenv('BM25_MIN', '50')}",
  ```
- Line 240: `BM25_MIN`
  ```python
  "value": bm25_hits,
                    "threshold": int(os.getenv("BM25_MIN", "50")),
                    "passed": bm25_hits >= int(os.getenv("BM25_MIN", "50")),
                    "message": f"BM25 breadth {bm25_hits} {'≥' if bm25_hits >= int(os.getenv('BM25_MIN', '50')) else '<'} min {os.getenv('BM25_MIN', '50')}",
                }
  ```
- Line 241: `BM25_MIN`
  ```python
  "threshold": int(os.getenv("BM25_MIN", "50")),
                    "passed": bm25_hits >= int(os.getenv("BM25_MIN", "50")),
                    "message": f"BM25 breadth {bm25_hits} {'≥' if bm25_hits >= int(os.getenv('BM25_MIN', '50')) else '<'} min {os.getenv('BM25_MIN', '50')}",
                }
  ```
- Line 241: `BM25_MIN`
  ```python
  "threshold": int(os.getenv("BM25_MIN", "50")),
                    "passed": bm25_hits >= int(os.getenv("BM25_MIN", "50")),
                    "message": f"BM25 breadth {bm25_hits} {'≥' if bm25_hits >= int(os.getenv('BM25_MIN', '50')) else '<'} min {os.getenv('BM25_MIN', '50')}",
                }
  ```
- Line 248: `VEC_MIN`
  ```python
  "metric": "vec_breadth",
                    "value": vec_hits,
                    "threshold": int(os.getenv("VEC_MIN", "50")),
                    "passed": vec_hits >= int(os.getenv("VEC_MIN", "50")),
                    "message": f"Vector breadth {vec_hits} {'≥' if vec_hits >= int(os.getenv('VEC_MIN', '50')) else '<'} min {os.getenv('VEC_MIN', '50')}",
  ```
- Line 249: `VEC_MIN`
  ```python
  "value": vec_hits,
                    "threshold": int(os.getenv("VEC_MIN", "50")),
                    "passed": vec_hits >= int(os.getenv("VEC_MIN", "50")),
                    "message": f"Vector breadth {vec_hits} {'≥' if vec_hits >= int(os.getenv('VEC_MIN', '50')) else '<'} min {os.getenv('VEC_MIN', '50')}",
                }
  ```
- Line 250: `VEC_MIN`
  ```python
  "threshold": int(os.getenv("VEC_MIN", "50")),
                    "passed": vec_hits >= int(os.getenv("VEC_MIN", "50")),
                    "message": f"Vector breadth {vec_hits} {'≥' if vec_hits >= int(os.getenv('VEC_MIN', '50')) else '<'} min {os.getenv('VEC_MIN', '50')}",
                }
  ```
- Line 250: `VEC_MIN`
  ```python
  "threshold": int(os.getenv("VEC_MIN", "50")),
                    "passed": vec_hits >= int(os.getenv("VEC_MIN", "50")),
                    "message": f"Vector breadth {vec_hits} {'≥' if vec_hits >= int(os.getenv('VEC_MIN', '50')) else '<'} min {os.getenv('VEC_MIN', '50')}",
                }
  ```
- Line 257: `FUSED_MIN`
  ```python
  "metric": "fused_breadth",
                    "value": fused_max,
                    "threshold": int(os.getenv("FUSED_MIN", "80")),
                    "passed": fused_max >= int(os.getenv("FUSED_MIN", "80")),
                    "message": f"Fused pool max {fused_max} {'≥' if fused_max >= int(os.getenv('FUSED_MIN', '80')) else '<'} min {os.getenv('FUSED_MIN', '80')}",
  ```
- Line 258: `FUSED_MIN`
  ```python
  "value": fused_max,
                    "threshold": int(os.getenv("FUSED_MIN", "80")),
                    "passed": fused_max >= int(os.getenv("FUSED_MIN", "80")),
                    "message": f"Fused pool max {fused_max} {'≥' if fused_max >= int(os.getenv('FUSED_MIN', '80')) else '<'} min {os.getenv('FUSED_MIN', '80')}",
                }
  ```
- Line 259: `FUSED_MIN`
  ```python
  "threshold": int(os.getenv("FUSED_MIN", "80")),
                    "passed": fused_max >= int(os.getenv("FUSED_MIN", "80")),
                    "message": f"Fused pool max {fused_max} {'≥' if fused_max >= int(os.getenv('FUSED_MIN', '80')) else '<'} min {os.getenv('FUSED_MIN', '80')}",
                }
  ```
- Line 259: `FUSED_MIN`
  ```python
  "threshold": int(os.getenv("FUSED_MIN", "80")),
                    "passed": fused_max >= int(os.getenv("FUSED_MIN", "80")),
                    "message": f"Fused pool max {fused_max} {'≥' if fused_max >= int(os.getenv('FUSED_MIN', '80')) else '<'} min {os.getenv('FUSED_MIN', '80')}",
                }
  ```

### scripts/gate_new_cases.py
- Line 20: `CANDIDATE_FILE`
  ```python
  from dspy_modules.retriever.rerank import mmr_rerank, per_file_cap

CASE_FILE = os.getenv("CANDIDATE_FILE", "evals/candidates.jsonl")
TOPK_MIN_HIT = int(os.getenv("GATE_TOPK_MIN_HIT", "1"))  # ≥1 gold file in topK
COVER_MIN = float(os.getenv("GATE_COVER_MIN", "0.10"))  # ≥10% token overlap in top 2 sentences
  ```
- Line 21: `GATE_TOPK_MIN_HIT`
  ```python
  CASE_FILE = os.getenv("CANDIDATE_FILE", "evals/candidates.jsonl")
TOPK_MIN_HIT = int(os.getenv("GATE_TOPK_MIN_HIT", "1"))  # ≥1 gold file in topK
COVER_MIN = float(os.getenv("GATE_COVER_MIN", "0.10"))  # ≥10% token overlap in top 2 sentences
TOPK = int(os.getenv("GATE_TOPK", "25"))  # eval with your per-tag topk
  ```
- Line 22: `GATE_COVER_MIN`
  ```python
  CASE_FILE = os.getenv("CANDIDATE_FILE", "evals/candidates.jsonl")
TOPK_MIN_HIT = int(os.getenv("GATE_TOPK_MIN_HIT", "1"))  # ≥1 gold file in topK
COVER_MIN = float(os.getenv("GATE_COVER_MIN", "0.10"))  # ≥10% token overlap in top 2 sentences
TOPK = int(os.getenv("GATE_TOPK", "25"))  # eval with your per-tag topk
  ```
- Line 23: `GATE_TOPK`
  ```python
  TOPK_MIN_HIT = int(os.getenv("GATE_TOPK_MIN_HIT", "1"))  # ≥1 gold file in topK
COVER_MIN = float(os.getenv("GATE_COVER_MIN", "0.10"))  # ≥10% token overlap in top 2 sentences
TOPK = int(os.getenv("GATE_TOPK", "25"))  # eval with your per-tag topk
  ```

### scripts/generate_reader_gold_bootstrap.py
- Line 19: `DATABASE_URL`
  ```python
  from psycopg2.extras import DictCursor

DSN = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_DSN")
OUT = os.getenv("OUT_FILE", "evals/reader_gold_bootstrap.jsonl")
MAX_PER_TAG = int(os.getenv("MAX_PER_TAG", "60"))
  ```
- Line 19: `POSTGRES_DSN`
  ```python
  from psycopg2.extras import DictCursor

DSN = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_DSN")
OUT = os.getenv("OUT_FILE", "evals/reader_gold_bootstrap.jsonl")
MAX_PER_TAG = int(os.getenv("MAX_PER_TAG", "60"))
  ```
- Line 20: `OUT_FILE`
  ```python
  DSN = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_DSN")
OUT = os.getenv("OUT_FILE", "evals/reader_gold_bootstrap.jsonl")
MAX_PER_TAG = int(os.getenv("MAX_PER_TAG", "60"))
SEED = int(os.getenv("SEED", "42"))
  ```
- Line 21: `MAX_PER_TAG`
  ```python
  DSN = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_DSN")
OUT = os.getenv("OUT_FILE", "evals/reader_gold_bootstrap.jsonl")
MAX_PER_TAG = int(os.getenv("MAX_PER_TAG", "60"))
SEED = int(os.getenv("SEED", "42"))
  ```
- Line 22: `SEED`
  ```python
  OUT = os.getenv("OUT_FILE", "evals/reader_gold_bootstrap.jsonl")
MAX_PER_TAG = int(os.getenv("MAX_PER_TAG", "60"))
SEED = int(os.getenv("SEED", "42"))

TAG_RULES = [
  ```

### scripts/generate_reader_gold_from_db.py
- Line 32: `POSTGRES_DSN`
  ```python
  def get_db_connection():
    """Get database connection from environment or default."""
    dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
    # Handle mock DSN for testing
    if dsn.startswith("mock://"):
  ```

### scripts/generation_cache_schema_migration.py
- Line 38: `POSTGRES_DSN`
  ```python
  # Database configuration - simplified for this script
def get_database_url():
    return os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
  ```
- Line 463: `MIGRATION_TEST_MODE`
  ```python
  try:
        # Check if running in test mode
        test_mode = os.getenv("MIGRATION_TEST_MODE", "false").lower() == "true"

        if test_mode:
  ```

### scripts/health_gated_evaluation.py
- Line 39: `HEALTH_CHECK_ENV`
  ```python
  self.warning_checks = []
        self.checks_enabled = {
            "env_validation": os.getenv("HEALTH_CHECK_ENV", "1") == "1",
            "index_present": os.getenv("HEALTH_CHECK_INDEX", "1") == "1",
            "token_budget": os.getenv("HEALTH_CHECK_TOKEN_BUDGET", "1") == "1",
  ```
- Line 40: `HEALTH_CHECK_INDEX`
  ```python
  self.checks_enabled = {
            "env_validation": os.getenv("HEALTH_CHECK_ENV", "1") == "1",
            "index_present": os.getenv("HEALTH_CHECK_INDEX", "1") == "1",
            "token_budget": os.getenv("HEALTH_CHECK_TOKEN_BUDGET", "1") == "1",
            "prefix_leakage": os.getenv("HEALTH_CHECK_PREFIX_LEAKAGE", "1") == "1",
  ```
- Line 41: `HEALTH_CHECK_TOKEN_BUDGET`
  ```python
  "env_validation": os.getenv("HEALTH_CHECK_ENV", "1") == "1",
            "index_present": os.getenv("HEALTH_CHECK_INDEX", "1") == "1",
            "token_budget": os.getenv("HEALTH_CHECK_TOKEN_BUDGET", "1") == "1",
            "prefix_leakage": os.getenv("HEALTH_CHECK_PREFIX_LEAKAGE", "1") == "1",
            "database_connectivity": os.getenv("HEALTH_CHECK_DB", "1") == "1",
  ```
- Line 42: `HEALTH_CHECK_PREFIX_LEAKAGE`
  ```python
  "index_present": os.getenv("HEALTH_CHECK_INDEX", "1") == "1",
            "token_budget": os.getenv("HEALTH_CHECK_TOKEN_BUDGET", "1") == "1",
            "prefix_leakage": os.getenv("HEALTH_CHECK_PREFIX_LEAKAGE", "1") == "1",
            "database_connectivity": os.getenv("HEALTH_CHECK_DB", "1") == "1",
            "model_availability": os.getenv("HEALTH_CHECK_MODELS", "1") == "1",
  ```
- Line 43: `HEALTH_CHECK_DB`
  ```python
  "token_budget": os.getenv("HEALTH_CHECK_TOKEN_BUDGET", "1") == "1",
            "prefix_leakage": os.getenv("HEALTH_CHECK_PREFIX_LEAKAGE", "1") == "1",
            "database_connectivity": os.getenv("HEALTH_CHECK_DB", "1") == "1",
            "model_availability": os.getenv("HEALTH_CHECK_MODELS", "1") == "1",
            "config_validation": os.getenv("HEALTH_CHECK_CONFIG", "1") == "1",
  ```
- Line 44: `HEALTH_CHECK_MODELS`
  ```python
  "prefix_leakage": os.getenv("HEALTH_CHECK_PREFIX_LEAKAGE", "1") == "1",
            "database_connectivity": os.getenv("HEALTH_CHECK_DB", "1") == "1",
            "model_availability": os.getenv("HEALTH_CHECK_MODELS", "1") == "1",
            "config_validation": os.getenv("HEALTH_CHECK_CONFIG", "1") == "1",
            "resource_availability": os.getenv("HEALTH_CHECK_RESOURCES", "1") == "1",
  ```
- Line 45: `HEALTH_CHECK_CONFIG`
  ```python
  "database_connectivity": os.getenv("HEALTH_CHECK_DB", "1") == "1",
            "model_availability": os.getenv("HEALTH_CHECK_MODELS", "1") == "1",
            "config_validation": os.getenv("HEALTH_CHECK_CONFIG", "1") == "1",
            "resource_availability": os.getenv("HEALTH_CHECK_RESOURCES", "1") == "1",
        }
  ```
- Line 46: `HEALTH_CHECK_RESOURCES`
  ```python
  "model_availability": os.getenv("HEALTH_CHECK_MODELS", "1") == "1",
            "config_validation": os.getenv("HEALTH_CHECK_CONFIG", "1") == "1",
            "resource_availability": os.getenv("HEALTH_CHECK_RESOURCES", "1") == "1",
        }
  ```
- Line 110: `DSPY_RAG_PATH`
  ```python
  # Check if DSPy RAG system path exists
        dspy_rag_path = os.getenv("DSPY_RAG_PATH", "src")
        if not os.path.exists(dspy_rag_path):
            self.failed_checks.append(f"DSPy RAG system path not found: {dspy_rag_path}")
  ```
- Line 116: `EVAL_CASES_FILE`
  ```python
  # Check if evaluation cases exist
        eval_cases_file = os.getenv("EVAL_CASES_FILE", "datasets/eval_cases.jsonl")
        if not os.path.exists(eval_cases_file):
            self.failed_checks.append(f"Evaluation cases file not found: {eval_cases_file}")
  ```
- Line 142: `MAX_TOKENS`
  ```python
  # Check if token limits are reasonable
        max_tokens = int(os.getenv("MAX_TOKENS", "1024"))
        if max_tokens > 4096:
            self.warning_checks.append(f"High token limit: {max_tokens} (may cause performance issues)")
  ```
- Line 147: `CONTEXT_MAX_CHARS`
  ```python
  # Check context limits
        context_max_chars = int(os.getenv("CONTEXT_MAX_CHARS", "1600"))
        if context_max_chars > 8000:
            self.warning_checks.append(f"High context limit: {context_max_chars} characters")
  ```
- Line 159: `BM25_TEXT_FIELD`
  ```python
  # This would check if BM25 text contains evaluation prefixes
        # For now, just validate the configuration
        bm25_text_field = os.getenv("BM25_TEXT_FIELD", "bm25_text")
        embedding_text_field = os.getenv("EMBEDDING_TEXT_FIELD", "embedding_text")
  ```
- Line 160: `EMBEDDING_TEXT_FIELD`
  ```python
  # For now, just validate the configuration
        bm25_text_field = os.getenv("BM25_TEXT_FIELD", "bm25_text")
        embedding_text_field = os.getenv("EMBEDDING_TEXT_FIELD", "embedding_text")

        if bm25_text_field == embedding_text_field:
  ```
- Line 202: `EMBEDDING_MODEL`
  ```python
  # Check embedding model
        embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        try:
            from sentence_transformers import SentenceTransformer
  ```
- Line 212: `RERANK_ENABLE`
  ```python
  # Check rerank model if enabled
        if os.getenv("RERANK_ENABLE", "1") == "1":
            rerank_model = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")
            try:
  ```
- Line 213: `RERANK_MODEL`
  ```python
  # Check rerank model if enabled
        if os.getenv("RERANK_ENABLE", "1") == "1":
            rerank_model = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")
            try:
                from sentence_transformers import CrossEncoder
  ```
- Line 227: `RETR_TOPK_VEC`
  ```python
  # Check retrieval parameters
        topk_vec = int(os.getenv("RETR_TOPK_VEC", "140"))
        topk_bm25 = int(os.getenv("RETR_TOPK_BM25", "140"))
  ```
- Line 228: `RETR_TOPK_BM25`
  ```python
  # Check retrieval parameters
        topk_vec = int(os.getenv("RETR_TOPK_VEC", "140"))
        topk_bm25 = int(os.getenv("RETR_TOPK_BM25", "140"))

        if topk_vec > 500:
  ```
- Line 237: `RERANK_ENABLE`
  ```python
  # Check reranking parameters
        if os.getenv("RERANK_ENABLE", "1") == "1":
            rerank_pool = int(os.getenv("RERANK_POOL", "60"))
            if rerank_pool > 200:
  ```
- Line 238: `RERANK_POOL`
  ```python
  # Check reranking parameters
        if os.getenv("RERANK_ENABLE", "1") == "1":
            rerank_pool = int(os.getenv("RERANK_POOL", "60"))
            if rerank_pool > 200:
                self.warning_checks.append(f"High rerank pool size: {rerank_pool}")
  ```
- Line 243: `BEDROCK_MAX_IN_FLIGHT`
  ```python
  # Check performance parameters
        max_in_flight = int(os.getenv("BEDROCK_MAX_IN_FLIGHT", "1"))
        if max_in_flight > 3:
            self.warning_checks.append(f"High concurrency: {max_in_flight} (may cause rate limiting)")
  ```

### scripts/make_cases_from_eval_gold.py
- Line 60: `CASES_FILE`
  ```python
  for q, target in merged.items():
        out.append(to_case(q, target))
    path = os.getenv("CASES_FILE", str(ROOT / "evals" / "gold_cases.json"))
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
  ```

### scripts/manual_index_retriever.py
- Line 129: `POSTGRES_DSN`
  ```python
  def main():
    dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
    retriever_dir = Path("src/dspy_modules/retriever")
  ```

### scripts/mcp_memory_server.py
- Line 636: `PYTHONPATH`
  ```python
  print(f"🔧 MCP tools: http://{args.host}:{args.port}/mcp/tools")
    # Helpful import diagnostics
    print(f"🧩 PYTHONPATH={os.environ.get('PYTHONPATH', '')}")
    try:
        print(f"🧭 sys.path[:3]={sys.path[:3]}")
  ```

### scripts/memory_healthcheck.py
- Line 48: `DATABASE_URL`
  ```python
  def check_database() -> Dict[str, Any]:
    dsn = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_DSN") or ""
    offline = os.getenv("MEMORY_HEALTHCHECK_OFFLINE", "0") == "1" or dsn.startswith("mock://")
    if offline:
  ```
- Line 48: `POSTGRES_DSN`
  ```python
  def check_database() -> Dict[str, Any]:
    dsn = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_DSN") or ""
    offline = os.getenv("MEMORY_HEALTHCHECK_OFFLINE", "0") == "1" or dsn.startswith("mock://")
    if offline:
  ```
- Line 49: `MEMORY_HEALTHCHECK_OFFLINE`
  ```python
  def check_database() -> Dict[str, Any]:
    dsn = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_DSN") or ""
    offline = os.getenv("MEMORY_HEALTHCHECK_OFFLINE", "0") == "1" or dsn.startswith("mock://")
    if offline:
        return {
  ```
- Line 97: `MEMORY_HEALTHCHECK_OFFLINE`
  ```python
  store = EpisodicReflectionStore()
        stats = store.get_stats()  # may fallback to zeros in offline/mock
        offline = os.getenv("MEMORY_HEALTHCHECK_OFFLINE", "0") == "1"
        status = "healthy" if (stats or offline) else "degraded"
        return {
  ```
- Line 106: `MEMORY_HEALTHCHECK_OFFLINE`
  ```python
  }
    except Exception as e:
        if os.getenv("MEMORY_HEALTHCHECK_OFFLINE", "0") == "1":
            return {
                "component": "episodic",
  ```
- Line 126: `MEMORY_HEALTHCHECK_OFFLINE`
  ```python
  return {
        "component": "cursor_rehydrator",
        "status": "healthy" if ok or os.getenv("MEMORY_HEALTHCHECK_OFFLINE", "0") == "1" else "error",
        "output": out if ok else (err or "offline/mock mode"),
    }
  ```
- Line 267: `MEMORY_HEALTHCHECK_OFFLINE`
  ```python
  if args.offline:
        os.environ["MEMORY_HEALTHCHECK_OFFLINE"] = "1"

    results: Dict[str, Any] = {"timestamp": time.time()}
  ```

### scripts/migrate_to_pydantic_settings.py
- Line 93: `VAR`
  ```python
  def _find_env_var_references(self, content: str):
        """Find environment variable references in the content."""
        # Look for patterns like os.environ['VAR'] or os.environ.get('VAR')
        patterns = [
            r'os\.environ\[["\']([^"\']+)["\']\]',
  ```
- Line 93: `VAR`
  ```python
  def _find_env_var_references(self, content: str):
        """Find environment variable references in the content."""
        # Look for patterns like os.environ['VAR'] or os.environ.get('VAR')
        patterns = [
            r'os\.environ\[["\']([^"\']+)["\']\]',
  ```
- Line 200: `DB_CONNECT_TIMEOUT`
  ```python
  examples.append("import os")
        examples.append("")
        examples.append("db_timeout = int(os.getenv('DB_CONNECT_TIMEOUT', 10))")
        examples.append("aws_region = os.getenv('AWS_REGION', 'us-east-1')")
        examples.append("chunk_size = int(os.getenv('CHUNK_SIZE', 450))")
  ```
- Line 201: `AWS_REGION`
  ```python
  examples.append("")
        examples.append("db_timeout = int(os.getenv('DB_CONNECT_TIMEOUT', 10))")
        examples.append("aws_region = os.getenv('AWS_REGION', 'us-east-1')")
        examples.append("chunk_size = int(os.getenv('CHUNK_SIZE', 450))")
        examples.append("```")
  ```
- Line 202: `CHUNK_SIZE`
  ```python
  examples.append("db_timeout = int(os.getenv('DB_CONNECT_TIMEOUT', 10))")
        examples.append("aws_region = os.getenv('AWS_REGION', 'us-east-1')")
        examples.append("chunk_size = int(os.getenv('CHUNK_SIZE', 450))")
        examples.append("```")
        examples.append("")
  ```

### scripts/nightly_smoke_evaluation.py
- Line 220: `EMBEDDING_MODEL`
  ```python
  from sentence_transformers import SentenceTransformer

            embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            model = SentenceTransformer(embedding_model)
            test_embedding = model.encode(["test"])
  ```
- Line 225: `RERANK_ENABLE`
  ```python
  # Test rerank model if enabled
            if os.getenv("RERANK_ENABLE", "1") == "1":
                from sentence_transformers import CrossEncoder
  ```
- Line 228: `RERANK_MODEL`
  ```python
  from sentence_transformers import CrossEncoder

                rerank_model = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")
                reranker = CrossEncoder(rerank_model)
                test_score = reranker.predict([("query", "document")])
  ```
- Line 375: `EVAL_CASES_FILE`
  ```python
  try:
            # Check if evaluation files exist
            eval_cases_file = os.getenv("EVAL_CASES_FILE", "datasets/eval_cases.jsonl")
            if os.path.exists(eval_cases_file):
                return {"status": "pass", "message": "Evaluation pipeline ready"}
  ```

### scripts/nli_borderline_gate.py
- Line 32: `RAGCHECKER_NLI_ENABLE`
  ```python
  # Configuration from environment
        self.enabled = os.getenv("RAGCHECKER_NLI_ENABLE", "0") == "1"
        self.borderline_only = os.getenv("RAGCHECKER_NLI_ON_BORDERLINE", "1") == "1"
        self.borderline_band = float(os.getenv("RAGCHECKER_BORDERLINE_BAND", "0.02"))
  ```
- Line 33: `RAGCHECKER_NLI_ON_BORDERLINE`
  ```python
  # Configuration from environment
        self.enabled = os.getenv("RAGCHECKER_NLI_ENABLE", "0") == "1"
        self.borderline_only = os.getenv("RAGCHECKER_NLI_ON_BORDERLINE", "1") == "1"
        self.borderline_band = float(os.getenv("RAGCHECKER_BORDERLINE_BAND", "0.02"))
        self.nli_threshold = float(os.getenv("RAGCHECKER_NLI_P_THRESHOLD", "0.60"))
  ```
- Line 34: `RAGCHECKER_BORDERLINE_BAND`
  ```python
  self.enabled = os.getenv("RAGCHECKER_NLI_ENABLE", "0") == "1"
        self.borderline_only = os.getenv("RAGCHECKER_NLI_ON_BORDERLINE", "1") == "1"
        self.borderline_band = float(os.getenv("RAGCHECKER_BORDERLINE_BAND", "0.02"))
        self.nli_threshold = float(os.getenv("RAGCHECKER_NLI_P_THRESHOLD", "0.60"))
  ```
- Line 35: `RAGCHECKER_NLI_P_THRESHOLD`
  ```python
  self.borderline_only = os.getenv("RAGCHECKER_NLI_ON_BORDERLINE", "1") == "1"
        self.borderline_band = float(os.getenv("RAGCHECKER_BORDERLINE_BAND", "0.02"))
        self.nli_threshold = float(os.getenv("RAGCHECKER_NLI_P_THRESHOLD", "0.60"))

        # Initialize model if enabled
  ```
- Line 199: `RAGCHECKER_EVIDENCE_JACCARD`
  ```python
  # Get threshold
        threshold = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07"))

        # Apply NLI gate to borderline sentences
  ```
- Line 245: `RAGCHECKER_NLI_ENABLE`
  ```python
  # Enable NLI gate
    os.environ["RAGCHECKER_NLI_ENABLE"] = "1"

    nli_gate = BorderlineNLIGate()
  ```

### scripts/ops_rhythm_system.py
- Line 334: `CONFIG_HASH`
  ```python
  def _version_few_shots(self) -> Dict[str, Any]:
        """Version few-shots under CONFIG_HASH."""
        config_hash = os.getenv("CONFIG_HASH", "default")

        try:
  ```

### scripts/phase2_kickstart.py
- Line 312: `CONFIG_HASH`
  ```python
  """Save compiled artifacts under CONFIG_HASH."""
        try:
            config_hash = os.getenv("CONFIG_HASH", "default")
            compiled_artifacts_dir = Path("compiled_artifacts") / config_hash
  ```

### scripts/postgresql_cache_service.py
- Line 36: `POSTGRES_DSN`
  ```python
  # Database configuration - simplified for this script
def get_database_url():
    return os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
  ```

### scripts/production_deployment_validation.py
- Line 1109: `DATABASE_URL`
  ```python
  # Create production configuration
        config = ProductionConfig(
            database_url=os.getenv("DATABASE_URL", "postgresql://localhost:5432/ai_agency"),
            max_connections=20,
            connection_timeout=30,
  ```

### scripts/ragchecker_enhanced_with_limit_features.py
- Line 46: `RAGCHECKER_ROUTE_BM25_MARGIN`
  ```python
  """Initialize geometry failure router."""
        return {
            "margin_threshold": float(os.getenv("RAGCHECKER_ROUTE_BM25_MARGIN", "0.20")),
            "agreement_threshold": float(os.getenv("RAGCHECKER_REWRITE_AGREE_STRONG", "0.50")),
        }
  ```
- Line 47: `RAGCHECKER_REWRITE_AGREE_STRONG`
  ```python
  return {
            "margin_threshold": float(os.getenv("RAGCHECKER_ROUTE_BM25_MARGIN", "0.20")),
            "agreement_threshold": float(os.getenv("RAGCHECKER_REWRITE_AGREE_STRONG", "0.50")),
        }
  ```
- Line 53: `RAGCHECKER_REWRITE_K`
  ```python
  """Initialize facet selector with yield-based filtering."""
        return {
            "max_facets": int(os.getenv("RAGCHECKER_REWRITE_K", "4")),
            "keep_facets": int(os.getenv("RAGCHECKER_REWRITE_KEEP", "2")),
            "min_yield": float(os.getenv("RAGCHECKER_REWRITE_YIELD_MIN", "1.5")),
  ```
- Line 54: `RAGCHECKER_REWRITE_KEEP`
  ```python
  return {
            "max_facets": int(os.getenv("RAGCHECKER_REWRITE_K", "4")),
            "keep_facets": int(os.getenv("RAGCHECKER_REWRITE_KEEP", "2")),
            "min_yield": float(os.getenv("RAGCHECKER_REWRITE_YIELD_MIN", "1.5")),
        }
  ```
- Line 55: `RAGCHECKER_REWRITE_YIELD_MIN`
  ```python
  "max_facets": int(os.getenv("RAGCHECKER_REWRITE_K", "4")),
            "keep_facets": int(os.getenv("RAGCHECKER_REWRITE_KEEP", "2")),
            "min_yield": float(os.getenv("RAGCHECKER_REWRITE_YIELD_MIN", "1.5")),
        }
  ```
- Line 69: `RAGCHECKER_EVIDENCE_JACCARD`
  ```python
  """Initialize support validator for two-of-three rule."""
        return {
            "evidence_jaccard": float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07")),
            "evidence_coverage": float(os.getenv("RAGCHECKER_EVIDENCE_COVERAGE", "0.20")),
            "cosine_floor": float(os.getenv("RAGCHECKER_COSINE_FLOOR", "0.58")),
  ```
- Line 70: `RAGCHECKER_EVIDENCE_COVERAGE`
  ```python
  return {
            "evidence_jaccard": float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07")),
            "evidence_coverage": float(os.getenv("RAGCHECKER_EVIDENCE_COVERAGE", "0.20")),
            "cosine_floor": float(os.getenv("RAGCHECKER_COSINE_FLOOR", "0.58")),
            "numeric_must_match": os.getenv("RAGCHECKER_NUMERIC_MUST_MATCH", "1") == "1",
  ```
- Line 71: `RAGCHECKER_COSINE_FLOOR`
  ```python
  "evidence_jaccard": float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07")),
            "evidence_coverage": float(os.getenv("RAGCHECKER_EVIDENCE_COVERAGE", "0.20")),
            "cosine_floor": float(os.getenv("RAGCHECKER_COSINE_FLOOR", "0.58")),
            "numeric_must_match": os.getenv("RAGCHECKER_NUMERIC_MUST_MATCH", "1") == "1",
            "entity_must_match": os.getenv("RAGCHECKER_ENTITY_MUST_MATCH", "1") == "1",
  ```
- Line 72: `RAGCHECKER_NUMERIC_MUST_MATCH`
  ```python
  "evidence_coverage": float(os.getenv("RAGCHECKER_EVIDENCE_COVERAGE", "0.20")),
            "cosine_floor": float(os.getenv("RAGCHECKER_COSINE_FLOOR", "0.58")),
            "numeric_must_match": os.getenv("RAGCHECKER_NUMERIC_MUST_MATCH", "1") == "1",
            "entity_must_match": os.getenv("RAGCHECKER_ENTITY_MUST_MATCH", "1") == "1",
        }
  ```
- Line 73: `RAGCHECKER_ENTITY_MUST_MATCH`
  ```python
  "cosine_floor": float(os.getenv("RAGCHECKER_COSINE_FLOOR", "0.58")),
            "numeric_must_match": os.getenv("RAGCHECKER_NUMERIC_MUST_MATCH", "1") == "1",
            "entity_must_match": os.getenv("RAGCHECKER_ENTITY_MUST_MATCH", "1") == "1",
        }
  ```
- Line 294: `RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR`
  ```python
  for doc in fused_docs:
            if not doc["has_query_anchors"]:
                doc["score"] *= float(os.getenv("RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR", "0.80"))
            else:
                doc["score"] *= float(os.getenv("RAGCHECKER_BM25_BOOST_ANCHORS", "1.6"))
  ```
- Line 296: `RAGCHECKER_BM25_BOOST_ANCHORS`
  ```python
  doc["score"] *= float(os.getenv("RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR", "0.80"))
            else:
                doc["score"] *= float(os.getenv("RAGCHECKER_BM25_BOOST_ANCHORS", "1.6"))

        # Apply MMR diversification
  ```
- Line 303: `RAGCHECKER_PER_DOC_LINE_CAP`
  ```python
  # Apply per-doc line cap
        final_docs = self._enforce_per_doc_line_cap(
            diversified_docs, int(os.getenv("RAGCHECKER_PER_DOC_LINE_CAP", "8"))
        )
  ```
- Line 306: `RAGCHECKER_CONTEXT_TOPK`
  ```python
  )

        return final_docs[: int(os.getenv("RAGCHECKER_CONTEXT_TOPK", "14"))]

    def _apply_rrf_fusion(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
  ```
- Line 310: `RAGCHECKER_RRF_K`
  ```python
  def _apply_rrf_fusion(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply Reciprocal Rank Fusion."""
        rrf_k = int(os.getenv("RAGCHECKER_RRF_K", "60"))

        # Group docs by source and calculate RRF scores
  ```
- Line 331: `RAGCHECKER_MMR_LAMBDA`
  ```python
  def _apply_mmr_diversification(self, docs: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Apply Maximal Marginal Relevance diversification."""
        mmr_lambda = float(os.getenv("RAGCHECKER_MMR_LAMBDA", "0.65"))

        # Simulate MMR diversification
  ```

### scripts/ragchecker_final_precision_push_evaluation.py
- Line 287: `RAGCHECKER_FAST_MODE`
  ```python
  # Set fast mode if requested
    if args.fast_mode:
        os.environ["RAGCHECKER_FAST_MODE"] = "1"

    # Initialize evaluator
  ```

### scripts/ragchecker_final_ragas_push_evaluation.py
- Line 156: `RAGCHECKER_EVIDENCE_JACCARD`
  ```python
  # Get thresholds from environment
        jaccard_threshold = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07"))
        rouge_threshold = float(os.getenv("ROUGE_FLOOR", "0.20"))
        cosine_threshold = float(os.getenv("COS_FLOOR", "0.58"))
  ```
- Line 157: `ROUGE_FLOOR`
  ```python
  # Get thresholds from environment
        jaccard_threshold = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07"))
        rouge_threshold = float(os.getenv("ROUGE_FLOOR", "0.20"))
        cosine_threshold = float(os.getenv("COS_FLOOR", "0.58"))
  ```
- Line 158: `COS_FLOOR`
  ```python
  jaccard_threshold = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07"))
        rouge_threshold = float(os.getenv("ROUGE_FLOOR", "0.20"))
        cosine_threshold = float(os.getenv("COS_FLOOR", "0.58"))

        # Count passing signals
  ```
- Line 191: `RAGCHECKER_NLI_ENABLE`
  ```python
  """Enhanced evidence filter with all three moves."""
        # Check if NLI gate is enabled and available
        if os.getenv("RAGCHECKER_NLI_ENABLE", "0") == "1" and self.nli_enhanced_filter and self.nli_gate:
            print("🔄 Using NLI-enhanced filtering")
            return self.nli_enhanced_filter.filter_with_nli_gate(answer, contexts)
  ```
- Line 196: `RAGCHECKER_CROSS_ENCODER_ENABLED`
  ```python
  # Check if cross-encoder is enabled and available
        if os.getenv("RAGCHECKER_CROSS_ENCODER_ENABLED", "0") == "1" and self.enhanced_filter and self.cross_encoder:
            print("🔄 Using cross-encoder enhanced filtering")
            return self.enhanced_filter.filter_with_cross_encoder(answer, contexts, query)
  ```

### scripts/ragchecker_limit_inspired_evaluation.py
- Line 317: `RAGCHECKER_FAST_MODE`
  ```python
  # Set fast mode if requested
    if args.fast_mode:
        os.environ["RAGCHECKER_FAST_MODE"] = "1"

    # Initialize evaluator
  ```

### scripts/ragchecker_official_evaluation.py
- Line 112: `EVAL_SUITE`
  ```python
  from evals_300.tools.run import run as ssot_run

    suite = os.environ.get("EVAL_SUITE", "300_core")
    pass_id = os.environ.get("EVAL_PASS", "reranker_ablation_suite")
  ```
- Line 113: `EVAL_PASS`
  ```python
  suite = os.environ.get("EVAL_SUITE", "300_core")
    pass_id = os.environ.get("EVAL_PASS", "reranker_ablation_suite")

    try:
  ```
- Line 116: `EVAL_CONCURRENCY`
  ```python
  try:
        conc_env = os.environ.get("EVAL_CONCURRENCY")
        concurrency = int(conc_env) if conc_env else None
    except ValueError:
  ```

### scripts/ragchecker_precision_climb_v2_evaluation.py
- Line 158: `RAGCHECKER_EVIDENCE_JACCARD`
  ```python
  # Get thresholds from environment
        jaccard_threshold = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07"))
        rouge_threshold = float(os.getenv("ROUGE_FLOOR", "0.20"))
        cosine_threshold = float(os.getenv("COS_FLOOR", "0.58"))
  ```
- Line 159: `ROUGE_FLOOR`
  ```python
  # Get thresholds from environment
        jaccard_threshold = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07"))
        rouge_threshold = float(os.getenv("ROUGE_FLOOR", "0.20"))
        cosine_threshold = float(os.getenv("COS_FLOOR", "0.58"))
  ```
- Line 160: `COS_FLOOR`
  ```python
  jaccard_threshold = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07"))
        rouge_threshold = float(os.getenv("ROUGE_FLOOR", "0.20"))
        cosine_threshold = float(os.getenv("COS_FLOOR", "0.58"))

        # Count passing signals
  ```
- Line 193: `RAGCHECKER_CROSS_ENCODER_ENABLED`
  ```python
  """Enhanced evidence filter with risk-aware sentence filtering and cross-encoder."""
        # Check if cross-encoder is enabled and available
        if os.getenv("RAGCHECKER_CROSS_ENCODER_ENABLED", "0") == "1" and self.enhanced_filter and self.cross_encoder:
            logger.info("🔄 Using cross-encoder enhanced filtering")
            return self.enhanced_filter.filter_with_cross_encoder(answer, contexts, query)
  ```
- Line 234: `RAGCHECKER_CLAIM_CONFIDENCE_WEIGHTS`
  ```python
  # Get weights from environment
        weights_str = os.getenv("RAGCHECKER_CLAIM_CONFIDENCE_WEIGHTS", "0.4,0.3,0.3")
        weights = [float(w.strip()) for w in weights_str.split(",")]
  ```
- Line 250: `RAGCHECKER_CLAIM_CONFIDENCE_ENABLED`
  ```python
  def enhanced_claim_binding(self, answer: str, contexts: List[str]) -> str:
        """Enhanced claim binding with confidence-based ordering."""
        if not os.getenv("RAGCHECKER_CLAIM_CONFIDENCE_ENABLED", "0") == "1":
            # Fall back to base claim binding if not enabled
            return answer
  ```
- Line 270: `RAGCHECKER_MIN_WORDS_AFTER_BINDING`
  ```python
  # Keep top claims until minimum words threshold is met
        min_words = int(os.getenv("RAGCHECKER_MIN_WORDS_AFTER_BINDING", "160"))
        selected_sentences = []
        word_count = 0
  ```

### scripts/ragchecker_precision_lift_evaluation.py
- Line 302: `RAGCHECKER_FAST_MODE`
  ```python
  # Set fast mode if requested
    if args.fast_mode:
        os.environ["RAGCHECKER_FAST_MODE"] = "1"

    # Initialize evaluator
  ```

### scripts/ragchecker_precision_optimization.py
- Line 180: `RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR`
  ```python
  for doc in fused_docs:
            if not doc["has_query_anchors"]:
                doc["score"] *= float(os.getenv("RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR", "0.70"))
            else:
                doc["score"] *= float(os.getenv("RAGCHECKER_BM25_BOOST_ANCHORS", "1.8"))
  ```
- Line 182: `RAGCHECKER_BM25_BOOST_ANCHORS`
  ```python
  doc["score"] *= float(os.getenv("RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR", "0.70"))
            else:
                doc["score"] *= float(os.getenv("RAGCHECKER_BM25_BOOST_ANCHORS", "1.8"))

        # Apply stricter MMR diversification
  ```
- Line 189: `RAGCHECKER_PER_DOC_LINE_CAP`
  ```python
  # Apply stricter per-doc line cap
        final_docs = self._enforce_per_doc_line_cap(
            diversified_docs, int(os.getenv("RAGCHECKER_PER_DOC_LINE_CAP", "6"))
        )
  ```
- Line 192: `RAGCHECKER_CONTEXT_TOPK`
  ```python
  )

        return final_docs[: int(os.getenv("RAGCHECKER_CONTEXT_TOPK", "12"))]
  ```

### scripts/ragchecker_precision_recovery_evaluation.py
- Line 155: `RAGCHECKER_RETRIEVAL_HYBRID`
  ```python
  """Extract retrieval-specific metrics."""
        return {
            "hybrid_enabled": os.getenv("RAGCHECKER_RETRIEVAL_HYBRID", "0") == "1",
            "rrf_enabled": os.getenv("RAGCHECKER_USE_RRF", "0") == "1",
            "mmr_enabled": os.getenv("RAGCHECKER_USE_MMR", "0") == "1",
  ```
- Line 156: `RAGCHECKER_USE_RRF`
  ```python
  return {
            "hybrid_enabled": os.getenv("RAGCHECKER_RETRIEVAL_HYBRID", "0") == "1",
            "rrf_enabled": os.getenv("RAGCHECKER_USE_RRF", "0") == "1",
            "mmr_enabled": os.getenv("RAGCHECKER_USE_MMR", "0") == "1",
            "mmr_lambda": float(os.getenv("RAGCHECKER_MMR_LAMBDA", "0.65")),
  ```
- Line 157: `RAGCHECKER_USE_MMR`
  ```python
  "hybrid_enabled": os.getenv("RAGCHECKER_RETRIEVAL_HYBRID", "0") == "1",
            "rrf_enabled": os.getenv("RAGCHECKER_USE_RRF", "0") == "1",
            "mmr_enabled": os.getenv("RAGCHECKER_USE_MMR", "0") == "1",
            "mmr_lambda": float(os.getenv("RAGCHECKER_MMR_LAMBDA", "0.65")),
            "context_topk": int(os.getenv("RAGCHECKER_CONTEXT_TOPK", "16")),
  ```
- Line 158: `RAGCHECKER_MMR_LAMBDA`
  ```python
  "rrf_enabled": os.getenv("RAGCHECKER_USE_RRF", "0") == "1",
            "mmr_enabled": os.getenv("RAGCHECKER_USE_MMR", "0") == "1",
            "mmr_lambda": float(os.getenv("RAGCHECKER_MMR_LAMBDA", "0.65")),
            "context_topk": int(os.getenv("RAGCHECKER_CONTEXT_TOPK", "16")),
            "bm25_weight": 0.55,  # From hybrid retriever
  ```
- Line 159: `RAGCHECKER_CONTEXT_TOPK`
  ```python
  "mmr_enabled": os.getenv("RAGCHECKER_USE_MMR", "0") == "1",
            "mmr_lambda": float(os.getenv("RAGCHECKER_MMR_LAMBDA", "0.65")),
            "context_topk": int(os.getenv("RAGCHECKER_CONTEXT_TOPK", "16")),
            "bm25_weight": 0.55,  # From hybrid retriever
            "dense_weight": 0.35,  # From hybrid retriever
  ```
- Line 167: `RAGCHECKER_REWRITE_K`
  ```python
  """Extract facet query decomposition metrics."""
        return {
            "rewrite_k": int(os.getenv("RAGCHECKER_REWRITE_K", "0")),
            "rewrite_keep": int(os.getenv("RAGCHECKER_REWRITE_KEEP", "0")),
            "rewrite_yield_min": float(os.getenv("RAGCHECKER_REWRITE_YIELD_MIN", "0.0")),
  ```
- Line 168: `RAGCHECKER_REWRITE_KEEP`
  ```python
  return {
            "rewrite_k": int(os.getenv("RAGCHECKER_REWRITE_K", "0")),
            "rewrite_keep": int(os.getenv("RAGCHECKER_REWRITE_KEEP", "0")),
            "rewrite_yield_min": float(os.getenv("RAGCHECKER_REWRITE_YIELD_MIN", "0.0")),
            "facets_generated": 0,  # Will be populated by actual implementation
  ```
- Line 169: `RAGCHECKER_REWRITE_YIELD_MIN`
  ```python
  "rewrite_k": int(os.getenv("RAGCHECKER_REWRITE_K", "0")),
            "rewrite_keep": int(os.getenv("RAGCHECKER_REWRITE_KEEP", "0")),
            "rewrite_yield_min": float(os.getenv("RAGCHECKER_REWRITE_YIELD_MIN", "0.0")),
            "facets_generated": 0,  # Will be populated by actual implementation
            "facets_kept": 0,  # Will be populated by actual implementation
  ```
- Line 191: `RAGCHECKER_TARGET_K_STRONG`
  ```python
  "target_k": 0,  # Will be determined by actual implementation
            "kept_sentences": 0,  # Will be determined by actual implementation
            "target_k_strong": int(os.getenv("RAGCHECKER_TARGET_K_STRONG", "8")),
            "target_k_weak": int(os.getenv("RAGCHECKER_TARGET_K_WEAK", "3")),
        }
  ```
- Line 192: `RAGCHECKER_TARGET_K_WEAK`
  ```python
  "kept_sentences": 0,  # Will be determined by actual implementation
            "target_k_strong": int(os.getenv("RAGCHECKER_TARGET_K_STRONG", "8")),
            "target_k_weak": int(os.getenv("RAGCHECKER_TARGET_K_WEAK", "3")),
        }
  ```
- Line 201: `RAGCHECKER_CLAIM_TOPK`
  ```python
  "claims_kept": 0,  # Will be populated by actual implementation
            "final_word_count": 0,  # Will be populated by actual implementation
            "claim_topk": int(os.getenv("RAGCHECKER_CLAIM_TOPK", "3")),
            "min_words_after_binding": int(os.getenv("RAGCHECKER_MIN_WORDS_AFTER_BINDING", "140")),
        }
  ```
- Line 202: `RAGCHECKER_MIN_WORDS_AFTER_BINDING`
  ```python
  "final_word_count": 0,  # Will be populated by actual implementation
            "claim_topk": int(os.getenv("RAGCHECKER_CLAIM_TOPK", "3")),
            "min_words_after_binding": int(os.getenv("RAGCHECKER_MIN_WORDS_AFTER_BINDING", "140")),
        }
  ```
- Line 210: `RAGCHECKER_REDUNDANCY_TRIGRAM_MAX`
  ```python
  "redundant_pruned": 0,  # Will be populated by actual implementation
            "per_chunk_pruned": 0,  # Will be populated by actual implementation
            "redundancy_trigram_max": float(os.getenv("RAGCHECKER_REDUNDANCY_TRIGRAM_MAX", "0.45")),
            "per_chunk_cap": int(os.getenv("RAGCHECKER_PER_CHUNK_CAP", "2")),
        }
  ```
- Line 211: `RAGCHECKER_PER_CHUNK_CAP`
  ```python
  "per_chunk_pruned": 0,  # Will be populated by actual implementation
            "redundancy_trigram_max": float(os.getenv("RAGCHECKER_REDUNDANCY_TRIGRAM_MAX", "0.45")),
            "per_chunk_cap": int(os.getenv("RAGCHECKER_PER_CHUNK_CAP", "2")),
        }
  ```
- Line 217: `RAGCHECKER_JUDGE_MODE`
  ```python
  """Extract judge mode metrics."""
        return {
            "judge_mode": os.getenv("RAGCHECKER_JUDGE_MODE", "haiku"),
            "haiku_floors_enabled": os.getenv("RAGCHECKER_HAIKU_FLOORS", "0") == "1",
            "json_ok": True,  # Will be determined by actual implementation
  ```
- Line 218: `RAGCHECKER_HAIKU_FLOORS`
  ```python
  return {
            "judge_mode": os.getenv("RAGCHECKER_JUDGE_MODE", "haiku"),
            "haiku_floors_enabled": os.getenv("RAGCHECKER_HAIKU_FLOORS", "0") == "1",
            "json_ok": True,  # Will be determined by actual implementation
            "fallback_used": False,  # Will be determined by actual implementation
  ```
- Line 348: `RAGCHECKER_FAST_MODE`
  ```python
  # Set fast mode if requested
    if args.fast_mode:
        os.environ["RAGCHECKER_FAST_MODE"] = "1"

    # Initialize evaluator
  ```

### scripts/ragchecker_production_evaluation.py
- Line 160: `RAGCHECKER_EVIDENCE_JACCARD`
  ```python
  # Get thresholds from environment
        jaccard_threshold = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07"))
        rouge_threshold = float(os.getenv("ROUGE_FLOOR", "0.20"))
        cosine_threshold = float(os.getenv("COS_FLOOR", "0.58"))
  ```
- Line 161: `ROUGE_FLOOR`
  ```python
  # Get thresholds from environment
        jaccard_threshold = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07"))
        rouge_threshold = float(os.getenv("ROUGE_FLOOR", "0.20"))
        cosine_threshold = float(os.getenv("COS_FLOOR", "0.58"))
  ```
- Line 162: `COS_FLOOR`
  ```python
  jaccard_threshold = float(os.getenv("RAGCHECKER_EVIDENCE_JACCARD", "0.07"))
        rouge_threshold = float(os.getenv("ROUGE_FLOOR", "0.20"))
        cosine_threshold = float(os.getenv("COS_FLOOR", "0.58"))

        # Count passing signals
  ```
- Line 195: `RAGCHECKER_NLI_ENABLE`
  ```python
  """Enhanced evidence filter with all three moves."""
        # Check if NLI gate is enabled and available
        if os.getenv("RAGCHECKER_NLI_ENABLE", "0") == "1" and self.nli_enhanced_filter and self.nli_gate:
            print("🔄 Using NLI-enhanced filtering")
            return self.nli_enhanced_filter.filter_with_nli_gate(answer, contexts)
  ```
- Line 201: `RAGCHECKER_CROSS_ENCODER_ENABLED`
  ```python
  # Check if cross-encoder is enabled and available (support both env names)
        ce_enabled = (
            os.getenv("RAGCHECKER_CROSS_ENCODER_ENABLED", "0") == "1"
            or os.getenv("RAGCHECKER_CE_RERANK_ENABLE", "0") == "1"
        )
  ```
- Line 202: `RAGCHECKER_CE_RERANK_ENABLE`
  ```python
  ce_enabled = (
            os.getenv("RAGCHECKER_CROSS_ENCODER_ENABLED", "0") == "1"
            or os.getenv("RAGCHECKER_CE_RERANK_ENABLE", "0") == "1"
        )
        if ce_enabled and self.enhanced_filter and self.cross_encoder:
  ```

### scripts/reader_debug_ab.py
- Line 29: `MMR_ALPHA`
  ```python
  qs["short"], qs["title"], qs["bm25"], qvec=[], tag=tag, k=lim["shortlist"], return_components=True
    )
    rows = mmr_rerank(rows, alpha=float(os.getenv("MMR_ALPHA", "0.85")), per_file_penalty=0.10, k=lim["shortlist"])
    rows = per_file_cap(rows, cap=int(os.getenv("PER_FILE_CAP", "5")))[: lim["topk"]]
    ctx, meta = build_reader_context(rows, q, tag, compact=bool(int(os.getenv("READER_COMPACT", "1"))))
  ```
- Line 30: `PER_FILE_CAP`
  ```python
  )
    rows = mmr_rerank(rows, alpha=float(os.getenv("MMR_ALPHA", "0.85")), per_file_penalty=0.10, k=lim["shortlist"])
    rows = per_file_cap(rows, cap=int(os.getenv("PER_FILE_CAP", "5")))[: lim["topk"]]
    ctx, meta = build_reader_context(rows, q, tag, compact=bool(int(os.getenv("READER_COMPACT", "1"))))
    return ctx, rows
  ```
- Line 31: `READER_COMPACT`
  ```python
  rows = mmr_rerank(rows, alpha=float(os.getenv("MMR_ALPHA", "0.85")), per_file_penalty=0.10, k=lim["shortlist"])
    rows = per_file_cap(rows, cap=int(os.getenv("PER_FILE_CAP", "5")))[: lim["topk"]]
    ctx, meta = build_reader_context(rows, q, tag, compact=bool(int(os.getenv("READER_COMPACT", "1"))))
    return ctx, rows
  ```
- Line 62: `Q`
  ```python
  if __name__ == "__main__":
    q = os.getenv("Q") or "What is DSPy according to 400_07_ai-frameworks-dspy.md?"
    tag = os.getenv("TAG", "rag_qa_single")
    ctx, rows = get_context(q, tag)
  ```
- Line 63: `TAG`
  ```python
  if __name__ == "__main__":
    q = os.getenv("Q") or "What is DSPy according to 400_07_ai-frameworks-dspy.md?"
    tag = os.getenv("TAG", "rag_qa_single")
    ctx, rows = get_context(q, tag)
    a = run_uncompiled(q, tag, ctx)
  ```

### scripts/reader_grid_sweep.py
- Line 72: `READER_COMPACT`
  ```python
  base = {
        "READER_CMD": cmd,
        "READER_COMPACT": os.getenv("READER_COMPACT", "1"),
    }
    # Small, targeted sweep: toggle abstention + span enforcement + precheck threshold
  ```
- Line 94: `CASES_FILE`
  ```python
  def main() -> None:
    ap = argparse.ArgumentParser(description="DSPy reader grid sweep for micro-F1")
    ap.add_argument("--cases", default=os.getenv("CASES_FILE", "evals/gold_cases.json"))
    ap.add_argument("--reader-gold", default=os.getenv("READER_GOLD_FILE", "evals/reader_gold.jsonl"))
    ap.add_argument("--cmd", default=os.getenv("READER_CMD", "python3 scripts/run_dspy_reader.py"))
  ```
- Line 95: `READER_GOLD_FILE`
  ```python
  ap = argparse.ArgumentParser(description="DSPy reader grid sweep for micro-F1")
    ap.add_argument("--cases", default=os.getenv("CASES_FILE", "evals/gold_cases.json"))
    ap.add_argument("--reader-gold", default=os.getenv("READER_GOLD_FILE", "evals/reader_gold.jsonl"))
    ap.add_argument("--cmd", default=os.getenv("READER_CMD", "python3 scripts/run_dspy_reader.py"))
    ap.add_argument("--out", help="Write JSON summary to this path")
  ```
- Line 96: `READER_CMD`
  ```python
  ap.add_argument("--cases", default=os.getenv("CASES_FILE", "evals/gold_cases.json"))
    ap.add_argument("--reader-gold", default=os.getenv("READER_GOLD_FILE", "evals/reader_gold.jsonl"))
    ap.add_argument("--cmd", default=os.getenv("READER_CMD", "python3 scripts/run_dspy_reader.py"))
    ap.add_argument("--out", help="Write JSON summary to this path")
    args = ap.parse_args()
  ```

### scripts/rehydration_integration.py
- Line 45: `AUTO_REHYDRATE`
  ```python
  def is_enabled() -> bool:
    return os.getenv("AUTO_REHYDRATE", "0") == "1"
  ```
- Line 50: `REHYDRATE_MINUTES`
  ```python
  def get_debounce_minutes() -> int:
    try:
        return int(os.getenv("REHYDRATE_MINUTES", "10"))
    except ValueError:
        return 10
  ```

### scripts/retrieval_schema_check.py
- Line 53: `IVFFLAT_LISTS`
  ```python
  # ivfflat on embedding (cosine); adjust lists via env if needed
            lists = int(os.getenv("IVFFLAT_LISTS", "100"))
            cur.execute(
                f"""
  ```

### scripts/run_add_content_tsv.py
- Line 15: `POSTGRES_DSN`
  ```python
  def main():
    dsn = os.getenv("POSTGRES_DSN") or os.getenv("DATABASE_URL")
    if not dsn:
        print("❌ Set POSTGRES_DSN or DATABASE_URL")
  ```
- Line 15: `DATABASE_URL`
  ```python
  def main():
    dsn = os.getenv("POSTGRES_DSN") or os.getenv("DATABASE_URL")
    if not dsn:
        print("❌ Set POSTGRES_DSN or DATABASE_URL")
  ```

### scripts/run_bedrock_eval_direct.py
- Line 25: `AWS_REGION`
  ```python
  def main():
    # Set AWS region for LiteLLM Bedrock integration
    os.environ["AWS_REGION"] = "us-east-1"

    # Set LiteLLM timeouts and retries to prevent hanging
  ```
- Line 28: `LITELLM_TIMEOUT`
  ```python
  # Set LiteLLM timeouts and retries to prevent hanging
    os.environ["LITELLM_TIMEOUT"] = "60"
    os.environ["LITELLM_MAX_RETRIES"] = "1"
    os.environ["RAGCHECKER_NUM_WORKERS"] = "1"
  ```
- Line 29: `LITELLM_MAX_RETRIES`
  ```python
  # Set LiteLLM timeouts and retries to prevent hanging
    os.environ["LITELLM_TIMEOUT"] = "60"
    os.environ["LITELLM_MAX_RETRIES"] = "1"
    os.environ["RAGCHECKER_NUM_WORKERS"] = "1"
  ```
- Line 30: `RAGCHECKER_NUM_WORKERS`
  ```python
  os.environ["LITELLM_TIMEOUT"] = "60"
    os.environ["LITELLM_MAX_RETRIES"] = "1"
    os.environ["RAGCHECKER_NUM_WORKERS"] = "1"

    print("⏱️  LiteLLM timeouts: 60s, max retries: 1, workers: 1")
  ```
- Line 56: `RAGCHECKER_FAST_MODE`
  ```python
  # Build the command with fast mode defaults
    # Honor RAGCHECKER_FAST_MODE if set; fallback to FAST_MODE; default = 1
    fast_env = os.getenv("RAGCHECKER_FAST_MODE")
    if fast_env is None:
        fast_env = os.getenv("FAST_MODE")
  ```
- Line 58: `FAST_MODE`
  ```python
  fast_env = os.getenv("RAGCHECKER_FAST_MODE")
    if fast_env is None:
        fast_env = os.getenv("FAST_MODE")
    fast_mode = (fast_env or "1") == "1"
  ```

### scripts/run_eval.py
- Line 47: `EVAL_MODE`
  ```python
  # Enforce eval hygiene via env signals
    os.environ["EVAL_MODE"] = "bedrock_only"
    os.environ["CACHE_DISABLED"] = "1"
  ```
- Line 48: `CACHE_DISABLED`
  ```python
  # Enforce eval hygiene via env signals
    os.environ["EVAL_MODE"] = "bedrock_only"
    os.environ["CACHE_DISABLED"] = "1"

    # Run official evaluation with Bedrock only
  ```
- Line 69: `EVAL_MODE`
  ```python
  "eval_file": Path(latest).name,
            "env": {
                "EVAL_MODE": os.environ.get("EVAL_MODE"),
                "CACHE_DISABLED": os.environ.get("CACHE_DISABLED"),
                "AWS_REGION": os.environ.get("AWS_REGION"),
  ```
- Line 70: `CACHE_DISABLED`
  ```python
  "env": {
                "EVAL_MODE": os.environ.get("EVAL_MODE"),
                "CACHE_DISABLED": os.environ.get("CACHE_DISABLED"),
                "AWS_REGION": os.environ.get("AWS_REGION"),
            },
  ```
- Line 71: `AWS_REGION`
  ```python
  "EVAL_MODE": os.environ.get("EVAL_MODE"),
                "CACHE_DISABLED": os.environ.get("CACHE_DISABLED"),
                "AWS_REGION": os.environ.get("AWS_REGION"),
            },
        }
  ```

### scripts/run_memory_verification.py
- Line 163: `MEMORY_VERIFY_USER`
  ```python
  storage = ConversationStorage()
    user_id = os.getenv("MEMORY_VERIFY_USER", "verify_user")
    session_id = os.getenv("MEMORY_VERIFY_SESSION", generate_session_id(user_id))
  ```
- Line 164: `MEMORY_VERIFY_SESSION`
  ```python
  storage = ConversationStorage()
    user_id = os.getenv("MEMORY_VERIFY_USER", "verify_user")
    session_id = os.getenv("MEMORY_VERIFY_SESSION", generate_session_id(user_id))

    if not seed_demo(storage, session_id, user_id):
  ```

### scripts/setup_ai_models.py
- Line 83: `POSTGRES_DSN`
  ```python
  def main() -> int:
    parser = argparse.ArgumentParser(description="Setup validator for Cursor-native AI models")
    parser.add_argument("--dsn", default=os.getenv("POSTGRES_DSN", ""), help="PostgreSQL DSN for optional checks")
    parser.add_argument("--check-db", action="store_true", help="Attempt DB connection and pgvector check")
    args = parser.parse_args()
  ```

### scripts/setup_db_minimal.py
- Line 47: `IVFFLAT_LISTS`
  ```python
  """
            )
            lists = int(os.getenv("IVFFLAT_LISTS", "100"))
            cur.execute(
                f"""
  ```
- Line 75: `DATABASE_URL`
  ```python
  def main() -> None:
    dsn = os.getenv("DATABASE_URL", "")
    # High-impact retrieval indexes
    ensure_retrieval_schema()
  ```

### scripts/single_doorway.py
- Line 32: `PYTHON`
  ```python
  def _select_python() -> str:
    # Prefer explicit env, then python3.12 if present, else current interpreter
    if os.environ.get("PYTHON"):
        return os.environ["PYTHON"]
    # Prefer the current interpreter (respects venv) over a global python3.12
  ```
- Line 33: `PYTHON`
  ```python
  # Prefer explicit env, then python3.12 if present, else current interpreter
    if os.environ.get("PYTHON"):
        return os.environ["PYTHON"]
    # Prefer the current interpreter (respects venv) over a global python3.12
    if sys.executable:
  ```

### scripts/sync_reader_case_ids.py
- Line 26: `CASES_FILE`
  ```python
  from collections import defaultdict

CASES_FILE = os.getenv("CASES_FILE", "evals/gold_cases.json")
READER_SRC = os.getenv("READER_SRC", "evals/reader_gold.jsonl")
READER_OUT = os.getenv("READER_OUT", "evals/reader_gold_comprehensive.jsonl")
  ```
- Line 27: `READER_SRC`
  ```python
  CASES_FILE = os.getenv("CASES_FILE", "evals/gold_cases.json")
READER_SRC = os.getenv("READER_SRC", "evals/reader_gold.jsonl")
READER_OUT = os.getenv("READER_OUT", "evals/reader_gold_comprehensive.jsonl")
READER_LEFTOVER = os.getenv("READER_LEFTOVER", "evals/reader_gold_unmatched.jsonl")
  ```
- Line 28: `READER_OUT`
  ```python
  CASES_FILE = os.getenv("CASES_FILE", "evals/gold_cases.json")
READER_SRC = os.getenv("READER_SRC", "evals/reader_gold.jsonl")
READER_OUT = os.getenv("READER_OUT", "evals/reader_gold_comprehensive.jsonl")
READER_LEFTOVER = os.getenv("READER_LEFTOVER", "evals/reader_gold_unmatched.jsonl")
  ```
- Line 29: `READER_LEFTOVER`
  ```python
  READER_SRC = os.getenv("READER_SRC", "evals/reader_gold.jsonl")
READER_OUT = os.getenv("READER_OUT", "evals/reader_gold_comprehensive.jsonl")
READER_LEFTOVER = os.getenv("READER_LEFTOVER", "evals/reader_gold_unmatched.jsonl")
  ```

### scripts/test_cross_encoder_integration.py
- Line 112: `RAGCHECKER_CROSS_ENCODER_ENABLED`
  ```python
  # Enable cross-encoder
    os.environ["RAGCHECKER_CROSS_ENCODER_ENABLED"] = "1"

    try:
  ```
- Line 155: `RAGCHECKER_CROSS_ENCODER_ENABLED`
  ```python
  # Enable cross-encoder
    os.environ["RAGCHECKER_CROSS_ENCODER_ENABLED"] = "1"

    try:
  ```

### scripts/test_enhanced_bedrock.py
- Line 60: `AWS_ACCESS_KEY_ID`
  ```python
  {
            "key_id": "key_0",
            "access_key": os.getenv("AWS_ACCESS_KEY_ID", ""),
            "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
            "region": os.getenv("AWS_REGION", "us-east-1"),
  ```
- Line 61: `AWS_SECRET_ACCESS_KEY`
  ```python
  "key_id": "key_0",
            "access_key": os.getenv("AWS_ACCESS_KEY_ID", ""),
            "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
            "region": os.getenv("AWS_REGION", "us-east-1"),
        }
  ```
- Line 62: `AWS_REGION`
  ```python
  "access_key": os.getenv("AWS_ACCESS_KEY_ID", ""),
            "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
            "region": os.getenv("AWS_REGION", "us-east-1"),
        }
    ]
  ```
- Line 255: `AWS_ACCESS_KEY_ID`
  ```python
  # Check prerequisites
    if not os.getenv("AWS_ACCESS_KEY_ID"):
        print("❌ AWS_ACCESS_KEY_ID not set. Please configure your AWS credentials.")
        print("   You can use the config/enhanced_bedrock_config.env file as a template.")
  ```

### scripts/test_reranker_integration.py
- Line 12: `DSPY_RAG_PATH`
  ```python
  # Add DSPy RAG system to path
dspy_rag_path = os.getenv("DSPY_RAG_PATH", "src")
if dspy_rag_path and dspy_rag_path not in sys.path:
    sys.path.insert(0, dspy_rag_path)
  ```

### scripts/tiny_grid.py
- Line 79: `RETRIEVER_WEIGHTS_FILE`
  ```python
  return False

    cfg_path = os.getenv("RETRIEVER_WEIGHTS_FILE", "configs/retriever_weights.yaml")
    bak = f"{cfg_path}.{time.strftime('%Y%m%d_%H%M%S')}.bak"
  ```

### scripts/tiny_hardening_system.py
- Line 238: `CONFIG_HASH`
  ```python
  "chunk_id_function": "generate_idempotent_chunk_id",
                "chunk_version": "2025-09-07-v1",
                "config_hash": os.getenv("CONFIG_HASH", "default"),
            }
  ```

### scripts/unified_memory_orchestrator.py
- Line 114: `PATH`
  ```python
  if venv_bin.exists():
            # Add venv to PATH
            os.environ["PATH"] = f"{venv_bin}:{os.environ.get('PATH', '')}"
            os.environ["VIRTUAL_ENV"] = str(venv_path)
  ```
- Line 114: `PATH`
  ```python
  if venv_bin.exists():
            # Add venv to PATH
            os.environ["PATH"] = f"{venv_bin}:{os.environ.get('PATH', '')}"
            os.environ["VIRTUAL_ENV"] = str(venv_path)
  ```
- Line 115: `VIRTUAL_ENV`
  ```python
  # Add venv to PATH
            os.environ["PATH"] = f"{venv_bin}:{os.environ.get('PATH', '')}"
            os.environ["VIRTUAL_ENV"] = str(venv_path)

            # Update sys.path to include venv packages
  ```

### scripts/upgrade_validation.py
- Line 77: `DATABASE_URL`
  ```python
  try:
            # Test database connectivity
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cursor = conn.cursor()
  ```
- Line 172: `MISTRAL_7B_URL`
  ```python
  try:
            # Test Mistral 7B model
            mistral_url = os.getenv("MISTRAL_7B_URL")
            if mistral_url:
                mistral_response = requests.get(f"{mistral_url}/health", timeout=5)
  ```
- Line 180: `YI_CODER_URL`
  ```python
  # Test Yi-Coder model
            yi_coder_url = os.getenv("YI_CODER_URL")
            if yi_coder_url:
                yi_coder_response = requests.get(f"{yi_coder_url}/health", timeout=5)
  ```
- Line 433: `DATABASE_URL`
  ```python
  try:
            # Test new database columns if they were added
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cursor = conn.cursor()
  ```
- Line 551: `MONITORING_URL`
  ```python
  """
        try:
            monitoring_url = os.getenv("MONITORING_URL")
            if monitoring_url:
                response = requests.post(f"{monitoring_url}/validation-alert", json=report, timeout=10)
  ```

### scripts/uv_team_onboarding.py
- Line 43: `SHELL`
  ```python
  import os

        return os.environ.get("SHELL", "bash")

    def _log_step(self, step: str, success: bool, details: str = ""):
  ```

### scripts/validate_config.py
- Line 208: `DB_DRIVER`
  ```python
  def _dsn_from_env() -> str:
    # Respect your existing env usage
    driver = os.getenv("DB_DRIVER", "postgresql+psycopg2")
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
  ```
- Line 209: `PGHOST`
  ```python
  # Respect your existing env usage
    driver = os.getenv("DB_DRIVER", "postgresql+psycopg2")
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    user = os.getenv("PGUSER", "danieljacobs")
  ```
- Line 210: `PGPORT`
  ```python
  driver = os.getenv("DB_DRIVER", "postgresql+psycopg2")
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    user = os.getenv("PGUSER", "danieljacobs")
    pwd = os.getenv("PGPASSWORD", "postgres")
  ```
- Line 211: `PGUSER`
  ```python
  host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    user = os.getenv("PGUSER", "danieljacobs")
    pwd = os.getenv("PGPASSWORD", "postgres")
    db = os.getenv("PGDATABASE", "ai_agency")
  ```
- Line 212: `PGPASSWORD`
  ```python
  port = os.getenv("PGPORT", "5432")
    user = os.getenv("PGUSER", "danieljacobs")
    pwd = os.getenv("PGPASSWORD", "postgres")
    db = os.getenv("PGDATABASE", "ai_agency")
    return f"{driver}://{user}:{pwd}@{host}:{port}/{db}"
  ```
- Line 213: `PGDATABASE`
  ```python
  user = os.getenv("PGUSER", "danieljacobs")
    pwd = os.getenv("PGPASSWORD", "postgres")
    db = os.getenv("PGDATABASE", "ai_agency")
    return f"{driver}://{user}:{pwd}@{host}:{port}/{db}"
  ```

### scripts/validate_eval_targets.py
- Line 12: `POSTGRES_DSN`
  ```python
  def main():
    gold = json.load(open("evals/gold_cases.json"))
    dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
    with psycopg2.connect(dsn, cursor_factory=RealDictCursor) as conn, conn.cursor() as cur:
        missing = []
  ```

### scripts/venv_manager.py
- Line 31: `VIRTUAL_ENV`
  ```python
  """Check if the project virtual environment is currently active."""
        # Check if VIRTUAL_ENV points to our project venv
        virtual_env = os.environ.get("VIRTUAL_ENV")
        if virtual_env:
            return Path(virtual_env).resolve() == self.venv_path.resolve()
  ```
- Line 55: `VENV_DISABLE_IMPORT_CHECK`
  ```python
  - VENV_REQUIRED_PACKAGES overrides as comma-separated list
        """
        if os.environ.get("VENV_DISABLE_IMPORT_CHECK", "0") == "1":
            return True, []
        # Allow override via env
  ```
- Line 58: `VENV_REQUIRED_PACKAGES`
  ```python
  return True, []
        # Allow override via env
        override = os.environ.get("VENV_REQUIRED_PACKAGES")
        if override:
            required_packages = [p.strip() for p in override.split(",") if p.strip()]
  ```
- Line 62: `VENV_VALIDATE_MINIMAL`
  ```python
  required_packages = [p.strip() for p in override.split(",") if p.strip()]
        else:
            minimal = os.environ.get("VENV_VALIDATE_MINIMAL", "0") == "1"
            required_packages = ["psycopg2", "dspy"] if minimal else ["psycopg2", "dspy", "pytest", "ruff"]
  ```
- Line 85: `VIRTUAL_ENV`
  ```python
  # Update environment variables to use venv
        os.environ["VIRTUAL_ENV"] = str(self.venv_path)
        os.environ["PATH"] = f"{self.venv_path}/bin:{os.environ.get('PATH', '')}"
  ```
- Line 86: `PATH`
  ```python
  # Update environment variables to use venv
        os.environ["VIRTUAL_ENV"] = str(self.venv_path)
        os.environ["PATH"] = f"{self.venv_path}/bin:{os.environ.get('PATH', '')}"

        # Update sys.path to include venv site-packages
  ```
- Line 86: `PATH`
  ```python
  # Update environment variables to use venv
        os.environ["VIRTUAL_ENV"] = str(self.venv_path)
        os.environ["PATH"] = f"{self.venv_path}/bin:{os.environ.get('PATH', '')}"

        # Update sys.path to include venv site-packages
  ```
- Line 144: `VIRTUAL_ENV`
  ```python
  "python_path": str(self.get_venv_python_path()),
            "sys_prefix": sys.prefix,
            "virtual_env": os.environ.get("VIRTUAL_ENV"),
            "dependencies_ok": self.validate_dependencies()[0],
        }
  ```

### scripts/verify_real_rag_parity.py
- Line 113: `RAGCHECKER_PROGRESS_LOG`
  ```python
  # Check 6: progress file exists and has sufficient lines
    progress_log = os.getenv("RAGCHECKER_PROGRESS_LOG", "metrics/baseline_evaluations/progress.jsonl")
    if os.path.exists(progress_log):
        with open(progress_log, "r") as f:
  ```
- Line 130: `RERANK_ENABLE`
  ```python
  # Check 7: rerank usage (if enabled)
    rerank_enabled = os.getenv("RERANK_ENABLE", "1") == "1"
    if rerank_enabled:
        # Check if any case has cross-encoder scores
  ```

### scripts/verify_schema_and_indexes.py
- Line 21: `POSTGRES_DSN`
  ```python
  def connect():
    dsn = os.getenv("POSTGRES_DSN") or os.getenv("DATABASE_URL")
    if not dsn:
        print("❌ No POSTGRES_DSN/DATABASE_URL set")
  ```
- Line 21: `DATABASE_URL`
  ```python
  def connect():
    dsn = os.getenv("POSTGRES_DSN") or os.getenv("DATABASE_URL")
    if not dsn:
        print("❌ No POSTGRES_DSN/DATABASE_URL set")
  ```

### scripts/verify_venv_mapping.py
- Line 28: `VIRTUAL_ENV`
  ```python
  # Check VIRTUAL_ENV
    venv_path = os.environ.get("VIRTUAL_ENV")
    if not venv_path:
        print("❌ VIRTUAL_ENV not set")
  ```

### src/common/role_guc_manager.py
- Line 56: `DATABASE_URL`
  ```python
  dsn = resolve_dsn(strict=False, emit_warning=False)
            except ImportError:
                dsn = os.getenv("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency")

        self.dsn = dsn
  ```

### src/config/settings.py
- Line 67: `SECRETS_DIR`
  ```python
  env_nested_delimiter="__",
        extra="ignore",
        secrets_dir=os.getenv("SECRETS_DIR", None),
        case_sensitive=False,
        validate_assignment=True,
  ```
- Line 83: `APP_ENV`
  ```python
  """Customize settings sources with clear precedence order."""
        # Determine environment-specific YAML file
        env = os.getenv("APP_ENV", "dev")
        base_path = Path("configs/base.yaml")
        env_path = Path(f"configs/{env}.yaml")
  ```

### src/dspy_modules/documentation_retrieval.py
- Line 363: `DATABASE_URL`
  ```python
  if db_connection_string is None:
        db_connection_string = os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")

    service = create_documentation_retrieval_service(db_connection_string)
  ```
- Line 375: `DATABASE_URL`
  ```python
  if db_connection_string is None:
        db_connection_string = os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")

    service = create_documentation_retrieval_service(db_connection_string)
  ```
- Line 387: `DATABASE_URL`
  ```python
  if db_connection_string is None:
        db_connection_string = os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")

    service = create_documentation_retrieval_service(db_connection_string)
  ```

### src/dspy_modules/dspy_reader_program.py
- Line 25: `DSPY_MODEL`
  ```python
  # return dspy.LM(model="ollama/llama2", max_tokens=512, temperature=0.2)
    # Keep tokens low & temp ~0.2 for stability; limit concurrency outside (CI runner)
    model_name = os.getenv("DSPY_MODEL", "anthropic.claude-3-haiku-20240307-v1:0")
    if "/" not in model_name:
        model_name = f"bedrock/{model_name}"
  ```
- Line 60: `READER_ABSTAIN`
  ```python
  # READER_PRECHECK: 1=enable token-overlap precheck (default), 0=disable
        # READER_PRECHECK_MIN_OVERLAP: float in [0,1], default 0.10
        self.abstain_enabled = bool(int(os.getenv("READER_ABSTAIN", "1")))
        self.enforce_span = bool(int(os.getenv("READER_ENFORCE_SPAN", "1")))
        self.precheck_enabled = bool(int(os.getenv("READER_PRECHECK", "1")))
  ```
- Line 61: `READER_ENFORCE_SPAN`
  ```python
  # READER_PRECHECK_MIN_OVERLAP: float in [0,1], default 0.10
        self.abstain_enabled = bool(int(os.getenv("READER_ABSTAIN", "1")))
        self.enforce_span = bool(int(os.getenv("READER_ENFORCE_SPAN", "1")))
        self.precheck_enabled = bool(int(os.getenv("READER_PRECHECK", "1")))
        try:
  ```
- Line 62: `READER_PRECHECK`
  ```python
  self.abstain_enabled = bool(int(os.getenv("READER_ABSTAIN", "1")))
        self.enforce_span = bool(int(os.getenv("READER_ENFORCE_SPAN", "1")))
        self.precheck_enabled = bool(int(os.getenv("READER_PRECHECK", "1")))
        try:
            self.precheck_min_overlap = float(os.getenv("READER_PRECHECK_MIN_OVERLAP", "0.10"))
  ```
- Line 64: `READER_PRECHECK_MIN_OVERLAP`
  ```python
  self.precheck_enabled = bool(int(os.getenv("READER_PRECHECK", "1")))
        try:
            self.precheck_min_overlap = float(os.getenv("READER_PRECHECK_MIN_OVERLAP", "0.10"))
        except ValueError:
            self.precheck_min_overlap = 0.10
  ```
- Line 77: `HINT_PREFETCH_LIMIT`
  ```python
  if hint:
            try:
                rows_prefetch = fetch_doc_chunks_by_slug(hint, limit=int(os.getenv("HINT_PREFETCH_LIMIT", "8")))
            except Exception:
                rows_prefetch = []
  ```
- Line 102: `MMR_ALPHA`
  ```python
  rows = merged
        rows = mmr_rerank(
            rows, alpha=float(os.getenv("MMR_ALPHA", "0.85")), per_file_penalty=0.10, k=limits["shortlist"], tag=tag
        )
        rows = per_file_cap(rows, cap=int(os.getenv("PER_FILE_CAP", "5")))[: limits["topk"]]
  ```
- Line 104: `PER_FILE_CAP`
  ```python
  rows, alpha=float(os.getenv("MMR_ALPHA", "0.85")), per_file_penalty=0.10, k=limits["shortlist"], tag=tag
        )
        rows = per_file_cap(rows, cap=int(os.getenv("PER_FILE_CAP", "5")))[: limits["topk"]]
        context, _meta = build_reader_context(rows, question, tag, compact=bool(int(os.getenv("READER_COMPACT", "1"))))
  ```
- Line 105: `READER_COMPACT`
  ```python
  )
        rows = per_file_cap(rows, cap=int(os.getenv("PER_FILE_CAP", "5")))[: limits["topk"]]
        context, _meta = build_reader_context(rows, question, tag, compact=bool(int(os.getenv("READER_COMPACT", "1"))))

        # Rule-first: Try deterministic span extraction
  ```

### src/dspy_modules/enhanced_rag_system.py
- Line 683: `POSTGRES_DSN`
  ```python
  if db_url is None:
        db_url = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")

    return EnhancedRAGQueryInterface(db_url, mistral_url)
  ```

### src/dspy_modules/reader/entrypoint.py
- Line 31: `TOKEN_PACK_ENABLE`
  ```python
  # Optional: token-budget packing powered by local counter
    enable_token_pack = bool(int(os.getenv("TOKEN_PACK_ENABLE", "0")))
    token_budget = int(os.getenv("TOKEN_PACK_BUDGET", "8192"))
    token_reserve = int(os.getenv("TOKEN_PACK_RESERVE", "1024"))
  ```
- Line 32: `TOKEN_PACK_BUDGET`
  ```python
  # Optional: token-budget packing powered by local counter
    enable_token_pack = bool(int(os.getenv("TOKEN_PACK_ENABLE", "0")))
    token_budget = int(os.getenv("TOKEN_PACK_BUDGET", "8192"))
    token_reserve = int(os.getenv("TOKEN_PACK_RESERVE", "1024"))
    token_family = os.getenv("TOKEN_PACK_FAMILY", "hf_fast")
  ```
- Line 33: `TOKEN_PACK_RESERVE`
  ```python
  enable_token_pack = bool(int(os.getenv("TOKEN_PACK_ENABLE", "0")))
    token_budget = int(os.getenv("TOKEN_PACK_BUDGET", "8192"))
    token_reserve = int(os.getenv("TOKEN_PACK_RESERVE", "1024"))
    token_family = os.getenv("TOKEN_PACK_FAMILY", "hf_fast")
    token_model = os.getenv("TOKEN_PACK_MODEL", "bert-base-uncased")
  ```
- Line 34: `TOKEN_PACK_FAMILY`
  ```python
  token_budget = int(os.getenv("TOKEN_PACK_BUDGET", "8192"))
    token_reserve = int(os.getenv("TOKEN_PACK_RESERVE", "1024"))
    token_family = os.getenv("TOKEN_PACK_FAMILY", "hf_fast")
    token_model = os.getenv("TOKEN_PACK_MODEL", "bert-base-uncased")
    llama_model_path = os.getenv("TOKEN_PACK_LLAMA_PATH")
  ```
- Line 35: `TOKEN_PACK_MODEL`
  ```python
  token_reserve = int(os.getenv("TOKEN_PACK_RESERVE", "1024"))
    token_family = os.getenv("TOKEN_PACK_FAMILY", "hf_fast")
    token_model = os.getenv("TOKEN_PACK_MODEL", "bert-base-uncased")
    llama_model_path = os.getenv("TOKEN_PACK_LLAMA_PATH")
  ```
- Line 36: `TOKEN_PACK_LLAMA_PATH`
  ```python
  token_family = os.getenv("TOKEN_PACK_FAMILY", "hf_fast")
    token_model = os.getenv("TOKEN_PACK_MODEL", "bert-base-uncased")
    llama_model_path = os.getenv("TOKEN_PACK_LLAMA_PATH")

    counter = None
  ```

### src/dspy_modules/retriever/limits.py
- Line 12: `RETRIEVER_LIMITS_FILE`
  ```python
  @lru_cache(maxsize=32)
def load_limits(tag: str = "", file_path: str | None = None) -> dict[str, int]:
    path = file_path or os.getenv("RETRIEVER_LIMITS_FILE", "configs/retriever_limits.yaml")
    limits: dict[str, int] = dict(DEFAULT_LIMITS)
    try:
  ```

### src/dspy_modules/retriever/pg.py
- Line 19: `POSTGRES_DSN`
  ```python
  def get_db_connection():
    """Get database connection from environment or default."""
    dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
    # Handle mock DSN for testing
    if dsn.startswith("mock://"):
  ```
- Line 58: `PGVECTOR_OPS`
  ```python
  def _vec_expr() -> str:
    ops = (os.getenv("PGVECTOR_OPS", "cosine") or "cosine").lower()
    if ops == "l2":
        return "1.0 / (1.0 + (b.embedding <=> %(qvec)s::vector))"
  ```
- Line 205: `COLD_START_WVEC_BOOST`
  ```python
  # Cold-start boost: increase w_vec when query is lexically sparse
    if cold_start:
        boost = float(os.getenv("COLD_START_WVEC_BOOST", "0.10"))
        weights["w_vec"] = weights["w_vec"] * (1.0 + boost)
  ```
- Line 217: `EMBED_DIM`
  ```python
  if not has_vec:
        try:
            dim = int(os.getenv("EMBED_DIM", "384"))
        except Exception:
            dim = 384
  ```
- Line 346: `FUSION_HEAD_ENABLE`
  ```python
  # Apply learned fusion head if enabled
    enabled = os.getenv("FUSION_HEAD_ENABLE", "0") == "1"
    ckpt = os.getenv("FUSION_HEAD_PATH", "")
    spec_path = os.getenv("FUSION_FEATURE_SPEC", "configs/feature_spec_v1.json")
  ```
- Line 347: `FUSION_HEAD_PATH`
  ```python
  # Apply learned fusion head if enabled
    enabled = os.getenv("FUSION_HEAD_ENABLE", "0") == "1"
    ckpt = os.getenv("FUSION_HEAD_PATH", "")
    spec_path = os.getenv("FUSION_FEATURE_SPEC", "configs/feature_spec_v1.json")
    hidden = int(os.getenv("FUSION_HIDDEN", "0"))
  ```
- Line 348: `FUSION_FEATURE_SPEC`
  ```python
  enabled = os.getenv("FUSION_HEAD_ENABLE", "0") == "1"
    ckpt = os.getenv("FUSION_HEAD_PATH", "")
    spec_path = os.getenv("FUSION_FEATURE_SPEC", "configs/feature_spec_v1.json")
    hidden = int(os.getenv("FUSION_HIDDEN", "0"))
    device = os.getenv("FUSION_DEVICE", "cpu")
  ```
- Line 349: `FUSION_HIDDEN`
  ```python
  ckpt = os.getenv("FUSION_HEAD_PATH", "")
    spec_path = os.getenv("FUSION_FEATURE_SPEC", "configs/feature_spec_v1.json")
    hidden = int(os.getenv("FUSION_HIDDEN", "0"))
    device = os.getenv("FUSION_DEVICE", "cpu")
  ```
- Line 350: `FUSION_DEVICE`
  ```python
  spec_path = os.getenv("FUSION_FEATURE_SPEC", "configs/feature_spec_v1.json")
    hidden = int(os.getenv("FUSION_HIDDEN", "0"))
    device = os.getenv("FUSION_DEVICE", "cpu")

    if enabled and ckpt and os.path.exists(ckpt):
  ```

### src/dspy_modules/retriever/reranker_config.py
- Line 42: `RETRIEVER_WEIGHTS_FILE`
  ```python
  Dictionary with reranker configuration
    """
    path = file_path or os.getenv("RETRIEVER_WEIGHTS_FILE", "configs/retriever_weights.yaml")
    config = dict(DEFAULT_RERANKER_CONFIG)
  ```
- Line 77: `RERANKER_CACHE_DIR`
  ```python
  "device": RENV.TORCH_DEVICE,
            "cache_enabled": "1",
            "cache_dir": os.getenv("RERANKER_CACHE_DIR", "cache"),
        }
    else:
  ```
- Line 81: `RERANKER_ENABLED`
  ```python
  else:
        env_overrides = {
            "enabled": os.getenv("RERANKER_ENABLED"),
            "model": os.getenv("RERANKER_MODEL"),
            "input_topk": os.getenv("RERANK_INPUT_TOPK"),
  ```
- Line 82: `RERANKER_MODEL`
  ```python
  env_overrides = {
            "enabled": os.getenv("RERANKER_ENABLED"),
            "model": os.getenv("RERANKER_MODEL"),
            "input_topk": os.getenv("RERANK_INPUT_TOPK"),
            "keep": os.getenv("RERANK_KEEP"),
  ```
- Line 83: `RERANK_INPUT_TOPK`
  ```python
  "enabled": os.getenv("RERANKER_ENABLED"),
            "model": os.getenv("RERANKER_MODEL"),
            "input_topk": os.getenv("RERANK_INPUT_TOPK"),
            "keep": os.getenv("RERANK_KEEP"),
            "batch_size": os.getenv("RERANK_BATCH"),
  ```
- Line 84: `RERANK_KEEP`
  ```python
  "model": os.getenv("RERANKER_MODEL"),
            "input_topk": os.getenv("RERANK_INPUT_TOPK"),
            "keep": os.getenv("RERANK_KEEP"),
            "batch_size": os.getenv("RERANK_BATCH"),
            "device": os.getenv("TORCH_DEVICE"),
  ```
- Line 85: `RERANK_BATCH`
  ```python
  "input_topk": os.getenv("RERANK_INPUT_TOPK"),
            "keep": os.getenv("RERANK_KEEP"),
            "batch_size": os.getenv("RERANK_BATCH"),
            "device": os.getenv("TORCH_DEVICE"),
            "cache_enabled": os.getenv("RERANKER_CACHE_ENABLED"),
  ```
- Line 86: `TORCH_DEVICE`
  ```python
  "keep": os.getenv("RERANK_KEEP"),
            "batch_size": os.getenv("RERANK_BATCH"),
            "device": os.getenv("TORCH_DEVICE"),
            "cache_enabled": os.getenv("RERANKER_CACHE_ENABLED"),
            "cache_dir": os.getenv("RERANKER_CACHE_DIR"),
  ```
- Line 87: `RERANKER_CACHE_ENABLED`
  ```python
  "batch_size": os.getenv("RERANK_BATCH"),
            "device": os.getenv("TORCH_DEVICE"),
            "cache_enabled": os.getenv("RERANKER_CACHE_ENABLED"),
            "cache_dir": os.getenv("RERANKER_CACHE_DIR"),
        }
  ```
- Line 88: `RERANKER_CACHE_DIR`
  ```python
  "device": os.getenv("TORCH_DEVICE"),
            "cache_enabled": os.getenv("RERANKER_CACHE_ENABLED"),
            "cache_dir": os.getenv("RERANKER_CACHE_DIR"),
        }
  ```

### src/dspy_modules/retriever/reranker_torch.py
- Line 55: `TORCH_DEVICE`
  ```python
  def _device():
    """Determine the best available device for inference"""
    device = RENV.TORCH_DEVICE if RENV else os.getenv("TORCH_DEVICE", "cpu")

    if device == "mps":  # Apple Silicon
  ```
- Line 82: `RERANKER_MODEL`
  ```python
  global _MODEL, _MODEL_NAME

    model_name = RENV.RERANKER_MODEL if RENV else os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

    # Return cached model if name hasn't changed
  ```
- Line 113: `RERANKER_CACHE_DIR`
  ```python
  RENV.RERANK_CACHE_PATH
        if (RENV and RENV.RERANK_CACHE_BACKEND == "sqlite")
        else os.getenv("RERANKER_CACHE_DIR", "cache")
    )
    # Backwards-compat for existing layout: RERANKER_CACHE_DIR expects a directory
  ```
- Line 212: `RERANKER_MODEL`
  ```python
  return [(cid, txt, 0.0) for cid, txt in candidates[:topk_keep]]

    model_name = RENV.RERANKER_MODEL if RENV else os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    query_hash = _query_hash(query)
    chunk_ids = [cid for cid, _ in candidates]
  ```
- Line 278: `RERANKER_MODEL`
  ```python
  "available": True,
        "model_name": (
            RENV.RERANKER_MODEL if RENV else os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
        ),
        "device": _device(),
  ```
- Line 281: `RERANK_BATCH`
  ```python
  ),
        "device": _device(),
        "batch_size": (RENV.RERANK_BATCH if RENV else int(os.getenv("RERANK_BATCH", "8"))),
        "input_topk": (RENV.RERANK_INPUT_TOPK if RENV else int(os.getenv("RERANK_INPUT_TOPK", "50"))),
        "output_topk": (RENV.RERANK_KEEP if RENV else int(os.getenv("RERANK_KEEP", "12"))),
  ```
- Line 282: `RERANK_INPUT_TOPK`
  ```python
  "device": _device(),
        "batch_size": (RENV.RERANK_BATCH if RENV else int(os.getenv("RERANK_BATCH", "8"))),
        "input_topk": (RENV.RERANK_INPUT_TOPK if RENV else int(os.getenv("RERANK_INPUT_TOPK", "50"))),
        "output_topk": (RENV.RERANK_KEEP if RENV else int(os.getenv("RERANK_KEEP", "12"))),
        "cache_enabled": True,
  ```
- Line 283: `RERANK_KEEP`
  ```python
  "batch_size": (RENV.RERANK_BATCH if RENV else int(os.getenv("RERANK_BATCH", "8"))),
        "input_topk": (RENV.RERANK_INPUT_TOPK if RENV else int(os.getenv("RERANK_INPUT_TOPK", "50"))),
        "output_topk": (RENV.RERANK_KEEP if RENV else int(os.getenv("RERANK_KEEP", "12"))),
        "cache_enabled": True,
    }
  ```

### src/dspy_modules/retriever/weights.py
- Line 12: `RETRIEVER_WEIGHTS_FILE`
  ```python
  @lru_cache(maxsize=32)
def load_weights(tag: str = "", file_path: str | None = None) -> dict[str, float]:
    path = file_path or os.getenv("RETRIEVER_WEIGHTS_FILE", "configs/retriever_weights.yaml")
    cfg: dict[str, float] = dict(DEFAULT)
    try:
  ```

### src/dspy_modules/vector_store.py
- Line 279: `HYBRID_USE_WRAPPER`
  ```python
  self.use_websearch_tsquery = use_websearch_tsquery
        # Wrapper configuration (feature flag + ns reserved slots)
        self.use_wrapper: bool = os.getenv("HYBRID_USE_WRAPPER", "1") == "1"
        try:
            self.ns_reserved: int = int(os.getenv("NS_RESERVED", "2"))
  ```
- Line 281: `NS_RESERVED`
  ```python
  self.use_wrapper: bool = os.getenv("HYBRID_USE_WRAPPER", "1") == "1"
        try:
            self.ns_reserved: int = int(os.getenv("NS_RESERVED", "2"))
        except Exception:
            self.ns_reserved = 2
  ```
- Line 319: `HYBRID_DEBUG_NS`
  ```python
  )

                debug_flag = os.getenv("HYBRID_DEBUG_NS", "0") == "1"
                try:
                    pool_ns_env = int(os.getenv("POOL_NS", "0"))
  ```
- Line 321: `POOL_NS`
  ```python
  debug_flag = os.getenv("HYBRID_DEBUG_NS", "0") == "1"
                try:
                    pool_ns_env = int(os.getenv("POOL_NS", "0"))
                except Exception:
                    pool_ns_env = 0
  ```
- Line 504: `VALIDATE_CANDIDATES`
  ```python
  # Optional: validate candidate rows into DTOs for downstream if requested
            try:
                if _RC_ADAPTER is not None and os.getenv("VALIDATE_CANDIDATES", "0") == "1":
                    raw = []
                    for idx, r in enumerate(payload["results"], start=1):
  ```
- Line 549: `INGEST_RUN_ID`
  ```python
  # Add run ID gating for evaluations
        run_id = os.getenv("INGEST_RUN_ID")
        chunk_variant = os.getenv("CHUNK_VARIANT")
        where_clause = "WHERE dc.embedding IS NOT NULL"
  ```
- Line 550: `CHUNK_VARIANT`
  ```python
  # Add run ID gating for evaluations
        run_id = os.getenv("INGEST_RUN_ID")
        chunk_variant = os.getenv("CHUNK_VARIANT")
        where_clause = "WHERE dc.embedding IS NOT NULL"
        params: list[Any] = [q_emb]  # First q_emb for SELECT
  ```
- Line 623: `INGEST_RUN_ID`
  ```python
  # Add run ID gating for evaluations
        run_id = os.getenv("INGEST_RUN_ID")
        chunk_variant = os.getenv("CHUNK_VARIANT")
  ```
- Line 624: `CHUNK_VARIANT`
  ```python
  # Add run ID gating for evaluations
        run_id = os.getenv("INGEST_RUN_ID")
        chunk_variant = os.getenv("CHUNK_VARIANT")

        where_clause = ""
  ```
- Line 720: `BM25_TRIGRAM_FALLBACK`
  ```python
  # Trigram fallback if results are thin
                    if len(rows) < limit and os.getenv("BM25_TRIGRAM_FALLBACK", "1") == "1":
                        try:
                            # Build fallback params explicitly to match placeholders:
  ```
- Line 788: `INGEST_RUN_ID`
  ```python
  # Add run ID gating for evaluations
        run_id = os.getenv("INGEST_RUN_ID")
        chunk_variant = os.getenv("CHUNK_VARIANT")
  ```
- Line 789: `CHUNK_VARIANT`
  ```python
  # Add run ID gating for evaluations
        run_id = os.getenv("INGEST_RUN_ID")
        chunk_variant = os.getenv("CHUNK_VARIANT")

        where_clause = ""
  ```
- Line 896: `TITLE_TRIGRAM_FALLBACK`
  ```python
  # Trigram fallback if results are thin
                    if len(rows) < limit and os.getenv("TITLE_TRIGRAM_FALLBACK", "1") == "1":
                        try:
                            cur.execute(
  ```
- Line 1065: `INGEST_RUN_ID`
  ```python
  # Add run ID gating for evaluations
        run_id = os.getenv("INGEST_RUN_ID")
        chunk_variant = os.getenv("CHUNK_VARIANT")
  ```
- Line 1066: `CHUNK_VARIANT`
  ```python
  # Add run ID gating for evaluations
        run_id = os.getenv("INGEST_RUN_ID")
        chunk_variant = os.getenv("CHUNK_VARIANT")

        where_clause = ""
  ```
- Line 1185: `INGEST_RUN_ID`
  ```python
  # Add run ID gating for evaluations
        run_id = os.getenv("INGEST_RUN_ID")
        chunk_variant = os.getenv("CHUNK_VARIANT")
  ```
- Line 1186: `CHUNK_VARIANT`
  ```python
  # Add run ID gating for evaluations
        run_id = os.getenv("INGEST_RUN_ID")
        chunk_variant = os.getenv("CHUNK_VARIANT")

        where_clause = ""
  ```

### src/utils/conversation_storage.py
- Line 1381: `DECISION_TRIGRAM_ENABLED`
  ```python
  import os as _os

            trigram_enabled = _os.getenv("DECISION_TRIGRAM_ENABLED", "true").lower() in ("1", "true", "yes")
            vector_query = None
            vector_params: list[Any] = []
  ```

### src/utils/logger.py
- Line 170: `LOG_LEVEL`
  ```python
  import os

    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE")
  ```
- Line 171: `LOG_FILE`
  ```python
  log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE")

    # Set up root logger
  ```

### src/utils/prompt_sanitizer.py
- Line 146: `SECURITY_MAX_FILE_MB`
  ```python
  # Check environment variable override
    env_max_size = os.getenv("SECURITY_MAX_FILE_MB")
    if env_max_size:
        try:
  ```

### src/utils/pyd_ndarray.py
- Line 11: `EVAL_STRICT_ARRAYS`
  ```python
  # Env-controlled strictness (CI vs dev)
STRICT = os.getenv("EVAL_STRICT_ARRAYS", "1") == "1"
  ```

### src/utils/retry_wrapper.py
- Line 118: `LLM_TIMEOUT_SEC`
  ```python
  # Check environment variable override
    env_timeout = os.getenv("LLM_TIMEOUT_SEC")
    if env_timeout:
        try:
  ```

### src/utils/timeout_config.py
- Line 56: `DB_CONNECT_TIMEOUT`
  ```python
  # Load from environment variables
    config.db_connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", config.db_connect_timeout))
    config.db_read_timeout = int(os.getenv("DB_READ_TIMEOUT", config.db_read_timeout))
    config.db_write_timeout = int(os.getenv("DB_WRITE_TIMEOUT", config.db_write_timeout))
  ```
- Line 57: `DB_READ_TIMEOUT`
  ```python
  # Load from environment variables
    config.db_connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", config.db_connect_timeout))
    config.db_read_timeout = int(os.getenv("DB_READ_TIMEOUT", config.db_read_timeout))
    config.db_write_timeout = int(os.getenv("DB_WRITE_TIMEOUT", config.db_write_timeout))
    config.db_pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", config.db_pool_timeout))
  ```
- Line 58: `DB_WRITE_TIMEOUT`
  ```python
  config.db_connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", config.db_connect_timeout))
    config.db_read_timeout = int(os.getenv("DB_READ_TIMEOUT", config.db_read_timeout))
    config.db_write_timeout = int(os.getenv("DB_WRITE_TIMEOUT", config.db_write_timeout))
    config.db_pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", config.db_pool_timeout))
  ```
- Line 59: `DB_POOL_TIMEOUT`
  ```python
  config.db_read_timeout = int(os.getenv("DB_READ_TIMEOUT", config.db_read_timeout))
    config.db_write_timeout = int(os.getenv("DB_WRITE_TIMEOUT", config.db_write_timeout))
    config.db_pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", config.db_pool_timeout))

    config.http_connect_timeout = int(os.getenv("HTTP_CONNECT_TIMEOUT", config.http_connect_timeout))
  ```
- Line 61: `HTTP_CONNECT_TIMEOUT`
  ```python
  config.db_pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", config.db_pool_timeout))

    config.http_connect_timeout = int(os.getenv("HTTP_CONNECT_TIMEOUT", config.http_connect_timeout))
    config.http_read_timeout = int(os.getenv("HTTP_READ_TIMEOUT", config.http_read_timeout))
    config.http_total_timeout = int(os.getenv("HTTP_TOTAL_TIMEOUT", config.http_total_timeout))
  ```
- Line 62: `HTTP_READ_TIMEOUT`
  ```python
  config.http_connect_timeout = int(os.getenv("HTTP_CONNECT_TIMEOUT", config.http_connect_timeout))
    config.http_read_timeout = int(os.getenv("HTTP_READ_TIMEOUT", config.http_read_timeout))
    config.http_total_timeout = int(os.getenv("HTTP_TOTAL_TIMEOUT", config.http_total_timeout))
  ```
- Line 63: `HTTP_TOTAL_TIMEOUT`
  ```python
  config.http_connect_timeout = int(os.getenv("HTTP_CONNECT_TIMEOUT", config.http_connect_timeout))
    config.http_read_timeout = int(os.getenv("HTTP_READ_TIMEOUT", config.http_read_timeout))
    config.http_total_timeout = int(os.getenv("HTTP_TOTAL_TIMEOUT", config.http_total_timeout))

    config.pdf_processing_timeout = int(os.getenv("PDF_PROCESSING_TIMEOUT", config.pdf_processing_timeout))
  ```
- Line 65: `PDF_PROCESSING_TIMEOUT`
  ```python
  config.http_total_timeout = int(os.getenv("HTTP_TOTAL_TIMEOUT", config.http_total_timeout))

    config.pdf_processing_timeout = int(os.getenv("PDF_PROCESSING_TIMEOUT", config.pdf_processing_timeout))
    config.file_upload_timeout = int(os.getenv("FILE_UPLOAD_TIMEOUT", config.file_upload_timeout))
    config.chunk_processing_timeout = int(os.getenv("CHUNK_PROCESSING_TIMEOUT", config.chunk_processing_timeout))
  ```
- Line 66: `FILE_UPLOAD_TIMEOUT`
  ```python
  config.pdf_processing_timeout = int(os.getenv("PDF_PROCESSING_TIMEOUT", config.pdf_processing_timeout))
    config.file_upload_timeout = int(os.getenv("FILE_UPLOAD_TIMEOUT", config.file_upload_timeout))
    config.chunk_processing_timeout = int(os.getenv("CHUNK_PROCESSING_TIMEOUT", config.chunk_processing_timeout))
  ```
- Line 67: `CHUNK_PROCESSING_TIMEOUT`
  ```python
  config.pdf_processing_timeout = int(os.getenv("PDF_PROCESSING_TIMEOUT", config.pdf_processing_timeout))
    config.file_upload_timeout = int(os.getenv("FILE_UPLOAD_TIMEOUT", config.file_upload_timeout))
    config.chunk_processing_timeout = int(os.getenv("CHUNK_PROCESSING_TIMEOUT", config.chunk_processing_timeout))

    config.llm_request_timeout = int(os.getenv("LLM_REQUEST_TIMEOUT", config.llm_request_timeout))
  ```
- Line 69: `LLM_REQUEST_TIMEOUT`
  ```python
  config.chunk_processing_timeout = int(os.getenv("CHUNK_PROCESSING_TIMEOUT", config.chunk_processing_timeout))

    config.llm_request_timeout = int(os.getenv("LLM_REQUEST_TIMEOUT", config.llm_request_timeout))
    config.llm_stream_timeout = int(os.getenv("LLM_STREAM_TIMEOUT", config.llm_stream_timeout))
  ```
- Line 70: `LLM_STREAM_TIMEOUT`
  ```python
  config.llm_request_timeout = int(os.getenv("LLM_REQUEST_TIMEOUT", config.llm_request_timeout))
    config.llm_stream_timeout = int(os.getenv("LLM_STREAM_TIMEOUT", config.llm_stream_timeout))

    config.health_check_timeout = int(os.getenv("HEALTH_CHECK_TIMEOUT", config.health_check_timeout))
  ```
- Line 72: `HEALTH_CHECK_TIMEOUT`
  ```python
  config.llm_stream_timeout = int(os.getenv("LLM_STREAM_TIMEOUT", config.llm_stream_timeout))

    config.health_check_timeout = int(os.getenv("HEALTH_CHECK_TIMEOUT", config.health_check_timeout))
    config.metrics_timeout = int(os.getenv("METRICS_TIMEOUT", config.metrics_timeout))
    config.startup_timeout = int(os.getenv("STARTUP_TIMEOUT", config.startup_timeout))
  ```
- Line 73: `METRICS_TIMEOUT`
  ```python
  config.health_check_timeout = int(os.getenv("HEALTH_CHECK_TIMEOUT", config.health_check_timeout))
    config.metrics_timeout = int(os.getenv("METRICS_TIMEOUT", config.metrics_timeout))
    config.startup_timeout = int(os.getenv("STARTUP_TIMEOUT", config.startup_timeout))
  ```
- Line 74: `STARTUP_TIMEOUT`
  ```python
  config.health_check_timeout = int(os.getenv("HEALTH_CHECK_TIMEOUT", config.health_check_timeout))
    config.metrics_timeout = int(os.getenv("METRICS_TIMEOUT", config.metrics_timeout))
    config.startup_timeout = int(os.getenv("STARTUP_TIMEOUT", config.startup_timeout))

    # Try to load from system.json if available
  ```

### tests/test_bedrock_client.py
- Line 335: `AWS_ACCESS_KEY_ID`
  ```python
  @unittest.skipUnless(
        os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("AWS_PROFILE"),
        "AWS credentials required for integration tests",
    )
  ```
- Line 335: `AWS_PROFILE`
  ```python
  @unittest.skipUnless(
        os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("AWS_PROFILE"),
        "AWS credentials required for integration tests",
    )
  ```

## Project YAML Configuration Files
Total YAML files: 72

- `.github/workflows/ci-apply-quarantine.yml`
- `.github/workflows/ci-bloat-guard.yml`
- `.github/workflows/ci-nightly-baseline.yml`
- `.github/workflows/ci-nightly-prop-tests.yml`
- `.github/workflows/ci-nightly-test-signal.yml`
- `.github/workflows/ci-pr-lanes.yml`
- `.github/workflows/ci-pr-quick.yml`
- `.github/workflows/ci-retirement-cleaner.yml`
- `.github/workflows/ci-schema-validation.yml`
- `.github/workflows/commit-message-check.yml`
- `.github/workflows/deep-audit.yml`
- `.github/workflows/drift-detector.yml`
- `.github/workflows/dry-run.yml`
- `.github/workflows/dspy-compile.yml`
- `.github/workflows/eval.yml`
- `.github/workflows/evals-docs.yml`
- `.github/workflows/maintenance-validation.yml`
- `.github/workflows/quick-check.yml`
- `.github/workflows/ragchecker-evaluation.yml`
- `.github/workflows/reader-gate.yml`
- `.github/workflows/reranker-ablation.yml`
- `.pre-commit-config.yml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/_new_new_secret_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/_new_secret_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/_super_secret_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/example_config_yaml/_health_check_test_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/example_config_yaml/aliases_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/example_config_yaml/azure_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/example_config_yaml/disable_schema_update.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/example_config_yaml/enterprise_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/example_config_yaml/langfuse_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/example_config_yaml/load_balancer.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/example_config_yaml/multi_instance_simple_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/example_config_yaml/oai_misc_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/example_config_yaml/opentelemetry_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/example_config_yaml/otel_test_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/example_config_yaml/pass_through_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/example_config_yaml/simple_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/example_config_yaml/spend_tracking_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/example_config_yaml/store_model_db_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/model_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/litellm/proxy/proxy_config.yaml`
- `.venv-linux/lib/python3.12/site-packages/markdown_it/port.yaml`
- `.venv-linux/lib/python3.12/site-packages/pre_commit/resources/empty_template_environment.yml`
- `.venv-linux/lib/python3.12/site-packages/pre_commit/resources/empty_template_pubspec.yaml`
- `.venv-linux/lib/python3.12/site-packages/safety/safety-policy-template.yml`
- `.venv-linux/lib/python3.12/site-packages/torch/_export/serde/schema.yaml`
- `.venv-linux/lib/python3.12/site-packages/torchgen/packaged/ATen/native/native_functions.yaml`
- `.venv-linux/lib/python3.12/site-packages/torchgen/packaged/ATen/native/tags.yaml`
- `.venv-linux/lib/python3.12/site-packages/torchgen/packaged/autograd/deprecated.yaml`
- `.venv-linux/lib/python3.12/site-packages/torchgen/packaged/autograd/derivatives.yaml`
- `300_experiments/300_eval_configs/faithfulness_quality.yaml`
- `300_experiments/300_eval_configs/latency_quality.yaml`
- `300_experiments/300_eval_configs/retrieval_quality.yaml`
- `300_experiments/300_eval_configs/robustness_quality.yaml`
- `baseline_artifacts/baseline_20250907_060050/eval_manifest.yaml`
- `baseline_artifacts/baseline_20250907_061631/eval_manifest.yaml`
- `best_weights.yaml`
- `config/agent_memory_spec.yaml`
- `config/retrieval.yaml`
- `configs/base.yaml`
- `configs/dev.yaml`
- `configs/precision_elevated.meta.yml`
- `configs/prod.yaml`
- `configs/reader_limits.yaml`
- `configs/retriever_limits.yaml`
- `configs/retriever_weights.yaml`
- `configs/test.yaml`
- `metrics/baseline_evaluations/latest_manifest.yaml`
- `templates/eval_manifest_template.yaml`
- `tests/budgets.yml`
- `tests/sentinels.yml`

## Configuration Classes Found
Total configuration classes: 153

- `scripts/_ragchecker_eval_impl.py:CleanRAGCheckerEvaluator`
- `scripts/advanced_analytics_system.py:AnalyticsConfig`
- `scripts/advanced_analytics_system.py:AnalyticsDatabase`
- `scripts/advanced_analytics_system.py:PerformanceMetric`
- `scripts/agent_communication_implementation.py:CommunicationDatabase`
- `scripts/cache_invalidation_integration.py:IntegrationConfig`
- `scripts/cache_invalidation_system.py:InvalidationConfig`
- `scripts/cache_performance_monitoring.py:CachePerformanceMonitor`
- `scripts/cache_performance_monitoring.py:MonitoringConfig`
- `scripts/cache_performance_monitoring.py:PerformanceAlert`
- `scripts/cache_performance_monitoring.py:PerformanceTrend`
- `scripts/code_review_integration.py:IntegrationConfig`
- `scripts/coder_agent_implementation.py:CoderDatabase`
- `scripts/comprehensive_system_monitor.py:DatabaseHealthMonitor`
- `scripts/comprehensive_system_monitor.py:DatabaseMetrics`
- `scripts/comprehensive_system_monitor.py:PipelinePerformanceMonitor`
- `scripts/comprehensive_testing_suite.py:TestConfig`
- `scripts/documentation_agent_implementation.py:DocumentationDatabase`
- `scripts/end_to_end_system_validation.py:DatabaseLayerValidator`
- `scripts/end_to_end_system_validation.py:MemorySystemValidator`
- `scripts/end_to_end_system_validation.py:PerformanceValidator`
- `scripts/enhanced_memory_orchestrator.py:EnhancedMemoryOrchestrator`
- `scripts/enhanced_memory_orchestrator_with_heuristics.py:EnhancedMemoryOrchestratorWithHeuristics`
- `scripts/episodic_memory_integration.py:EpisodicMemoryIntegration`
- `scripts/episodic_memory_system.py:EpisodicMemorySystem`
- `scripts/eval_manifest_generator.py:EvalManifestGenerator`
- `scripts/final_precision_push_config.py:FinalPrecisionPushConfig`
- `scripts/final_ragas_push_config.py:FinalRAGASPushConfig`
- `scripts/focused_config_migration.py:FocusedConfigurationAnalyzer`
- `scripts/health_gated_evaluation.py:HealthGatedEvaluator`
- `scripts/ltst_memory_integration.py:LTSTIntegrationConfig`
- `scripts/ltst_memory_integration.py:LTSTMemoryIntegration`
- `scripts/mcp_memory_server.py:MemoryQuery`
- `scripts/mcp_memory_server.py:MemoryResponse`
- `scripts/memory_benchmark.py:MemoryBenchmark`
- `scripts/migrate_memory_context.py:MemoryContextMigrator`
- `scripts/migrate_to_pydantic_settings.py:ConfigurationMigrationAnalyzer`
- `scripts/migrate_to_pydantic_settings.py:Performance`
- `scripts/migrate_to_pydantic_settings.py:TimeoutConfig`
- `scripts/model_adaptation_framework.py:AdaptationConfig`
- `scripts/model_adaptation_framework.py:PerformanceBasedAdapter`
- `scripts/nightly_smoke_evaluation.py:NightlySmokeEvaluator`
- `scripts/overflow_handler.py:OverflowConfig`
- `scripts/performance_monitor.py:MonitoringConfig`
- `scripts/performance_monitor.py:PerformanceDashboard`
- `scripts/performance_monitor.py:PerformanceDatabase`
- `scripts/performance_monitor.py:PerformanceMetric`
- `scripts/performance_monitor.py:PerformanceMonitor`
- `scripts/performance_monitor.py:PerformanceSnapshot`
- `scripts/performance_optimization.py:OptimizationConfig`
- `scripts/performance_optimization.py:PerformanceMetrics`
- `scripts/performance_optimization.py:PerformanceOptimizer`
- `scripts/postgresql_cache_service.py:CacheConfig`
- `scripts/precision_climb_v2_config.py:PrecisionClimbV2Config`
- `scripts/precision_lift_pack_config.py:PrecisionLiftPackConfig`
- `scripts/precision_push_final_config.py:PrecisionPushFinalConfig`
- `scripts/precision_recovery_config.py:PrecisionRecoveryConfig`
- `scripts/production_deployment_validation.py:ProductionConfig`
- `scripts/production_ragas_config.py:ProductionRAGASConfig`
- `scripts/ragchecker_constitution_validator.py:RAGCheckerConstitutionValidator`
- `scripts/ragchecker_debug_manager.py:RAGCheckerDebugContext`
- `scripts/ragchecker_debug_manager.py:RAGCheckerDebugManager`
- `scripts/ragchecker_enhanced_evaluation.py:EnhancedRAGCheckerEvaluator`
- `scripts/ragchecker_enhanced_with_limit_features.py:EnhancedRAGCheckerWithLimitFeatures`
- `scripts/ragchecker_episodic_integration.py:RAGCheckerEpisodicIntegration`
- `scripts/ragchecker_error_recovery.py:RAGCheckerErrorRecovery`
- `scripts/ragchecker_evaluation.py:RAGCheckerEvaluator`
- `scripts/ragchecker_evaluation.py:RAGCheckerResult`
- `scripts/ragchecker_final_precision_push_evaluation.py:FinalPrecisionPushEvaluator`
- `scripts/ragchecker_final_ragas_push_evaluation.py:FinalRAGASPushEvaluator`
- `scripts/ragchecker_governance_integration.py:RAGCheckerGovernanceIntegration`
- `scripts/ragchecker_limit_inspired_evaluation.py:LimitInspiredEvaluator`
- `scripts/ragchecker_official_evaluation.py:OfficialRAGCheckerEvaluator`
- `scripts/ragchecker_official_evaluation.py:RAGCheckerInput`
- `scripts/ragchecker_performance_monitor.py:PerformanceAlert`
- `scripts/ragchecker_performance_monitor.py:PerformanceMonitor`
- `scripts/ragchecker_performance_monitor.py:PerformanceSnapshot`
- `scripts/ragchecker_performance_monitor.py:PerformanceThresholds`
- `scripts/ragchecker_performance_optimizer.py:PerformanceMetrics`
- `scripts/ragchecker_pipeline_governance.py:RAGCheckerPipelineGovernance`
- `scripts/ragchecker_precision_climb_v2_evaluation.py:EvalItem`
- `scripts/ragchecker_precision_climb_v2_evaluation.py:PrecisionClimbV2Evaluator`
- `scripts/ragchecker_precision_lift_evaluation.py:PrecisionLiftEvaluator`
- `scripts/ragchecker_precision_optimization.py:PrecisionOptimizedRAGChecker`
- `scripts/ragchecker_precision_recovery_evaluation.py:PrecisionRecoveryEvaluator`
- `scripts/ragchecker_production_evaluation.py:ProductionRAGASEvaluator`
- `scripts/ragchecker_pydantic_models.py:RAGCheckerInput`
- `scripts/ragchecker_pydantic_models.py:RAGCheckerMetrics`
- `scripts/ragchecker_pydantic_models.py:RAGCheckerResult`
- `scripts/ragchecker_ragas_competitive_evaluation.py:RAGASCompetitiveEvaluator`
- `scripts/research_agent_implementation.py:ResearchDatabase`
- `scripts/resilience_system.py:ResilienceConfig`
- `scripts/resilience_system.py:ResilienceDatabase`
- `scripts/run_evaluation_suite.py:EvaluationSuiteRunner`
- `scripts/similarity_scoring_algorithms.py:SimilarityConfig`
- `scripts/unified_memory_orchestrator.py:UnifiedMemoryOrchestrator`
- `scripts/uv_performance_monitor.py:UVPerformanceMonitor`
- `src/config/models.py:Database`
- `src/config/models.py:Eval`
- `src/config/models.py:Memory`
- `src/config/models.py:Observability`
- `src/config/models.py:Performance`
- `src/config/models.py:RAG`
- `src/config/models.py:Security`
- `src/config/settings.py:Settings`
- `src/dspy_modules/dspy_reader_program.py:RAGAnswer`
- `src/dspy_modules/enhanced_rag_system.py:EnhancedRAGQueryInterface`
- `src/dspy_modules/enhanced_rag_system.py:EnhancedRAGSystem`
- `src/evaluation/enhanced_metrics.py:EnhancedEvaluator`
- `src/evaluation/enhanced_metrics.py:EvaluationMetrics`
- `src/evaluation/unified_schemas.py:EvaluationBatch`
- `src/evaluation/unified_schemas.py:EvaluationResult`
- `src/retrieval/freshness_enhancer.py:FreshnessConfig`
- `src/retrieval/intent_router.py:IntentRouterConfig`
- `src/retrieval/memory_integration.py:MemoryContext`
- `src/retrieval/memory_integration.py:MemoryIntegrator`
- `src/retrieval/prefilter.py:PrefilterConfig`
- `src/retrieval/robustness_checks.py:PerformanceMetrics`
- `src/schemas/eval.py:Config`
- `src/schemas/eval.py:EvaluationResult`
- `src/schemas/models.py:Config`
- `src/schemas/results.py:EvaluationSuiteResult`
- `src/training/domain_tuning_pipeline.py:DomainTuningConfig`
- `src/uncertainty/confidence_calibration.py:CalibrationConfig`
- `src/uncertainty/feedback_loops.py:FeedbackConfig`
- `src/uncertainty/feedback_loops.py:FeedbackDatabase`
- `src/uncertainty/selective_answering.py:SelectiveAnsweringConfig`
- `src/utils/database_resilience.py:DatabaseHealth`
- `src/utils/database_resilience.py:DatabaseResilienceManager`
- `src/utils/memory_rehydrator.py:MemoryRehydrator`
- `src/utils/opentelemetry_config.py:OpenTelemetryConfig`
- `src/utils/prompt_sanitizer.py:SecurityError`
- `src/utils/retry_wrapper.py:ConfigurationError`
- `src/utils/retry_wrapper.py:TimeoutError`
- `src/utils/timeout_config.py:TimeoutConfig`
- `src/utils/validator.py:SecurityError`
- `tests/prompt_eval.py:PromptEvalConfig`
- `tests/prompt_eval.py:PromptEvaluator`
- `tests/test_bedrock_integration.py:TestRAGCheckerIntegration`
- `tests/test_coder_role.py:TestCoderRoleConfiguration`
- `tests/test_coder_role_performance.py:TestCoderRolePerformance`
- `tests/test_config_profiles.py:TestProfileConfiguration`
- `tests/test_config_settings.py:TestConfigurationPrecedence`
- `tests/test_config_settings.py:TestSettings`
- `tests/test_fast_path.py:TestFastPathConfiguration`
- `tests/test_fast_path.py:TestFastPathPerformance`
- `tests/test_ragchecker_evaluation.py:TestOfficialRAGCheckerEvaluator`
- `tests/test_ragchecker_evaluation.py:TestRAGCheckerInput`
- `tests/test_ragchecker_evaluation.py:TestRAGCheckerIntegration`
- `tests/test_ragchecker_evaluation.py:TestRAGCheckerValidation`
- `tests/test_ragchecker_performance.py:TestRAGCheckerPerformance`
- `tests/test_ragchecker_performance.py:TestRAGCheckerScalability`
- `tests/test_session_registry_performance.py:TestSessionRegistryPerformance`

## Migration Priority

### High Priority (Core Configuration)
- `POSTGRES_DSN` - Core system configuration
- `AWS_REGION` - Core system configuration
- `AWS_ACCESS_KEY_ID` - Core system configuration
- `AWS_SECRET_ACCESS_KEY` - Core system configuration
- `DSPY_MODEL` - Core system configuration
- `CHUNK_SIZE` - Core system configuration
- `DB_CONNECT_TIMEOUT` - Core system configuration
- `DB_READ_TIMEOUT` - Core system configuration
- `DB_WRITE_TIMEOUT` - Core system configuration
- `HTTP_CONNECT_TIMEOUT` - Core system configuration
- `HTTP_READ_TIMEOUT` - Core system configuration
- `HTTP_TOTAL_TIMEOUT` - Core system configuration
- `LLM_REQUEST_TIMEOUT` - Core system configuration
- `LLM_STREAM_TIMEOUT` - Core system configuration

### Medium Priority (Feature Configuration)
- `EVAL_*` variables (11 found)
- `MEMORY_*` variables (3 found)
