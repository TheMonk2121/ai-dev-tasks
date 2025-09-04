Map of Maps: Codebase Navigation and Blast Radius

- Core Domains: High-level areas of responsibility
  - dspy-rag-system/: Core DSPy-based RAG system (modules, utils, workflows)
  - src/retrieval/: Retrieval pipeline (intent routing, prefilter, reranker, fusion)
  - scripts/: Operational tools, evaluation harnesses, maintenance utilities
  - configs/ and config/: Runtime/eval configs and cost/bedrock settings
  - metrics/: Baselines, reports, visualizations
  - artifacts/: PRDs, task lists, execution notes
  - 400_guides/ and 100_memory/: Architecture, workflows, and internal guides
  - tests/ and dspy-rag-system/tests/: Unit/integration tests

- Core Pipelines: Retrieval + RAG components
  - src/retrieval/intent_router.py: Query intent routing
  - src/retrieval/prefilter.py: Candidate filtering
  - src/retrieval/reranker.py: Ranking logic
  - src/retrieval/fusion.py: Result blending
  - src/retrieval/quality_gates.py and src/retrieval/robustness_checks.py: Safety and quality gates
  - dspy-rag-system/src/dspy_modules/rag_system.py and enhanced_rag_system.py: End-to-end orchestration

- Evaluation & Monitoring
  - dspy-rag-system/src/monitoring/: Performance schema, storage, collector, dashboard
  - scripts/eval/: Retrieval and faithfulness eval scripts
  - metrics/baseline_evaluations/: Baselines, red lines, progress summaries
  - scripts/ragchecker_official_evaluation.py and tests/test_ragchecker_*: RAGChecker integration

- Configuration & Ops
  - config/retrieval.yaml and configs/eval/*.yaml: Retrieval and evaluation settings
  - scripts/*_setup*.py, setup.sh, setup_secrets.py: Environment setup
  - .github/workflows/eval.yml: CI eval workflow
  - .pre-commit-config.yaml and .git/hooks/*: Local quality gates

- Documentation Maps
  - 400_guides/400_03_system-overview-and-architecture.md: System overview
  - 400_guides/400_06_memory-and-context-systems.md and 400_ltst-memory-system-*.md: Memory system
  - 400_guides/400_07_ai-frameworks-dspy.md and 400_dspy-mcp-integration-guide.md: DSPy + MCP
  - artifacts/prds/: Product requirements and specs

- Visualizations
  - metrics/visualizations/dependency_graph.html: Existing static dependency graph (historical)
  - metrics/visualizations/import_graph.json: Generated import graph (run scripts/code_map.py)
  - metrics/visualizations/import_graph.html: Interactive graph viewer for import_graph.json

- Blast Radius Workflow
  - Generate graph: `python scripts/code_map.py`
  - Analyze change impact: `python scripts/blast_radius.py path/to/file.py`
  - Filter impacted tests: Script output includes test files

- Suggested Entry Points
  - dspy-rag-system/src/dspy_modules/rag_pipeline.py: DSPy pipeline
  - dspy-rag-system/src/dspy_modules/context_models.py: Context and data models
  - dspy-rag-system/src/utils/: Cross-cutting utilities (privacy, session, monitoring)
  - src/retrieval/test_hardening.py and scripts/test_retrieval_system.py: Retrieval tests/examples

Notes
- The import graph excludes third-party and venv paths.
- Use the blast radius tool before refactors to scope reviews and tests.

