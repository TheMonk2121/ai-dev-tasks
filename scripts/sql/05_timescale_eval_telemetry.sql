-- 05_timescale_eval_telemetry.sql
-- TimescaleDB tables for eval telemetry

CREATE TABLE IF NOT EXISTS eval_event (
  ts            TIMESTAMPTZ NOT NULL,
  run_id        TEXT NOT NULL,
  case_id       TEXT NOT NULL,
  stage         TEXT NOT NULL,              -- 'rewrite','retrieve','rerank','reader','score'
  metric_name   TEXT NOT NULL,              -- 'latency_ms','tokens_in','tokens_out','f1','recall_at_5',...
  metric_value  DOUBLE PRECISION NOT NULL,
  model         TEXT,
  tag           TEXT,
  ok            BOOLEAN,
  meta          JSONB NOT NULL DEFAULT '{}'
);

SELECT create_hypertable('eval_event', 'ts', if_not_exists => TRUE);

-- Compression & retention policies (tune windows to taste)
-- Use IF NOT EXISTS to avoid errors if policies already exist
DO $$
BEGIN
  -- Compression policy
  BEGIN
    ALTER TABLE eval_event SET (
      timescaledb.compress,
      timescaledb.compress_segmentby = 'run_id'
    );
    PERFORM add_compression_policy('eval_event', INTERVAL '3 days');
  EXCEPTION WHEN OTHERS THEN
    -- Ignore if policy already exists
    RAISE NOTICE 'Compression policy already exists or could not be added';
  END;

  -- Retention policy
  BEGIN
    PERFORM add_retention_policy('eval_event', INTERVAL '90 days');
  EXCEPTION WHEN OTHERS THEN
    -- Ignore if policy already exists
    RAISE NOTICE 'Retention policy already exists or could not be added';
  END;
END$$;

-- Continuous aggregate (daily rollup)
CREATE MATERIALIZED VIEW IF NOT EXISTS eval_daily
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 day', ts) AS day,
       tag, model,
       count(*) FILTER (WHERE metric_name='f1' AND ok)               AS ok_cases,
       avg(metric_value) FILTER (WHERE metric_name='f1')              AS f1_avg,
       avg(metric_value) FILTER (WHERE metric_name='latency_ms')      AS p50_latency_ms
FROM eval_event
GROUP BY day, tag, model;

-- Optional run/case dimensions (plain PG for easy joins)
CREATE TABLE IF NOT EXISTS eval_run (
  run_id        TEXT PRIMARY KEY,
  tag           TEXT,
  started_at    TIMESTAMPTZ NOT NULL,
  finished_at   TIMESTAMPTZ,
  model         TEXT,
  meta          JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS eval_case_result (
  run_id        TEXT REFERENCES eval_run(run_id) ON DELETE CASCADE,
  case_id       TEXT NOT NULL,
  f1            DOUBLE PRECISION,
  precision     DOUBLE PRECISION,
  recall        DOUBLE PRECISION,
  latency_ms    DOUBLE PRECISION,
  ok            BOOLEAN,
  meta          JSONB NOT NULL DEFAULT '{}',
  PRIMARY KEY (run_id, case_id)
);
