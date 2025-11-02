# 📡 API Endpoints Documentation

## Base URL
```
http://localhost:5000/api/v1
```

## 🆕 New Analytics Endpoints

### 1. Root Cause Analysis
```http
GET /analytics/root-cause?limit=10
```
**Description**: Get failure root cause analysis with Pareto data

**Response**:
```json
{
  "total_failures": 656,
  "total_cost": 750000.00,
  "data": [
    {
      "root_cause": "Normal wear",
      "failure_count": 120,
      "total_downtime": 1500.5,
      "total_cost": 150000.00,
      "avg_cost": 1250.00,
      "cost_percentage": 20.0,
      "cumulative_cost_pct": 20.0
    }
  ]
}
```

### 2. Equipment Reliability
```http
GET /analytics/equipment-reliability?equipment_type=Tractor
```
**Description**: Get MTBF and reliability metrics per equipment

**Response**:
```json
{
  "total_equipment": 50,
  "data": [
    {
      "equipment_id": "TRC-001",
      "equipment_type": "Tractor",
      "model": "John Deere 6M",
      "failure_count": 5,
      "total_downtime": 45.5,
      "avg_downtime": 9.1,
      "total_cost": 12500.00,
      "mtbf_days": 122.5
    }
  ]
}
```

### 3. Type Reliability
```http
GET /analytics/type-reliability
```
**Description**: Get reliability metrics grouped by equipment type

**Response**:
```json
{
  "total_types": 4,
  "data": [
    {
      "equipment_type": "Tractor",
      "equipment_count": 50,
      "total_failures": 250,
      "total_downtime": 3000.0,
      "avg_downtime": 12.0,
      "total_cost": 350000.00,
      "avg_cost": 1400.00
    }
  ]
}
```

### 4. Maintenance Effectiveness
```http
GET /analytics/maintenance-effectiveness
```
**Description**: Analyze maintenance effectiveness and prevention rates

**Response**:
```json
{
  "prevention_rate": 61.1,
  "total_failures": 656,
  "prevented_failures": 401,
  "prevention_breakdown": [...],
  "maintenance_types": [
    {
      "type_id": 1,
      "maintenance_type": "Preventive",
      "count": 800,
      "total_cost": 450000.00,
      "total_downtime": 2500.0,
      "avg_cost": 562.50
    }
  ]
}
```

### 5. Cost-Benefit Analysis
```http
GET /analytics/cost-benefit
```
**Description**: Calculate comprehensive cost-benefit analysis

**Response**:
```json
{
  "total_failure_cost": 750000.00,
  "total_maintenance_cost": 450000.00,
  "total_downtime_cost": 500000.00,
  "total_cost": 1700000.00,
  "preventable_repair_cost": 300000.00,
  "preventable_downtime_cost": 200000.00,
  "total_preventable": 500000.00,
  "savings_percentage": 40.0,
  "downtime_cost_per_hour": 500,
  "recommendations": {
    "potential_savings": 500000.00,
    "expected_savings_70pct": 350000.00,
    "estimated_roi": "300% within 18 months"
  }
}
```

### 6. Worst Performers
```http
GET /analytics/worst-performers?limit=10
```
**Description**: Get equipment with lowest MTBF

**Response**:
```json
{
  "count": 10,
  "data": [
    {
      "equipment_id": "TRC-033",
      "equipment_type": "Tractor",
      "model": "Case IH Magnum",
      "failure_count": 7,
      "total_cost": 9322.75,
      "mtbf_days": 122.33
    }
  ]
}
```

### 7. Failure Trends
```http
GET /analytics/trends?days=30
```
**Description**: Get failure trends over time

**Response**:
```json
{
  "period_days": 30,
  "data_points": 28,
  "data": [
    {
      "date": "2024-10-01",
      "failure_count": 5,
      "daily_cost": 12500.00,
      "daily_downtime": 45.5
    }
  ]
}
```

### 8. Analytics Summary
```http
GET /analytics/summary
```
**Description**: Get comprehensive analytics summary

**Response**:
```json
{
  "total_equipment": 200,
  "total_failures": 656,
  "total_maintenance": 2095,
  "avg_downtime": 13.2,
  "total_failure_cost": 750000.00,
  "total_maintenance_cost": 450000.00,
  "prevented_failures": 401,
  "critical_failures": 59,
  "prevention_rate": 61.1,
  "last_updated": "2025-11-02T18:30:00"
}
```

### 9. Refresh Analytics
```http
POST /analytics/refresh
```
**Description**: Trigger analytics data refresh

**Response**:
```json
{
  "status": "success",
  "message": "Analytics refresh triggered",
  "timestamp": "2025-11-02T18:30:00"
}
```

## 📊 Existing KPI Endpoints

### Business KPIs
```http
GET /kpis/business
```

### Operational KPIs
```http
GET /kpis/operational
```

### Technical KPIs
```http
GET /kpis/technical
```

### Model KPIs
```http
GET /kpis/model
```

### Dashboard KPIs
```http
GET /kpis/dashboard
```

### KPI Summary
```http
GET /kpis/summary
```

## 🔧 Equipment Endpoints

### Get All Equipment
```http
GET /equipment
```

### Get Equipment by ID
```http
GET /equipment/{equipment_id}
```

### Get Equipment by Type
```http
GET /equipment/type/{equipment_type}
```

## 🔮 Prediction Endpoints

### Get Predictions
```http
GET /predictions
```

### Get Prediction by Equipment
```http
GET /predictions/equipment/{equipment_id}
```

## 📅 Schedule Endpoints

### Get Maintenance Schedule
```http
GET /schedule
```

### Get Schedule by Equipment
```http
GET /schedule/equipment/{equipment_id}
```

## 🔧 Maintenance Endpoints

### Get Maintenance Records
```http
GET /maintenance
```

### Get Maintenance by Equipment
```http
GET /maintenance/equipment/{equipment_id}
```

## 🏥 Health Check

### API Health
```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "WeeFarm Predictive Maintenance API",
  "version": "1.0.0"
}
```

## 📝 Usage Examples

### Python (using requests)
```python
import requests

base_url = "http://localhost:5000/api/v1"

# Get root cause analysis
response = requests.get(f"{base_url}/analytics/root-cause")
data = response.json()

# Get cost-benefit analysis
response = requests.get(f"{base_url}/analytics/cost-benefit")
cost_data = response.json()
```

### JavaScript (using fetch)
```javascript
const baseUrl = 'http://localhost:5000/api/v1';

// Get equipment reliability
fetch(`${baseUrl}/analytics/equipment-reliability`)
  .then(response => response.json())
  .then(data => console.log(data));
```

### Streamlit (using API client)
```python
from utils.api_client import get_api_client

api = get_api_client()

# Get analytics data
root_cause = api.get_root_cause_analysis()
reliability = api.get_equipment_reliability()
cost_benefit = api.get_cost_benefit_analysis()
```

## 🚀 Testing Endpoints

### Using curl
```bash
# Test root cause analysis
curl http://localhost:5000/api/v1/analytics/root-cause

# Test cost-benefit analysis
curl http://localhost:5000/api/v1/analytics/cost-benefit

# Test with parameters
curl "http://localhost:5000/api/v1/analytics/worst-performers?limit=5"
```

### Using Swagger UI
Navigate to: `http://localhost:5000/docs`

### Using ReDoc
Navigate to: `http://localhost:5000/redoc`

## 🔐 Authentication
Currently, no authentication is required. Add authentication middleware for production use.

## ⚠️ Error Responses

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

## 📊 Rate Limiting
No rate limiting currently implemented. Consider adding for production.

---

**Last Updated**: November 2, 2025
**API Version**: 1.0.0
