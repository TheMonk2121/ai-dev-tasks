# Process Tasks List: B-1059 — Retrieval Tuning Protocol & Evaluation Framework

## 📋 **Task List Overview**

**Backlog Item**: B-1059
**Priority**: 🔥 HIGHEST
**Status**: 🔴 CRITICAL - IMMEDIATE ACTION REQUIRED
**Total Tasks**: 29 tasks across 9 phases
**Estimated Total Time**: 45-60 hours

**Objective**: Transform the RAG system from struggling (F1: 0.112) to production-ready performance through systematic implementation of industry-grade retrieval tuning protocol.

---

## 🎯 **Success Criteria**

- **Recall@20**: 0.099 → 0.35-0.55 (+251% to +455%)
- **Precision@k**: Maintain ≥0.12 (no regression)
- **F1 Score**: 0.112 → 0.22-0.30 (+96% to +168%)
- **Faithfulness**: ≥ 0.60 (global)
- **Case 11 (config)**: F1 ≥ 0.20 (currently failing)
- **All 15 RAGChecker cases**: Above 10% F1

---

## 📊 **Phase-by-Phase Implementation Plan**

### **Phase 1: Bedrock Canonicalization (P0) - Critical Path (Verification)**
**Estimated Time**: 4-7 hours
**Dependencies**: None
**Success Gate**: Bedrock evaluation running without fallback

#### **Task A1: Verify Bedrock canonicalization (already integrated)**
- **Status**: 🔴 Not Started
- **Priority**: Critical
- **Estimated Time**: 0.5-1h
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] Official Bedrock path runs locally without fallback (verification)
  - [ ] Region/model IDs validated; secrets not committed
  - [ ] Structured errors logged with actionable messages
- **Implementation Steps**:
  1. Validate AWS credentials and region configuration
  2. Confirm config/bedrock_config.yaml is present and correct
  3. Run an eval via official Bedrock-only path
  4. Verify structured error handling and logging
- **Quality Gates**: Code review, Tests passing, Security reviewed
- **Solo Workflow**: Auto-Advance: no, Context preservation: yes

#### **Task A2: CI: make Bedrock the default evaluator; disable fallback for gates**
- **Status**: 🔴 Not Started
- **Priority**: Critical
- **Estimated Time**: 2-3h
- **Dependencies**: A1
- **Acceptance Criteria**:
  - [ ] CI job uses Bedrock path
  - [ ] Pipeline fails if Bedrock path fails or gates unmet
  - [ ] Artifacts uploaded (JSON/CSV + HTML summary)
- **Implementation Steps**:
  1. Update CI configuration to use Bedrock path
  2. Implement fallback disable for production gates
  3. Add structured logging and artifact upload
  4. Test CI pipeline with Bedrock integration
- **Quality Gates**: Integration tests, CI validation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

#### **Task A3: Eval run script & troubleshooting capture**
- **Status**: 🔴 Not Started
- **Priority**: High
- **Estimated Time**: 1-2h
- **Dependencies**: A1
- **Acceptance Criteria**:
  - [ ] Single command runs full eval
  - [ ] On failure, emits friendly tips and last 200 lines
- **Implementation Steps**:
  1. Create scripts/run_eval_bedrock.sh (and/or scripts/run_eval.py) wrapper
  2. Enforce cache-off eval mode; write artifacts to metrics/baseline_evaluations/B-1059/<timestamp>/
  3. Implement log capture and rotation; attach last 200 lines on failure
  4. Add user-friendly error messages and troubleshooting tips
  5. Test error handling scenarios
- **Quality Gates**: Integration tests, User experience validation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

---

### **Phase 2: Coverage & Indexing (P1) - Critical Path**
**Estimated Time**: 5-7 hours
**Dependencies**: None
**Success Gate**: Case 11 no longer returns empty sets

#### **Task B1: Define indexing rules (globs & chunking)**
- **Status**: 🔴 Not Started
- **Priority**: Critical
- **Estimated Time**: 2-3h
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] File globs cover config/dev/test/security paths
  - [ ] Chunk policies applied by file type
  - [ ] Exact-identifier matching enabled (preserve case)
- **Implementation Steps**:
  1. Create indexing/config_rules.json with comprehensive file patterns
  2. Define chunk policies for different file types
  3. Implement exact-identifier matching logic
  4. Test with various file types and edge cases
- **Quality Gates**: Unit tests, Edge case validation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

#### **Task B2: Extract Python docstrings & metadata**
- **Status**: 🔴 Not Started
- **Priority**: High
- **Estimated Time**: 2h
- **Dependencies**: B1
- **Acceptance Criteria**:
  - [ ] Docstrings captured with symbol paths
  - [ ] Signatures searchable (exact match)
- **Implementation Steps**:
  1. Implement AST-based docstring extraction
  2. Capture function/class signatures with full paths
  3. Handle edge cases (async, decorators, nested classes)
  4. Add unit tests for extraction logic
- **Quality Gates**: Unit tests, AST parsing validation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

#### **Task B3: Re-index & smoke-test coverage**
- **Status**: 🔴 Not Started
- **Priority**: Critical
- **Estimated Time**: 1-2h
- **Dependencies**: B1
- **Acceptance Criteria**:
  - [ ] Case 11 no longer returns empty sets
  - [ ] Index size & doc counts logged
- **Implementation Steps**:
  1. Rebuild index with new rules
  2. Validate config lookup queries return candidates
  3. Test known keys (e.g., AWS_DEFAULT_REGION)
  4. Log index statistics and performance metrics
- **Quality Gates**: Integration tests, Performance validation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

---

### **Phase 3: Hybrid Fusion & Pre-filter (P1) - Critical Path**
**Estimated Time**: 4-6 hours
**Dependencies**: B3
**Success Gate**: Recall improves ≥ +0.20 absolute while maintaining precision ≥ 0.12

#### **Task C1: Weighted RRF fusion**
- **Status**: 🔴 Not Started
- **Priority**: Critical
- **Estimated Time**: 2-3h
- **Dependencies**: B3
- **Acceptance Criteria**:
  - [ ] Fused list reproducible & deterministic
  - [ ] Unit tests for tie-breaks & stability
- **Implementation Steps**:
  1. Implement src/retrieval/fusion.py with RRF algorithm
  2. Configure k=60, λ_lex=0.6, λ_sem=0.4
  3. Add unit tests for rank math and duplicate handling
  4. Ensure deterministic behavior with fixed seeds
- **Quality Gates**: Unit tests, Performance baseline
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

#### **Task C2: Candidate generation defaults**
- **Status**: 🔴 Not Started
- **Priority**: Critical
- **Estimated Time**: 1h
- **Dependencies**: C1
- **Acceptance Criteria**:
  - [ ] Configurable via YAML/env
  - [ ] Logged at runtime
- **Implementation Steps**:
  1. Set BM25_topk=80, Vec_topk=80 in config/retrieval.yaml
  2. Implement configuration loading and override logic
  3. Add runtime logging of configuration values
  4. Ensure latency remains acceptable locally
- **Quality Gates**: Unit tests, Performance validation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

#### **Task C3: Recall-friendly pre-filter**
- **Status**: 🔴 Not Started
- **Priority**: High
- **Estimated Time**: 1-2h
- **Dependencies**: C1
- **Acceptance Criteria**:
  - [ ] Recall improves ≥ +0.20 absolute on recent run
  - [ ] Precision remains ≥ 0.12
- **Implementation Steps**:
  1. Implement pre-filter logic: keep top-50 fused
  2. Apply drop rule: only if (cosine<0.15 && not BM25 top-20)
  3. Test before/after candidate counts
  4. Validate edge cases (low-cosine exact-term hits)
- **Quality Gates**: Integration tests, Gate validation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

---

### **Phase 4: Rerank & Packing (P2) - Critical Path**
**Estimated Time**: 7-9 hours
**Dependencies**: C1-C3
**Success Gate**: Precision improves without recall loss, Faithfulness ≥ 0.60

#### **Task D1: Rerank top-50 → select top-6..8 (α=0.7)**
- **Status**: 🔴 Not Started
- **Priority**: Critical
- **Estimated Time**: 3-4h
- **Dependencies**: C1-C3
- **Acceptance Criteria**:
  - [ ] Precision improves without recall loss
  - [ ] Deterministic selection given fixed seed
- **Implementation Steps**:
  1. Implement src/retrieval/rerank.py with Bedrock integration
  2. Configure blending: 0.7*rerank + 0.3*fused
  3. Add caching for rerank scores per query hash
  4. Implement graceful degradation on model errors
- **Quality Gates**: Integration tests, Performance validation, Security review
- **Solo Workflow**: Auto-Advance: no, Context preservation: yes

#### **Task D2: MMR diversity & context cap**
- **Status**: 🔴 Not Started
- **Priority**: High
- **Estimated Time**: 2h
- **Dependencies**: D1
- **Acceptance Criteria**:
  - [ ] Near-duplicate chunks reduced
  - [ ] Latency stable; answer brevity improved
- **Implementation Steps**:
  1. Apply MMR algorithm with λ=0.7
  2. Cap packed context at 1200-1600 tokens
  3. Test MMR selection behavior
  4. Validate performance under long documents
- **Quality Gates**: Unit tests, Performance validation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

#### **Task D3: Evidence-first answer composer**
- **Status**: 🔴 Not Started
- **Priority**: Critical
- **Estimated Time**: 2-3h
- **Dependencies**: D1
- **Acceptance Criteria**:
  - [ ] Faithfulness ≥ 0.60 (global)
  - [ ] Lookup answers include snippet + path
- **Implementation Steps**:
  1. Implement evidence-first rendering logic
  2. Always present top snippet(s) + file path before summary
  3. Avoid filler content and unnecessary text
  4. Add unit tests for renderer formatting
- **Quality Gates**: Unit tests, Integration tests, Documentation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

---

### **Phase 5: Intent Routing & Policies (P2) - High Priority**
**Estimated Time**: 6-8 hours
**Dependencies**: C1-D3
**Success Gate**: Case 11 F1 ≥ 0.20, Router accuracy ≥ 80%

#### **Task E1: Heuristic intent router**
- **Status**: 🔴 Not Started
- **Priority**: High
- **Estimated Time**: 3h
- **Dependencies**: C1-D3
- **Acceptance Criteria**:
  - [ ] Router accuracy ≥ 80% on labeled eval set
  - [ ] Per-intent knobs applied
- **Implementation Steps**:
  1. Implement lightweight regex/keyword router
  2. Support lookup/config, how-to/troubleshoot, multi-hop intents
  3. Add unit tests for rule coverage
  4. Test end-to-end per-intent paths
- **Quality Gates**: Unit tests, Integration tests
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

#### **Task E2: Lookup backstop & exact-match detection**
- **Status**: 🔴 Not Started
- **Priority**: Critical
- **Estimated Time**: 2h
- **Dependencies**: E1
- **Acceptance Criteria**:
  - [ ] Case 11 F1 ≥ 0.20
  - [ ] Zero-answer rate near 0% for lookup queries
- **Implementation Steps**:
  1. Implement exact-match finder with fallback logic
  2. Fall back to BM25 top-3 if no exact key/path
  3. Require snippet in final answer
  4. Handle edge cases (punctuation, casing)
- **Quality Gates**: Unit tests, Edge case validation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

#### **Task E3: Cursor rule updates (policy enforcement)**
- **Status**: 🔴 Not Started
- **Priority**: Medium
- **Estimated Time**: 1h
- **Dependencies**: D3
- **Acceptance Criteria**:
  - [ ] Rules merged; verified in two runs
  - [ ] Violations flagged in CI annotations
- **Implementation Steps**:
  1. Add rules enforcing evidence-first, context cap
  2. Implement "admit uncertainty" policy
  3. Verify rules in two consecutive runs
  4. Add CI annotations for policy violations
- **Quality Gates**: Integration tests, Documentation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

---

### **Phase 6: Tuning & Gates (P3) - High Priority**
**Estimated Time**: 6-8 hours
**Dependencies**: C1-D3, A2
**Success Gate**: CI reads gates from YAML, two-green ratchet working

#### **Task F1: Coordinate-ascent sweeps (scripts/tuning_sweeps.py)**
- **Status**: 🔴 Not Started
- **Priority**: High
- **Estimated Time**: 3-4h
- **Dependencies**: C1-D3
- **Acceptance Criteria**:
  - [ ] Reproducible summary with top configs
  - [ ] CLI supports --summary & --apply
- **Implementation Steps**:
  1. Implement grid sweeps over key parameters
  2. Support BM25_topk, Vec_topk, λ_lex/λ_sem, cosine_min, α, top_n
  3. Emit CSV + best settings per intent
  4. Add CLI with --summary and --apply options
- **Quality Gates**: Unit tests, Performance validation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

#### **Task F2: Gate configs & two-green ratchet (config/eval_gates.yaml)**
- **Status**: 🔴 Not Started
- **Priority**: Critical
- **Estimated Time**: 1-2h
- **Dependencies**: A2
- **Acceptance Criteria**:
  - [ ] CI reads gates from YAML
  - [ ] Two consecutive greens required to ratchet
- **Implementation Steps**:
  1. Encode initial gates (Prec≥0.12, Rec≥0.15, Faith≥0.60)
  2. Implement ratchet sequence logic
  3. Add unit tests for parser
  4. Test simulated runs trigger ratchet
- **Quality Gates**: Unit tests, Integration tests
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

#### **Task F3: CI integration for gate deltas & NiceGUI panel**
- **Status**: 🔴 Not Started
- **Priority**: Medium
- **Estimated Time**: 2-3h
- **Dependencies**: F2
- **Acceptance Criteria**:
  - [ ] CI summary shows ΔPrecision/ΔRecall/ΔF1/ΔFaithfulness
  - [ ] Dashboard displays per-intent trend charts
- **Implementation Steps**:
  1. Surface delta vs. last run in CI
  2. Update dashboard trend lines per intent
  3. Implement artifact parsing and rendering
  4. Add visual smoke tests
- **Quality Gates**: Integration tests, Documentation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

---

### **Phase 7: Test Set Hardening (P3) - High Priority**
**Estimated Time**: 5-7 hours
**Dependencies**: B1-B3, E1
**Success Gate**: Each weak domain +2 new cases, multi-hop chains working

#### **Task G1: Add hard negatives per weak domain**
- **Status**: 🔴 Not Started
- **Priority**: Critical
- **Estimated Time**: 3h
- **Dependencies**: B1-B3
- **Acceptance Criteria**:
  - [ ] Each weak domain +2 new cases
  - [ ] False-positive rate measurable and reduced post-tuning
- **Implementation Steps**:
  1. Identify weak domains: config/dev/test/security & DSPy impl
  2. Add near-miss distractors (same file wrong section, sibling files)
  3. Measure false-positive rate before/after
  4. Validate discrimination in eval runs
- **Quality Gates**: Integration tests, Documentation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

#### **Task G2: Add multi-hop chains & labels**
- **Status**: 🔴 Not Started
- **Priority**: High
- **Estimated Time**: 2h
- **Dependencies**: E1
- **Acceptance Criteria**:
  - [ ] R@50 measured on multi-hop subset
  - [ ] No hallucinated edges in answers
- **Implementation Steps**:
  1. Label intents for multi-hop tasks
  2. Ensure tasks span ≥2 files
  3. Measure R@50 on multi-hop subset
  4. Validate chain correctness
- **Quality Gates**: Integration tests
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

---

### **Phase 8: Documentation, Memory & Governance (P4) - Medium Priority**
**Estimated Time**: 6-8 hours
**Dependencies**: D1-F1, F2, D3, E3, A1
**Success Gate**: All documentation complete, memory updated, Cursor rules live

#### **Task H1: Write "Retrieval Tuning Recipe" guide**
- **Status**: 🔴 Not Started
- **Priority**: High
- **Estimated Time**: 2-3h
- **Dependencies**: D1-F1
- **Acceptance Criteria**:
  - [ ] Complete with examples & defaults
  - [ ] Linked from docs index
- **Implementation Steps**:
  1. Create docs/guide_retrieval_tuning.md
  2. Include trade-offs, knobs, and playbooks
  3. Add examples and default configurations
  4. Link from documentation index
- **Quality Gates**: Documentation review, Link validation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

#### **Task H2: Evaluation methodology & gates doc**
- **Status**: 🔴 Not Started
- **Priority**: Medium
- **Estimated Time**: 2h
- **Dependencies**: F2
- **Acceptance Criteria**:
  - [ ] Matches YAML gates
  - [ ] Includes "two-green" rule
- **Implementation Steps**:
  1. Create docs/eval_methodology.md
  2. Explain metrics, gates, and ratchets
  3. Ensure alignment with YAML configuration
  4. Document the "two-green" rule
- **Quality Gates**: Documentation review
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

#### **Task H3: Memory entries + Cursor rules**
- **Status**: 🔴 Not Started
- **Priority**: High
- **Estimated Time**: 1-2h
- **Dependencies**: D3, E3
- **Acceptance Criteria**:
  - [ ] Memory updated; tags applied
  - [ ] Cursor rules live & tested
- **Implementation Steps**:
  1. Save long-term facts (recipe, evidence policy, Bedrock canonical)
  2. Apply appropriate tags
  3. Enforce via Cursor rules
  4. Test policy check unit tests
- **Quality Gates**: Unit tests, Documentation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

#### **Task H4: Bedrock setup doc**
- **Status**: 🔴 Not Started
- **Priority**: Medium
- **Estimated Time**: 1-2h
- **Dependencies**: A1
- **Acceptance Criteria**:
  - [ ] Verified by a clean-room run
  - [ ] All env vars and permissions documented
- **Implementation Steps**:
  1. Create docs/bedrock_setup.md
  2. Include troubleshooting section
  3. Document all environment variables and permissions
  4. Verify with clean-room setup
- **Quality Gates**: Documentation review, Setup validation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

---

### **Phase 9: Observability & Solo Workflow (P4 / Optional) - Low Priority**
**Estimated Time**: 5-8 hours
**Dependencies**: A2, A3, F1, I1
**Success Gate**: Metrics exported, dashboard working, solo workflow functional

#### **Task I1: Export metrics & summaries**
- **Status**: 🔴 Not Started
- **Priority**: Medium
- **Estimated Time**: 1h
- **Dependencies**: A2
- **Acceptance Criteria**:
  - [ ] Files generated each run
  - [ ] Schema stable & documented
- **Implementation Steps**:
  1. Persist metrics/last_eval_summary.json
  2. Generate CSVs for trends
  3. Ensure stable schema
  4. Document data format
- **Quality Gates**: Unit tests, Integration tests
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

#### **Task I2: NiceGUI trend panel (per-intent)**
- **Status**: 🔴 Not Started
- **Priority**: Low
- **Estimated Time**: 2-3h
- **Dependencies**: I1
- **Acceptance Criteria**:
  - [ ] Loads latest artifacts
  - [ ] Clear Δ vs. previous run
- **Implementation Steps**:
  1. Create charts for Precision/Recall/F1/Faithfulness
  2. Add P@5/NDCG@10 by intent
  3. Load latest artifacts
  4. Show clear delta vs. previous run
- **Quality Gates**: Integration tests, Visual validation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

#### **Task I3: One-command solo workflows (optional)**
- **Status**: 🔴 Not Started
- **Priority**: Low
- **Estimated Time**: 2-3h
- **Dependencies**: A3, F1
- **Acceptance Criteria**:
  - [ ] start/continue/ship UX works end-to-end
  - [ ] Context preserved across sessions
- **Implementation Steps**:
  1. Wire scripts/solo_workflow.py
  2. Support running sweeps, applying best knobs
  3. Trigger eval + dashboard update
  4. Preserve context across sessions
- **Quality Gates**: Integration tests, Documentation
- **Solo Workflow**: Auto-Advance: yes, Context preservation: yes

---

## 🚀 **Implementation Strategy**

### **Critical Path (Must Complete First)**
1. **Phase 1**: Bedrock Canonicalization (4-7h)
2. **Phase 2**: Coverage & Indexing (5-7h)
3. **Phase 3**: Hybrid Fusion & Pre-filter (4-6h)
4. **Phase 4**: Rerank & Packing (7-9h)

### **High Priority (Complete After Critical Path)**
5. **Phase 5**: Intent Routing & Policies (6-8h)
6. **Phase 6**: Tuning & Gates (6-8h)
7. **Phase 7**: Test Set Hardening (5-7h)

### **Medium Priority (Complete After High Priority)**
8. **Phase 8**: Documentation, Memory & Governance (6-8h)

### **Low Priority (Optional, Complete Last)**
9. **Phase 9**: Observability & Solo Workflow (5-8h)

---

## 📊 **Progress Tracking**

### **Phase Completion Status**
- [ ] **Phase 1**: Bedrock Canonicalization (0/3 tasks)
- [ ] **Phase 2**: Coverage & Indexing (0/3 tasks)
- [ ] **Phase 3**: Hybrid Fusion & Pre-filter (0/3 tasks)
- [ ] **Phase 4**: Rerank & Packing (0/3 tasks)
- [ ] **Phase 5**: Intent Routing & Policies (0/3 tasks)
- [ ] **Phase 6**: Tuning & Gates (0/3 tasks)
- [ ] **Phase 7**: Test Set Hardening (0/2 tasks)
- [ ] **Phase 8**: Documentation, Memory & Governance (0/4 tasks)
- [ ] **Phase 9**: Observability & Solo Workflow (0/3 tasks)

### **Overall Progress**
- **Total Tasks**: 29
- **Completed**: 0
- **In Progress**: 0
- **Not Started**: 29
- **Completion Rate**: 0%

---

## 🎯 **Next Actions**

1. **Start with Phase 1, Task A1**: Finalize Bedrock credentials & config
2. **Validate Bedrock connectivity** before proceeding to CI integration
3. **Test indexing improvements** in Phase 2 to validate coverage fixes
4. **Measure baseline metrics** before implementing hybrid fusion
5. **Implement systematic testing** for each phase completion

---

## 📝 **Notes & Dependencies**

- **AWS Credentials**: Ensure proper access to Bedrock services
- **Database**: Verify PostgreSQL connectivity and pgvector extensions
- **Testing Environment**: Set up isolated testing to avoid production impact
- **Documentation**: Keep all guides updated as implementation progresses
- **Quality Gates**: Enforce strict validation before phase advancement

---

**Ready to begin implementation with Phase 1: Bedrock Canonicalization!**

---

## 🚀 **Solo Developer Execution Playbook**

### **🔎 TL;DR**
| what this file is | read when | do next |
|-------------------|-----------|----------|
| Execution playbook to run B-1059 from PRD → working system with auto-advance + smart pausing | You're ready to execute the PRD task list | Run the Quick Start command, then follow phase gates below |

### **🎯 Current Status**

**Backlog ID**: B-1059
**Status**: ACTIVE (execution-ready)
**Priority**: 🔥 Critical
**Owner**: Daniel / Core RAG & Memory
**Inputs**: PRD B-1059 (WBS A–I), latest eval report & gate YAML
**Outputs**: Tuned retrieval stack, Bedrock-canonical evals, ratcheting CI gates, docs & memory updates

### **When to use**

- You have the B-1059 PRD + WBS and want a repeatable process to ship it.
- You're operating as a solo developer and need auto-advance with smart pauses at the right decision points.

### **Execution skip rule**

Skip automation if a step needs external approval or secrets you don't have; switch to Manual Process for that step.

### **Backlog integration**

- **Source of truth**: B-1059 PRD WBS (Epics A–I).
- **Cross-refs**: 000_backlog.md and your evaluation artifacts.

---

## 🚀 **Solo Developer Quick Start**

```bash
# 0) Start an execution session for B-1059
python3 scripts/solo_workflow.py start "B-1059 Retrieval Tuning + Bedrock canonical eval"

# 1) Run current phase with auto-advance & context
python3 scripts/solo_workflow.py execute --prd prd/B-1059.md --auto-advance --context-preserve

# 2) Resume later
python3 scripts/solo_workflow.py continue

# 3) Ship & archive (after final green run + docs)
python3 scripts/solo_workflow.py ship
```

*(If these helpers don't exist yet, they are part of the B-1059 WBS: "Solo workflow" items in Phase 9.)*

---

## 🧭 **Execution Configuration**

- **Auto-Advance**: ON by default
- **Context Preservation**: LTST memory integrates PRD §0 context + prior decisions
- **Smart Pausing**: Triggered only at critical decisions or external deps (see pause points)
- **State File**: .ai_state.json (gitignored); tracks phase, task, artifacts, gates, deltas

### **Artifacts**

- `config/retrieval.yaml`, `config/eval_gates.yaml`
- `metrics/last_eval_summary.json`, `metrics/*.csv`
- `docs/*` (tuning recipe, evaluation methodology, Bedrock setup, evidence-first)

---

## 🛠️ **Process Phases & Tasks (auto-advance with smart pauses)**

Below: each phase lists Tasks (from PRD WBS) → Pause Points → Success Signals → Primary Commands → Artifacts.

### **Phase 1 — Bedrock Canonicalization (WBS A1–A3)**

**Goal**: Make Bedrock the default evaluator; no gate decisions from fallback.

**Tasks**
- A1 Finalize creds/config (config/bedrock_config.yaml)
- A2 CI switches to official Bedrock path; fallback disabled for gates
- A3 run_eval_bedrock.sh wrapper + troubleshooting capture

**Smart pause when**:
- AWS auth/region/model unresolved; CI lacks secret scope.

**Success signals**:
- Local & CI runs use Bedrock; artifacts uploaded; fallback allowed only for local dev.

**Commands**
```bash
bash scripts/run_eval_bedrock.sh
```

**Artifacts**: Updated CI workflow; logs; verified Bedrock setup doc.

---

### **Phase 2 — Coverage & Indexing (WBS B1–B3)**

**Goal**: Close blind spots (config/dev/test/security/docstrings).

**Tasks**
- B1 indexing/config_rules.json (globs + chunk policies)
- B2 Python docstring extraction
- B3 Re-index + smoke tests (e.g., AWS_DEFAULT_REGION, pyproject.toml)

**Smart pause when**:
- Binary/large files cause index bloat; encoding errors require rule tweaks.

**Success signals**:
- Config lookups return candidates; Case-11 no longer zero.

**Artifacts**: Index stats; before/after sample queries.

---

### **Phase 3 — Hybrid Fusion & Pre-filter (WBS C1–C3)**

**Goal**: Restore recall without wrecking precision.

**Tasks**
- C1 Weighted-RRF fusion (k=60, λ_lex=0.6, λ_sem=0.4)
- C2 Defaults: BM25_topk=80, Vec_topk=80
- C3 Recall-friendly pre-filter: keep top-50 fused; drop only if (cos<0.15 && !BM25 top-20)

**Smart pause when**:
- Latency exceeds local budget; candidate counts explode unexpectedly.

**Success signals**:
- ΔRecall ≥ +0.20 abs; Precision ≥ 0.12; F1 improves over prior run.

---

### **Phase 4 — Rerank & Packing (WBS D1–D3)**

**Goal**: Lift precision; keep recall via diversity + caps.

**Tasks**
- D1 Rerank top-50 → select top-6..8; final score 0.7*rerank + 0.3*fused
- D2 MMR (λ=0.7); context cap 1200–1600 tokens
- D3 Evidence-first composer (snippet + filepath, then summary)

**Smart pause when**:
- Rerank model/latency issues; evidence rendering mismatches file spans.

**Success signals**:
- Precision climbs (≥ 0.18–0.24); Faithfulness ≥ 0.60; answers shorter & grounded.

---

### **Phase 5 — Intent Routing & Policies (WBS E1–E3)**

**Goal**: Intent-aware knobs; eliminate "no answer" for lookups.

**Tasks**
- E1 Heuristic router: lookup/config, how-to, multi-hop
- E2 Lookup backstop: BM25 top-3 if no exact match; require snippet
- E3 Cursor rules enforce evidence-first + context cap + "admit uncertainty"

**Smart pause when**:
- Router accuracy <80% on labeled set; backstop floods low-quality hits.

**Success signals**:
- Case-11 ≥ 0.20 F1; zero-answer rate ~0% for lookups; per-intent NDCG/P@5 improve.

---

### **Phase 6 — Tuning & Gates (WBS F1–F3)**

**Goal**: Controlled ratchet using two-green rule.

**Tasks**
- F1 Coordinate-ascent sweeps (BM25/Vec_topk, λ's, cosine_min, α, top_n)
- F2 config/eval_gates.yaml (initial + ratchet sequence)
- F3 CI summary deltas + NiceGUI trend panel

**Smart pause when**:
- Parameter sweeps exceed time budget; gate thrash (flapping).

**Success signals**:
- Two consecutive green runs; Recall → 0.35–0.45, then Precision → 0.20, etc.

**Commands**
```bash
python3 scripts/tuning_sweeps.py --summary
```

---

### **Phase 7 — Test Set Hardening (WBS G1–G2)**

**Goal**: Honest signals via hard negatives and multi-hop labels.

**Tasks**
- G1 +2 hard-negative cases per weak domain
- G2 Multi-hop chains labeled; R@50 tracked

**Smart pause when**:
- New cases cause unexplained collapses → investigate coverage vs thresholds.

**Success signals**:
- Reduced false positives; multi-hop correctness verified.

---

### **Phase 8 — Documentation, Memory & Governance (WBS H1–H4)**

**Goal**: Make it teachable + enforceable (docs, memory, rules).

**Tasks**
- H1 Retrieval Tuning Recipe
- H2 Eval methodology & gates doc
- H3 Memory entries + Cursor rules live
- H4 Bedrock setup doc (clean-room verified)

**Smart pause when**:
- Policy conflicts with current outputs; decide exception vs correction.

**Success signals**:
- Docs reviewed; memory updated; Cursor rules trigger on violations.

---

### **Phase 9 — Observability & Solo Workflow (WBS I1–I3, optional)**

**Goal**: Frictionless solo loop + visible trends.

**Tasks**
- I1 Export metrics/CSV, stable schemas
- I2 Trend panel (per-intent)
- I3 One-command workflow (start|continue|ship)

**Success signals**:
- One-command run covers sweep → eval → dashboard; deltas visible.

---

## ✅ **Quality Gates (check each phase)**

- [ ] **Code Review** (self-review acceptable, checklist-based)
- [ ] **Tests Passing** (unit+integration)
- [ ] **Performance** (local eval ≤ 5 min; rerank p95 ≤ 300 ms)
- [ ] **Security** (no secrets in repo; least privilege)
- [ ] **Docs Updated** (guides + policies)
- [ ] **Resilience** (retry/backoff; clear failure modes)
- [ ] **Edge Cases** (large files, encodings, empty hits)
- [ ] **Gates Met** (two-green rule before ratchet)

---

## 🧩 **PRD → Execution Mapping**

| PRD Section | Execution Use |
|-------------|---------------|
| §0 Context | Seeds LTST context & decisions; drives defaults |
| §1–2 Problem/Solution | Validates scope; prevents gold-plating |
| §4 Technical Approach | Implements hybrid→fusion→rerank→packing |
| §6 Evaluation | Bedrock canonical runs; per-intent metrics |
| §7 Implementation Plan | This phase plan & gates |
| §8 WBS | Concrete tasks A–I above |

---

## 📦 **State & Error Handling**

- **State file**: .ai_state.json — tracks current phase/task, artifacts, deltas, last good knobs.
- **HotFix flow**: detect failure → generate fix task → apply → re-run → resume.
- **Retry logic**: exponential backoff on Bedrock/network; bounded sweep grids.

---

## 🟢 **Runbook: minimal happy path (first pass)**

1. **A1–A3**: Bedrock default in CI → green run
2. **B1–B3**: Index rules + docstrings → smoke tests pass
3. **C1–C3**: wRRF + recall-friendly pre-filter → Recall ≥ 0.35
4. **D1–D3**: Rerank + MMR + evidence-first → Precision ≥ 0.18; Faithfulness ≥ 0.60
5. **E1–E2**: Router + lookup backstop → Case-11 fixed
6. **F1–F2**: Sweeps + initial gates → two greens, ratchet Recall gate
7. **G1–G2**: Hard negatives + multi-hop labels → stable metrics
8. **H1–H4**: Docs + memory + rules → polish
9. **I1–I3**: Trends + one-command loop (optional)

---

## 📈 **Ratchet ladder (apply after two greens, each rung)**

1. Recall ≥ 0.35 (Precision ≥ 0.12)
2. Precision ≥ 0.20 (Recall ≥ 0.45)
3. Recall ≥ 0.60 (Precision ≥ 0.20)
4. Precision ≥ 0.30; Faithfulness ≥ 0.70

---

## 🧪 **Command snippets (reference)**

```bash
# Evaluate (Bedrock canonical)
bash scripts/run_eval_bedrock.sh

# Parameter sweeps
python3 scripts/tuning_sweeps.py --summary

# Re-index
python3 scripts/index_repo.py --rules indexing/config_rules.json
```

*(Wire these as part of WBS if not present yet.)*

---

## 📜 **Special instructions**

- Prefer simple, reversible changes; keep numerics in YAML.
- Use evidence-first answers; show snippet + filepath for lookups.
- Keep rerank influence (α) high only when precision stalls.
- Open the funnel at candidate gen; let rerank do the pruning.
- Enforce two-green before any gate ratchet.
- **Track Δ vs last run (CI summary + dashboard) for every change.**



Process Task List: B-1059 — Retrieval Tuning Protocol & Evaluation Framework

Guided by your process task list template, adapted for solo execution and direct mapping from the B-1059 PRD → WBS.

🔎 TL;DR
what this file is	read when	do next
Execution playbook to run B-1059 from PRD → working system with auto-advance + smart pausing	You’re ready to execute the PRD task list	Run the Quick Start command, then follow phase gates below
🎯 Current Status

Backlog ID: B-1059

Status: ACTIVE (execution-ready)

Priority: 🔥 Critical

Owner: Daniel / Core RAG & Memory

Inputs: PRD B-1059 (WBS A–I), latest eval report & gate YAML

Outputs: Tuned retrieval stack, Bedrock-canonical evals, ratcheting CI gates, docs & memory updates

When to use

You have the B-1059 PRD + WBS and want a repeatable process to ship it.

You’re operating as a solo developer and need auto-advance with smart pauses at the right decision points.

Execution skip rule

Skip automation if a step needs external approval or secrets you don’t have; switch to Manual Process for that step.

Backlog integration

Source of truth: B-1059 PRD WBS (Epics A–I).

Cross-refs: 000_backlog.md and your evaluation artifacts.

🚀 Solo Developer Quick Start
# 0) Start an execution session for B-1059
python3 scripts/solo_workflow.py start "B-1059 Retrieval Tuning + Bedrock canonical eval"

# 1) Run current phase with auto-advance & context
python3 scripts/solo_workflow.py execute --prd prd/B-1059.md --auto-advance --context-preserve

# 2) Resume later
python3 scripts/solo_workflow.py continue

# 3) Ship & archive (after final green run + docs)
python3 scripts/solo_workflow.py ship


(If these helpers don’t exist yet, they are part of the B-1059 WBS: “Solo workflow” items in Phase 9.)

🧭 Execution Configuration

Auto-Advance: ON by default

Context Preservation: LTST memory integrates PRD §0 context + prior decisions

Smart Pausing: Triggered only at critical decisions or external deps (see pause points)

State File: .ai_state.json (gitignored); tracks phase, task, artifacts, gates, deltas

Artifacts:

config/retrieval.yaml, config/eval_gates.yaml

metrics/last_eval_summary.json, metrics/*.csv

docs/* (tuning recipe, evaluation methodology, Bedrock setup, evidence-first)

🛠️ Process Phases & Tasks (auto-advance with smart pauses)

Below: each phase lists Tasks (from PRD WBS) → Pause Points → Success Signals → Primary Commands → Artifacts.

Phase 1 — Bedrock Canonicalization (WBS A1–A3)

Goal: Make Bedrock the default evaluator; no gate decisions from fallback.

Tasks

A1 Finalize creds/config (config/bedrock_config.yaml)

A2 CI switches to official Bedrock path; fallback disabled for gates

A3 run_eval_bedrock.sh wrapper + troubleshooting capture

Smart pause when:

AWS auth/region/model unresolved; CI lacks secret scope.

Success signals:

Local & CI runs use Bedrock; artifacts uploaded; fallback allowed only for local dev.

Commands

bash scripts/run_eval_bedrock.sh


Artifacts: Updated CI workflow; logs; verified Bedrock setup doc.

Phase 2 — Coverage & Indexing (WBS B1–B3)

Goal: Close blind spots (config/dev/test/security/docstrings).

Tasks

B1 indexing/config_rules.json (globs + chunk policies)

B2 Python docstring extraction

B3 Re-index + smoke tests (e.g., AWS_DEFAULT_REGION, pyproject.toml)

Smart pause when:

Binary/large files cause index bloat; encoding errors require rule tweaks.

Success signals:

Config lookups return candidates; Case-11 no longer zero.

Artifacts: Index stats; before/after sample queries.

Phase 3 — Hybrid Fusion & Pre-filter (WBS C1–C3)

Goal: Restore recall without wrecking precision.

Tasks

C1 Weighted-RRF fusion (k=60, λ_lex=0.6, λ_sem=0.4)

C2 Defaults: BM25_topk=80, Vec_topk=80

C3 Recall-friendly pre-filter: keep top-50 fused; drop only if (cos<0.15 && !BM25 top-20)

Smart pause when:

Latency exceeds local budget; candidate counts explode unexpectedly.

Success signals:

ΔRecall ≥ +0.20 abs; Precision ≥ 0.12; F1 improves over prior run.

Phase 4 — Rerank & Packing (WBS D1–D3)

Goal: Lift precision; keep recall via diversity + caps.

Tasks

D1 Rerank top-50 → select top-6..8; final score 0.7*rerank + 0.3*fused

D2 MMR (λ=0.7); context cap 1200–1600 tokens

D3 Evidence-first composer (snippet + filepath, then summary)

Smart pause when:

Rerank model/latency issues; evidence rendering mismatches file spans.

Success signals:

Precision climbs (≥ 0.18–0.24); Faithfulness ≥ 0.60; answers shorter & grounded.

Phase 5 — Intent Routing & Policies (WBS E1–E3)

Goal: Intent-aware knobs; eliminate “no answer” for lookups.

Tasks

E1 Heuristic router: lookup/config, how-to, multi-hop

E2 Lookup backstop: BM25 top-3 if no exact match; require snippet

E3 Cursor rules enforce evidence-first + context cap + “admit uncertainty”

Smart pause when:

Router accuracy <80% on labeled set; backstop floods low-quality hits.

Success signals:

Case-11 ≥ 0.20 F1; zero-answer rate ~0% for lookups; per-intent NDCG/P@5 improve.

Phase 6 — Tuning & Gates (WBS F1–F3)

Goal: Controlled ratchet using two-green rule.

Tasks

F1 Coordinate-ascent sweeps (BM25/Vec_topk, λ’s, cosine_min, α, top_n)

F2 config/eval_gates.yaml (initial + ratchet sequence)

F3 CI summary deltas + NiceGUI trend panel

Smart pause when:

Parameter sweeps exceed time budget; gate thrash (flapping).

Success signals:

Two consecutive green runs; Recall → 0.35–0.45, then Precision → 0.20, etc.

Commands

python3 scripts/tuning_sweeps.py --summary

Phase 7 — Test Set Hardening (WBS G1–G2)

Goal: Honest signals via hard negatives and multi-hop labels.

Tasks

G1 +2 hard-negative cases per weak domain

G2 Multi-hop chains labeled; R@50 tracked

Smart pause when:

New cases cause unexplained collapses → investigate coverage vs thresholds.

Success signals:

Reduced false positives; multi-hop correctness verified.

Phase 8 — Documentation, Memory & Governance (WBS H1–H4)

Goal: Make it teachable + enforceable (docs, memory, rules).

Tasks

H1 Retrieval Tuning Recipe

H2 Eval methodology & gates doc

H3 Memory entries + Cursor rules live

H4 Bedrock setup doc (clean-room verified)

Smart pause when:

Policy conflicts with current outputs; decide exception vs correction.

Success signals:

Docs reviewed; memory updated; Cursor rules trigger on violations.

Phase 9 — Observability & Solo Workflow (WBS I1–I3, optional)

Goal: Frictionless solo loop + visible trends.

Tasks

I1 Export metrics/CSV, stable schemas

I2 Trend panel (per-intent)

I3 One-command workflow (start|continue|ship)

Success signals:

One-command run covers sweep → eval → dashboard; deltas visible.

✅ Quality Gates (check each phase)

 Code Review (self-review acceptable, checklist-based)

 Tests Passing (unit+integration)

 Performance (local eval ≤ 5 min; rerank p95 ≤ 300 ms)

 Security (no secrets in repo; least privilege)

 Docs Updated (guides + policies)

 Resilience (retry/backoff; clear failure modes)

 Edge Cases (large files, encodings, empty hits)

 Gates Met (two-green rule before ratchet)

🧩 PRD → Execution Mapping
PRD Section	Execution Use
§0 Context	Seeds LTST context & decisions; drives defaults
§1–2 Problem/Solution	Validates scope; prevents gold-plating
§4 Technical Approach	Implements hybrid→fusion→rerank→packing
§6 Evaluation	Bedrock canonical runs; per-intent metrics
§7 Implementation Plan	This phase plan & gates
§8 WBS	Concrete tasks A–I above
📦 State & Error Handling

State file: .ai_state.json — tracks current phase/task, artifacts, deltas, last good knobs.

HotFix flow: detect failure → generate fix task → apply → re-run → resume.

Retry logic: exponential backoff on Bedrock/network; bounded sweep grids.

🟢 Runbook: minimal happy path (first pass)

A1–A3: Bedrock default in CI → green run

B1–B3: Index rules + docstrings → smoke tests pass

C1–C3: wRRF + recall-friendly pre-filter → Recall ≥ 0.35

D1–D3: Rerank + MMR + evidence-first → Precision ≥ 0.18; Faithfulness ≥ 0.60

E1–E2: Router + lookup backstop → Case-11 fixed

F1–F2: Sweeps + initial gates → two greens, ratchet Recall gate

G1–G2: Hard negatives + multi-hop labels → stable metrics

H1–H4: Docs + memory + rules → polish

I1–I3: Trends + one-command loop (optional)

📈 Ratchet ladder (apply after two greens, each rung)

Recall ≥ 0.35 (Precision ≥ 0.12)

Precision ≥ 0.20 (Recall ≥ 0.45)

Recall ≥ 0.60 (Precision ≥ 0.20)

Precision ≥ 0.30; Faithfulness ≥ 0.70

🧪 Command snippets (reference)
# Evaluate (Bedrock canonical)
bash scripts/run_eval_bedrock.sh

# Parameter sweeps
python3 scripts/tuning_sweeps.py --summary

# Re-index
python3 scripts/index_repo.py --rules indexing/config_rules.json


(Wire these as part of WBS if not present yet.)

📜 Special instructions

Prefer simple, reversible changes; keep numerics in YAML.

Use evidence-first answers; show snippet + filepath for lookups.

Keep rerank influence (α) high only when precision stalls.

Open the funnel at candidate gen; let rerank do the pruning.

Enforce two-green before any gate ratchet.

Track Δ vs last run (CI summary + dashboard) for every change.
