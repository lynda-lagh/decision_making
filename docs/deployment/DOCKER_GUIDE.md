# 🐳 Docker Deployment Guide - WeeFarm Predictive Maintenance

## 📋 Overview

This guide shows you how to deploy the entire WeeFarm application using Docker containers.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           Docker Compose Stack              │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐  ┌──────────────┐        │
│  │  Dashboard   │  │   Backend    │        │
│  │  (Streamlit) │◄─┤   (FastAPI)  │        │
│  │  Port: 8501  │  │  Port: 5000  │        │
│  └──────────────┘  └──────┬───────┘        │
│                           │                 │
│                    ┌──────▼───────┐         │
│                    │  PostgreSQL  │         │
│                    │  Port: 5432  │         │
│                    └──────────────┘         │
│                                             │
└─────────────────────────────────────────────┘
```

## 📦 What's Included

### 4 Docker Services:

1. **`db`** - PostgreSQL 15 database
2. **`backend`** - FastAPI REST API
3. **`dashboard`** - Streamlit web interface
4. **`pipeline`** - ML pipeline runner (optional)

## 🚀 Quick Start

### Prerequisites

Install Docker Desktop:
- **Windows**: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Mac**: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: Install Docker Engine and Docker Compose

### Step 1: Build and Start

```bash
# Navigate to project directory
cd c:\Users\lynda\OneDrive\Bureau\sousou

# Build and start all services
docker-compose up -d --build
```

This will:
- ✅ Build Docker images
- ✅ Start PostgreSQL database
- ✅ Start FastAPI backend
- ✅ Start Streamlit dashboard
- ✅ Create network connections

### Step 2: Verify Services

```bash
# Check running containers
docker-compose ps

# Expected output:
# NAME                 STATUS    PORTS
# weefarm_db           Up        0.0.0.0:5432->5432/tcp
# weefarm_backend      Up        0.0.0.0:5000->5000/tcp
# weefarm_dashboard    Up        0.0.0.0:8501->8501/tcp
```

### Step 3: Access Applications

- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:5000/docs
- **API Health**: http://localhost:5000/health
- **Database**: localhost:5432

## 📊 Initial Data Setup

### Option 1: Load Data via API

```bash
# Generate synthetic data
docker-compose exec backend python src/data_generation/generate_all_data.py

# Migrate to database
docker-compose exec backend python database/migrate_data.py
```

### Option 2: Run Pipeline

```bash
# Run complete pipeline
docker-compose run --rm pipeline python pipeline/pipeline.py
```

### Option 3: Use Existing Data

If you already have data in CSV files:

```bash
# Copy data to container
docker cp data/synthetic/. weefarm_backend:/app/data/synthetic/

# Migrate to database
docker-compose exec backend python database/migrate_data.py
```

## 🛠️ Common Commands

### Start Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f dashboard
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes database data)
docker-compose down -v
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 dashboard
```

### Execute Commands in Containers

```bash
# Access backend shell
docker-compose exec backend bash

# Access database
docker-compose exec db psql -U postgres -d weefarm_db

# Run Python script
docker-compose exec backend python check_database.py

# Run pipeline
docker-compose exec backend python pipeline/pipeline.py
```

## 🔄 Update and Rebuild

### After Code Changes

```bash
# Rebuild specific service
docker-compose up -d --build backend

# Rebuild all services
docker-compose up -d --build
```

### Update Dependencies

```bash
# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📁 Volume Management

### Persistent Data

The following data persists across container restarts:

- **Database**: `postgres_data` volume
- **Models**: `./models` directory
- **Data**: `./data` directory
- **Results**: `./results` directory

### Backup Database

```bash
# Backup
docker-compose exec db pg_dump -U postgres weefarm_db > backup.sql

# Restore
docker-compose exec -T db psql -U postgres weefarm_db < backup.sql
```

## 🌐 Production Deployment

### Environment Variables

Create `.env` file:

```bash
# Copy template
cp .env.docker .env

# Edit with production values
nano .env
```

### Security Checklist

- [ ] Change default database password
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up backup strategy
- [ ] Enable logging and monitoring

### Production docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: .
    restart: always
    environment:
      DATABASE_URL_FILE: /run/secrets/database_url
    secrets:
      - database_url

secrets:
  db_password:
    file: ./secrets/db_password.txt
  database_url:
    file: ./secrets/database_url.txt
```

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Restart service
docker-compose restart backend
```

### Database Connection Issues

```bash
# Check database is running
docker-compose ps db

# Test connection
docker-compose exec backend python -c "from backend.app.database import engine; print(engine)"

# Check database logs
docker-compose logs db
```

### Port Already in Use

```bash
# Find process using port
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000

# Change port in docker-compose.yml
ports:
  - "5001:5000"  # Use different host port
```

### Out of Disk Space

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything
docker system prune -a --volumes
```

## 📊 Monitoring

### Health Checks

```bash
# API health
curl http://localhost:5000/health

# Database health
docker-compose exec db pg_isready -U postgres

# Dashboard health
curl http://localhost:8501
```

### Resource Usage

```bash
# View container stats
docker stats

# View specific container
docker stats weefarm_backend
```

## 🔧 Advanced Configuration

### Custom Network

```yaml
networks:
  weefarm_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.25.0.0/16
```

### Resource Limits

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Scaling Services

```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3

# With load balancer
docker-compose up -d --scale backend=3 nginx
```

## 📝 Scheduled Tasks

### Run Pipeline Daily

Create cron job:

```bash
# Edit crontab
crontab -e

# Add line (runs at 2 AM daily)
0 2 * * * cd /path/to/sousou && docker-compose run --rm pipeline
```

### Using Docker Compose

```yaml
pipeline:
  build: .
  command: >
    sh -c "while true; do
      python pipeline/pipeline.py;
      sleep 86400;
    done"
```

## 🚀 Deployment Platforms

### Deploy to Cloud

#### **AWS ECS**
```bash
# Install ECS CLI
ecs-cli compose up

# Or use AWS Copilot
copilot init
```

#### **Google Cloud Run**
```bash
gcloud run deploy weefarm-backend --source .
```

#### **Azure Container Instances**
```bash
az container create --resource-group myResourceGroup \
  --file docker-compose.yml
```

#### **DigitalOcean App Platform**
```bash
# Use docker-compose.yml directly
doctl apps create --spec docker-compose.yml
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Streamlit Deployment](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)

## ✅ Checklist

Before deploying to production:

- [ ] All services start successfully
- [ ] Database migrations complete
- [ ] API endpoints respond correctly
- [ ] Dashboard loads without errors
- [ ] Pipeline runs successfully
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] Security hardened
- [ ] Documentation updated
- [ ] Team trained

---

**Last Updated**: November 2, 2025  
**Version**: 1.0  
**Status**: ✅ Production Ready
