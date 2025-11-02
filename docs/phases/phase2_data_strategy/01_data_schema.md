# Phase 2: Data Schema Design

## Database Schema for Predictive Maintenance System

### Overview

This schema supports:
- Equipment tracking and management
- Maintenance history recording
- Failure event logging
- Time series data for forecasting
- Predictive model inputs

---

## Entity Relationship Diagram (ERD)

```
┌──────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Equipment      │────1:N──│ MaintenanceRecord│────N:1──│ MaintenanceType │
│                  │         │                  │         │                 │
│ - equipment_id   │         │ - record_id      │         │ - type_id       │
│ - type           │         │ - equipment_id   │         │ - type_name     │
│ - brand          │         │ - date           │         │ - description   │
│ - model          │         │ - type_id        │         │ - priority      │
│ - serial_number  │         │ - cost           │         └─────────────────┘
│ - year           │         │ - description    │
│ - purchase_date  │         │ - downtime_hours │         ┌─────────────────┐
│ - warranty_exp   │         │ - priority       │    ┌────│   Operator      │
│ - status         │         └──────────────────┘    │    │                 │
│ - condition_score│                 │               │    │ - operator_id   │
└──────────────────┘                 │               │    │ - name          │
        │                            │               │    │ - certification │
        │                            │               │    │ - experience    │
        │                   ┌──────────────────┐    │    └─────────────────┘
        │                   │  FailureEvent    │    │             │
        └──────────1:N──────│                  │    │             │
        │                   │ - failure_id     │    │             │
        │                   │ - equipment_id   │    │             │
        │                   │ - failure_date   │    │    ┌─────────────────┐
        │                   │ - failure_type   │    └─N:1│  UsageLog       │
        │                   │ - severity       │         │                 │
        │                   │ - root_cause     │         │ - log_id        │
        │                   │ - repair_cost    │         │ - equipment_id  │
        │                   │ - predicted      │         │ - operator_id   │
        │                   └──────────────────┘         │ - date          │
        │                                                │ - hours_used    │
        │                   ┌──────────────────┐         │ - fuel_consumed │
        └──────────1:N──────│  SensorReading   │         │ - workload      │
                            │                  │         └─────────────────┘
                            │ - reading_id     │
                            │ - equipment_id   │         ┌─────────────────┐
                            │ - timestamp      │    ┌────│  WeatherData    │
                            │ - temperature    │    │    │                 │
                            │ - vibration      │    │    │ - weather_id    │
                            │ - oil_pressure   │    │    │ - date          │
                            │ - fuel_level     │    │    │ - temperature   │
                            │ - error_codes    │    │    │ - precipitation │
                            └──────────────────┘    │    │ - humidity      │
                                                    │    │ - season        │
                                     ┌──────────────┘    └─────────────────┘
                                     │
                            ┌──────────────────┐
                            │  MaintenanceParts│
                            │                  │
                            │ - part_id        │
                            │ - record_id      │
                            │ - part_name      │
                            │ - quantity       │
                            │ - unit_cost      │
                            │ - supplier       │
                            └──────────────────┘
```

---

## Table Definitions

### 1. Equipment Table

**Purpose**: Store information about each piece of agricultural equipment

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `equipment_id` | VARCHAR(20) | Unique equipment identifier | PRIMARY KEY |
| `equipment_type` | VARCHAR(50) | Type (Tractor, Harvester, etc.) | NOT NULL |
| `brand` | VARCHAR(50) | Manufacturer brand | NOT NULL |
| `model` | VARCHAR(50) | Model name/number | NOT NULL |
| `serial_number` | VARCHAR(50) | Manufacturer serial number | UNIQUE |
| `year_manufactured` | INTEGER | Year of manufacture | NOT NULL |
| `purchase_date` | DATE | Date purchased | NOT NULL |
| `purchase_cost` | DECIMAL(10,2) | Initial purchase cost | NOT NULL |
| `warranty_expiry` | DATE | Warranty expiration date | NULL |
| `current_status` | VARCHAR(20) | Active, Under Maintenance, Retired | NOT NULL |
| `condition_score` | DECIMAL(3,2) | Equipment condition (0-1) | DEFAULT 1.0 |
| `operating_hours` | INTEGER | Total operating hours | DEFAULT 0 |
| `hours_since_service` | INTEGER | Hours since last maintenance | DEFAULT 0 |
| `last_service_date` | DATE | Date of last maintenance | NULL |
| `next_service_due` | DATE | Next scheduled service | NULL |
| `service_interval_hours` | INTEGER | Hours between services | DEFAULT 500 |
| `location` | VARCHAR(100) | Farm location | NULL |
| `assigned_operator` | VARCHAR(20) | Primary operator ID | FOREIGN KEY → Operator |
| `depreciation_rate` | DECIMAL(5,4) | Annual depreciation rate | DEFAULT 0.15 |
| `current_value` | DECIMAL(10,2) | Current estimated value | NULL |
| `insurance_policy` | VARCHAR(50) | Insurance policy number | NULL |
| `notes` | TEXT | Additional notes | NULL |
| `created_at` | TIMESTAMP | Record creation timestamp | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | Last update timestamp | DEFAULT NOW() |

**Sample Data**:
```sql
INSERT INTO Equipment VALUES 
('TRC-001', 'Tractor', 'John Deere', '5075E', 2018, '2018-03-15', 45000.00, 
 'Active', 2450, '2024-09-15', '2024-12-15', 'North Field', NOW(), NOW());
```

---

### 2. MaintenanceType Table

**Purpose**: Categorize types of maintenance activities

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `type_id` | INTEGER | Unique type identifier | PRIMARY KEY, AUTO_INCREMENT |
| `type_name` | VARCHAR(50) | Preventive, Corrective, Predictive | UNIQUE, NOT NULL |
| `description` | TEXT | Description of maintenance type | NULL |
| `typical_cost_range` | VARCHAR(50) | Typical cost range | NULL |

**Sample Data**:
```sql
INSERT INTO MaintenanceType (type_name, description) VALUES 
('Preventive', 'Scheduled maintenance to prevent failures'),
('Corrective', 'Repairs after equipment failure'),
('Predictive', 'Maintenance based on condition monitoring');
```

---

### 3. MaintenanceRecord Table

**Purpose**: Log all maintenance activities performed on equipment

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `record_id` | INTEGER | Unique record identifier | PRIMARY KEY, AUTO_INCREMENT |
| `equipment_id` | VARCHAR(20) | Equipment being serviced | FOREIGN KEY → Equipment |
| `maintenance_date` | DATE | Date of maintenance | NOT NULL |
| `type_id` | INTEGER | Type of maintenance | FOREIGN KEY → MaintenanceType |
| `description` | TEXT | Work performed | NOT NULL |
| `parts_replaced` | TEXT | Parts that were replaced | NULL |
| `labor_hours` | DECIMAL(5,2) | Hours of labor | NOT NULL |
| `parts_cost` | DECIMAL(10,2) | Cost of parts | DEFAULT 0 |
| `labor_cost` | DECIMAL(10,2) | Cost of labor | DEFAULT 0 |
| `total_cost` | DECIMAL(10,2) | Total maintenance cost | NOT NULL |
| `downtime_hours` | DECIMAL(5,2) | Equipment downtime | DEFAULT 0 |
| `technician_name` | VARCHAR(100) | Technician who performed work | NULL |
| `notes` | TEXT | Additional notes | NULL |
| `created_at` | TIMESTAMP | Record creation | DEFAULT NOW() |

**Sample Data**:
```sql
INSERT INTO MaintenanceRecord VALUES 
(1, 'TRC-001', '2024-09-15', 1, 'Oil change and filter replacement', 
 'Oil filter, Air filter', 2.5, 45.00, 125.00, 170.00, 2.5, 
 'John Smith', 'Routine service', NOW());
```

---

### 4. FailureEvent Table

**Purpose**: Record equipment failures and breakdowns

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `failure_id` | INTEGER | Unique failure identifier | PRIMARY KEY, AUTO_INCREMENT |
| `equipment_id` | VARCHAR(20) | Equipment that failed | FOREIGN KEY → Equipment |
| `failure_date` | DATE | Date of failure | NOT NULL |
| `failure_type` | VARCHAR(50) | Engine, Hydraulic, Electrical, etc. | NOT NULL |
| `severity` | VARCHAR(20) | Minor, Moderate, Critical | NOT NULL |
| `description` | TEXT | Failure description | NOT NULL |
| `root_cause` | TEXT | Identified root cause | NULL |
| `downtime_hours` | DECIMAL(5,2) | Hours equipment was down | NOT NULL |
| `repair_cost` | DECIMAL(10,2) | Cost to repair | NOT NULL |
| `prevented_by_maintenance` | BOOLEAN | Could it have been prevented? | DEFAULT FALSE |
| `created_at` | TIMESTAMP | Record creation | DEFAULT NOW() |

**Sample Data**:
```sql
INSERT INTO FailureEvent VALUES 
(1, 'TRC-001', '2024-06-20', 'Hydraulic', 'Moderate', 
 'Hydraulic hose burst during operation', 'Worn hose, exceeded service life', 
 8.0, 850.00, TRUE, NOW());
```

---

### 5. Operator Table

**Purpose**: Track equipment operators and their information

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `operator_id` | VARCHAR(20) | Unique operator identifier | PRIMARY KEY |
| `name` | VARCHAR(100) | Operator full name | NOT NULL |
| `certification_level` | VARCHAR(50) | Certification type | NULL |
| `years_experience` | INTEGER | Years of experience | DEFAULT 0 |
| `hire_date` | DATE | Date hired | NOT NULL |
| `contact_phone` | VARCHAR(20) | Contact number | NULL |
| `safety_incidents` | INTEGER | Number of safety incidents | DEFAULT 0 |
| `performance_score` | DECIMAL(3,2) | Performance rating (0-1) | DEFAULT 0.75 |
| `status` | VARCHAR(20) | Active, On Leave, Terminated | DEFAULT 'Active' |
| `created_at` | TIMESTAMP | Record creation | DEFAULT NOW() |

---

### 6. UsageLog Table

**Purpose**: Daily usage tracking for equipment

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `log_id` | INTEGER | Unique log identifier | PRIMARY KEY, AUTO_INCREMENT |
| `equipment_id` | VARCHAR(20) | Equipment used | FOREIGN KEY → Equipment |
| `operator_id` | VARCHAR(20) | Operator | FOREIGN KEY → Operator |
| `usage_date` | DATE | Date of usage | NOT NULL |
| `start_time` | TIME | Start time | NULL |
| `end_time` | TIME | End time | NULL |
| `hours_used` | DECIMAL(5,2) | Hours operated | NOT NULL |
| `fuel_consumed` | DECIMAL(8,2) | Fuel used (liters) | DEFAULT 0 |
| `distance_traveled` | DECIMAL(8,2) | Distance (km) | DEFAULT 0 |
| `workload_type` | VARCHAR(50) | Type of work performed | NULL |
| `field_conditions` | VARCHAR(50) | Soil/field conditions | NULL |
| `notes` | TEXT | Usage notes | NULL |
| `created_at` | TIMESTAMP | Record creation | DEFAULT NOW() |

---

### 7. SensorReading Table

**Purpose**: IoT sensor data for predictive analytics (future enhancement)

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `reading_id` | BIGINT | Unique reading identifier | PRIMARY KEY, AUTO_INCREMENT |
| `equipment_id` | VARCHAR(20) | Equipment being monitored | FOREIGN KEY → Equipment |
| `timestamp` | TIMESTAMP | Reading timestamp | NOT NULL |
| `engine_temperature` | DECIMAL(5,2) | Engine temp (°C) | NULL |
| `oil_pressure` | DECIMAL(5,2) | Oil pressure (PSI) | NULL |
| `hydraulic_pressure` | DECIMAL(5,2) | Hydraulic pressure (PSI) | NULL |
| `vibration_level` | DECIMAL(5,2) | Vibration (mm/s) | NULL |
| `fuel_level` | DECIMAL(5,2) | Fuel level (%) | NULL |
| `battery_voltage` | DECIMAL(4,2) | Battery voltage (V) | NULL |
| `rpm` | INTEGER | Engine RPM | NULL |
| `error_codes` | TEXT | Diagnostic error codes | NULL |
| `anomaly_detected` | BOOLEAN | Anomaly flag | DEFAULT FALSE |

---

### 8. WeatherData Table

**Purpose**: Weather conditions for correlation analysis

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `weather_id` | INTEGER | Unique weather identifier | PRIMARY KEY, AUTO_INCREMENT |
| `date` | DATE | Weather date | UNIQUE, NOT NULL |
| `temperature_avg` | DECIMAL(4,1) | Average temperature (°C) | NULL |
| `temperature_max` | DECIMAL(4,1) | Max temperature (°C) | NULL |
| `temperature_min` | DECIMAL(4,1) | Min temperature (°C) | NULL |
| `precipitation` | DECIMAL(5,2) | Rainfall (mm) | DEFAULT 0 |
| `humidity` | DECIMAL(3,0) | Humidity (%) | NULL |
| `wind_speed` | DECIMAL(4,1) | Wind speed (km/h) | NULL |
| `season` | VARCHAR(20) | Season | NULL |
| `weather_condition` | VARCHAR(50) | Sunny, Rainy, Cloudy, etc. | NULL |

---

### 9. MaintenanceParts Table

**Purpose**: Detailed parts tracking for maintenance

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `part_id` | INTEGER | Unique part identifier | PRIMARY KEY, AUTO_INCREMENT |
| `record_id` | INTEGER | Maintenance record | FOREIGN KEY → MaintenanceRecord |
| `part_name` | VARCHAR(100) | Part description | NOT NULL |
| `part_number` | VARCHAR(50) | Manufacturer part number | NULL |
| `quantity` | INTEGER | Quantity used | DEFAULT 1 |
| `unit_cost` | DECIMAL(10,2) | Cost per unit | NOT NULL |
| `total_cost` | DECIMAL(10,2) | Total cost (quantity × unit_cost) | NOT NULL |
| `supplier` | VARCHAR(100) | Parts supplier | NULL |
| `warranty_months` | INTEGER | Part warranty period | DEFAULT 0 |

---

## Data Relationships

### One-to-Many Relationships

1. **Equipment → MaintenanceRecord** (1:N)
   - One equipment can have many maintenance records
   - Each maintenance record belongs to one equipment

2. **Equipment → FailureEvent** (1:N)
   - One equipment can have many failure events
   - Each failure belongs to one equipment

3. **MaintenanceType → MaintenanceRecord** (1:N)
   - One maintenance type can be used in many records
   - Each record has one maintenance type

---

## Derived/Calculated Fields

These fields will be calculated in application logic or views:

### Equipment Level Metrics
```sql
-- Mean Time Between Failures (MTBF)
SELECT equipment_id, 
       AVG(days_between_failures) as mtbf_days
FROM (
    SELECT equipment_id,
           DATEDIFF(failure_date, LAG(failure_date) OVER (PARTITION BY equipment_id ORDER BY failure_date)) as days_between_failures
    FROM FailureEvent
) subquery
GROUP BY equipment_id;

-- Total Maintenance Cost (YTD)
SELECT equipment_id,
       SUM(total_cost) as ytd_cost
FROM MaintenanceRecord
WHERE YEAR(maintenance_date) = YEAR(CURDATE())
GROUP BY equipment_id;

-- Maintenance Frequency
SELECT equipment_id,
       COUNT(*) as maintenance_count,
       COUNT(*) / DATEDIFF(MAX(maintenance_date), MIN(maintenance_date)) * 365 as annual_frequency
FROM MaintenanceRecord
GROUP BY equipment_id;
```

---

## Indexes for Performance

```sql
-- Equipment table
CREATE INDEX idx_equipment_type ON Equipment(equipment_type);
CREATE INDEX idx_equipment_status ON Equipment(current_status);

-- MaintenanceRecord table
CREATE INDEX idx_maintenance_equipment ON MaintenanceRecord(equipment_id);
CREATE INDEX idx_maintenance_date ON MaintenanceRecord(maintenance_date);
CREATE INDEX idx_maintenance_type ON MaintenanceRecord(type_id);

-- FailureEvent table
CREATE INDEX idx_failure_equipment ON FailureEvent(equipment_id);
CREATE INDEX idx_failure_date ON FailureEvent(failure_date);
CREATE INDEX idx_failure_type ON FailureEvent(failure_type);
```

---

## Data Validation Rules

### Equipment
- `year_manufactured` must be between 1990 and current year
- `purchase_date` cannot be in the future
- `operating_hours` must be >= 0
- `current_status` must be one of: 'Active', 'Under Maintenance', 'Retired'

### MaintenanceRecord
- `maintenance_date` cannot be in the future
- `total_cost` = `parts_cost` + `labor_cost`
- `labor_hours` must be > 0
- `downtime_hours` must be >= 0

### FailureEvent
- `failure_date` cannot be in the future
- `severity` must be one of: 'Minor', 'Moderate', 'Critical'
- `downtime_hours` must be > 0
- `repair_cost` must be > 0

---

## Time Series Aggregation Views

For ML model training and forecasting:

```sql
-- Monthly maintenance costs by equipment
CREATE VIEW monthly_maintenance_costs AS
SELECT 
    equipment_id,
    DATE_FORMAT(maintenance_date, '%Y-%m') as month,
    SUM(total_cost) as total_cost,
    COUNT(*) as maintenance_count,
    AVG(downtime_hours) as avg_downtime
FROM MaintenanceRecord
GROUP BY equipment_id, DATE_FORMAT(maintenance_date, '%Y-%m');

-- Weekly failure rates
CREATE VIEW weekly_failure_rates AS
SELECT 
    equipment_id,
    YEARWEEK(failure_date) as year_week,
    COUNT(*) as failure_count,
    SUM(downtime_hours) as total_downtime,
    SUM(repair_cost) as total_repair_cost
FROM FailureEvent
GROUP BY equipment_id, YEARWEEK(failure_date);
```

---

## Advanced Features for ML

### Feature Engineering Views

**1. Equipment Health Score**
```sql
CREATE VIEW equipment_health_score AS
SELECT 
    e.equipment_id,
    e.equipment_type,
    e.condition_score,
    -- Age factor (0-1, newer is better)
    1 - (YEAR(CURDATE()) - e.year_manufactured) / 20.0 AS age_score,
    -- Usage intensity (0-1, less usage is better)
    1 - (e.operating_hours / (e.service_interval_hours * 10)) AS usage_score,
    -- Maintenance compliance (0-1, recent service is better)
    CASE 
        WHEN e.hours_since_service <= e.service_interval_hours THEN 1.0
        WHEN e.hours_since_service <= e.service_interval_hours * 1.5 THEN 0.7
        ELSE 0.3
    END AS maintenance_score,
    -- Failure history (0-1, fewer failures is better)
    1 - LEAST(
        (SELECT COUNT(*) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id) / 10.0,
        1.0
    ) AS reliability_score,
    -- Overall health (weighted average)
    (
        e.condition_score * 0.3 +
        (1 - (YEAR(CURDATE()) - e.year_manufactured) / 20.0) * 0.2 +
        (1 - (e.operating_hours / (e.service_interval_hours * 10))) * 0.2 +
        (1 - LEAST((SELECT COUNT(*) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id) / 10.0, 1.0)) * 0.3
    ) AS overall_health_score
FROM Equipment e;
```

**2. Failure Prediction Features**
```sql
CREATE VIEW failure_prediction_features AS
SELECT 
    e.equipment_id,
    e.equipment_type,
    e.brand,
    YEAR(CURDATE()) - e.year_manufactured AS age_years,
    e.operating_hours,
    e.hours_since_service,
    e.hours_since_service / NULLIF(e.service_interval_hours, 0) AS service_overdue_ratio,
    -- Recent maintenance count (last 6 months)
    (SELECT COUNT(*) FROM MaintenanceRecord m 
     WHERE m.equipment_id = e.equipment_id 
     AND m.maintenance_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)) AS recent_maintenance_count,
    -- Recent failure count (last 6 months)
    (SELECT COUNT(*) FROM FailureEvent f 
     WHERE f.equipment_id = e.equipment_id 
     AND f.failure_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)) AS recent_failure_count,
    -- Total failures
    (SELECT COUNT(*) FROM FailureEvent f 
     WHERE f.equipment_id = e.equipment_id) AS total_failures,
    -- Average repair cost
    (SELECT AVG(repair_cost) FROM FailureEvent f 
     WHERE f.equipment_id = e.equipment_id) AS avg_repair_cost,
    -- Days since last failure
    DATEDIFF(CURDATE(), 
        (SELECT MAX(failure_date) FROM FailureEvent f 
         WHERE f.equipment_id = e.equipment_id)) AS days_since_last_failure,
    -- Total maintenance cost (last year)
    (SELECT SUM(total_cost) FROM MaintenanceRecord m 
     WHERE m.equipment_id = e.equipment_id 
     AND m.maintenance_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)) AS annual_maintenance_cost,
    -- Condition score
    e.condition_score,
    -- Season (for seasonal patterns)
    QUARTER(CURDATE()) AS current_quarter,
    MONTH(CURDATE()) AS current_month
FROM Equipment e
WHERE e.current_status = 'Active';
```

**3. Cost Forecasting Features**
```sql
CREATE VIEW cost_forecasting_features AS
SELECT 
    DATE_FORMAT(m.maintenance_date, '%Y-%m') AS year_month,
    e.equipment_type,
    COUNT(*) AS maintenance_count,
    SUM(m.total_cost) AS total_cost,
    AVG(m.total_cost) AS avg_cost,
    SUM(m.downtime_hours) AS total_downtime,
    SUM(CASE WHEN m.type_id = 1 THEN m.total_cost ELSE 0 END) AS preventive_cost,
    SUM(CASE WHEN m.type_id = 2 THEN m.total_cost ELSE 0 END) AS corrective_cost,
    SUM(CASE WHEN m.type_id = 3 THEN m.total_cost ELSE 0 END) AS predictive_cost,
    -- Lag features (previous month cost)
    LAG(SUM(m.total_cost), 1) OVER (PARTITION BY e.equipment_type ORDER BY DATE_FORMAT(m.maintenance_date, '%Y-%m')) AS prev_month_cost,
    LAG(SUM(m.total_cost), 3) OVER (PARTITION BY e.equipment_type ORDER BY DATE_FORMAT(m.maintenance_date, '%Y-%m')) AS prev_quarter_cost,
    -- Rolling average (3 months)
    AVG(SUM(m.total_cost)) OVER (
        PARTITION BY e.equipment_type 
        ORDER BY DATE_FORMAT(m.maintenance_date, '%Y-%m')
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS rolling_avg_3m
FROM MaintenanceRecord m
JOIN Equipment e ON m.equipment_id = e.equipment_id
GROUP BY DATE_FORMAT(m.maintenance_date, '%Y-%m'), e.equipment_type;
```

**4. Equipment Performance Dashboard**
```sql
CREATE VIEW equipment_performance_dashboard AS
SELECT 
    e.equipment_id,
    e.equipment_type,
    e.brand,
    e.model,
    e.current_status,
    e.operating_hours,
    -- Financial metrics
    e.purchase_cost,
    e.current_value,
    (e.purchase_cost - e.current_value) AS total_depreciation,
    -- Maintenance metrics
    (SELECT COUNT(*) FROM MaintenanceRecord m WHERE m.equipment_id = e.equipment_id) AS total_maintenance_events,
    (SELECT SUM(total_cost) FROM MaintenanceRecord m WHERE m.equipment_id = e.equipment_id) AS lifetime_maintenance_cost,
    (SELECT SUM(downtime_hours) FROM MaintenanceRecord m WHERE m.equipment_id = e.equipment_id) AS total_maintenance_downtime,
    -- Failure metrics
    (SELECT COUNT(*) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id) AS total_failures,
    (SELECT SUM(repair_cost) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id) AS total_failure_cost,
    (SELECT SUM(downtime_hours) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id) AS total_failure_downtime,
    -- Calculated KPIs
    CASE 
        WHEN (SELECT COUNT(*) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id) > 0
        THEN e.operating_hours / (SELECT COUNT(*) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id)
        ELSE NULL
    END AS mtbf_hours,
    (SELECT AVG(downtime_hours) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id) AS mttr_hours,
    -- Total cost of ownership
    e.purchase_cost + 
    COALESCE((SELECT SUM(total_cost) FROM MaintenanceRecord m WHERE m.equipment_id = e.equipment_id), 0) +
    COALESCE((SELECT SUM(repair_cost) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id), 0) AS total_cost_of_ownership,
    -- Cost per operating hour
    (COALESCE((SELECT SUM(total_cost) FROM MaintenanceRecord m WHERE m.equipment_id = e.equipment_id), 0) +
     COALESCE((SELECT SUM(repair_cost) FROM FailureEvent f WHERE f.equipment_id = e.equipment_id), 0)) / 
    NULLIF(e.operating_hours, 0) AS cost_per_hour
FROM Equipment e;
```

---

## Data Volume Estimates

For a farm with **50 equipment units** over **3 years**:

| Table | Estimated Rows | Storage | Purpose |
|-------|----------------|---------|---------|
| Equipment | 50 | ~15 KB | Core equipment data |
| MaintenanceType | 3-5 | <1 KB | Lookup table |
| MaintenanceRecord | 1,500-2,000 | ~600 KB | Historical maintenance |
| FailureEvent | 150-300 | ~120 KB | Failure history |
| Operator | 10-20 | ~5 KB | Operator information |
| UsageLog | 15,000-20,000 | ~2 MB | Daily usage tracking |
| SensorReading | 0 (future) | 0 | IoT data (optional) |
| WeatherData | 1,095 | ~50 KB | 3 years daily weather |
| MaintenanceParts | 3,000-4,000 | ~300 KB | Parts inventory |
| **Total** | **~25,000** | **~3 MB** | Very manageable |

With sensor data (1 reading/hour): ~2.6M rows, ~200 MB (still manageable)

---

## Next Steps

1. ✅ Schema designed
2. ⏳ Create SQL schema file
3. ⏳ Build synthetic data generator
4. ⏳ Generate sample dataset
5. ⏳ Validate data quality

---

**Status**: ✅ Schema Design Complete
**Next**: Create data generation scripts
