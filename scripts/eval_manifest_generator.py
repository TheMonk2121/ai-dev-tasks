#!/usr/bin/env python3
"""
Evaluation Manifest Generator
Generates comprehensive run manifests for production-grade traceability and reproducibility.
"""

import hashlib
import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class EvalManifestGenerator:
    """Generates comprehensive evaluation manifests for production traceability."""

    def __init__(self, output_dir: str = "metrics/manifests"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_id = str(uuid.uuid4())[:8]
        self.timestamp = datetime.now().isoformat()

    def generate_manifest(self, config_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate comprehensive evaluation manifest."""
        config_overrides = config_overrides or {}

        manifest = {
            "manifest_id": self.manifest_id,
            "timestamp": self.timestamp,
            "run_type": "production_evaluation",
            "version": "1.0",
            
            # Model Configuration
            "models": self._capture_model_config(),
            
            # System Configuration
            "system_config": self._capture_system_config(config_overrides),
            
            # Data Configuration
            "data_config": self._capture_data_config(),
            
            # Evaluation Configuration
            "eval_config": self._capture_eval_config(config_overrides),
            
            # Infrastructure Configuration
            "infrastructure": self._capture_infrastructure_config(),
            
            # Quality Gates
            "quality_gates": self._capture_quality_gates(),
            
            # Deterministic Settings
            "deterministic_settings": self._capture_deterministic_settings(),
            
            # Health Checks
            "health_checks": self._capture_health_checks(),
            
            # Audit Trail
            "audit_trail": self._capture_audit_trail(),
        }

        return manifest

    def _capture_model_config(self) -> Dict[str, Any]:
        """Capture model configuration and IDs."""
        return {
            "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            "rerank_model": os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base"),
            "generation_model": os.getenv("GENERATION_MODEL", "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0"),
            "embedding_provider": os.getenv("EMBEDDING_PROVIDER", "local"),
            "generation_provider": os.getenv("GENERATION_PROVIDER", "bedrock"),
            "model_versions": {
                "embedding": self._get_model_version(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")),
                "rerank": self._get_model_version(os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")),
            }
        }

    def _capture_system_config(self, overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Capture system configuration with hash generation."""
        config = {
            # Retrieval Configuration
            "retrieval": {
                "topk_vec": int(os.getenv("RETR_TOPK_VEC", "140")),
                "topk_bm25": int(os.getenv("RETR_TOPK_BM25", "140")),
                "topk_other": int(os.getenv("RETR_TOPK_OTHER", "0")),
                "fusion_method": os.getenv("FUSION_METHOD", "RRF"),
                "rrf_k": int(os.getenv("RRF_K", "60")),
            },
            
            # Reranking Configuration
            "reranking": {
                "enabled": os.getenv("RERANK_ENABLE", "1") == "1",
                "model": os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base"),
                "pool_size": int(os.getenv("RERANK_POOL", "60")),
                "topn": int(os.getenv("RERANK_TOPN", "18")),
            },
            
            # Context Configuration
            "context": {
                "max_docs": int(os.getenv("CONTEXT_DOCS_MAX", "12")),
                "max_chars": int(os.getenv("CONTEXT_MAX_CHARS", "1600")),
                "tail_keep": int(os.getenv("FUSE_TAIL_KEEP", "0")),
            },
            
            # Performance Configuration
            "performance": {
                "workers": int(os.getenv("PIPELINE_WORKERS", "2")),
                "max_in_flight": int(os.getenv("BEDROCK_MAX_IN_FLIGHT", "1")),
                "max_rps": float(os.getenv("BEDROCK_MAX_RPS", "0.12")),
                "timeout_sec": int(os.getenv("BEDROCK_CALL_TIMEOUT_SEC", "35")),
            }
        }
        
        # Apply overrides
        config.update(overrides)
        
        # Generate configuration hash
        config_str = json.dumps(config, sort_keys=True)
        config_hash = hashlib.sha256(config_str.encode()).hexdigest()[:16]
        config["config_hash"] = config_hash
        
        return config

    def _capture_data_config(self) -> Dict[str, Any]:
        """Capture data configuration and run IDs."""
        return {
            "ingest_run_id": os.getenv("INGEST_RUN_ID", "unknown"),
            "chunk_variant": os.getenv("CHUNK_VARIANT", "default"),
            "dataset_version": os.getenv("DATASET_VERSION", "latest"),
            "eval_cases_file": os.getenv("EVAL_CASES_FILE", "datasets/eval_cases.jsonl"),
            "data_checksum": self._get_data_checksum(),
        }

    def _capture_eval_config(self, overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Capture evaluation configuration."""
        return {
            "eval_driver": os.getenv("EVAL_DRIVER", "dspy_rag"),
            "use_real_rag": os.getenv("RAGCHECKER_USE_REAL_RAG", "1") == "1",
            "bypass_cli": os.getenv("RAGCHECKER_BYPASS_CLI", "1") == "1",
            "disable_embeddings": os.getenv("RAGCHECKER_DISABLE_EMBEDDINGS", "1") == "1",
            "progress_log": os.getenv("RAGCHECKER_PROGRESS_LOG", "metrics/baseline_evaluations/progress.jsonl"),
            "save_candidates_max": int(os.getenv("SAVE_CANDIDATES_MAX", "20")),
            "snapshot_max_items": int(os.getenv("SNAPSHOT_MAX_ITEMS", "50")),
        }

    def _capture_infrastructure_config(self) -> Dict[str, Any]:
        """Capture infrastructure configuration."""
        return {
            "python_version": os.sys.version,
            "platform": os.name,
            "dspy_rag_path": os.getenv("DSPY_RAG_PATH", "src"),
            "database_url": self._mask_sensitive_data(os.getenv("DATABASE_URL", "postgresql://***")),
            "aws_region": os.getenv("AWS_REGION", "us-east-1"),
            "environment": os.getenv("ENVIRONMENT", "development"),
        }

    def _capture_quality_gates(self) -> Dict[str, Any]:
        """Capture quality gate thresholds."""
        return {
            "precision_min": float(os.getenv("PRECISION_MIN", "0.20")),
            "recall_min": float(os.getenv("RECALL_MIN", "0.45")),
            "f1_min": float(os.getenv("F1_MIN", "0.22")),
            "latency_max": float(os.getenv("LATENCY_MAX", "30.0")),
            "faithfulness_min": float(os.getenv("FAITHFULNESS_MIN", "0.60")),
            "oracle_retrieval_hit_min": float(os.getenv("ORACLE_RETRIEVAL_HIT_MIN", "0.85")),
            "reader_used_gold_min": float(os.getenv("READER_USED_GOLD_MIN", "0.70")),
        }

    def _capture_deterministic_settings(self) -> Dict[str, Any]:
        """Capture deterministic evaluation settings."""
        return {
            "temperature": float(os.getenv("TEMPERATURE", "0.0")),
            "disable_cache": os.getenv("EVAL_DISABLE_CACHE", "1") == "1",
            "prompt_audit": os.getenv("PROMPT_AUDIT", "1") == "1",
            "few_shot_ids": os.getenv("FEW_SHOT_IDS", "").split(",") if os.getenv("FEW_SHOT_IDS") else [],
            "prompt_hash": self._get_prompt_hash(),
            "cot_flag": os.getenv("COT_FLAG", "0") == "1",
            "seed": int(os.getenv("RANDOM_SEED", "42")),
        }

    def _capture_health_checks(self) -> Dict[str, Any]:
        """Capture health check configuration."""
        return {
            "env_validation": os.getenv("HEALTH_CHECK_ENV", "1") == "1",
            "index_present": os.getenv("HEALTH_CHECK_INDEX", "1") == "1",
            "token_budget": os.getenv("HEALTH_CHECK_TOKEN_BUDGET", "1") == "1",
            "prefix_leakage": os.getenv("HEALTH_CHECK_PREFIX_LEAKAGE", "1") == "1",
            "database_connectivity": os.getenv("HEALTH_CHECK_DB", "1") == "1",
            "model_availability": os.getenv("HEALTH_CHECK_MODELS", "1") == "1",
        }

    def _capture_audit_trail(self) -> Dict[str, Any]:
        """Capture audit trail information."""
        return {
            "git_commit": self._get_git_commit(),
            "git_branch": self._get_git_branch(),
            "user": os.getenv("USER", "unknown"),
            "hostname": os.getenv("HOSTNAME", "unknown"),
            "pid": os.getpid(),
            "working_directory": os.getcwd(),
            "environment_variables": self._get_relevant_env_vars(),
        }

    def _get_model_version(self, model_name: str) -> str:
        """Get model version information."""
        # This would typically query the model registry or API
        # For now, return a placeholder
        return f"{model_name}_v1.0"

    def _get_data_checksum(self) -> str:
        """Get data checksum for reproducibility."""
        eval_file = os.getenv("EVAL_CASES_FILE", "datasets/eval_cases.jsonl")
        if os.path.exists(eval_file):
            with open(eval_file, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        return "unknown"

    def _get_prompt_hash(self) -> str:
        """Get prompt hash for audit trail."""
        # This would hash the actual prompts used
        # For now, return a placeholder
        return "prompt_hash_placeholder"

    def _get_git_commit(self) -> str:
        """Get current git commit hash."""
        try:
            import subprocess
            result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
            return result.stdout.strip()[:8] if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

    def _get_git_branch(self) -> str:
        """Get current git branch."""
        try:
            import subprocess
            result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

    def _get_relevant_env_vars(self) -> Dict[str, str]:
        """Get relevant environment variables for audit trail."""
        relevant_vars = [
            "DSPY_RAG_PATH", "EVAL_DRIVER", "RAGCHECKER_USE_REAL_RAG",
            "RETR_TOPK_VEC", "RETR_TOPK_BM25", "RERANK_ENABLE",
            "BEDROCK_MAX_RPS", "AWS_REGION", "ENVIRONMENT"
        ]
        return {var: os.getenv(var, "not_set") for var in relevant_vars}

    def _mask_sensitive_data(self, data: str) -> str:
        """Mask sensitive data in configuration."""
        if "://" in data:
            parts = data.split("://")
            if len(parts) > 1:
                return f"{parts[0]}://***"
        return data

    def save_manifest(self, manifest: Dict[str, Any], format: str = "yaml") -> str:
        """Save manifest to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"eval_manifest_{timestamp}_{self.manifest_id}.{format}"
        filepath = self.output_dir / filename

        if format == "yaml":
            with open(filepath, "w") as f:
                yaml.dump(manifest, f, default_flow_style=False, indent=2)
        elif format == "json":
            with open(filepath, "w") as f:
                json.dump(manifest, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return str(filepath)

    def load_manifest(self, filepath: str) -> Dict[str, Any]:
        """Load manifest from file."""
        with open(filepath, "r") as f:
            if filepath.endswith(".yaml") or filepath.endswith(".yml"):
                return yaml.safe_load(f)
            elif filepath.endswith(".json"):
                return json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {filepath}")


def main():
    """Main entry point for manifest generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate evaluation manifest")
    parser.add_argument("--output-dir", default="metrics/manifests", help="Output directory for manifests")
    parser.add_argument("--format", choices=["yaml", "json"], default="yaml", help="Output format")
    parser.add_argument("--config-file", help="Configuration file to load overrides from")
    
    args = parser.parse_args()
    
    # Load configuration overrides if provided
    config_overrides = {}
    if args.config_file:
        with open(args.config_file, "r") as f:
            if args.config_file.endswith(".yaml") or args.config_file.endswith(".yml"):
                config_overrides = yaml.safe_load(f)
            elif args.config_file.endswith(".json"):
                config_overrides = json.load(f)
    
    # Generate manifest
    generator = EvalManifestGenerator(args.output_dir)
    manifest = generator.generate_manifest(config_overrides)
    
    # Save manifest
    filepath = generator.save_manifest(manifest, args.format)
    
    print(f"✅ Evaluation manifest generated: {filepath}")
    print(f"📋 Manifest ID: {manifest['manifest_id']}")
    print(f"🔧 Config Hash: {manifest['system_config']['config_hash']}")
    print(f"📊 Data Checksum: {manifest['data_config']['data_checksum']}")
    
    return filepath


if __name__ == "__main__":
    main()
