# Task Generation: B-1059 - Retrieval Tuning Protocol & Evaluation Framework

## 📋 **Task Generation Stub**

### **Backlog Item**: B-1059
### **PRD Source**: [PRD_B-1059_retrieval-tuning-protocol.md](PRD_B-1059_retrieval-tuning-protocol.md)
### **Status**: 🔄 **Ready for Task Generation**
### **Priority**: 🔥 **HIGHEST**

---

## 🎯 **PRD Summary for Task Generation**

### **Core Objective**
Implement industry-grade RAG retrieval tuning protocol with systematic precision/recall optimization, intent-aware routing, hybrid retrieval, and performance gates to transform system from struggling (F1: 0.112) to production-ready performance.

### **Key Deliverables**
- **Hybrid Retrieval System**: BM25 + Vector search with weighted RRF fusion
- **Intent-Aware Routing**: Config, How-to, Status, Multi-hop optimization
- **Evidence-First Answers**: Snippets + file paths before summaries
- **Performance Gates**: Two-green rule with systematic ratcheting
- **Bedrock Integration**: Canonical evaluation framework

### **Evaluation Hygiene & Reproducibility (New)**
- **Cache-off evals**: Hard-fail if generation cache is accessed during evaluation
- **Fixed dataset + seed**: Pin dataset path/split and random seed; store dataset content hash
- **Run artifact isolation**: Write outputs to `metrics/baseline_evaluations/B-1059/<timestamp>/`
- **Config snapshot**: Persist retrieval/rerank/packing config and env (commit, env vars) with a content hash
- **Standard evaluator**: Use RAGChecker v2 (Pydantic + constitution checks) for all runs
- **Alerts/thresholds**: Use PerformanceMonitor thresholds; export JSON summaries for CI

### **Target Metrics**
- **Recall**: 0.099 → 0.35-0.55 (+25-45 pts)
- **F1**: 0.112 → 0.22-0.30 (+10-18 pts)
- **Precision**: Maintain ≥ 0.12
- **Case 11**: 0.0% → 20%+ F1 (config coverage)

---

## 🏗️ **Work Breakdown Structure (WBS) for Task Generation**

### **Epic A — Bedrock Canonicalization**
**Objective**: Establish Bedrock as the canonical evaluation framework
- **A1**: Validate AWS credentials and finalize Bedrock configuration
- **A2**: Update CI job to use Bedrock path and disable fallback for gates
- **A3**: Add troubleshooting log capture and documentation

### **Epic B — Coverage & Indexing**
**Objective**: Expand content coverage to fix Case 11 (0.0% F1)
- **B1**: Implement indexing rules with file globs and chunking strategies
- **B2**: Add docstring extraction for Python files
- **B3**: Re-index repository and validate config lookups

### **Epic C — Hybrid Fusion & Pre-filter**
**Objective**: Implement hybrid retrieval to restore recall funnel
- **C1**: Implement weighted RRF fusion algorithm
- **C2**: Set optimal defaults (BM25_topk=80, Vec_topk=80)
- **C3**: Add recall-friendly pre-filtering

### **Epic D — Reranking & Packing**
**Objective**: Implement precision-focused reranking and evidence-first answers
- **D1**: Implement top-50 reranking with α=0.7 weighting
- **D2**: Add MMR diversity and context capping
- **D3**: Create evidence-first answer composer

### **Epic E — Intent Routing & Policies**
**Objective**: Implement intent-aware optimization for different query types
- **E1**: Build heuristic intent routing system
- **E2**: Add lookup backstop for config queries
- **E3**: Codify evidence-first policy

### **Epic F — Tuning & Gates**
**Objective**: Implement systematic tuning with performance gates
- **F1**: Build coordinate ascent tuning sweeps
- **F2**: Implement two-green ratchet system
- **F3**: Integrate gates with CI and monitoring

### **Epic G — Test Set Hardening**
**Objective**: Improve evaluation quality with hard negatives
- **G1**: Add hard negatives for weak domains
- **G2**: Create near-miss test cases
- **G3**: Validate per-intent performance dashboards

### **Epic H — Documentation & Memory**
**Objective**: Complete documentation and governance integration
- **H1**: Write comprehensive tuning guides
- **H2**: Integrate with memory system
- **H3**: Update Cursor rules for enforcement

---

## ⚙️ **Technical Implementation Details**

### **Hybrid Retrieval Parameters**
- **BM25_topk**: 80 (restore recall)
- **Vector_topk**: 80 (restore recall)
- **RRF fusion**: k=60, λ_lex=0.6, λ_sem=0.4
- **Pre-filter**: cosine < 0.15 AND not in BM25 top-20

### **Reranking Configuration**
- **Input**: Top 50 fused candidates
- **Output**: Top 6-8 selected
- **Weighting**: α=0.7 (rerank) + 0.3 (fused)
- **Tiebreakers**: Exact terms, file proximity, code blocks

### **Performance Gates**
- **Initial**: Precision ≥ 0.12, Recall ≥ 0.15, Faithfulness ≥ 0.60
- **Ratchet Path**: Systematic improvement with two-green rule
- **Target**: Production-ready metrics (F1 ≥ 0.30, Recall ≥ 0.60)

---

## 📊 **Success Criteria for Task Generation**

### **Technical Success**
- All 8 epics broken down into executable tasks
- Clear dependencies and sequencing identified
- Resource estimates and complexity scoring applied
- Integration points with existing systems mapped

### **Task Quality**
- **Actionable**: Each task has clear "what" and "how"
- **Measurable**: Success criteria defined for each task
- **Testable**: Validation steps included
- **Dependencies**: Clear prerequisites and blockers identified

### **Implementation Readiness**
- **Priority ordering**: Critical path identified
- **Resource allocation**: Skills and time requirements estimated
- **Risk mitigation**: Contingency plans for high-risk tasks
- **Integration**: How tasks fit into existing workflows

---

## 🔄 **Task Generation Workflow**

### **Step 1: Epic Analysis**
- Review each epic for complexity and dependencies
- Identify critical path and parallel execution opportunities
- Assess resource requirements and skill sets needed

### **Step 2: Task Breakdown**
- Break each epic into 2-4 executable tasks
- Define clear acceptance criteria for each task
- Estimate complexity and time requirements

### **Step 3: Dependency Mapping**
- Map task dependencies within and across epics
- Identify critical path and potential bottlenecks
- Plan for parallel execution where possible

### **Step 4: Priority Assignment**
- Apply priority scoring based on impact and dependencies
- Identify P0 (critical), P1 (high), P2 (medium) tasks
- Plan for incremental delivery and validation

### **Step 5: Resource Planning**
- Assign skill requirements to each task
- Estimate time and effort requirements
- Identify potential blockers and mitigation strategies

---

## 📝 **Task Generation Template**

### **Task Structure**
```
## Task: [Epic Letter]-[Task Number]: [Descriptive Title]

**Epic**: [Epic Name]
**Priority**: [P0/P1/P2]
**Complexity**: [1-5 points]
**Estimated Time**: [X hours]
**Dependencies**: [Prerequisites]

**Objective**: [What this task accomplishes]

**Acceptance Criteria**:
- [ ] [Specific deliverable 1]
- [ ] [Specific deliverable 2]
- [ ] [Validation step]

**Implementation Steps**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Success Metrics**:
- [Metric 1]: [Target value]
- [Metric 2]: [Target value]

**Risks & Mitigation**:
- **Risk**: [Description]
- **Mitigation**: [Strategy]

**Integration Points**:
- [System/component 1]: [How it integrates]
- [System/component 2]: [How it integrates]
```

---

## 🎯 **Complete Task List for B-1059**

### **Task List: B-1059 — Retrieval Tuning Protocol & Evaluation Framework**

**Overview**: Turn the PRD for B-1059 into an actionable, solo-friendly plan that locks in an industry-grade tuning protocol (hybrid retrieval → fusion → rerank → packing), canonicalizes Bedrock for evals, hardens coverage/indexing, enforces evidence-first answers, and ratchets CI gates with a two-green policy. Structured with MoSCoW and the enhanced task template from your guide.

---

## 📊 **MoSCoW Prioritization Summary**

- **🔥 Must Have**: 16 tasks — critical path (Bedrock, coverage, hybrid fusion, rerank/packing, gates)
- **🎯 Should Have**: 8 tasks — intent routing, docs, dashboards, tuning sweeps
- **⚡ Could Have**: 5 tasks — one-command solo workflow, trend visual polish, extra resilience suites
- **⏸️ Won't Have**: 0 tasks — everything here supports baseline → industry targets

---

## 🚀 **Solo Developer Quick Start**

```bash
# Start a focused session for B-1059
python3 scripts/solo_workflow.py start "B-1059 Retrieval Tuning + Bedrock canonical eval"

# Continue last session
python3 scripts/solo_workflow.py continue

# Run official Bedrock eval and summarize
bash scripts/run_eval_bedrock.sh && python3 scripts/tuning_sweeps.py --summary
```

---

## 📋 **Phase-by-Phase Task Breakdown**

### **Phase 1: Bedrock Canonicalization (P0) — Verification**

#### **A1 — Verify Bedrock canonicalization (already integrated)**
- **Priority**: Critical • MoSCoW: 🔥 Must • Estimated Time: 0.5–1h • Dependencies: —
- **Solo Optimization**: Auto-advance: no, Context preservation: yes
- **Description**: Confirm Bedrock is canonical for evals and functioning without fallback; secrets/configs validated.
- **Acceptance Criteria**:
  - [ ] Official Bedrock path runs locally without fallback (verification)
  - [ ] Region/model IDs validated; secrets not committed
  - [ ] Structured errors present for common failures
- **Testing Requirements**:
  - [ ] Integration: end-to-end eval run using Bedrock-only path
  - [ ] Resilience: network/auth failure simulation
- **Implementation Notes**: Store local secrets in .env/AWS profile; never in repo.
- **Quality Gates**: Code review, Tests passing, Docs updated (docs/bedrock_setup.md), Security reviewed (secrets handling)
- **Solo Workflow Integration**: Auto-Advance: no • Context: yes • One-Command: yes • Smart Pause: yes

#### **A2 — CI: make Bedrock the default evaluator; disable fallback for gates**
- **Priority**: Critical • MoSCoW: 🔥 Must • Estimated Time: 2–3h • Dependencies: A1
- **Description**: Update CI to call the official Bedrock path; allow fallback only for local dev, not gates.
- **Acceptance Criteria**:
  - [ ] CI job uses Bedrock path
  - [ ] Pipeline fails if Bedrock path fails or gates unmet
  - [ ] Artifacts uploaded (JSON/CSV + HTML summary)
- **Testing Requirements**:
  - [ ] Integration: CI run in a test branch
  - [ ] Resilience: Bedrock transient failure → proper retry/backoff
- **Implementation Notes**: Add structured logs; surface gate deltas in CI summary.
- **Quality Gates**: As above
- **Solo Workflow Integration**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

#### **A3 — Eval run script & troubleshooting capture**
- **Priority**: High • MoSCoW: 🎯 Should • Estimated Time: 1–2h • Dependencies: A1
- **Description**: scripts/run_eval_bedrock.sh (and/or scripts/run_eval.py) to wrap the official run and capture logs/exit codes; enforce cache-off eval mode and artifact export.
- **Acceptance Criteria**:
  - [ ] Single command runs full eval
  - [ ] On failure, emits friendly tips and last 200 lines
- **Testing Requirements**:
  - [ ] Integration: non-zero exit on gate failure
  - [ ] Resilience: log truncation & rotation
- **Implementation Notes**: Colorized stderr; timestamped artifacts.
- **Quality Gates**: As above
- **Solo Workflow Integration**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

---

### **Phase 2: Coverage & Indexing (P1)**

#### **B1 — Define indexing rules (globs & chunking)**
- **Priority**: Critical • MoSCoW: 🔥 Must • Estimated Time: 2–3h • Dependencies: —
- **Description**: Create indexing/config_rules.json with includes for .md,.py(docstrings),.yaml/.yml,.toml,.json,.ini,.env.example,.github/workflows/*,Makefile,requirements*.txt,scripts/* and chunk policies (prose/code 350–600 tokens; config 20–40 line blocks).
- **Acceptance Criteria**:
  - [ ] File globs cover config/dev/test/security paths
  - [ ] Chunk policies applied by file type
  - [ ] Exact-identifier matching enabled (preserve case)
- **Testing Requirements**:
  - [ ] Unit: rule parsing & path filtering
  - [ ] Edge: huge files; binary skip; weird encodings
- **Implementation Notes**: Keep rules data-driven for future repos.
- **Quality Gates**: Review/tests/docs updated
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

#### **B2 — Extract Python docstrings & metadata**
- **Priority**: High • MoSCoW: 🎯 Should • Estimated Time: 2h • Dependencies: B1
- **Description**: Index .py docstrings and function/class signatures for troubleshooting/impl queries.
- **Acceptance Criteria**:
  - [ ] Docstrings captured with symbol paths
  - [ ] Signatures searchable (exact match)
- **Testing Requirements**:
  - [ ] Unit: AST extraction
  - [ ] Edge: async defs, decorators, nested classes
- **Implementation Notes**: Use stdlib ast; avoid exec/import.
- **Quality Gates**: Review/tests/docs
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: no • Smart Pause: no

#### **B3 — Re-index & smoke-test coverage**
- **Priority**: Critical • MoSCoW: 🔥 Must • Estimated Time: 1–2h • Dependencies: B1
- **Description**: Rebuild the index; validate that config lookup queries now return candidates.
- **Acceptance Criteria**:
  - [ ] Case 11 no longer returns empty sets
  - [ ] Index size & doc counts logged
- **Testing Requirements**:
  - [ ] Integration: search known keys (e.g., AWS_DEFAULT_REGION)
  - [ ] Performance: index time bounded
- **Implementation Notes**: Keep artifact snapshot for regressions.
- **Quality Gates**: Review/tests
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

---

### **Phase 3: Hybrid Fusion & Pre-filter (P1)**

#### **C1 — Weighted RRF fusion**
- **Priority**: Critical • MoSCoW: 🔥 Must • Estimated Time: 2–3h • Dependencies: B3
- **Description**: Implement src/retrieval/fusion.py with RRF: k=60, λ_lex=0.6, λ_sem=0.4.
- **Acceptance Criteria**:
  - [ ] Fused list reproducible & deterministic
  - [ ] Unit tests for tie-breaks & stability
- **Testing Requirements**:
  - [ ] Unit: rank math, duplicate handling
  - [ ] Integration: recall increase vs. single-mode
- **Implementation Notes**: Keep function pure; no global state.
- **Quality Gates**: Review/tests/perf baseline
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

#### **C2 — Candidate generation defaults**
- **Priority**: Critical • MoSCoW: 🔥 Must • Estimated Time: 1h • Dependencies: C1
- **Description**: Set BM25_topk=80, Vec_topk=80 in config/retrieval.yaml.
- **Acceptance Criteria**:
  - [ ] Configurable via YAML/env
  - [ ] Logged at runtime
- **Testing Requirements**:
  - [ ] Unit: config load/override
  - [ ] Perf: ensure latency acceptable locally
- **Quality Gates**: Review/tests
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

#### **C3 — Recall-friendly pre-filter**
- **Priority**: High • MoSCoW: 🎯 Should • Estimated Time: 1–2h • Dependencies: C1
- **Description**: Keep top-50 fused; drop only if (cosine<0.15 && not BM25 top-20).
- **Acceptance Criteria**:
  - [ ] Recall improves ≥ +0.20 absolute on recent run
  - [ ] Precision remains ≥ 0.12
- **Testing Requirements**:
  - [ ] Integration: before/after candidate counts
  - [ ] Edge: low-cosine exact-term hits retained
- **Quality Gates**: Review/tests/gates
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

---

### **Phase 4: Rerank & Packing (P2)**

#### **D1 — Rerank top-50 → select top-6..8 (α=0.7)**
- **Priority**: Critical • MoSCoW: 🔥 Must • Estimated Time: 3–4h • Dependencies: C1–C3
- **Description**: Implement src/retrieval/rerank.py to call Bedrock reranker, blend 0.7*rerank + 0.3*fused.
- **Acceptance Criteria**:
  - [ ] Precision improves without recall loss
  - [ ] Deterministic selection given fixed seed
- **Testing Requirements**:
  - [ ] Integration: rerank API happy path + timeouts
  - [ ] Resilience: graceful degrade on model error
- **Implementation Notes**: Cache rerank scores per query hash.
- **Quality Gates**: Review/tests/perf/security
- **Solo Workflow**: Auto-Advance: no • Context: yes • One-Command: partial • Smart Pause: yes

#### **D2 — MMR diversity & context cap**
- **Priority**: High • MoSCoW: 🎯 Should • Estimated Time: 2h • Dependencies: D1
- **Description**: Apply MMR (λ=0.7); cap packed context at 1200–1600 tokens.
- **Acceptance Criteria**:
  - [ ] Near-duplicate chunks reduced
  - [ ] Latency stable; answer brevity improved
- **Testing Requirements**:
  - [ ] Unit: MMR selection behavior
  - [ ] Perf: cap enforced under long docs
- **Quality Gates**: Review/tests
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

#### **D3 — Evidence-first answer composer**
- **Priority**: Critical • MoSCoW: 🔥 Must • Estimated Time: 2–3h • Dependencies: D1
- **Description**: Always present top snippet(s) + file path before summary; avoid filler.
- **Acceptance Criteria**:
  - [ ] Faithfulness ≥ 0.60 (global)
  - [ ] Lookup answers include snippet + path
- **Testing Requirements**:
  - [ ] Unit: renderer formatting
  - [ ] Integration: path correctness; snippet bounds
- **Quality Gates**: Review/tests/docs
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

---

### **Phase 5: Intent Routing & Policies (P2)**

#### **E1 — Heuristic intent router**
- **Priority**: High • MoSCoW: 🎯 Should • Estimated Time: 3h • Dependencies: C1–D3
- **Description**: Lightweight regex/keyword router for lookup/config, how-to/troubleshoot, multi-hop.
- **Acceptance Criteria**:
  - [ ] Router accuracy ≥ 80% on labeled eval set
  - [ ] Per-intent knobs applied
- **Testing Requirements**:
  - [ ] Unit: rule coverage tests
  - [ ] Integration: end-to-end per-intent paths
- **Quality Gates**: Review/tests
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

#### **E2 — Lookup backstop & exact-match detection**
- **Priority**: Critical • MoSCoW: 🔥 Must • Estimated Time: 2h • Dependencies: E1
- **Description**: If no exact key/path, fall back to BM25 top-3; require snippet in final answer.
- **Acceptance Criteria**:
  - [ ] Case 11 F1 ≥ 0.20
  - [ ] Zero-answer rate near 0% for lookup queries
- **Testing Requirements**:
  - [ ] Unit: exact-match finder
  - [ ] Edge: keys with punctuation, casing
- **Quality Gates**: Review/tests
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

#### **E3 — Cursor rule updates (policy enforcement)**
- **Priority**: Medium • MoSCoW: 🎯 Should • Estimated Time: 1h • Dependencies: D3
- **Description**: Add rules enforcing evidence-first, context cap, "admit uncertainty."
- **Acceptance Criteria**:
  - [ ] Rules merged; verified in two runs
  - [ ] Violations flagged in CI annotations
- **Testing Requirements**:
  - [ ] Integration: policy checks on sample outputs
- **Quality Gates**: Review/tests/docs
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

---

### **Phase 6: Tuning & Gates (P3)**

#### **F1 — Coordinate-ascent sweeps (scripts/tuning_sweeps.py)**
- **Priority**: High • MoSCoW: 🎯 Should • Estimated Time: 3–4h • Dependencies: C1–D3
- **Description**: Grid sweeps over BM25_topk, Vec_topk, λ_lex/λ_sem, cosine_min, α, top_n; emit CSV + best settings per intent.
- **Acceptance Criteria**:
  - [ ] Reproducible summary with top configs
  - [ ] CLI supports --summary & --apply
- **Testing Requirements**:
  - [ ] Unit: parameter grid integrity
  - [ ] Perf: bounded run time
- **Quality Gates**: Review/tests
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

#### **F2 — Gate configs & two-green ratchet (config/eval_gates.yaml)**
- **Priority**: Critical • MoSCoW: 🔥 Must • Estimated Time: 1–2h • Dependencies: A2
- **Description**: Encode initial gates (Prec≥0.12, Rec≥0.15, Faith≥0.60) and ratchet sequence.
- **Acceptance Criteria**:
  - [ ] CI reads gates from YAML
  - [ ] Two consecutive greens required to ratchet
- **Testing Requirements**:
  - [ ] Unit: parser tests
  - [ ] Integration: simulated runs trigger ratchet
- **Quality Gates**: Review/tests
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

#### **F3 — CI integration for gate deltas & NiceGUI panel**
- **Priority**: Medium • MoSCoW: 🎯 Should • Estimated Time: 2–3h • Dependencies: F2
- **Description**: Surface delta vs. last run; update dashboard trend lines per intent.
- **Acceptance Criteria**:
  - [ ] CI summary shows ΔPrecision/ΔRecall/ΔF1/ΔFaithfulness
  - [ ] Dashboard displays per-intent trend charts
- **Testing Requirements**:
  - [ ] Integration: artifact parsing & render
- **Quality Gates**: Review/tests/docs
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

---

### **Phase 7: Test Set Hardening (P3)**

#### **G1 — Add hard negatives per weak domain**
- **Priority**: Critical • MoSCoW: 🔥 Must • Estimated Time: 3h • Dependencies: B1–B3
- **Description**: For config/dev/test/security & DSPy impl, add near-miss distractors (same file wrong section; sibling file with similar terms).
- **Acceptance Criteria**:
  - [ ] Each weak domain +2 new cases
  - [ ] False-positive rate measurable and reduced post-tuning
- **Testing Requirements**:
  - [ ] Integration: eval runs show discrimination
- **Quality Gates**: Review/tests/docs
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: no • Smart Pause: no

#### **G2 — Add multi-hop chains & labels**
- **Priority**: High • MoSCoW: 🎯 Should • Estimated Time: 2h • Dependencies: E1
- **Description**: Label intents; ensure multi-hop tasks span ≥2 files.
- **Acceptance Criteria**:
  - [ ] R@50 measured on multi-hop subset
  - [ ] No hallucinated edges in answers
- **Testing Requirements**:
  - [ ] Integration: chain correctness checks
- **Quality Gates**: Review/tests
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: no • Smart Pause: no

---

### **Phase 8: Documentation, Memory & Governance (P4)**

#### **H1 — Write "Retrieval Tuning Recipe" guide**
- **Priority**: High • MoSCoW: 🎯 Should • Estimated Time: 2–3h • Dependencies: D1–F1
- **Description**: docs/guide_retrieval_tuning.md with trade-offs, knobs, and playbooks.
- **Acceptance Criteria**:
  - [ ] Complete with examples & defaults
  - [ ] Linked from docs index
- **Testing Requirements**:
  - [ ] Docs lint/links pass
- **Quality Gates**: Review/docs
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

#### **H2 — Evaluation methodology & gates doc**
- **Priority**: Medium • MoSCoW: 🎯 Should • Estimated Time: 2h • Dependencies: F2
- **Description**: docs/eval_methodology.md explaining metrics, gates, ratchets.
- **Acceptance Criteria**:
  - [ ] Matches YAML gates
  - [ ] Includes "two-green" rule
- **Testing Requirements**:
  - [ ] Docs lint
- **Quality Gates**: Review/docs
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

#### **H3 — Memory entries + Cursor rules**
- **Priority**: High • MoSCoW: 🎯 Should • Estimated Time: 1–2h • Dependencies: D3, E3
- **Description**: Save long-term facts (recipe, evidence policy, Bedrock canonical) and enforce via Cursor rules.
- **Acceptance Criteria**:
  - [ ] Memory updated; tags applied
  - [ ] Cursor rules live & tested
- **Testing Requirements**:
  - [ ] Policy check unit tests
- **Quality Gates**: Review/tests/docs
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

#### **H4 — Bedrock setup doc**
- **Priority**: Medium • MoSCoW: 🎯 Should • Estimated Time: 1–2h • Dependencies: A1
- **Description**: docs/bedrock_setup.md with troubleshooting section.
- **Acceptance Criteria**:
  - [ ] Verified by a clean-room run
  - [ ] All env vars and permissions documented
- **Testing Requirements**:
  - [ ] Docs lint
- **Quality Gates**: Review/docs
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

---

### **Phase 9: Observability & Solo Workflow (P4 / optional)**

#### **I1 — Export metrics & summaries**
- **Priority**: Medium • MoSCoW: 🎯 Should • Estimated Time: 1h • Dependencies: A2
- **Description**: Persist metrics/last_eval_summary.json plus CSVs for trends.
- **Acceptance Criteria**:
  - [ ] Files generated each run
  - [ ] Schema stable & documented
- **Testing Requirements**:
  - [ ] Unit: writer + schema; Integration: CI artifacts
- **Quality Gates**: Review/tests
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

#### **I2 — NiceGUI trend panel (per-intent)**
- **Priority**: Low • MoSCoW: ⚡ Could • Estimated Time: 2–3h • Dependencies: I1
- **Description**: Charts for Precision/Recall/F1/Faithfulness + P@5/NDCG@10 by intent.
- **Acceptance Criteria**:
  - [ ] Loads latest artifacts
  - [ ] Clear Δ vs. previous run
- **Testing Requirements**:
  - [ ] Integration: artifact load; visual smoke tests
- **Quality Gates**: Review/tests
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

#### **I3 — One-command solo workflows (optional)**
- **Priority**: Low • MoSCoW: ⚡ Could • Estimated Time: 2–3h • Dependencies: A3, F1
- **Description**: Wire scripts/solo_workflow.py to run sweeps, apply best knobs, and trigger eval + dashboard update.
- **Acceptance Criteria**:
  - [ ] start/continue/ship UX works end-to-end
  - [ ] Context preserved across sessions
- **Testing Requirements**:
  - [ ] Integration: dry-run & real-run paths
- **Quality Gates**: Review/tests/docs
- **Solo Workflow**: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: yes

---

## 📊 **Quality Metrics (for this initiative)**

- **Test Coverage Target**: ≥ 80% for retrieval/rerank/packing modules
- **Performance**: Local eval completes ≤ 5 min; rerank latency ≤ 300 ms per query (p95)
- **Security**: No secrets in repo; least-privilege AWS permissions
- **Reliability**: CI flake rate < 2% over 10 consecutive runs
- **Solo Optimization**: One-command paths for eval and sweeps; context preserved

---

## 🚨 **Risk Mitigation**

- **Latency creep**: keep rerank_top_n ≤ 8; lower Vec_topk before BM25_topk if needed
- **Overfitting to reranker**: retain 0.3 fused weight; validate on per-intent metrics
- **Gate thrash**: enforce two-green rule; ratchet slowly
- **Coverage drift**: keep indexing/config_rules.json versioned; add smoke tests

---

## 🎯 **Ready for Implementation**

This complete task list provides everything needed to implement B-1059:

- **29 detailed tasks** across 9 phases with clear dependencies
- **MoSCoW prioritization** ensuring critical path is addressed first
- **Solo workflow integration** with auto-advance and context preservation
- **Quality gates and testing requirements** for each task
- **Risk mitigation strategies** and performance targets

**Ready to begin implementation starting with Phase 1 (Bedrock Canonicalization)!**

---

*Task Generation Stub Created: September 1, 2025*
*Status: Ready for Task Generation*
*Backlog Item: B-1059*
*Priority: 🔥 HIGHEST*



Task List: B-1059 — Retrieval Tuning Protocol & Evaluation Framework
Overview

Turn the PRD for B-1059 into an actionable, solo-friendly plan that locks in an industry-grade tuning protocol (hybrid retrieval → fusion → rerank → packing), canonicalizes Bedrock for evals, hardens coverage/indexing, enforces evidence-first answers, and ratchets CI gates with a two-green policy. Structured with MoSCoW and the enhanced task template from your guide.

MoSCoW Prioritization Summary

🔥 Must Have: 16 tasks — critical path (Bedrock, coverage, hybrid fusion, rerank/packing, gates)

🎯 Should Have: 8 tasks — intent routing, docs, dashboards, tuning sweeps

⚡ Could Have: 5 tasks — one-command solo workflow, trend visual polish, extra resilience suites

⏸️ Won’t Have: 0 tasks — everything here supports baseline → industry targets

Solo Developer Quick Start
# Start a focused session for B-1059
python3 scripts/solo_workflow.py start "B-1059 Retrieval Tuning + Bedrock canonical eval"

# Continue last session
python3 scripts/solo_workflow.py continue

# Run official Bedrock eval and summarize
bash scripts/run_eval_bedrock.sh && python3 scripts/tuning_sweeps.py --summary

Phase 1: Bedrock Canonicalization (P0)
A1 — Finalize Bedrock credentials & config

Priority: Critical • MoSCoW: 🔥 Must • Estimated Time: 1–2h • Dependencies: —
Solo Optimization: Auto-advance: no, Context preservation: yes
Description: Validate AWS credentials, region, and config/bedrock_config.yaml.
Acceptance Criteria:

 Official Bedrock path runs locally without fallback

 Region/model IDs validated; secrets not committed

 Failure modes logged with actionable messages
Testing Requirements:

 Unit: config loader validation

 Integration: end-to-end eval run using Bedrock

 Resilience: network/auth failure simulation
Implementation Notes: Store local secrets in .env/AWS profile; never in repo.
Quality Gates:

 Code review • [ ] Tests passing • [ ] Docs updated (docs/bedrock_setup.md)

 Security reviewed (secrets handling) • [ ] Performance validated
Solo Workflow Integration: Auto-Advance: no • Context: yes • One-Command: yes • Smart Pause: yes

A2 — CI: make Bedrock the default evaluator; disable fallback for gates

Priority: Critical • MoSCoW: 🔥 Must • Estimated Time: 2–3h • Dependencies: A1
Description: Update CI to call the official Bedrock path; allow fallback only for local dev, not gates.
Acceptance Criteria:

 CI job uses Bedrock path

 Pipeline fails if Bedrock path fails or gates unmet

 Artifacts uploaded (JSON/CSV + HTML summary)
Testing Requirements:

 Integration: CI run in a test branch

 Resilience: Bedrock transient failure → proper retry/backoff
Implementation Notes: Add structured logs; surface gate deltas in CI summary.
Quality Gates: As above
Solo Workflow Integration: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

A3 — Eval run script & troubleshooting capture

Priority: High • MoSCoW: 🎯 Should • Estimated Time: 1–2h • Dependencies: A1
Description: scripts/run_eval_bedrock.sh to wrap the official run and capture logs/exit codes.
Acceptance Criteria:

 Single command runs full eval

 On failure, emits friendly tips and last 200 lines
Testing Requirements:

 Integration: non-zero exit on gate failure

 Resilience: log truncation & rotation
Implementation Notes: Colorized stderr; timestamped artifacts.
Quality Gates: As above
Solo Workflow Integration: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

Phase 2: Coverage & Indexing (P1)
B1 — Define indexing rules (globs & chunking)

Priority: Critical • MoSCoW: 🔥 Must • Estimated Time: 2–3h • Dependencies: —
Description: Create indexing/config_rules.json with includes for .md,.py(docstrings),.yaml/.yml,.toml,.json,.ini,.env.example,.github/workflows/*,Makefile,requirements*.txt,scripts/* and chunk policies (prose/code 350–600 tokens; config 20–40 line blocks).
Acceptance Criteria:

 File globs cover config/dev/test/security paths

 Chunk policies applied by file type

 Exact-identifier matching enabled (preserve case)
Testing Requirements:

 Unit: rule parsing & path filtering

 Edge: huge files; binary skip; weird encodings
Implementation Notes: Keep rules data-driven for future repos.
Quality Gates: Review/tests/docs updated
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

B2 — Extract Python docstrings & metadata

Priority: High • MoSCoW: 🎯 Should • Estimated Time: 2h • Dependencies: B1
Description: Index .py docstrings and function/class signatures for troubleshooting/impl queries.
Acceptance Criteria:

 Docstrings captured with symbol paths

 Signatures searchable (exact match)
Testing Requirements:

 Unit: AST extraction

 Edge: async defs, decorators, nested classes
Implementation Notes: Use stdlib ast; avoid exec/import.
Quality Gates: Review/tests/docs
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: no • Smart Pause: no

B3 — Re-index & smoke-test coverage

Priority: Critical • MoSCoW: 🔥 Must • Estimated Time: 1–2h • Dependencies: B1
Description: Rebuild the index; validate that config lookup queries now return candidates.
Acceptance Criteria:

 Case 11 no longer returns empty sets

 Index size & doc counts logged
Testing Requirements:

 Integration: search known keys (e.g., AWS_DEFAULT_REGION)

 Performance: index time bounded
Implementation Notes: Keep artifact snapshot for regressions.
Quality Gates: Review/tests
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

Phase 3: Hybrid Fusion & Pre-filter (P1)
C1 — Weighted RRF fusion

Priority: Critical • MoSCoW: 🔥 Must • Estimated Time: 2–3h • Dependencies: B3
Description: Implement src/retrieval/fusion.py with RRF: k=60, λ_lex=0.6, λ_sem=0.4.
Acceptance Criteria:

 Fused list reproducible & deterministic

 Unit tests for tie-breaks & stability
Testing Requirements:

 Unit: rank math, duplicate handling

 Integration: recall increase vs. single-mode
Implementation Notes: Keep function pure; no global state.
Quality Gates: Review/tests/perf baseline
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

C2 — Candidate generation defaults

Priority: Critical • MoSCoW: 🔥 Must • Estimated Time: 1h • Dependencies: C1
Description: Set BM25_topk=80, Vec_topk=80 in config/retrieval.yaml.
Acceptance Criteria:

 Configurable via YAML/env

 Logged at runtime
Testing Requirements:

 Unit: config load/override

 Perf: ensure latency acceptable locally
Quality Gates: Review/tests
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

C3 — Recall-friendly pre-filter

Priority: High • MoSCoW: 🎯 Should • Estimated Time: 1–2h • Dependencies: C1
Description: Keep top-50 fused; drop only if (cosine<0.15 && not BM25 top-20).
Acceptance Criteria:

 Recall improves ≥ +0.20 absolute on recent run

 Precision remains ≥ 0.12
Testing Requirements:

 Integration: before/after candidate counts

 Edge: low-cosine exact-term hits retained
Quality Gates: Review/tests/gates
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

Phase 4: Rerank & Packing (P2)
D1 — Rerank top-50 → select top-6..8 (α=0.7)

Priority: Critical • MoSCoW: 🔥 Must • Estimated Time: 3–4h • Dependencies: C1–C3
Description: Implement src/retrieval/rerank.py to call Bedrock reranker, blend 0.7*rerank + 0.3*fused.
Acceptance Criteria:

 Precision improves without recall loss

 Deterministic selection given fixed seed
Testing Requirements:

 Integration: rerank API happy path + timeouts

 Resilience: graceful degrade on model error
Implementation Notes: Cache rerank scores per query hash.
Quality Gates: Review/tests/perf/security
Solo Workflow: Auto-Advance: no • Context: yes • One-Command: partial • Smart Pause: yes

D2 — MMR diversity & context cap

Priority: High • MoSCoW: 🎯 Should • Estimated Time: 2h • Dependencies: D1
Description: Apply MMR (λ=0.7); cap packed context at 1200–1600 tokens.
Acceptance Criteria:

 Near-duplicate chunks reduced

 Latency stable; answer brevity improved
Testing Requirements:

 Unit: MMR selection behavior

 Perf: cap enforced under long docs
Quality Gates: Review/tests
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

D3 — Evidence-first answer composer

Priority: Critical • MoSCoW: 🔥 Must • Estimated Time: 2–3h • Dependencies: D1
Description: Always present top snippet(s) + file path before summary; avoid filler.
Acceptance Criteria:

 Faithfulness ≥ 0.60 (global)

 Lookup answers include snippet + path
Testing Requirements:

 Unit: renderer formatting

 Integration: path correctness; snippet bounds
Quality Gates: Review/tests/docs
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

Phase 5: Intent Routing & Policies (P2)
E1 — Heuristic intent router

Priority: High • MoSCoW: 🎯 Should • Estimated Time: 3h • Dependencies: C1–D3
Description: Lightweight regex/keyword router for lookup/config, how-to/troubleshoot, multi-hop.
Acceptance Criteria:

 Router accuracy ≥ 80% on labeled eval set

 Per-intent knobs applied
Testing Requirements:

 Unit: rule coverage tests

 Integration: end-to-end per-intent paths
Quality Gates: Review/tests
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

E2 — Lookup backstop & exact-match detection

Priority: Critical • MoSCoW: 🔥 Must • Estimated Time: 2h • Dependencies: E1
Description: If no exact key/path, fall back to BM25 top-3; require snippet in final answer.
Acceptance Criteria:

 Case 11 F1 ≥ 0.20

 Zero-answer rate near 0% for lookup queries
Testing Requirements:

 Unit: exact-match finder

 Edge: keys with punctuation, casing
Quality Gates: Review/tests
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

E3 — Cursor rule updates (policy enforcement)

Priority: Medium • MoSCoW: 🎯 Should • Estimated Time: 1h • Dependencies: D3
Description: Add rules enforcing evidence-first, context cap, “admit uncertainty.”
Acceptance Criteria:

 Rules merged; verified in two runs

 Violations flagged in CI annotations
Testing Requirements:

 Integration: policy checks on sample outputs
Quality Gates: Review/tests/docs
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

Phase 6: Tuning & Gates (P3)
F1 — Coordinate-ascent sweeps (scripts/tuning_sweeps.py)

Priority: High • MoSCoW: 🎯 Should • Estimated Time: 3–4h • Dependencies: C1–D3
Description: Grid sweeps over BM25_topk, Vec_topk, λ_lex/λ_sem, cosine_min, α, top_n; emit CSV + best settings per intent.
Acceptance Criteria:

 Reproducible summary with top configs

 CLI supports --summary & --apply
Testing Requirements:

 Unit: parameter grid integrity

 Perf: bounded run time
Quality Gates: Review/tests
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

F2 — Gate configs & two-green ratchet (config/eval_gates.yaml)

Priority: Critical • MoSCoW: 🔥 Must • Estimated Time: 1–2h • Dependencies: A2
Description: Encode initial gates (Prec≥0.12, Rec≥0.15, Faith≥0.60) and ratchet sequence.
Acceptance Criteria:

 CI reads gates from YAML

 Two consecutive greens required to ratchet
Testing Requirements:

 Unit: parser tests

 Integration: simulated runs trigger ratchet
Quality Gates: Review/tests
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

F3 — CI integration for gate deltas & NiceGUI panel

Priority: Medium • MoSCoW: 🎯 Should • Estimated Time: 2–3h • Dependencies: F2
Description: Surface delta vs. last run; update dashboard trend lines per intent.
Acceptance Criteria:

 CI summary shows ΔPrecision/ΔRecall/ΔF1/ΔFaithfulness

 Dashboard displays per-intent trend charts
Testing Requirements:

 Integration: artifact parsing & render
Quality Gates: Review/tests/docs
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

Phase 7: Test Set Hardening (P3)
G1 — Add hard negatives per weak domain

Priority: Critical • MoSCoW: 🔥 Must • Estimated Time: 3h • Dependencies: B1–B3
Description: For config/dev/test/security & DSPy impl, add near-miss distractors (same file wrong section; sibling file with similar terms).
Acceptance Criteria:

 Each weak domain +2 new cases

 False-positive rate measurable and reduced post-tuning
Testing Requirements:

 Integration: eval runs show discrimination
Quality Gates: Review/tests/docs
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: no • Smart Pause: no

G2 — Add multi-hop chains & labels

Priority: High • MoSCoW: 🎯 Should • Estimated Time: 2h • Dependencies: E1
Description: Label intents; ensure multi-hop tasks span ≥2 files.
Acceptance Criteria:

 R@50 measured on multi-hop subset

 No hallucinated edges in answers
Testing Requirements:

 Integration: chain correctness checks
Quality Gates: Review/tests
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: no • Smart Pause: no

Phase 8: Documentation, Memory & Governance (P4)
H1 — Write “Retrieval Tuning Recipe” guide

Priority: High • MoSCoW: 🎯 Should • Estimated Time: 2–3h • Dependencies: D1–F1
Description: docs/guide_retrieval_tuning.md with trade-offs, knobs, and playbooks.
Acceptance Criteria:

 Complete with examples & defaults

 Linked from docs index
Testing Requirements:

 Docs lint/links pass
Quality Gates: Review/docs
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

H2 — Evaluation methodology & gates doc

Priority: Medium • MoSCoW: 🎯 Should • Estimated Time: 2h • Dependencies: F2
Description: docs/eval_methodology.md explaining metrics, gates, ratchets.
Acceptance Criteria:

 Matches YAML gates

 Includes “two-green” rule
Testing Requirements:

 Docs lint
Quality Gates: Review/docs
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

H3 — Memory entries + Cursor rules

Priority: High • MoSCoW: 🎯 Should • Estimated Time: 1–2h • Dependencies: D3, E3
Description: Save long-term facts (recipe, evidence policy, Bedrock canonical) and enforce via Cursor rules.
Acceptance Criteria:

 Memory updated; tags applied

 Cursor rules live & tested
Testing Requirements:

 Policy check unit tests
Quality Gates: Review/tests/docs
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

H4 — Bedrock setup doc

Priority: Medium • MoSCoW: 🎯 Should • Estimated Time: 1–2h • Dependencies: A1
Description: docs/bedrock_setup.md with troubleshooting section.
Acceptance Criteria:

 Verified by a clean-room run

 All env vars and permissions documented
Testing Requirements:

 Docs lint
Quality Gates: Review/docs
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

Phase 9: Observability & Solo Workflow (P4 / optional)
I1 — Export metrics & summaries

Priority: Medium • MoSCoW: 🎯 Should • Estimated Time: 1h • Dependencies: A2
Description: Persist metrics/last_eval_summary.json plus CSVs for trends.
Acceptance Criteria:

 Files generated each run

 Schema stable & documented
Testing Requirements:

 Unit: writer + schema; Integration: CI artifacts
Quality Gates: Review/tests
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

I2 — NiceGUI trend panel (per-intent)

Priority: Low • MoSCoW: ⚡ Could • Estimated Time: 2–3h • Dependencies: I1
Description: Charts for Precision/Recall/F1/Faithfulness + P@5/NDCG@10 by intent.
Acceptance Criteria:

 Loads latest artifacts

 Clear Δ vs. previous run
Testing Requirements:

 Integration: artifact load; visual smoke tests
Quality Gates: Review/tests
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: no

I3 — One-command solo workflows (optional)

Priority: Low • MoSCoW: ⚡ Could • Estimated Time: 2–3h • Dependencies: A3, F1
Description: Wire scripts/solo_workflow.py to run sweeps, apply best knobs, and trigger eval + dashboard update.
Acceptance Criteria:

 start/continue/ship UX works end-to-end

 Context preserved across sessions
Testing Requirements:

 Integration: dry-run & real-run paths
Quality Gates: Review/tests/docs
Solo Workflow: Auto-Advance: yes • Context: yes • One-Command: yes • Smart Pause: yes

Quality Metrics (for this initiative)

Test Coverage Target: ≥ 80% for retrieval/rerank/packing modules

Performance: Local eval completes ≤ 5 min; rerank latency ≤ 300 ms per query (p95)

Security: No secrets in repo; least-privilege AWS permissions

Reliability: CI flake rate < 2% over 10 consecutive runs

Solo Optimization: One-command paths for eval and sweeps; context preserved

Risk Mitigation

Latency creep: keep rerank_top_n ≤ 8; lower Vec_topk before BM25_topk if needed

Overfitting to reranker: retain 0.3 fused weight; validate on per-intent metrics

Gate thrash: enforce two-green rule; ratchet slowly

Coverage drift: keep indexing/config_rules.json versioned; add smoke tests
