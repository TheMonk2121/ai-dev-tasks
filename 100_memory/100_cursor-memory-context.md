
---
MEMORY_CONTEXT: HIGH
ANCHOR_KEY: memory-context
ANCHOR_PRIORITY: 0
ROLE_PINS:
  - planner
  - implementer
  - researcher
  - coder
CONTENT_TYPE: guide
COMPLEXITY: intermediate
LAST_UPDATED: 2025-09-11
NEXT_REVIEW: 2025-01-31
RELATED_FILES:
  - 400_01_memory-system-architecture.md
  - 400_02_memory-rehydration-context-management.md
  - UV_MIGRATION_COMPLETE.md
  - VENV_MAPPING_VERIFICATION.md
---

<!-- CONTEXT_INDEX
{
  "files": [
    {"path": "100_memory/100_cursor-memory-context.md", "role": "entry"},
    {"path": "000_core/000_evaluation-system-entry-point.md", "role": "evaluation-entry"},
    {"path": "000_core/000_backlog.md", "role": "priorities"},
    {"path": "000_core/004_development-roadmap.md", "role": "roadmap"},
    {"path": "400_guides/400_00_getting-started-and-index.md", "role": "getting-started"},
    {"path": "400_guides/400_03_system-overview-and-architecture.md", "role": "architecture"},
    {"path": "400_guides/400_06_memory-and-context-systems.md", "role": "navigation"},
    {"path": "400_guides/400_02_governance-and-ai-constitution.md", "role": "ai-safety"},
    {"path": "400_guides/400_01_documentation-playbook.md", "role": "file-analysis"},

    {"path": "100_memory/104_dspy-development-context.md", "role": "dspy-context"},
    {"path": "dspy-rag-system/tests/README-dev.md", "role": "test-development"},
    {"path": "200_setup/202_setup-requirements.md", "role": "setup"},
    {"path": "400_guides/400_04_development-workflow-and-standards.md", "role": "development-workflow"},
    {"path": "400_guides/400_11_deployments-ops-and-observability.md", "role": "deployment-operations"},
    {"path": "400_guides/400_10_security-compliance-and-access.md", "role": "integration-security"},
    {"path": "400_guides/400_11_deployments-ops-and-observability.md", "role": "migration"},
    {"path": "400_guides/400_11_deployments-ops-and-observability.md", "role": "performance"},
    {"path": "400_guides/400_05_coding-and-prompting-standards.md", "role": "few-shot"},
    {"path": "400_guides/400_06_memory-and-context-systems.md", "role": "memory-system"},
    {"path": "scripts/task_generation_automation.py", "role": "automation"},
    {"path": "scripts/backlog_status_tracking.py", "role": "automation"},
    {"path": "scripts/venv_manager.py", "role": "dev-environment"},
    {"path": "scripts/run_workflow.py", "role": "dev-environment"},
    {"path": "scripts/README_venv_manager.md", "role": "dev-environment"},
    {"path": "400_guides/400_12_product-management-and-roadmap.md", "role": "quick-reference"},
    {"path": "400_guides/400_12_product-management-and-roadmap.md", "role": "quick-reference"},
    {"path": "500_research-index.md", "role": "research-index"},
    {"path": "400_guides/400_documentation-tiering-guide.md", "role": "documentation-rules"},
    {"path": "000_core/005_troubleshooting-patterns.md", "role": "debugging-patterns"},
    {"path": "100_memory/100_communication-patterns-guide.md", "role": "communication-patterns"},
    {"path": "100_memory/100_dspy-role-communication-guide.md", "role": "dspy-communication"},
    {"path": "100_memory/100_technical-artifacts-integration-guide.md", "role": "technical-integration"},
    {"path": "100_memory/100_role-system-alignment-guide.md", "role": "role-alignment"},
    {"path": "000_core/009_implementation-patterns.md", "role": "implementation-patterns"},
    {"path": "100_memory/100_evidence-based-optimization-guide.md", "role": "evidence-optimization"},
    {"path": "000_core/006_database-troubleshooting.md", "role": "database-troubleshooting"},
    {"path": "artifacts/execution/Execution-B-1032-Documentation-t-t3-Authority-Structure-Implementation.md", "role": "b-1032-completion"}
  ]
}
CONTEXT_INDEX -->

<!-- ANCHOR_KEY: memory-context -->
<!-- ANCHOR_PRIORITY: 0 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher", "coder"] -->

# Cursor Memory Context

## 🔎 TL;DR {#tldr}

:

**🚨 MANDATORY FIRST STEP**: Run this command before any project work:
```bash
export POSTGRES_DSN="mock://test" && uv run python scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "current project status and core documentation"
```

**📊 CURRENT PROJECT STATUS**:
- **Lessons Engine**: ✅ **PRODUCTION READY** - Closed-Loop Lessons Engine (CLLE) fully implemented
- **Key Components**: lessons_extractor.py, lessons_loader.py, evolution_tracker.py, lessons_quality_check.py
- **Integration**: Full integration with ragchecker_official_evaluation.py
- **CI Integration**: CI produces `configs/EVOLUTION.md` regularly; loader emits JSON-only stdou
- **Current State**: System ready for evaluation runs with automatic lesson learning
- **Next Steps**: Run evaluations to generate and apply lessons

**🧠 LESSONS LEARNED**:
- Check `metrics/lessons/lessons.jsonl` for current lessons
- Check `metrics/derived_configs/` for generated configurations
- Check `configs/EVOLUTION.md` for configuration evolution
- Use `uv run python scripts/lessons_quality_check.py` to verify system health

| what this file is | read when | do next |
|---|---|---|
| Primary memory scaffold for AI rehydration and context management | Starting new session or need current project state
| Check backlog and system overview for next priorities; access DSPy roles via Unified Memory Orchestrator |

## 📚 Memory Guides Quick Reference {#memory-guides}

- **`100_memory/100_cursor-memory-context.md`** – authoritative entry point for memory rehydration, role context, and session policies.
- **`100_memory/104_dspy-development-context.md`** – DSPy-specific memory integrations, retrieval heuristics, and evaluation hooks.
- **`100_memory/100_role-system-alignment-guide.md`** – mapping between agent roles, memory stores, and orchestration safeguards.
- **`100_memory/100_technical-artifacts-integration-guide.md`** – integration patterns for artifacts, embeddings, and cross-system context.

🚧 **Quality Gates**: Deployment remains blocked until **F1 ≥ baseline**, **precision drift ≤ 2 pts**, **latency increase ≤ 15 %**, and **oracle metrics meet thresholds**. See `scripts/gate_and_promote.py` for enforcement details.

## 🚨 Critical Policies (Read First) {#critical-policies}

## 🚨 **CRITICAL: MEMORY REHYDRATION REQUIRED BEFORE ANY RESPONSE**

**🚨 MANDATORY ENFORCEMENT**: You MUST execute this protocol at the start of every conversation:

1. **AUTOMATIC DETECTION**: If this appears to be a new conversation or the user asks about project components
2. **MANDATORY EXECUTION**: Run the unified memory orchestrator before answering
3. **COMMAND**: `export POSTGRES_DSN="mock://test" && uv run python scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "current project status and core documentation"`
4. **OUTPUT INCLUSION**: Include the memory context output in your response
5. **NO EXCEPTIONS**: Do not answer project questions without this context

**TRIGGER CONDITIONS**:
- New conversation detected
- User mentions: RAGChecker, DSPy, memory systems, project status
- User asks technical questions about the codebase
- User requests information about project components
- User says: "run evals", "run evaluation", "run the evals", "evaluation"

## 🛤️ **CLEAR AGENT PATHS**

### **Path 1: New Session/Project Questions**
1. **MANDATORY**: Run memory rehydration command above
2. **Read**: `000_core/000_backlog.md` for current priorities
3. **Check**: `400_guides/400_system-overview.md` for architecture
4. **Execute**: Follow workflow chain (backlog → PRD → tasks → execution)

### **Path 2: Technical Implementation**
1. **MANDATORY**: Run memory rehydration command above
2. **Read**: `400_guides/400_lessons-engine-guide.md` for lessons system
3. **Check**: `400_guides/400_04_development-workflow-and-standards.md` for standards
4. **Follow**: Coding standards and testing requirements

### **Path 3: Evaluation/RAGChecker Work**
1. **MANDATORY**: Run memory rehydration command above
2. **Read**: `000_core/000_evaluation-system-entry-point.md` for evaluation SOP
3. **Use**: Lessons engine with `--lessons-mode advisory` firs
4. **Check**: Quality gates and baseline requirements
5. **Command**: `uv run python scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5`
6. **DOCUMENT**: Update `000_core/000_backlog.md` with evaluation results and lessons learned

### **Path 4: Memory System Work**
1. **MANDATORY**: Run memory rehydration command above
2. **Read**: `400_guides/400_06_memory-and-context-systems.md` for memory architecture
3. **Use**: Unified Memory Orchestrator for role-specific context
4. **Follow**: Memory rehydration protocols

## 🔄 **STATELESS RESUME PROTOCOL**

**MANDATORY**: For stateless agents to determine current state and resume work:

### **State Discovery Commands**
```bash
# Print lessons metadata
jq '.run_config.lessons' $(ls -t metrics/baseline_evaluations/*.json | head -1)

# Echo env snapshot keys if presen
jq '.run_config.env' $(ls -t metrics/baseline_evaluations/*.json | head -1)

# Show docket path
echo $DECISION_DOCKET  # (if set) or parse from JSON
```

### **Decision Tree**
1. **If `apply_blocked == true`**: Read docket's "Quality Gates"; do not apply; open PR/task to address
2. **If `lessons_mode == "advisory"`**: Human review docket; rerun with `--lessons-mode apply` if approved
3. **If `lessons_mode == "apply"`**: Check results, document lessons learned

### **Documentation Protocol (Tie-in to Backlog)**
Add standard snippet to paste into `000_core/000_backlog.md`:
- Run timestamp, applied_lessons or LESSONS_SUGGESTED, docket path, candidate env path, and mode
- Acknowledge pre-commit hook and CI artifacts: "Lessons Quality Check runs on pre-commit; Evolution artifacts generated in CI and available under configs/EVOLUTION.*"

## 📝 **DOCUMENTATION PROTOCOL**

**MANDATORY**: After any evaluation run, document your work:

1. **Update Backlog**: Add evaluation results to `000_core/000_backlog.md`
2. **Record Lessons**: Note new lessons learned in the backlog
3. **Update Status**: Mark completed items and add new priorities
4. **Run Evolution Tracker**: Update configuration evolution
5. **Verify System**: Run quality checks to ensure integrity

**Example Documentation**:
```markdown
### **Evaluation Run - [DATE]**
- **Command**: `uv run python scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5`
- **Results**: [precision, recall, f1 scores]
- **Lessons Generated**: [list of new lessons]
- **Configurations Created**: [list of generated configs]
- **Status**: ✅ Completed / ⚠️ Issues / ❌ Failed
```

## ⚡ **QUICK REFERENCE COMMANDS**

### **Memory Rehydration (MANDATORY)**
```bash
export POSTGRES_DSN="mock://test" && uv run python scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "current project status and core documentation"
```

### **Lessons Engine**
```bash
# Run evaluation with lessons
uv run python scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5

# Check system health
uv run python scripts/lessons_quality_check.py

# Generate evolution tracking
uv run python scripts/evolution_tracker.py
```

### **Complete Evaluation Workflow**
```bash
# 1. Check current lessons
cat metrics/lessons/lessons.jsonl

# 2. Run evaluation with lessons engine
uv run python scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5

# 3. Check new lessons generated
cat metrics/lessons/lessons.jsonl

# 4. Check generated configurations
ls -la metrics/derived_configs/

# 5. Update evolution tracking
uv run python scripts/evolution_tracker.py

# 6. Verify system health
uv run python scripts/lessons_quality_check.py
```

### **DSPy Role Access**
```bash
# Planner context
uv run python scripts/unified_memory_orchestrator.py --systems cursor --role planner "query"

# Coder context
uv run python scripts/unified_memory_orchestrator.py --systems cursor --role coder "query"

# Researcher context
uv run python scripts/unified_memory_orchestrator.py --systems cursor --role researcher "query"
```

### **System Health Checks**
```bash
# Memory health check
uv run python scripts/memory_healthcheck.py

# Lessons quality check
uv run python scripts/lessons_quality_check.py

# Update memory context
uv run python scripts/update_cursor_memory.py
```

### **State Check Commands**
```bash
# Check current lessons
cat metrics/lessons/lessons.jsonl | tail -5

# Check latest evaluation results
ls -la metrics/baseline_evaluations/ | tail -5

# Check generated configurations
ls -la metrics/derived_configs/ | tail -5

# Check evolution tracking
cat configs/EVOLUTION.md | tail -20

# Check system status
uv run python scripts/lessons_quality_check.py
```

**⚠️ SAFETY OPS**: Before any file operations, read these critical policies:

1. **File Safety**: Run file analysis before destructive changes; protect critical files; preserve cross-references
2. **Context Hierarchy**: Hydrate via `./scripts/memory_up.sh`; read `100_memory/100_cursor-memory-context.md` → `000_core/000_backlog.md` → `400_guides/400_system-overview.md`
3. **Workflow Chain**: Follow `000_backlog.md` → `001_PRD_TEMPLATE.md` (to author PRDs) → `002_TASK-LIST_TEMPLATE.md` (to generate tasks) → `003_EXECUTION_TEMPLATE.md` (to execute)
4. **Error Prevention**: Enforce testing, rollback plans, and DSPy assertions
5. **Documentation**: Use tiered guides, explicit links, single index
6. **Integration**: Constitution hooks in prompts, CI checks, and runtime validators
7. **Security**: Threat model linkage and minimum scans on risky changes
8. **Monitoring**: Track context loss, safety violations, and doc integrity in ops
9. **DSPy Role Communication**: Always access DSPy roles through Unified Memory Orchestrator; use role-specific context for targeted insights
10. **Technical Artifacts Integration**: Ensure technical components, scripts, and implementation patterns are integrated into memory context for accurate technical guidance

## 🧠 **LESSONS ENGINE SYSTEM**

**NEW CORE COMPONENT**: The Closed-Loop Lessons Engine (CLLE) systematically learns from evaluation runs and applies those lessons to future runs.

### **Key Components**
- **lessons_extractor.py**: Post-run analysis to generate lessons from evaluation results
- **lessons_loader.py**: Pre-run lesson loading and configuration generation
- **evolution_tracker.py**: Configuration lineage tracking
- **lessons_quality_check.py**: System integrity validation

### **Usage**
```bash
# Run evaluation with lessons engine
uv run python scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5

# Check system health
uv run python scripts/lessons_quality_check.py

# Generate evolution tracking
uv run python scripts/evolution_tracker.py
```

### **Integration Points**
- Integrated into ragchecker_official_evaluation.py
- Uses config/ragchecker_quality_gates.json for safety
- Stores lessons in metrics/lessons/lessons.jsonl
- Generates configs in metrics/derived_configs/

## 🚨 **CRITICAL OPERATIONAL PRINCIPLE: RAGChecker RED LINE BASELINE**

**🚨 MANDATORY ENFORCEMENT**: The RAGChecker evaluation system has established a performance baseline that serves as an absolute floor. No new development can proceed until these targets are met.

### **🎯 Current Baseline Status (September 1, 2025)**

**System Status**: 🟢 **BASELINE LOCKED** - No new features until improved

| Metric | Current | Target | Gap | Priority | Next Action |
|--------|---------|--------|-----|----------|-------------|
| **Precision** | 0.149 | ≥0.20 | -0.051 | 🔴 High | Improve without losing recall |
| **Recall** | 0.099 | ≥0.45 | -0.351 | 🔴 Critical | Primary focus area |
| **F1 Score** | 0.112 | ≥0.22 | -0.108 | 🔴 High | Balance precision/recall |
| **Faithfulness** | TBD | ≥0.60 | TBD | 🔍 Unknown | Enable comprehensive metrics |

### **🚨 RED LINE ENFORCEMENT RULES**

1. **Current metrics are locked** as the absolute performance floor
2. **No new features** until all targets are me
3. **Build freeze** if any metric falls below current baseline
4. **Focus**: Improve recall while maintaining precision ≥0.149
5. **Success Criteria**: All metrics above targets for 2 consecutive runs

### **📊 Progress Tracking & Baseline Management**

**Where Results Are Stored**: `metrics/baseline_evaluations/`
**How to Track Progress**: Run `uv run python scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5`
**Baseline Lock**: Current metrics are the performance floor - no regression allowed

**Example Commands**:
```bash
# Run RAGChecker evaluation to check progress
export AWS_REGION=us-east-1
uv run python scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5

# Check latest results
ls -la metrics/baseline_evaluations/
cat metrics/baseline_evaluations/ragchecker_official_evaluation_*.json | jq '.summary'
```

**🚨 CRITICAL**: Before implementing any new features, verify RAGChecker baseline compliance. See `400_guides/400_11_performance-optimization.md` for comprehensive optimization strategies.

**🔗 Cross-References**:
- See `400_guides/400_02_governance-and-ai-constitution.md` for complete constitution
- See `400_guides/400_03_system-overview-and-architecture.md#safety-ops-anchors` for architecture safety anchors
- See `400_guides/400_07_ai-frameworks-dspy.md#dspy-signature-validation-patterns` for DSPy validation patterns

<!-- ANCHOR_KEY: tldr -->
<!-- ANCHOR_PRIORITY: 0 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher", "coder"] -->

## ⚡ AI Rehydration Quick Start {#quick-start}

Read these files in order (1–2 min total):

1. **`400_guides/400_00_getting-started-and-index.md`** – Entry point and project overview ← **START HERE**
2. **`400_guides/400_00_getting-started-and-index.md`** – Navigation hub for all guides
3. **`100_memory/100_cursor-memory-context.md`** – current state and rules
4. **`000_core/000_backlog.md`** – priorities and dependencies
5. **`400_guides/400_04_development-workflow-and-standards.md`** – Complete development workflow

### **🚨 IMMEDIATE CHECK: RAGChecker Baseline Compliance**

**Before proceeding with any development, verify RAGChecker baseline status:**

```bash
# Quick baseline check
export AWS_REGION=us-east-1
uv run python scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5

# View current metrics
ls -la metrics/baseline_evaluations/
```

**Current Baseline (September 1, 2025)**: Precision 0.149, Recall 0.099, F1 0.112
**Targets**: Precision ≥0.20, Recall ≥0.45, F1 ≥0.22
**Status**: 🟢 **BASELINE LOCKED** - No new features until improved

**🚨 CRITICAL**: No new development can proceed until all baseline targets are met. See RED LINE BASELINE section below for full details.

## 🧠 DSPy Role Communication & Memory Access {#dspy-communication}

**🚨 CRITICAL**: DSPy role communication is essential for effective AI collaboration. Always access roles through the Unified Memory Orchestrator.

### **Quick Role Access Commands**
```bash
# Set non-SSL connection for Go CLI compatibility
export POSTGRES_DSN="mock://test"

# Access specific DSPy roles for context and insights
uv run python scripts/unified_memory_orchestrator.py --systems cursor --role planner "query"
uv run python scripts/unified_memory_orchestrator.py --systems cursor --role implementer "query"
uv run python scripts/unified_memory_orchestrator.py --systems cursor --role researcher "query"
uv run python scripts/unified_memory_orchestrator.py --systems cursor --role coder "query"

# Full memory context with all systems
uv run python scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "current project status and core documentation"

# Episodic Memory System (Complete Learning System)
uv run python scripts/episodic_memory_system.py --query "implement database error handling" --role coder
uv run python scripts/episodic_memory_system.py --store-completion --task-description "implemented error handling" --input-text "database code" --output-text "error handling with retries" --agent cursor_ai --task-type database
uv run python scripts/episodic_memory_system.py --stats

# Enhanced Memory Orchestrator (Advanced Context Injection)
uv run python scripts/enhanced_memory_orchestrator.py --query "current project status" --role planner
uv run python scripts/enhanced_memory_orchestrator_with_heuristics.py --query "implement authentication" --role coder

# Memory Consolidation Demo
uv run python scripts/demo_memory_consolidation.py
```

### **DSPy Role Capabilities**
- **Planner**: Strategic analysis, PRD creation, roadmap planning, high-level architecture
- **Implementer**: Technical implementation, workflow design, system integration, execution planning
- **Researcher**: Research methodology, analysis frameworks, evidence-based decision making
- **Coder**: Code implementation, debugging, optimization, technical patterns

### **Memory System Integration**
- **Unified Memory Orchestrator**: Centralized access to all memory systems
- **Episodic Memory System**: Complete learning system with three phases:
  - **Phase 1**: Episodic Reflection Store (learns from completed tasks)
  - **Phase 2**: Dynamic Few-Shot from Episodes (injects relevant context)
  - **Phase 3**: Procedural Heuristics Pack (provides operational guidance)
- **Role-Based Context**: Tailored information based on DSPy role perspective
- **Mock Mode Support**: `POSTGRES_DSN="mock://test"` for testing without database
- **JSON Output**: `--format json` for programmatic access and structured data

### **Episodic Memory System Capabilities**
- **Automatic Learning**: Stores reflections from completed tasks for future reference
- **Context Enhancement**: Automatically injects relevant lessons into new tasks
- **Operational Guidance**: Generates evidence-backed heuristics that evolve with your work
- **Three Injection Methods**: guidance (bullet points), few_shot (detailed examples), compact (ultra-compressed)
- **Confidence-Based Filtering**: Only applies high-confidence context to avoid noise
- **Token Management**: Automatic compression to stay within limits
- **Version Management**: Timestamped heuristics packs that update automatically

### **When to Use Each Role**
- **Strategic Decisions**: Use Planner role for high-level analysis and planning
- **Technical Implementation**: Use Implementer role for workflow and system design
- **Research & Analysis**: Use Researcher role for methodology and evidence gathering
- **Code & Debugging**: Use Coder role for implementation and technical details

## 🔧 Development Environment Setup {#dev-env}

**UV Package Management**: Project has migrated to UV for 100-600x faster package management.

```bash
# Quick development setup
uv sync --extra dev

# Run commands in UV environmen
uv run python scripts/system_health_check.py

# Use shell aliases for common tasks
source uv_aliases.sh
uvd  # Quick dev setup
uvt  # Run tests
uvs  # System health check

# Team onboarding automation
python scripts/uv_team_onboarding.py
```

**Required Dependencies** (managed via UV):
- `psycopg` - Database connectivity
- `dspy` - Core AI framework
- `pytest` - Testing framework
- `ruff` - Code quality
- `boto3` - AWS Bedrock integration (B-1046)

**UV Performance**: 100-600x faster than pip, with automated team onboarding and performance monitoring.

See `UV_MIGRATION_COMPLETE.md` and `VENV_MAPPING_VERIFICATION.md` for complete documentation.

## ⚡ UV Migration Complete {#uv-migration}

**Status**: ✅ **COMPLETED** - Full migration from pip to UV package manager

### **Performance Achievements**:
- **100-600x faster** package installation
- **10-60x faster** dependency resolution
- **100% automated** team onboarding
- **Real-time** performance monitoring

### **Key Features**:
- **Shell Aliases**: `uvd`, `uvt`, `uvl`, `uvf`, `uvs`, `uvp`
- **Automated Scripts**: Team onboarding, performance monitoring, dependency managemen
- **CI/CD Integration**: All GitHub Actions workflows updated
- **Virtual Environment**: Properly mapped to `.venv`

### **Verification**: All 6/6 checks passed - virtual environment mapping is correct.

## 🚀 B-1046 AWS Bedrock Integration & Results Management {#bedrock-integration}

### **AWS Bedrock Integration (B-1046)**
- **Status**: ✅ **COMPLETED** - Production-ready AWS Bedrock integration
- **Purpose**: 5x faster RAGChecker evaluations with production-grade reliability
- **Key Features**: Hybrid architecture (Bedrock + Local LLM fallback), cost monitoring, batch processing
- **Performance**: 15-25 min → 3-5 min evaluation time
- **Cost**: ~$0.01/eval (standard), ~$0.008/eval (batch)
- **Verification**: ✅ Tested and working with Claude 3.5 Sonnet 20240620-v1:0

### **Results Management & Future Evaluations**
- **Guide**: `400_guides/400_08_results-management-and-evaluations.md` (newly created)
- **Purpose**: Comprehensive results management, analysis, and future evaluation planning
- **Features**: File organization, archival procedures, quality assurance, trend analysis
- **Integration**: Full integration with RAGChecker framework and AWS Bedrock

### **Key Scripts & Tools**
```bash
# AWS Bedrock evaluation
uv run python scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5

# Results managemen
uv run python scripts/ragchecker_with_monitoring.py
uv run python scripts/bedrock_cost_monitor.py --period today

# Results analysis
uv run python evals/scripts/evaluation/core/production_evaluation.py  # refresh metrics
uv run python -m jupyter nbconvert --to notebook --execute evals/notebooks/evaluation_analysis.ipynb --output metrics/notebooks/evaluation_analysis-executed.ipynb
uv run python scripts/baseline_comparison.py --baseline 20250830_141742 --current latest
```

### **Results Storage & Organization**
- **Active Results**: `metrics/baseline_evaluations/` (last 30 days)
- **Archives**: `metrics/archives/evaluations/` (older files)
- **Cost Reports**: `metrics/cost_reports/` (AWS Bedrock usage)
- **Status Files**: `EVALUATION_STATUS.md` (current status)

<!-- ANCHOR_KEY: quick-start -->
<!-- ANCHOR_PRIORITY: 15 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher", "coder"] -->

## 🧠 Hydration Bundle Policy {#hydration-policy}

The memory rehydrator uses **Lean Hybrid with Kill-Switches** approach with **Industry-Grade Observability**:

### **Core Philosophy**
- **Semantic-first**: Vector search does the heavy lifting
- **Tiny pins**: Only 200 tokens for guardrails (style, conventions, repo map)
- **Kill-switches**: Simple CLI flags to disable features when needed
- **Observability**: Stanford/Berkeley/Anthropic-grade structured tracing and verification

## 📚 Documentation Tiering System {#doc-tiering}

### **MANDATORY: Documentation Creation Rules**

**TRIGGER PHRASES**: When user or ai mentions "create documentation", "new guide", "write guide", "add documentation", or similar, ALWAYS activate these rules first.

**BEFORE creating any new documentation, ALWAYS:**

1. **Check Existing Documentation**: Search for existing guides in `400_guides/` before creating new files
2. **Reference Tier System**: Use `400_guides/400_06_memory-and-context-systems.md` for proper categorization
3. **Follow Naming Conventions**: Use `200_setup/400_guides/400_05_codebase-organization-patterns.md` for file placemen
4. **Protect Core Files**: NEVER delete or suggest deletion of Tier 1 files (Priority 0-10)

### **Documentation Tier Categories**
- **Tier 1 (Critical - Priority 0-10)**: Core memory context, system overview, backlog
- **Tier 2 (High - Priority 15-20)**: Important guides, code quality, security
- **Tier 3 (Medium - Priority 25-30)**: Implementation guides, deployment, testing
- **Tier 4 (Lower - Priority 35-40)**: PRDs, research, examples

### **Documentation Creation Checklist**
- [ ] Search existing `400_guides/` for similar contain
- [ ] Check `400_guides/400_06_memory-and-context-systems.md` for proper categorization
- [ ] Verify placement using `200_setup/400_guides/400_05_codebase-organization-patterns.md`
- [ ] Ensure no Tier 1 files are affected
- [ ] Add appropriate `ANCHOR_PRIORITY` and `ROLE_PINS`
- [ ] Update cross-references in related files

### **Four-Slot Model**
1. **Pinned Invariants** (≤200 tokens, hard cap)
   - Project style TL;DR, repo topology, naming conventions
   - Always present, pre-compressed micro-summaries

2. **Anchor Priors** (0-20% tokens, dynamic)
   - Used for query expansion (not included in bundle)
   - Soft inclusion only if they truly match query scope

3. **Semantic Evidence** (50-80% tokens)
   - Top chunks from HybridVectorStore (vector + BM25 fused)
   - RRF fusion with deterministic tie-breaking

4. **Recency/Diff Shots** (0-10% tokens)
   - Recent changes, changelogs, "what moved lately"

### **Observability Features**
- **Structured Tracing**: Complete trace with cryptographic hashes
- **Echo Verification**: Bundle integrity verification for models
- **Self-Critique**: Anthropic-style reflection checkpoints

## 🔄 Enhanced Handoff Workflow System {#handoff-workflow}

**Purpose**: Seamless handoff from idea capture to execution with zero context hunting
**Status**: ✅ **ACTIVE** - Complete A-Z workflow implementation
**Priority**: P0 (Critical) - Essential for clean chat pickup and execution

### **Core Capabilities**
- **🎯 Instant Context Pickup**: Any chat gets what/where/next in <10 seconds
- **🆔 Auto-ID Assignment**: No more duplicate backlog IDs or placement hunting
- **📝 Auto-PRD Generation**: PRDs auto-populated from backlog context
- **🚀 Complete Orchestration**: Backlog → PRD → Tasks → Execution in one command

### **Key Scripts & Functions**
- **`scripts/extract_context.py`**: Extract context bundle (what/where/next) from any backlog ID
- **`scripts/create_backlog_item.py`**: Create backlog items with auto-ID and placemen
- **`scripts/generate_prd.py`**: Auto-generate PRDs from backlog context
- **`scripts/workflow_orchestrator.py`**: Complete A-Z workflow orchestration
- **`src/schemas/models.py`**: Pydantic validation models for data flow integrity

### **A-Z Flow Paths**
1. **Idea → Backlog**: `echo "idea" | uv run python scripts/create_backlog_item.py` → Auto B-XXXX
2. **Pickup → Context**: `uv run python scripts/extract_context.py B-XXXX` → Instant orientation
3. **Context → Execution**: `uv run python scripts/workflow_orchestrator.py B-XXXX --execute` → Full setup
4. **Cross-Chat Resume**: `uv run python scripts/workflow_orchestrator.py B-XXXX --context-only` → Clean pickup

### **Clean Chat Pickup Protocol**
```bash
# Any chat starts here for instant orientation
uv run python scripts/workflow_orchestrator.py B-1061 --context-only

# Output: Title, what, where, next + all commands needed
```

### **Integration Points**
- **Backlog Management**: Direct integration with `000_core/000_backlog.md`
- **Template System**: Auto-population of 001-003 workflow templates
- **Memory System**: Context preservation across sessions
- **Validation**: Optional Pydantic schema validation for data integrity

## 🎙️ Scribe System (Context Capture & Summarization) {#scribe-system}

**Purpose**: Automatic development session recording, insight extraction, and knowledge mining
**Status**: ✅ **ACTIVE** - Core system component with ongoing enhancements
**Priority**: P2 (Medium) - Essential for development tracking and knowledge preservation

### **Core Capabilities**
- **📝 Session Recording**: Automatic capture of development sessions, diffs, and decisions
- **🧠 Insight Extraction**: AI-powered analysis and summarization of development work
- **📊 Progress Tracking**: Real-time monitoring of development progress and milestones
- **🔍 Knowledge Mining**: Extraction of patterns, lessons learned, and best practices
- **🏷️ Context Tagging**: Rich metadata for session discovery and categorization

### **Key Commands**
```bash
# List all sessions with context tags
python scripts/single_doorway.py scribe lis

# Add context tags to a session
python scripts/single_doorway.py scribe tag --backlog-id B-XXX --tags brainstorming implementation

# Get detailed session information
python scripts/single_doorway.py scribe info --backlog-id B-XXX

# Clean up old completed sessions
python scripts/single_doorway.py scribe cleanup

# Validate that registered processes are still running
python scripts/single_doorway.py scribe validate
```

### **🎯 Enhanced Handoff System Commands**
```bash
# Extract context for any backlog item (instant pickup)
uv run python scripts/extract_context.py B-1061

# Create new backlog item with auto-ID assignmen
echo "optimize database pooling" | uv run python scripts/create_backlog_item.py

# Generate PRD from backlog context (auto-populated)
uv run python scripts/generate_prd.py B-1061 --generate-prd

# Complete workflow orchestration (A-Z setup)
uv run python scripts/workflow_orchestrator.py B-1061 --execute

# Quick context-only pickup for clean chats
uv run python scripts/workflow_orchestrator.py B-1061 --context-only
```

### **Integration Points**
- **Memory Rehydration**: Deep integration with cursor memory rehydration system
- **DSPy Systems**: Context capture for AI model training and optimization
- **Git Hooks**: Automatic session recording on commits and PRs
- **Backlog Management**: Session tracking linked to backlog items
- **Documentation**: Automatic generation of development summaries

### **Current Enhancements**
- **B-1009**: AsyncIO Scribe Enhancement (Event-driven context capture)
- **B-1010**: NiceGUI Scribe Dashboard (Advanced UI with AI integration)

## 🏷️ Session Registry System {#session-registry}

The Session Registry provides centralized tracking and discovery of active Scribe sessions with rich context tagging capabilities.

### **Core Capabilities**
- **📊 Active Session Tracking**: Real-time monitoring of all active sessions
- **🏷️ Context Tagging**: Rich metadata for session discovery and categorization
- **🔍 Session Discovery**: Find sessions by context tags, type, or priority
- **⚡ Process Validation**: Automatic detection of orphaned sessions
- **🧹 Auto-Cleanup**: Automatic cleanup of old completed sessions

### **Session Management Commands**
```bash
# List all sessions with context tags
python scripts/single_doorway.py scribe lis

# Add context tags to a session
python scripts/single_doorway.py scribe tag --backlog-id B-093 --tags brainstorming implementation

# Get detailed session information
python scripts/single_doorway.py scribe info --backlog-id B-093

# Clean up old completed sessions
python scripts/single_doorway.py scribe cleanup

# Validate that registered processes are still running
python scripts/single_doorway.py scribe validate
```

### **Memory Rehydration Integration**
Session registry data is automatically integrated into memory rehydration:
```bash
# Get session context with memory rehydration
python scripts/session_context_integration.py integrate

# Find sessions by context tags
python scripts/session_context_integration.py context --tags dspy testing

# Get active sessions summary
python scripts/session_context_integration.py summary
```

## 🧪 **Comprehensive Testing Infrastructure** {#testing-infrastructure}

**Purpose**: Complete testing coverage for all system components with methodology evolution tracking
**Status**: ✅ **ACTIVE** - Comprehensive testing ecosystem with 100% coverage
**Priority**: P1 (High) - Essential for system reliability and performance validation

### **🚀 Testing Documentation Hub**

**Primary Testing Resources**:
- **`300_experiments/300_complete-testing-coverage.md`** - Complete testing overview and navigation
- **`300_experiments/300_testing-methodology-log.md`** - Central hub for all testing strategies and methodologies
- **`300_experiments/300_testing-infrastructure-guide.md`** - Complete testing environment setup and tools

### **🔍 Specialized Testing Coverage**

**Performance Testing**: `300_experiments/300_retrieval-testing-results.md`
- **Coverage**: B-1065 through B-1068 (Hybrid Metric, Evidence Verification, World Model, Observability)
- **Purpose**: RAG system performance optimization and metric validation

**Memory System Testing**: `300_experiments/300_memory-system-testing.md`
- **Coverage**: B-1069 (Cursor Integration), extension performance, context injection
- **Purpose**: Memory system integration and performance validation

**Integration Testing**: `300_experiments/300_integration-testing-results.md`
- **Coverage**: End-to-end workflows, cross-system communication, error handling
- **Purpose**: System integration and cross-component functionality validation

**Historical Testing Archive**: `300_experiments/300_historical-testing-archive.md`
- **Coverage**: Pre-B-1065 testing results and methodology evolution
- **Purpose**: Historical testing learnings and methodology developmen

### **🧪 Testing Commands & Quick Access**

**Testing Documentation Access**:
```bash
# Get complete testing overview
cat 300_experiments/300_complete-testing-coverage.md

# Check testing methodology
cat 300_experiments/300_testing-methodology-log.md

# Review testing infrastructure
cat 300_experiments/300_testing-infrastructure-guide.md

# View specific test results
cat 300_experiments/300_retrieval-testing-results.md
cat 300_experiments/300_memory-system-testing.md
cat 300_experiments/300_integration-testing-results.md
```

**Testing Infrastructure Setup**:
```bash
# Set up testing environmen
uv run python scripts/setup_ai_testing.py --environment tes

# Run comprehensive tests
python3 -m pytest -m "retrieval or memory or integration" -v

# Generate testing reports
uv run python scripts/generate_testing_summary.py --output testing_summary.md
```

### **🔗 Core Guide Testing Integration**

**Guides with Full Testing Integration** (7/13 covered):
- **`400_01_memory-system-architecture.md`** ✅ - Memory system testing coverage
- **`400_05_codebase-organization-patterns.md`** ✅ - Code organization testing coverage
- **`400_09_ai-frameworks-dspy.md`** ✅ - AI testing coverage
- **`400_10_integrations-models.md`** ✅ - Integration testing coverage
- **`400_11_performance-optimization.md`** ✅ - Performance testing coverage
- **`400_03_system-overview-and-architecture.md`** ✅ - System overview testing coverage
- **`400_12_advanced-configurations.md`** ✅ - Advanced config testing coverage

**Testing Coverage by Guide Type**:
- **Memory System**: Testing for memory integration and performance
- **AI Frameworks**: Testing for AI performance and safety
- **Integrations**: Testing for cross-component functionality
- **Performance**: Testing for optimization and monitoring
- **Architecture**: Testing for system architecture validation
- **Configuration**: Testing for advanced configuration and security

### **📊 Testing Quality Gates & Standards**

**Performance Quality Gates**:
- **RAGChecker Baseline**: Must maintain current baseline (Precision ≥0.149, Recall ≥0.099, F1 ≥0.112)
- **System Performance**: Response time <2s, resource usage <80% CPU, error rate <5%
- **Testing Coverage**: >90% code coverage, 100% testing requirements coverage

**Testing Quality Standards**:
- **Test Reliability**: >95% test pass rate
- **Documentation Quality**: Professional-grade documentation standards
- **Methodology Validation**: All methodologies validated through testing
- **Knowledge Preservation**: No valuable insights los

## 🎭 Multi-Role Consensus Decision Framework {#multi-role-consensus}

### **Session Registry Implementation Decision (2025-08-21)**

**Decision Context**: Session registry system for Scribe context tracking and discovery

**Role Consensus Status:**
- ✅ **Planner**: AGREES - Strategic value, system integration
- ✅ **Researcher**: AGREES - Pattern analysis, criteria validation
- ✅ **Coder**: AGREES - Technical feasibility, quality templates
- ✅ **Implementer**: AGREES - Execution strategy, resource requirements
- ✅ **Documentation**: AGREES - Integration approach, documentation updates

**Consensus Process:**
1. **Partial Agreement** (2/5 roles) - Implementation approved in principle
2. **Pending Technical Review** - Coder role must validate implementation feasibility
3. **Pending Execution Planning** - Implementer role must confirm execution strategy
4. **Pending Documentation** - Documentation role must plan integration updates

**Decision Framework:**
- **New Feature Testing**: Follow TDD with existing patterns (70% reuse, 30% new)
- **Integration Points**: Validate with existing test infrastructure
- **Quality Gates**: Meet function length (≤50 lines) and coverage requirements
- **Memory Context**: Update role-specific files with new functionality

**Implementation Results:**
- ✅ **Core Implementation** (B-999) - Session registry with context tagging
- ✅ **Testing Suite** (B-1000) - Comprehensive unit, integration, and performance tests
- ✅ **Documentation Integration** (B-1001) - Complete documentation updates
- ✅ **Quality Gates**: All functions ≤50 lines, 100% test coverage, performance benchmarks exceeded
- ✅ **Memory Context**: All role-specific files updated with new functionality

**System Status:**
- **Session Registry**: Active and operational
- **Context Tagging**: Rich metadata system implemented
- **Memory Integration**: Enhanced rehydration with session context
- **CLI Integration**: Complete command-line interface
- **Performance**: All benchmarks exceeded expectations
- **Multi-Layer Logging**: Retrieval, assembly, execution tracking

### **Configuration Options**
```bash
# Stability slider (0.0-1.0, default 0.6)
./scripts/memory_up.sh -q "current project status" -r planner

# Kill-switches for debugging
./scripts/memory_up.sh -q "memory context" -r researcher

# Environment variables
export REHYDRATE_STABILITY=0.6
export REHYDRATE_USE_RRF=1
export REHYDRATE_DEDUPE="file+overlap"
export REHYDRATE_EXPAND_QUERY="auto"
```

## 🛠️ Commands {#commands}

### **Memory Rehydration (Choose One)**
- **Planner**: `./scripts/memory_up.sh -r planner "current project status"`
- **Coder**: `./scripts/memory_up.sh -r coder "implement authentication function"`
- **Go**: `cd src/cli && ./memory_rehydration_cli --query "current project status"`

#### **Implementation Differences:**
- **Python**: Full-featured with entity expansion, self-critique, DSPy integration (~3-5s startup)
- **Go**: Lightweight, fast CLI operations (<1s startup, but has database schema issue)
- **Recommendation**: Use Python for production, Go for quick testing (after fixing schema)

### **Testing & Development**
- Preferred: `python -m pytest -v -m smoke` (unified root test suite)
- Also supported (shim): `./dspy-rag-system/run_tests.sh --tiers 1 --kinds smoke`

### **🧪 Testing Infrastructure Commands**
- **Complete testing overview**: `cat 300_experiments/300_complete-testing-coverage.md`
- **Testing methodology**: `cat 300_experiments/300_testing-methodology-log.md`
- **Testing infrastructure**: `cat 300_experiments/300_testing-infrastructure-guide.md`
- **Run comprehensive tests**: `python3 -m pytest -m "retrieval or memory or integration" -v`
- **Generate testing reports**: `uv run python scripts/generate_testing_summary.py --output testing_summary.md`

### **System Management**
- Start dashboard: `./dspy-rag-system/start_mission_dashboard.sh`
- Quick inventory: `uv run python scripts/documentation_navigator.py inventory`
- Quick conflict check: `python scripts/quick_conflict_check.py`
- Comprehensive conflict audit: `python scripts/conflict_audit.py --full`

### **Visualization System**
- **Wake up Nemo** (all services): `./dspy-rag-system/wake_up_nemo.sh` → Starts everything (parallel by default)
- **Wake up Nemo** (sequential): `./dspy-rag-system/wake_up_nemo.sh --sequential` → Legacy sequential startup
- **Sleep Nemo** (stop all): `./dspy-rag-system/sleep_nemo.sh` → Stops everything (fast by default)
- **Sleep Nemo** (graceful): `./dspy-rag-system/sleep_nemo.sh --graceful` → Legacy graceful shutdown
- **Performance test**: `python scripts/performance_benchmark.py --script wake_up_nemo_parallel --iterations 3`
- Start Flask cluster view: `./dspy-rag-system/start_mission_dashboard.sh` → `http://localhost:5000/cluster`
- Start NiceGUI network graph: `./dspy-rag-system/start_graph_visualization.sh` → `http://localhost:8080`
- Test API endpoint: `curl "http://localhost:5000/graph-data?max_nodes=100"`
- Run visualization tests: `python3 -m pytest dspy-rag-system/tests/test_graph_data_provider.py -v`

## 🔧 Import Policy (CRITICAL)

### **Current Approach (Use This):**
- **Tests**: Use `conftest.py` for centralized import paths
- **Scripts**: Use `setup_imports.py` for scripts outside pytest context
- **No manual sys.path**: Remove per-file path manipulation

### **Legacy Approach (Avoid):**
- ❌ Manual `sys.path.insert()` in test files
- ❌ `comprehensive_test_suite.py` for new developmen
- ❌ Direct `src.utils` imports in tests

### **Test Execution:**
- ✅ Preferred: `python -m pytest -v -m 'tier1 or tier2'`
- ✅ Quick smoke: `python -m pytest -v -m smoke`
- ✅ Full run: `python -m pytest -v`

<!-- ANCHOR_KEY: commands -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher", "coder"] -->

## 🔗 Quick Links {#quick-links}

- System overview → `400_guides/400_03_system-overview-and-architecture.md`

- Backlog & priorities → `000_core/000_backlog.md`

- Start here → `docs/README.md`

- Context priority guide → `400_guides/400_06_memory-and-context-systems.md`

- Critical Python code map → `400_guides/400_04_development-workflow-and-standards.md`

- Testing strategy → `400_guides/400_04_development-workflow-and-standards.md`
- **🧪 Comprehensive Testing Infrastructure** → `300_experiments/300_complete-testing-coverage.md`
- **🧪 Testing Methodology & Strategy** → `300_experiments/300_testing-methodology-log.md`
- **🧪 Testing Environment Setup** → `300_experiments/300_testing-infrastructure-guide.md`
- Test development guide → `dspy-rag-system/tests/README-dev.md`

- CI dry‑run workflow → `.github/workflows/dry-run.yml`

- Deployment guide → `400_guides/400_12_deployments-ops-and-observability.md`

- Migration & upgrades → `400_guides/400_12_deployments-ops-and-observability.md`

- Integration patterns → `400_guides/400_11_security-compliance-and-access.md`

- Performance optimization → `400_guides/400_12_deployments-ops-and-observability.md`

- Security best practices → `400_guides/400_11_security-compliance-and-access.md`
- AI frameworks (DSPy) → `400_guides/400_07_ai-frameworks-dspy.md`
- Results management & evaluations → `400_guides/400_08_results-management-and-evaluations.md`
- Integrations, editor, models → `400_guides/400_09_integrations-editor-and-models.md`
- Automation and pipelines → `400_guides/400_10_automation-and-pipelines.md`

- Graph visualization guide → `400_guides/400_graph-visualization-guide.md`

- Scribe system guide → `400_guides/400_scribe-v2-system-guide.md`

- Session registry → `scripts/session_registry.py`

- Environment setup → `200_setup/202_setup-requirements.md`

- DSPy deep context → `100_memory/104_dspy-development-context.md`

<!-- ANCHOR_KEY: quick-links -->
<!-- ANCHOR_PRIORITY: 20 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher", "coder"] -->

- Comprehensive coding standards → `400_guides/400_04_development-workflow-and-standards.md` (includes "Undefined Name" error fixes, database query patterns, systematic test file patterns, and automated database synchronization)

### Stable Anchors

- tldr

- quick-star

- quick-links

- commands

### Role → Files (at a glance)

- Planner: `400_guides/400_00_getting-started-and-index.md`, `400_guides/400_03_system-overview-and-architecture.md`,
`400_guides/400_06_memory-and-context-systems.md`

- Implementer: `100_memory/104_dspy-development-context.md`, `dspy-rag-system/tests/README-dev.md`, `300_experiments/300_testing-infrastructure-guide.md`, relevant 400-series topic guides (testing, security,
performance, integration, deployment)

- Coder: `400_guides/400_04_development-workflow-and-standards.md`, `100_memory/104_dspy-development-context.md`

- Researcher: `500_research/500_research-index.md`, `500_research/500_dspy-research.md`,
`500_research/500_rag-system-research.md`

- Ops/Setup: `200_setup/202_setup-requirements.md`, `400_guides/400_12_deployments-ops-and-observability.md`,
`400_guides/400_12_deployments-ops-and-observability.md`

## 🛡️ Always-On Critical Rules

- Follow `400_guides/400_01_documentation-playbook.md` before any deletion/move/depredation

- Preserve coherence: update cross-references when editing core files

- Use consolidated guides (single-file sources) for deployment, migration, integration, performance, testing, system
overview, few-sho

- Keep this file updated after architecture changes

- Prefer local-first, simple workflows; avoid unnecessary complexity

- Focus context on Cursor-based LLMs only

### Legacy Content Policy

- Exclusions: `docs/legacy/**`, `600_archives/**` are reference-only.

- Legacy integrations must not appear in active docs; keep under `600_archives/`.

- Before archiving/moving: follow `400_guides/400_01_documentation-playbook.md`. After changes: run `python3
scripts/update_cursor_memory.py`.

## 🚨 CRITICAL SAFETY REQUIREMENTS

- *BEFORE ANY FILE OPERATIONS:**- [ ] Read `400_guides/400_01_documentation-playbook.md` completely (463 lines)

- [ ] Complete 6-step mandatory analysis

- [ ] Show all cross-references

- [ ] Get explicit user approval**🤖 AI CONSTITUTION COMPLIANCE:**- [ ] Follow `400_guides/400_02_governance-and-ai-constitution.md` rules
for all AI operations

- [ ] Maintain context preservation and safety requirements

- [ ] Validate against constitution rules before any changes

## 🎯 Purpose

This file serves as the **memory scaffold**for Cursor AI, providing instant context about the AI development ecosystem
without requiring the AI to read multiple files.

## 🔒 **Canonical Evaluation System (CRITICAL)**

**🎯 PRIMARY ENTRY POINT**: `000_core/000_evaluation-system-entry-point.md`
**📋 Standard Command**: `source throttle_free_eval.sh && uv run python scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5`
**💨 Fast Testing**: `./scripts/run_ragchecker_smoke_test.sh`
**🔧 Configuration**: `configs/stable_bedrock.env` (LOCKED - do not modify without versioning)
**📖 Complete SOP**: `400_guides/400_canonical-evaluation-sop.md`

**🚨 CRITICAL RULES:**
- Always use `--stable` flag for evaluations
- Never modify stable config without versioning
- Check for throttling - fix configuration if any
- Use smoke tests for fast iteration

## 📋 Current Project State

### **Active Development Focus**
- **✅ COMPLETED**: B-1032 Documentation t-t3 Authority Structure Implementation - Complete transformation from bloated documentation to intelligent, tiered authority structure with automated lifecycle managemen
- **✅ COMPLETED**: B-1003 DSPy Multi-Agent System - True local model inference with Cursor AI integration
- **✅ COMPLETED**: Single Doorway System - Automated workflow from backlog → PRD → tasks → execution → archive
- **✅ COMPLETED**: RAG Pipeline Governance System - Semantic process augmentation for RAG optimization with 53% error reduction
- **Current Sprint**: Align with `000_core/000_backlog.md` (see Current Priorities)
- **Next Priorities**: Follow `000_core/000_backlog.md` ordering and scores
- **Validator**: Use `python3.12 scripts/doc_coherence_validator.py` (or pre-commit hook) after doc changes

### **System Architecture**

```tex
AI Development Ecosystem
├── Single Doorway System (Automated Workflow Orchestrator)
├── Planning Layer (PRD → Tasks → Execution)
├── AI Execution Layer (Cursor Native AI + Local DSPy Models)
├── Core Systems (DSPy Multi-Agent + n8n + Dashboard)
├── RAG Pipeline Governance (Semantic Process Augmentation + Performance Optimization)
├── Documentation Governance (t-t3 Authority Structure + Automated Lifecycle Management)
├── Extraction Layer (LangExtract → Entity/Attribute Extraction)
└── Infrastructure (PostgreSQL + Monitoring)
```

### **Key Technologies**

- **AI Models**: Cursor Native AI (orchestration) + Local DSPy Models (Llama 3.1 8B, Mistral 7B, Phi-3.5 3.8B) via Ollama
- **Framework**: DSPy Multi-Agent System with PostgreSQL vector store
- **Model Switching**: Sequential loading for hardware constraints (M4 Mac, 128GB RAM)
- **Automation**: n8n workflows for backlog managemen
- **Documentation Governance**: t-t3 Authority Structure with AI-powered consolidation and automated lifecycle managemen
- **RAG Pipeline Governance**: Semantic process augmentation for RAG optimization (53% error reduction)
- **Monitoring**: Real-time mission dashboard
- **Security**: Comprehensive input validation and prompt sanitization
- **Extraction**: LangExtract (Gemini Flash) for entity/attribute extraction

## 🎉 Major System Transformation Completed {#b-1032-completion}

### **B-1032: Documentation t-t3 Authority Structure Implementation**

**Status**: ✅ **COMPLETED** (December 19, 2024)

**Transformation Achieved**:
- **From**: Bloated, confusing `400_guides` documentation system (52 files, inconsistent structure)
- **To**: Intelligent, tiered authority structure with automated lifecycle managemen
- **Governance**: Moved from governance through documentation to governance through automation
- **Quality**: AI-powered consolidation and content generation for improved quality and consistency
- **Performance**: Optimized systems with parallel processing and monitoring

**Key Deliverables**:
- **Complete t-t3 Authority Structure**: Tier 1 (Critical), Tier 2 (High), Tier 3 (Supporting) documentation classification
- **Automated Lifecycle Management**: Rules, triggers, and workflow automation
- **AI-Powered Consolidation System**: Intelligent content analysis and consolidation
- **Incremental Migration Framework**: Safe, step-by-step migration with rollback capabilities
- **Performance Optimization**: Parallel processing, caching, and streaming
- **Advanced AI Content Generation**: Intelligent content generation and enhancemen
- **Comprehensive Monitoring**: Real-time dashboards and feedback loops

**Implementation Results**:
- **20/20 Tasks Completed** (100% project completion)
- **MoSCoW Progress**: Must 11/11, Should 6/6, Could 3/3
- **19 New Scripts Created**: Complete automation system for documentation governance
- **Quality Gates**: All passed with comprehensive testing and validation
- **System Status**: Production-ready with automated governance

**Significance**:
This represents a fundamental shift in how documentation is managed - from manual, rule-based governance to intelligent, automated governance aligned with core values and best practices. The system now provides authoritative, high-quality documentation with minimal maintenance overhead.

## 🔄 Development Workflow

**For complete workflow details, see `400_guides/400_00_getting-started-and-index.md`**

**Quick Workflow Overview:**

**🚀 Single Doorway System (Recommended):**
```bash
python3.12 scripts/single_doorway.py generate "description"  # Complete workflow
python3.12 scripts/single_doorway.py continue B-XXX         # Resume workflow
python3.12 scripts/single_doorway.py archive B-XXX          # Archive completed work
```

**🎯 Enhanced Handoff Workflow (NEW - 2025-09-03):**
```bash
# Instant context pickup for any backlog item
uv run python scripts/extract_context.py B-1061

# Complete workflow orchestration
uv run python scripts/workflow_orchestrator.py B-1061 --execute

# Create new backlog items with auto-ID
echo "your idea" | uv run python scripts/create_backlog_item.py

# Auto-generate PRDs from backlog context
uv run python scripts/generate_prd.py B-1061 --generate-prd
```

**Traditional Manual Workflow:**
1. **Backlog Selection** → Pick top scored item from `000_core/000_backlog.md`
2. **PRD Creation** → Use `000_core/001_PRD_TEMPLATE.md` (skip for items < 5 pts AND score≥3.0)
3. **Task Generation** → Use `000_core/002_TASK-LIST_TEMPLATE.md` workflow
4. **AI Execution** → Use `000_core/003_EXECUTION_TEMPLATE.md` (the execution engine)
5. **State Management** → `.ai_state.json` for context persistence

<!-- WORKFLOW_REFERENCE: 400_guides/400_00_getting-started-and-index.md -->

### **File Organization**

- **Essential**: `400_guides/400_00_getting-started-and-index.md`, `400_guides/400_03_system-overview-and-architecture.md`, `000_core/000_backlog.md`

- **Implementation**: `100_memory/104_dspy-development-context.md`, `200_setup/202_setup-requirements.md`

- **Analysis**: `400_guides/400_01_documentation-playbook.md` - **🚨 MANDATORY: File deletion/deprecation analysis methodology**
- **Domain**: `100_memory/100_backlog-guide.md`

- *⚠️ CRITICAL**: Before ANY file operations, you MUST read and follow `400_guides/400_01_documentation-playbook.md` completely!

## 🛠️ Development Guidelines

### **🚨 MANDATORY: File Deletion/Deprecation Analysis**

- *Before suggesting ANY file deletion or deprecation, you MUST:

1. Run the analysis checklist**: `uv run python scripts/file_analysis_checklist.py <target_file>`
2. **Follow the 6-step process**in `400_guides/400_01_documentation-playbook.md`
3.**Complete ALL steps**before making recommendations
4.**Get explicit user approval**for high-risk operations**This is NON-NEGOTIABLE**- failure to follow these steps means you cannot suggest file deletion!

## 🚨 CRITICAL SAFETY REQUIREMENTS

### **⚠️ MANDATORY: File Analysis Before Any File Operations**

- *BEFORE suggesting ANY file deletion, deprecation, or archiving, you MUST:**1.**Read `400_guides/400_01_documentation-playbook.md`**- Complete the 6-step mandatory analysis
2.**Complete ALL steps**- No exceptions, no shortcuts
3.**Show cross-references**- Prove you've done the analysis
4.**Get user approval**- For any high-risk operations**🚨 FAILURE TO FOLLOW THESE STEPS MEANS YOU CANNOT SUGGEST FILE OPERATIONS!**

- *📋 Quick Checklist:**- [ ] Read `400_guides/400_01_documentation-playbook.md` (463 lines - READ ALL OF IT)

- [ ] Complete 6-step mandatory analysis

- [ ] Show all cross-references

- [ ] Provide detailed reasoning

- [ ] Get explicit user approval

### **📚 Complete Documentation Inventory**

**For complete documentation inventory, see `400_guides/400_documentation-reference.md`**

**Essential Files Quick Reference:**

- **Critical**: `100_memory/100_cursor-memory-context.md`, `000_core/000_backlog.md`, `400_guides/400_03_system-overview-and-architecture.md`, `400_guides/400_00_getting-started-and-index.md`, `400_guides/400_04_development-workflow-and-standards.md`, `400_guides/400_02_governance-and-ai-constitution.md`, `400_guides/400_01_documentation-playbook.md`, `400_guides/400_11_deployments-ops-and-observability.md`, `400_guides/400_cursor-context-engineering-guide.md`
- **Workflow**: `000_core/001_PRD_TEMPLATE.md`, `000_core/002_TASK-LIST_TEMPLATE.md`, `000_core/003_EXECUTION_TEMPLATE.md`
- **Setup**: `200_setup/202_setup-requirements.md`
- **Architecture**: `100_memory/104_dspy-development-context.md`
- **Coding Standards**: `400_guides/400_04_development-workflow-and-standards.md` (NEW - conflict prevention system)

### **🗄️ Vector Database Status**

**Database**: PostgreSQL with pgvector extension
**Status**: ✅ **FULLY SYNCHRONIZED** (2025-08-14)
**Coverage**: 32 documents, 1,064 chunks
**CONTEXT_INDEX**: 20/20 files indexed with role mapping

#### **Database Health:**
- **Core Files**: 11/11 files current and indexed
- **400_guides**: 14/14 files current and indexed
- **500_research**: 1/1 files current and indexed
- **Cross-References**: 35% average coverage across all guides
- **Semantic Search**: Full-text, vector similarity, and metadata search operational

#### **AI Rehydration Capability:**
- **Memory Rehydrator**: Can access all core documentation
- **Role-Aware Context**: Builds context bundles based on CONTEXT_INDEX roles
- **Task-Scoped Retrieval**: Hybrid search via vector store with span grounding
- **Token Budgeting**: ~1,200 tokens default with pinned anchors firs

#### **Recent Database Updates:**
- **P0 Critical**: Updated outdated files (100_cursor-memory-context.md, 000_backlog.md)
- **P1 High**: Added 7 missing files from CONTEXT_INDEX
- **Verification**: Complete database integrity check passed
- **Cross-Reference Analysis**: All guides properly linked

<!-- DOCUMENTATION_REFERENCE: 400_guides/400_documentation-reference.md -->

### **🎯 When to Read What: Context-Specific Guidance**

**For detailed context-specific guidance, see `400_guides/400_documentation-reference.md`**

**Quick Reading Order:**

1. **New Sessions**: `400_guides/400_00_getting-started-and-index.md` → `100_memory/100_cursor-memory-context.md` → `000_core/000_backlog.md` → `400_guides/400_03_system-overview-and-architecture.md`
2. **Development**: `400_guides/400_00_getting-started-and-index.md` → workflow files → implementation guides
3. **Research**: `500_research/500_research-index.md` → `500_research/500_dspy-research.md`, `500_research/500_rag-system-research.md`
4. **File Management**: `400_guides/400_01_documentation-playbook.md` (MANDATORY) → `200_setup/400_guides/400_05_codebase-organization-patterns.md`

### **🔗 Cross-Reference System**

**Status**: ✅ **FULLY OPERATIONAL** (2025-08-14)

#### **CONTEXT_INDEX Coverage:**
- **Total Files**: 20 files with role-based indexing
- **Core Files**: 13 files (entry, priorities, architecture, navigation, etc.)
- **Specialized Files**: 7 files (deployment, integration, migration, etc.)
- **Role Mapping**: Each file assigned specific role for AI rehydration

#### **Cross-Reference Quality:**
- **High Coverage**: 400_context-priority-guide.md (72% cross-references)
- **Medium Coverage**: 400_ai-constitution.md, 400_development-workflow.md (38-48%)
- **Low Coverage**: 400_deployment-operations.md, 400_performance-optimization-guide.md (3-4%)
- **Average Coverage**: 35% across all 400_guides files

#### **Navigation Patterns:**
- **Safety-First**: AI constitution and file analysis guides prominently referenced
- **Quality-Focused**: Code criticality and testing strategy guides well-linked
- **Development-Oriented**: Project overview and system overview central to navigation
- **Specialized Access**: Deployment, integration, migration guides available for specific tasks

<!-- CONTEXT_GUIDANCE_REFERENCE: 400_guides/400_documentation-reference.md -->

<!-- AUTO:current_priorities:start -->
### **Current Priorities**

1. **B‑095**: MCP Server Role Auto-Detection (2 points)
   - Enhance MCP server to automatically detect role based on conversation context

2. **B‑1016**: RL-Enhanced DSPy Model Selection (7 points)
   - Implement reinforcement learning to optimize model selection, hyperparameter tuning, and performance-based evolution in the existing DSPy multi-agent system

3. **B‑1021**: Transformer Attention for Memory Orchestration (5 points)
   - Add transformer attention mechanisms to memory merger for intelligent cross-system relationship learning and dynamic context prioritization

4. **B‑1022**: Graph Neural Networks for Adaptive Memory Graphs (7 points)
   - Implement GNN learning for entity and dependency graphs to enable adaptive graph structure learning and multi-hop reasoning
<!-- AUTO:current_priorities:end -->

<!-- AUTO:recently_completed:start -->
No recently completed items.
<!-- AUTO:recently_completed:end -->

<!-- AUTO:doc_health:start -->
### **Documentation Health**

- Files checked: None
- Anchor warnings: 0
- Invariant warnings: 0
- Last run: 2025-09-20T02:37:19
<!-- AUTO:doc_health:end -->

## Memory Rehydration Commands

### Quick Memory Rehydration
```bash
# Standard memory rehydration
./scripts/memory_up.sh

# With custom stability (lower = more diverse results)
./scripts/memory_up.sh -q "current project status" -r planner

# Minimal mode for debugging
./scripts/memory_up.sh -q "memory context" -r researcher
```

### Role-Specific Memory Rehydration
```bash
# Planner role - strategic context
./scripts/memory_up.sh -r planner "current project status"

# Coder role - implementation context
./scripts/memory_up.sh -r coder "implement authentication function"

# Researcher role - analysis context
./scripts/memory_up.sh -r researcher "performance analysis"

# Implementer role - system context
./scripts/memory_up.sh -r implementer "database optimization"
```
