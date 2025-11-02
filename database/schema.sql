-- ============================================================================
-- PREDICTIVE MAINTENANCE SYSTEM - DATABASE SCHEMA
-- ============================================================================
-- Purpose: Agricultural equipment maintenance management and predictive analytics
-- Version: 2.0 (Enhanced)
-- Date: 2025-10-31
-- ============================================================================

-- Drop existing tables (in reverse order of dependencies)
DROP TABLE IF EXISTS MaintenanceParts;
DROP TABLE IF EXISTS SensorReading;
DROP TABLE IF EXISTS UsageLog;
DROP TABLE IF EXISTS FailureEvent;
DROP TABLE IF EXISTS MaintenanceRecord;
DROP TABLE IF EXISTS WeatherData;
DROP TABLE IF EXISTS Operator;
DROP TABLE IF EXISTS MaintenanceType;
DROP TABLE IF EXISTS Equipment;

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Equipment Table
CREATE TABLE Equipment (
    equipment_id VARCHAR(20) PRIMARY KEY,
    equipment_type VARCHAR(50) NOT NULL,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    serial_number VARCHAR(50) UNIQUE,
    year_manufactured INTEGER NOT NULL CHECK (year_manufactured >= 1990 AND year_manufactured <= YEAR(CURDATE())),
    purchase_date DATE NOT NULL CHECK (purchase_date <= CURDATE()),
    purchase_cost DECIMAL(10,2) NOT NULL CHECK (purchase_cost > 0),
    warranty_expiry DATE,
    current_status VARCHAR(20) NOT NULL DEFAULT 'Active' CHECK (current_status IN ('Active', 'Under Maintenance', 'Retired')),
    condition_score DECIMAL(3,2) DEFAULT 1.0 CHECK (condition_score BETWEEN 0 AND 1),
    operating_hours INTEGER DEFAULT 0 CHECK (operating_hours >= 0),
    hours_since_service INTEGER DEFAULT 0 CHECK (hours_since_service >= 0),
    last_service_date DATE,
    next_service_due DATE,
    service_interval_hours INTEGER DEFAULT 500 CHECK (service_interval_hours > 0),
    location VARCHAR(100),
    assigned_operator VARCHAR(20),
    depreciation_rate DECIMAL(5,4) DEFAULT 0.15 CHECK (depreciation_rate BETWEEN 0 AND 1),
    current_value DECIMAL(10,2),
    insurance_policy VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_equipment_type (equipment_type),
    INDEX idx_status (current_status),
    INDEX idx_location (location)
);

-- Maintenance Type Lookup Table
CREATE TABLE MaintenanceType (
    type_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    typical_cost_range VARCHAR(50),
    priority INTEGER DEFAULT 2 CHECK (priority BETWEEN 1 AND 5)
);

-- Insert maintenance types
INSERT INTO MaintenanceType (type_name, description, typical_cost_range, priority) VALUES
('Preventive', 'Scheduled maintenance to prevent failures', '$100-$500', 2),
('Corrective', 'Repairs after equipment failure', '$300-$3000', 1),
('Predictive', 'Maintenance based on condition monitoring', '$200-$1000', 2);

-- Operator Table
CREATE TABLE Operator (
    operator_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    certification_level VARCHAR(50),
    years_experience INTEGER DEFAULT 0 CHECK (years_experience >= 0),
    hire_date DATE NOT NULL,
    contact_phone VARCHAR(20),
    safety_incidents INTEGER DEFAULT 0 CHECK (safety_incidents >= 0),
    performance_score DECIMAL(3,2) DEFAULT 0.75 CHECK (performance_score BETWEEN 0 AND 1),
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'On Leave', 'Terminated')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_operator_status (status)
);

-- Weather Data Table
CREATE TABLE WeatherData (
    weather_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    date DATE UNIQUE NOT NULL,
    temperature_avg DECIMAL(4,1),
    temperature_max DECIMAL(4,1),
    temperature_min DECIMAL(4,1),
    precipitation DECIMAL(5,2) DEFAULT 0,
    humidity DECIMAL(3,0) CHECK (humidity BETWEEN 0 AND 100),
    wind_speed DECIMAL(4,1),
    season VARCHAR(20) CHECK (season IN ('Spring', 'Summer', 'Fall', 'Winter')),
    weather_condition VARCHAR(50),
    INDEX idx_weather_date (date),
    INDEX idx_season (season)
);

-- ============================================================================
-- TRANSACTIONAL TABLES
-- ============================================================================

-- Maintenance Record Table
CREATE TABLE MaintenanceRecord (
    record_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    equipment_id VARCHAR(20) NOT NULL,
    maintenance_date DATE NOT NULL CHECK (maintenance_date <= CURDATE()),
    type_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    parts_replaced TEXT,
    labor_hours DECIMAL(5,2) NOT NULL CHECK (labor_hours > 0),
    parts_cost DECIMAL(10,2) DEFAULT 0 CHECK (parts_cost >= 0),
    labor_cost DECIMAL(10,2) DEFAULT 0 CHECK (labor_cost >= 0),
    total_cost DECIMAL(10,2) NOT NULL CHECK (total_cost >= 0),
    downtime_hours DECIMAL(5,2) DEFAULT 0 CHECK (downtime_hours >= 0),
    technician_name VARCHAR(100),
    priority INTEGER DEFAULT 2 CHECK (priority BETWEEN 1 AND 5),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id) ON DELETE CASCADE,
    FOREIGN KEY (type_id) REFERENCES MaintenanceType(type_id),
    INDEX idx_maintenance_equipment (equipment_id),
    INDEX idx_maintenance_date (maintenance_date),
    INDEX idx_maintenance_type (type_id),
    INDEX idx_maintenance_priority (priority),
    CHECK (total_cost = parts_cost + labor_cost)
);

-- Failure Event Table
CREATE TABLE FailureEvent (
    failure_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    equipment_id VARCHAR(20) NOT NULL,
    failure_date DATE NOT NULL CHECK (failure_date <= CURDATE()),
    failure_type VARCHAR(50) NOT NULL CHECK (failure_type IN ('Engine', 'Hydraulic', 'Electrical', 'Mechanical', 'Tire', 'Belt', 'Other')),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('Minor', 'Moderate', 'Critical')),
    description TEXT NOT NULL,
    root_cause TEXT,
    downtime_hours DECIMAL(5,2) NOT NULL CHECK (downtime_hours > 0),
    repair_cost DECIMAL(10,2) NOT NULL CHECK (repair_cost > 0),
    prevented_by_maintenance BOOLEAN DEFAULT FALSE,
    predicted BOOLEAN DEFAULT FALSE,
    prediction_accuracy DECIMAL(3,2) CHECK (prediction_accuracy BETWEEN 0 AND 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id) ON DELETE CASCADE,
    INDEX idx_failure_equipment (equipment_id),
    INDEX idx_failure_date (failure_date),
    INDEX idx_failure_type (failure_type),
    INDEX idx_failure_severity (severity)
);

-- Usage Log Table
CREATE TABLE UsageLog (
    log_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    equipment_id VARCHAR(20) NOT NULL,
    operator_id VARCHAR(20),
    usage_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    hours_used DECIMAL(5,2) NOT NULL CHECK (hours_used > 0),
    fuel_consumed DECIMAL(8,2) DEFAULT 0 CHECK (fuel_consumed >= 0),
    distance_traveled DECIMAL(8,2) DEFAULT 0 CHECK (distance_traveled >= 0),
    workload_type VARCHAR(50),
    field_conditions VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id) ON DELETE CASCADE,
    FOREIGN KEY (operator_id) REFERENCES Operator(operator_id) ON DELETE SET NULL,
    INDEX idx_usage_equipment (equipment_id),
    INDEX idx_usage_date (usage_date),
    INDEX idx_usage_operator (operator_id)
);

-- Sensor Reading Table (IoT - Future Enhancement)
CREATE TABLE SensorReading (
    reading_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    equipment_id VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    engine_temperature DECIMAL(5,2),
    oil_pressure DECIMAL(5,2),
    hydraulic_pressure DECIMAL(5,2),
    vibration_level DECIMAL(5,2),
    fuel_level DECIMAL(5,2) CHECK (fuel_level BETWEEN 0 AND 100),
    battery_voltage DECIMAL(4,2),
    rpm INTEGER CHECK (rpm >= 0),
    error_codes TEXT,
    anomaly_detected BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id) ON DELETE CASCADE,
    INDEX idx_sensor_equipment (equipment_id),
    INDEX idx_sensor_timestamp (timestamp),
    INDEX idx_sensor_anomaly (anomaly_detected)
);

-- Maintenance Parts Table
CREATE TABLE MaintenanceParts (
    part_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    record_id INTEGER NOT NULL,
    part_name VARCHAR(100) NOT NULL,
    part_number VARCHAR(50),
    quantity INTEGER DEFAULT 1 CHECK (quantity > 0),
    unit_cost DECIMAL(10,2) NOT NULL CHECK (unit_cost >= 0),
    total_cost DECIMAL(10,2) NOT NULL CHECK (total_cost >= 0),
    supplier VARCHAR(100),
    warranty_months INTEGER DEFAULT 0 CHECK (warranty_months >= 0),
    FOREIGN KEY (record_id) REFERENCES MaintenanceRecord(record_id) ON DELETE CASCADE,
    INDEX idx_parts_record (record_id),
    INDEX idx_parts_name (part_name),
    CHECK (total_cost = quantity * unit_cost)
);

-- ============================================================================
-- VIEWS FOR ANALYTICS AND ML
-- ============================================================================

-- Equipment Health Score View
CREATE VIEW equipment_health_score AS
SELECT 
    e.equipment_id,
    e.equipment_type,
    e.brand,
    e.model,
    e.condition_score,
    1 - (YEAR(CURDATE()) - e.year_manufactured) / 20.0 AS age_score,
    1 - (e.operating_hours / (e.service_interval_hours * 10)) AS usage_score,
    CASE 
        WHEN e.hours_since_service <= e.service_interval_hours THEN 1.0
        WHEN e.hours_since_service <= e.service_interval_hours * 1.5 THEN 0.7
        ELSE 0.3
    END AS maintenance_score,
    1 - LEAST(
        (SELECT COUNT(*) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id) / 10.0,
        1.0
    ) AS reliability_score,
    (
        e.condition_score * 0.3 +
        (1 - (YEAR(CURDATE()) - e.year_manufactured) / 20.0) * 0.2 +
        (1 - (e.operating_hours / (e.service_interval_hours * 10))) * 0.2 +
        (1 - LEAST((SELECT COUNT(*) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id) / 10.0, 1.0)) * 0.3
    ) AS overall_health_score
FROM Equipment e;

-- Equipment Performance Dashboard View
CREATE VIEW equipment_performance_dashboard AS
SELECT 
    e.equipment_id,
    e.equipment_type,
    e.brand,
    e.model,
    e.current_status,
    e.operating_hours,
    e.purchase_cost,
    e.current_value,
    (e.purchase_cost - COALESCE(e.current_value, 0)) AS total_depreciation,
    (SELECT COUNT(*) FROM MaintenanceRecord m WHERE m.equipment_id = e.equipment_id) AS total_maintenance_events,
    COALESCE((SELECT SUM(total_cost) FROM MaintenanceRecord m WHERE m.equipment_id = e.equipment_id), 0) AS lifetime_maintenance_cost,
    COALESCE((SELECT SUM(downtime_hours) FROM MaintenanceRecord m WHERE m.equipment_id = e.equipment_id), 0) AS total_maintenance_downtime,
    (SELECT COUNT(*) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id) AS total_failures,
    COALESCE((SELECT SUM(repair_cost) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id), 0) AS total_failure_cost,
    COALESCE((SELECT SUM(downtime_hours) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id), 0) AS total_failure_downtime,
    CASE 
        WHEN (SELECT COUNT(*) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id) > 0
        THEN e.operating_hours / (SELECT COUNT(*) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id)
        ELSE NULL
    END AS mtbf_hours,
    (SELECT AVG(downtime_hours) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id) AS mttr_hours,
    e.purchase_cost + 
    COALESCE((SELECT SUM(total_cost) FROM MaintenanceRecord m WHERE m.equipment_id = e.equipment_id), 0) +
    COALESCE((SELECT SUM(repair_cost) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id), 0) AS total_cost_of_ownership,
    (COALESCE((SELECT SUM(total_cost) FROM MaintenanceRecord m WHERE m.equipment_id = e.equipment_id), 0) +
     COALESCE((SELECT SUM(repair_cost) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id), 0)) / 
    NULLIF(e.operating_hours, 0) AS cost_per_hour
FROM Equipment e;

-- Monthly Maintenance Costs View
CREATE VIEW monthly_maintenance_costs AS
SELECT 
    DATE_FORMAT(m.maintenance_date, '%Y-%m') as month,
    e.equipment_type,
    COUNT(*) as maintenance_count,
    SUM(m.total_cost) as total_cost,
    AVG(m.total_cost) as avg_cost,
    SUM(m.downtime_hours) as total_downtime,
    SUM(CASE WHEN m.type_id = 1 THEN m.total_cost ELSE 0 END) as preventive_cost,
    SUM(CASE WHEN m.type_id = 2 THEN m.total_cost ELSE 0 END) as corrective_cost,
    SUM(CASE WHEN m.type_id = 3 THEN m.total_cost ELSE 0 END) as predictive_cost
FROM MaintenanceRecord m
JOIN Equipment e ON m.equipment_id = e.equipment_id
GROUP BY DATE_FORMAT(m.maintenance_date, '%Y-%m'), e.equipment_type;

-- Weekly Failure Rates View
CREATE VIEW weekly_failure_rates AS
SELECT 
    equipment_id,
    YEARWEEK(failure_date) as year_week,
    COUNT(*) as failure_count,
    SUM(downtime_hours) as total_downtime,
    SUM(repair_cost) as total_repair_cost
FROM FailureEvent
GROUP BY equipment_id, YEARWEEK(failure_date);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update equipment operating hours from usage log
DELIMITER //
CREATE TRIGGER update_operating_hours
AFTER INSERT ON UsageLog
FOR EACH ROW
BEGIN
    UPDATE Equipment 
    SET operating_hours = operating_hours + NEW.hours_used,
        hours_since_service = hours_since_service + NEW.hours_used,
        updated_at = CURRENT_TIMESTAMP
    WHERE equipment_id = NEW.equipment_id;
END//
DELIMITER ;

-- Update equipment after maintenance
DELIMITER //
CREATE TRIGGER update_after_maintenance
AFTER INSERT ON MaintenanceRecord
FOR EACH ROW
BEGIN
    UPDATE Equipment 
    SET last_service_date = NEW.maintenance_date,
        hours_since_service = 0,
        next_service_due = DATE_ADD(NEW.maintenance_date, INTERVAL 90 DAY),
        updated_at = CURRENT_TIMESTAMP
    WHERE equipment_id = NEW.equipment_id;
END//
DELIMITER ;

-- ============================================================================
-- SAMPLE DATA INSERTION (Optional)
-- ============================================================================

-- Add sample equipment
INSERT INTO Equipment (equipment_id, equipment_type, brand, model, serial_number, year_manufactured, purchase_date, purchase_cost, current_status, location) VALUES
('TRC-001', 'Tractor', 'John Deere', '5075E', 'JD2018001', 2018, '2018-03-15', 45000.00, 'Active', 'North Field'),
('HRV-001', 'Harvester', 'Case IH', 'Axial-Flow 8250', 'CI2019001', 2019, '2019-08-20', 350000.00, 'Active', 'Main Barn');

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
