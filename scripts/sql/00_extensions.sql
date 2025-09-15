-- 00_extensions.sql
-- Safe to re-run extensions setup

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Optional, only if you're using it for eval telemetry:
CREATE EXTENSION IF NOT EXISTS timescaledb;
