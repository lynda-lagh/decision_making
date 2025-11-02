# Phase 2: Data Dictionary

## Complete Field Definitions

### Equipment Table

| Field Name | Data Type | Format/Range | Example | Business Rule |
|------------|-----------|--------------|---------|---------------|
| equipment_id | VARCHAR(20) | XXX-NNN | TRC-001 | Prefix: TRC=Tractor, HRV=Harvester, IRR=Irrigation, PLT=Planter, SPR=Sprayer |
| equipment_type | VARCHAR(50) | Enum | Tractor | Values: Tractor, Harvester, Irrigation System, Planter, Sprayer |
| brand | VARCHAR(50) | Text | John Deere | Major brands: John Deere, Case IH, New Holland, Kubota, Massey Ferguson |
| model | VARCHAR(50) | Alphanumeric | 5075E | Manufacturer model number |
| year_manufactured | INTEGER | 1990-2024 | 2018 | Must be <= current year |
| purchase_date | DATE | YYYY-MM-DD | 2018-03-15 | Cannot be future date |
| purchase_cost | DECIMAL(10,2) | 5000-500000 | 45000.00 | USD, typical range $5K-$500K |
| current_status | VARCHAR(20) | Enum | Active | Values: Active, Under Maintenance, Retired |
| operating_hours | INTEGER | 0-50000 | 2450 | Cumulative hours, updated after each use |
| last_service_date | DATE | YYYY-MM-DD | 2024-09-15 | NULL if never serviced |
| next_service_due | DATE | YYYY-MM-DD | 2024-12-15 | Calculated based on hours or time |
| location | VARCHAR(100) | Text | North Field | Farm location or storage area |

### MaintenanceType Table

| Field Name | Data Type | Format/Range | Example | Business Rule |
|------------|-----------|--------------|---------|---------------|
| type_id | INTEGER | 1-N | 1 | Auto-increment primary key |
| type_name | VARCHAR(50) | Enum | Preventive | Values: Preventive, Corrective, Predictive |
| description | TEXT | Free text | Scheduled maintenance... | Explains the maintenance type |
| typical_cost_range | VARCHAR(50) | Text | $100-$500 | Informational only |

### MaintenanceRecord Table

| Field Name | Data Type | Format/Range | Example | Business Rule |
|------------|-----------|--------------|---------|---------------|
| record_id | INTEGER | 1-N | 1 | Auto-increment primary key |
| equipment_id | VARCHAR(20) | FK | TRC-001 | Must exist in Equipment table |
| maintenance_date | DATE | YYYY-MM-DD | 2024-09-15 | Cannot be future date |
| type_id | INTEGER | 1-3 | 1 | Must exist in MaintenanceType table |
| description | TEXT | Free text | Oil change and filter... | Detailed work description |
| parts_replaced | TEXT | Comma-separated | Oil filter, Air filter | List of parts |
| labor_hours | DECIMAL(5,2) | 0.1-100 | 2.5 | Hours worked |
| parts_cost | DECIMAL(10,2) | 0-50000 | 45.00 | USD, cost of parts only |
| labor_cost | DECIMAL(10,2) | 0-10000 | 125.00 | USD, labor charges |
| total_cost | DECIMAL(10,2) | 0-50000 | 170.00 | parts_cost + labor_cost |
| downtime_hours | DECIMAL(5,2) | 0-1000 | 2.5 | Hours equipment unavailable |
| technician_name | VARCHAR(100) | Text | John Smith | Person who performed work |
| notes | TEXT | Free text | Routine service | Additional comments |

### FailureEvent Table

| Field Name | Data Type | Format/Range | Example | Business Rule |
|------------|-----------|--------------|---------|---------------|
| failure_id | INTEGER | 1-N | 1 | Auto-increment primary key |
| equipment_id | VARCHAR(20) | FK | TRC-001 | Must exist in Equipment table |
| failure_date | DATE | YYYY-MM-DD | 2024-06-20 | Cannot be future date |
| failure_type | VARCHAR(50) | Enum | Hydraulic | Values: Engine, Hydraulic, Electrical, Mechanical, Tire, Belt, Other |
| severity | VARCHAR(20) | Enum | Moderate | Values: Minor, Moderate, Critical |
| description | TEXT | Free text | Hydraulic hose burst... | Detailed failure description |
| root_cause | TEXT | Free text | Worn hose... | Identified cause if known |
| downtime_hours | DECIMAL(5,2) | 0.1-1000 | 8.0 | Hours equipment was down |
| repair_cost | DECIMAL(10,2) | 0-50000 | 850.00 | USD, total repair cost |
| prevented_by_maintenance | BOOLEAN | TRUE/FALSE | TRUE | Could preventive maintenance have avoided this? |

---

## Enumerated Values

### Equipment Types
- **Tractor**: General-purpose farm vehicle
- **Harvester**: Crop harvesting equipment
- **Irrigation System**: Water distribution system
- **Planter**: Seed planting equipment
- **Sprayer**: Chemical/fertilizer application

### Equipment Status
- **Active**: In regular use
- **Under Maintenance**: Currently being serviced
- **Retired**: No longer in use

### Maintenance Types
- **Preventive**: Scheduled, time-based or usage-based maintenance
- **Corrective**: Repairs after failure
- **Predictive**: Condition-based maintenance

### Failure Types
- **Engine**: Motor, fuel system, exhaust
- **Hydraulic**: Pumps, hoses, cylinders
- **Electrical**: Battery, wiring, sensors
- **Mechanical**: Gears, bearings, transmission
- **Tire**: Tire wear or damage
- **Belt**: Drive belts, chains
- **Other**: Miscellaneous failures

### Severity Levels
- **Minor**: <4 hours downtime, <$500 cost
- **Moderate**: 4-24 hours downtime, $500-$2000 cost
- **Critical**: >24 hours downtime, >$2000 cost

---

## Calculated Fields

### Equipment Metrics

**Age (years)**
```python
age = current_year - year_manufactured
```

**Days Since Last Service**
```python
days_since_service = today - last_service_date
```

**Service Overdue**
```python
overdue = next_service_due < today
```

**Cost Per Operating Hour**
```python
cost_per_hour = total_maintenance_cost / operating_hours
```

### Maintenance Metrics

**Mean Time Between Failures (MTBF)**
```python
mtbf = total_operating_hours / number_of_failures
```

**Mean Time To Repair (MTTR)**
```python
mttr = sum(downtime_hours) / number_of_failures
```

**Planned Maintenance Percentage**
```python
pmp = (preventive_count / total_maintenance_count) * 100
```

---

## Data Quality Rules

### Required Fields
- All PRIMARY KEY fields
- All fields marked NOT NULL
- Foreign keys must reference existing records

### Data Ranges
- Dates: Not in the future (except next_service_due)
- Costs: >= 0
- Hours: >= 0
- Years: 1990 <= year <= current_year

### Business Logic
- total_cost = parts_cost + labor_cost
- Equipment cannot have maintenance records before purchase_date
- Failure dates should align with maintenance records

---

## Sample Data Distributions

### Equipment Type Distribution (Typical Farm)
- Tractors: 40%
- Harvesters: 20%
- Irrigation: 15%
- Planters: 15%
- Sprayers: 10%

### Maintenance Type Distribution
- Preventive: 35%
- Corrective: 55%
- Predictive: 10%

### Failure Type Distribution
- Engine: 25%
- Hydraulic: 20%
- Electrical: 15%
- Mechanical: 15%
- Tire: 15%
- Belt: 5%
- Other: 5%

### Severity Distribution
- Minor: 60%
- Moderate: 30%
- Critical: 10%

---

## Data Generation Parameters

### For Synthetic Data

**Equipment**
- Count: 50 units
- Age distribution: Normal (mean=8 years, std=4 years)
- Operating hours: 200-1000 hours/year

**Maintenance Records**
- Frequency: 2-4 times per year per equipment
- Cost distribution: Log-normal (mean=$300, std=$200)
- Seasonal pattern: More maintenance in winter (off-season)

**Failure Events**
- Frequency: 0.5-1.5 failures per equipment per year
- Cost distribution: Log-normal (mean=$800, std=$500)
- Seasonal pattern: More failures during harvest season

---

**Status**: ✅ Data Dictionary Complete
**Next**: Build synthetic data generator
