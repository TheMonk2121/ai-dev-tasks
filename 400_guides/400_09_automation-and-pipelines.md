\n+## 🔄 Backlog Automation Hooks
\n+- Pre‑commit: validate backlog ID format and allowed status values.
- CI: run `python3 scripts/backlog_status_tracking.py --check-stale` and publish results to logs/artifacts.
\n+## 🤖 Automated Constitution Checks
\n+- Add CI validators for markdown links, headings, and safety gates.
- Fail fast on constitution violations; report actionable remediation.
- Consider pre‑commit hooks to protect cross‑ref integrity.
# Automation and Pipelines

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Canonical automation and pipelines guide (n8n, Scribe, background workers) | Setting up or modifying automations | Use patterns here; cross-link to 11 for observability |

### CI Gates (from Comprehensive Guide)
- Lint: `ruff check . && black --check .`
- Docs: `markdownlint ./*.md` (MD034 bare URLs, MD040 code lang)
- SQL: `sqlfluff lint .`
- Conflicts: `python scripts/quick_conflict_check.py` and `python scripts/conflict_audit.py --full`

### DSPy Signature Validation in CI
- Validate DSPy signatures during CI to catch schema/IO drift:
  - `python -m dspy_modules.signature_validator_cli --validate-all` (or project script equivalent)
  - Publish validation summary (pass/fail counts, avg validation time) as CI artifacts

### Lint/Error Reduction Policy in CI
- Prioritize safe categories for automated fixes (RUF001, F401, I001, F541). Report diffs.
- Block bulk auto-fixes for dangerous categories (PT009, B007, SIM117, RUF013, SIM102, F841); require manual review job output.

## 🎯 Purpose

Define automation patterns and pipelines (n8n workflows, Scribe capture, background services) that support the development workflow.

## 📋 When to Use This Guide

- Building or modifying automated flows (backlog scrubbing, document processing)
- Integrating pipelines with deployments/monitoring
- Adding background services or scheduled jobs

## 🧭 Overview

- n8n Workflows: backlog scrubbing, notifications, event-driven tasks
- Scribe System: automated context capture and reporting
- Background Workers: scheduled maintenance and processing
- MCP Server Automation: automatic startup, monitoring, and health checks

## 🏗️ Reference Architecture

### Components
- n8n server and workflows (HTTP triggers, schedulers)
- Scribe capture pipeline (session registry, summaries, reporting)
- Webhook/API services (Flask/FastAPI) for orchestration
- Observability hooks into 11 (metrics, health, alerts)
- MCP server automation (LaunchAgent, health monitoring, auto-restart)

### Data Flow
1. Event (commit, PR, backlog change) triggers n8n
2. n8n calls service/webhook → performs action (scrub scores, capture, notify)
3. Results emit metrics → dashboards/alerts

## 🔧 How-To

- Configure n8n workflows; define triggers and actions
- Connect workflows to CI/CD signals and dashboards
- Use Scribe to capture context changes and generate reports

### n8n Backlog Scrubber (Summary)
- Scoring formula `(BV + TC + RR + LE) / Effort`
- Endpoints: `/webhook/backlog-scrubber`, `/health`, `/stats`
- See `400_n8n-backlog-scrubber-guide.md` for API details and troubleshooting

### MCP Server Automation
**Automatic startup, monitoring, and health management for MCP services.**

**Scripts**:
- **`scripts/start_mcp_server.sh`**: Start MCP memory server with port conflict resolution
- **`scripts/setup_mcp_autostart.sh`**: Configure LaunchAgent for automatic startup
- **`scripts/mcp_memory_server.py`**: Main MCP server with monitoring and caching

**LaunchAgent Configuration**:
- **File**: `~/Library/LaunchAgents/com.ai.mcp-memory-server.plist`
- **Auto-start**: Server starts automatically on login
- **Auto-restart**: Automatic restart on failure with throttling
- **Python 3.12**: Ensures correct Python version usage

**Health Monitoring**:
- **Endpoints**: `/health`, `/metrics`, `/status`
- **Auto-restart**: LaunchAgent restarts server on failure
- **Port Management**: Automatic fallback to available ports (3000-3010)
- **Performance**: Cache hit rate monitoring and response time tracking

**Usage**:
```bash
# Start server manually
./scripts/start_mcp_server.sh

# Setup auto-start
./scripts/setup_mcp_autostart.sh

# Check health
curl http://localhost:3000/health

# View metrics
curl http://localhost:3000/metrics

# Status dashboard
open http://localhost:3000/status
```

## 🧪 Validation

- Each pipeline includes health checks and retry logic
- Observability hooks feed into 11 (Ops & Observability)

### Operational Checks
- Health endpoints respond within thresholds
- Retry/backoff configured for transient errors
- Backups or dry-run modes for data updates

## 🔗 Interfaces

- Deployments & Ops: `400_11_deployments-ops-and-observability.md`
- Coding & Testing: `400_05_coding-and-prompting-standards.md`
- Integrations: `400_08_integrations-editor-and-models.md`

## 📚 References

- Observability System: `400_observability-system.md`
- System Overview: `400_03_system-overview-and-architecture.md`

## 📚 References

- Getting Started: `400_00_getting-started-and-index.md`
- Product & Roadmap: `400_12_product-management-and-roadmap.md`

## 📋 Changelog
- 2025-08-28: Reconstructed and expanded automation & pipelines guide from n8n and observability sources.
