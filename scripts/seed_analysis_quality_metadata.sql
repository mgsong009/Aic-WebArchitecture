USE aic_db;

CREATE TABLE IF NOT EXISTS analysis_run_metadata (
    id                       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    job_id                   INT UNSIGNED NOT NULL UNIQUE,
    metric_version           VARCHAR(64),
    baseline_version         VARCHAR(64),
    optimized_version        VARCHAR(64),
    processed_count          INT,
    total_runtime_ms         FLOAT,
    baseline_runtime_ms      FLOAT,
    runtime_delta_pct        FLOAT,
    memory_peak_kb           FLOAT,
    baseline_memory_peak_kb  FLOAT,
    memory_delta_pct         FLOAT,
    stage_runtimes_ms        JSON,
    score_deltas             JSON,
    quality_passed           BOOLEAN,
    bootstrap_passed         BOOLEAN,
    measured_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES analysis_jobs(id) ON DELETE CASCADE,
    INDEX idx_measured_at (measured_at)
) ENGINE=InnoDB;

INSERT INTO analysis_jobs (
    job_uuid,
    submission_id,
    status,
    error_message,
    created_at,
    started_at,
    completed_at
) VALUES (
    '11111111-1111-4111-8111-111111111111',
    5,
    'done',
    NULL,
    '2025-04-03 16:05:00',
    '2025-04-03 16:05:01',
    '2025-04-03 16:05:09'
) ON DUPLICATE KEY UPDATE
    status = VALUES(status),
    error_message = VALUES(error_message),
    started_at = VALUES(started_at),
    completed_at = VALUES(completed_at),
    id = LAST_INSERT_ID(id);

SET @analysis_quality_job_id = LAST_INSERT_ID();

INSERT INTO analysis_run_metadata (
    job_id,
    metric_version,
    baseline_version,
    optimized_version,
    processed_count,
    total_runtime_ms,
    baseline_runtime_ms,
    runtime_delta_pct,
    memory_peak_kb,
    baseline_memory_peak_kb,
    memory_delta_pct,
    stage_runtimes_ms,
    score_deltas,
    quality_passed,
    bootstrap_passed,
    measured_at
) VALUES (
    @analysis_quality_job_id,
    'aic-metrics-2026.05',
    'pipeline-baseline-token-loop',
    'pipeline-optimized-batch-v1',
    32,
    8120.0,
    14180.0,
    -42.736,
    196608.0,
    245760.0,
    -20.0,
    JSON_OBJECT(
        'input_validation', 420.0,
        'token_features', 960.0,
        'embedding', 4120.0,
        'metric_scoring', 1840.0,
        'bootstrap_validation', 780.0
    ),
    JSON_OBJECT(
        'pi', 0.0,
        'ui', 0.0,
        'oi', 0.0,
        'aic', 0.0
    ),
    TRUE,
    TRUE,
    '2025-04-03 16:05:10'
) ON DUPLICATE KEY UPDATE
    metric_version = VALUES(metric_version),
    baseline_version = VALUES(baseline_version),
    optimized_version = VALUES(optimized_version),
    processed_count = VALUES(processed_count),
    total_runtime_ms = VALUES(total_runtime_ms),
    baseline_runtime_ms = VALUES(baseline_runtime_ms),
    runtime_delta_pct = VALUES(runtime_delta_pct),
    memory_peak_kb = VALUES(memory_peak_kb),
    baseline_memory_peak_kb = VALUES(baseline_memory_peak_kb),
    memory_delta_pct = VALUES(memory_delta_pct),
    stage_runtimes_ms = VALUES(stage_runtimes_ms),
    score_deltas = VALUES(score_deltas),
    quality_passed = VALUES(quality_passed),
    bootstrap_passed = VALUES(bootstrap_passed),
    measured_at = VALUES(measured_at);
