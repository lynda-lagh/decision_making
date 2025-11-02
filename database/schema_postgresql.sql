-- WeeFarm PostgreSQL Database Schema
-- Phase 6: Application Development

-- Drop existing tables if they exist
DROP TABLE IF EXISTS kpi_history CASCADE;
DROP TABLE IF EXISTS kpi_targets CASCADE;
DROP TABLE IF EXISTS kpi_metrics CASCADE;
DROP TABLE IF EXISTS model_performance CASCADE;
DROP TABLE IF EXISTS maintenance_schedule CASCADE;
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS failure_events CASCADE;
DROP TABLE IF EXISTS maintenance_records CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;

-- ===== TABLE 1: equipment =====
CREATE TABLE equipment (
    equipment_id VARCHAR(20) PRIMARY KEY,
    equipment_type VARCHAR(50) NOT NULL,
    brand VARCHAR(50),
    model VARCHAR(50),
    year_manufactured INTEGER CHECK (year_manufactured >= 1900 AND year_manufactured <= 2100),
    purchase_date DATE,
    location VARCHAR(100),
    operating_hours DECIMAL(10, 2) DEFAULT 0 CHECK (operating_hours >= 0),
    last_service_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_equipment_type ON equipment(equipment_type);
CREATE INDEX idx_equipment_location ON equipment(location);

-- ===== TABLE 2: maintenance_records =====
CREATE TABLE maintenance_records (
    record_id SERIAL PRIMARY KEY,
    equipment_id VARCHAR(20) NOT NULL,
    maintenance_date DATE NOT NULL,
    type_id INTEGER NOT NULL CHECK (type_id IN (1, 2, 3)),
    description TEXT,
    technician VARCHAR(100),
    parts_replaced TEXT,
    total_cost DECIMAL(10, 2) CHECK (total_cost >= 0),
    downtime_hours DECIMAL(5, 2) CHECK (downtime_hours >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id) ON DELETE CASCADE
);

CREATE INDEX idx_maintenance_equipment ON maintenance_records(equipment_id);
CREATE INDEX idx_maintenance_date ON maintenance_records(maintenance_date);
CREATE INDEX idx_maintenance_type ON maintenance_records(type_id);

-- ===== TABLE 3: failure_events =====
CREATE TABLE failure_events (
    failure_id SERIAL PRIMARY KEY,
    equipment_id VARCHAR(20) NOT NULL,
    failure_date DATE NOT NULL,
    failure_type VARCHAR(100),
    severity VARCHAR(20) CHECK (severity IN ('Minor', 'Moderate', 'Critical')),
    description TEXT,
    repair_cost DECIMAL(10, 2) CHECK (repair_cost >= 0),
    downtime_hours DECIMAL(5, 2) CHECK (downtime_hours >= 0),
    prevented_by_maintenance BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id) ON DELETE CASCADE
);

CREATE INDEX idx_failure_equipment ON failure_events(equipment_id);
CREATE INDEX idx_failure_date ON failure_events(failure_date);
CREATE INDEX idx_failure_severity ON failure_events(severity);

-- ===== TABLE 4: predictions =====
CREATE TABLE predictions (
    prediction_id SERIAL PRIMARY KEY,
    equipment_id VARCHAR(20) NOT NULL,
    prediction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    svm_prediction INTEGER CHECK (svm_prediction IN (0, 1)),
    svm_probability DECIMAL(5, 4) CHECK (svm_probability >= 0 AND svm_probability <= 1),
    xgb_prediction INTEGER CHECK (xgb_prediction IN (0, 1)),
    xgb_probability DECIMAL(5, 4) CHECK (xgb_probability >= 0 AND xgb_probability <= 1),
    risk_score DECIMAL(5, 2) CHECK (risk_score >= 0 AND risk_score <= 100),
    priority_level VARCHAR(20) CHECK (priority_level IN ('Critical', 'High', 'Medium', 'Low')),
    recommended_action TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id) ON DELETE CASCADE
);

CREATE INDEX idx_prediction_equipment ON predictions(equipment_id);
CREATE INDEX idx_prediction_date ON predictions(prediction_date);
CREATE INDEX idx_prediction_priority ON predictions(priority_level);

-- ===== TABLE 5: maintenance_schedule =====
CREATE TABLE maintenance_schedule (
    schedule_id SERIAL PRIMARY KEY,
    equipment_id VARCHAR(20) NOT NULL,
    scheduled_date DATE NOT NULL,
    priority_level VARCHAR(20) CHECK (priority_level IN ('Critical', 'High', 'Medium', 'Low')),
    risk_score DECIMAL(5, 2) CHECK (risk_score >= 0 AND risk_score <= 100),
    status VARCHAR(20) DEFAULT 'Scheduled' CHECK (status IN ('Scheduled', 'In Progress', 'Completed', 'Cancelled')),
    assigned_technician VARCHAR(100),
    estimated_cost DECIMAL(10, 2),
    estimated_duration_hours DECIMAL(5, 2),
    actual_start_time TIMESTAMP,
    actual_end_time TIMESTAMP,
    actual_cost DECIMAL(10, 2),
    completion_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id) ON DELETE CASCADE
);

CREATE INDEX idx_schedule_equipment ON maintenance_schedule(equipment_id);
CREATE INDEX idx_schedule_date ON maintenance_schedule(scheduled_date);
CREATE INDEX idx_schedule_priority ON maintenance_schedule(priority_level);
CREATE INDEX idx_schedule_status ON maintenance_schedule(status);

-- ===== TABLE 6: model_performance =====
CREATE TABLE model_performance (
    performance_id SERIAL PRIMARY KEY,
    model_name VARCHAR(50) NOT NULL,
    model_version VARCHAR(20) DEFAULT '1.0',
    evaluation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    accuracy DECIMAL(5, 4) CHECK (accuracy >= 0 AND accuracy <= 1),
    precision_score DECIMAL(5, 4) CHECK (precision_score >= 0 AND precision_score <= 1),
    recall DECIMAL(5, 4) CHECK (recall >= 0 AND recall <= 1),
    f1_score DECIMAL(5, 4) CHECK (f1_score >= 0 AND f1_score <= 1),
    roc_auc DECIMAL(5, 4) CHECK (roc_auc >= 0 AND roc_auc <= 1),
    sample_size INT NOT NULL CHECK (sample_size > 0),
    true_positives INT,
    false_positives INT,
    true_negatives INT,
    false_negatives INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_performance_model ON model_performance(model_name);
CREATE INDEX idx_performance_date ON model_performance(evaluation_date);

-- ===== TABLE 7: kpi_metrics =====
CREATE TABLE kpi_metrics (
    metric_id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_category VARCHAR(50) NOT NULL CHECK (metric_category IN ('Business', 'Technical', 'Operational', 'Model')),
    metric_value DECIMAL(10, 4) NOT NULL,
    target_value DECIMAL(10, 4),
    measurement_date DATE NOT NULL DEFAULT CURRENT_DATE,
    period VARCHAR(20),
    status VARCHAR(20) CHECK (status IN ('Excellent', 'Good', 'Warning', 'Critical')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kpi_name ON kpi_metrics(metric_name);
CREATE INDEX idx_kpi_category ON kpi_metrics(metric_category);
CREATE INDEX idx_kpi_date ON kpi_metrics(measurement_date);
CREATE INDEX idx_kpi_status ON kpi_metrics(status);

-- ===== TABLE 8: kpi_targets =====
CREATE TABLE kpi_targets (
    target_id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL UNIQUE,
    metric_category VARCHAR(50) NOT NULL,
    target_value DECIMAL(10, 4) NOT NULL,
    excellent_threshold DECIMAL(10, 4),
    good_threshold DECIMAL(10, 4),
    warning_threshold DECIMAL(10, 4),
    critical_threshold DECIMAL(10, 4),
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('higher', 'lower')),
    description TEXT,
    unit VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kpi_target_name ON kpi_targets(metric_name);
CREATE INDEX idx_kpi_target_category ON kpi_targets(metric_category);

-- ===== TABLE 9: kpi_history =====
CREATE TABLE kpi_history (
    history_id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL CHECK (period_end >= period_start),
    period_type VARCHAR(20),
    avg_value DECIMAL(10, 4),
    min_value DECIMAL(10, 4),
    max_value DECIMAL(10, 4),
    trend VARCHAR(20) CHECK (trend IN ('Improving', 'Declining', 'Stable')),
    change_percent DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kpi_history_name ON kpi_history(metric_name);
CREATE INDEX idx_kpi_history_period ON kpi_history(period_start, period_end);

-- Success message
SELECT 'Database schema created successfully!' AS status;
SELECT 'Total tables created: 9' AS info;
