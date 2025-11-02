# PostgreSQL Database Schema
## WeeFarm Predictive Maintenance System

**Project**: WeeFarm  
**Date**: November 1, 2025  
**Database**: PostgreSQL 15+  
**Status**: Design Phase

---

## 📊 Database Overview

### Purpose
Store all equipment data, maintenance records, failure events, predictions, maintenance schedules, and KPI metrics for the WeeFarm predictive maintenance pipeline.

### Key Features
- ✅ Relational data model with foreign keys
- ✅ Indexes for performance optimization
- ✅ Timestamps for audit trail
- ✅ Support for ML pipeline outputs
- ✅ KPI tracking and monitoring
- ✅ Scalable design for growth

---

## 🗄️ Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│    equipment    │
│─────────────────│
│ equipment_id PK │◄─────┐
│ equipment_type  │      │
│ brand           │      │
│ model           │      │
│ location        │      │
│ ...             │      │
└─────────────────┘      │
                         │
         ┌───────────────┼───────────────┬──────────────┬──────────────┐
         │               │               │              │              │
         │               │               │              │              │
┌────────▼────────┐ ┌────▼──────────┐ ┌─▼────────────┐ ┌▼──────────────┐
│ maintenance_    │ │ failure_      │ │ predictions  │ │ maintenance_  │
│ records         │ │ events        │ │              │ │ schedule      │
│─────────────────│ │───────────────│ │──────────────│ │───────────────│
│ record_id PK    │ │ failure_id PK │ │ prediction_  │ │ schedule_id PK│
│ equipment_id FK │ │ equipment_id  │ │ id PK        │ │ equipment_id  │
│ maintenance_date│ │ FK            │ │ equipment_id │ │ FK            │
│ type_id         │ │ failure_date  │ │ FK           │ │ scheduled_date│
│ ...             │ │ ...           │ │ risk_score   │ │ priority_level│
└─────────────────┘ └───────────────┘ │ ...          │ │ ...           │
                                       └──────────────┘ └───────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  KPI TABLES (NEW)                                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ kpi_metrics  │  │ kpi_targets  │  │ kpi_history  │             │
│  │──────────────│  │──────────────│  │──────────────│             │
│  │ metric_id PK │  │ target_id PK │  │ history_id PK│             │
│  │ metric_name  │  │ metric_name  │  │ metric_name  │             │
│  │ metric_value │  │ target_value │  │ avg_value    │             │
│  │ status       │  │ thresholds   │  │ trend        │             │
│  │ date         │  │ direction    │  │ period       │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Table Definitions

### 1. equipment

**Purpose**: Store all agricultural equipment information

```sql
CREATE TABLE equipment (
    -- Primary Key
    equipment_id VARCHAR(10) PRIMARY KEY,
    
    -- Equipment Details
    equipment_type VARCHAR(50) NOT NULL,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year_manufactured INT NOT NULL CHECK (year_manufactured >= 1990 AND year_manufactured <= 2025),
    purchase_date DATE NOT NULL,
    
    -- Location
    location VARCHAR(50) NOT NULL,
    
    -- Usage Metrics
    operating_hours INT NOT NULL DEFAULT 0 CHECK (operating_hours >= 0),
    last_service_date DATE,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    CONSTRAINT chk_purchase_date CHECK (purchase_date <= CURRENT_DATE)
);

-- Indexes for performance
CREATE INDEX idx_equipment_type ON equipment(equipment_type);
CREATE INDEX idx_equipment_location ON equipment(location);
CREATE INDEX idx_equipment_operating_hours ON equipment(operating_hours);
```

**Sample Data**:
```sql
INSERT INTO equipment VALUES
('EQ-001', 'Tractor', 'John Deere', '5075E', 2018, '2018-03-15', 'Jendouba', 3500, '2024-10-15', NOW(), NOW()),
('EQ-002', 'Harvester', 'Case IH', 'Axial-Flow 250', 2020, '2020-06-20', 'Nabeul', 2100, '2024-09-20', NOW(), NOW());
```

---

### 2. maintenance_records

**Purpose**: Track all maintenance activities

```sql
CREATE TABLE maintenance_records (
    -- Primary Key
    record_id SERIAL PRIMARY KEY,
    
    -- Foreign Key
    equipment_id VARCHAR(10) NOT NULL REFERENCES equipment(equipment_id) ON DELETE CASCADE,
    
    -- Maintenance Details
    maintenance_date DATE NOT NULL,
    type_id INT NOT NULL CHECK (type_id IN (1, 2, 3)), -- 1: Preventive, 2: Corrective, 3: Predictive
    description TEXT,
    technician VARCHAR(100),
    parts_replaced TEXT,
    
    -- Cost & Downtime
    total_cost DECIMAL(10, 2) NOT NULL CHECK (total_cost >= 0),
    downtime_hours DECIMAL(5, 2) NOT NULL DEFAULT 0 CHECK (downtime_hours >= 0),
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_maintenance_date CHECK (maintenance_date <= CURRENT_DATE)
);

-- Indexes
CREATE INDEX idx_maintenance_equipment ON maintenance_records(equipment_id);
CREATE INDEX idx_maintenance_date ON maintenance_records(maintenance_date);
CREATE INDEX idx_maintenance_type ON maintenance_records(type_id);
```

**Maintenance Types**:
- `1`: Preventive (scheduled, proactive)
- `2`: Corrective (reactive, after failure)
- `3`: Predictive (ML-driven, before failure)

**Sample Data**:
```sql
INSERT INTO maintenance_records (equipment_id, maintenance_date, type_id, description, technician, total_cost, downtime_hours) VALUES
('EQ-001', '2024-10-15', 1, 'Routine oil change and filter replacement', 'Ahmed Ben Ali', 280.00, 2.5),
('EQ-002', '2024-09-20', 2, 'Repair hydraulic system leak', 'Mohamed Trabelsi', 850.00, 8.0);
```

---

### 3. failure_events

**Purpose**: Record all equipment failures

```sql
CREATE TABLE failure_events (
    -- Primary Key
    failure_id SERIAL PRIMARY KEY,
    
    -- Foreign Key
    equipment_id VARCHAR(10) NOT NULL REFERENCES equipment(equipment_id) ON DELETE CASCADE,
    
    -- Failure Details
    failure_date DATE NOT NULL,
    failure_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('Minor', 'Moderate', 'Critical')),
    description TEXT,
    
    -- Impact
    repair_cost DECIMAL(10, 2) NOT NULL CHECK (repair_cost >= 0),
    downtime_hours DECIMAL(5, 2) NOT NULL CHECK (downtime_hours >= 0),
    
    -- Analysis
    prevented_by_maintenance BOOLEAN DEFAULT FALSE,
    root_cause TEXT,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_failure_date CHECK (failure_date <= CURRENT_DATE)
);

-- Indexes
CREATE INDEX idx_failure_equipment ON failure_events(equipment_id);
CREATE INDEX idx_failure_date ON failure_events(failure_date);
CREATE INDEX idx_failure_severity ON failure_events(severity);
```

**Severity Levels**:
- `Minor`: Small issue, minimal impact
- `Moderate`: Significant issue, moderate downtime
- `Critical`: Major failure, extended downtime

**Sample Data**:
```sql
INSERT INTO failure_events (equipment_id, failure_date, failure_type, severity, description, repair_cost, downtime_hours, prevented_by_maintenance) VALUES
('EQ-001', '2024-08-10', 'Engine Overheating', 'Moderate', 'Coolant system failure', 1200.00, 12.0, TRUE),
('EQ-002', '2024-07-15', 'Hydraulic Failure', 'Critical', 'Complete hydraulic system breakdown', 2500.00, 24.0, FALSE);
```

---

### 4. predictions (NEW - Pipeline Output)

**Purpose**: Store ML model predictions

```sql
CREATE TABLE predictions (
    -- Primary Key
    prediction_id SERIAL PRIMARY KEY,
    
    -- Foreign Key
    equipment_id VARCHAR(10) NOT NULL REFERENCES equipment(equipment_id) ON DELETE CASCADE,
    
    -- Prediction Metadata
    prediction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    model_version VARCHAR(20) DEFAULT '1.0',
    
    -- SVM Model Output (Stage 1)
    svm_prediction INT NOT NULL CHECK (svm_prediction IN (0, 1)), -- 0: No Fail, 1: Will Fail
    svm_probability DECIMAL(5, 4) NOT NULL CHECK (svm_probability >= 0 AND svm_probability <= 1),
    
    -- XGBoost Model Output (Stage 2)
    xgb_prediction INT NOT NULL CHECK (xgb_prediction IN (0, 1)),
    xgb_probability DECIMAL(5, 4) NOT NULL CHECK (xgb_probability >= 0 AND xgb_probability <= 1),
    
    -- Final Output
    risk_score DECIMAL(5, 2) NOT NULL CHECK (risk_score >= 0 AND risk_score <= 100), -- 0-100
    priority_level VARCHAR(20) NOT NULL CHECK (priority_level IN ('Critical', 'High', 'Medium', 'Low')),
    recommended_action TEXT,
    
    -- Confidence Metrics
    confidence_score DECIMAL(5, 4),
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_equipment_prediction_date UNIQUE (equipment_id, prediction_date)
);

-- Indexes
CREATE INDEX idx_prediction_equipment ON predictions(equipment_id);
CREATE INDEX idx_prediction_date ON predictions(prediction_date);
CREATE INDEX idx_prediction_priority ON predictions(priority_level);
CREATE INDEX idx_prediction_risk_score ON predictions(risk_score DESC);
```

**Sample Data**:
```sql
INSERT INTO predictions (equipment_id, prediction_date, svm_prediction, svm_probability, xgb_prediction, xgb_probability, risk_score, priority_level, recommended_action) VALUES
('EQ-001', '2024-11-01', 1, 0.8500, 1, 0.7200, 72.00, 'Critical', 'Schedule immediate maintenance within 24 hours'),
('EQ-002', '2024-11-01', 1, 0.6500, 0, 0.3500, 35.00, 'Medium', 'Schedule maintenance within 2 weeks');
```

---

### 5. maintenance_schedule (NEW - Pipeline Output)

**Purpose**: Manage maintenance schedule generated by pipeline

```sql
CREATE TABLE maintenance_schedule (
    -- Primary Key
    schedule_id SERIAL PRIMARY KEY,
    
    -- Foreign Key
    equipment_id VARCHAR(10) NOT NULL REFERENCES equipment(equipment_id) ON DELETE CASCADE,
    prediction_id INT REFERENCES predictions(prediction_id) ON DELETE SET NULL,
    
    -- Schedule Details
    scheduled_date DATE NOT NULL,
    priority_level VARCHAR(20) NOT NULL CHECK (priority_level IN ('Critical', 'High', 'Medium', 'Low')),
    risk_score DECIMAL(5, 2) CHECK (risk_score >= 0 AND risk_score <= 100),
    
    -- Status Tracking
    status VARCHAR(20) NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Scheduled', 'In Progress', 'Completed', 'Cancelled')),
    
    -- Assignment
    assigned_technician VARCHAR(100),
    estimated_duration_hours DECIMAL(5, 2),
    estimated_cost DECIMAL(10, 2),
    
    -- Completion Details
    actual_start_time TIMESTAMP,
    actual_end_time TIMESTAMP,
    actual_cost DECIMAL(10, 2),
    completion_notes TEXT,
    
    -- Additional Info
    notes TEXT,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_scheduled_date CHECK (scheduled_date >= CURRENT_DATE),
    CONSTRAINT chk_actual_times CHECK (actual_end_time IS NULL OR actual_end_time >= actual_start_time)
);

-- Indexes
CREATE INDEX idx_schedule_equipment ON maintenance_schedule(equipment_id);
CREATE INDEX idx_schedule_date ON maintenance_schedule(scheduled_date);
CREATE INDEX idx_schedule_status ON maintenance_schedule(status);
CREATE INDEX idx_schedule_priority ON maintenance_schedule(priority_level);
CREATE INDEX idx_schedule_technician ON maintenance_schedule(assigned_technician);
```

**Status Flow**:
```
Pending → Scheduled → In Progress → Completed
                              ↓
                          Cancelled
```

**Sample Data**:
```sql
INSERT INTO maintenance_schedule (equipment_id, scheduled_date, priority_level, risk_score, status, estimated_cost, notes) VALUES
('EQ-001', '2024-11-02', 'Critical', 72.00, 'Scheduled', 500.00, 'High-risk equipment, immediate attention required'),
('EQ-002', '2024-11-15', 'Medium', 35.00, 'Pending', 280.00, 'Routine preventive maintenance');
```

---

### 6. model_performance (NEW - Monitoring)

**Purpose**: Track ML model performance over time

```sql
CREATE TABLE model_performance (
    -- Primary Key
    performance_id SERIAL PRIMARY KEY,
    
    -- Model Details
    model_name VARCHAR(50) NOT NULL,
    model_version VARCHAR(20) DEFAULT '1.0',
    evaluation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Performance Metrics
    accuracy DECIMAL(5, 4) CHECK (accuracy >= 0 AND accuracy <= 1),
    precision_score DECIMAL(5, 4) CHECK (precision_score >= 0 AND precision_score <= 1),
    recall DECIMAL(5, 4) CHECK (recall >= 0 AND recall <= 1),
    f1_score DECIMAL(5, 4) CHECK (f1_score >= 0 AND f1_score <= 1),
    roc_auc DECIMAL(5, 4) CHECK (roc_auc >= 0 AND roc_auc <= 1),
    
    -- Evaluation Details
    sample_size INT NOT NULL CHECK (sample_size > 0),
    true_positives INT,
    false_positives INT,
    true_negatives INT,
    false_negatives INT,
    
    -- Additional Info
    notes TEXT,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_performance_model ON model_performance(model_name);
CREATE INDEX idx_performance_date ON model_performance(evaluation_date);
```

**Sample Data**:
```sql
INSERT INTO model_performance (model_name, model_version, evaluation_date, accuracy, precision_score, recall, f1_score, roc_auc, sample_size, notes) VALUES
('SVM', '1.0', '2024-11-01', 0.4500, 0.3529, 1.0000, 0.5217, 0.3929, 20, 'Perfect recall, many false positives'),
('XGBoost_RFE', '1.0', '2024-11-01', 0.7500, 0.6000, 0.5000, 0.5455, 0.6667, 20, 'Best F1-score, balanced performance');
```

---

### 7. kpi_metrics (NEW - KPI Tracking)

**Purpose**: Store all KPI measurements over time

```sql
CREATE TABLE kpi_metrics (
    -- Primary Key
    metric_id SERIAL PRIMARY KEY,
    
    -- KPI Identification
    metric_name VARCHAR(100) NOT NULL,
    metric_category VARCHAR(50) NOT NULL,
    
    -- Values
    metric_value DECIMAL(10, 4) NOT NULL,
    target_value DECIMAL(10, 4),
    
    -- Metadata
    measurement_date DATE NOT NULL DEFAULT CURRENT_DATE,
    period VARCHAR(20),
    
    -- Status
    status VARCHAR(20),
    
    -- Additional Info
    notes TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_kpi_category CHECK (metric_category IN ('Business', 'Technical', 'Operational', 'Model')),
    CONSTRAINT chk_kpi_status CHECK (status IN ('Excellent', 'Good', 'Warning', 'Critical'))
);

-- Indexes
CREATE INDEX idx_kpi_name ON kpi_metrics(metric_name);
CREATE INDEX idx_kpi_category ON kpi_metrics(metric_category);
CREATE INDEX idx_kpi_date ON kpi_metrics(measurement_date);
CREATE INDEX idx_kpi_status ON kpi_metrics(status);
```

**Sample Data**:
```sql
INSERT INTO kpi_metrics (metric_name, metric_category, metric_value, target_value, measurement_date, period, status) VALUES
-- Business KPIs
('Cost Reduction %', 'Business', 44.0, 40.0, '2024-11-01', 'Monthly', 'Excellent'),
('ROI %', 'Business', 833.0, 200.0, '2024-11-01', 'Quarterly', 'Excellent'),
('Downtime Avoided Hours', 'Business', 500.0, 400.0, '2024-11-01', 'Monthly', 'Excellent'),

-- Technical KPIs
('System Uptime %', 'Technical', 99.8, 99.5, '2024-11-01', 'Daily', 'Excellent'),
('API Response Time ms', 'Technical', 150.0, 200.0, '2024-11-01', 'Daily', 'Excellent'),
('Pipeline Execution Time s', 'Technical', 12.5, 300.0, '2024-11-01', 'Daily', 'Excellent'),

-- Operational KPIs
('Preventive Maintenance Ratio %', 'Operational', 38.7, 50.0, '2024-11-01', 'Monthly', 'Warning'),
('MTBF Hours', 'Operational', 1633.0, 2000.0, '2024-11-01', 'Monthly', 'Warning'),
('MTTR Hours', 'Operational', 7.5, 8.0, '2024-11-01', 'Monthly', 'Excellent'),

-- Model KPIs
('SVM Recall', 'Model', 100.0, 80.0, '2024-11-01', 'Weekly', 'Excellent'),
('XGBoost Accuracy', 'Model', 75.0, 75.0, '2024-11-01', 'Weekly', 'Good'),
('XGBoost F1 Score', 'Model', 54.5, 70.0, '2024-11-01', 'Weekly', 'Warning');
```

---

### 8. kpi_targets (NEW - KPI Configuration)

**Purpose**: Store target values and thresholds for each KPI

```sql
CREATE TABLE kpi_targets (
    -- Primary Key
    target_id SERIAL PRIMARY KEY,
    
    -- KPI Identification
    metric_name VARCHAR(100) NOT NULL UNIQUE,
    metric_category VARCHAR(50) NOT NULL,
    
    -- Target Values
    target_value DECIMAL(10, 4) NOT NULL,
    
    -- Thresholds (for color coding)
    excellent_threshold DECIMAL(10, 4),
    good_threshold DECIMAL(10, 4),
    warning_threshold DECIMAL(10, 4),
    critical_threshold DECIMAL(10, 4),
    
    -- Direction (higher is better or lower is better)
    direction VARCHAR(10) NOT NULL,
    
    -- Metadata
    description TEXT,
    unit VARCHAR(20),
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_kpi_direction CHECK (direction IN ('higher', 'lower'))
);

-- Indexes
CREATE INDEX idx_kpi_target_name ON kpi_targets(metric_name);
CREATE INDEX idx_kpi_target_category ON kpi_targets(metric_category);
```

**Sample Data**:
```sql
INSERT INTO kpi_targets (metric_name, metric_category, target_value, excellent_threshold, good_threshold, warning_threshold, critical_threshold, direction, unit) VALUES
-- Business KPIs (higher is better)
('Cost Reduction %', 'Business', 40.0, 40.0, 30.0, 20.0, 10.0, 'higher', '%'),
('ROI %', 'Business', 200.0, 500.0, 200.0, 100.0, 50.0, 'higher', '%'),

-- Technical KPIs
('System Uptime %', 'Technical', 99.5, 99.5, 99.0, 98.0, 95.0, 'higher', '%'),
('API Response Time ms', 'Technical', 200.0, 100.0, 200.0, 500.0, 1000.0, 'lower', 'ms'),

-- Operational KPIs
('Preventive Maintenance Ratio %', 'Operational', 50.0, 50.0, 40.0, 30.0, 20.0, 'higher', '%'),
('MTBF Hours', 'Operational', 2000.0, 2000.0, 1500.0, 1000.0, 500.0, 'higher', 'hours'),
('MTTR Hours', 'Operational', 8.0, 4.0, 8.0, 12.0, 24.0, 'lower', 'hours'),

-- Model KPIs
('XGBoost Accuracy', 'Model', 75.0, 80.0, 75.0, 70.0, 60.0, 'higher', '%'),
('XGBoost F1 Score', 'Model', 70.0, 80.0, 70.0, 60.0, 50.0, 'higher', 'score');
```

---

### 9. kpi_history (NEW - Historical Trends)

**Purpose**: Store aggregated KPI data for trend analysis

```sql
CREATE TABLE kpi_history (
    -- Primary Key
    history_id SERIAL PRIMARY KEY,
    
    -- KPI Identification
    metric_name VARCHAR(100) NOT NULL,
    
    -- Time Period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    period_type VARCHAR(20),
    
    -- Aggregated Values
    avg_value DECIMAL(10, 4),
    min_value DECIMAL(10, 4),
    max_value DECIMAL(10, 4),
    
    -- Trend Analysis
    trend VARCHAR(20),
    change_percent DECIMAL(10, 4),
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_kpi_period CHECK (period_end >= period_start),
    CONSTRAINT chk_kpi_trend CHECK (trend IN ('Improving', 'Declining', 'Stable'))
);

-- Indexes
CREATE INDEX idx_kpi_history_name ON kpi_history(metric_name);
CREATE INDEX idx_kpi_history_period ON kpi_history(period_start, period_end);
```

**Sample Data**:
```sql
INSERT INTO kpi_history (metric_name, period_start, period_end, period_type, avg_value, min_value, max_value, trend, change_percent) VALUES
('Cost Reduction %', '2024-10-01', '2024-10-31', 'Monthly', 42.0, 40.0, 44.0, 'Improving', 2.0),
('Preventive Maintenance Ratio %', '2024-10-01', '2024-10-31', 'Monthly', 36.5, 35.0, 38.7, 'Improving', 3.0),
('XGBoost Accuracy', '2024-10-01', '2024-10-31', 'Monthly', 74.5, 72.0, 75.0, 'Stable', 0.5),
('MTBF Hours', '2024-10-01', '2024-10-31', 'Monthly', 1600.0, 1550.0, 1633.0, 'Improving', 1.5);
```

---

## 🔗 Relationships & Constraints

### Foreign Key Relationships

```sql
-- maintenance_records references equipment
ALTER TABLE maintenance_records
    ADD CONSTRAINT fk_maintenance_equipment
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
    ON DELETE CASCADE;

-- failure_events references equipment
ALTER TABLE failure_events
    ADD CONSTRAINT fk_failure_equipment
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
    ON DELETE CASCADE;

-- predictions references equipment
ALTER TABLE predictions
    ADD CONSTRAINT fk_prediction_equipment
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
    ON DELETE CASCADE;

-- maintenance_schedule references equipment and predictions
ALTER TABLE maintenance_schedule
    ADD CONSTRAINT fk_schedule_equipment
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
    ON DELETE CASCADE;

ALTER TABLE maintenance_schedule
    ADD CONSTRAINT fk_schedule_prediction
    FOREIGN KEY (prediction_id) REFERENCES predictions(prediction_id)
    ON DELETE SET NULL;
```

---

## 📊 Views for Common Queries

### 1. Equipment Health View

```sql
CREATE VIEW vw_equipment_health AS
SELECT 
    e.equipment_id,
    e.equipment_type,
    e.brand,
    e.model,
    e.location,
    e.operating_hours,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.purchase_date)) AS age_years,
    COUNT(DISTINCT m.record_id) AS maintenance_count,
    COUNT(DISTINCT f.failure_id) AS failure_count,
    COALESCE(p.risk_score, 0) AS latest_risk_score,
    COALESCE(p.priority_level, 'Unknown') AS latest_priority,
    p.prediction_date AS last_prediction_date
FROM equipment e
LEFT JOIN maintenance_records m ON e.equipment_id = m.equipment_id
LEFT JOIN failure_events f ON e.equipment_id = f.equipment_id
LEFT JOIN LATERAL (
    SELECT * FROM predictions 
    WHERE equipment_id = e.equipment_id 
    ORDER BY prediction_date DESC 
    LIMIT 1
) p ON TRUE
GROUP BY e.equipment_id, e.equipment_type, e.brand, e.model, e.location, 
         e.operating_hours, e.purchase_date, p.risk_score, p.priority_level, p.prediction_date;
```

---

### 2. Maintenance Schedule View

```sql
CREATE VIEW vw_maintenance_schedule_summary AS
SELECT 
    ms.schedule_id,
    ms.equipment_id,
    e.equipment_type,
    e.brand,
    e.model,
    e.location,
    ms.scheduled_date,
    ms.priority_level,
    ms.risk_score,
    ms.status,
    ms.assigned_technician,
    ms.estimated_cost,
    CASE 
        WHEN ms.scheduled_date < CURRENT_DATE AND ms.status NOT IN ('Completed', 'Cancelled') THEN 'Overdue'
        WHEN ms.scheduled_date = CURRENT_DATE THEN 'Due Today'
        WHEN ms.scheduled_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'Due This Week'
        ELSE 'Upcoming'
    END AS urgency_status
FROM maintenance_schedule ms
JOIN equipment e ON ms.equipment_id = e.equipment_id
WHERE ms.status NOT IN ('Completed', 'Cancelled')
ORDER BY ms.priority_level DESC, ms.scheduled_date ASC;
```

---

### 3. Cost Analysis View

```sql
CREATE VIEW vw_cost_analysis AS
SELECT 
    e.equipment_id,
    e.equipment_type,
    e.location,
    COALESCE(SUM(m.total_cost), 0) AS total_maintenance_cost,
    COALESCE(SUM(f.repair_cost), 0) AS total_failure_cost,
    COALESCE(SUM(m.total_cost), 0) + COALESCE(SUM(f.repair_cost), 0) AS total_cost,
    COUNT(DISTINCT m.record_id) AS maintenance_count,
    COUNT(DISTINCT f.failure_id) AS failure_count,
    COALESCE(SUM(m.downtime_hours), 0) + COALESCE(SUM(f.downtime_hours), 0) AS total_downtime_hours
FROM equipment e
LEFT JOIN maintenance_records m ON e.equipment_id = m.equipment_id
LEFT JOIN failure_events f ON e.equipment_id = f.equipment_id
GROUP BY e.equipment_id, e.equipment_type, e.location;
```

---

### 4. Latest KPIs View

```sql
CREATE VIEW vw_latest_kpis AS
SELECT DISTINCT ON (metric_name)
    metric_name,
    metric_category,
    metric_value,
    target_value,
    status,
    measurement_date,
    CASE 
        WHEN status = 'Excellent' THEN '🟢'
        WHEN status = 'Good' THEN '🟡'
        WHEN status = 'Warning' THEN '🟠'
        WHEN status = 'Critical' THEN '🔴'
    END AS status_icon
FROM kpi_metrics
ORDER BY metric_name, measurement_date DESC;
```

---

### 5. KPI Summary by Category View

```sql
CREATE VIEW vw_kpi_summary AS
SELECT 
    metric_category,
    COUNT(*) as total_kpis,
    COUNT(CASE WHEN status = 'Excellent' THEN 1 END) as excellent_count,
    COUNT(CASE WHEN status = 'Good' THEN 1 END) as good_count,
    COUNT(CASE WHEN status = 'Warning' THEN 1 END) as warning_count,
    COUNT(CASE WHEN status = 'Critical' THEN 1 END) as critical_count,
    ROUND(AVG(metric_value), 2) as avg_value
FROM kpi_metrics
WHERE measurement_date = CURRENT_DATE
GROUP BY metric_category;
```

---

### 6. KPI Trends View

```sql
CREATE VIEW vw_kpi_trends AS
SELECT 
    km.metric_name,
    km.metric_category,
    km.measurement_date,
    km.metric_value,
    km.target_value,
    km.status,
    LAG(km.metric_value) OVER (PARTITION BY km.metric_name ORDER BY km.measurement_date) as previous_value,
    km.metric_value - LAG(km.metric_value) OVER (PARTITION BY km.metric_name ORDER BY km.measurement_date) as change_value,
    CASE 
        WHEN km.metric_value > LAG(km.metric_value) OVER (PARTITION BY km.metric_name ORDER BY km.measurement_date) THEN 'Increasing'
        WHEN km.metric_value < LAG(km.metric_value) OVER (PARTITION BY km.metric_name ORDER BY km.measurement_date) THEN 'Decreasing'
        ELSE 'Stable'
    END as trend_direction
FROM kpi_metrics km
WHERE km.measurement_date >= CURRENT_DATE - INTERVAL '30 days';
```

---

## 🔍 Useful Queries

### Get High-Risk Equipment

```sql
SELECT 
    e.equipment_id,
    e.equipment_type,
    e.location,
    p.risk_score,
    p.priority_level,
    p.recommended_action
FROM equipment e
JOIN predictions p ON e.equipment_id = p.equipment_id
WHERE p.prediction_date = CURRENT_DATE
  AND p.priority_level IN ('Critical', 'High')
ORDER BY p.risk_score DESC;
```

---

### Get Maintenance Schedule for Next Week

```sql
SELECT 
    ms.scheduled_date,
    e.equipment_id,
    e.equipment_type,
    e.location,
    ms.priority_level,
    ms.assigned_technician,
    ms.status
FROM maintenance_schedule ms
JOIN equipment e ON ms.equipment_id = e.equipment_id
WHERE ms.scheduled_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
  AND ms.status != 'Cancelled'
ORDER BY ms.scheduled_date, ms.priority_level DESC;
```

---

### Calculate Preventive Maintenance Ratio

```sql
SELECT 
    e.equipment_id,
    e.equipment_type,
    COUNT(CASE WHEN m.type_id = 1 THEN 1 END) AS preventive_count,
    COUNT(m.record_id) AS total_maintenance,
    ROUND(
        COUNT(CASE WHEN m.type_id = 1 THEN 1 END)::NUMERIC / 
        NULLIF(COUNT(m.record_id), 0) * 100, 
        2
    ) AS preventive_ratio_percent
FROM equipment e
LEFT JOIN maintenance_records m ON e.equipment_id = m.equipment_id
GROUP BY e.equipment_id, e.equipment_type
ORDER BY preventive_ratio_percent DESC;
```

---

## 🔧 Database Functions

### Update Equipment Operating Hours

```sql
CREATE OR REPLACE FUNCTION update_operating_hours()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE equipment
    SET updated_at = CURRENT_TIMESTAMP
    WHERE equipment_id = NEW.equipment_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_equipment_timestamp
AFTER INSERT OR UPDATE ON maintenance_records
FOR EACH ROW
EXECUTE FUNCTION update_operating_hours();
```

---

### Auto-Update Maintenance Schedule Status

```sql
CREATE OR REPLACE FUNCTION update_schedule_status()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.actual_end_time IS NOT NULL THEN
        NEW.status := 'Completed';
    ELSIF NEW.actual_start_time IS NOT NULL THEN
        NEW.status := 'In Progress';
    END IF;
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_schedule_status
BEFORE UPDATE ON maintenance_schedule
FOR EACH ROW
EXECUTE FUNCTION update_schedule_status();
```

---

### Get All KPIs for Dashboard

```sql
-- Get latest KPIs grouped by category
SELECT 
    metric_category,
    metric_name,
    metric_value,
    target_value,
    status,
    measurement_date
FROM vw_latest_kpis
ORDER BY metric_category, metric_name;
```

---

### Get KPI Trends (Last 30 Days)

```sql
-- Get trend for specific KPI
SELECT 
    measurement_date,
    metric_value,
    target_value,
    status
FROM kpi_metrics
WHERE metric_name = 'Cost Reduction %'
  AND measurement_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY measurement_date;
```

---

### Get KPIs Below Target

```sql
-- Find KPIs that need attention
SELECT 
    metric_name,
    metric_category,
    metric_value,
    target_value,
    status,
    (target_value - metric_value) as gap
FROM vw_latest_kpis
WHERE status IN ('Warning', 'Critical')
ORDER BY 
    CASE status 
        WHEN 'Critical' THEN 1 
        WHEN 'Warning' THEN 2 
    END,
    gap DESC;
```

---

### Calculate KPI Performance Score

```sql
-- Overall system health score based on KPIs
SELECT 
    ROUND(
        (COUNT(CASE WHEN status = 'Excellent' THEN 1 END) * 100.0 +
         COUNT(CASE WHEN status = 'Good' THEN 1 END) * 75.0 +
         COUNT(CASE WHEN status = 'Warning' THEN 1 END) * 50.0 +
         COUNT(CASE WHEN status = 'Critical' THEN 1 END) * 25.0) / 
        COUNT(*), 2
    ) as overall_health_score,
    COUNT(*) as total_kpis,
    COUNT(CASE WHEN status = 'Excellent' THEN 1 END) as excellent,
    COUNT(CASE WHEN status = 'Good' THEN 1 END) as good,
    COUNT(CASE WHEN status = 'Warning' THEN 1 END) as warning,
    COUNT(CASE WHEN status = 'Critical' THEN 1 END) as critical
FROM vw_latest_kpis;
```

---

## 📦 Database Setup Script

### Complete Setup SQL

```sql
-- Create database
CREATE DATABASE weefarm_db;

-- Connect to database
\c weefarm_db

-- Create tables in order (respecting foreign keys)
-- 1. equipment (no dependencies)
-- 2. maintenance_records (depends on equipment)
-- 3. failure_events (depends on equipment)
-- 4. predictions (depends on equipment)
-- 5. maintenance_schedule (depends on equipment, predictions)
-- 6. model_performance (no dependencies)
-- 7. kpi_metrics (no dependencies) -- NEW
-- 8. kpi_targets (no dependencies) -- NEW
-- 9. kpi_history (no dependencies) -- NEW

-- Create views
-- Create functions and triggers

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE weefarm_db TO weefarm_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO weefarm_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO weefarm_user;
```

---

## 📊 Summary

### Total Tables: 9

**Core Tables (3)**:
1. equipment
2. maintenance_records
3. failure_events

**Pipeline Output Tables (3)**:
4. predictions
5. maintenance_schedule
6. model_performance

**KPI Tables (3)** - NEW:
7. kpi_metrics - Store all KPI measurements
8. kpi_targets - Store target values and thresholds
9. kpi_history - Store aggregated trends

### Total Views: 6

1. vw_equipment_health
2. vw_maintenance_schedule_summary
3. vw_cost_analysis
4. vw_latest_kpis - NEW
5. vw_kpi_summary - NEW
6. vw_kpi_trends - NEW

### KPI Features:
- ✅ 25+ KPIs tracked
- ✅ 4 categories (Business, Technical, Operational, Model)
- ✅ Color-coded status (Excellent, Good, Warning, Critical)
- ✅ Historical trend analysis
- ✅ Target comparison
- ✅ Automated calculation

---

**End of Document**
