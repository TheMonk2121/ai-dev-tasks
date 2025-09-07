#!/usr/bin/env python3
"""
Configuration Locking System
- Freeze and version chunking configurations
- Shadow re-ingest with dual indexing
- Production monitoring and guardrails
- One-command evaluation runbook
"""

import hashlib
import json
import os
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .enhanced_chunking import ChunkingConfig, EnhancedChunker


@dataclass
class LockedConfig:
    """Locked configuration with versioning and metadata"""
    
    # Core configuration
    chunk_size: int
    overlap_ratio: float
    jaccard_threshold: float
    prefix_policy: str  # "A" or "B"
    
    # Versioning
    chunk_version: str
    embedder_name: str
    tokenizer_name: str
    tokenizer_hash: str
    
    # Metadata
    created_at: str
    created_by: str
    baseline_metrics: Dict[str, Any]
    
    # Production flags
    is_locked: bool = True
    is_production: bool = False
    shadow_table: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LockedConfig":
        """Create from dictionary"""
        return cls(**data)
    
    def get_config_hash(self) -> str:
        """Get hash of core configuration parameters"""
        core_params = {
            "chunk_size": self.chunk_size,
            "overlap_ratio": self.overlap_ratio,
            "jaccard_threshold": self.jaccard_threshold,
            "prefix_policy": self.prefix_policy,
            "embedder_name": self.embedder_name,
        }
        return hashlib.sha256(json.dumps(core_params, sort_keys=True).encode()).hexdigest()[:16]


class ConfigLockManager:
    """Manages configuration locking and versioning"""
    
    def __init__(self, config_dir: Path = Path("config/locked_configs")):
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.lock_file = self.config_dir / "active_config.json"
        self.history_dir = self.config_dir / "history"
        self.history_dir.mkdir(exist_ok=True)
    
    def create_locked_config(
        self,
        chunk_size: int = 450,
        overlap_ratio: float = 0.10,
        jaccard_threshold: float = 0.8,
        prefix_policy: str = "A",
        embedder_name: str = "BAAI/bge-large-en-v1.5",
        baseline_metrics: Optional[Dict[str, Any]] = None,
    ) -> LockedConfig:
        """Create a new locked configuration"""
        
        # Get tokenizer info
        tokenizer_name, tokenizer_hash = self._get_tokenizer_info(embedder_name)
        
        # Create version string
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        chunk_version = f"{timestamp}-v1"
        
        config = LockedConfig(
            chunk_size=chunk_size,
            overlap_ratio=overlap_ratio,
            jaccard_threshold=jaccard_threshold,
            prefix_policy=prefix_policy,
            chunk_version=chunk_version,
            embedder_name=embedder_name,
            tokenizer_name=tokenizer_name,
            tokenizer_hash=tokenizer_hash,
            created_at=datetime.now().isoformat(),
            created_by=os.getenv("USER", "unknown"),
            baseline_metrics=baseline_metrics or {},
            is_locked=True,
            is_production=False,
        )
        
        return config
    
    def lock_config(self, config: LockedConfig) -> None:
        """Lock a configuration and save it"""
        # Save to history
        history_file = self.history_dir / f"{config.chunk_version}.json"
        with open(history_file, "w") as f:
            json.dump(config.to_dict(), f, indent=2)
        
        # Set as active
        with open(self.lock_file, "w") as f:
            json.dump(config.to_dict(), f, indent=2)
        
        print(f"✅ Configuration locked: {config.chunk_version}")
        print(f"   Chunk size: {config.chunk_size}")
        print(f"   Overlap ratio: {config.overlap_ratio}")
        print(f"   Jaccard threshold: {config.jaccard_threshold}")
        print(f"   Prefix policy: {config.prefix_policy}")
        print(f"   Embedder: {config.embedder_name}")
    
    def get_active_config(self) -> Optional[LockedConfig]:
        """Get the currently active locked configuration"""
        if not self.lock_file.exists():
            return None
        
        try:
            with open(self.lock_file, "r") as f:
                data = json.load(f)
            return LockedConfig.from_dict(data)
        except Exception as e:
            print(f"⚠️  Error loading active config: {e}")
            return None
    
    def promote_to_production(self, config: LockedConfig) -> None:
        """Promote a configuration to production"""
        config.is_production = True
        config.shadow_table = f"document_chunks_{config.chunk_version.replace('-', '_')}"
        
        # Update active config
        with open(self.lock_file, "w") as f:
            json.dump(config.to_dict(), f, indent=2)
        
        print(f"🚀 Configuration promoted to production: {config.chunk_version}")
        print(f"   Shadow table: {config.shadow_table}")
    
    def _get_tokenizer_info(self, embedder_name: str) -> Tuple[str, str]:
        """Get tokenizer name and hash for embedder"""
        try:
            from transformers import AutoTokenizer
            
            tokenizer = AutoTokenizer.from_pretrained(embedder_name)
            tokenizer_name = tokenizer.name_or_path
            tokenizer_hash = hashlib.sha256(str(tokenizer).encode()).hexdigest()[:16]
            
            return tokenizer_name, tokenizer_hash
        except Exception:
            return "unknown", "unknown"


class ShadowIndexManager:
    """Manages shadow indexing and dual-table operations"""
    
    def __init__(self, config: LockedConfig):
        self.config = config
        self.shadow_table = config.shadow_table or f"document_chunks_{config.chunk_version.replace('-', '_')}"
        self.primary_table = "document_chunks"
    
    def create_shadow_table(self) -> str:
        """Create shadow table for new configuration"""
        # This would typically create a new table in your database
        # For now, we'll return the table name
        print(f"📊 Creating shadow table: {self.shadow_table}")
        return self.shadow_table
    
    def get_retrieval_table(self, use_shadow: bool = False) -> str:
        """Get the table to use for retrieval"""
        if use_shadow and self.config.is_production:
            return self.shadow_table
        return self.primary_table
    
    def get_ingest_run_id(self) -> str:
        """Get the ingest run ID for this configuration"""
        return f"{self.config.chunk_version}-{self.config.get_config_hash()[:8]}"


class ProductionGuardrails:
    """Production guardrails and monitoring"""
    
    def __init__(self, config: LockedConfig):
        self.config = config
        self.metrics_file = Path("metrics/production_guardrails.json")
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration against production requirements"""
        issues = []
        warnings = []
        
        # Hard caps
        if self.config.chunk_size > 1000:
            issues.append(f"Chunk size too large: {self.config.chunk_size}")
        
        if self.config.overlap_ratio > 0.5:
            issues.append(f"Overlap ratio too high: {self.config.overlap_ratio}")
        
        if self.config.jaccard_threshold < 0.5:
            warnings.append(f"Low Jaccard threshold: {self.config.jaccard_threshold}")
        
        # Tokenizer validation
        if self.config.tokenizer_name == "unknown":
            warnings.append("Tokenizer info not available")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "config_hash": self.config.get_config_hash(),
        }
    
    def check_retrieval_health(self, retrieval_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check retrieval health metrics"""
        if not retrieval_results:
            return {"healthy": False, "error": "No retrieval results"}
        
        # Check for prefix leakage in BM25
        bm25_with_prefix = sum(1 for r in retrieval_results 
                              if r.get("bm25_text", "").startswith("Document:"))
        
        # Check token counts
        token_counts = [r.get("embedding_token_count", 0) for r in retrieval_results]
        over_budget = sum(1 for t in token_counts if t > self.config.chunk_size)
        
        # Check retrieval snapshot size
        snapshot_sizes = [len(r.get("retrieval_snapshot", [])) for r in retrieval_results]
        avg_snapshot_size = sum(snapshot_sizes) / len(snapshot_sizes) if snapshot_sizes else 0
        
        return {
            "healthy": bm25_with_prefix == 0 and over_budget == 0,
            "bm25_prefix_leakage": bm25_with_prefix,
            "over_budget_chunks": over_budget,
            "avg_snapshot_size": avg_snapshot_size,
            "total_results": len(retrieval_results),
        }
    
    def save_metrics(self, metrics: Dict[str, Any]) -> None:
        """Save production metrics"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "config_version": self.config.chunk_version,
            "metrics": metrics,
        }
        
        with open(self.metrics_file, "w") as f:
            json.dump(data, f, indent=2)


class EvaluationRunbook:
    """One-command evaluation runbook"""
    
    def __init__(self, config: LockedConfig):
        self.config = config
        self.shadow_manager = ShadowIndexManager(config)
        self.guardrails = ProductionGuardrails(config)
    
    def generate_ingest_command(self) -> str:
        """Generate ingest command with locked configuration"""
        ingest_run_id = self.shadow_manager.get_ingest_run_id()
        
        env_vars = [
            f"INGEST_RUN_ID={ingest_run_id}",
            f"CHUNK_SIZE={self.config.chunk_size}",
            f"OVERLAP_RATIO={self.config.overlap_ratio}",
            f"JACCARD_THRESHOLD={self.config.jaccard_threshold}",
            f"PREFIX_POLICY={self.config.prefix_policy}",
            "EVAL_DISABLE_CACHE=1",
        ]
        
        return f"""
# Ingest with locked configuration
export {' '.join(env_vars)}

# Run enhanced ingest
python dspy-rag-system/scripts/ingest_enhanced.py --run-id "$INGEST_RUN_ID"
"""
    
    def generate_eval_command(self) -> str:
        """Generate evaluation command"""
        return """
# Evaluate with locked configuration
python scripts/ragchecker_official_evaluation.py \\
  --cases eval/test_cases.json \\
  --outdir metrics/baseline_evaluations \\
  --use-bedrock \\
  --bypass-cli
"""
    
    def generate_sanity_checks(self) -> str:
        """Generate sanity check commands"""
        return """
# Sanity checks
jq '{eval_path, schema_version}' metrics/baseline_evaluations/*.json
jq '.case_results | map(.retrieval_snapshot|length) | max' metrics/baseline_evaluations/*.json
jq '[.case_results[].oracle_retrieval_hit_prefilter] | add' metrics/baseline_evaluations/*.json
"""
    
    def generate_full_runbook(self) -> str:
        """Generate complete evaluation runbook"""
        return f"""
# Production Evaluation Runbook
# Configuration: {self.config.chunk_version}
# Hash: {self.config.get_config_hash()}

{self.generate_ingest_command()}

{self.generate_eval_command()}

{self.generate_sanity_checks()}

# Production health checks
python -c "
from dspy_rag_system.src.utils.config_lock import ProductionGuardrails, LockedConfig
import json

# Load config and run health checks
with open('config/locked_configs/active_config.json') as f:
    config_data = json.load(f)
config = LockedConfig.from_dict(config_data)
guardrails = ProductionGuardrails(config)

# Validate configuration
validation = guardrails.validate_config()
print(f'Config valid: {{validation[\"valid\"]}}')
if validation['issues']:
    print(f'Issues: {{validation[\"issues\"]}}')
if validation['warnings']:
    print(f'Warnings: {{validation[\"warnings\"]}}')
"
"""


def create_production_config(
    chunk_size: int = 450,
    overlap_ratio: float = 0.10,
    jaccard_threshold: float = 0.8,
    prefix_policy: str = "A",
    embedder_name: str = "BAAI/bge-large-en-v1.5",
    baseline_metrics: Optional[Dict[str, Any]] = None,
) -> LockedConfig:
    """Create and lock a production configuration"""
    
    manager = ConfigLockManager()
    config = manager.create_locked_config(
        chunk_size=chunk_size,
        overlap_ratio=overlap_ratio,
        jaccard_threshold=jaccard_threshold,
        prefix_policy=prefix_policy,
        embedder_name=embedder_name,
        baseline_metrics=baseline_metrics,
    )
    
    manager.lock_config(config)
    return config


def get_production_runbook() -> str:
    """Get the production evaluation runbook"""
    manager = ConfigLockManager()
    config = manager.get_active_config()
    
    if not config:
        return "No active configuration found. Run create_production_config() first."
    
    runbook = EvaluationRunbook(config)
    return runbook.generate_full_runbook()


if __name__ == "__main__":
    # Example usage
    config = create_production_config()
    print("\n" + "="*60)
    print("PRODUCTION EVALUATION RUNBOOK")
    print("="*60)
    print(get_production_runbook())
