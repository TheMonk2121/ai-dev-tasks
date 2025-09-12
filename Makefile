# AI Dev Tasks - Test Targets
# 
# test-fast: Run quick gate tests in host venv (macOS)
# test-full: Run full test suite in container venv (Linux)

.PHONY: test-fast test-full setup-host setup-container clean

# Environment variables for deterministic runs
export RAGCHECKER_BYPASS_CLI=1
export TOKENIZERS_PARALLELISM=false
export DSPY_CACHE=0
export AWS_REGION=us-east-1
export POSTGRES_DSN=mock://test

# Quick gate tests in host venv (macOS)
test-fast:
	@echo "Running quick gate tests in host venv..."
	uv run pytest -q tests/test_schema_roundtrip.py tests/test_doc_coherence_validator.py

# Full test suite in container venv (Linux)
test-full:
	@echo "Running full test suite in container venv..."
	./scripts/docker_pytest.sh

# Full test suite with caching (faster for repeated runs)
test-full-cached:
	@echo "Running full test suite with cached venv..."
	./scripts/docker_pytest_cached.sh

# Setup host environment for quick dev
setup-host:
	@echo "Setting up host venv for quick dev..."
	./scripts/setup_host_venv.sh

# Setup container environment for full testing
setup-container:
	@echo "Setting up container venv for full testing..."
	./scripts/setup_container_venv.sh

# Clean up virtual environments
clean:
	@echo "Cleaning up virtual environments..."
	rm -rf .venv .venv-linux

# Evaluation profile targets
eval-real:
	@echo "Running evaluation with real profile..."
	@if [ -f "scripts/eval_real.sh" ]; then \
		./scripts/eval_real.sh; \
	else \
		python3 scripts/ragchecker_official_evaluation.py --profile real; \
	fi

eval-gold:
	@echo "Running evaluation with gold profile..."
	@if [ -f "scripts/eval_gold.sh" ]; then \
		./scripts/eval_gold.sh; \
	else \
		python3 scripts/ragchecker_official_evaluation.py --profile gold; \
	fi

eval-mock:
	@echo "Running evaluation with mock profile..."
	@if [ -f "scripts/eval_mock.sh" ]; then \
		./scripts/eval_mock.sh; \
	else \
		python3 scripts/ragchecker_official_evaluation.py --profile mock; \
	fi

test-profiles:
	@echo "Running profile configuration tests..."
	uv run pytest -v tests/test_config_profiles.py

# Help target
help:
	@echo "Available targets:"
	@echo "  test-fast        - Run quick gate tests in host venv (macOS)"
	@echo "  test-full        - Run full test suite in container venv (Linux)"
	@echo "  test-full-cached - Run full test suite with cached venv (faster)"
	@echo "  setup-host       - Setup host environment for quick dev"
	@echo "  setup-container  - Setup container environment for full testing"
	@echo "  clean            - Clean up virtual environments"
	@echo "  eval-real        - Run evaluation with real profile"
	@echo "  eval-gold        - Run evaluation with gold profile"
	@echo "  eval-mock        - Run evaluation with mock profile"
	@echo "  test-profiles    - Run profile configuration tests"
	@echo "  help             - Show this help message"
