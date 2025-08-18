# Watch Folder Guide

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

<!-- README_AUTOFIX_START -->
# Auto-generated sections for watch_folder_guide.md
# Generated: 2025-08-17T21:49:49.329747

## Missing sections to add:

## Last Reviewed

2025-08-17

## Owner

Document owner/maintainer information

<!-- README_AUTOFIX_END -->
