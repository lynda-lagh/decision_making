# Enabling Firm Performance Through Data-Driven Decision-Making in Maintenance Management

## Project Overview

**Project Title**: Predictive Maintenance Management System for Agricultural Equipment

**Context**: This project is developed for WeeFarm, an AgriTech startup that provides digital solutions for farmers. The system will enable data-driven decision-making for agricultural equipment maintenance using time series prediction and machine learning.

**Objectives**:
- Reduce equipment downtime through predictive maintenance
- Optimize maintenance costs and scheduling
- Improve farm productivity by preventing unexpected failures
- Provide actionable insights through interactive dashboards

## Technology Stack

- **Backend**: Python (FastAPI)
- **Database**: PostgreSQL
- **ML/Analytics**: scikit-learn, TensorFlow, Prophet, pandas
- **Visualization**: Plotly, Dash
- **Frontend**: React.js with Tailwind CSS
- **Deployment**: Docker, AWS/Azure

## Project Structure

```
sousou/
├── docs/                          # Documentation
│   ├── phase1_research/          # Research & requirements
│   ├── phase2_data_strategy/     # Data planning
│   ├── phase3_data_prep/         # Data preparation docs
│   ├── phase4_design/            # System design
│   └── final_report/             # Final deliverables
├── data/                          # Data files
│   ├── raw/                      # Raw data
│   ├── processed/                # Cleaned data
│   └── synthetic/                # Generated data
├── notebooks/                     # Jupyter notebooks for analysis
├── src/                          # Source code
│   ├── data_generation/          # Data generation scripts
│   ├── preprocessing/            # Data cleaning
│   ├── models/                   # ML models
│   ├── api/                      # Backend API
│   └── dashboard/                # Frontend dashboard
├── tests/                        # Unit tests
├── models/                       # Saved trained models
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Getting Started

### 🚀 Quick Start (Choose Your Method)

```
┌─────────────────────────────────────────────────────────┐
│                   DEPLOYMENT OPTIONS                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  🐳 DOCKER (Recommended)          💻 LOCAL DEVELOPMENT  │
│  ├─ One-command deployment        ├─ Full control       │
│  ├─ All services included         ├─ Direct access      │
│  ├─ Production-ready               ├─ Easy debugging    │
│  └─ Easy management                └─ Custom setup      │
│                                                          │
│  ⚡ Start: start-docker-improved.bat                    │
│  📖 Guide: docker/START_HERE.md                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

#### Option 1: Docker Deployment (Recommended) 🐳

**Prerequisites:**
- Docker Desktop installed and running
- 8GB RAM minimum
- 10GB free disk space

**Steps:**
```bash
# 1. Navigate to docker directory
cd docker

# 2. Start all services
start-docker-improved.bat

# 3. Access applications
# Dashboard: http://localhost:8501
# API Docs:  http://localhost:5000/docs
```

**Services Deployed:**
- PostgreSQL Database (port 5432)
- FastAPI Backend (port 5000)
- Streamlit Dashboard (port 8501)

**Documentation:**
- Full Guide: `docker/START_HERE.md`
- Quick Reference: `docker/QUICK_REFERENCE.md`

---

#### Option 2: Local Development (Without Docker) 💻

**Prerequisites:**
- Python 3.11+
- PostgreSQL 15+
- Git

**Steps:**

1. **Clone & Setup Environment**
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

2. **Setup Database**
```bash
# Create PostgreSQL database
createdb weefarm_db

# Run migrations
python database/create_tables.py
```

3. **Configure Environment**
```bash
# Copy environment template
copy .env.example .env

# Edit .env with your database credentials
# DATABASE_URL=postgresql://postgres:password@localhost:5432/weefarm_db
```

4. **Run Backend API**
```bash
# Start FastAPI server
cd backend
python -m uvicorn app.main:app --reload --port 5000

# API available at: http://localhost:5000/docs
```

5. **Run Dashboard**
```bash
# In a new terminal, run the complete dashboard
streamlit run app_complete_dashboard.py

# Dashboard available at: http://localhost:8501
```

**Note:** The main dashboard file is `app_complete_dashboard.py` which includes all 7 pages.

6. **Run Pipeline (Optional)**
```bash
# Generate data and train models
python run_integrated_pipeline.py
```

---

### 📊 Accessing the Application

| Component | URL | Description |
|-----------|-----|-------------|
| **Dashboard** | http://localhost:8501 | 7-page interactive interface |
| **API Docs** | http://localhost:5000/docs | REST API documentation |
| **Database** | localhost:5432 | PostgreSQL (user: postgres) |

---

### 🔧 Common Commands

**Docker:**
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart dashboard
```

**Local Development:**
```bash
# Run Streamlit dashboard (7 pages)
streamlit run app_complete_dashboard.py

# Run backend API
cd backend
python -m uvicorn app.main:app --reload --port 5000

# Run pipeline
python run_integrated_pipeline.py

# Run tests
pytest

# Format code
black .

# Check code quality
flake8
```

---

### 📚 Additional Documentation

- 📖 [Quick Start Guide](QUICK_START.md) - Detailed setup
- 🐳 [Docker Guide](docker/START_HERE.md) - Docker deployment
- 🔧 [Setup Guide](SETUP_GUIDE.md) - Environment configuration
- 📊 [Project Progress](PROJECT_PROGRESS.md) - Development status

## Timeline

- **Phase 1**: Research & Requirements (Week 1)
- **Phase 2**: Data Strategy (Week 1-2)
- **Phase 3**: Data Collection & Preparation (Week 2-3)
- **Phase 4**: System Design (Week 3-4)
- **Phase 5**: Model Development (Week 4-6)
- **Phase 6**: Application Development (Week 6-8)
- **Phase 7**: Testing & Validation (Week 8-9)
- **Phase 8**: Deployment & Documentation (Week 9-10)
- **Phase 9**: Presentation & Handover (Week 10)

## Current Status

✅ **Phase 1-6: COMPLETE** - Research, Data, Design, Models, Application  
✅ **Docker Deployment: COMPLETE** (2025-11-09) - Production Ready  
⏳ **Phase 7-8: PLANNED** - Time Series & Advanced Features

**Overall Progress**: 75% (Application complete & deployed!)

### **What's Working:**
- ✅ PostgreSQL Database (100 equipment, 2,749 records)
- ✅ ML Pipeline (25+ models, ensemble methods)
- ✅ FastAPI Backend (35+ REST endpoints)
- ✅ Streamlit Dashboard (7 interactive pages)
- ✅ Docker Deployment (3 services, health checks)
- ✅ Predictions & Risk Analysis
- ✅ Maintenance Scheduling
- ✅ KPI Tracking (20+ metrics)
- ✅ Data Quality Monitoring
- ✅ Model Performance Tracking

### Quick Links
- 📖 [Quick Start Guide](QUICK_START.md) - Start here!
- 📊 [Project Progress](PROJECT_PROGRESS.md) - Track progress
- 🔧 [Setup Guide](SETUP_GUIDE.md) - Environment setup
- 📚 [Phase 1 Summary](docs/phase1_research/PHASE1_SUMMARY.md) - Research complete
- 🗄️ [Phase 2 Summary](docs/phase2_data_strategy/PHASE2_SUMMARY.md) - Schema complete
- 💾 [Database Schema](database/schema.sql) - SQL implementation

### Latest Achievements

**November 9, 2025 - Docker Deployment:**
- ✅ Complete Docker containerization (3 services)
- ✅ Health checks and auto-restart policies
- ✅ One-command deployment
- ✅ Comprehensive documentation (5 guides)
- ✅ Helper scripts for easy management

**November 2, 2025 - Application Complete:**
- ✅ Complete ML Pipeline (25+ models)
- ✅ FastAPI Backend with full CRUD operations
- ✅ 7-page Interactive Streamlit Dashboard
- ✅ Priority Distribution & Risk Analysis
- ✅ Real-time predictions and scheduling
- ✅ 44% cost reduction achieved!

### Next Steps
1. ✅ ~~Docker deployment~~ - COMPLETE!
2. Advanced time series forecasting (Phase 7-8)
3. Model interpretability (SHAP/LIME)
4. Performance optimization
5. Production monitoring & alerts

---

## 🆘 Troubleshooting

### Docker Issues

**Problem: Port already in use**
```bash
# Solution 1: Stop existing containers
docker-compose down

# Solution 2: Find and kill process
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

**Problem: Container won't start**
```bash
# Check logs
docker-compose logs <service_name>

# Restart service
docker-compose restart <service_name>

# Clean restart
docker-compose down
docker-compose up -d
```

**Problem: Database connection failed**
```bash
# Wait for database to initialize (30 seconds)
timeout /t 30

# Check database health
docker exec weefarm_db pg_isready -U postgres
```

### Local Development Issues

**Problem: Module not found**
```bash
# Ensure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem: Database connection error**
```bash
# Check PostgreSQL is running
# Verify credentials in .env file
# Ensure database exists: createdb weefarm_db
```

**Problem: Port 8501 already in use**
```bash
# Use different port
streamlit run app_complete_dashboard.py --server.port 8502
```

### Getting Help

- 📖 Check documentation in `docker/` folder
- 🔍 View logs: `docker-compose logs -f`
- 💬 Review error messages carefully
- 🐛 Check GitHub issues (if applicable)

---

## 📄 License

This project is developed for WeeFarm as part of an academic project.

## 👥 Contributors

- Project Team: Data Science & Engineering
- Supervisor: [Name]
- Organization: WeeFarm AgriTech

---

**Last Updated**: November 9, 2025  
**Version**: 1.0 (Production Ready)  
**Status**: ✅ Deployed and Operational
