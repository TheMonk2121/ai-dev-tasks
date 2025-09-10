#!/bin/bash
# Setup script for evaluation environment variables
# This script sets up all required environment variables for the evaluation system

echo "🔧 Setting up evaluation environment variables..."

# =============================================================================
# CRITICAL EVALUATION VARIABLES
# =============================================================================

# DSPy RAG System Path
export DSPY_RAG_PATH="dspy-rag-system/src"

# Evaluation Driver (synthetic for testing, dspy_rag for real evaluations)
export EVAL_DRIVER="synthetic"

# RAGChecker Configuration
export RAGCHECKER_USE_REAL_RAG="0"

# Retrieval Configuration
export RETR_TOPK_VEC="50"
export RETR_TOPK_BM25="50"

# Reranker Configuration
export RERANK_ENABLE="0"

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# PostgreSQL Database (use mock for testing, real for production)
export POSTGRES_DSN="mock://test"
# For real database: export POSTGRES_DSN="postgresql://danieljacobs@localhost:5432/ai_agency"

# Alternative database URL (some scripts use this)
export DATABASE_URL="mock://test"

# =============================================================================
# EVALUATION PROFILES
# =============================================================================

# Current evaluation profile
export EVAL_PROFILE="mock"

# Evaluation concurrency
export EVAL_CONCURRENCY="3"

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

# Default model for evaluations
export EVAL_DEFAULT_MODEL="anthropic.claude-3-haiku-20240307-v1:0"

# Fallback model
export EVAL_FALLBACK_MODEL="anthropic.claude-3-sonnet-20240229-v1:0"

# =============================================================================
# EVALUATION PATHS
# =============================================================================

# Gold cases path
export EVAL_GOLD_CASES_PATH="evals/gold/v1/gold_cases.jsonl"

# Evaluation manifest path
export EVAL_MANIFEST_PATH="evals/gold/v1/manifest.json"

# Results output directory
export EVAL_RESULTS_OUTPUT_DIR="metrics/baseline_evaluations"

# =============================================================================
# VALIDATION SETTINGS
# =============================================================================

# Validation strictness
export EVAL_VALIDATION_STRICT="true"

# Allow missing files
export EVAL_ALLOW_MISSING_FILES="false"

# Unknown tag warning
export EVAL_UNKNOWN_TAG_WARNING="true"

# Check file existence
export EVAL_CHECK_FILE_EXISTENCE="true"

# =============================================================================
# EVALUATION LIMITS
# =============================================================================

# Maximum cases per evaluation
export EVAL_MAX_CASES_PER_EVAL="100"

# Default sample size
export EVAL_DEFAULT_SAMPLE_SIZE="50"

# =============================================================================
# PERFORMANCE SETTINGS
# =============================================================================

# Concurrency limit
export EVAL_CONCURRENCY_LIMIT="3"

# Timeout in seconds
export EVAL_TIMEOUT_SECONDS="300"

# =============================================================================
# KNOWN TAGS
# =============================================================================

# Comma-separated list of known evaluation tags
export EVAL_KNOWN_TAGS="ops_health,meta_ops,rag_qa_single,rag_qa_multi,db_workflows,negatives,rag,dspy,memory,context"

# =============================================================================
# ADDITIONAL CONFIGURATION
# =============================================================================

# Disable cache for deterministic evaluations
export EVAL_DISABLE_CACHE="1"

# DSPy teleprompt cache
export DSPY_TELEPROMPT_CACHE="false"

# Use gold cases
export USE_GOLD="0"

# Gold cases path (alternative)
export GOLD_CASES_PATH="evals/gold/v1/gold_cases.jsonl"

echo "✅ Evaluation environment variables set up successfully!"
echo "📋 Key variables:"
echo "   - EVAL_DRIVER: $EVAL_DRIVER"
echo "   - POSTGRES_DSN: $POSTGRES_DSN"
echo "   - DSPY_RAG_PATH: $DSPY_RAG_PATH"
echo "   - RAGCHECKER_USE_REAL_RAG: $RAGCHECKER_USE_REAL_RAG"
echo "   - RETR_TOPK_VEC: $RETR_TOPK_VEC"
echo "   - RETR_TOPK_BM25: $RETR_TOPK_BM25"
echo "   - RERANK_ENABLE: $RERANK_ENABLE"
