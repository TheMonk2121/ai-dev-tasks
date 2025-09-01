# PRD: B-1059 - Retrieval Tuning Protocol & Evaluation Framework (Industry Recipe)

## 📋 **Product Requirements Document**

### **Backlog Item**: B-1059
### **Title**: Retrieval Tuning Protocol & Evaluation Framework (Industry Recipe)
### **Status**: 🔴 **CRITICAL - IMMEDIATE ACTION REQUIRED**
### **Priority**: 🔥 **HIGHEST**
### **Points**: 8

### **Metadata**
- **Backlog ID**: B-1059
- **Owner**: Daniel / Core RAG & Memory
- **Stakeholders**: Retrieval/Agents, Evaluation/CI, Documentation/Governance
- **Status**: Draft for implementation
- **Last updated**: 2025-09-01 (America/Chicago)

---

## 🎯 **Executive Summary**

Your current evaluation harness is in place (Bedrock-ready, CI gates, test suite), but metrics show volatile trade-offs: precision rises when recall collapses, and vice versa. Coverage gaps (e.g., config/dev/test/security) and inconsistent routing lead to domain-specific failures. You need a repeatable, measurable industry-grade "recipe" to tune retrieval, reranking, and packing—plus guardrails that prevent premature optimization and regressions.

### **Core Objectives**
- **Solidify reusable tuning framework** ("industry recipe") that encodes precision/recall trade-offs and makes them intent-aware
- **Provide deterministic knob sweeps** (coordinate ascent) and two-green ratcheting to prevent over-optimization
- **Produce clear inputs/outputs** for downstream agents and memory
- **Establish Bedrock as canonical evaluator** with complete CI integration
- **Deliver taskable PRD** with explicit WBS, acceptance criteria, and Definition of Done

---

## 📊 **Current State Analysis**

### **Performance Baseline**
- **Current F1 Score**: 0.112 (11.2%)
- **Current Precision**: 0.149 (14.9%)
- **Current Recall**: 0.099 (9.9%)
- **Critical Issue**: Case 11 (Configuration) at 0.0% F1

### **Root Cause Analysis**
- **Over-tight gating**: BM25_topk and Vector_topk too restrictive (10 vs needed 80)
- **Coverage gaps**: Configuration files not properly indexed
- **Precision/recall imbalance**: System optimized for precision at expense of recall

### **Context & Problem Statement**
Your current evaluation harness is in place (Bedrock-ready, CI gates, test suite), but metrics show volatile trade-offs: precision rises when recall collapses, and vice versa. Coverage gaps (e.g., config/dev/test/security) and inconsistent routing lead to domain-specific failures. You need a repeatable, measurable industry-grade "recipe" to tune retrieval, reranking, and packing—plus guardrails that prevent premature optimization and regressions.

---

## 🚀 **Target State & Objectives**

### **Primary Objectives**
1. **Restore Recall**: 0.099 → 0.35-0.55 (+25-45 pts)
2. **Maintain Precision**: ≥ 0.12 (current 0.149 passes)
3. **Improve F1**: 0.112 → 0.22-0.30 (+10-18 pts)
4. **Fix Critical Cases**: Case 11 (config) above 20% F1

### **Success Criteria**
- All 15 RAGChecker cases above 10% F1
- Case 11 (configuration) above 20% F1
- Systematic performance improvement without regression
- Production-ready baseline metrics achieved

### **Goals & Non-Goals**

#### **2.1 Goals**
Solidify a reusable tuning framework ("industry recipe") that:

- **Encodes the precision/recall trade-offs** and makes them intent-aware (lookup vs how-to vs multi-hop)
- **Provides deterministic knob sweeps** (coordinate ascent) and two-green ratcheting so you don't over-optimize
- **Produces clear inputs/outputs** for downstream agents and memory

**Documentation & Governance**
- Thorough, versioned docs integrated into the correct memory layers (turn → rolling summary → facts/long-term) and enforced via Cursor rules and documentation authority structures
- "Evidence-first" answer policy codified

**Bedrock as the canonical evaluator**
- Complete Bedrock configuration and make the official Bedrock evaluation path the default for CI/quality gates

**Taskability**
- Deliver a PRD that can be converted directly into a task list: explicit WBS, acceptance criteria, and "Definition of Done"

#### **2.2 Non-Goals**
- **Not a wholesale re-architecture** of your RAG/CAG system
- **Not introducing cutting-edge graph engines** yet (those live in B-1050/51/52; we will add hooks to A/B them later)
- **Not model fine-tuning**; focus is retrieval, reranking, packing, evaluation, and governance

---

## 👥 **Users & Use Cases**

### **Primary User**
- **You (solo dev)**, operating the stack locally, running evals frequently

### **Use Cases**
- **Tune retrieval for config/file lookups**
- **Tune for troubleshooting/how-to answers** with multiple evidence shards
- **Preserve multi-hop reasoning** for advanced questions
- **Enforce evidence-first answers** to raise faithfulness and reduce hallucination

---

## 📈 **Success Metrics & Targets**

### **4.1 Global Metrics (short → mid → long term)**
- **Precision**: ≥0.20 → ≥0.30 → ≥0.40–0.50
- **Recall**: ≥0.45 → ≥0.60 → ≥0.70
- **F1**: ≥0.22 → ≥0.30–0.40 → ≥0.50
- **Faithfulness**: ≥0.60 → ≥0.70 → ≥0.75+

### **4.2 Intent-Specific Checks**
- **File/Config lookup**: P@5 primary, NDCG@10 secondary; answer must include exact snippet + filepath
- **Troubleshoot/How-to**: NDCG@10 primary, R@20 secondary; at least 2 distinct evidence chunks
- **Project/Status**: P@5 primary, Faithfulness secondary; evidence-first summary, no contradictions
- **Multi-hop/Advanced**: R@50 primary, Faithfulness secondary; correct chain across files (no hallucinated edges)

---

## 🔧 **Technical Approach**

### **5.1 Coverage & Indexing**
**File types to index:**
`.md`, `.py` (docstrings), `.yaml`, `.yml`, `.toml`, `.json`, `.ini`, `.env.example`, `.github/workflows/*`, `Makefile`, `requirements*.txt`, `scripts/*`

**Chunking defaults:**
- **Prose/code**: 350–600 tokens, 20–25% overlap
- **Config**: line-block chunks (20–40 lines), preserve keys and adjacent comments
- **Normalization**: lowercase prose fields; preserve case in code/IDs; add exact-identifier match feature
- **Evidence extraction**: keep source paths and line spans for snippet rendering

### **5.2 Candidate Generation (Hybrid)**
**Retrieve two lists, then fuse:**
- **BM25_topk = 80, Vec_topk = 80** (opening the funnel; later tightened)
- **Weighted RRF fusion:**
  ```
  score(d) = λ_lex/(k + r_bm25(d)) + λ_sem/(k + r_vec(d))
  ```
- **Defaults**: k=60, λ_lex=0.6, λ_sem=0.4 (bias lexical to fix lookup/config first)

### **5.3 Pre-filter (Recall-friendly)**
- **Keep top 50 fused**
- **Drop only if** (cosine < 0.15) AND (not in BM25 top-20)
- **Rationale**: never discard strong lexical hits just because cosine is low

### **5.4 Reranking (Precision Lever)**
- **Cross-encoder/Bedrock reranker** over the top 50 fused
- **Select top 6–8**; final score 0.7 * rerank + 0.3 * fused
- **Tiebreakers**: exact-term bonus; same-file proximity; code-block bonus for tech queries

### **5.5 Diversity & Packing**
- **MMR (λ=0.7)** to avoid near-duplicates
- **Context cap**: ~1200–1600 tokens
- **Evidence-first answer**: 1–2 top snippets with paths, then constrained summary

### **5.6 Intent-Aware Routing (Lightweight)**
- **Lookup/Config**: if no exact key/path match found, backstop with BM25 top-3 regardless of cosine; strict snippet requirement
- **How-to/Troubleshoot**: allow 2–3 diverse chunks; looser thresholds to preserve coverage
- **Multi-hop**: allow more candidates pre-rerank; require cross-file coherence checks

### **5.7 Tuning Algorithm (Coordinate Ascent)**
- **Fix rerank α=0.7**; sweep BM25_topk ∈ {40,80}, Vec_topk ∈ {40,80,120} → pick highest Recall with Precision ≥ 0.12
- **Sweep fusion weights** λ_lex ∈ {0.5,0.6,0.7}, λ_sem = 1−λ_lex → maximize P@5 (lookup) + NDCG@10 (how-to) average
- **Sweep pre-filter cosine** min {0.10, 0.15, 0.20} → maximize F1
- **If Precision < 0.20** after step 3, set α=0.8 and reduce rerank_top_n ∈ {5,6}

---

## 🧪 **Evaluation Framework**

### **6.1 Bedrock as Canonical**
- **Bedrock credentials/config completed and validated**
- **CI uses official Bedrock path** for RAGChecker; fallback path disabled for gates (allowed only in local dev runs)

### **6.2 Metrics**
- **Global**: Precision, Recall, F1, Faithfulness
- **Intent**: P@5 (lookup), NDCG@10 (how-to), R@50 (multi-hop)
- **Report per case and by domain** (config/dev/test/security, DSPy impl, error handling, advanced features)

### **6.3 Gates & Ratcheting**
- **Two-green rule**: increase thresholds only after two consecutive green runs
- **Initial global gates**: Precision ≥ 0.12, Recall ≥ 0.15, Faithfulness ≥ 0.60
- **Ratchet path**:
  - Recall → 0.35–0.45 (keep Precision ≥ 0.12)
  - Precision → 0.20 (Recall ≥ 0.45)
  - Recall → 0.60 (Precision ≥ 0.20)
  - Precision → 0.30, Faithfulness → 0.70

### **6.4 Test Set Hardening**
- **Add hard negatives** for each weak domain: same-file wrong sections; sibling files with near synonyms
- **Ensure per-intent queries exist** and are labeled

---

## 📦 **Deliverables & Artifacts**

### **7.1 Config & Code**
- **config/retrieval.yaml** (new): defaults for top-k, RRF weights, pre-filter, rerank α, packing caps, MMR λ, intent routing
- **config/eval_gates.yaml** (new): current gates + ratchet schedule
- **scripts/run_eval_bedrock.sh** (updated): official eval, result export
- **scripts/tuning_sweeps.py** (new): coordinate ascent sweeps with summary CSV/JSON
- **src/retrieval/fusion.py** (new or updated): weighted-RRF
- **src/retrieval/rerank.py** (updated): top-50 rerank; α weighting; tie-breakers
- **src/retrieval/packing.py** (updated): MMR diversity; context cap; evidence-first composer
- **src/retrieval/routing.py** (new): lightweight intent routing (heuristics/regex)
- **indexing/config_rules.json** (new): file globs and chunking strategy per type

### **7.2 Documentation**
- **docs/guide_retrieval_tuning.md**: the recipe, trade-offs, knobs, playbooks
- **docs/evidence_first_policy.md**: snippet + path requirements; style rules
- **docs/bedrock_setup.md**: canonical instructions, troubleshooting
- **docs/eval_methodology.md**: metrics, gates, ratchet rules, test-set design

### **7.3 Memory & Governance**
**Memory entries (Facts/Long-Term) for:**
- Retrieval tuning recipe (versioned)
- Evidence-first policy
- Bedrock canonical evaluator policy

**Cursor rules additions to enforce:**
- Evidence-first responses
- No packing beyond context cap
- Reference snippet path requirement for lookup answers

### **7.4 Observability**
- **metrics/last_eval_summary.json** and csv/ exports
- **NiceGUI (or equivalent) panel section** for per-intent trend lines

---

## ✅ **Acceptance Criteria (Definition of Done)**

- **Bedrock default in CI**; official path runs green locally and in CI
- **Retrieval defaults applied** (BM25_topk, Vec_topk, wRRF, pre-filter, rerank α, MMR, caps)
- **Intent-aware routing live** with at least 3 intents enforced
- **Evidence-first policy active** and validated in 10 sample answers, including config lookups (snippet + path present)
- **Gates & ratchet configured**; two-green rule enforced
- **Metrics (2 green runs)**:
  - Precision ≥ 0.12, Recall ≥ 0.15, Faithfulness ≥ 0.60 (initial)
  - Then Recall ≥ 0.35 while keeping Precision ≥ 0.12
- **Docs complete** and placed into correct memory layers; Cursor rules updated
- **Test set expanded** with hard negatives for weak domains; per-intent labeling present
- **Artifacts produced** (configs, scripts, charts) and linked from the docs index

---

## 🏗️ **Work Breakdown Structure (WBS → easily taskable)**

### **Epic A — Bedrock Canonicalization**
- **A1**: Validate AWS creds; finalize config/bedrock_config.yaml
- **A2**: Update CI job to use Bedrock path; disable fallback for gates
- **A3**: Add troubleshooting log capture; document in docs/bedrock_setup.md

### **Epic B — Coverage & Indexing**
- **B1**: Implement indexing/config_rules.json with file globs and chunking per type
- **B2**: Add docstring extraction for .py
- **B3**: Re-index repo; smoke-test config lookups

### **Epic C — Hybrid Fusion & Pre-filter**
- **C1**: Implement wRRF in src/retrieval/fusion.py
- **C2**: Set defaults (BM25_topk=80, Vec_topk=80, k=60, λ_lex=0.6, λ_sem=0.4)
- **C3**: Add pre-filter (cos < 0.15 && !BM25_top20)

### **Epic D — Reranking & Packing**
- **D1**: Rerank top-50; α=0.7; select 6–8
- **D2**: MMR (λ=0.7), context cap 1200–1600
- **D3**: Evidence-first composer (snippet+path, then summary)

### **Epic E — Intent Routing & Policies**
- **E1**: Implement heuristic intent routing in src/retrieval/routing.py
- **E2**: Add lookup backstop (BM25 top-3) when no exact key match
- **E3**: Codify evidence-first in docs/evidence_first_policy.md

### **Epic F — Tuning & Gates**
- **F1**: Build scripts/tuning_sweeps.py (coordinate ascent)
- **F2**: Add config/eval_gates.yaml with two-green ratchet
- **F3**: Integrate gate parsing in CI and NiceGUI

### **Epic G — Test Set Hardening**
- **G1**: Add hard negatives to config/dev/test/security; label intents
- **G2**: Add how-to near-misses; add multi-hop chains
- **G3**: Validate per-intent dashboards

### **Epic H — Documentation & Memory**
- **H1**: Write docs/guide_retrieval_tuning.md and docs/eval_methodology.md
- **H2**: Insert facts into long-term memory; associate tags (retrieval_recipe, evidence_policy, bedrock_canonical)
- **H3**: Update Cursor rules to enforce evidence-first and caps

---

## 🚨 **Risks & Mitigations**

### **Technical Risks**
- **Latency creep** (top-k increases): mitigate by keeping rerank_top_n ≤ 6–8; prefer lowering Vec_topk before BM25_topk
- **Overfitting to reranker quirks**: keep fused score in final blend (0.3); validate on per-intent NDCG
- **Config path brittleness**: maintain backstop BM25 path for lookups; ensure glob rules stable
- **Gate thrash**: enforce two-green rule; ratchet slowly

---

## ⚖️ **Trade-offs & Alternatives**

- **Higher BM25 bias** improves lookups and config but may miss paraphrases; compensate with downstream rerank and MMR
- **Aggressive pre-filters** raise precision but collapse recall; adopt recall-friendly pre-filter as default and let the reranker clean up
- **Graph expansion early** (B-1050/51/52) could help multi-hop, but adds surface area; ship behind flags only after P3 metrics hold

---

## 🚀 **Rollout Plan (Phased)**

- **P0 (Day 0–1)**: Bedrock canonicalization; gates set to initial thresholds
- **P1 (Day 1–2)**: Coverage+indexing; wRRF and pre-filter live; rerank α=0.7; evidence-first composer; first green run
- **P2 (Day 2–3)**: Tuning sweeps; raise Recall to ≥0.35 without Precision <0.12; second green run
- **P3 (Day 3–5)**: Intent routing; hard-negatives added; ratchet Precision to ≥0.20 while keeping Recall ≥0.45; two green runs
- **P4 (Day 5+)**: Stabilize; docs/memory complete; prepare A/B hooks for B-1050/51/52

---

## ⚙️ **Config Templates (ready to drop in)**

### **13.1 config/retrieval.yaml**
```yaml
candidate_gen:
  bm25_topk: 80
  vec_topk: 80
fusion:
  method: weighted_rrf
  rrf_k: 60
  lambda_lex: 0.6
  lambda_sem: 0.4
prefilter:
  keep_top_fused: 50
  drop_rule:
    cosine_min: 0.15
    keep_if_bm25_rank_leq: 20
rerank:
  enabled: true
  input_top_n: 50
  select_top_n: 6
  alpha_rerank: 0.7   # final = alpha*rerank + (1-alpha)*fused
packing:
  mmr_lambda: 0.7
  context_cap_tokens: 1500
answering:
  evidence_first: true
  max_snippets: 2
intent_routing:
  lookup:
    require_exact_match: true
    bm25_backstop_topn: 3
  howto:
    allow_diverse_chunks: 3
  multihop:
    allow_extra_candidates: true
```

### **13.2 config/eval_gates.yaml**
```yaml
gates:
  initial:
    precision_min: 0.12
    recall_min: 0.15
    faithfulness_min: 0.60
  ratchet_sequence:
    - { after_runs: 2, recall_min: 0.35, precision_min: 0.12, faithfulness_min: 0.60 }
    - { after_runs: 2, precision_min: 0.20, recall_min: 0.45, faithfulness_min: 0.65 }
    - { after_runs: 2, recall_min: 0.60, precision_min: 0.20, faithfulness_min: 0.70 }
    - { after_runs: 2, precision_min: 0.30, recall_min: 0.60, faithfulness_min: 0.70 }
```

### **13.3 indexing/config_rules.json**
```json
{
  "include_globs": [
    "**/*.md", "**/*.py", "**/*.yaml", "**/*.yml", "**/*.toml",
    "**/*.json", "**/*.ini", "**/.env.example",
    ".github/workflows/*.yml", "Makefile", "requirements*.txt", "scripts/*"
  ],
  "chunking": {
    "prose_code": { "tokens": 500, "overlap": 0.22 },
    "config": { "line_block": true, "lines_per_block": [20, 40] }
  },
  "preserve": { "case_in_code": true, "exact_identifiers": true }
}
```

### **13.4 Cursor Rules (additions)**
- **Answers must present evidence snippets and file paths** for lookup/config questions
- **Do not exceed context cap**; prefer diversity over repetition (MMR)
- **If no strong evidence is available**, say so and suggest next diagnostic step—do not hallucinate

---

## ❓ **Open Questions**

- **Do we need a separate "security mode"** with stricter retrieval on secrets-like terms?
- **Should we persist per-intent historical knobs** to warm-start future tuning?
- **Where to set the latency budget** per query type on local hardware?

---

*PRD Created: August 31, 2025*
*Status: Complete - Ready for Implementation*
*Backlog Item: B-1059*
*Priority: 🔥 HIGHEST*
*Last Updated: 2025-09-01 (America/Chicago)*
