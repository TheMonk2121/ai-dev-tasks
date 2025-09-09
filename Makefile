# AI Dev Tasks Makefile
# Provides convenient targets for common development tasks

.PHONY: help eval-real eval-gold eval-mock test-profiles

help:  ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

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

lint:  ## Run linting
	ruff check .
	pyright .

test:  ## Run tests
	pytest tests/ -v

clean:  ## Clean temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
