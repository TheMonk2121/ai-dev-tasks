# Automation and Pipelines

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Canonical automation and pipelines guide (n8n, Scribe, background workers) | Setting up or modifying automations | Use patterns here; cross-link to 11 for observability |

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

## 🏗️ Reference Architecture

### Components
- n8n server and workflows (HTTP triggers, schedulers)
- Scribe capture pipeline (session registry, summaries, reporting)
- Webhook/API services (Flask/FastAPI) for orchestration
- Observability hooks into 11 (metrics, health, alerts)

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
