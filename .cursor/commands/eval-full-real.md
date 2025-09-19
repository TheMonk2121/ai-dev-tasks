env -u INGEST_RUN_ID -u CHUNK_VARIANT UV_PROJECT_ENVIRONMENT=.venv \
uv run python scripts/evaluation/ragchecker_official_evaluation.py --profile real
