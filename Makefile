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

# Help target
help:
	@echo "Available targets:"
	@echo "  test-fast        - Run quick gate tests in host venv (macOS)"
	@echo "  test-full        - Run full test suite in container venv (Linux)"
	@echo "  test-full-cached - Run full test suite with cached venv (faster)"
	@echo "  setup-host       - Setup host environment for quick dev"
	@echo "  setup-container  - Setup container environment for full testing"
	@echo "  clean            - Clean up virtual environments"
	@echo "  help             - Show this help message"
