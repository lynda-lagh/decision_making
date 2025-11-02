# REST API Design - WeeFarm Predictive Maintenance
## API Specification Document

**Project**: WeeFarm  
**Date**: November 1, 2025  
**Framework**: Flask or FastAPI  
**Version**: 1.0  
**Base URL**: `http://localhost:5000/api/v1`

---

## 📊 API Overview

### Purpose
Provide RESTful API endpoints for the WeeFarm predictive maintenance pipeline, enabling:
- Equipment management
- Prediction execution and retrieval
- Maintenance scheduling
- Dashboard data access

### Key Features
- ✅ RESTful design principles
- ✅ JSON request/response format
- ✅ API key authentication
- ✅ Error handling with standard HTTP codes
- ✅ Pagination for large datasets
- ✅ Filtering and sorting capabilities

---

## 🔐 Authentication

### API Key Authentication

**Header**:
```
Authorization: Bearer <api_key>
```

**Example**:
```bash
curl -H "Authorization: Bearer your-api-key-here" \
     http://localhost:5000/api/v1/equipment
```

---

## 📋 API Endpoints

### 1. Equipment Endpoints

#### 1.1 List All Equipment

```
GET /api/v1/equipment
```

**Description**: Get list of all equipment with optional filtering

**Query Parameters**:
- `type` (optional): Filter by equipment type
- `location` (optional): Filter by location
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)
- `sort_by` (optional): Sort field (default: equipment_id)
- `order` (optional): Sort order (asc/desc, default: asc)

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "equipment_id": "EQ-001",
      "equipment_type": "Tractor",
      "brand": "John Deere",
      "model": "5075E",
      "year_manufactured": 2018,
      "location": "Jendouba",
      "operating_hours": 3500,
      "last_service_date": "2024-10-15",
      "health_status": "Good"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

---

#### 1.2 Get Equipment Details

```
GET /api/v1/equipment/{equipment_id}
```

**Description**: Get detailed information for specific equipment

**Path Parameters**:
- `equipment_id`: Equipment identifier (e.g., EQ-001)

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "equipment_id": "EQ-001",
    "equipment_type": "Tractor",
    "brand": "John Deere",
    "model": "5075E",
    "year_manufactured": 2018,
    "purchase_date": "2018-03-15",
    "location": "Jendouba",
    "operating_hours": 3500,
    "last_service_date": "2024-10-15",
    "age_years": 6,
    "maintenance_count": 15,
    "failure_count": 3,
    "latest_prediction": {
      "prediction_date": "2024-11-01",
      "risk_score": 72.0,
      "priority_level": "Critical",
      "recommended_action": "Schedule immediate maintenance"
    }
  }
}
```

**Error Response** (404 Not Found):
```json
{
  "success": false,
  "error": {
    "code": "EQUIPMENT_NOT_FOUND",
    "message": "Equipment with ID EQ-999 not found"
  }
}
```

---

#### 1.3 Create New Equipment

```
POST /api/v1/equipment
```

**Description**: Add new equipment to the system

**Request Body**:
```json
{
  "equipment_id": "EQ-101",
  "equipment_type": "Tractor",
  "brand": "Massey Ferguson",
  "model": "5710",
  "year_manufactured": 2023,
  "purchase_date": "2023-05-10",
  "location": "Nabeul",
  "operating_hours": 150
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "Equipment created successfully",
  "data": {
    "equipment_id": "EQ-101",
    "created_at": "2024-11-01T10:30:00Z"
  }
}
```

---

#### 1.4 Update Equipment

```
PUT /api/v1/equipment/{equipment_id}
```

**Description**: Update equipment information

**Request Body**:
```json
{
  "operating_hours": 3600,
  "last_service_date": "2024-11-01",
  "location": "Bizerte"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Equipment updated successfully",
  "data": {
    "equipment_id": "EQ-001",
    "updated_at": "2024-11-01T10:35:00Z"
  }
}
```

---

#### 1.5 Delete Equipment

```
DELETE /api/v1/equipment/{equipment_id}
```

**Description**: Delete equipment from system

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Equipment deleted successfully"
}
```

---

### 2. Prediction Endpoints

#### 2.1 Run Prediction Pipeline

```
POST /api/v1/predict
```

**Description**: Execute the ML prediction pipeline for all equipment or specific equipment

**Request Body** (Optional):
```json
{
  "equipment_ids": ["EQ-001", "EQ-002"],  // Optional: specific equipment
  "save_to_db": true,                      // Optional: save results (default: true)
  "send_alerts": true                      // Optional: send alerts (default: true)
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Prediction pipeline completed successfully",
  "data": {
    "total_equipment": 100,
    "predictions_generated": 100,
    "high_risk_count": 17,
    "critical_count": 5,
    "execution_time_seconds": 12.5,
    "timestamp": "2024-11-01T06:00:00Z"
  }
}
```

---

#### 2.2 Get All Predictions

```
GET /api/v1/predictions
```

**Description**: Get all predictions with filtering

**Query Parameters**:
- `date` (optional): Filter by prediction date (YYYY-MM-DD)
- `priority` (optional): Filter by priority (Critical/High/Medium/Low)
- `equipment_type` (optional): Filter by equipment type
- `page` (optional): Page number
- `per_page` (optional): Items per page

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "prediction_id": 1,
      "equipment_id": "EQ-001",
      "equipment_type": "Tractor",
      "prediction_date": "2024-11-01",
      "risk_score": 72.0,
      "priority_level": "Critical",
      "svm_prediction": 1,
      "xgb_prediction": 1,
      "recommended_action": "Schedule immediate maintenance within 24 hours"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100
  }
}
```

---

#### 2.3 Get Predictions for Equipment

```
GET /api/v1/predictions/equipment/{equipment_id}
```

**Description**: Get prediction history for specific equipment

**Query Parameters**:
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `limit` (optional): Number of records (default: 10)

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "equipment_id": "EQ-001",
    "predictions": [
      {
        "prediction_date": "2024-11-01",
        "risk_score": 72.0,
        "priority_level": "Critical"
      },
      {
        "prediction_date": "2024-10-31",
        "risk_score": 68.5,
        "priority_level": "High"
      }
    ]
  }
}
```

---

#### 2.4 Get Latest Predictions

```
GET /api/v1/predictions/latest
```

**Description**: Get most recent predictions for all equipment

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "prediction_date": "2024-11-01",
    "total_equipment": 100,
    "summary": {
      "critical": 5,
      "high": 12,
      "medium": 25,
      "low": 58
    },
    "predictions": [
      {
        "equipment_id": "EQ-001",
        "risk_score": 72.0,
        "priority_level": "Critical"
      }
    ]
  }
}
```

---

### 3. Maintenance Schedule Endpoints

#### 3.1 Get Maintenance Schedule

```
GET /api/v1/schedule
```

**Description**: Get maintenance schedule with filtering

**Query Parameters**:
- `start_date` (optional): Start date
- `end_date` (optional): End date
- `status` (optional): Filter by status
- `priority` (optional): Filter by priority
- `technician` (optional): Filter by assigned technician

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "schedule_id": 1,
      "equipment_id": "EQ-001",
      "equipment_type": "Tractor",
      "scheduled_date": "2024-11-02",
      "priority_level": "Critical",
      "risk_score": 72.0,
      "status": "Scheduled",
      "assigned_technician": "Ahmed Ben Ali",
      "estimated_cost": 500.00,
      "estimated_duration_hours": 4.0
    }
  ]
}
```

---

#### 3.2 Get Schedule by Priority

```
GET /api/v1/schedule/priority/{level}
```

**Description**: Get maintenance tasks by priority level

**Path Parameters**:
- `level`: Priority level (Critical/High/Medium/Low)

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "priority_level": "Critical",
    "count": 5,
    "tasks": [
      {
        "schedule_id": 1,
        "equipment_id": "EQ-001",
        "scheduled_date": "2024-11-02",
        "status": "Scheduled"
      }
    ]
  }
}
```

---

#### 3.3 Create Maintenance Task

```
POST /api/v1/schedule
```

**Description**: Create new maintenance task

**Request Body**:
```json
{
  "equipment_id": "EQ-001",
  "scheduled_date": "2024-11-05",
  "priority_level": "High",
  "risk_score": 65.0,
  "assigned_technician": "Mohamed Trabelsi",
  "estimated_cost": 350.00,
  "notes": "Preventive maintenance based on ML prediction"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "Maintenance task created successfully",
  "data": {
    "schedule_id": 15,
    "equipment_id": "EQ-001",
    "scheduled_date": "2024-11-05"
  }
}
```

---

#### 3.4 Update Maintenance Task

```
PUT /api/v1/schedule/{schedule_id}
```

**Description**: Update maintenance task

**Request Body**:
```json
{
  "status": "In Progress",
  "actual_start_time": "2024-11-02T08:00:00Z",
  "assigned_technician": "Ahmed Ben Ali"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Maintenance task updated successfully"
}
```

---

#### 3.5 Complete Maintenance Task

```
POST /api/v1/schedule/{schedule_id}/complete
```

**Description**: Mark maintenance task as completed

**Request Body**:
```json
{
  "actual_end_time": "2024-11-02T12:30:00Z",
  "actual_cost": 480.00,
  "completion_notes": "Replaced hydraulic fluid and filters. Equipment tested and operational."
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Maintenance task completed successfully",
  "data": {
    "schedule_id": 1,
    "status": "Completed",
    "duration_hours": 4.5,
    "cost_variance": -20.00
  }
}
```

---

### 4. Dashboard Endpoints

#### 4.1 Get Dashboard Summary

```
GET /api/v1/dashboard/summary
```

**Description**: Get summary statistics for dashboard

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "total_equipment": 100,
    "high_risk_equipment": 17,
    "critical_equipment": 5,
    "pending_maintenance": 12,
    "completed_this_month": 25,
    "total_cost_this_month": 15420.00,
    "estimated_savings": 8500.00,
    "average_health_score": 79.7,
    "last_prediction_date": "2024-11-01"
  }
}
```

---

#### 4.2 Get Active Alerts

```
GET /api/v1/dashboard/alerts
```

**Description**: Get active alerts for critical equipment

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "alert_count": 5,
    "alerts": [
      {
        "alert_id": 1,
        "equipment_id": "EQ-001",
        "equipment_type": "Tractor",
        "location": "Jendouba",
        "priority": "Critical",
        "risk_score": 72.0,
        "message": "Equipment requires immediate maintenance",
        "created_at": "2024-11-01T06:00:00Z"
      }
    ]
  }
}
```

---

#### 4.3 Get Performance Metrics

```
GET /api/v1/dashboard/metrics
```

**Description**: Get model performance and system metrics

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "model_performance": {
      "svm": {
        "accuracy": 0.45,
        "precision": 0.35,
        "recall": 1.00,
        "f1_score": 0.52
      },
      "xgboost": {
        "accuracy": 0.75,
        "precision": 0.60,
        "recall": 0.50,
        "f1_score": 0.55
      }
    },
    "pipeline_metrics": {
      "last_run": "2024-11-01T06:00:00Z",
      "execution_time_seconds": 12.5,
      "predictions_generated": 100,
      "success_rate": 100.0
    },
    "business_metrics": {
      "cost_reduction_percent": 44.0,
      "maintenance_efficiency": 65.0,
      "downtime_reduction_percent": 30.0
    }
  }
}
```

---

### 5. Maintenance Records Endpoints

#### 5.1 Get Maintenance History

```
GET /api/v1/maintenance
```

**Description**: Get maintenance records with filtering

**Query Parameters**:
- `equipment_id` (optional): Filter by equipment
- `type` (optional): Filter by type (1: Preventive, 2: Corrective, 3: Predictive)
- `start_date` (optional): Start date
- `end_date` (optional): End date

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "record_id": 1,
      "equipment_id": "EQ-001",
      "maintenance_date": "2024-10-15",
      "type_id": 1,
      "type_name": "Preventive",
      "description": "Routine oil change",
      "technician": "Ahmed Ben Ali",
      "total_cost": 280.00,
      "downtime_hours": 2.5
    }
  ]
}
```

---

### 6. Failure Events Endpoints

#### 6.1 Get Failure History

```
GET /api/v1/failures
```

**Description**: Get failure events with filtering

**Query Parameters**:
- `equipment_id` (optional): Filter by equipment
- `severity` (optional): Filter by severity
- `start_date` (optional): Start date
- `end_date` (optional): End date

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "failure_id": 1,
      "equipment_id": "EQ-001",
      "failure_date": "2024-08-10",
      "failure_type": "Engine Overheating",
      "severity": "Moderate",
      "repair_cost": 1200.00,
      "downtime_hours": 12.0,
      "prevented_by_maintenance": true
    }
  ]
}
```

---

## 🔒 Error Handling

### Standard Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}  // Optional additional details
  }
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid API key |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Duplicate resource |
| 500 | Internal Server Error | Server error |

### Error Codes

| Code | Description |
|------|-------------|
| `INVALID_REQUEST` | Request validation failed |
| `EQUIPMENT_NOT_FOUND` | Equipment ID not found |
| `PREDICTION_FAILED` | ML prediction failed |
| `DATABASE_ERROR` | Database operation failed |
| `UNAUTHORIZED` | Authentication failed |
| `PIPELINE_ERROR` | Pipeline execution failed |

---

## 📝 Request/Response Examples

### Example: Run Prediction and Get Results

**Step 1: Run Prediction**
```bash
curl -X POST http://localhost:5000/api/v1/predict \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Step 2: Get Latest Predictions**
```bash
curl -X GET http://localhost:5000/api/v1/predictions/latest \
  -H "Authorization: Bearer your-api-key"
```

**Step 3: Create Maintenance Tasks**
```bash
curl -X POST http://localhost:5000/api/v1/schedule \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": "EQ-001",
    "scheduled_date": "2024-11-02",
    "priority_level": "Critical",
    "risk_score": 72.0
  }'
```

---

## 🔧 Implementation Notes

### Flask Implementation

```python
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/weefarm_db'
db = SQLAlchemy(app)

@app.route('/api/v1/equipment', methods=['GET'])
def get_equipment():
    equipment = Equipment.query.all()
    return jsonify({
        'success': True,
        'data': [e.to_dict() for e in equipment]
    })

@app.route('/api/v1/predict', methods=['POST'])
def run_prediction():
    pipeline = WeeFarmPipeline(config)
    results = pipeline.run()
    return jsonify({
        'success': True,
        'message': 'Prediction completed',
        'data': results
    }), 200
```

---

## 📚 API Documentation

### Swagger/OpenAPI

Generate interactive API documentation using Swagger UI:

```yaml
openapi: 3.0.0
info:
  title: WeeFarm Predictive Maintenance API
  version: 1.0.0
  description: REST API for agricultural equipment predictive maintenance

servers:
  - url: http://localhost:5000/api/v1
    description: Development server

paths:
  /equipment:
    get:
      summary: List all equipment
      responses:
        '200':
          description: Successful response
```

---

**End of Document**
