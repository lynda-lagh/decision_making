# 📦 WeeFarm Predictive Maintenance - Deployment Package

## 🎯 Quick Start on New PC

This guide will help you deploy the complete WeeFarm system on any new computer in **under 10 minutes**.

---

## 📋 Prerequisites

### Required Software:
1. **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop)
   - Windows: Docker Desktop for Windows
   - Mac: Docker Desktop for Mac
   - Linux: Docker Engine + Docker Compose

2. **Git** (optional) - [Download](https://git-scm.com/downloads)
   - Only needed if cloning from repository

---

## 📁 Files You Need

### Essential Files (Copy these to new PC):

```
sousou/
├── backend/                    # FastAPI backend
├── dashboard/                  # Streamlit dashboard
├── src/                        # Data generation scripts
├── database/                   # Database scripts
├── pipeline/                   # ML pipeline
├── data/                       # Data folder (optional)
├── models/                     # ML models folder
├── Dockerfile.backend          # Backend Docker image
├── Dockerfile.dashboard        # Dashboard Docker image
├── docker-compose.yml          # Docker orchestration
├── requirements.txt            # Python dependencies
├── .dockerignore              # Docker ignore file
├── .env.docker                # Environment variables
└── README.md                  # This file
```

---

## 🚀 Deployment Steps

### Step 1: Copy Project Files

**Option A: Using USB/External Drive**
```bash
# Copy entire 'sousou' folder to new PC
# Place it anywhere (e.g., C:\Projects\sousou)
```

**Option B: Using Git**
```bash
git clone <your-repository-url>
cd sousou
```

**Option C: Using ZIP**
```bash
# Extract sousou.zip to desired location
# Navigate to extracted folder
```

---

### Step 2: Install Docker Desktop

1. Download Docker Desktop for your OS
2. Install and start Docker Desktop
3. Verify installation:
   ```bash
   docker --version
   docker-compose --version
   ```

---

### Step 3: Deploy with One Command

```bash
# Navigate to project folder
cd path/to/sousou

# Start everything (first time - will take 5-10 minutes)
docker-compose up -d --build
```

This single command will:
- ✅ Build all Docker images
- ✅ Start PostgreSQL database
- ✅ Start FastAPI backend
- ✅ Start Streamlit dashboard
- ✅ Create network connections

---

### Step 4: Initialize Data

```bash
# Generate synthetic data
docker-compose exec backend python src/data_generation/generate_all_data.py

# Create database tables
docker-compose exec backend python database/create_tables.py

# Load data into database
docker-compose exec backend python database/migrate_data.py

# Run ML pipeline
docker-compose exec backend python pipeline/pipeline.py
```

---

### Step 5: Access Applications

- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:5000/docs
- **Database**: localhost:5432

---

## 🎯 Quick Commands

### Start/Stop Services
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend
```

### Regenerate Data
```bash
# Generate new data
docker-compose exec backend python src/data_generation/generate_all_data.py

# Recreate tables
docker-compose exec backend python database/create_tables.py

# Migrate data
docker-compose exec backend python database/migrate_data.py

# Run pipeline
docker-compose exec backend python pipeline/pipeline.py
```

### Check Status
```bash
# View running containers
docker-compose ps

# Check backend logs
docker-compose logs backend

# Check database status
docker-compose exec backend python check_database.py
```

---

## 📊 What You Get

### Data Volume:
- **400 Equipment** units
- **9,093 Maintenance** records
- **2,634 Failure** events
- **400 Predictions** with risk scores
- **~300 Maintenance tasks** scheduled
- **20 KPIs** calculated

### Features:
- ✅ Real-time predictions
- ✅ Interactive dashboard (7 pages)
- ✅ REST API (30+ endpoints)
- ✅ Time series forecasting
- ✅ Advanced analytics
- ✅ Cost-benefit analysis
- ✅ Automated maintenance scheduling

---

## 🔧 Configuration

### Change Number of Equipment

Edit `src/data_generation/config.py`:
```python
NUM_EQUIPMENT = 400  # Change this number
```

### Change Database Password

Edit `docker-compose.yml`:
```yaml
environment:
  POSTGRES_PASSWORD: your_new_password
  DB_PASSWORD: your_new_password
```

### Change Ports

Edit `docker-compose.yml`:
```yaml
ports:
  - "8501:8501"  # Dashboard (change first number)
  - "5000:5000"  # API (change first number)
  - "5432:5432"  # Database (change first number)
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change ports in docker-compose.yml
ports:
  - "8502:8501"  # Use different port
```

### Docker Not Starting
```bash
# Restart Docker Desktop
# Then try again:
docker-compose up -d
```

### Database Connection Error
```bash
# Check database is running
docker-compose ps db

# Restart database
docker-compose restart db
```

### Out of Disk Space
```bash
# Clean up Docker
docker system prune -a --volumes
```

---

## 📦 Backup & Restore

### Backup Database
```bash
# Backup
docker-compose exec db pg_dump -U postgres weefarm_db > backup.sql

# Restore
docker-compose exec -T db psql -U postgres weefarm_db < backup.sql
```

### Backup Data Files
```bash
# Copy these folders:
- data/synthetic/
- models/
- results/
```

---

## 🌐 Production Deployment

### For Production Use:

1. **Change passwords** in `.env` file
2. **Enable HTTPS** with reverse proxy (nginx)
3. **Set up backups** (daily database dumps)
4. **Configure firewall** rules
5. **Enable monitoring** (logs, metrics)
6. **Use Docker secrets** for sensitive data

### Cloud Deployment:

**AWS**:
```bash
# Use ECS or EC2
docker-compose up -d
```

**Google Cloud**:
```bash
# Use Cloud Run
gcloud run deploy
```

**Azure**:
```bash
# Use Container Instances
az container create
```

**DigitalOcean**:
```bash
# Use App Platform
doctl apps create
```

---

## 📚 Documentation

- **API Documentation**: http://localhost:5000/docs
- **Dashboard Guide**: `DASHBOARD_FEATURES.md`
- **Docker Guide**: `DOCKER_GUIDE.md`
- **Pipeline Guide**: `PIPELINE_GUIDE.md`
- **API Endpoints**: `API_ENDPOINTS.md`

---

## 🆘 Support

### Common Issues:

1. **"Port already in use"**
   - Solution: Change port in docker-compose.yml

2. **"Cannot connect to Docker daemon"**
   - Solution: Start Docker Desktop

3. **"Database connection refused"**
   - Solution: Wait 30 seconds for database to start

4. **"No data in dashboard"**
   - Solution: Run data generation and pipeline scripts

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Docker containers running: `docker-compose ps`
- [ ] Dashboard accessible: http://localhost:8501
- [ ] API accessible: http://localhost:5000/docs
- [ ] Database has data: `docker-compose exec backend python check_database.py`
- [ ] Predictions generated: Check dashboard predictions page
- [ ] All 7 dashboard pages working

---

## 🎯 System Requirements

### Minimum:
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disk**: 10 GB free space
- **OS**: Windows 10/11, macOS 10.15+, Linux

### Recommended:
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Disk**: 20+ GB SSD
- **OS**: Latest version

---

## 📝 Version Info

- **Version**: 1.0.0
- **Last Updated**: November 2, 2025
- **Python**: 3.11
- **Docker**: 24.0+
- **PostgreSQL**: 15

---

## 🎉 Success!

If you can access the dashboard at http://localhost:8501 and see data, **congratulations!** Your deployment is successful! 🚀

---

**Questions?** Check the documentation files or run:
```bash
docker-compose logs -f
```
