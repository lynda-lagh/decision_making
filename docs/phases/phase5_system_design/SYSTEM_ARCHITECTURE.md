# System Architecture - WeeFarm Predictive Maintenance Pipeline
## End-to-End ML Pipeline for Agricultural Equipment

**Project**: WeeFarm Data-Driven Maintenance Management  
**Date**: November 1, 2025  
**Version**: 1.0  
**Status**: Design Phase

---

## 📊 Executive Summary

This document describes the complete system architecture for the WeeFarm predictive maintenance pipeline. The system is designed as an **end-to-end ML pipeline** that automates data ingestion, feature engineering, model prediction, and decision-making for agricultural equipment maintenance.

### Key Features

- ✅ **Automated Pipeline**: End-to-end automation from data to decisions
- ✅ **Real-time Predictions**: Daily equipment health assessments
- ✅ **Scalable Architecture**: PostgreSQL + Python + REST API
- ✅ **ML Model Integration**: Hybrid SVM + XGBoost approach
- ✅ **Interactive Dashboard**: Real-time monitoring and alerts

---

## 🏗️ System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    WeeFarm ML Pipeline System                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Data      │      │   Feature    │      │    Model    │
│  Ingestion  │─────►│  Engineering │─────►│  Prediction │
│   Layer     │      │   Pipeline   │      │   Engine    │
└─────────────┘      └──────────────┘      └──────┬──────┘
                                                    │
┌─────────────┐      ┌──────────────┐             │
│ PostgreSQL  │◄─────┤  Backend API │◄────────────┘
│  Database   │      │   (Flask)    │
└─────────────┘      └──────┬───────┘
                            │
                     ┌──────▼───────┐
                     │  Dashboard   │
                     │ (Streamlit)  │
                     └──────────────┘
```

---

## 🔄 ML Pipeline Architecture

### Complete Pipeline Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                      WEEFARM ML PIPELINE                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  STAGE 1: DATA INGESTION                                        │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ • Equipment data (CSV/Database)                        │    │
│  │ • Maintenance records                                   │    │
│  │ • Failure events                                        │    │
│  │ • Real-time sensor data (future)                       │    │
│  └────────────────┬───────────────────────────────────────┘    │
│                   │                                              │
│                   ▼                                              │
│  STAGE 2: DATA VALIDATION & CLEANING                           │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ • Check for missing values                             │    │
│  │ • Validate data types                                   │    │
│  │ • Remove duplicates                                     │    │
│  │ • Handle outliers                                       │    │
│  └────────────────┬───────────────────────────────────────┘    │
│                   │                                              │
│                   ▼                                              │
│  STAGE 3: FEATURE ENGINEERING                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ • Calculate equipment age                              │    │
│  │ • Aggregate maintenance history                        │    │
│  │ • Aggregate failure history                            │    │
│  │ • Calculate health score                               │    │
│  │ • Select top 10 features                               │    │
│  └────────────────┬───────────────────────────────────────┘    │
│                   │                                              │
│                   ▼                                              │
│  STAGE 4: MODEL PREDICTION (HYBRID APPROACH)                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Step 1: SVM Screening (High Sensitivity)              │    │
│  │   • Predict high-risk equipment                        │    │
│  │   • Output: ~17 flagged equipment                      │    │
│  │                                                         │    │
│  │ Step 2: XGBoost Prioritization (High Precision)       │    │
│  │   • Calculate risk scores (0-100%)                     │    │
│  │   • Assign priority levels                             │    │
│  │   • Output: Prioritized maintenance list               │    │
│  └────────────────┬───────────────────────────────────────┘    │
│                   │                                              │
│                   ▼                                              │
│  STAGE 5: DECISION ENGINE                                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ • Critical (>70%): Immediate maintenance               │    │
│  │ • High (40-70%): Within 1 week                         │    │
│  │ • Medium (20-40%): Within 2 weeks                      │    │
│  │ • Low (<20%): Monitor closely                          │    │
│  └────────────────┬───────────────────────────────────────┘    │
│                   │                                              │
│                   ▼                                              │
│  STAGE 6: OUTPUT & STORAGE                                     │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ • Save predictions to database                         │    │
│  │ • Generate maintenance schedule                        │    │
│  │ • Send alerts/notifications                            │    │
│  │ • Update dashboard                                      │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Data Layer

### PostgreSQL Database Schema

```sql
-- Equipment Table
CREATE TABLE equipment (
    equipment_id VARCHAR(10) PRIMARY KEY,
    equipment_type VARCHAR(50),
    brand VARCHAR(50),
    model VARCHAR(50),
    year_manufactured INT,
    purchase_date DATE,
    location VARCHAR(50),
    operating_hours INT,
    last_service_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Maintenance Records Table
CREATE TABLE maintenance_records (
    record_id SERIAL PRIMARY KEY,
    equipment_id VARCHAR(10) REFERENCES equipment(equipment_id),
    maintenance_date DATE,
    type_id INT, -- 1: Preventive, 2: Corrective, 3: Predictive
    description TEXT,
    technician VARCHAR(100),
    parts_replaced TEXT,
    total_cost DECIMAL(10, 2),
    downtime_hours DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Failure Events Table
CREATE TABLE failure_events (
    failure_id SERIAL PRIMARY KEY,
    equipment_id VARCHAR(10) REFERENCES equipment(equipment_id),
    failure_date DATE,
    failure_type VARCHAR(50),
    severity VARCHAR(20), -- Minor, Moderate, Critical
    description TEXT,
    repair_cost DECIMAL(10, 2),
    downtime_hours DECIMAL(5, 2),
    prevented_by_maintenance BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Predictions Table (NEW - for pipeline output)
CREATE TABLE predictions (
    prediction_id SERIAL PRIMARY KEY,
    equipment_id VARCHAR(10) REFERENCES equipment(equipment_id),
    prediction_date DATE,
    svm_prediction INT, -- 0: No Fail, 1: Will Fail
    svm_probability DECIMAL(5, 4),
    xgb_prediction INT,
    xgb_probability DECIMAL(5, 4),
    risk_score DECIMAL(5, 2), -- 0-100
    priority_level VARCHAR(20), -- Critical, High, Medium, Low
    recommended_action TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Maintenance Schedule Table (NEW - for pipeline output)
CREATE TABLE maintenance_schedule (
    schedule_id SERIAL PRIMARY KEY,
    equipment_id VARCHAR(10) REFERENCES equipment(equipment_id),
    scheduled_date DATE,
    priority_level VARCHAR(20),
    risk_score DECIMAL(5, 2),
    status VARCHAR(20), -- Pending, Scheduled, Completed, Cancelled
    assigned_technician VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model Performance Tracking (NEW - for monitoring)
CREATE TABLE model_performance (
    performance_id SERIAL PRIMARY KEY,
    model_name VARCHAR(50),
    evaluation_date DATE,
    accuracy DECIMAL(5, 4),
    precision_score DECIMAL(5, 4),
    recall DECIMAL(5, 4),
    f1_score DECIMAL(5, 4),
    roc_auc DECIMAL(5, 4),
    sample_size INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔧 Pipeline Components

### 1. Data Ingestion Module

**File**: `src/pipeline/data_ingestion.py`

```python
class DataIngestionPipeline:
    """
    Ingests data from various sources into the pipeline
    """
    def __init__(self, db_connection):
        self.db = db_connection
    
    def load_equipment_data(self):
        """Load equipment data from database"""
        pass
    
    def load_maintenance_records(self):
        """Load maintenance records"""
        pass
    
    def load_failure_events(self):
        """Load failure events"""
        pass
    
    def validate_data(self, data):
        """Validate data quality"""
        pass
```

---

### 2. Feature Engineering Module

**File**: `src/pipeline/feature_engineering.py`

```python
class FeatureEngineeringPipeline:
    """
    Transforms raw data into ML-ready features
    """
    def __init__(self):
        self.selected_features = [
            'age', 'operating_hours', 'usage_intensity',
            'maintenance_count', 'preventive_ratio', 
            'maintenance_frequency', 'failure_count',
            'failure_rate', 'mtbf', 'health_score'
        ]
    
    def calculate_equipment_features(self, equipment_df):
        """Calculate age, usage intensity"""
        pass
    
    def aggregate_maintenance_features(self, maintenance_df):
        """Aggregate maintenance history"""
        pass
    
    def aggregate_failure_features(self, failure_df):
        """Aggregate failure history"""
        pass
    
    def calculate_health_score(self, features_df):
        """Calculate composite health score"""
        pass
    
    def select_features(self, features_df):
        """Select top 10 features"""
        return features_df[self.selected_features]
```

---

### 3. Model Prediction Module

**File**: `src/pipeline/model_prediction.py`

```python
class ModelPredictionPipeline:
    """
    Hybrid two-stage prediction pipeline
    """
    def __init__(self, svm_model_path, xgb_model_path):
        self.svm_model = joblib.load(svm_model_path)
        self.xgb_model = joblib.load(xgb_model_path)
    
    def stage1_svm_screening(self, features):
        """
        Stage 1: SVM screening for high-risk equipment
        Returns: high_risk_mask, probabilities
        """
        predictions = self.svm_model.predict(features)
        probabilities = self.svm_model.predict_proba(features)[:, 1]
        return predictions, probabilities
    
    def stage2_xgb_prioritization(self, features):
        """
        Stage 2: XGBoost prioritization
        Returns: risk_scores, priority_levels
        """
        risk_scores = self.xgb_model.predict_proba(features)[:, 1]
        priority_levels = self.assign_priority(risk_scores)
        return risk_scores, priority_levels
    
    def assign_priority(self, risk_scores):
        """
        Assign priority levels based on risk scores
        """
        priorities = []
        for score in risk_scores:
            if score > 0.7:
                priorities.append('Critical')
            elif score > 0.4:
                priorities.append('High')
            elif score > 0.2:
                priorities.append('Medium')
            else:
                priorities.append('Low')
        return priorities
    
    def predict(self, features):
        """
        Complete hybrid prediction pipeline
        """
        # Stage 1: SVM screening
        svm_pred, svm_prob = self.stage1_svm_screening(features)
        
        # Stage 2: XGBoost prioritization
        xgb_risk, xgb_priority = self.stage2_xgb_prioritization(features)
        
        return {
            'svm_prediction': svm_pred,
            'svm_probability': svm_prob,
            'risk_score': xgb_risk * 100,  # Convert to 0-100
            'priority_level': xgb_priority
        }
```

---

### 4. Decision Engine Module

**File**: `src/pipeline/decision_engine.py`

```python
class DecisionEngine:
    """
    Makes maintenance decisions based on predictions
    """
    def __init__(self):
        self.action_map = {
            'Critical': 'Schedule immediate maintenance (within 24 hours)',
            'High': 'Schedule maintenance within 1 week',
            'Medium': 'Schedule maintenance within 2 weeks',
            'Low': 'Monitor closely, regular maintenance schedule'
        }
    
    def generate_recommendations(self, predictions_df):
        """
        Generate maintenance recommendations
        """
        recommendations = []
        for idx, row in predictions_df.iterrows():
            recommendation = {
                'equipment_id': row['equipment_id'],
                'priority': row['priority_level'],
                'risk_score': row['risk_score'],
                'action': self.action_map[row['priority_level']],
                'estimated_cost': self.estimate_cost(row['priority_level']),
                'scheduled_date': self.calculate_schedule_date(row['priority_level'])
            }
            recommendations.append(recommendation)
        return recommendations
    
    def estimate_cost(self, priority):
        """Estimate maintenance cost based on priority"""
        cost_map = {
            'Critical': 500,
            'High': 350,
            'Medium': 280,
            'Low': 200
        }
        return cost_map.get(priority, 280)
    
    def calculate_schedule_date(self, priority):
        """Calculate recommended maintenance date"""
        from datetime import datetime, timedelta
        today = datetime.now()
        
        schedule_map = {
            'Critical': today + timedelta(days=1),
            'High': today + timedelta(days=7),
            'Medium': today + timedelta(days=14),
            'Low': today + timedelta(days=30)
        }
        return schedule_map.get(priority, today + timedelta(days=14))
```

---

### 5. Main Pipeline Orchestrator

**File**: `src/pipeline/main_pipeline.py`

```python
class WeeFarmPipeline:
    """
    Main pipeline orchestrator - runs end-to-end ML pipeline
    """
    def __init__(self, config):
        self.config = config
        self.db = self.connect_database()
        self.data_ingestion = DataIngestionPipeline(self.db)
        self.feature_engineering = FeatureEngineeringPipeline()
        self.model_prediction = ModelPredictionPipeline(
            svm_model_path='models/failure_prediction_model.pkl',
            xgb_model_path='models/failure_prediction_model_improved.pkl'
        )
        self.decision_engine = DecisionEngine()
    
    def run(self):
        """
        Execute complete ML pipeline
        """
        print("="*80)
        print("WEEFARM ML PIPELINE - STARTING")
        print("="*80)
        
        # Stage 1: Data Ingestion
        print("\n[1/6] Data Ingestion...")
        equipment = self.data_ingestion.load_equipment_data()
        maintenance = self.data_ingestion.load_maintenance_records()
        failures = self.data_ingestion.load_failure_events()
        print(f"✅ Loaded {len(equipment)} equipment records")
        
        # Stage 2: Data Validation
        print("\n[2/6] Data Validation...")
        equipment = self.data_ingestion.validate_data(equipment)
        print("✅ Data validated")
        
        # Stage 3: Feature Engineering
        print("\n[3/6] Feature Engineering...")
        features = self.feature_engineering.calculate_equipment_features(equipment)
        features = self.feature_engineering.aggregate_maintenance_features(
            features, maintenance
        )
        features = self.feature_engineering.aggregate_failure_features(
            features, failures
        )
        features = self.feature_engineering.calculate_health_score(features)
        features_selected = self.feature_engineering.select_features(features)
        print(f"✅ Generated {len(features_selected.columns)} features")
        
        # Stage 4: Model Prediction
        print("\n[4/6] Model Prediction...")
        predictions = self.model_prediction.predict(features_selected)
        print(f"✅ Generated predictions for {len(equipment)} equipment")
        
        # Stage 5: Decision Engine
        print("\n[5/6] Generating Recommendations...")
        recommendations = self.decision_engine.generate_recommendations(predictions)
        print(f"✅ Generated {len(recommendations)} recommendations")
        
        # Stage 6: Save Results
        print("\n[6/6] Saving Results...")
        self.save_predictions(predictions)
        self.save_maintenance_schedule(recommendations)
        print("✅ Results saved to database")
        
        print("\n" + "="*80)
        print("PIPELINE COMPLETE!")
        print("="*80)
        
        return recommendations
    
    def save_predictions(self, predictions):
        """Save predictions to database"""
        # Implementation here
        pass
    
    def save_maintenance_schedule(self, recommendations):
        """Save maintenance schedule to database"""
        # Implementation here
        pass
```

---

## 🌐 API Layer

### REST API Endpoints

**Framework**: Flask or FastAPI

#### Equipment Endpoints

```
GET    /api/equipment                  # List all equipment
GET    /api/equipment/{id}             # Get equipment details
POST   /api/equipment                  # Add new equipment
PUT    /api/equipment/{id}             # Update equipment
DELETE /api/equipment/{id}             # Delete equipment
```

#### Prediction Endpoints

```
POST   /api/predict                    # Run prediction pipeline
GET    /api/predictions                # Get all predictions
GET    /api/predictions/{equipment_id} # Get predictions for equipment
GET    /api/predictions/latest         # Get latest predictions
```

#### Maintenance Schedule Endpoints

```
GET    /api/schedule                   # Get maintenance schedule
GET    /api/schedule/priority/{level}  # Get by priority (Critical/High/Medium/Low)
POST   /api/schedule                   # Create maintenance task
PUT    /api/schedule/{id}              # Update maintenance task
DELETE /api/schedule/{id}              # Cancel maintenance task
```

#### Dashboard Endpoints

```
GET    /api/dashboard/summary          # Dashboard summary stats
GET    /api/dashboard/alerts           # Get active alerts
GET    /api/dashboard/metrics          # Get performance metrics
```

---

## 📊 Dashboard Layer

### Streamlit Dashboard

**File**: `src/dashboard/app.py`

#### Dashboard Pages

1. **Overview Page**
   - Total equipment count
   - High-risk equipment count
   - Upcoming maintenance tasks
   - Cost savings summary

2. **Equipment Health Page**
   - Equipment list with health scores
   - Filter by location, type, priority
   - Search functionality

3. **Maintenance Schedule Page**
   - Calendar view of scheduled maintenance
   - Priority-based task list
   - Technician assignment

4. **Predictions Page**
   - Latest prediction results
   - Risk score distribution
   - Model performance metrics

5. **Analytics Page**
   - Cost trends
   - Failure patterns
   - Maintenance effectiveness
   - ROI analysis

---

## 🔄 Pipeline Execution Flow

### Daily Automated Run

```
┌─────────────────────────────────────────┐
│  Scheduled Task (Cron/Task Scheduler)   │
│  Runs daily at 6:00 AM                  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  1. Data Ingestion                      │
│     - Load latest equipment data        │
│     - Load new maintenance records      │
│     - Load new failure events           │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  2. Feature Engineering                 │
│     - Calculate features for all equip  │
│     - Update health scores              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  3. Model Prediction                    │
│     - SVM screening                     │
│     - XGBoost prioritization            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  4. Decision Engine                     │
│     - Generate recommendations          │
│     - Update maintenance schedule       │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  5. Notifications                       │
│     - Send alerts for critical items    │
│     - Email maintenance schedule        │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  6. Dashboard Update                    │
│     - Refresh dashboard data            │
│     - Update visualizations             │
└─────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: Flask or FastAPI
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy
- **ML Libraries**: scikit-learn, XGBoost, joblib

### Frontend
- **Dashboard**: Streamlit or Plotly Dash
- **Visualization**: Plotly, Matplotlib, Seaborn

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Scheduling**: APScheduler or Cron
- **Monitoring**: Prometheus + Grafana (optional)

---

## 📦 Deployment Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Production Server                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────┐     ┌─────────────────┐           │
│  │  PostgreSQL     │     │  Flask API      │           │
│  │  Container      │◄────┤  Container      │           │
│  │  Port: 5432     │     │  Port: 5000     │           │
│  └─────────────────┘     └────────┬────────┘           │
│                                    │                     │
│  ┌─────────────────┐              │                     │
│  │  Streamlit      │◄─────────────┘                     │
│  │  Dashboard      │                                     │
│  │  Port: 8501     │                                     │
│  └─────────────────┘                                     │
│                                                           │
│  ┌─────────────────┐                                     │
│  │  Pipeline       │                                     │
│  │  Scheduler      │                                     │
│  │  (Cron/APSched) │                                     │
│  └─────────────────┘                                     │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Considerations

### Authentication & Authorization
- API key authentication for API endpoints
- Role-based access control (Admin, Technician, Viewer)
- Secure password hashing (bcrypt)

### Data Security
- Database connection encryption (SSL)
- Environment variables for sensitive data
- Input validation and sanitization
- SQL injection prevention (parameterized queries)

### Model Security
- Model versioning and tracking
- Model file integrity checks
- Secure model storage

---

## 📈 Monitoring & Logging

### Pipeline Monitoring
- Log each pipeline stage execution
- Track execution time per stage
- Monitor prediction quality
- Alert on pipeline failures

### Model Monitoring
- Track model performance over time
- Monitor prediction distribution
- Detect model drift
- Retrain triggers

### System Monitoring
- Database performance
- API response times
- Dashboard load times
- Resource usage (CPU, memory)

---

## 🔄 CI/CD Pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Code      │────►│   Build &   │────►│   Deploy    │
│   Commit    │     │   Test      │     │   to Prod   │
└─────────────┘     └─────────────┘     └─────────────┘
      │                    │                    │
      │                    │                    │
      ▼                    ▼                    ▼
  Git Push          Unit Tests           Docker Deploy
                    Integration          Update Models
                    Model Tests          Restart Services
```

---

## 📝 Configuration Management

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/weefarm

# API
API_HOST=0.0.0.0
API_PORT=5000
API_SECRET_KEY=your-secret-key

# Models
SVM_MODEL_PATH=models/failure_prediction_model.pkl
XGB_MODEL_PATH=models/failure_prediction_model_improved.pkl

# Pipeline
PIPELINE_SCHEDULE=0 6 * * *  # Daily at 6 AM
ALERT_EMAIL=maintenance@weefarm.tn
```

---

## 🎯 Success Metrics

### Pipeline Performance
- **Execution Time**: <5 minutes for 100 equipment
- **Prediction Accuracy**: >75%
- **API Response Time**: <200ms
- **Dashboard Load Time**: <2 seconds

### Business Metrics
- **Cost Reduction**: 40%+ vs reactive maintenance
- **Downtime Reduction**: 30%+
- **Maintenance Efficiency**: 60%+ prediction accuracy
- **ROI**: Positive within 6 months

---

## 🚀 Next Steps

1. ✅ Set up PostgreSQL database
2. ✅ Implement pipeline modules
3. ✅ Build REST API
4. ✅ Create Streamlit dashboard
5. ✅ Deploy with Docker
6. ✅ Set up monitoring
7. ✅ Test end-to-end

---

**End of Document**
