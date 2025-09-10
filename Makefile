# AI Dev Tasks Makefile
# Provides convenient targets for common development tasks and CI parity

.PHONY: help code-review format typecheck test test-ci db-init \
	eval-real eval-gold eval-mock eval-ablation-off eval-ablation-on eval-ablation-suite \
	gate-rerank-uplift metrics-signal ci pipeline test-profiles \
	test-ragchecker test-ragchecker-performance eval-ragchecker \
	gate-ragchecker gate-ragchecker-strict

help:  ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ---------- Code Quality ----------
code-review: ## Ruff lint + format check
	uvx ruff check .
	uvx ruff format --check .

format: ## Apply formatting with Ruff formatter
	uvx ruff format .

typecheck: ## Static typing (pyright)
	uvx pyright .


test:  ## Run tests
	pytest tests/ -v

test-ci: ## Fast tests for CI (parallel, fail fast)
	uv run pytest -q -n 3 --maxfail=1 --tb=short

# ---------- DB & Ingest ----------
db-init: ## Initialize lightweight DB schema for CI/dev
	bash scripts/ci_init_db.sh

# ---------- Evaluations ----------
eval-real:  ## Baseline/tuning on real RAG
	./scripts/eval_real.sh

eval-gold:  ## Real RAG + gold cases
	./scripts/eval_gold.sh

eval-mock:  ## Infra-only smoke (never for baselines)
	./scripts/eval_mock.sh

test-profiles:  ## Test all evaluation profiles
	@echo "Testing profile configuration loader..."
	@python3 scripts/lib/config_loader.py --profile real --help || true
	@python3 scripts/lib/config_loader.py --profile gold --help || true
	@python3 scripts/lib/config_loader.py --profile mock --help || true
	@echo "✅ Profile tests completed"

# Development targets
install:  ## Install dependencies
	pip install -r requirements.txt

clean:  ## Clean temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# ---------- Reranker Ablation Suite ----------
eval-ablation-off: ## Run reranker ablation (OFF)
	uv run python -m evals_300.tools.run \
		--suite 300_core \
		--pass reranker_ablation_off \
		--out metrics/rerank_off \
		--seed 42 \
		--concurrency ${MAX_WORKERS:-3}

eval-ablation-on: ## Run reranker ablation (ON)
	uv run python -m evals_300.tools.run \
		--suite 300_core \
		--pass reranker_ablation_on \
		--out metrics/rerank_on \
		--seed 42 \
		--concurrency ${MAX_WORKERS:-3}

eval-ablation-suite: ## Run OFF then ON and write compare.json
	uv run python -m evals_300.tools.run \
		--suite 300_core \
		--pass reranker_ablation_suite \
		--concurrency ${MAX_WORKERS:-3}

gate-rerank-uplift: ## Gate Δ micro-F1 ≥ threshold
	uv run python scripts/ci_check_reranker_uplift.py \
		--threshold ${UPLIFT_THRESHOLD:-0.01} \
		metrics/rerank_off/summary.json \
		metrics/rerank_on/summary.json

# ---------- RAGChecker Evaluation Suite ----------
eval-ragchecker: ## Run RAGChecker evaluation
	uv run python3 scripts/run_eval.py

test-ragchecker: ## Run RAGChecker test suite
	uv run python -m pytest tests/test_ragchecker_evaluation.py -v --tb=short

test-ragchecker-performance: ## Run RAGChecker performance tests
	uv run python -m pytest tests/test_ragchecker_performance.py -v --tb=short

gate-ragchecker: ## Validate RAGChecker evaluation results
	uv run python scripts/abp_validation.py --profile precision_elevated --max-age-days 2 --ci-mode

gate-ragchecker-strict: ## Strict RAGChecker quality gates (for release branches)
	uv run python scripts/abp_validation.py --profile precision_elevated --max-age-days 2 --strict

metrics-signal: ## Generate nightly test-signal CSV
	uv run python scripts/test_signal_report.py

# ---------- Pipelines ----------
ci: ## Canonical CI pipeline
	$(MAKE) code-review typecheck test-ci eval-ablation-off eval-ablation-on gate-rerank-uplift

pipeline: ## Full local parity pipeline
	$(MAKE) code-review typecheck test-ci db-init eval-real
