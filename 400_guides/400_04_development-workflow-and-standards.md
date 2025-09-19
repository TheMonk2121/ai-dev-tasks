# 🔄 Development Workflows & Standards

<!-- ANCHOR_KEY: development-workflow-standards -->
<!-- ANCHOR_PRIORITY: 5 -->
<!-- ROLE_PINS: ["implementer", "coder"] -->

## 🔍 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Complete development workflow and coding standards for implementing features | Starting a new feature, implementing changes, or reviewing development process | Read 05 (Codebase Organization) then apply the workflow to your development |

- **what this file is**: End-to-end development workflow and coding standards for implementing features.

- **read when**: When starting a new feature, implementing changes, or reviewing development process.

- **do next**: Read 05 (Codebase Organization & Patterns) then apply the workflow to your development.

## 📋 **Table of Contents**

### **Core Workflow**
- [🧭 Workflow (Idea → Live)](#-workflow-idea--live)
- [🧱 Detailed Workflow Stages](#-detailed-workflow-stages)

### **Governance & Standards**
- [🛡️ AI Constitution & Governance Rules](#️-ai-constitution--governance-rules)
- [🛡️ Governance-by-Code Insights](#️-governance-by-code-insights)
- [💬 Communication Patterns Guide](#-communication-patterns-guide)

### **Analysis & Problem Solving**
- [🧠 Strategic Analysis: [Topic]](#-strategic-analysis-topic)
- [🚨 The Problem is Real](#-the-problem-is-real)
- [💡 The Opportunity](#-the-opportunity)
- [🎯 Proposed Solution](#-proposed-solution)

### **Implementation & Quality**
- [📚 Documentation Playbook & File Management](#-documentation-playbook--file-management)
- [🧪 Testing & Quality Assurance](#-testing--quality-assurance)
- [🏗️ Testing Infrastructure Guide](#️-testing-infrastructure-guide)
- [🔧 Implementation Patterns Library](#-implementation-patterns-library)

### **Reference Materials**
- [🧩 Standards](#-standards)
- [🔧 How-To (Common Tasks)](#-how-to-common-tasks)
- [📝 Checklists](#-checklists)
- [🔗 Interfaces](#-interfaces)
- [📚 References](#-references)

## 🎯 **Current Status**
- **Priority**: 🔥 **HIGH** - Essential for development workflow
- **Phase**: 2 of 4 (Codebase Development)
- **Dependencies**: 03 (System Overview & Architecture)

## 🎯 **Purpose**

Define the end-to-end development workflow (from idea to deployment) and the standards we enforce to keep quality high and changes safe.

## 📋 When to Use This Guide

- Starting a new feature or refactor
- Planning or reviewing implementation steps
- Aligning on commit, review, and testing standards
- Preparing changes for deploymen

## ✅ Expected Outcomes

- Clear, repeatable workflow stages
- Consistent implementation and review standards
- Traceable commits tied to backlog items
- Changes that pass tests, link checks, and CI gates

## 🧭 Workflow (Idea → Live)

1) Backlog and Scope
- Open or select a backlog item in `000_core/000_backlog.md`
- Confirm dependencies and acceptance criteria

2) Planning
- Read context from `400_00_getting-started-and-index.md` and `400_03_system-overview-and-architecture.md`
- For docs work, consult `400_01_documentation-playbook.md`

3) Implementation
- Follow code standards in `400_05_coding-and-prompting-standards.md`
- Use evidence-first edits and keep commits atomic

4) Testing
- Apply testing strategy from `400_05_coding-and-prompting-standards.md#testing-strategy-and-quality-gates`
- Ensure unit/integration/E2E coverage as appropriate

5) Security & Compliance
- Review `400_10_security-compliance-and-access.md` for security checks

6) Deployment & Ops
- Use `400_11_deployments-ops-and-observability.md` for rollout and validation

## 🧱 Detailed Workflow Stages

### Stage 1: Setup & Context
- Environment check: `uv run python scripts/venv_manager.py --check`
- Memory rehydration: `./scripts/shell/utilities/memory_up.sh -q "your task"`
- Quick conflict check: `uv run python scripts/quick_conflict_check.py`
- **Cursor Git Integration Fix**: If you see "🔍 Quick conflict check" messages during commits, use `git commit --no-verify` or `./scripts/commit_without_cursor.sh "message"` to bypass Cursor's built-in conflict detection

## 🛡️ **AI Constitution & Governance Rules**

### **🚨 CRITICAL: AI Constitution Compliance**

**Why This Matters**: All AI operations must comply with the project's AI constitution to ensure safety, consistency, and proper governance. This is non-negotiable for system integrity.

### **Core AI Constitution Rules**

#### **1. Memory Context Preservation**
- **Context Rehydration**: Always run memory rehydration before AI operations
- **Cross-Session Continuity**: Maintain context across development sessions
- **Decision Tracking**: Record all AI decisions and their rationale
- **Context Validation**: Verify context integrity before proceeding

#### **2. Safety & Governance**
- **Input Validation**: All AI inputs must be validated and sanitized
- **Output Verification**: All AI outputs must be verified for safety and accuracy
- **Constitution Hooks**: AI prompts must include constitution compliance checks
- **Runtime Validation**: Continuous validation during AI operations

#### **3. Role-Based Access Control**
- **DSPy Role System**: Access AI capabilities through proper DSPy roles
- **Role-Specific Context**: Use role-appropriate context for different tasks
- **Permission Validation**: Verify role permissions before operations
- **Context Isolation**: Maintain role-specific context boundaries

#### **4. Error Handling & Recovery**
- **Graceful Degradation**: AI failures must not crash the system
- **Fallback Mechanisms**: Provide fallback options for AI failures
- **Error Logging**: Log all AI errors with context and recovery steps
- **Recovery Procedures**: Implement automatic recovery where possible

### **AI Constitution Implementation**

#### **Constitution Hooks in Prompts**
```python
# Example constitution-compliant promp
constitution_prompt = f"""
{base_prompt}

🚨 AI CONSTITUTION COMPLIANCE:
- Verify input safety and validation
- Ensure output accuracy and safety
- Maintain context integrity
- Follow role-specific guidelines
- Log all decisions and actions

CONTEXT: {current_context}
ROLE: {current_role}
SAFETY_LEVEL: {safety_level}
"""
```

#### **Runtime Constitution Validation**
```python
class ConstitutionValidator:
    """Validates AI operations against constitution rules."""

    def validate_input(self, input_data: str) -> bool:
        """Validate input against safety rules."""
        # Implementation details
        pass

    def validate_output(self, output_data: str) -> bool:
        """Validate output against safety rules."""
        # Implementation details
        pass

    def log_decision(self, decision: str, context: dict) -> None:
        """Log AI decision for audit trail."""
        # Implementation details
        pass
```

#### **Constitution Compliance Commands**
```bash
# Validate constitution compliance
uv run python scripts/validate_constitution.py --check-all

# Check AI operation safety
uv run python scripts/ai_safety_check.py --operation "your_operation"

# Validate context integrity
uv run python scripts/validate_context.py --full-check

# Constitution compliance repor
uv run python scripts/constitution_report.py --output compliance_report.md
```

#### **Cursor Rules Integration**
- **Memory Rehydration Trigger**: `.cursorrules` automatically triggers `./scripts/shell/utilities/memory_up.sh` at the start of new chats
- **Two Types of Cursor Rules**:
  - **Root Level**: `.cursorrules` - Contains memory rehydration trigger and core project rules
  - **Directory Level**: `.cursor/rules/` - Contains specialized rules for specific contexts
- **Automatic Context Loading**: Ensures AI has immediate access to project state, backlog, and system architecture
- **Role-Specific Context**: Memory rehydration includes role-specific information (planner, implementer, researcher, coder)

## 🛡️ **Governance-by-Code Insights**

### **🚨 CRITICAL: Governance-by-Code is Essential**

**Why This Matters**: Governance-by-code provides automated, consistent enforcement of governance rules through CI/CD pipelines. Without automated governance, compliance becomes manual, error-prone, and unsustainable.

### **Core Governance-by-Code Principles**

#### **1. Single Source of Truth = CI**
- **Principle**: Docs explain; CI enforces
- **Application**: All governance rules must be automated in CI/CD pipelines
- **Avoid**: Manual checklists or documentation-only enforcemen

#### **2. Small, Composable Tests > Giant End-to-End**
- **Principle**: If a check flakes, quarantine it fas
- **Application**: Build small, focused CI jobs that can be individually disabled
- **Avoid**: Monolithic validation systems that fail as a uni

#### **3. Budgets, Not Vibes**
- **Principle**: Every gate ties to a budget (latency p95, recall@k, token cost)
- **Application**: Define measurable thresholds for all governance gates
- **Avoid**: Subjective or qualitative enforcement criteria

#### **4. Progressive Hardening**
- **Principle**: Start permissive, move to required after 3–7 green runs
- **Application**: Begin with warn-only gates, flip to fail after proven stability
- **Avoid**: Starting with strict enforcement that blocks developmen

### **Memory System Evolution Insights**

#### **1. Markdown as Router, Not Encyclopedia**
- **Insight**: Point to RAG/CAG instead of restating facts
- **Application**: Turn 100_cursor-memory-context.md into thin index/map-of-maps
- **Benefit**: Freshness and confidence win by design

#### **2. RAG/CAG as Source of Truth**
- **Insight**: Vector DB provides facts, docs provide routing
- **Application**: Build ≤200-token hydration pins from RAG/CAG
- **Benefit**: Always current, always relevan

#### **3. Map-of-Maps for Structural Routing**
- **Insight**: Help Cursor AI navigate codebase efficiently
- **Application**: Extract module graphs, entrypoints, risk assessments
- **Benefit**: Surgical AI assistance instead of "read half the repo"

#### **4. Memory Events → Facts → Pins**
- **Insight**: Structured memory pipeline with budgets
- **Application**: Capture CI results, evals, vector health as events
- **Benefit**: Measurable, auditable memory system

### **Industry Best Practices**

#### **1. Policy-as-Code (IBM, AWS, Azure)**
- **Practice**: Embed governance in pipelines, not just documentation
- **Examples**: AWS Bedrock Guardrails, Azure Groundedness Detection
- **Application**: CI jobs enforce policies, not human review

#### **2. System Cards (OpenAI)**
- **Practice**: Lightly human-readable dashboards of behavior and metrics
- **Application**: Expose governance health via metrics and dashboards
- **Benefit**: Transparency and accountability

#### **3. Automated Risk Measurement**
- **Practice**: Continuous monitoring and measurement of AI system risks
- **Application**: Automated risk assessment and alerting systems
- **Benefit**: Proactive risk identification and mitigation

### **Governance-by-Code Commands**

#### **Governance Management Commands**
```bash
# Validate governance compliance
uv run python scripts/validate_governance_compliance.py --policy ai_safety --full-check

# Test governance rules
uv run python scripts/test_governance_rules.py --rule ethical_ai --test-scenario fairness

# Monitor governance health
uv run python scripts/monitor_governance_health.py --real-time --output governance_report.md

# Generate governance repor
uv run python scripts/generate_governance_report.py --policy all --output governance_report.md
```

#### **CI/CD Integration Commands**
```bash
# Integrate governance into CI/CD
uv run python scripts/integrate_governance_cicd.py --pipeline main --governance-policy ai_safety

# Test governance pipeline
uv run python scripts/test_governance_pipeline.py --pipeline main --governance-rule ethical_ai

# Validate governance automation
uv run python scripts/validate_governance_automation.py --pipeline main --full-check

# Monitor governance pipeline health
uv run python scripts/monitor_governance_pipeline.py --pipeline main --real-time
```

### **Governance-by-Code Quality Gates**

#### **Automation Standards**
- **CI Integration**: All governance rules must be automated in CI/CD
- **Test Coverage**: Governance tests must have comprehensive coverage
- **Performance Budgets**: All governance gates must have measurable thresholds
- **Progressive Hardening**: Governance must start permissive and harden over time

#### **Compliance Requirements**
- **Policy Enforcement**: All policies must be automatically enforced
- **Risk Monitoring**: Continuous monitoring of AI system risks
- **Audit Trails**: Comprehensive logging of governance decisions
- **Performance Metrics**: Measurable governance performance indicators

## 💬 **Communication Patterns Guide**

### **🚨 CRITICAL: Communication Patterns are Essential**

**Why This Matters**: Communication patterns provide structured approaches for effective AI-user interaction and collaboration. Without proper communication patterns, interactions become inefficient, misunderstandings occur, and collaboration quality suffers.

### **Successful Communication Patterns**

#### **1. Strategic Discussion Format**
**Pattern**: Problem → Analysis → Strategy → Questions
- **Problem**: Concrete metrics and clear pain points
- **Analysis**: Systematic breakdown of current state
- **Strategy**: Phased approach with clear benefits
- **Questions**: Invite collaboration rather than assumptions

**Example**:
```
🚨 **The Problem is Real**: 51 files, 28,707 lines of documentation bloa
💡 **Proposed Strategy**: Apply README context management principles
🎯 **Expected Benefits**: Reduced cognitive load, improved quality
❓ **Questions for You**: What's your tolerance for automated changes?
```

#### **2. Structured Response Elements**
**Pattern**: Use consistent formatting that resonates
- **Clear sections** with emoji headers (🎯, 💡, 🚀, ❓)
- **Concrete metrics** (file counts, line counts, performance numbers)
- **Actionable timeframes** (Week 1, Week 2, Phase 1, Phase 2)
- **Balanced approach** (not over-engineering, but thorough)

#### **3. User Preference Alignment**
**Pattern**: Match user's communication style
- **Strategic questions** rather than jumping to implementation
- **Systematic approaches** with clear phases
- **Incremental, testable changes** over big-bang solutions
- **Focus on "why" before "how"**

#### **4. Memory System Integration**
**Pattern**: Leverage memory context for personalization
- **Solo developer** in local-first environmen
- **Simpler, streamlined approaches** preferred
- **Avoid overfitting or over-complication**
- **Plain, straightforward language**

### **Formatting Guidelines**

#### **Strategic Discussions**
```
## 🧠 **Strategic Analysis: [Topic]**

### **Current State Assessment**
- **Concrete metrics** and clear pain points
- **Systematic breakdown** of current state

### **Proposed Strategy**
- **Phased approach** with clear timeframes
- **Expected benefits** with specific outcomes

### **Key Design Decisions**
- **Options presented** rather than assumptions
- **Questions for collaboration** and input

### **Expected Benefits**
- **Concrete improvements** with metrics
- **Clear value proposition**
```

#### **Problem-Solution Format**
```
## 🚨 **The Problem is Real**
- **Specific metrics** (files, lines, performance)
- **Clear pain points** and impac

## 💡 **The Opportunity**
- **Leverage existing successes** (like README context system)
- **Apply proven patterns** to new domains

## 🎯 **Proposed Solution**
- **Systematic approach** with phases
- **Clear benefits** and outcomes
```

### **Communication Pattern Commands**

#### **Pattern Management Commands**
```bash
# List communication patterns
uv run python scripts/list_communication_patterns.py --category strategic

# Apply communication pattern
uv run python scripts/apply_communication_pattern.py --pattern strategic_discussion --context user_preferences

# Validate communication effectiveness
uv run python scripts/validate_communication_effectiveness.py --pattern strategic_discussion --user-feedback feedback.json

# Generate communication repor
uv run python scripts/generate_communication_report.py --pattern all --output communication_report.md
```

#### **Pattern Quality Commands**
```bash
# Test communication pattern
uv run python scripts/test_communication_pattern.py --pattern strategic_discussion --test-scenario planning

# Measure pattern effectiveness
uv run python scripts/measure_communication_effectiveness.py --pattern strategic_discussion --metrics clarity engagemen

# Generate pattern repor
uv run python scripts/generate_communication_pattern_report.py --pattern strategic_discussion --output pattern_report.md

# Monitor communication quality
uv run python scripts/monitor_communication_quality.py --real-time --output quality_report.md
```

### **Communication Pattern Quality Gates**

#### **Pattern Standards**
- **Clarity**: All communication patterns must be clear and understandable
- **Effectiveness**: Patterns must improve communication quality and efficiency
- **Consistency**: Patterns must be consistently applied across interactions
- **User Alignment**: Patterns must align with user preferences and needs

#### **Communication Requirements**
- **Structure**: All communications must follow established patterns
- **Metrics**: Communications must include concrete metrics and data
- **Collaboration**: Communications must invite user input and collaboration
- **Quality**: All communications must meet established quality standards

#### 10-minute triage (from Comprehensive Guide)
- Merge markers: `git grep -nE '^(<<<<<<<|=======|>>>>>>>)'`
- Python deps: `python -m pip check`
- Node deps: `npm ls --all`
- Deep audit pointers: `python scripts/conflict_audit.py --full`, `python scripts/system_health_check.py --deep`

### Stage 2: Planning
- Assess code criticality (Tier 1–3) and affected modules
- Decide on reuse vs build per `400_05_coding-and-prompting-standards.md`
- Define test plan and acceptance criteria

### Stage 3: Implementation
- Follow coding patterns and guardrails in 05 (types, errors, structure)
- Keep edits atomic and evidence-first; reference sources in commit body
- Useful commands: `ruff check .`, `ruff format .`

### Stage 4: Testing
- Unit, integration, and system tests as appropriate
- Coverage targets and quality gates per 05 testing strategy

## 📚 **Documentation Playbook & File Management**

### **🚨 MANDATORY: File Deletion/Deprecation Analysis**

**Before suggesting ANY file deletion, deprecation, or archiving, you MUST:**

1. **Complete 6-Step Mandatory Analysis** (from `400_01_documentation-playbook.md`)
2. **Show All Cross-References** - Prove you've done the analysis
3. **Get Explicit User Approval** - For any high-risk operations
4. **Follow Documentation Rules** - Use proper tiering and categorization

**🚨 FAILURE TO FOLLOW THESE STEPS MEANS YOU CANNOT SUGGEST FILE OPERATIONS!**

### **6-Step Mandatory Analysis Process**

#### **Step 1: File Analysis Checklist**
```bash
# Run the analysis checklis
uv run python scripts/file_analysis_checklist.py <target_file>

# Check for conflicts and dependencies
uv run python scripts/quick_conflict_check.py
uv run python scripts/conflict_audit.py --full
```

#### **Step 2: Cross-Reference Analysis**
- **Upstream Dependencies**: Files that reference this file
- **Downstream Dependencies**: Files this file references
- **Context Index**: Memory system integration points
- **Documentation Links**: Cross-references in guides

#### **Step 3: Impact Assessment**
- **Criticality Level**: Tier 1 (Critical), Tier 2 (High), Tier 3 (Supporting)
- **User Impact**: Who will be affected by this change
- **System Impact**: How this affects system functionality
- **Recovery Plan**: How to restore if needed

#### **Step 4: Documentation Rules Compliance**
- **Tier Classification**: Proper priority classification (0-12)
- **Role Pins**: Appropriate role assignments
- **Content Type**: Guide, reference, example, or archive
- **Cross-Reference Updates**: Update all related documentation

#### **Step 5: Implementation Planning**
- **Migration Strategy**: How to safely move/archive contain
- **Rollback Plan**: How to undo if problems arise
- **Testing Plan**: How to validate the change
- **Communication Plan**: How to notify affected users

#### **Step 6: Execution & Validation**
- **Safe Execution**: Follow the planned approach
- **Validation**: Verify the change worked correctly
- **Cross-Reference Update**: Update all related documentation
- **Memory Context Update**: Update memory system integration

### **Documentation Tier System**

#### **Tier 1 (Critical - Priority 0-10)**
- **Core Memory Context**: `100_cursor-memory-context.md`
- **System Overview**: `400_03_system-overview-and-architecture.md`
- **Backlog Management**: `000_core/000_backlog.md`
- **Development Workflow**: This guide

#### **Tier 2 (High - Priority 15-20)**
- **AI Frameworks**: `400_09_ai-frameworks-dspy.md`
- **Performance Optimization**: `400_11_performance-optimization.md`
- **Code Organization**: `400_05_codebase-organization-patterns.md`

#### **Tier 3 (Supporting - Priority 25-30)**
- **Project Planning**: `400_07_project-planning-roadmap.md`
- **Task Management**: `400_08_task-management-workflows.md`
- **Advanced Configurations**: `400_12_advanced-configurations.md`

### **File Management Commands**

#### **Safe File Operations**
```bash
# Quick conflict check
uv run python scripts/quick_conflict_check.py

# Comprehensive conflict audi
uv run python scripts/conflict_audit.py --full

# File analysis checklis
uv run python scripts/file_analysis_checklist.py <target_file>

# Documentation coherence validation
uv run python scripts/doc_coherence_validator.py

# Memory context update
uv run python scripts/update_cursor_memory.py
```

#### **Documentation Health Monitoring**
```bash
# Check documentation health
uv run python scripts/documentation_health_check.py

# Validate cross-references
uv run python scripts/validate_cross_references.py

# Check for broken links
uv run python scripts/check_broken_links.py
```
- Run: `uv run pytest tests/ -q` (see markers/tiers in repo)
- **RAGChecker Evaluation**: Run official RAGChecker evaluation for RAG system changes
  ```bash
  # Run Official RAGChecker evaluation
  uv run python scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable --lessons-mode advisory --lessons-scope profile --lessons-window 5

  # Pre-commit RAGChecker validation
  uv run python scripts/pre_commit_ragchecker.py

  # Check evaluation status
  cat metrics/baseline_evaluations/EVALUATION_STATUS.md

  # CI/CD automated evaluation (GitHub Actions)
  # Triggered automatically on RAGChecker-related changes
  ```

### Stage 5: Quality
- Code review checklist (function length, typing, errors, docs)
- CI dry-run validates lint, types, tests on PRs

### Stage 6: Deploymen
- Pre-deploy checklist (tests/quality/perf/security) then rollout via 11

## 🧩 Standards

- Commits reference backlog IDs where applicable
- Documentation updated alongside code changes
- No broken links (link validation required)
- Consolidated guide links only (no links to archived 600_ files)
- Consistent section structure across guides

### Commit & Traceability
- Reference backlog IDs when applicable (e.g., B-xxxx)
- Summarize problem and resolution for housecleaning items

## 🔧 How-To (Common Tasks)

- Start a feature: align scope, create branch if required by policy, implement with small commits
- Update docs: follow `400_01_documentation-playbook.md` structure and cross-link patterns
- Add tests: consult testing gates in 05; keep tests fast and focused
- Run link validation: ensure all internal links resolve in 400_guides and 000/100/

### Development Commands
```bash
# Start development session
uv run python scripts/single_doorway.py generate "feature description"

# Check code quality
uv run ruff check .

# Run tests
uv run pytest tests/ -q
```

## 🧪 Evaluation Profiles and Layout

<!-- ANCHOR_KEY: evaluation-profiles-layout -->
<!-- ANCHOR_PRIORITY: 6 -->
<!-- ROLE_PINS: ["implementer", "coder"] -->

### TL;DR
- Single orchestrator with profile dispatch; no duplicate runners.
- Configs live under `evals/configs/{gold,real,mock}/`.
- Baseline outputs under `metrics/baseline_evaluations/{gold,real,mock}/`.

### Entrypoints
- Orchestrator: `scripts/evaluation/ragchecker_official_evaluation.py`
- Module wrapper: `python -m scripts.evaluation ...` (thin forwarder)
- Profiles package: `scripts/evaluation/profiles/{gold,real,mock}.py`
- Shared utils: `scripts/evaluation/core/`

### Commands (uv-only)
```bash
# Gold (PR gates / baselines)
UV_PROJECT_ENVIRONMENT=.venv \
uv run python scripts/evaluation/ragchecker_official_evaluation.py --profile gold

# Real (development, full pipeline)
UV_PROJECT_ENVIRONMENT=.venv \
uv run python scripts/evaluation/ragchecker_official_evaluation.py --profile real

# Mock (plumbing; forbidden on main gates)
UV_PROJECT_ENVIRONMENT=.venv \
uv run python scripts/evaluation/ragchecker_official_evaluation.py --profile mock
```

### Directory Structure
```
scripts/
  evaluation/
    ragchecker_official_evaluation.py   # single CLI
    __main__.py                         # python -m wrapper
    core/                               # shared utils
    profiles/
      gold.py
      real.py
      mock.py

evals/
  configs/
    gold/
    real/
    mock/

metrics/
  baseline_evaluations/
    gold/
    real/
    mock/

tests/
  evaluation/
    mock/test_mock_smoke.py
    test_main_wrapper.py
```

### Quality Gates (recap)
- Use ruff, black --check, and basedpyright.
- Enforce RAGChecker gates on gold where applicable.

### Virtual Environment Management

#### **Virtual Environment Manager Overview**
The Virtual Environment Manager ensures your project's virtual environment is properly activated and working before running any scripts. This solves the common issue where scripts fail because they can't find required dependencies.

#### **Usage Commands**
```bash
# Check Venv Status
uv run python scripts/venv_manager.py --check

# Activate Venv
uv run python scripts/venv_manager.py --activate

# Show Venv Information
uv run python scripts/venv_manager.py --info

# Validate Dependencies
uv run python scripts/venv_manager.py --validate

# Run Workflow with Venv Check
uv run python scripts/run_workflow.py generate "feature"
```

#### **Integration Points**
The venv manager is automatically integrated into:
1. **Memory Rehydrator** - Ensures venv is active before importing modules
2. **Single Doorway** - Uses venv Python for all subprocess calls
3. **Workflow Runner** - Checks venv before running any workflow

#### **Required Dependencies**
The venv manager checks for these essential packages:
- `psycopg` - Database connectivity
- `dspy` - Core AI framework
- `pytest` - Testing framework
- `ruff` - Code quality

#### **Benefits**
1. **Automatic Detection** - No need to manually activate venv
2. **Dependency Validation** - Ensures all required packages are installed
3. **Clear Error Messages** - Tells you exactly what's missing
4. **Seamless Integration** - Works with existing workflow scripts

#### **Troubleshooting**
```bash
# Venv Not Found
uv venv --python 3.12
uv sync --extra dev

# Missing Dependencies
uv sync --extra dev
uv add psycopg-binary dspy pytest ruff
```

**Import Errors**: The venv manager automatically handles Python path issues and ensures the correct Python executable is used.

### **Critical Lessons Learned: Evaluation System Design**

#### **🚨 CRITICAL DISCOVERY: Synthetic Data Evaluation - No True Baseline**

**Date**: 2025-01-06
**Category**: Evaluation System / Critical Discovery
**Severity**: CRITICAL - System-Wide Impact

#### **What Happened**
**CRITICAL DISCOVERY**: The entire evaluation system has been using synthetic test cases instead of the actual DSPy RAG system. This means we have NO TRUE BASELINE for our current RAG performance.

#### **The Real Problem**
- **Retrieval Oracle Hit: 6.7%** - This was from synthetic data, not real RAG
- **All performance metrics** are based on hardcoded test cases
- **No actual RAG system evaluation** has been performed
- **Baseline targets** (Precision ≥0.20, Recall ≥0.45) are meaningless without real data

#### **Root Cause Analysis**
1. **Evaluation System Design Flaw**
   - `ragchecker_official_evaluation.py` uses hardcoded test cases
   - No integration with actual DSPy RAG system
   - Synthetic data creates false performance metrics

2. **Missing Real RAG Integration**
   - Evaluation system calls `generate_answer_with_context()` with fake context
   - Never calls the actual `RAGModule.forward()` method
   - No connection to `HybridVectorStore` or real retrieval

3. **Baseline Measurement Error**
   - All performance targets based on synthetic data
   - No understanding of actual system capabilities
   - Optimization efforts targeting wrong metrics

#### **Prevention Strategies**

**Evaluation System Design**:
1. **Always verify data source** - Is it synthetic or real?
2. **Test with actual system** before establishing baselines
3. **Document data provenance** in all evaluation results
4. **Validate integration points** between evaluation and target system

**Baseline Establishment**:
1. **Run real system first** to establish true performance
2. **Compare synthetic vs real** to understand gaps
3. **Set targets based on real data** not assumptions
4. **Document evaluation methodology** clearly

**System Integration**:
1. **Test end-to-end flow** from query to response
2. **Validate all integration points** between components
3. **Use real data sources** for evaluation
4. **Document data flow** and dependencies clearly

#### **Key Lessons**
- **Test with Real Data**: Synthetic data doesn't reflect real performance
- **Validate Integration**: Ensure evaluation system connects to actual system
- **Document Data Sources**: Always know where your evaluation data comes from
- **Establish True Baselines**: Use real system performance as the foundation

## 📝 Checklists

- [ ] Backlog item selected and scoped
- [ ] Code follows 05 standards; types and naming are clear
- [ ] Tests added/updated and pass locally
- [ ] Links valid across docs (no references to removed files)
- [ ] Security considerations reviewed (10)
- [ ] Deployment plan confirmed (11)
- [ ] **RAGChecker evaluation run** for RAG system changes (if applicable)
- [ ] **CI/CD pipeline validation** for RAGChecker changes (automated)

## 🔗 Interfaces

- Backlog: `000_core/000_backlog.md`
- Memory System Overview: `400_guides/400_00_memory-system-overview.md`
- System Architecture: `400_guides/400_03_system-overview-and-architecture.md`
- Codebase Organization: `400_guides/400_05_codebase-organization-patterns.md`
- Security: `400_guides/400_10_security-compliance-and-access.md`
- Deployments/Ops: `400_guides/400_11_deployments-ops-and-observability.md`

## 🚀 **Memory System Rollout and Deployment**

### **🚨 CRITICAL: Memory System Rollout Guide**

**Purpose**: Step-by-step guide to roll out and validate the LTST memory system across environments.

#### **Step 1: Prepare Environment**

- Ensure Python deps: psycopg-binary, pytes
- Configure DATABASE_URL
- Recommended Postgres extensions:
  - vector (required for pgvector)
  - pg_trgm (optional for trigram decision search)

#### **Step 2: Apply Schema**

Apply the LTST schema objects (tables, views, functions):

```bash
psql "$DATABASE_URL" -f dspy-rag-system/config/database/ltst_memory_schema.sql
```

#### **Step 3: Healthcheck**

Verify connectivity, extensions, and required objects:

```bash
python scripts/memory_healthcheck.py
```

Resolve issues before proceeding.

#### **Step 4: Verification**

Run the end-to-end smoke test:

```bash
python scripts/run_memory_verification.py
```

Expected output includes context length, history count, and continuity score.

#### **Step 5: Feature Flags**

If `pg_trgm` is unavailable or you want to disable trigram search temporarily:

```bash
export DECISION_TRIGRAM_ENABLED=false
```

Decision search falls back to BM25-only.

#### **Step 6: Extended Tests**

```bash
# Session Continuity
pytest -q dspy-rag-system/tests/test_session_continuity.py

# LTST Comprehensive
pytest -q dspy-rag-system/tests/test_ltst_comprehensive.py

# Decision Retrieval
pytest -q dspy-rag-system/test_decision_retrieval.py
```

#### **Step 7: Observability**

The system records performance metrics to `memory_performance_metrics`. If this generates excessive logs/errors in early phases, gate insertion behind a feature flag or reduce verbosity.

#### **Step 8: Rollback**

Reapply known-good schema (if needed) and disable flags to revert to conservative paths.

#### **Memory System Deployment Checklist**

##### **Pre-Deployment**
- [ ] Database connection and permissions verified
- [ ] Required PostgreSQL extensions available
- [ ] Python dependencies installed
- [ ] Configuration environment variables se
- [ ] Backup of current system state created

##### **Deployment**
- [ ] LTST schema applied successfully
- [ ] Memory healthcheck passes
- [ ] Verification script completes successfully
- [ ] Feature flags configured appropriately
- [ ] Extended test suite passes

##### **Post-Deployment**
- [ ] System performance monitoring active
- [ ] Memory metrics being collected
- [ ] Error rates within acceptable thresholds
- [ ] User acceptance testing completed
- [ ] Rollback plan validated

##### **Validation**
- [ ] Memory context preservation working
- [ ] Cross-session continuity functioning
- [ ] Decision tracking operational
- [ ] Performance metrics within targets
- [ ] All integration tests passing

## 📚 References

- Documentation Playbook: `400_01_documentation-playbook.md`
- AI Frameworks (DSPy/MCP): `400_07_ai-frameworks-dspy.md`
- Integrations: `400_08_integrations-editor-and-models.md`
- Automation & Pipelines: `400_09_automation-and-pipelines.md`

## 🧪 **Testing & Quality Assurance**

### **🚨 CRITICAL: Testing & Quality Assurance are Essential**

**Why This Matters**: Testing and quality assurance ensure that all development work meets established standards, functions correctly, and maintains system reliability. Without proper testing, bugs proliferate, system stability degrades, and user experience suffers.

### **Testing Framework & Standards**

#### **Test Categories & Coverage**
- **Unit Tests**: Individual component testing with comprehensive coverage
- **Integration Tests**: Component interaction and system integration testing
- **Performance Tests**: System performance and scalability validation
- **Security Tests**: Security vulnerability and compliance testing
- **User Acceptance Tests**: End-user functionality and experience validation

#### **Quality Assurance Processes**
- **Code Review**: Peer review and automated quality checks
- **Static Analysis**: Code quality and security analysis
- **Dynamic Testing**: Runtime behavior and performance validation
- **Regression Testing**: Ensuring new changes don't break existing functionality

## 🔧 **Implementation Patterns Library**

### **🚨 CRITICAL: Implementation Patterns are Essential**

**Why This Matters**: Implementation patterns provide reusable, proven solutions for common development tasks. Without proper pattern integration into memory context, AI agents cannot provide consistent, high-quality implementation guidance or leverage established best practices.

### **Pattern Library Categories**

#### **1. Memory System Patterns**

##### **Memory Rehydration Pattern**
```python
def memory_rehydration_pattern(query: str, role: str) -> Dict[str, Any]:
    """Standard pattern for memory rehydration."""
    # Set environmen
    os.environ["POSTGRES_DSN"] = "mock://test"

    # Execute memory orchestration
    result = subprocess.run([
        "python3", "scripts/unified_memory_orchestrator.py",
        "--systems", "cursor",
        "--role", role,
        query
    ], capture_output=True, text=True)

    return json.loads(result.stdout)
```

##### **Context Integration Pattern**
```python
def context_integration_pattern(base_context: Dict[str, Any],
                               additional_context: Dict[str, Any]) -> Dict[str, Any]:
    """Standard pattern for integrating multiple context sources."""
    integrated_context = base_context.copy()

    # Merge additional context
    for key, value in additional_context.items():
        if key in integrated_context:
            if isinstance(integrated_context[key], list):
                integrated_context[key].extend(value)
            elif isinstance(integrated_context[key], dict):
                integrated_context[key].update(value)
            else:
                integrated_context[key] = value

    return integrated_contex
```

#### **2. DSPy Integration Patterns**

##### **DSPy Module Pattern**
```python
from dspy import Module, InputField, OutputField

class StandardDSPyModule(Module):
    """Standard pattern for DSPy module implementation."""

    def __init__(self):
        super().__init__()
        self.input_field = InputField()
        self.output_field = OutputField()

    def forward(self, input_data):
        """Standard forward method pattern."""
        # Process input
        processed_input = self.process_input(input_data)

        # Generate output
        output = self.generate_output(processed_input)

        # Validate output
        validated_output = self.validate_output(output)

        return validated_outpu

    def process_input(self, input_data):
        """Process input data."""
        # Implementation specific to module
        pass

    def generate_output(self, processed_input):
        """Generate output from processed input."""
        # Implementation specific to module
        pass

    def validate_output(self, output):
        """Validate output quality."""
        # Implementation specific to module
        pass
```

#### **3. System Integration Patterns**

##### **API Integration Pattern**
```python
def api_integration_pattern(endpoint: str, data: Dict[str, Any],
                           headers: Dict[str, str] = None) -> Dict[str, Any]:
    """Standard pattern for API integration."""

    # Set default headers
    if headers is None:
        headers = {"Content-Type": "application/json"}

    # Prepare request
    request_data = json.dumps(data)

    # Execute request
    try:
        response = requests.post(endpoint, data=request_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"API integration failed: {str(e)}")
```

##### **Database Integration Pattern**
```python
def database_integration_pattern(query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Standard pattern for database integration."""

    # Get database connection
    connection = get_database_connection()

    try:
        # Execute query
        cursor = connection.cursor()
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)

        # Fetch results
        results = cursor.fetchall()

        # Convert to list of dictionaries
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in results]

    finally:
        connection.close()
```

### **Implementation Pattern Commands**

#### **Pattern Management Commands**
```bash
# List available patterns
uv run python scripts/list_implementation_patterns.py --category memory_system

# Apply pattern to code
uv run python scripts/apply_implementation_pattern.py --pattern memory_rehydration --target-file target.py

# Validate pattern implementation
uv run python scripts/validate_pattern_implementation.py --pattern memory_rehydration --target-file target.py

# Generate pattern documentation
uv run python scripts/generate_pattern_documentation.py --pattern memory_rehydration --output pattern_doc.md
```

#### **Pattern Quality Commands**
```bash
# Test pattern implementation
uv run python scripts/test_pattern_implementation.py --pattern memory_rehydration --target-file target.py

# Measure pattern effectiveness
uv run python scripts/measure_pattern_effectiveness.py --pattern memory_rehydration --target-file target.py

# Generate pattern repor
uv run python scripts/generate_pattern_report.py --pattern memory_rehydration --output pattern_report.md
```

### **Implementation Pattern Quality Gates**

#### **Pattern Standards**
- **Reusability**: Patterns must be reusable across different contexts
- **Effectiveness**: Patterns must provide proven, effective solutions
- **Documentation**: All patterns must be well-documented with examples
- **Testing**: All patterns must be thoroughly tested and validated

#### **Implementation Requirements**
- **Consistency**: Pattern implementations must be consistent across the codebase
- **Quality**: Pattern implementations must meet established quality standards
- **Performance**: Pattern implementations must not degrade system performance
- **Maintenance**: Pattern implementations must be maintainable and extensible

**Why This Matters**: Testing and quality assurance provide the foundation for reliable, maintainable, and high-quality software development. Without proper testing, code quality suffers, bugs proliferate, and system reliability is compromised.

### **Testing Framework**

#### **Test Strategy & Planning**
```python
class TestingFramework:
    """Comprehensive testing framework for development workflows."""

    def __init__(self):
        self.test_types = {
            "unit": "Unit tests for individual components",
            "integration": "Integration tests for component interaction",
            "system": "System tests for end-to-end functionality",
            "performance": "Performance tests for system efficiency",
            "security": "Security tests for system protection"
        }
        self.test_strategies = {}

    def plan_testing(self, project_scope: dict) -> dict:
        """Plan comprehensive testing strategy for project."""

        # Validate project scope
        if not self._validate_project_scope(project_scope):
            raise ValueError("Invalid project scope")

        # Define testing strategy
        testing_strategy = self._define_testing_strategy(project_scope)

        # Plan test execution
        test_execution_plan = self._plan_test_execution(testing_strategy)

        # Define quality gates
        quality_gates = self._define_quality_gates(testing_strategy)

        return {
            "testing_planned": True,
            "testing_strategy": testing_strategy,
            "test_execution_plan": test_execution_plan,
            "quality_gates": quality_gates
        }

    def _validate_project_scope(self, project_scope: dict) -> bool:
        """Validate project scope completeness."""

        required_fields = ["components", "complexity", "risk_level", "timeline"]

        for field in required_fields:
            if field not in project_scope:
                return False

        return True

    def _define_testing_strategy(self, project_scope: dict) -> dict:
        """Define comprehensive testing strategy."""

        # Implementation for testing strategy definition
        return {
            "test_coverage_target": 0.90,
            "test_types": list(self.test_types.keys()),
            "automation_level": "high",
            "quality_thresholds": {
                "unit_test_coverage": 0.95,
                "integration_test_coverage": 0.85,
                "system_test_coverage": 0.80
            }
        }
```

#### **Quality Assurance & Gates**
```python
class QualityAssuranceFramework:
    """Manages quality assurance and quality gates."""

    def __init__(self):
        self.quality_dimensions = {
            "functionality": "Functional correctness and completeness",
            "reliability": "System reliability and stability",
            "performance": "System performance and efficiency",
            "security": "System security and protection",
            "maintainability": "Code maintainability and readability"
        }
        self.quality_gates = {}

    def validate_quality_gates(self, quality_metrics: dict) -> dict:
        """Validate that all quality gates are met."""

        # Validate quality metrics
        if not self._validate_quality_metrics(quality_metrics):
            raise ValueError("Invalid quality metrics")

        # Check quality gates
        gate_results = {}
        for dimension, threshold in self.quality_dimensions.items():
            gate_results[dimension] = self._check_quality_gate(
                dimension, quality_metrics.get(dimension, {})
            )

        # Overall quality assessmen
        overall_quality = self._assess_overall_quality(gate_results)

        return {
            "quality_validated": True,
            "gate_results": gate_results,
            "overall_quality": overall_quality,
            "recommendations": self._generate_quality_recommendations(gate_results)
        }

    def _validate_quality_metrics(self, quality_metrics: dict) -> bool:
        """Validate quality metrics completeness."""

        # Implementation for quality metrics validation
        return True  # Placeholder

    def _check_quality_gate(self, dimension: str, metrics: dict) -> dict:
        """Check if quality gate is met for specific dimension."""

        # Implementation for quality gate checking
        return {
            "passed": True,
            "score": 0.95,
            "threshold": 0.80,
            "details": f"Quality gate passed for {dimension}"
        }
```

### **Testing & Quality Commands**

#### **Testing Management Commands**
```bash
# Plan testing strategy
uv run python scripts/plan_testing.py --project-scope project_scope.yaml --output testing_strategy.md

# Execute test suite
uv run python scripts/execute_tests.py --test-type all --output test_results.json

# Generate test coverage repor
uv run python scripts/generate_coverage_report.py --output coverage_report.md

# Validate test quality
uv run python scripts/validate_test_quality.py --test-results test_results.json
```

#### **Quality Assurance Commands**
```bash
# Validate quality gates
uv run python scripts/validate_quality_gates.py --metrics quality_metrics.yaml --stric

# Generate quality repor
uv run python scripts/generate_quality_report.py --output quality_report.md

# Monitor quality trends
uv run python scripts/monitor_quality_trends.py --timeframe 30d --output quality_trends.md

# Quality improvement recommendations
uv run python scripts/generate_quality_recommendations.py --gate-results gate_results.json
```

### **Testing & Quality Quality Gates**

#### **Testing Standards**
- **Test Coverage**: Minimum 90% test coverage for all components
- **Test Quality**: All tests must be meaningful and maintainable
- **Automation**: High level of test automation required
- **Execution Time**: Tests must complete within acceptable time limits

#### **Quality Requirements**
- **Functionality**: All functional requirements must be me
- **Reliability**: System must be stable and reliable
- **Performance**: System must meet performance requirements
- **Security**: All security requirements must be satisfied
- **Maintainability**: Code must be maintainable and readable

## 🚀 **Implementation Summary & Best Practices**

### **🎯 Overview**

**Implementation Summary** documents completed improvements and best practices learned during development, providing valuable insights for future implementation work.

**What**: Comprehensive summary of implementation improvements, fixes, and patterns that have been successfully applied.

**When**: When implementing new features, fixing issues, or following established development patterns.

**How**: Reference the completed improvements and apply similar patterns to new development work.

### **✅ Completed Implementation Improvements**

#### **1. Import Safety Fixes**
- **Fixed `scripts/ragchecker_official_evaluation.py`**: Removed import-time `SystemExit` side effects by changing `raise SystemExit(main())` to `sys.exit(main())`
- **Result**: Script is now safe to import in tests without executing
- **Pattern**: Always use `sys.exit()` instead of `raise SystemExit()` in scripts

#### **2. Test Configuration Improvements**
- **Updated `pytest.ini`**: Added `norecursedirs` to exclude archived/experiment paths:
  - `600_archives`
  - `300_experiments` 
  - `docs/legacy`
  - `node_modules`
  - `.git`
  - `.pytest_cache`
  - `__pycache__`
  - `.dspy_cache`
- **Result**: PR test runs are now lean and focused on active code
- **Pattern**: Always exclude non-testable directories from pytest runs

#### **3. Metrics Cleanup System**
- **Created `scripts/clean_ephemeral_metrics.py`**: Comprehensive cleanup tool for ephemeral metrics
  - Removes zero-byte JSON/JSONL files
  - Optionally quarantines invalid JSON files
  - Dry-run mode by default
  - Configurable directories and quarantine location
- **Usage**:
  ```bash
  # Dry run
  python3 scripts/clean_ephemeral_metrics.py
  
  # Apply cleanup
  python3 scripts/clean_ephemeral_metrics.py --apply --quarantine-invalid
  ```
- **Pattern**: Always provide dry-run mode for destructive operations

#### **4. Static Import Analysis**
- **Created `scripts/check_static_imports.py`**: Comprehensive dependency analysis tool
  - Parses all Python files in scripts directory
  - Attempts to import top-level modules
  - Categorizes missing dependencies (external vs internal)
  - Generates CSV reports
  - Excludes test files by default
- **Usage**:
  ```bash
  # Basic analysis
  python3 scripts/check_static_imports.py
  
  # With CSV report
  python3 scripts/check_static_imports.py --csv dependency_report.csv
  
  # Include test files
  python3 scripts/check_static_imports.py --include-tests
  ```
- **Pattern**: Provide comprehensive analysis tools with multiple output formats

#### **5. Development Environment Improvements**
- **Virtual Environment Management**: Improved venv activation and dependency management
- **Script Safety**: All scripts now support dry-run and validation modes
- **Error Handling**: Comprehensive error handling with meaningful error messages
- **Logging**: Structured logging with appropriate log levels

### **🔧 Implementation Patterns Applied**

#### **Script Development Pattern**
```python
def main():
    """Main function with proper error handling."""
    try:
        # Implementation logic
        result = process_data()
        return result
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

#### **Configuration Management Pattern**
```python
class Config:
    """Configuration with validation and defaults."""
    def __init__(self, config_file: str = None):
        self.config = self._load_config(config_file)
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration values."""
        required_keys = ["database_url", "api_key"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config: {key}")
```

#### **Testing Pattern**
```python
def test_script_safety():
    """Test that scripts can be imported safely."""
    # Import should not execute main()
    import scripts.example_script
    assert hasattr(scripts.example_script, 'main')
```

### **📊 Implementation Metrics**

| Improvement | Files Affected | Lines Changed | Impact |
|-------------|----------------|---------------|---------|
| **Import Safety** | 1 | 2 | High - Test safety |
| **Test Configuration** | 1 | 8 | High - CI efficiency |
| **Metrics Cleanup** | 1 | 150+ | Medium - Maintenance |
| **Import Analysis** | 1 | 200+ | Medium - Development |
| **Environment** | Multiple | 50+ | High - Developer experience |

### **🎯 Lessons Learned**

1. **Always use `sys.exit()` instead of `raise SystemExit()`** in scripts
2. **Exclude non-testable directories** from pytest runs
3. **Provide dry-run mode** for all destructive operations
4. **Include comprehensive analysis tools** with multiple output formats
5. **Validate configuration** with meaningful error messages
6. **Use structured logging** with appropriate log levels

### **🔄 Continuous Improvement Process**

1. **Identify Issues**: Regular analysis of development pain points
2. **Implement Fixes**: Apply systematic improvements
3. **Document Patterns**: Capture successful implementation patterns
4. **Share Knowledge**: Update documentation with lessons learned
5. **Iterate**: Continuously improve based on feedback

---

## 🏗️ **Testing Infrastructure Guide**

### **🚨 CRITICAL: Testing Infrastructure Architecture**

**Purpose**: Complete guide to testing environment setup, tools, dependencies, and configuration for reproducible testing.

#### **Core Components**
- **Testing Environment**: Python 3.12 virtual environment with all dependencies
- **Database**: PostgreSQL with pgvector extension for vector operations
- **Evaluation Framework**: RAGChecker with AWS Bedrock integration
- **Memory Systems**: LTST memory system with database backend
- **Integration Tools**: MCP server, Cursor integration, and testing utilities

#### **Infrastructure Layers**
```
┌─────────────────────────────────────────────────────────────┐
│                    Testing Applications                     │
├─────────────────────────────────────────────────────────────┤
│                    Testing Framework                       │
├─────────────────────────────────────────────────────────────┤
│                    Core Dependencies                       │
├─────────────────────────────────────────────────────────────┤
│                    System Infrastructure                   │
└─────────────────────────────────────────────────────────────┘
```

### **🚀 Environment Setup**

#### **System Requirements**
- **Operating System**: macOS 12.0+, Windows 10+, or Linux Ubuntu 20.04+
- **Python**: Python 3.12 (required)
- **Memory**: Minimum 8GB RAM, recommended 16GB+
- **Storage**: Minimum 10GB free space
- **Network**: Internet access for package installation and AWS services

#### **Required Software**
- **Python 3.12**: [Download from python.org](https://python.org)
- **PostgreSQL 14+**: [Download from postgresql.org](https://postgresql.org)
- **Git**: [Download from git-scm.com](https://git-scm.com)
- **VS Code/Cursor**: [Download from cursor.sh](https://cursor.sh)

#### **Step-by-Step Setup**

**1. Clone Repository**
```bash
git clone https://github.com/yourusername/ai-dev-tasks.gi
cd ai-dev-tasks
```

**2. Create Virtual Environment**
```bash
# Create virtual environmen
python3.12 -m venv venv

# Activate virtual environmen
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
venv\Scripts\activate
```

**3. Install Dependencies**
```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.tx

# Install development dependencies
pip install -r requirements-dev.tx
```

**4. Database Setup**
```bash
# Install PostgreSQL (if not already installed)
# macOS with Homebrew:
brew install postgresql
brew services start postgresql

# Create database
createdb ai_agency

# Install pgvector extension
psql -d ai_agency -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**5. Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
# Set your database connection, AWS credentials, etc.
```

### **🛠️ Testing Tools & Dependencies**

#### **Core Testing Framework**

**Python Testing Stack**
- **pytest**: Primary testing framework
- **pytest-asyncio**: Async testing support
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking and patching

**Code Quality Tools**
- **Ruff**: Fast Python linter and formatter
- **Bandit**: Security linting
- **Pre-commit**: Git hooks for code quality

**Performance Testing**
- **pytest-benchmark**: Performance benchmarking
- **memory-profiler**: Memory usage profiling
- **cProfile**: Python profiling

#### **AI Development Tools**

**DSPy Framework**
- **dspy-ai**: Core DSPy framework
- **dspy-ai[all]**: Full DSPy with all dependencies
- **dspy-ai[bedrock]**: AWS Bedrock integration

**Vector Operations**
- **pgvector**: PostgreSQL vector extension
- **numpy**: Numerical computing
- **scikit-learn**: Machine learning utilities

**Evaluation & Monitoring**
- **ragchecker**: RAG evaluation framework
- **boto3**: AWS SDK for Python
- **psycopg**: PostgreSQL adapter

### **🔧 Configuration Management**

#### **Required Environment Variables**
```bash
# Database Configuration
POSTGRES_DSN=postgresql://username:password@localhost:5432/ai_agency
POSTGRES_HOST=localhos
POSTGRES_PORT=5432
POSTGRES_DB=ai_agency
POSTGRES_USER=username
POSTGRES_PASSWORD=password

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Testing Configuration
TESTING_MODE=true
TEST_DATABASE_URL=postgresql://username:password@localhost:5432/ai_agency_tes
LOG_LEVEL=DEBUG
```

#### **Configuration Files**

**pyproject.toml**
```toml
[tool.pytest.ini_options]
testpaths = ["tests", "src"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--import-mode=importlib --strict-markers"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "performance: marks tests as performance tests",
    "memory: marks tests as memory system tests",
    "retrieval: marks tests as retrieval system tests"
]

[tool.ruff]
target-version = "py312"
line-length = 88
select = ["E", "F", "I", "N", "W", "B", "A", "C4", "UP", "PL", "RUF"]
ignore = ["E501", "B008", "C901"]
extend-select = ["RUF001", "RUF002", "RUF003", "PLE2502"]
```

### **🧪 Testing Workflows**

#### **Test Execution Commands**

**Basic Testing**
```bash
# Run all tests
pytes

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run tests with verbose output
pytest -v

# Run tests and stop on first failure
pytest -x
```

**Specific Test Categories**
```bash
# Run only unit tests
pytest -m "not integration and not performance"

# Run only integration tests
pytest -m integration

# Run only performance tests
pytest -m performance

# Run only memory system tests
pytest -m memory

# Run only retrieval system tests
pytest -m retrieval
```

**Performance Testing**
```bash
# Run performance benchmarks
pytest --benchmark-only

# Run performance tests with profiling
pytest -m performance --profile

# Run memory profiling
pytest -m performance --memray
```

#### **Test Organization**

**Test Directory Structure**
```
tests/
├── unit/                    # Unit tests
│   ├── test_memory/        # Memory system unit tests
│   ├── test_retrieval/     # Retrieval system unit tests
│   └── test_integration/   # Integration unit tests
├── integration/             # Integration tests
│   ├── test_end_to_end/    # End-to-end workflow tests
│   ├── test_cross_system/  # Cross-system integration tests
│   └── test_performance/   # Performance integration tests
├── performance/             # Performance tests
│   ├── test_benchmarks/    # Performance benchmarks
│   ├── test_load/          # Load testing
│   └── test_stress/        # Stress testing
└── fixtures/                # Test fixtures and data
    ├── test_data/          # Test datasets
    ├── mock_services/      # Mock external services
    └── test_configs/       # Test configurations
```

### **🔍 Debugging & Troubleshooting**

#### **Common Issues & Solutions**

**Database Connection Issues**
```bash
# Check PostgreSQL status
brew services list | grep postgresql

# Restart PostgreSQL
brew services restart postgresql

# Check database connectivity
psql -h localhost -U username -d ai_agency -c "SELECT 1;"

# Reset database
dropdb ai_agency && createdb ai_agency
```

**Python Environment Issues**
```bash
# Check Python version
python --version

# Verify virtual environmen
which python

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.tx

# Check for conflicts
pip check
```

**Testing Framework Issues**
```bash
# Clear pytest cache
pytest --cache-clear

# Run with debug output
pytest -v --tb=long

# Check test discovery
pytest --collect-only

# Run single test file
pytest tests/unit/test_memory.py -v
```

#### **Debugging Tools**

**Python Debugging**
```python
# Add debug breakpoints
import pdb; pdb.set_trace()

# Use ipdb for better debugging
import ipdb; ipdb.set_trace()

# Add logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Performance Debugging**
```bash
# Profile specific functions
python -m cProfile -o profile.stats script.py

# Analyze profile results
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"

# Memory profiling
python -m memory_profiler script.py
```

### **📈 Monitoring & Reporting**

#### **Test Execution Monitoring**

**Real-time Monitoring**
```bash
# Run tests with live output
pytest -v --tb=shor

# Monitor test progress
pytest --durations=10

# Track test execution time
pytest --durations=0
```

**Test Results Reporting**
```bash
# Generate HTML coverage repor
pytest --cov=src --cov-report=html

# Generate XML coverage repor
pytest --cov=src --cov-report=xml

# Generate performance repor
pytest --benchmark-only --benchmark-json=benchmark_results.json
```

#### **Performance Metrics**
- **Test Execution Time**: Total time for test suite execution
- **Memory Usage**: Peak memory consumption during testing
- **CPU Utilization**: CPU usage during test execution
- **Database Performance**: Query execution times and throughpu

### **🔄 Continuous Integration**

#### **GitHub Actions Configuration**
```yaml
name: Testing Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.12]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.tx
        pip install -r requirements-dev.tx

    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

#### **Pre-commit Hooks**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/astral-sh/ruff-pre-commi
    rev: v0.0.270
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

### **🚀 Advanced Testing Features**

#### **Parallel Test Execution**
```bash
# Run tests in parallel
pytest -n auto

# Specify number of processes
pytest -n 4

# Use specific worker type
pytest -n 4 --dist=worksteal
```

#### **Custom Test Markers**
```python
import pytes

@pytest.mark.slow
def test_slow_operation():
    # This test will be marked as slow
    pass

@pytest.mark.integration
def test_integration_feature():
    # This test will be marked as integration
    pass

@pytest.mark.performance
def test_performance_metric():
    # This test will be marked as performance
    pass
```

## ❓ **Questions for You**

1. **What's your tolerance for [specific aspect]?**
2. **What's the most painful aspect of [current situation]?**
3. **What do you actually use regularly?** vs what just sits there?
4. **How [specific] should [approach] be?**
5. **What's the ideal end state?** (metrics, structure, size)
```

#### **Application Guidelines**

##### **When to Apply**
- **Starting new strategic discussions**
- **Presenting complex solutions**
- **Seeking user input** on design decisions
- **Explaining technical concepts** to non-technical stakeholders

##### **How to Apply**
1. **Start with problem definition** (concrete metrics)
2. **Present systematic analysis** (current state)
3. **Propose structured solution** (phased approach)
4. **Ask collaborative questions** (invite input)
5. **Highlight expected benefits** (clear value)

##### **What to Avoid**
- **Jumping straight to implementation** without strategy
- **Making assumptions** about user preferences
- **Over-engineering** solutions
- **Using complex language** when simple works

#### **Success Metrics**

##### **Communication Effectiveness**
- **User engagement** with strategic questions
- **Clarity of understanding** (user asks follow-up questions)
- **Decision-making speed** (faster consensus)
- **Implementation success** (solutions that work)

##### **Pattern Recognition**
- **Consistent formatting** that resonates
- **Repeated successful** communication elements
- **User feedback** on communication style
- **Memory system** integration effectiveness

## 🧹 **Project Maintenance & Cleanup System**

### **🚨 CRITICAL: Automated Maintenance is Essential**

**Why This Matters**: Automated maintenance keeps the project clean, performant, and provides valuable insights about development patterns. Without proper maintenance, cache files accumulate, disk space is wasted, and development performance degrades.

### **Maintenance System Overview**

The maintenance system provides automated cleanup and analysis of Python cache files, temporary files, logs, and other artifacts. It's designed to keep the project clean while capturing valuable insights about development patterns and build artifacts.

#### **Key Features**
- **Intelligent Cache Analysis**: Captures detailed information about Python cache files before deletion
- **Module Activity Tracking**: Identifies which modules are compiled most frequently
- **Lessons Learned Capture**: Saves detailed analysis to JSON files for trend analysis
- **Comprehensive Cleanup**: Handles Python cache, temp files, logs, test artifacts, and monitoring data
- **Automated Scheduling**: Daily, weekly, monthly, and quarterly maintenance schedules

### **Maintenance Scripts**

#### **1. `scripts/maintenance_cleanup.py`**
Main maintenance script with comprehensive cleanup capabilities.

**Usage:**
```bash
# Run specific cleanup tasks
uv run python scripts/maintenance_cleanup.py --python-cache --verbose
uv run python scripts/maintenance_cleanup.py --temp-files --logs
uv run python scripts/maintenance_cleanup.py --full --dry-run

# Clean with custom age thresholds
uv run python scripts/maintenance_cleanup.py --logs --days 14
uv run python scripts/maintenance_cleanup.py --monitoring --days 30
```

**Options:**
- `--python-cache`: Clean Python cache files and directories
- `--temp-files`: Clean temporary files and directories
- `--logs`: Clean old log files (default: 7 days)
- `--test-artifacts`: Clean test artifacts and cache
- `--monitoring`: Clean old monitoring data (default: 30 days)
- `--hypothesis`: Clean Hypothesis cache
- `--database`: Run database maintenance
- `--dry-run`: Show what would be cleaned without actually cleaning
- `--verbose`: Show detailed output
- `--days N`: Set age threshold for log files

#### **2. `scripts/schedule_maintenance.py`**
Schedules and manages automated maintenance tasks.

**Usage:**
```bash
# Install automated maintenance schedule
uv run python scripts/schedule_maintenance.py --install

# Run manual maintenance
uv run python scripts/schedule_maintenance.py --run daily
uv run python scripts/schedule_maintenance.py --run weekly

# Show current schedule
uv run python scripts/schedule_maintenance.py --show

# Create standalone maintenance script
uv run python scripts/schedule_maintenance.py --create-script
```

**Schedule:**
- **Daily** (2 AM): Python cache + temp files
- **Weekly** (Sunday 3 AM): Logs + test artifacts + Hypothesis cache
- **Monthly** (1st 4 AM): Monitoring data + database maintenance
- **Quarterly** (1st 5 AM): Full cleanup

#### **3. `scripts/analyze_cache_trends.py`**
Analyzes cache patterns and trends across multiple cleanup sessions.

**Usage:**
```bash
# Analyze trends
uv run python scripts/analyze_cache_trends.py

# Save trend repor
uv run python scripts/analyze_cache_trends.py --save-repor

# Custom logs directory
uv run python scripts/analyze_cache_trends.py --logs-dir custom_logs
```

### **Cache Analysis Features**

#### **What Gets Analyzed**
- **Cache directories**: Count, size, and location of `__pycache__` directories
- **Python cache files**: Count and distribution of `.pyc`, `.pyo`, `.pyd` files
- **Module activity**: Which modules are compiled most frequently
- **Temporal patterns**: When cache files were created and modified
- **Size patterns**: Largest cache directories and files
- **Development patterns**: Frequency of compilation and cleanup

#### **Analysis Output**
Each cleanup generates a detailed JSON report in `logs/cache_analysis_YYYYMMDD_HHMMSS.json` with:
- **Summary statistics**: Total cache directories, files, and activity
- **Module activity**: Most frequently compiled modules
- **Cache timeline**: Recent cache activity and patterns
- **Lessons learned**: Insights and recommendations
- **Pattern analysis**: Development workflow patterns

#### **Trend Analysis**
The trend analyzer provides insights across multiple cleanup sessions:
- **Cache growth patterns**: How cache usage changes over time
- **Module activity trends**: Which modules are most frequently compiled
- **Cleanup frequency analysis**: How often maintenance runs
- **Development pattern insights**: Understanding of development workflow
- **Optimization recommendations**: Actionable suggestions for improvement

### **Maintenance Benefits**

#### **Performance Benefits**
- **Faster git operations**: Cleaner repository with fewer files
- **Reduced disk usage**: Automatic cleanup of temporary files
- **Better development experience**: Less clutter in project directory
- **Optimized build times**: Clean cache prevents stale compilation issues

#### **Learning Benefits**
- **Development pattern insights**: Understand which modules are most active
- **Build artifact analysis**: Learn about compilation patterns
- **Optimization opportunities**: Identify areas for improvement
- **Historical tracking**: Maintain long-term development data

#### **Maintenance Benefits**
- **Automated cleanup**: No manual intervention required
- **Configurable schedules**: Flexible maintenance timing
- **Safe operation**: Dry-run mode for testing
- **Comprehensive reporting**: Detailed logs and analysis

### **Best Practices**

#### **Recommended Usage**
1. **Start with dry-run**: Always test with `--dry-run` firs
2. **Regular cleanup**: Set up automated daily/weekly schedules
3. **Monitor trends**: Review cache analysis reports periodically
4. **Customize thresholds**: Adjust age thresholds based on project needs
5. **Archive reports**: Keep analysis files for long-term trend analysis

#### **Important Notes**
- **Virtual environment exclusion**: Cache in `.venv` directories is never touched
- **Safe deletion**: Only removes cache files, never source code
- **Backup analysis**: All analysis data is saved before deletion
- **Configurable**: All thresholds and patterns can be customized

### **Integration with Development Workflow**

#### **Pre-commit Integration**
```bash
# Add maintenance check to pre-commit hooks
python3 scripts/maintenance_cleanup.py --python-cache --dry-run
```

#### **CI/CD Integration**
```yaml
# Add to GitHub Actions workflow
- name: Run maintenance cleanup
  run: |
    uv run python scripts/maintenance_cleanup.py --python-cache --temp-files
```

#### **Development Commands**
```bash
# Quick cleanup before developmen
uv run python scripts/maintenance_cleanup.py --python-cache --verbose

# Full cleanup after major changes
uv run python scripts/maintenance_cleanup.py --full --verbose

# Analyze development patterns
uv run python scripts/analyze_cache_trends.py --save-repor
```

### **Troubleshooting**

#### **Common Issues**
- **Permission errors**: Ensure script has write access to logs directory
- **Missing dependencies**: Install required packages with `uv add`
- **Large cache files**: Use `--verbose` to see what's being cleaned
- **Analysis file errors**: Check JSON format of analysis files

#### **Debugging**
- **Use dry-run mode**: Test changes without affecting files
- **Check logs**: Review maintenance logs for errors
- **Verify paths**: Ensure all file paths are correct
- **Test incrementally**: Run specific cleanup tasks individually

## 🛠️ Agent Troubleshooting Language Patterns

<!-- ANCHOR_KEY: agent-troubleshooting-patterns -->
<!-- ANCHOR_PRIORITY: 3 -->
<!-- ROLE_PINS: ["implementer", "coder"] -->

### **TL;DR**
This section captures common language patterns used by AI agents during debugging and troubleshooting sessions. These patterns serve as mental hooks for context retrieval and can be used to improve debugging efficiency and consistency.

### **🔍 Problem Identification Patterns**

#### **Initial Recognition**
- "I can see the issue..."
- "I see the problem..."
- "The issue is..."
- "The problem is..."
- "Looking at the error..."

#### **Persistent Issues**
- "The issue is still there..."
- "The problem keeps persisting..."
- "The issue is still persisting..."
- "This is still not working..."
- "The problem continues..."

#### **Root Cause Analysis**
- "The root cause is..."
- "The underlying issue is..."
- "The real problem is..."
- "This is happening because..."

### **🛠️ Debugging Progression Patterns**

#### **Investigation**
- "Let me check what's happening..."
- "Let me debug this by..."
- "Let me investigate..."
- "Let me examine..."
- "Let me analyze..."

#### **Iterative Fixes**
- "Let me try a different approach..."
- "Let me fix this by..."
- "Let me address this issue..."
- "Let me resolve this..."
- "Let me correct this..."

#### **Testing & Validation**
- "Now let me test..."
- "Let me verify..."
- "Let me check if this works..."
- "Let me validate..."

### **✅ Solution Implementation Patterns**

#### **Successful Resolution**
- "That fixed it..."
- "The issue is resolved..."
- "The problem is solved..."
- "This should work now..."
- "The fix is complete..."

#### **Partial Success**
- "This partially addresses..."
- "This helps with..."
- "This improves..."
- "This reduces the issue..."

#### **Next Steps**
- "The next step is..."
- "Now we need to..."
- "The remaining issue is..."
- "To complete this..."

### **🔄 Debugging Effectiveness Analysis**

#### **Measurement Patterns**
- "Let me measure the effectiveness..."
- "Let me track the debugging progress..."
- "Let me analyze the debugging patterns..."
- "Let me evaluate the solution..."

#### **Learning Patterns**
- "This teaches us..."
- "The key insight is..."
- "The pattern here is..."
- "This suggests that..."

### **📊 Debugging Effectiveness Analysis Framework**

<!-- ANCHOR_KEY: debugging-effectiveness-analysis -->
<!-- ANCHOR_PRIORITY: 2 -->
<!-- ROLE_PINS: ["implementer", "coder"] -->

#### **TL;DR**
Systematic feedback loop to measure and improve the effectiveness of agent troubleshooting patterns, memory system integration, and debugging efficiency over time.

#### **🎯 Key Performance Indicators (KPIs)**

##### **1. Time-Based Metrics**
- **Time to Problem Identification**: How quickly agents recognize issues
- **Time to Root Cause**: Duration from problem identification to understanding cause
- **Time to Resolution**: Total time from first mention to successful fix
- **Iteration Count**: Number of attempts before successful resolution

##### **2. Pattern Effectiveness Metrics**
- **Pattern Recognition Accuracy**: How often we correctly identify debugging sessions
- **Context Retrieval Success**: Percentage of relevant historical context found
- **Pattern Reuse Rate**: How often similar patterns lead to faster resolution
- **Learning Transfer**: Effectiveness of applying patterns across different technologies

##### **3. Memory System Performance**
- **Query Success Rate**: Percentage of successful context retrievals
- **Relevance Score**: How relevant retrieved context is to current problem
- **Context Utilization**: How often retrieved context is actually used
- **Memory Update Frequency**: How often patterns are updated/improved

#### **🔄 Feedback Loop Implementation**

##### **Phase 1: Data Collection**
```python
# Example data structure for tracking debugging sessions
debugging_session = {
    "session_id": "unique_identifier",
    "timestamp": "2024-12-19T10:30:00Z",
    "technology": "bash_scripts",
    "issue_type": "shellcheck_warnings",
    "problem_identification_time": "10:30:15",
    "root_cause_time": "10:32:45",
    "resolution_time": "10:35:20",
    "total_iterations": 3,
    "patterns_used": [
        "I can see the issue...",
        "Let me try a different approach...",
        "Perfect! The script is working correctly..."
    ],
    "context_retrieved": [
        "similar_shellcheck_fix_2024-12-15",
        "bash_variable_assignment_patterns"
    ],
    "context_utilized": True,
    "resolution_success": True
}
```

##### **Phase 2: Analysis & Pattern Recognition**
- **Session Analysis**: Identify successful vs. unsuccessful debugging patterns
- **Pattern Extraction**: Extract reusable patterns from successful sessions
- **Context Mapping**: Map problems to relevant historical context
- **Effectiveness Scoring**: Rate pattern effectiveness based on resolution time

##### **Phase 3: Continuous Improvement**
- **Pattern Updates**: Refine patterns based on effectiveness data
- **Context Enhancement**: Improve context retrieval based on utilization rates
- **Learning Integration**: Apply successful patterns to new problem domains
- **Feedback Integration**: Update memory system with new insights

#### **📈 Measurement Strategy**

##### **Automated Tracking**
```bash
# Track debugging session metrics
uv run python scripts/debugging_effectiveness_tracker.py --session-start
uv run python scripts/debugging_effectiveness_tracker.py --pattern-used "I can see the issue"
uv run python scripts/debugging_effectiveness_tracker.py --session-end --success
```

##### **Weekly Analysis**
- **Pattern Effectiveness Review**: Analyze which patterns lead to faster resolution
- **Context Utilization Analysis**: Identify gaps in context retrieval
- **Learning Transfer Assessment**: Measure pattern effectiveness across technologies
- **Memory System Optimization**: Update context retrieval based on usage patterns

##### **Monthly Optimization**
- **Pattern Library Updates**: Add new effective patterns, remove ineffective ones
- **Context Enhancement**: Improve historical context based on utilization data
- **Training Data Updates**: Update memory system with new successful patterns
- **Performance Benchmarking**: Compare debugging effectiveness over time

## 🔗 Related

- Getting Started: `400_00_getting-started-and-index.md`                  
- Product & Roadmap: `400_12_product-management-and-roadmap.md`           

## 📋 Changelog
- 2025-08-28: Restored consolidated development workflow and standards guide.                                  
- 2025-09-10: Added comprehensive project maintenance and cleanup system documentation.
- 2025-09-11: Added agent troubleshooting language patterns for improved debugging consistency.
