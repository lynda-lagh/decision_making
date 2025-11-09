# 🚀 Docker Quick Reference

## 🎯 One-Command Start
```bash
cd docker
start-docker-improved.bat
```

## 📋 Essential Commands

### Start/Stop
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

### View Status
```bash
# Check running containers
docker-compose ps

# View resource usage
docker stats

# Check logs
docker-compose logs -f
```

### Restart Services
```bash
# Restart specific service
docker-compose restart dashboard
docker-compose restart backend

# Restart all
docker-compose restart
```

### Rebuild After Changes
```bash
# Quick rebuild (one service)
docker-compose build dashboard
docker-compose up -d dashboard

# Full rebuild (all services)
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🌐 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| Dashboard | http://localhost:8501 | Streamlit UI (7 pages) |
| API Docs | http://localhost:5000/docs | FastAPI Interactive Docs |
| Alternative API Docs | http://localhost:5000/redoc | ReDoc Documentation |
| Database | localhost:5432 | PostgreSQL (user: postgres, pass: 0000) |

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Find what's using the port
netstat -ano | findstr :8501
netstat -ano | findstr :5000

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

### Container Won't Start
```bash
# View detailed logs
docker-compose logs <service_name>

# Example
docker-compose logs dashboard
docker-compose logs backend
```

### Database Connection Issues
```bash
# Check database is ready
docker exec weefarm_db pg_isready -U postgres

# Connect to database
docker exec -it weefarm_db psql -U postgres -d weefarm_db

# View tables
\dt
```

### Clean Restart
```bash
# Nuclear option - fresh start
docker-compose down -v
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

## 📊 Monitoring

### View Logs
```bash
# All services (real-time)
docker-compose logs -f

# Specific service
docker-compose logs -f dashboard
docker-compose logs -f backend
docker-compose logs -f pipeline
docker-compose logs -f db

# Last 100 lines
docker-compose logs --tail=100 dashboard
```

### Container Shell Access
```bash
# Access dashboard container
docker exec -it weefarm_dashboard bash

# Access backend container
docker exec -it weefarm_backend bash

# Access database container
docker exec -it weefarm_db bash
```

### Database Queries
```bash
# Connect to PostgreSQL
docker exec -it weefarm_db psql -U postgres -d weefarm_db

# Common queries
SELECT COUNT(*) FROM sensor_data;
SELECT * FROM equipment LIMIT 10;
SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 10;
```

## 🛠️ Helper Scripts

Located in `docker/` directory:

| Script | Purpose |
|--------|---------|
| `start-docker-improved.bat` | Full deployment with checks |
| `stop-docker.bat` | Stop all services |
| `view-logs.bat` | Interactive log viewer |
| `restart-service.bat` | Interactive service restart |
| `rebuild.bat` | Full rebuild and restart |

## 🔐 Environment Variables

Edit `docker-compose.yml` to change:

```yaml
environment:
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: 0000  # ⚠️ Change in production!
  POSTGRES_DB: weefarm_db
  DATABASE_URL: postgresql://postgres:0000@db:5432/weefarm_db
```

## 📈 Performance Tips

### Speed Up Builds
```bash
# Use build cache
docker-compose build

# Skip cache for clean build
docker-compose build --no-cache
```

### Reduce Image Size
- Already using `python:3.11-slim`
- Cleanup in Dockerfile with `rm -rf /var/lib/apt/lists/*`
- Multi-stage builds (advanced)

### Resource Limits
Add to `docker-compose.yml`:
```yaml
services:
  dashboard:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

## 🎯 Common Workflows

### Development Workflow
```bash
# 1. Make code changes
# 2. Rebuild specific service
docker-compose build dashboard
docker-compose up -d dashboard

# 3. View logs
docker-compose logs -f dashboard
```

### Production Deployment
```bash
# 1. Update code
git pull

# 2. Full rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 3. Verify
docker-compose ps
docker-compose logs -f
```

### Backup Database
```bash
# Create backup
docker exec weefarm_db pg_dump -U postgres weefarm_db > backup.sql

# Restore backup
docker exec -i weefarm_db psql -U postgres weefarm_db < backup.sql
```

## ⚡ Quick Checks

```bash
# Is Docker running?
docker info

# Are containers running?
docker-compose ps

# Any errors in logs?
docker-compose logs --tail=50

# Resource usage
docker stats --no-stream

# Disk usage
docker system df
```

## 🆘 Emergency Commands

```bash
# Stop everything immediately
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all images
docker rmi $(docker images -q)

# Clean everything
docker system prune -a --volumes
```

---

**💡 Tip**: Bookmark this page for quick reference!
