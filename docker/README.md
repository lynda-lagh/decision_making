# 🐳 Docker Deployment

Complete Docker setup for WeeFarm Predictive Maintenance System.

## 🚀 Quick Start (3 Steps)

### 1. Ensure Docker Desktop is Running
- Open Docker Desktop application
- Wait for it to fully start (whale icon in system tray)

### 2. Run Deployment Script
```bash
cd docker
start-docker-improved.bat
```

### 3. Access Applications
- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:5000/docs

That's it! 🎉

---

## 📁 Files in This Directory

| File | Description |
|------|-------------|
| `docker-compose.yml` | Main orchestration file (4 services) |
| `Dockerfile.backend` | Backend API + Pipeline image |
| `Dockerfile.dashboard` | Streamlit dashboard image |
| `.dockerignore` | Files to exclude from build |
| `start-docker-improved.bat` | **Main deployment script** ⭐ |
| `stop-docker.bat` | Stop all services |
| `view-logs.bat` | Interactive log viewer |
| `restart-service.bat` | Interactive service restart |
| `rebuild.bat` | Full rebuild script |
| `QUICK_REFERENCE.md` | Command cheat sheet |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              User Browser                        │
└────────────┬──────────────────┬─────────────────┘
             │                  │
     Port 8501│          Port 5000│
             │                  │
   ┌─────────▼────────┐  ┌─────▼──────────┐
   │   Dashboard      │  │   Backend API   │
   │  (Streamlit)     │◄─┤   (FastAPI)     │
   └─────────┬────────┘  └─────┬──────────┘
             │                  │
             │          ┌───────▼──────────┐
             │          │  Pipeline Service │
             │          │  (Autonomous)     │
             │          └───────┬──────────┘
             │                  │
             │          Port 5432│
             │                  │
         ┌───▼──────────────────▼───┐
         │   PostgreSQL Database     │
         │      (weefarm_db)         │
         └───────────────────────────┘
```

---

## 📦 Services

### 1. PostgreSQL Database (`weefarm_db`)
- **Port**: 5432
- **User**: postgres
- **Password**: 0000
- **Database**: weefarm_db
- **Volume**: Persistent storage

### 2. Backend API (`weefarm_backend`)
- **Port**: 5000
- **Framework**: FastAPI
- **Features**: REST API, auto-docs
- **Health Check**: `/health`

### 3. Pipeline Service (`weefarm_pipeline`)
- **No exposed port**
- **Purpose**: Autonomous data processing
- **Runs**: `run_integrated_pipeline.py`

### 4. Dashboard (`weefarm_dashboard`)
- **Port**: 8501
- **Framework**: Streamlit
- **Features**: 7-page interactive dashboard
- **File**: `app_complete_dashboard.py`

---

## 🔧 Common Commands

### Start/Stop
```bash
# Start all
docker-compose up -d

# Stop all
docker-compose down

# Restart specific service
docker-compose restart dashboard
```

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f dashboard
```

### Status
```bash
# Check running containers
docker-compose ps

# Resource usage
docker stats
```

### Rebuild
```bash
# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 📚 Documentation

- **Full Guide**: `../DOCKER_DEPLOYMENT_GUIDE.md`
- **Quick Reference**: `QUICK_REFERENCE.md`
- **Main README**: `../README.md`

---

## 🆘 Troubleshooting

### Issue: Port already in use
```bash
# Check what's using port 8501
netstat -ano | findstr :8501

# Stop the service or change port in docker-compose.yml
```

### Issue: Container won't start
```bash
# View detailed logs
docker-compose logs <service_name>

# Example
docker-compose logs dashboard
```

### Issue: Database connection failed
```bash
# Check database is ready
docker exec weefarm_db pg_isready -U postgres

# Wait a bit longer (database takes ~30 seconds to initialize)
```

### Issue: Build fails
```bash
# Clean rebuild
docker-compose down
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

---

## ✅ Verification

After deployment, verify:

- [ ] Docker Desktop is running
- [ ] All 4 containers are up: `docker-compose ps`
- [ ] Dashboard accessible: http://localhost:8501
- [ ] API docs accessible: http://localhost:5000/docs
- [ ] No errors in logs: `docker-compose logs`

---

## 🔐 Security Notes

### For Production:

1. **Change default password** in `docker-compose.yml`:
```yaml
POSTGRES_PASSWORD: your_secure_password
```

2. **Don't expose database port**:
```yaml
# Comment out in production
# ports:
#   - "5432:5432"
```

3. **Use environment files**:
```bash
# Create .env file
POSTGRES_PASSWORD=secure_password

# Reference in docker-compose.yml
environment:
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

---

## 💡 Tips

- **First run**: Takes 5-10 minutes to build images
- **Subsequent runs**: Takes ~30 seconds to start
- **Logs**: Always check logs if something doesn't work
- **Rebuild**: Required after code changes
- **Persistence**: Database data survives container restarts

---

## 📞 Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify Docker is running: `docker info`
3. Try clean restart: `docker-compose down && docker-compose up -d`
4. See `QUICK_REFERENCE.md` for more commands

---

**🎯 Ready to deploy? Run `start-docker-improved.bat`**
