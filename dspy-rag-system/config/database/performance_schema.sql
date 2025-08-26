-- Performance Data Storage Schema for PRD Creation Workflow
-- Supports high-volume performance metrics with efficient querying and data retention

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Performance metrics collection points
CREATE TYPE collection_point_type AS ENUM (
    'workflow_start',
    'section_analysis',
    'template_processing',
    'context_integration',
    'validation_check',
    'workflow_complete',
    'error_occurred'
);

-- Workflow phases
CREATE TYPE workflow_phase_type AS ENUM (
    'prd_creation',
    'task_generation',
    'task_execution',
    'validation',
    'completion'
);

-- Performance metrics table (partitioned by date)
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID NOT NULL,
    collection_point collection_point_type NOT NULL,
    workflow_phase workflow_phase_type NOT NULL,
    duration_ms DECIMAL(10,3) NOT NULL CHECK (duration_ms >= 0),
    success BOOLEAN NOT NULL DEFAULT true,
    error_message TEXT,
    metadata JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (timestamp);

-- Workflow performance data table
CREATE TABLE workflow_performance (
    workflow_id UUID PRIMARY KEY,
    backlog_item_id VARCHAR(50),
    prd_file_path TEXT,
    task_count INTEGER DEFAULT 0,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    total_duration_ms DECIMAL(10,3) CHECK (total_duration_ms >= 0),
    success BOOLEAN NOT NULL DEFAULT true,
    error_count INTEGER DEFAULT 0,
    context_size_bytes INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Performance analysis results table
CREATE TABLE performance_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID NOT NULL REFERENCES workflow_performance(workflow_id),
    performance_score DECIMAL(5,2) CHECK (performance_score >= 0 AND performance_score <= 100),
    bottlenecks JSONB,
    recommendations JSONB,
    warnings JSONB,
    analysis_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Performance alerts table
CREATE TABLE performance_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID REFERENCES workflow_performance(workflow_id),
    alert_type VARCHAR(50) NOT NULL,
    alert_level VARCHAR(20) NOT NULL CHECK (alert_level IN ('info', 'warning', 'error', 'critical')),
    message TEXT NOT NULL,
    metadata JSONB,
    acknowledged BOOLEAN DEFAULT false,
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Performance trends table (aggregated data for dashboard)
CREATE TABLE performance_trends (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    workflow_phase workflow_phase_type NOT NULL,
    collection_point collection_point_type NOT NULL,
    total_workflows INTEGER DEFAULT 0,
    successful_workflows INTEGER DEFAULT 0,
    failed_workflows INTEGER DEFAULT 0,
    avg_duration_ms DECIMAL(10,3),
    min_duration_ms DECIMAL(10,3),
    max_duration_ms DECIMAL(10,3),
    p50_duration_ms DECIMAL(10,3),
    p95_duration_ms DECIMAL(10,3),
    p99_duration_ms DECIMAL(10,3),
    total_errors INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(date, workflow_phase, collection_point)
);

-- Create partitions for performance_metrics (last 30 days)
DO $$
DECLARE
    partition_date DATE;
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    -- Create partitions for the last 30 days
    FOR i IN 0..29 LOOP
        partition_date := CURRENT_DATE - i;
        partition_name := 'performance_metrics_' || to_char(partition_date, 'YYYY_MM_DD');
        start_date := partition_date;
        end_date := partition_date + INTERVAL '1 day';

        EXECUTE format('
            CREATE TABLE IF NOT EXISTS %I PARTITION OF performance_metrics
            FOR VALUES FROM (%L) TO (%L)
        ', partition_name, start_date, end_date);

        -- Create indexes on partition
        EXECUTE format('
            CREATE INDEX IF NOT EXISTS idx_%I_workflow_id ON %I (workflow_id)
        ', partition_name, partition_name);

        EXECUTE format('
            CREATE INDEX IF NOT EXISTS idx_%I_collection_point ON %I (collection_point)
        ', partition_name, partition_name);

        EXECUTE format('
            CREATE INDEX IF NOT EXISTS idx_%I_timestamp ON %I (timestamp)
        ', partition_name, partition_name);
    END LOOP;
END $$;

-- Create indexes on main tables
CREATE INDEX idx_performance_metrics_workflow_id ON performance_metrics (workflow_id);
CREATE INDEX idx_performance_metrics_collection_point ON performance_metrics (collection_point);
CREATE INDEX idx_performance_metrics_workflow_phase ON performance_metrics (workflow_phase);
CREATE INDEX idx_performance_metrics_timestamp ON performance_metrics (timestamp);
CREATE INDEX idx_performance_metrics_success ON performance_metrics (success);

CREATE INDEX idx_workflow_performance_backlog_item_id ON workflow_performance (backlog_item_id);
CREATE INDEX idx_workflow_performance_start_time ON workflow_performance (start_time);
CREATE INDEX idx_workflow_performance_success ON workflow_performance (success);
CREATE INDEX idx_workflow_performance_total_duration ON workflow_performance (total_duration_ms);

CREATE INDEX idx_performance_analysis_workflow_id ON performance_analysis (workflow_id);
CREATE INDEX idx_performance_analysis_score ON performance_analysis (performance_score);
CREATE INDEX idx_performance_analysis_timestamp ON performance_analysis (analysis_timestamp);

CREATE INDEX idx_performance_alerts_workflow_id ON performance_alerts (workflow_id);
CREATE INDEX idx_performance_alerts_level ON performance_alerts (alert_level);
CREATE INDEX idx_performance_alerts_acknowledged ON performance_alerts (acknowledged);
CREATE INDEX idx_performance_alerts_created_at ON performance_alerts (created_at);

CREATE INDEX idx_performance_trends_date ON performance_trends (date);
CREATE INDEX idx_performance_trends_phase ON performance_trends (workflow_phase);
CREATE INDEX idx_performance_trends_collection_point ON performance_trends (collection_point);

-- Create GIN indexes for JSONB columns
CREATE INDEX idx_performance_metrics_metadata ON performance_metrics USING GIN (metadata);
CREATE INDEX idx_performance_analysis_bottlenecks ON performance_analysis USING GIN (bottlenecks);
CREATE INDEX idx_performance_analysis_recommendations ON performance_analysis USING GIN (recommendations);
CREATE INDEX idx_performance_alerts_metadata ON performance_alerts USING GIN (metadata);

-- Functions for data management

-- Function to insert performance metric
CREATE OR REPLACE FUNCTION insert_performance_metric(
    p_workflow_id UUID,
    p_collection_point collection_point_type,
    p_workflow_phase workflow_phase_type,
    p_duration_ms DECIMAL(10,3),
    p_success BOOLEAN DEFAULT true,
    p_error_message TEXT DEFAULT NULL,
    p_metadata JSONB DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    metric_id UUID;
BEGIN
    INSERT INTO performance_metrics (
        workflow_id,
        collection_point,
        workflow_phase,
        duration_ms,
        success,
        error_message,
        metadata
    ) VALUES (
        p_workflow_id,
        p_collection_point,
        p_workflow_phase,
        p_duration_ms,
        p_success,
        p_error_message,
        p_metadata
    ) RETURNING id INTO metric_id;

    RETURN metric_id;
END;
$$ LANGUAGE plpgsql;

-- Function to insert workflow performance data
CREATE OR REPLACE FUNCTION insert_workflow_performance(
    p_workflow_id UUID,
    p_backlog_item_id VARCHAR(50) DEFAULT NULL,
    p_prd_file_path TEXT DEFAULT NULL,
    p_task_count INTEGER DEFAULT 0,
    p_start_time TIMESTAMPTZ,
    p_end_time TIMESTAMPTZ DEFAULT NULL,
    p_total_duration_ms DECIMAL(10,3) DEFAULT NULL,
    p_success BOOLEAN DEFAULT true,
    p_error_count INTEGER DEFAULT 0,
    p_context_size_bytes INTEGER DEFAULT 0
) RETURNS UUID AS $$
BEGIN
    INSERT INTO workflow_performance (
        workflow_id,
        backlog_item_id,
        prd_file_path,
        task_count,
        start_time,
        end_time,
        total_duration_ms,
        success,
        error_count,
        context_size_bytes
    ) VALUES (
        p_workflow_id,
        p_backlog_item_id,
        p_prd_file_path,
        p_task_count,
        p_start_time,
        p_end_time,
        p_total_duration_ms,
        p_success,
        p_error_count,
        p_context_size_bytes
    ) ON CONFLICT (workflow_id) DO UPDATE SET
        end_time = EXCLUDED.end_time,
        total_duration_ms = EXCLUDED.total_duration_ms,
        success = EXCLUDED.success,
        error_count = EXCLUDED.error_count,
        updated_at = NOW();

    RETURN p_workflow_id;
END;
$$ LANGUAGE plpgsql;

-- Function to insert performance analysis
CREATE OR REPLACE FUNCTION insert_performance_analysis(
    p_workflow_id UUID,
    p_performance_score DECIMAL(5,2),
    p_bottlenecks JSONB DEFAULT NULL,
    p_recommendations JSONB DEFAULT NULL,
    p_warnings JSONB DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    analysis_id UUID;
BEGIN
    INSERT INTO performance_analysis (
        workflow_id,
        performance_score,
        bottlenecks,
        recommendations,
        warnings
    ) VALUES (
        p_workflow_id,
        p_performance_score,
        p_bottlenecks,
        p_recommendations,
        p_warnings
    ) RETURNING id INTO analysis_id;

    RETURN analysis_id;
END;
$$ LANGUAGE plpgsql;

-- Function to create performance alert
CREATE OR REPLACE FUNCTION create_performance_alert(
    p_workflow_id UUID DEFAULT NULL,
    p_alert_type VARCHAR(50),
    p_alert_level VARCHAR(20),
    p_message TEXT,
    p_metadata JSONB DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    alert_id UUID;
BEGIN
    INSERT INTO performance_alerts (
        workflow_id,
        alert_type,
        alert_level,
        message,
        metadata
    ) VALUES (
        p_workflow_id,
        p_alert_type,
        p_alert_level,
        p_message,
        p_metadata
    ) RETURNING id INTO alert_id;

    RETURN alert_id;
END;
$$ LANGUAGE plpgsql;

-- Function to update performance trends
CREATE OR REPLACE FUNCTION update_performance_trends(
    p_date DATE DEFAULT CURRENT_DATE
) RETURNS VOID AS $$
BEGIN
    -- Delete existing trends for the date
    DELETE FROM performance_trends WHERE date = p_date;

    -- Insert aggregated trends
    INSERT INTO performance_trends (
        date,
        workflow_phase,
        collection_point,
        total_workflows,
        successful_workflows,
        failed_workflows,
        avg_duration_ms,
        min_duration_ms,
        max_duration_ms,
        p50_duration_ms,
        p95_duration_ms,
        p99_duration_ms,
        total_errors
    )
    SELECT
        p_date,
        pm.workflow_phase,
        pm.collection_point,
        COUNT(DISTINCT pm.workflow_id) as total_workflows,
        COUNT(DISTINCT CASE WHEN pm.success THEN pm.workflow_id END) as successful_workflows,
        COUNT(DISTINCT CASE WHEN NOT pm.success THEN pm.workflow_id END) as failed_workflows,
        AVG(pm.duration_ms) as avg_duration_ms,
        MIN(pm.duration_ms) as min_duration_ms,
        MAX(pm.duration_ms) as max_duration_ms,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pm.duration_ms) as p50_duration_ms,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY pm.duration_ms) as p95_duration_ms,
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY pm.duration_ms) as p99_duration_ms,
        COUNT(CASE WHEN NOT pm.success THEN 1 END) as total_errors
    FROM performance_metrics pm
    WHERE DATE(pm.timestamp) = p_date
    GROUP BY pm.workflow_phase, pm.collection_point;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old data (data retention)
CREATE OR REPLACE FUNCTION cleanup_old_performance_data(
    p_retention_days INTEGER DEFAULT 30
) RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
    cutoff_date DATE;
BEGIN
    cutoff_date := CURRENT_DATE - p_retention_days;

    -- Delete old performance metrics (partitions will be dropped automatically)
    DELETE FROM performance_metrics
    WHERE timestamp < cutoff_date;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    -- Delete old workflow performance data
    DELETE FROM workflow_performance
    WHERE start_time < cutoff_date;

    -- Delete old performance analysis
    DELETE FROM performance_analysis
    WHERE analysis_timestamp < cutoff_date;

    -- Delete old alerts (keep for 90 days)
    DELETE FROM performance_alerts
    WHERE created_at < (CURRENT_DATE - 90);

    -- Delete old trends (keep for 365 days)
    DELETE FROM performance_trends
    WHERE date < (CURRENT_DATE - 365);

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Views for common queries

-- View for workflow performance summary
CREATE VIEW workflow_performance_summary AS
SELECT
    wp.workflow_id,
    wp.backlog_item_id,
    wp.prd_file_path,
    wp.task_count,
    wp.start_time,
    wp.end_time,
    wp.total_duration_ms,
    wp.success,
    wp.error_count,
    pa.performance_score,
    pa.bottlenecks,
    pa.recommendations,
    pa.warnings
FROM workflow_performance wp
LEFT JOIN performance_analysis pa ON wp.workflow_id = pa.workflow_id;

-- View for collection point performance
CREATE VIEW collection_point_performance AS
SELECT
    collection_point,
    workflow_phase,
    COUNT(*) as total_metrics,
    COUNT(CASE WHEN success THEN 1 END) as successful_metrics,
    COUNT(CASE WHEN NOT success THEN 1 END) as failed_metrics,
    AVG(duration_ms) as avg_duration_ms,
    MIN(duration_ms) as min_duration_ms,
    MAX(duration_ms) as max_duration_ms,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_ms) as p50_duration_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) as p95_duration_ms,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY duration_ms) as p99_duration_ms
FROM performance_metrics
GROUP BY collection_point, workflow_phase;

-- View for recent alerts
CREATE VIEW recent_alerts AS
SELECT
    pa.id,
    pa.workflow_id,
    pa.alert_type,
    pa.alert_level,
    pa.message,
    pa.acknowledged,
    pa.created_at,
    wp.backlog_item_id,
    wp.prd_file_path
FROM performance_alerts pa
LEFT JOIN workflow_performance wp ON pa.workflow_id = wp.workflow_id
WHERE pa.created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY pa.created_at DESC;

-- Triggers for automatic updates

-- Trigger to update workflow performance when metrics are inserted
CREATE OR REPLACE FUNCTION update_workflow_performance_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Update workflow performance with latest metrics
    UPDATE workflow_performance
    SET
        end_time = NEW.timestamp,
        total_duration_ms = (
            SELECT SUM(duration_ms)
            FROM performance_metrics
            WHERE workflow_id = NEW.workflow_id
        ),
        error_count = (
            SELECT COUNT(*)
            FROM performance_metrics
            WHERE workflow_id = NEW.workflow_id AND NOT success
        ),
        updated_at = NOW()
    WHERE workflow_id = NEW.workflow_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_workflow_performance
    AFTER INSERT ON performance_metrics
    FOR EACH ROW
    EXECUTE FUNCTION update_workflow_performance_trigger();

-- Trigger to create alerts for performance issues
CREATE OR REPLACE FUNCTION create_performance_alert_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Alert for slow workflows (>15 seconds)
    IF NEW.total_duration_ms > 15000 THEN
        PERFORM create_performance_alert(
            NEW.workflow_id,
            'slow_workflow',
            'warning',
            format('Workflow took %.1fms (threshold: 15000ms)', NEW.total_duration_ms),
            jsonb_build_object('duration_ms', NEW.total_duration_ms, 'threshold_ms', 15000)
        );
    END IF;

    -- Alert for failed workflows
    IF NOT NEW.success THEN
        PERFORM create_performance_alert(
            NEW.workflow_id,
            'workflow_failure',
            'error',
            format('Workflow failed with %s errors', NEW.error_count),
            jsonb_build_object('error_count', NEW.error_count)
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_create_performance_alerts
    AFTER INSERT OR UPDATE ON workflow_performance
    FOR EACH ROW
    EXECUTE FUNCTION create_performance_alert_trigger();

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO your_app_user;

-- Create a scheduled job to update trends daily (requires pg_cron extension)
-- SELECT cron.schedule('update-performance-trends', '0 1 * * *', 'SELECT update_performance_trends();');

-- Create a scheduled job to cleanup old data weekly (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-performance-data', '0 2 * * 0', 'SELECT cleanup_old_performance_data();');
