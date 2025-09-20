# AI Dev Tasks - Test Targets
# 
# test-fast: Run quick gate tests in host venv (macOS)
# test-full: Run full test suite in container venv (Linux)

.PHONY: test-fast test-full setup-host setup-container clean dsn-resolver-info validate-github-actions

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

dsn-resolver-info:
	@echo "DSN Resolver"
	@echo "Yup—everything funnels through resolve_dsn in src/common/db_dsn.py:93, which normalizes DATABASE_URL/POSTGRES_DSN, guards against mismatches, applies SSL/pgBouncer policies, and logs usage."
	@echo "Coverage lives in tests/db/test_dsn_resolver.py:1, so new code should import common.db_dsn.resolve_dsn() rather than touching env vars directly."

# Validate GitHub Actions workflows for common context issues
validate-github-actions:
	@echo "Validating GitHub Actions workflows..."
	@echo "Checking for problematic context usage..."
	@if grep -r "\$${{ runner\.temp }}" .github/workflows/ --exclude="*.md" 2>/dev/null; then \
		echo "❌ Found problematic \$${{ runner.temp }} usage"; \
		echo "   Fix: Replace with /tmp/ or \$${{ env.RUNNER_TEMP }}"; \
		echo "   Example: HF_HOME: /tmp/hf"; \
		exit 1; \
	fi
	@if grep -r "\$${{ env\.RUNNER_TEMP }}" .github/workflows/ --exclude="*.md" 2>/dev/null; then \
		echo "❌ Found problematic \$${{ env.RUNNER_TEMP }} usage"; \
		echo "   Fix: Replace with /tmp/ for better compatibility"; \
		echo "   Example: HF_HOME: /tmp/hf"; \
		exit 1; \
	fi
	@echo "✅ GitHub Actions workflows validated successfully"
	@echo "   All context usage follows project standards"

# Fix missing Any imports in Python files
fix-any-imports:
	@echo "Fixing missing Any imports in Python files..."
	@python3 scripts/fix_any_imports.py
	@echo "✅ Any import fixes completed"

# MCP Memory Server Management
mcp-start:
	@echo "Starting MCP Memory Server..."
	@cd /Users/danieljacobs/Code/ai-dev-tasks && UV_PROJECT_ENVIRONMENT=.venv uv run python scripts/utilities/memory/mcp_memory_server.py &
	@echo "✅ MCP Memory Server started on localhost:3000"

mcp-stop:
	@echo "Stopping MCP Memory Server..."
	@pkill -f mcp_memory_server || true
	@echo "✅ MCP Memory Server stopped"

mcp-restart: mcp-stop mcp-start
	@echo "✅ MCP Memory Server restarted"

mcp-status:
	@echo "Checking MCP Memory Server status..."
	@if curl -s http://localhost:3000/health > /dev/null 2>&1; then \
		echo "✅ MCP Memory Server is running on localhost:3000"; \
		curl -s http://localhost:3000/health | python3 -m json.tool; \
	else \
		echo "❌ MCP Memory Server is not running"; \
	fi

mcp-test:
	@echo "Testing MCP Memory Server functionality..."
	@curl -X POST http://localhost:3000/mcp/tools/call \
		-H "Content-Type: application/json" \
		-d '{"tool_name": "record_chat_history", "arguments": {"user_input": "MCP server test", "system_output": "Testing MCP server functionality", "project_dir": "/Users/danieljacobs/Code/ai-dev-tasks", "file_operations": "MCP server test", "llm_name": "cursor-ai"}}' \
		| python3 -m json.tool
	@echo "✅ MCP Memory Server test completed"

mcp-logs:
	@echo "Showing MCP Memory Server logs..."
	@tail -20 mcp_server.log

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
	@echo "  dsn-resolver-info - Show centralized DSN resolver guidance"
	@echo "  validate-github-actions - Validate GitHub Actions workflows for context issues"
	@echo "  fix-any-imports  - Fix missing Any imports in Python files"
	@echo "  mcp-start        - Start MCP Memory Server on localhost:3000"
	@echo "  mcp-stop         - Stop MCP Memory Server"
	@echo "  mcp-restart      - Restart MCP Memory Server"
	@echo "  mcp-status       - Check MCP Memory Server status"
	@echo "  mcp-test         - Test MCP Memory Server functionality"
	@echo "  mcp-logs         - Show MCP Memory Server logs"
	@echo "  help             - Show this help message"
