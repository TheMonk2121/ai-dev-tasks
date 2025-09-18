-- TimescaleDB Optimization Script for Evaluation System
-- This script enhances our TimescaleDB setup for better evaluation analytics

-- =============================================================================
-- 1. ENHANCED CONTINUOUS AGGREGATES
-- =============================================================================

-- Hourly aggregation for detailed analysis
CREATE MATERIALIZED VIEW IF NOT EXISTS eval_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour'::interval, ts) AS hour,
    tag,
    model,
    stage,
    count(*) FILTER (WHERE metric_name = 'f1' AND ok) AS ok_cases,
    avg(metric_value) FILTER (WHERE metric_name = 'f1') AS f1_avg,
    min(metric_value) FILTER (WHERE metric_name = 'f1') AS f1_min,
    max(metric_value) FILTER (WHERE metric_name = 'f1') AS f1_max,
    avg(metric_value) FILTER (WHERE metric_name = 'latency_ms') AS p50_latency_ms,
    min(metric_value) FILTER (WHERE metric_name = 'latency_ms') AS min_latency_ms,
    max(metric_value) FILTER (WHERE metric_name = 'latency_ms') AS max_latency_ms,
    count(*) FILTER (WHERE metric_name = 'precision') AS precision_samples,
    avg(metric_value) FILTER (WHERE metric_name = 'precision') AS precision_avg,
    avg(metric_value) FILTER (WHERE metric_name = 'recall') AS recall_avg,
    avg(metric_value) FILTER (WHERE metric_name = 'faithfulness') AS faithfulness_avg
FROM eval_event
GROUP BY time_bucket('1 hour'::interval, ts), tag, model, stage;

-- Weekly aggregation for trend analysis
CREATE MATERIALIZED VIEW IF NOT EXISTS eval_weekly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 week'::interval, ts) AS week,
    tag,
    model,
    count(*) FILTER (WHERE metric_name = 'f1' AND ok) AS ok_cases,
    avg(metric_value) FILTER (WHERE metric_name = 'f1') AS f1_avg,
    stddev(metric_value) FILTER (WHERE metric_name = 'f1') AS f1_stddev,
    avg(metric_value) FILTER (WHERE metric_name = 'latency_ms') AS p50_latency_ms,
    percentile_cont(0.95) WITHIN GROUP (ORDER BY metric_value) FILTER (WHERE metric_name = 'latency_ms') AS p95_latency_ms,
    count(*) FILTER (WHERE metric_name = 'precision') AS total_cases,
    avg(metric_value) FILTER (WHERE metric_name = 'precision') AS precision_avg,
    avg(metric_value) FILTER (WHERE metric_name = 'recall') AS recall_avg,
    avg(metric_value) FILTER (WHERE metric_name = 'faithfulness') AS faithfulness_avg
FROM eval_event
GROUP BY time_bucket('1 week'::interval, ts), tag, model;

-- Monthly aggregation for long-term trends
CREATE MATERIALIZED VIEW IF NOT EXISTS eval_monthly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 month'::interval, ts) AS month,
    tag,
    model,
    count(*) FILTER (WHERE metric_name = 'f1' AND ok) AS ok_cases,
    avg(metric_value) FILTER (WHERE metric_name = 'f1') AS f1_avg,
    stddev(metric_value) FILTER (WHERE metric_name = 'f1') AS f1_stddev,
    avg(metric_value) FILTER (WHERE metric_name = 'latency_ms') AS p50_latency_ms,
    percentile_cont(0.99) WITHIN GROUP (ORDER BY metric_value) FILTER (WHERE metric_name = 'latency_ms') AS p99_latency_ms,
    count(*) FILTER (WHERE metric_name = 'precision') AS total_cases,
    avg(metric_value) FILTER (WHERE metric_name = 'precision') AS precision_avg,
    avg(metric_value) FILTER (WHERE metric_name = 'recall') AS recall_avg,
    avg(metric_value) FILTER (WHERE metric_name = 'faithfulness') AS faithfulness_avg
FROM eval_event
GROUP BY time_bucket('1 month'::interval, ts), tag, model;

-- =============================================================================
-- 2. COMPRESSION POLICIES
-- =============================================================================

-- Add compression policy for eval_event (compress data older than 7 days)
SELECT add_compression_policy('eval_event', INTERVAL '7 days');

-- Add compression policy for eval_run (compress data older than 30 days)
SELECT add_compression_policy('eval_run', INTERVAL '30 days');

-- =============================================================================
-- 3. RETENTION POLICIES
-- =============================================================================

-- Keep eval_event data for 1 year
SELECT add_retention_policy('eval_event', INTERVAL '1 year');

-- Keep eval_run data for 2 years
SELECT add_retention_policy('eval_run', INTERVAL '2 years');

-- Keep eval_case_result data for 1 year
SELECT add_retention_policy('eval_case_result', INTERVAL '1 year');

-- =============================================================================
-- 4. ADDITIONAL HYPERTABLES
-- =============================================================================

-- Convert eval_run to hypertable if not already
SELECT create_hypertable('eval_run', 'created_at', if_not_exists => TRUE);

-- Convert eval_case_result to hypertable if not already
SELECT create_hypertable('eval_case_result', 'created_at', if_not_exists => TRUE);

-- =============================================================================
-- 5. PERFORMANCE INDEXES
-- =============================================================================

-- Index for common query patterns
CREATE INDEX IF NOT EXISTS idx_eval_event_run_id_ts ON eval_event (run_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_eval_event_metric_name_ts ON eval_event (metric_name, ts DESC);
CREATE INDEX IF NOT EXISTS idx_eval_event_stage_ts ON eval_event (stage, ts DESC);
CREATE INDEX IF NOT EXISTS idx_eval_event_model_ts ON eval_event (model, ts DESC);

-- Composite index for filtering
CREATE INDEX IF NOT EXISTS idx_eval_event_composite ON eval_event (run_id, stage, metric_name, ts DESC);

-- =============================================================================
-- 6. USEFUL QUERIES FOR ANALYSIS
-- =============================================================================

-- View for evaluation performance trends
CREATE OR REPLACE VIEW evaluation_performance_trends AS
SELECT 
    day,
    tag,
    model,
    ok_cases,
    f1_avg,
    p50_latency_ms,
    CASE 
        WHEN LAG(f1_avg) OVER (PARTITION BY tag, model ORDER BY day) IS NOT NULL 
        THEN f1_avg - LAG(f1_avg) OVER (PARTITION BY tag, model ORDER BY day)
        ELSE NULL 
    END AS f1_change,
    CASE 
        WHEN LAG(p50_latency_ms) OVER (PARTITION BY tag, model ORDER BY day) IS NOT NULL 
        THEN p50_latency_ms - LAG(p50_latency_ms) OVER (PARTITION BY tag, model ORDER BY day)
        ELSE NULL 
    END AS latency_change
FROM eval_daily
ORDER BY day DESC, tag, model;

-- View for evaluation quality metrics
CREATE OR REPLACE VIEW evaluation_quality_metrics AS
SELECT 
    run_id,
    tag,
    model,
    started_at,
    finished_at,
    EXTRACT(EPOCH FROM (finished_at - started_at)) AS duration_seconds,
    (SELECT COUNT(*) FROM eval_case_result WHERE run_id = er.run_id) AS total_cases,
    (SELECT COUNT(*) FROM eval_case_result WHERE run_id = er.run_id AND ok = true) AS successful_cases,
    (SELECT AVG(f1) FROM eval_case_result WHERE run_id = er.run_id) AS avg_f1,
    (SELECT AVG(precision) FROM eval_case_result WHERE run_id = er.run_id) AS avg_precision,
    (SELECT AVG(recall) FROM eval_case_result WHERE run_id = er.run_id) AS avg_recall,
    (SELECT AVG(latency_ms) FROM eval_case_result WHERE run_id = er.run_id) AS avg_latency_ms
FROM eval_run er
ORDER BY started_at DESC;

-- =============================================================================
-- 7. ALERTING QUERIES
-- =============================================================================

-- Query for performance degradation alerts
CREATE OR REPLACE VIEW performance_degradation_alerts AS
SELECT 
    tag,
    model,
    day,
    f1_avg,
    LAG(f1_avg) OVER (PARTITION BY tag, model ORDER BY day) AS prev_f1_avg,
    f1_avg - LAG(f1_avg) OVER (PARTITION BY tag, model ORDER BY day) AS f1_delta,
    CASE 
        WHEN f1_avg - LAG(f1_avg) OVER (PARTITION BY tag, model ORDER BY day) < -0.1 
        THEN 'F1_DEGRADATION'
        WHEN p50_latency_ms - LAG(p50_latency_ms) OVER (PARTITION BY tag, model ORDER BY day) > 1000
        THEN 'LATENCY_INCREASE'
        ELSE NULL
    END AS alert_type
FROM eval_daily
WHERE day >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY day DESC, tag, model;
