
<!-- ANCHOR_KEY: testing-research -->
<!-- ANCHOR_PRIORITY: 10 -->
<!-- ROLE_PINS: ["researcher", "coder"] -->

# 🧪 Testing Research

Backlog link: B-012

<!-- ANCHOR: tldr -->
{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Research on testing approaches and gates for this repo | Designing/adjusting tests or debugging flaky model-eval
checks | Apply `400_guides/400_testing-strategy-guide.md`; run `./dspy-rag-system/run_tests.sh` or
`run_comprehensive_tests.sh` |

## 🎯 **Current Status**-**Status**: ✅ **ACTIVE**- Research file with content

- **Priority**: 🔧 Medium - Research for implementation

- **Points**: 3 - Research and testing guidance

- **Dependencies**: 400_guides/400_context-priority-guide.md, 400_guides/400_testing-strategy-guide.md

- **Next Steps**: Implement testing patterns and quality assurance

<!-- ANCHOR: key-findings -->

## Key Findings

- AI-oriented testing must blend deterministic tests (parsers/validators) with model-evaluation checks (answer
faithfulness and citation presence) to handle nondeterminism.

- Metamorphic testing (invariants under paraphrase/format changes) is effective for prompts and retrieval pipelines.

- Property-based tests reveal edge cases in chunking, retrieval, sanitization where fixed cases miss defects.

- CI should gate on RAG metrics (e.g., retrieval recall@k, citation faithfulness) and on basic security tests
(prompt-injection refusal, PII redaction).

- Flake management: constrained reruns (1–2) and tolerance bands reduce false negatives while still catching drift.
- Align test oracles with span-grounded citations: sentence-level faithfulness against retrieved chunks improves
precision of failures (400_guides/400_documentation-retrieval-guide.md).

<!-- ANCHOR: actionable-patterns -->

## Actionable Patterns

- Metamorphic tests: define invariants (e.g., answers must still cite sources after benign question paraphrase) and
assert they hold.

- Property-based generators: fuzz chunk sizes/overlaps; validate retrieval coverage and citation offsets remain
consistent.

- RAG evaluation in CI: maintain a seed QA set; assert recall@5 and faithfulness meet thresholds; fail on regression.

- Security checks: adversarial prompts must be refused; outputs must not contain PII/secrets (regex screens) before
passing.

- Flake policy: allow up to 2 reruns only for model-eval tests; record variance and alert on significant drift.
- Deterministic harnesses for non-LLM code (indexers, sanitizers) ensure reproducible failures separate from model noise
(400_guides/400_testing-strategy-guide.md).

<!-- ANCHOR: implementation-refs -->

## Implementation References

- 400_guides/400_testing-strategy-guide.md (strategy, gates, matrices)

- dspy-rag-system/tests/comprehensive_test_suite.py (extend with RAG eval + metamorphic cases)

- tests/test_doc_coherence_validator.py (coherence checks)

- dspy-rag-system/tests/test_validation_and_monitoring.py (observability hooks)

<!-- ANCHOR: citations -->

## Citations

- 400_guides/400_testing-strategy-guide.md

- docs/research/papers/monitoring-papers.md

- docs/research/articles/monitoring-articles.md

- docs/research/tutorials/monitoring-tutorials.md
