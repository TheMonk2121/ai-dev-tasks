# AI Development Tasks - Governance Makefile
# Provides convenient commands for validator operations

.PHONY: help gov/validate gov/readme-fix gov/xref gov/ledger-sweep \
	nemo/wake nemo/wake-seq nemo/sleep nemo/sleep-graceful nemo/status

help:
	@echo "AI Development Tasks - Governance Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make gov/validate [SCOPE=...]     - Run validator with CI mode"
	@echo "  make gov/readme-fix SCOPE=...     - Run README autofix (dry-run by default)"
	@echo "  make gov/xref SCOPE=...           - Run XRef scanner (dry-run by default)"
	@echo "  make gov/ledger-sweep             - Check for expired waiver extensions"
	@echo "  make gov/archive-zeroize DRY_RUN=1|0 - Archive zeroization rail"
	@echo "  make gov/archive-manifest         - Rebuild archive manifest"
	@echo "  make gov/shadow-fix DRY_RUN=1|0   - Shadow name fixer"
	@echo "  make gov/status                   - Current validator status"
	@echo "  make gov/counters                 - Clean-day counters"
	@echo "  make help                         - Show this help"
	@echo ""
	@echo "Examples:"
	@echo "  make gov/validate SCOPE=000_core"
	@echo "  make gov/readme-fix SCOPE=500_research"
	@echo "  make gov/xref SCOPE=400_guides"
	@echo "  make gov/archive-zeroize DRY_RUN=1"
	@echo "  make gov/shadow-fix DRY_RUN=1"
	@echo ""
	@echo "Nemo commands:"
	@echo "  make nemo/wake             # Start all (parallel/fast)"
	@echo "  make nemo/wake-seq         # Start all (sequential)"
	@echo "  make nemo/sleep            # Stop all (fast)"
	@echo "  make nemo/sleep-graceful   # Stop all (graceful)"
	@echo "  make nemo/status           # Show Nemo status"

gov/validate:
	@echo "🔍 Running validator in CI mode..."
	@if [ -n "$(SCOPE)" ]; then \
		echo "Scope: $(SCOPE)"; \
		python3 scripts/doc_coherence_validator.py --ci --json --scope $(SCOPE); \
	else \
		python3 scripts/doc_coherence_validator.py --ci --json; \
	fi

gov/readme-fix:
	@if [ -z "$(SCOPE)" ]; then \
		echo "❌ Error: SCOPE is required for gov/readme-fix"; \
		echo "Usage: make gov/readme-fix SCOPE=directory"; \
		exit 1; \
	fi
	@echo "📝 Running README autofix for scope: $(SCOPE)"
	@echo "Note: This is a dry-run. Add --write to actually modify files."
	@python3 scripts/readme_autofix.py --scope $(SCOPE) --dry-run

gov/xref:
	@if [ -z "$(SCOPE)" ]; then \
		echo "❌ Error: SCOPE is required for gov/xref"; \
		echo "Usage: make gov/xref SCOPE=directory"; \
		exit 1; \
	fi
	@echo "🔗 Running XRef scanner for scope: $(SCOPE)"
	@echo "Note: This is a dry-run. Add --write to actually modify files."
	@python3 scripts/xref_apply.py --scope $(SCOPE) --dry-run

gov/ledger-sweep:
	@echo "🧹 Checking for expired waiver extensions..."
	@python3 scripts/ledger_sweep.py

# Nemo convenience targets (avoid 'optimized' filenames)
nemo/wake:
	@cd dspy-rag-system && ./wake_up_nemo.sh --parallel

nemo/wake-seq:
	@cd dspy-rag-system && ./wake_up_nemo.sh --sequential

nemo/sleep:
	@cd dspy-rag-system && ./sleep_nemo.sh --fast

nemo/sleep-graceful:
	@cd dspy-rag-system && ./sleep_nemo.sh --graceful

nemo/status:
	@cd dspy-rag-system && ./wake_up_nemo.sh --status

# Additional convenience commands
gov/status:
	@echo "📊 Current validator status:"
	@python3 scripts/doc_coherence_validator.py --ci --json | python3 -c "import json, sys; data=json.load(sys.stdin); print('Categories:'); [print(f'  {k}: {v.get(\"violations\", 0)} violations') for k,v in data.get('categories', {}).items()]"

gov/counters:
	@echo "📈 Clean-day counters:"
	@python3 -c "import json; counters=json.load(open('data/validator_counters.json')); targets={'archive':3,'shadow_fork':7,'multirep':5,'readme':14}; [print(f'  {k}: {v}/{targets.get(k,\"-\")} days') for k,v in counters.items()]"

gov/archive-manifest:
	@echo "🔍 Rebuilding archive manifest..."
	@python3 scripts/archive_manifest_rebuild.py

gov/archive-zeroize:
	@if [ -z "$(DRY_RUN)" ]; then \
		echo "❌ Error: DRY_RUN is required for gov/archive-zeroize"; \
		echo "Usage: make gov/archive-zeroize DRY_RUN=1 (dry-run) or DRY_RUN=0 (write)"; \
		exit 1; \
	fi
	@echo "🔧 Running archive zeroization rail..."
	@if [ "$(DRY_RUN)" = "1" ]; then \
		echo "Mode: Dry run (no changes)"; \
		python3 scripts/archive_restore.py --dry-run; \
	else \
		echo "Mode: Write (applying changes)"; \
		python3 scripts/archive_restore.py --write; \
	fi

gov/shadow-fix:
	@if [ -z "$(DRY_RUN)" ]; then \
		echo "❌ Error: DRY_RUN is required for gov/shadow-fix"; \
		echo "Usage: make gov/shadow-fix DRY_RUN=1 (dry-run) or DRY_RUN=0 (write)"; \
		exit 1; \
	fi
	@echo "🔧 Running shadow name fixer..."
	@if [ "$(DRY_RUN)" = "1" ]; then \
		echo "Mode: Dry run (no changes)"; \
		python3 scripts/fix_shadow_names.py --dry-run; \
	else \
		echo "Mode: Write (applying changes)"; \
		python3 scripts/fix_shadow_names.py --write; \
	fi
