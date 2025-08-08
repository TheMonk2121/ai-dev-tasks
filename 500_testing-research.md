<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_testing-strategy-guide.md -->

# Testing Research

Backlog link: B-012

<!-- ANCHOR: tldr -->
<a id="tldr"></a>

## 🔎 TL;DR

- Test types/pyramid, gates, CI hooks, perf/security test insights
- Mirrors `400_testing-strategy-guide.md`

<!-- ANCHOR: key-findings -->
<a id="key-findings"></a>

 
## Key Findings
- AI-oriented testing must blend deterministic tests (parsers/validators) with model-evaluation checks (answer faithfulness and citation presence) to handle nondeterminism.
- Metamorphic testing (invariants under paraphrase/format changes) is effective for prompts and retrieval pipelines.
- Property-based tests reveal edge cases in chunking, retrieval, sanitization where fixed cases miss defects.
- CI should gate on RAG metrics (e.g., retrieval recall@k, citation faithfulness) and on basic security tests (prompt-injection refusal, PII redaction).
- Flake management: constrained reruns (1–2) and tolerance bands reduce false negatives while still catching drift.
 - Align test oracles with span-grounded citations: sentence-level faithfulness against retrieved chunks improves precision of failures (400_documentation-retrieval-guide.md).

<!-- ANCHOR: actionable-patterns -->
<a id="actionable-patterns"></a>

 
## Actionable Patterns
- Metamorphic tests: define invariants (e.g., answers must still cite sources after benign question paraphrase) and assert they hold.
- Property-based generators: fuzz chunk sizes/overlaps; validate retrieval coverage and citation offsets remain consistent.
- RAG evaluation in CI: maintain a seed QA set; assert recall@5 and faithfulness meet thresholds; fail on regression.
- Security checks: adversarial prompts must be refused; outputs must not contain PII/secrets (regex screens) before passing.
- Flake policy: allow up to 2 reruns only for model-eval tests; record variance and alert on significant drift.
 - Deterministic harnesses for non-LLM code (indexers, sanitizers) ensure reproducible failures separate from model noise (400_testing-strategy-guide.md).

<!-- ANCHOR: implementation-refs -->
<a id="implementation-refs"></a>

 
## Implementation References
- 400_testing-strategy-guide.md (strategy, gates, matrices)
- dspy-rag-system/tests/comprehensive_test_suite.py (extend with RAG eval + metamorphic cases)
- tests/test_doc_coherence_validator.py (coherence checks)
- dspy-rag-system/tests/test_validation_and_monitoring.py (observability hooks)

<!-- ANCHOR: citations -->
<a id="citations"></a>

 
## Citations
- 400_testing-strategy-guide.md
- docs/research/papers/monitoring-papers.md
- docs/research/articles/monitoring-articles.md
- docs/research/tutorials/monitoring-tutorials.md

