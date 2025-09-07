# Production Configuration Locking System

## TL;DR

**What**: Lock validated chunking configurations (450/0.10/J=0.8/prefix-A) with versioning, shadow indexing, and production monitoring.

**When**: After validating configuration performance and before production deployment.

**How**: Use `scripts/lock_production_config.py` to lock config, then `scripts/production_evaluation.py` for evaluation.

## Overview

The Production Configuration Locking System provides a comprehensive approach to managing chunking configurations in production environments. It implements the validated 450/0.10/J=0.8/prefix-A configuration with proper versioning, shadow indexing, and monitoring.

## Core Components

### 1. Configuration Locking (`config_lock.py`)

**Purpose**: Freeze and version chunking configurations with metadata.

**Key Features**:
- Versioned configurations with timestamps
- Tokenizer information and hashing
- Baseline metrics storage
- Production promotion workflow

**Usage**:
```python
from dspy_rag_system.src.utils.config_lock import create_production_config

config = create_production_config(
    chunk_size=450,
    overlap_ratio=0.10,
    jaccard_threshold=0.8,
    prefix_policy="A",
    embedder_name="BAAI/bge-large-en-v1.5"
)
```

### 2. Shadow Indexing (`ShadowIndexManager`)

**Purpose**: Manage dual-table operations for safe configuration rollouts.

**Key Features**:
- Shadow table creation
- Dual retrieval support
- Ingest run ID generation
- Table routing logic

**Usage**:
```python
shadow_manager = ShadowIndexManager(config)
shadow_table = shadow_manager.create_shadow_table()
retrieval_table = shadow_manager.get_retrieval_table(use_shadow=True)
```

### 3. Production Guardrails (`ProductionGuardrails`)

**Purpose**: Monitor and validate production health.

**Key Features**:
- Configuration validation
- Retrieval health checks
- Prefix leakage detection
- Token budget enforcement

**Usage**:
```python
guardrails = ProductionGuardrails(config)
validation = guardrails.validate_config()
health = guardrails.check_retrieval_health(retrieval_results)
```

### 4. Evaluation Runbook (`EvaluationRunbook`)

**Purpose**: Generate one-command evaluation workflows.

**Key Features**:
- Environment variable setup
- Ingest command generation
- Evaluation command generation
- Sanity check commands

## Production Workflow

### Step 1: Lock Configuration

```bash
# Lock the validated configuration
python scripts/lock_production_config.py \
  --chunk-size 450 \
  --overlap-ratio 0.10 \
  --jaccard-threshold 0.8 \
  --prefix-policy A \
  --embedder "BAAI/bge-large-en-v1.5" \
  --generate-runbook
```

### Step 2: Run Production Evaluation

```bash
# Run complete evaluation with locked configuration
python scripts/production_evaluation.py
```

### Step 3: Monitor Health

```bash
# Check production health
python scripts/production_health_monitor.py
```

### Step 4: Promote to Production

```bash
# Promote configuration to production
python scripts/lock_production_config.py --promote
```

## Configuration Structure

### LockedConfig Fields

```python
@dataclass
class LockedConfig:
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
```

### Environment Variables

The system uses these environment variables for configuration:

- `CHUNK_SIZE`: Chunk size (default: 450)
- `OVERLAP_RATIO`: Overlap ratio (default: 0.10)
- `JACCARD_THRESHOLD`: Jaccard threshold (default: 0.8)
- `PREFIX_POLICY`: Prefix policy "A" or "B" (default: "A")
- `CHUNK_VERSION`: Configuration version
- `INGEST_RUN_ID`: Ingest run identifier
- `EVAL_DISABLE_CACHE`: Disable evaluation caching

## Production Guardrails

### Hard Caps

- **Max chunk size**: 1000 tokens
- **Max overlap ratio**: 0.5
- **Min Jaccard threshold**: 0.5
- **Token budget**: 1024 tokens per chunk

### Health Checks

1. **Configuration Validation**
   - Parameter bounds checking
   - Tokenizer availability
   - Embedder compatibility

2. **Retrieval Health**
   - Prefix leakage detection
   - Token budget compliance
   - Snapshot size validation

3. **Performance Monitoring**
   - Oracle hit rates
   - Retrieval latency
   - Deduplication rates

### Alert Conditions

- 🚨 Configuration validation failed
- 🚨 BM25 prefix leakage detected
- 🚨 Over budget chunks found
- ⚠️ Low retrieval snapshot size
- ⚠️ Low oracle hit rate

## Shadow Indexing Strategy

### Dual Table Approach

1. **Primary Table**: `document_chunks` (current production)
2. **Shadow Table**: `document_chunks_{version}` (new configuration)

### Retrieval Routing

```python
def get_retrieval_table(use_shadow: bool = False) -> str:
    if use_shadow and config.is_production:
        return shadow_table
    return primary_table
```

### Ingest Run ID Format

```
{chunk_version}-{config_hash[:8]}
```

Example: `2025-09-07-143022-v1-a1b2c3d4`

## Monitoring and Alerting

### Daily Health Dashboard

- **Retrieval Oracle Hit Rate**: Target ≥0.45
- **Filter Hit Rate**: Target ≥0.20
- **Reader Gold Usage**: Target ≥baseline
- **Retrieval Snapshot Size**: Target 30-60 chunks
- **CE Score Distribution**: Monitor for drift
- **Ingest Throughput**: Monitor performance
- **Deduplication Rate**: Target 10-35%

### Production Metrics

```json
{
  "timestamp": "2025-09-07T14:30:22Z",
  "config_version": "2025-09-07-143022-v1",
  "overall_healthy": true,
  "config_health": {
    "valid": true,
    "issues": [],
    "warnings": []
  },
  "retrieval_health": {
    "healthy": true,
    "bm25_prefix_leakage": 0,
    "over_budget_chunks": 0,
    "avg_snapshot_size": 45.2
  }
}
```

## Troubleshooting

### Common Issues

1. **Configuration Not Found**
   ```bash
   # Check active configuration
   cat config/locked_configs/active_config.json
   ```

2. **Environment Variables Not Set**
   ```bash
   # Verify environment setup
   python scripts/production_evaluation.py --skip-ingest --skip-eval
   ```

3. **Retrieval Health Issues**
   ```bash
   # Run health monitor
   python scripts/production_health_monitor.py
   ```

### Debug Commands

```bash
# Check configuration status
python -c "
from dspy_rag_system.src.utils.config_lock import ConfigLockManager
manager = ConfigLockManager()
config = manager.get_active_config()
print(f'Active config: {config.chunk_version if config else \"None\"}')
"

# Validate configuration
python -c "
from dspy_rag_system.src.utils.config_lock import ProductionGuardrails, LockedConfig
import json

with open('config/locked_configs/active_config.json') as f:
    config_data = json.load(f)
config = LockedConfig.from_dict(config_data)
guardrails = ProductionGuardrails(config)
validation = guardrails.validate_config()
print(f'Config valid: {validation[\"valid\"]}')
"
```

## Integration with Existing Systems

### Enhanced Chunking Integration

The configuration locking system integrates with the enhanced chunking module:

```python
# Environment variables automatically override config
config = ChunkingConfig(embedder_name="BAAI/bge-large-en-v1.5")
# Will use CHUNK_SIZE, OVERLAP_RATIO, etc. from environment
```

### RAGChecker Integration

The system works with existing RAGChecker evaluation:

```bash
# Standard RAGChecker evaluation with locked config
python scripts/ragchecker_official_evaluation.py \
  --cases eval/test_cases.json \
  --outdir metrics/baseline_evaluations \
  --use-bedrock \
  --bypass-cli
```

### Database Integration

Shadow tables integrate with existing database schema:

```sql
-- Shadow table creation (handled by ShadowIndexManager)
CREATE TABLE document_chunks_2025_09_07_143022_v1 (
  id VARCHAR(255) PRIMARY KEY,
  doc_id VARCHAR(255),
  chunk_index INTEGER,
  embedding_text TEXT,
  bm25_text TEXT,
  embedding_token_count INTEGER,
  bm25_token_count INTEGER,
  chunk_version VARCHAR(255),
  ingest_run_id VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Best Practices

### Configuration Management

1. **Always lock configurations** before production use
2. **Use shadow indexing** for safe rollouts
3. **Monitor health metrics** continuously
4. **Validate configurations** before promotion

### Evaluation Workflow

1. **Lock configuration** with baseline metrics
2. **Run shadow ingest** with new configuration
3. **Evaluate performance** against baseline
4. **Promote to production** if metrics improve
5. **Monitor continuously** for regressions

### Rollback Strategy

1. **Keep previous configuration** in history
2. **Maintain dual tables** during transition
3. **Monitor key metrics** for 48 hours
4. **Rollback if thresholds** are exceeded

## Future Enhancements

### Planned Features

1. **Automatic A/B Testing**: Route traffic between configurations
2. **Performance Regression Detection**: Automatic rollback triggers
3. **Configuration Optimization**: ML-driven parameter tuning
4. **Multi-Environment Support**: Staging and production configs

### Integration Points

1. **CI/CD Pipeline**: Automated configuration validation
2. **Monitoring Systems**: Real-time health dashboards
3. **Alert Systems**: Slack/email notifications
4. **Database Migrations**: Automated schema updates

## Conclusion

The Production Configuration Locking System provides a robust, production-ready approach to managing chunking configurations. It ensures configuration stability, enables safe rollouts, and provides comprehensive monitoring for production environments.

The system implements the validated 450/0.10/J=0.8/prefix-A configuration with proper versioning, shadow indexing, and monitoring, following the production deployment strategy outlined in the original requirements.
