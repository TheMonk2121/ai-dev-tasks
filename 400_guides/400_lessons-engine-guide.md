# Lessons Engine System Guide

## TL;DR

The Closed-Loop Lessons Engine (CLLE) systematically learns from evaluation runs and applies those lessons to future runs, creating a continuous improvement loop that addresses the core gap in the evaluation process.

## Overview

The lessons engine consists of four core components that work together to:
1. **Extract** lessons from evaluation results
2. **Store** lessons persistently for future use
3. **Load** relevant lessons for new runs
4. **Apply** lessons to generate improved configurations

## Core Components

### 1. Lessons Extractor (`scripts/lessons_extractor.py`)

**Purpose**: Analyzes evaluation results and generates structured lessons

**Key Functions**:
- `analyze_failure_modes()`: Identifies performance patterns
- `generate_lessons()`: Creates lessons with parameter recommendations
- `main()`: Orchestrates the extraction process

**Usage**:
```bash
python3 scripts/lessons_extractor.py <run_json_path> [progress_jsonl_path] [out_jsonl]
```

**Example Lesson Generated**:
```json
{
  "id": "LL-2025-09-06-001",
  "finding": {"pattern": "high_precision_low_recall", "evidence": {"precision": 0.85, "recall": 0.15}},
  "recommendation": {
    "changes": [
      {"key": "RETRIEVAL_TOP_K", "op": "add", "value": 2},
      {"key": "RERANK_TOP_K", "op": "add", "value": 5}
    ],
    "predicted_effect": {"recall": "+0.03~+0.06", "precision": "-0.01~0"}
  }
}
```

### 2. Lessons Loader (`scripts/lessons_loader.py`)

**Purpose**: Loads relevant lessons and generates candidate configurations

**Key Functions**:
- `filter_lessons()`: Filters lessons by scope and relevance
- `resolve_conflicts()`: Handles competing lessons
- `apply_changes()`: Applies parameter changes to configurations
- `main()`: Orchestrates the loading process

**Usage**:
```bash
python3 scripts/lessons_loader.py <base_env> <lessons_jsonl> [--mode advisory|apply] [--scope-level profile|dataset|global] [--window N]
```

**Modes**:
- `advisory`: Generate candidate config and decision docke
- `apply`: Apply lessons directly (with quality gate enforcement)

### 3. Evolution Tracker (`scripts/evolution_tracker.py`)

**Purpose**: Tracks configuration lineage and evolution

**Key Functions**:
- `scan_configs()`: Scans all configuration files and metadata
- `build_evolution_graph()`: Creates evolution relationships
- `generate_mermaid_diagram()`: Visualizes configuration evolution

**Usage**:
```bash
python3 scripts/evolution_tracker.py
```

**Outputs**:
- `configs/EVOLUTION.json`: Structured evolution data
- `configs/EVOLUTION.md`: Human-readable evolution repor

### 4. Quality Checker (`scripts/lessons_quality_check.py`)

**Purpose**: Validates system integrity and completeness

**Key Functions**:
- `check_lessons_file()`: Validates lessons JSONL forma
- `check_config_metadata()`: Ensures metadata completeness
- `check_derived_configs()`: Validates generated configurations
- `check_quality_gates()`: Verifies quality gate configuration

**Usage**:
```bash
python3 scripts/lessons_quality_check.py
```

## Integration with Evaluation System

### Command Line Integration

The lessons engine is integrated into `ragchecker_official_evaluation.py` with new arguments:

```bash
python3 scripts/ragchecker_official_evaluation.py
  --lessons-mode {off,advisory,apply}
  --lessons-scope {auto,dataset,profile,global}
  --lessons-window N
```

### Pre-Run Integration

Before evaluation:
1. Loads relevant lessons based on scope
2. Generates candidate configuration
3. Applies lessons if in "apply" mode
4. Sets environment variables for tracking

### Post-Run Integration

After evaluation:
1. Extracts lessons from results
2. Stores lessons in JSONL forma
3. Updates evolution tracking
4. Persists metadata in results

## Quality Gates and Safety

### Quality Gate Configuration

Quality gates are defined in `config/ragchecker_quality_gates.json`:

```json
{
  "precision": {"min": 0.20},
  "recall": {"min": 0.45},
  "f1": {"min": 0.22},
  "latency": {"max": 5.0},
  "cost": {"max": 0.10}
}
```

### Safety Mechanisms

1. **Conservative Effect Parsing**: Handles malformed effect strings gracefully
2. **Quality Gate Enforcement**: Blocks apply mode if violations detected
3. **Conflict Resolution**: Prevents duplicate parameter changes
4. **Scope Filtering**: Only applies relevant lessons

## Data Flow

```
Evaluation Run
    ↓
Extract Lessons (lessons_extractor.py)
    ↓
Store Lessons (metrics/lessons/lessons.jsonl)
    ↓
Load Lessons (lessons_loader.py)
    ↓
Apply Lessons (generate candidate config)
    ↓
Next Evaluation Run
```

## File Structure

```
metrics/
├── lessons/
│   └── lessons.jsonl          # Stored lessons
├── derived_configs/
│   ├── *_candidate.env        # Generated configurations
│   └── *_decision_docket.md   # Decision documentation
└── baseline_evaluations/
    └── *.json                 # Evaluation results with lessons metadata

configs/
├── *.env                      # Base configurations
├── *.meta.yml                 # Configuration metadata
├── EVOLUTION.json             # Evolution tracking data
├── EVOLUTION.md               # Evolution repor
└── ragchecker_quality_gates.json  # Quality thresholds
```

## Stateless State Discovery

**For stateless agents to determine current state and next actions:**

### **Latest Results Analysis**
```bash
# Get most recent evaluation results
LATEST_RESULTS=$(ls -t metrics/baseline_evaluations/*.json | head -1)
echo "Latest results: $LATEST_RESULTS"

# Parse lessons metadata
jq '.run_config.lessons' "$LATEST_RESULTS"
```

### **Explicit Stateless State Discovery Procedure**

**For stateless agents to determine current state and next actions:**

1. **Find latest eval JSON** under `metrics/baseline_evaluations/` and parse:
   - `.run_config.lessons.lessons_mode`
   - `.run_config.lessons.applied_lessons[]`
   - `.run_config.lessons.decision_docket`
   - `.run_config.lessons.candidate_env`
   - `.run_config.lessons.apply_blocked`
   - `.run_config.lessons.gate_warnings[]`
   - `.run_config.env.RAGCHECKER_ENV_FILE`
   - `.run_config.env.LESSONS_APPLIED` or `.run_config.env.LESSONS_SUGGESTED`
   - `.run_config.env.DECISION_DOCKET`

2. **Decision Logic**:
   - **If `apply_blocked == true`**: Read the docket's "Quality Gates" section; do not apply; propose next eval plan
   - **If `lessons_mode == "advisory"`**: Human review → optionally rerun in apply mode
   - **If `lessons_mode == "apply"`**: Check results, document lessons learned

3. **Next Actions**:
   - **Always**: Run quality checks and evolution tracking
   - **Document**: Add evaluation results to backlog with docket link

### **Key JSON Structure to Parse**
```json
{
  "run_config": {
    "lessons": {
      "lessons_mode": "advisory|apply",
      "lessons_scope": "profile|dataset|global",
      "lessons_window": 5,
      "applied_lessons": ["LL-2025-09-06-001"],
      "decision_docket": "metrics/derived_configs/20250906_153947_decision_docket.md",
      "candidate_env": "metrics/derived_configs/20250906_153947_candidate.env",
      "apply_blocked": false,
      "gate_warnings": []
    },
    "env": {
      "RAGCHECKER_ENV_FILE": "configs/precision_elevated.env",
      "LESSONS_APPLIED": "LL-2025-09-06-001",
      "LESSONS_SUGGESTED": "LL-2025-09-06-001",
      "DERIVED_FROM": "precision_elevated.env",
      "DECISION_DOCKET": "metrics/derived_configs/20250906_153947_decision_docket.md"
    }
  }
}
```

### **Decision Tree for Next Actions**
1. **If `apply_blocked == true`**: Read decision docket, fix gates before applying
2. **If `lessons_mode == advisory`**: Human review of docket, optionally rerun with `--lessons-mode apply`
3. **If `lessons_mode == apply`**: Check results, document lessons learned
4. **Always**: Run quality checks and evolution tracking

## Env Vars & Modes

| Mode | Environment Variables Set | Behavior |
|------|---------------------------|----------|
| **advisory** | `LESSONS_SUGGESTED`, `DECISION_DOCKET` | Base env used; generates candidate config and decision docket for review |
| **apply (success)** | `LESSONS_APPLIED`, `DERIVED_FROM`, `RAGCHECKER_ENV_FILE` | Candidate env used; applies lessons and updates active configuration |
| **apply (blocked)** | `LESSONS_SUGGESTED`, `DECISION_DOCKET` | Base env used; runner prints "Apply blocked ...; docket: <path>"; same as advisory |

### **Environment Variable Contract**
- **`LESSONS_APPLIED`**: Comma-separated list of lesson IDs that were applied
- **`LESSONS_SUGGESTED`**: Comma-separated list of lesson IDs that were suggested
- **`DERIVED_FROM`**: Base configuration file that was used
- **`DECISION_DOCKET`**: Path to decision docket markdown file
- **`RAGCHECKER_ENV_FILE`**: Path to active environment configuration

## Gate Enforcement Semantics

### **Quality Gate Rules (Actual Logic Implemented)**
- **Min-gated metrics** (precision, recall, f1, faithfulness): Block apply if worst-case predicted delta ≤ 0 (i.e., could reduce)
- **Max-gated metrics** (latency): Block apply on any predicted increase (including "+10~15%")
- **Percent effects**: Treated conservatively; use docket to inspect warnings
- **Unparseable effects**: Skip strict enforcement, log warning

### **Gate Configuration**
```json
{
  "precision": {"min": 0.20},
  "recall": {"min": 0.45},
  "f1": {"min": 0.22},
  "latency": {"max": 30.0},
  "faithfulness": {"min": 0.60}
}
```

### **Effect Parsing Examples**
- **`"+0.03~+0.06"`**: Min=0.03, Max=0.06 (absolute)
- **`"+10~15%"`**: Min=10%, Max=15% (percentage)
- **`"-0.02"`**: Min=-0.02, Max=-0.02 (absolute)
- **`"0.5"`**: Min=0.5, Max=0.5 (absolute)

### **Blocking Logic**
1. **For min gates**: Block if `max_delta <= 0` (any decrease)
2. **For max gates**: Block if `max_delta > 0` (any increase)
3. **Conservative approach**: When in doubt, block apply mode

## Usage Examples

### Basic Advisory Mode

```bash
# Run evaluation with lessons engine in advisory mode
python3 scripts/ragchecker_official_evaluation.py
  --lessons-mode advisory
  --lessons-scope profile
  --lessons-window 5
```

### Apply Mode with Quality Gates

```bash
# Run evaluation with lessons engine in apply mode
python3 scripts/ragchecker_official_evaluation.py
  --lessons-mode apply
  --lessons-scope profile
  --lessons-window 3
```

### System Health Check

```bash
# Check lessons system integrity
python3 scripts/lessons_quality_check.py

# Generate evolution tracking
python3 scripts/evolution_tracker.py
```

## Troubleshooting

### Common Issues

1. **JSON Parsing Errors**: Ensure logs go to stderr, JSON to stdou
2. **Quality Gate Violations**: Check predicted effects against gates
3. **Missing Lessons**: Verify lessons.jsonl exists and is valid
4. **Scope Mismatches**: Ensure lesson scopes match filter criteria

### Debug Commands

```bash
# Check lessons file validity
python3 scripts/lessons_quality_check.py

# Test lessons loader
python3 scripts/lessons_loader.py configs/precision_elevated.env metrics/lessons/lessons.jsonl --mode advisory

# View evolution tracking
cat configs/EVOLUTION.md
```

## Best Practices

1. **Always use advisory mode first** to review changes
2. **Check quality gates** before applying lessons
3. **Monitor evolution tracking** for configuration lineage
4. **Run quality checks** regularly to ensure system integrity
5. **Use appropriate scopes** to avoid irrelevant lessons

## Future Enhancements

### **Completed ✅**
- ✅ **Pre-commit hooks**: Lessons quality check runs automatically on commi
- ✅ **CI/CD integration**: Evolution tracking runs in CI workflows and produces `configs/EVOLUTION.md` regularly
- ✅ **Quality gate enforcement**: Conservative blocking logic implemented
- ✅ **JSON-only output**: Loader outputs machine-readable JSON to stdout, logs to stderr

### **Planned 🔄**
- **DB episodic store integration**: Persist lessons into episodic memory system
- **Sidecar metadata updates on apply**: Automatic `.meta.yml` updates (currently manual)
- **Enhanced conflict resolution**: Full precedence system (manual > profile > dataset > global)
- **Idempotence fingerprinting**: Prevent duplicate lesson applications

### **Manual Steps (Until Automation)**
- **Sidecar updates**: Manually update `.meta.yml` files after apply
- **Backlog documentation**: Manually add evaluation results to `000_core/000_backlog.md`

## Results JSON Schema

**Canonical JSON example for `.run_config.lessons` and `.run_config.env`**:

```json
{
  "run_config": {
    "env": {
      "RAGCHECKER_ENV_FILE": "configs/precision_elevated.env",
      "LESSONS_APPLIED": "LL-2025-09-06-001,LL-2025-09-06-002",
      "LESSONS_SUGGESTED": "LL-2025-09-06-001",
      "DERIVED_FROM": "precision_elevated.env",
      "DECISION_DOCKET": "metrics/derived_configs/20250906_153947_decision_docket.md"
    },
    "lessons": {
      "lessons_mode": "advisory|apply",
      "lessons_scope": "profile|dataset|global|auto",
      "lessons_window": 5,
      "applied_lessons": ["LL-2025-09-06-001"],
      "decision_docket": "metrics/derived_configs/20250906_153947_decision_docket.md",
      "candidate_env": "metrics/derived_configs/20250906_153947_candidate.env",
      "apply_blocked": false,
      "gate_warnings": []
    }
  }
}
```
