# 🚀 WeeFarm Predictive Maintenance - Quick Deployment

## 📦 What's Included

This is a **complete, production-ready** predictive maintenance system with:

- ✅ **Machine Learning Pipeline** - Predicts equipment failures
- ✅ **REST API** - 30+ endpoints for data access
- ✅ **Interactive Dashboard** - 7 pages of analytics
- ✅ **Time Series Forecasting** - 30-day failure predictions
- ✅ **Advanced Analytics** - Cost-benefit analysis
- ✅ **Docker Deployment** - One-command setup

---

## ⚡ Quick Start (3 Steps)

### 1️⃣ Install Docker Desktop

Download and install: https://www.docker.com/products/docker-desktop

### 2️⃣ Run Deployment Script

**Windows**:
```cmd
deploy.bat
```

**Mac/Linux**:
```bash
chmod +x deploy.sh
./deploy.sh
```

### 3️⃣ Access Dashboard

Open browser: http://localhost:8501

**That's it!** 🎉

---

## 📊 What You'll Get

### Data:
- **400 Equipment** units
- **9,093 Maintenance** records  
- **2,634 Failure** events
- **400 Predictions** with risk scores

### Dashboard Pages:
1. **Overview** - System status
2. **Equipment** - 400 equipment details
3. **Predictions** - Risk scores & priorities
4. **Schedule** - Maintenance tasks
5. **Analytics** - Advanced analysis
6. **Forecasting** - 30-day predictions
7. **Settings** - Configuration

### API Endpoints:
- Equipment management
- Predictions & risk analysis
- Maintenance scheduling
- KPIs & analytics
- Time series forecasting

---

## 🎯 Manual Deployment

If you prefer manual steps:

```bash
# 1. Start containers
docker-compose up -d --build

# 2. Generate data
docker-compose exec backend python src/data_generation/generate_all_data.py

# 3. Create tables
docker-compose exec backend python database/create_tables.py

# 4. Load data
docker-compose exec backend python database/migrate_data.py

# 5. Run pipeline
docker-compose exec backend python pipeline/pipeline.py

# 6. Access dashboard
# Open: http://localhost:8501
```

---

## 🔧 Common Commands

### Start/Stop
```bash
docker-compose up -d      # Start
docker-compose down       # Stop
docker-compose restart    # Restart
```

### View Logs
```bash
docker-compose logs -f
```

### Check Status
```bash
docker-compose ps
```

### Regenerate Data
```bash
docker-compose exec backend python src/data_generation/generate_all_data.py
docker-compose exec backend python database/create_tables.py
docker-compose exec backend python database/migrate_data.py
docker-compose exec backend python pipeline/pipeline.py
```

---

## 📁 Project Structure

```
sousou/
├── backend/              # FastAPI REST API
├── dashboard/            # Streamlit web interface
├── src/                  # Data generation
├── database/             # Database scripts
├── pipeline/             # ML pipeline (6 stages)
├── models/               # Trained ML models
├── data/                 # Data files
├── docker-compose.yml    # Docker configuration
├── deploy.bat           # Windows deployment
└── deploy.sh            # Mac/Linux deployment
```

---

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:8501 | Interactive web interface |
| **API Docs** | http://localhost:5000/docs | Swagger API documentation |
| **API** | http://localhost:5000/api/v1 | REST API endpoints |
| **Database** | localhost:5432 | PostgreSQL database |

---

## 🔐 Default Credentials

### Database:
- **Host**: localhost
- **Port**: 5432
- **Database**: weefarm_db
- **User**: postgres
- **Password**: 0000

⚠️ **Change password for production!**

---

## 🐛 Troubleshooting

### Issue: Port already in use
**Solution**: Edit `docker-compose.yml` and change ports:
```yaml
ports:
  - "8502:8501"  # Dashboard
  - "5001:5000"  # API
```

### Issue: Docker not starting
**Solution**: 
1. Open Docker Desktop
2. Wait for it to start
3. Run `docker-compose up -d` again

### Issue: No data in dashboard
**Solution**: Run the data generation scripts:
```bash
docker-compose exec backend python src/data_generation/generate_all_data.py
docker-compose exec backend python database/migrate_data.py
docker-compose exec backend python pipeline/pipeline.py
```

---

## 📚 Documentation

- **Complete Guide**: `DEPLOYMENT_PACKAGE.md`
- **Docker Guide**: `DOCKER_GUIDE.md`
- **Dashboard Features**: `DASHBOARD_FEATURES.md`
- **API Endpoints**: `API_ENDPOINTS.md`
- **Pipeline Guide**: `PIPELINE_GUIDE.md`

---

## 🎯 System Requirements

### Minimum:
- Docker Desktop installed
- 4 GB RAM
- 10 GB disk space

### Recommended:
- 8 GB RAM
- 20 GB SSD
- 4+ CPU cores

---

## ✅ Verification

After deployment, check:

1. ✅ Dashboard loads: http://localhost:8501
2. ✅ API responds: http://localhost:5000/docs
3. ✅ Containers running: `docker-compose ps`
4. ✅ Data present: Check dashboard pages

---

## 🆘 Need Help?

1. Check logs: `docker-compose logs -f`
2. Review documentation files
3. Verify Docker is running
4. Ensure ports are available

---

## 🎉 Success Indicators

You'll know it's working when:
- ✅ Dashboard shows 400 equipment
- ✅ Predictions page has risk scores
- ✅ Schedule page has maintenance tasks
- ✅ Analytics page shows charts
- ✅ Forecasting page displays trends

---

## 📝 Version

- **Version**: 1.0.0
- **Date**: November 2, 2025
- **Python**: 3.11
- **Docker**: 24.0+

---

## 🚀 Ready to Deploy?

Just run:
```bash
deploy.bat
```

And you're done! 🎊

---

**Made with ❤️ for predictive maintenance**
