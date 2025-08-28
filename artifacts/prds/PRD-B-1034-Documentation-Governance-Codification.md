# PRD: B-1034 — Documentation Governance Codification: CI-First Enforcement

## 📋 **Project Overview**

**Status**: Proposed
**Priority**: 🔥 Must Have
**Type**: System Architecture / Governance Automation
**Dependencies**: B-1033 (Surgical Documentation Consolidation, must be completed first)
**Estimated Effort**: 4–6 weeks
**Owner**: Daniel Jacobs

## 🎯 **Objective**

Transform the newly consolidated 10-guide documentation canon into a code-enforced governance system. Documentation remains explanatory, but all critical rules (validation, performance, contribution standards, security, consolidation lifecycle) are enforced by CI jobs, pre-commit hooks, and automation scripts.

This ensures:
- **Consistency**: CI is the single source of truth for governance
- **Clarity**: Docs point to automation instead of re-explaining rules
- **Sustainability**: Governance scales without adding bloat

## 🛠️ **Scope**

### **In-Scope**
- Consolidation rules codified into CI pipelines
- Pre-commit enforcement of critical validations
- Automatic drift detection (docs vs. CI)
- Indexing of 10 canonical guides in README.md
- Archive management automation for deprecated guides
- Memory system integration with governance rules
- Map-of-maps (MoM) codebase routing for Cursor AI
- Performance budgets and evaluation harnesses

### **Out-of-Scope**
- Any further doc consolidation (handled in B-1033)
- Major AI framework changes (handled in separate backlog items)

## 📐 **Approach (3 Phases)**

### **Phase 1: CI-First Governance (Week 1-2)**

Convert validation checklists from B-1033 into CI jobs:

**Core CI Jobs:**
- **Smoke test job**: Prove ingest → query works
- **Cross-reference validator**: Auto-fail if broken links or missing guide references
- **Canonical index enforcement**: Fail if README.md index and actual 10 guides diverge
- **Re-enable pre-commit gates** in minimal, stable order (Ruff, mypy, doc validator)
- **Archive bot**: Moves deprecated guides into /600_archives/ with validation

**Memory System Integration:**
- **Memory routing**: Turn 100_cursor-memory-context.md into thin index/map-of-maps
- **RAG/CAG hydration**: Build ≤200-token pins from vector DB instead of doc bodies
- **Memory events**: Capture CI results, evals, vector health as structured events
- **LTST integration**: Link memory events to persistent session storage

### **Phase 2: Metrics & Budgets (Week 3-4)**

Introduce performance budgets in CI:

**Performance Budgets:**
- **Rehydration time < 5s** (LTST memory system)
- **Eval accuracy regression <= 5%** (retrieval quality)
- **Doc canon: index_match=true** and guides.count <= 10
- **Smoke test latency <= 3s** (pgvector + DSPy→RAG pipeline)

**Evaluation System:**
- **Micro-eval runner**: 10–20 Q/A pairs from your own docs
- **Nightly + PR evaluation**: Compute accuracy/recall@k, fail on >5% regression
- **Export metrics JSON artifacts** on each run; trend via dashboard
- **Cache freshness tracking**: CAG confidence and stale cache percentages

**Map-of-Maps (MoM) Implementation:**
- **Module graph extraction**: Who-imports-who relationships
- **Entrypoints mapping**: CLIs, __main__, scripts with hints
- **Risk assessment**: Blast radius scores for code changes
- **Retrieval hooks**: Domain → RAG index → default query mapping
- **Hydration integration**: ≤60-token MoM pin in 200-token hydration bundle

### **Phase 3: Contributor Workflow Automation (Week 5-6)**

PR template enforces:
- **What changed** (explicit change description)
- **Metric impacted** (which budget this affects)
- **Rollback plan** (how to undo if needed)
- **"Lesson learned" entry** (auto-adds to ledger file)

**GitHub Actions Automation:**
- **Auto-label PRs by size** (XS/S/M/L). Block L merges without approval
- **Coverage delta enforced** only on changed files
- **"Lesson learned" entries** auto-tagged and logged
- **MoM diff comments** on PRs showing structural changes

## ✅ **Success Criteria**

- **Docs reduced to 10 canonical guides** and tracked via README.md index
- **All governance rules automated in CI** (no checklist-only rules remain)
- **PRs blocked unless they pass validation, budgets, and contribution checks**
- **Archive system ensures no drift** between active docs and canon
- **Metrics tracked and enforced in CI** (latency, recall, cache)
- **Memory system routes to RAG/CAG** instead of reading doc bodies
- **MoM provides structural routing** for Cursor AI agents

## 📊 **Deliverables**

### **CI Workflows**
- `.github/workflows/validate.yml` - Authoritative validation gates
- `.github/workflows/smoke.yml` - 90-second product truth test
- `.github/workflows/eval.yml` - Retrieval quality micro-evaluation
- `.github/workflows/archive.yml` - Archive management automation
- `.github/workflows/build_code_mom.yml` - Map-of-maps generation

### **Pre-commit Configuration**
- Enhanced `.pre-commit-config.yaml` with active validators
- Documentation coherence validation
- Canonical index enforcement
- Archive denylist checking

### **Evaluation System**
- `eval/evalset.jsonl` - 10-20 Q/A pairs from real docs
- `eval/run_eval.py` - Evaluation runner with budgets
- `scripts/build_hydration.py` - RAG/CAG hydration pin builder
- `scripts/mom_*.py` - Map-of-maps extractors and builders

### **Memory System Integration**
- `100_memory/memory_routes.json` - RAG routing table
- `scripts/mem_emit.py` - Memory event emission
- `artifacts/memory/stream/` - Structured memory events
- `artifacts/code_mom/` - Map-of-maps JSON files

### **Contributor Tools**
- Enhanced PR template with governance sections
- `scripts/canon_vs_disk.py` - README index validation
- `scripts/check_index_denylist.py` - Archive contamination check
- `scripts/check_priming_order.py` - Memory routing consistency

### **Documentation Updates**
- Updated README.md with canonical guide index
- Memory context as router (not encyclopedia)
- Migration log from B-1033 → B-1034 enforcement

## 🚦 **Risks & Mitigation**

### **Flaky Tests**
- **Risk**: CI gates become unreliable and block development
- **Mitigation**: Start soft-fail, flip to hard after 5 consecutive green runs
- **Monitoring**: Quarantine flaky checks nightly, don't block merges

### **Over-gating Velocity**
- **Risk**: Too many gates slow down development
- **Mitigation**: Limit to one budget per PR, focus on high-impact gates
- **Monitoring**: Track PR merge times and adjust gate sensitivity

### **Human Review Pile-up**
- **Risk**: Manual reviews accumulate and stall consolidation
- **Mitigation**: Quarantine flaky checks, automate more validation
- **Monitoring**: Weekly review cycles, auto-advance where safe

### **Memory System Complexity**
- **Risk**: RAG/CAG integration becomes too complex
- **Mitigation**: Start with simple routing, add sophistication incrementally
- **Monitoring**: Measure rehydration time and CAG confidence trends

## 🎯 **Key Insights from ChatGPT Conversation**

### **Governance-by-Code Principles**
1. **Single source of truth = CI**: Docs explain; CI enforces
2. **Small, composable tests > giant end-to-end**: If a check flakes, quarantine it fast
3. **Budgets, not vibes**: Every gate ties to a budget (latency p95, recall@k, token cost)
4. **Progressive hardening**: Start permissive, move to required after 3–7 green runs

### **Memory System Evolution**
1. **Markdown as router, not encyclopedia**: Point to RAG/CAG instead of restating facts
2. **RAG/CAG as source of truth**: Freshness and confidence win by design
3. **Map-of-maps for structural routing**: Help Cursor AI navigate codebase efficiently
4. **Memory events → facts → pins**: Structured memory pipeline with budgets

### **Industry Best Practices**
1. **Policy-as-code**: Embed governance in pipelines, not just documentation
2. **System cards**: Lightly human-readable dashboards of behavior and metrics
3. **Automated risk measurement**: Track metrics and expose via dashboards
4. **Transactive memory systems**: Know who owns what domain, not just that knowledge exists

## 🔧 **Technical Implementation**

### **CI Job Architecture**
```yaml
# .github/workflows/validate.yml
name: Validate
on: [push, pull_request]
jobs:
  fast-gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - name: Install deps
        run: pip install -r requirements.txt
      - name: Ruff + mypy
        run: |
          ruff check .
          ruff format --check .
          mypy src || true  # start soft; flip hard after 3 greens
      - name: Docs validator
        run: python3 scripts/doc_coherence_validator.py --ci
      - name: Canonical index check
        run: python3 scripts/canon_vs_disk.py
      - name: Archive denylist check
        run: python3 scripts/check_index_denylist.py
```

### **Smoke Test Implementation**
```yaml
# .github/workflows/smoke.yml
name: Smoke
on: [push, pull_request]
jobs:
  e2e-smoke:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: ankane/pgvector:latest
        env:
          POSTGRES_PASSWORD: postgres
        ports: ["5432:5432"]
        options: >-
          --health-cmd="pg_isready -U postgres"
          --health-interval=5s --health-timeout=5s --health-retries=10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - name: Install deps
        run: pip install -r requirements.txt
      - name: Setup schema
        run: psql postgresql://postgres:postgres@localhost:5432/postgres -f dspy-rag-system/config/database/schema.sql
      - name: Smoke test
        run: python -m tests.smoke_test --dsn postgresql://postgres:postgres@localhost:5432/postgres --budget_ms 3000
```

### **Memory Routing Structure**
```json
// 100_memory/memory_routes.json
{
  "priorities":  { "index": "backlog_v1",  "query": "current sprint; top 5 B- items; dependencies" },
  "architecture":{ "index": "system_v1",   "query": "macro architecture; critical components; responsibilities" },
  "changes":     { "index": "changes_v1",  "query": "last 7 days merges; high-impact; affected modules" },
  "ops":         { "index": "ops_v1",      "query": "rollback, migration, smoke; 10-step quick path" },
  "metrics":     { "index": "metrics_v1",  "query": "eval acc/MRR; p95 latency; rehydrate_ms; CAG confidence" }
}
```

### **Map-of-Maps Schema**
```json
// artifacts/code_mom/modules.json
[
  {
    "module": "dspy_rag_system.src.core",
    "file": "dspy-rag-system/src/core/__init__.py",
    "package": "dspy_rag_system.src",
    "kind": "core",
    "owner": "owner:default",
    "public_api": ["RAGSystem", "VectorStore", "MemoryManager"],
    "summary": "Core RAG system components for document processing and retrieval"
  }
]
```

## 📈 **Success Metrics**

### **Governance Effectiveness**
- **Zero governance drift**: README index always matches filesystem
- **Archive contamination**: 0 files from archives in active indices
- **Consolidation compliance**: All new docs follow 10-guide canon

### **Performance Budgets**
- **Rehydration time**: <5s (target), <3s (stretch)
- **Eval accuracy**: >0.70 baseline, <5% regression tolerance
- **Smoke test latency**: <3s (target), <2s (stretch)
- **Cache freshness**: >0.85 confidence, <10% stale cache

### **Developer Experience**
- **PR merge time**: <30 minutes for compliant PRs
- **Gate reliability**: >95% pass rate for non-flaky gates
- **Memory effectiveness**: <200-token hydration pins, >0.90 relevance

## 🎯 **Next Steps**

1. **Complete B-1033**: Ensure 10-guide consolidation is finished
2. **Phase 1 Implementation**: Build core CI jobs and memory routing
3. **Phase 2 Implementation**: Add performance budgets and MoM system
4. **Phase 3 Implementation**: Automate contributor workflows
5. **Validation & Rollout**: Test with real PRs, flip gates from warn→fail

## 📚 **References**

- **B-1033**: Surgical Documentation Consolidation (prerequisite)
- **B-1032**: Documentation t-t3 Authority Structure (foundation)
- **ChatGPT Conversation**: Governance-by-code insights and industry practices
- **Memory System**: LTST, CAG, and hydration patterns
- **CI/CD Best Practices**: Progressive hardening and budget enforcement

---

*This PRD captures the transition from governance-by-documentation to governance-by-code, incorporating insights from industry practices and ChatGPT's recommendations for sustainable, automated governance systems.*
