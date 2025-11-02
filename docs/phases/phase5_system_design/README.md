# Phase 5: System Design
## WeeFarm - Predictive Maintenance Pipeline

**Status**: ✅ Complete  
**Date**: November 1, 2025  
**Duration**: Design Phase

---

## 📋 Overview

Phase 5 focuses on designing the complete system architecture for the WeeFarm predictive maintenance pipeline. This includes database schema, API design, dashboard wireframes, and ML pipeline integration.

---

## 🎯 Objectives Achieved

- ✅ Design end-to-end ML pipeline architecture
- ✅ Create PostgreSQL database schema
- ✅ Design REST API endpoints
- ✅ Create dashboard wireframes
- ✅ Plan model integration strategy
- ✅ Document deployment architecture

---

## 📁 Documents in This Phase

### 1. **SYSTEM_ARCHITECTURE.md** ⭐
**Complete System Architecture**
- ML pipeline flow (6 stages)
- Component architecture
- Technology stack
- Deployment strategy
- Monitoring & logging

**Key Features**:
- End-to-end automation
- Hybrid SVM + XGBoost approach
- Real-time predictions
- Scalable design

[📄 View Document](./SYSTEM_ARCHITECTURE.md)

---

### 2. **DATABASE_SCHEMA.md** ⭐
**PostgreSQL Database Design**
- 6 tables with relationships
- Indexes for performance
- Views for common queries
- Functions and triggers
- Sample data

**Tables**:
1. equipment
2. maintenance_records
3. failure_events
4. predictions (NEW)
5. maintenance_schedule (NEW)
6. model_performance (NEW)

[📄 View Document](./DATABASE_SCHEMA.md)

---

### 3. **API_DESIGN.md** ⭐
**REST API Specification**
- 25+ API endpoints
- Request/response formats
- Authentication (API key)
- Error handling
- Pagination & filtering

**Endpoint Categories**:
- Equipment management
- Prediction execution
- Maintenance scheduling
- Dashboard data
- Analytics

[📄 View Document](./API_DESIGN.md)

---

### 4. **DASHBOARD_WIREFRAMES.md** ⭐
**Dashboard UI Design**
- 6 pages wireframed
- Color scheme
- Responsive design
- User interactions

**Pages**:
1. Overview
2. Equipment Health
3. Predictions
4. Maintenance Schedule
5. Analytics
6. Settings

[📄 View Document](./DASHBOARD_WIREFRAMES.md)

---

### 5. **KPI_FRAMEWORK.md** ⭐
**Key Performance Indicators**
- 4 KPI categories (Business, Technical, Operational, Model)
- 25+ KPIs defined
- Targets and thresholds
- Color-coded performance levels
- Tracking and reporting strategy

**KPI Categories**:
1. **Business KPIs**: Cost reduction (44%), ROI (833%), downtime avoided
2. **Technical KPIs**: System uptime (99.8%), API response (<200ms)
3. **Operational KPIs**: Preventive ratio (38.7%), MTBF (1,633h), MTTR
4. **Model KPIs**: Accuracy (75%), Precision (60%), Recall (100%)

[📄 View Document](./KPI_FRAMEWORK.md)

---

### 6. **README.md** (~15 pages)
**Phase 5 Summary**
- Overview of all documents
- Quick reference guide
- Next steps for Phase 6

---

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────┐
│                    WeeFarm ML Pipeline                   │
└─────────────────────────────────────────────────────────┘

Data Ingestion → Feature Engineering → Model Prediction →
Decision Engine → Output & Storage

┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│ PostgreSQL  │◄─────┤  Backend API │◄─────┤  Dashboard  │
│  Database   │      │   (Flask)    │      │ (Streamlit) │
└─────────────┘      └──────────────┘      └─────────────┘
```

---

## 🔄 ML Pipeline Stages

### Stage 1: Data Ingestion
- Load equipment data
- Load maintenance records
- Load failure events
- Validate data quality

### Stage 2: Feature Engineering
- Calculate equipment features (age, usage)
- Aggregate maintenance history
- Aggregate failure history
- Calculate health scores
- Select top 10 features

### Stage 3: Model Prediction (Hybrid)
- **Step 1**: SVM Screening (high sensitivity)
  - Flags ~17 high-risk equipment
- **Step 2**: XGBoost Prioritization (high precision)
  - Calculates risk scores (0-100%)
  - Assigns priority levels

### Stage 4: Decision Engine
- Critical (>70%): Immediate maintenance
- High (40-70%): Within 1 week
- Medium (20-40%): Within 2 weeks
- Low (<20%): Monitor closely

### Stage 5: Output & Storage
- Save predictions to database
- Generate maintenance schedule
- Send alerts/notifications
- Update dashboard

---

## 🗄️ Database Schema

### Core Tables

**equipment**: 100 equipment units
- equipment_id, type, brand, model
- location, operating_hours
- last_service_date

**maintenance_records**: Maintenance history
- maintenance_date, type_id
- total_cost, downtime_hours

**failure_events**: Failure history
- failure_date, severity
- repair_cost, downtime_hours

### Pipeline Output Tables

**predictions**: ML model outputs
- svm_prediction, xgb_prediction
- risk_score, priority_level
- recommended_action

**maintenance_schedule**: Generated schedule
- scheduled_date, priority_level
- assigned_technician, status
- estimated_cost

**model_performance**: Model tracking
- accuracy, precision, recall
- f1_score, roc_auc

---

## 🌐 API Endpoints

### Equipment
- `GET /api/v1/equipment` - List all
- `GET /api/v1/equipment/{id}` - Get details
- `POST /api/v1/equipment` - Create new
- `PUT /api/v1/equipment/{id}` - Update
- `DELETE /api/v1/equipment/{id}` - Delete

### Predictions
- `POST /api/v1/predict` - Run pipeline
- `GET /api/v1/predictions` - Get all
- `GET /api/v1/predictions/equipment/{id}` - By equipment
- `GET /api/v1/predictions/latest` - Latest results

### Maintenance Schedule
- `GET /api/v1/schedule` - Get schedule
- `GET /api/v1/schedule/priority/{level}` - By priority
- `POST /api/v1/schedule` - Create task
- `PUT /api/v1/schedule/{id}` - Update task
- `POST /api/v1/schedule/{id}/complete` - Complete task

### Dashboard
- `GET /api/v1/dashboard/summary` - Summary stats
- `GET /api/v1/dashboard/alerts` - Active alerts
- `GET /api/v1/dashboard/metrics` - Performance metrics

---

## 📊 Dashboard Pages

### 1. Overview Page
- Total equipment: 100
- High-risk equipment: 17
- Critical alerts: 5
- Pending maintenance: 12
- Cost this month
- Estimated savings

### 2. Equipment Health Page
- Equipment list with filters
- Risk scores and priorities
- Health scores (0-100)
- Equipment details
- Maintenance history

### 3. Predictions Page
- Latest prediction run
- Risk distribution
- SVM + XGBoost results
- Model performance
- Recommendations

### 4. Maintenance Schedule Page
- Calendar view
- Task list by priority
- Technician workload
- Task management

### 5. Analytics Page
- Cost analysis
- Maintenance effectiveness
- Failure analysis
- Model performance tracking
- Regional analysis

### 6. Settings Page
- System configuration
- Model settings
- Alert configuration
- User management

---

## 🛠️ Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: Flask or FastAPI
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy
- **ML**: scikit-learn, XGBoost

### Frontend
- **Dashboard**: Streamlit
- **Visualization**: Plotly, Matplotlib

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Scheduling**: APScheduler
- **Monitoring**: Logging

---

## 📦 Deployment Architecture

```
┌──────────────────────────────────────────┐
│         Production Server                 │
├──────────────────────────────────────────┤
│                                           │
│  ┌─────────────┐   ┌─────────────┐      │
│  │ PostgreSQL  │   │  Flask API  │      │
│  │ Container   │◄──┤  Container  │      │
│  │ Port: 5432  │   │  Port: 5000 │      │
│  └─────────────┘   └──────┬──────┘      │
│                            │              │
│  ┌─────────────┐          │              │
│  │ Streamlit   │◄─────────┘              │
│  │ Dashboard   │                          │
│  │ Port: 8501  │                          │
│  └─────────────┘                          │
│                                           │
│  ┌─────────────┐                          │
│  │  Pipeline   │                          │
│  │  Scheduler  │                          │
│  │  (Daily 6AM)│                          │
│  └─────────────┘                          │
│                                           │
└──────────────────────────────────────────┘
```

---

## 🔐 Security

### Authentication
- API key authentication
- Role-based access control
- Secure password hashing

### Data Security
- Database encryption (SSL)
- Environment variables
- Input validation
- SQL injection prevention

---

## 📈 Monitoring

### Pipeline Monitoring
- Log execution stages
- Track execution time
- Monitor prediction quality
- Alert on failures

### Model Monitoring
- Track performance metrics
- Monitor prediction distribution
- Detect model drift
- Retrain triggers

### System Monitoring
- Database performance
- API response times
- Dashboard load times
- Resource usage

---

## 🚀 Next Steps (Phase 6)

### Implementation Tasks

1. **PostgreSQL Setup**
   - Install PostgreSQL
   - Create database
   - Run schema scripts
   - Migrate CSV data

2. **Pipeline Development**
   - Implement data ingestion
   - Build feature engineering
   - Integrate ML models
   - Create decision engine

3. **API Development**
   - Set up Flask application
   - Implement endpoints
   - Add authentication
   - Test API

4. **Dashboard Development**
   - Create Streamlit app
   - Build all 6 pages
   - Add visualizations
   - Connect to API

5. **Testing & Deployment**
   - Unit tests
   - Integration tests
   - Docker setup
   - Deploy to server

---

## 📚 Related Documents

### Phase 4 Documents
- [Failure Prediction Model Summary](../phase4_model_development/FAILURE_PREDICTION_MODEL_SUMMARY.md)
- [Phase 4 README](../phase4_model_development/README.md)

### Phase 5 Documents
- [System Architecture](./SYSTEM_ARCHITECTURE.md)
- [Database Schema](./DATABASE_SCHEMA.md)
- [API Design](./API_DESIGN.md)
- [Dashboard Wireframes](./DASHBOARD_WIREFRAMES.md)

### Project Documents
- [Project Progress](../../PROJECT_PROGRESS.md)
- [Phase 4 Complete](../../PHASE4_COMPLETE.md)

---

## 🎉 Phase 5 Summary

### Achievements
✅ Designed end-to-end ML pipeline  
✅ Created database schema (6 tables)  
✅ Designed REST API (25+ endpoints)  
✅ Created dashboard wireframes (6 pages)  
✅ Documented deployment architecture  
✅ Planned monitoring strategy  

### Deliverables
- 📄 4 comprehensive design documents
- 🗄️ Complete database schema
- 🌐 Full API specification
- 📊 Dashboard wireframes
- 🏗️ System architecture diagram

### Ready For
🚀 **Phase 6: Application Development**
- Implement PostgreSQL database
- Build ML pipeline
- Develop REST API
- Create Streamlit dashboard
- Deploy system

---

**Phase 5 Status**: ✅ COMPLETE  
**Quality**: Excellent  
**Ready for Phase 6**: YES

---

**End of Document**
