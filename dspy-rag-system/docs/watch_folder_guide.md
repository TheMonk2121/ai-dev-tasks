# Watch Folder Guide

## TL;DR

- Drop files into `dspy-rag-system/watch_folder/` to auto-ingest.
- Supported: `.txt`, `.md`, `.pdf`, `.csv`.
- Processed files are moved to `dspy-rag-system/processed_documents/`.

## Overview

The watch-folder service monitors `watch_folder/` and securely ingests new files into the vector store.

## Usage

1. Start the environment and services as per `README.md`.
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
