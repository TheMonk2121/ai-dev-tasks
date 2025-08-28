# Watch Folder Guide

> DEPRECATED: Content integrated into core guides — see `400_guides/400_11_deployments-ops-and-observability.md` (services/health/monitoring), `400_guides/400_09_automation-and-pipelines.md` (ingestion automation/scripts, CI hooks), `400_guides/400_08_integrations-editor-and-models.md` (ingestion touchpoints, dashboards), and `400_guides/400_00_getting-started-and-index.md` (index). Implementation lives under `dspy-rag-system/watch_folder/` and related scripts.

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Guide for setting up and using folder monitoring | Setting up file monitoring or configuring watch services |
Configure watch folders or monitor current setup |

## TL;DR

- Drop files into `dspy-rag-system/watch_folder/` to auto-ingest.
- Supported: `.txt`, `.md`, `.pdf`, `.csv`.
- Processed files are moved to `dspy-rag-system/processed_documents/`.

## Overview

The watch-folder service monitors `watch_folder/` and securely ingests new files into the vector store.

## Usage

1. Start the environment and services as per `docs/README.md`.
2. Copy or drag files into `dspy-rag-system/watch_folder/`.
3. Verify ingestion via the dashboard or logs.

## Security & Stability

- Filename and path validation to prevent injection.
- File stability polling to avoid partial reads.
- Unsupported files are quarantined in `dspy-rag-system/quarantine/`.

## Troubleshooting

- Ensure the watcher is running (`start_watch_folder.sh` or integrated runner).
- Check logs for validation errors.
- Confirm PostgreSQL/pgvector is reachable.
