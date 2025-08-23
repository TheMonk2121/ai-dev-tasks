# System Service Guide

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Guide for managing and configuring system services | Setting up services or troubleshooting system issues | Configure
services or resolve current issues |

## TL;DR

- Run background processing as a long-lived service.
- Provides health/readiness endpoints and monitoring.
- Integrates with mission dashboard and retry logic.

## Overview

This guide explains running the RAG pipeline components as system services (local dev or containerized).

## Starting Services

- Dashboard: `python3 src/dashboard.py`
- Mission dashboard: `./start_mission_dashboard.sh`
- Watch folder: `./start_watch_folder.sh`

## Health & Monitoring

- Health endpoints: `/health`, `/ready`
- Metrics: `/api/monitoring` (production metrics and security events)

## Reliability

- Central retry wrapper with exponential backoff
- Connection pooling for the vector store

## Troubleshooting

- Ensure environment variables and DB connectivity
- Check logs for failed retries and circuit-breaker events
