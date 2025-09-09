#!/usr/bin/env python3
"""
Evaluation Determinism System
- Determinism switches for trustworthy evaluations
- Prompt audit and tracking
- Oracle staging and retrieval breadth validation
"""

import hashlib
import json
import os
import random
import time
from dataclasses import dataclass
from typing import Any

from .config_lock import LockedConfig


@dataclass
class DeterminismConfig:
    """Configuration for deterministic evaluation"""

    # Determinism switches
    temperature: float = 0.0
    seed: int = 42
    eval_disable_cache: bool = True
    record_eval_path: bool = True

    # Prompt audit
    log_prompt_hash: bool = True
    log_few_shot_ids: bool = True
    log_cot_enabled: bool = True
    log_prompt_tokens: bool = True
    no_rationale_text: bool = True

    # Retrieval validation
    min_retrieval_snapshot_size: int = 30
    max_retrieved_context: int = 12
    oracle_sanity_check: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "temperature": self.temperature,
            "seed": self.seed,
            "eval_disable_cache": self.eval_disable_cache,
            "record_eval_path": self.record_eval_path,
            "log_prompt_hash": self.log_prompt_hash,
            "log_few_shot_ids": self.log_few_shot_ids,
            "log_cot_enabled": self.log_cot_enabled,
            "log_prompt_tokens": self.log_prompt_tokens,
            "no_rationale_text": self.no_rationale_text,
            "min_retrieval_snapshot_size": self.min_retrieval_snapshot_size,
            "max_retrieved_context": self.max_retrieved_context,
            "oracle_sanity_check": self.oracle_sanity_check,
        }


@dataclass
class PromptAudit:
    """Prompt audit information"""

    prompt_hash: str
    few_shot_ids: list[str]
    cot_enabled: bool
    prompt_tokens: int
    model_name: str
    timestamp: str
    eval_path: str
    ingest_run_id: str
    chunk_version: str
    config_hash: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "prompt_hash": self.prompt_hash,
            "few_shot_ids": self.few_shot_ids,
            "cot_enabled": self.cot_enabled,
            "prompt_tokens": self.prompt_tokens,
            "model_name": self.model_name,
            "timestamp": self.timestamp,
            "eval_path": self.eval_path,
            "ingest_run_id": self.ingest_run_id,
            "chunk_version": self.chunk_version,
            "config_hash": self.config_hash,
        }


class DeterminismManager:
    """Manages evaluation determinism and prompt auditing"""

    def __init__(self, config: LockedConfig):
        self.config = config
        self.determinism_config = DeterminismConfig()
        self.prompt_audits: list[PromptAudit] = []
        self.few_shot_queries: set[str] = set()

        # Set global determinism
        self._set_global_determinism()

    def _set_global_determinism(self) -> None:
        """Set global determinism switches"""
        # Set environment variables
        os.environ["EVAL_DISABLE_CACHE"] = "1" if self.determinism_config.eval_disable_cache else "0"
        os.environ["EVAL_PATH"] = "dspy_rag"
        os.environ["INGEST_RUN_ID"] = f"{self.config.chunk_version}-{self.config.get_config_hash()[:8]}"
        os.environ["CHUNK_VERSION"] = self.config.chunk_version
        os.environ["CONFIG_HASH"] = self.config.get_config_hash()

        # Set random seed
        random.seed(self.determinism_config.seed)

        print("🔧 Determinism switches set:")
        print(f"   Temperature: {self.determinism_config.temperature}")
        print(f"   Seed: {self.determinism_config.seed}")
        print(f"   Cache disabled: {self.determinism_config.eval_disable_cache}")
        print("   Eval path: dspy_rag")
        print(f"   Ingest run ID: {os.environ['INGEST_RUN_ID']}")

    def audit_prompt(
        self,
        prompt: str,
        few_shot_examples: list[dict[str, Any]] = None,
        cot_enabled: bool = False,
        model_name: str = "unknown",
    ) -> PromptAudit:
        """Audit a prompt and return audit information"""

        # Calculate prompt hash
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]

        # Extract few-shot IDs
        few_shot_ids = []
        if few_shot_examples:
            for example in few_shot_examples:
                if "id" in example:
                    few_shot_ids.append(example["id"])
                elif "question" in example:
                    # Use question hash as ID
                    question_hash = hashlib.sha256(example["question"].encode()).hexdigest()[:8]
                    few_shot_ids.append(f"q_{question_hash}")

        # Count prompt tokens (rough estimate)
        prompt_tokens = len(prompt.split()) * 1.3  # Rough token estimate

        # Create audit
        audit = PromptAudit(
            prompt_hash=prompt_hash,
            few_shot_ids=few_shot_ids,
            cot_enabled=cot_enabled,
            prompt_tokens=int(prompt_tokens),
            model_name=model_name,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            eval_path="dspy_rag",
            ingest_run_id=os.environ.get("INGEST_RUN_ID", ""),
            chunk_version=self.config.chunk_version,
            config_hash=self.config.get_config_hash(),
        )

        # Store audit
        self.prompt_audits.append(audit)

        # Check for few-shot leakage
        self._check_few_shot_leakage(prompt, few_shot_examples)

        return audit

    def _check_few_shot_leakage(self, prompt: str, few_shot_examples: list[dict[str, Any]] = None) -> None:
        """Check for few-shot/CoT leakage"""
        if few_shot_examples:
            for example in few_shot_examples:
                if "question" in example:
                    self.few_shot_queries.add(example["question"])

        # Check if eval query matches any few-shot query
        if prompt in self.few_shot_queries:
            print("⚠️  Few-shot leakage detected: eval query matches few-shot example")

    def validate_retrieval_breadth(self, retrieval_snapshot: list[dict[str, Any]]) -> dict[str, Any]:
        """Validate retrieval breadth"""
        snapshot_size = len(retrieval_snapshot)

        issues = []
        warnings = []

        if snapshot_size < self.determinism_config.min_retrieval_snapshot_size:
            issues.append(
                f"Retrieval snapshot size too low: {snapshot_size} (expected ≥{self.determinism_config.min_retrieval_snapshot_size})"
            )
        elif snapshot_size < 50:
            warnings.append(f"Retrieval snapshot size low: {snapshot_size} (expected ≥50)")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "snapshot_size": snapshot_size,
            "min_required": self.determinism_config.min_retrieval_snapshot_size,
        }

    def validate_oracle_sanity(self, oracle_hit: float) -> dict[str, Any]:
        """Validate oracle sanity"""
        if oracle_hit <= 0:
            return {
                "valid": False,
                "error": f"Oracle hit rate is zero: {oracle_hit}",
                "oracle_hit": oracle_hit,
            }

        if oracle_hit < 0.1:
            return {
                "valid": False,
                "warning": f"Oracle hit rate very low: {oracle_hit}",
                "oracle_hit": oracle_hit,
            }

        return {
            "valid": True,
            "oracle_hit": oracle_hit,
        }

    def validate_run_id_gating(self, retrieval_snapshot: list[dict[str, Any]]) -> dict[str, Any]:
        """Validate run-ID gating"""
        expected_run_id = f"{self.config.chunk_version}-{self.config.get_config_hash()[:8]}"
        expected_chunk_size = self.config.chunk_size

        issues = []
        warnings = []

        for i, chunk in enumerate(retrieval_snapshot):
            # Check ingest_run_id
            chunk_run_id = chunk.get("ingest_run_id", "")
            if chunk_run_id != expected_run_id:
                issues.append(f"Chunk {i}: Wrong ingest_run_id. Expected {expected_run_id}, got {chunk_run_id}")

            # Check chunk_size (if available in metadata)
            chunk_size = chunk.get("chunk_size")
            if chunk_size and chunk_size != expected_chunk_size:
                issues.append(f"Chunk {i}: Wrong chunk_size. Expected {expected_chunk_size}, got {chunk_size}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "expected_run_id": expected_run_id,
            "expected_chunk_size": expected_chunk_size,
        }

    def get_prompt_audit_summary(self) -> dict[str, Any]:
        """Get summary of prompt audits"""
        if not self.prompt_audits:
            return {"total_audits": 0}

        total_audits = len(self.prompt_audits)
        unique_prompts = len(set(audit.prompt_hash for audit in self.prompt_audits))
        total_tokens = sum(audit.prompt_tokens for audit in self.prompt_audits)
        cot_enabled_count = sum(1 for audit in self.prompt_audits if audit.cot_enabled)

        return {
            "total_audits": total_audits,
            "unique_prompts": unique_prompts,
            "total_tokens": total_tokens,
            "avg_tokens_per_prompt": total_tokens / total_audits if total_audits > 0 else 0,
            "cot_enabled_count": cot_enabled_count,
            "cot_enabled_rate": cot_enabled_count / total_audits if total_audits > 0 else 0,
        }

    def save_audit_log(self, filepath: str) -> None:
        """Save audit log to file"""
        audit_data = {
            "config": self.determinism_config.to_dict(),
            "locked_config": {
                "chunk_version": self.config.chunk_version,
                "config_hash": self.config.get_config_hash(),
                "chunk_size": self.config.chunk_size,
                "overlap_ratio": self.config.overlap_ratio,
                "jaccard_threshold": self.config.jaccard_threshold,
                "prefix_policy": self.config.prefix_policy,
            },
            "audits": [audit.to_dict() for audit in self.prompt_audits],
            "summary": self.get_prompt_audit_summary(),
        }

        with open(filepath, "w") as f:
            json.dump(audit_data, f, indent=2)

        print(f"📝 Audit log saved to: {filepath}")


def create_determinism_manager(config: LockedConfig) -> DeterminismManager:
    """Create a determinism manager for the given configuration"""
    return DeterminismManager(config)
