# 📚 Documentation Index

Welcome to the WeeFarm Predictive Maintenance documentation!

---

## 🎯 Start Here

**New to the project?** Read this first:
- **[START_HERE.md](START_HERE.md)** - Quick overview and getting started guide

---

## 📁 Documentation Structure

### 🚀 Deployment Documentation
**Location**: `deployment/`

Essential guides for deploying the system:

| File | Description |
|------|-------------|
| **[README_DEPLOYMENT.md](deployment/README_DEPLOYMENT.md)** | Quick start deployment guide (3 steps) |
| **[DEPLOYMENT_PACKAGE.md](deployment/DEPLOYMENT_PACKAGE.md)** | Complete deployment guide with all details |
| **[COPY_CHECKLIST.md](deployment/COPY_CHECKLIST.md)** | Checklist of files to copy to new PC |
| **[DOCKER_GUIDE.md](deployment/DOCKER_GUIDE.md)** | Docker deployment and management guide |

**Use these when**: Setting up the system on a new computer

---

### 📖 User Guides
**Location**: `guides/`

Guides for using the system:

| File | Description |
|------|-------------|
| **[DASHBOARD_FEATURES.md](guides/DASHBOARD_FEATURES.md)** | Complete dashboard features and pages |
| **[PIPELINE_GUIDE.md](guides/PIPELINE_GUIDE.md)** | ML pipeline stages and workflow |

**Use these when**: Learning how to use the dashboard or understand the pipeline

---

### 🔌 API Documentation
**Location**: `api/`

API reference and endpoints:

| File | Description |
|------|-------------|
| **[API_ENDPOINTS.md](api/API_ENDPOINTS.md)** | Complete API endpoint reference |

**Use these when**: Integrating with the API or building custom applications

---

### 🏗️ Architecture Documentation
**Location**: `architecture/`

System architecture and design:

| File | Description |
|------|-------------|
| *(To be added)* | System architecture diagrams |
| *(To be added)* | Database schema |
| *(To be added)* | Component interactions |

**Use these when**: Understanding system design or planning modifications

---

## 🗺️ Quick Navigation

### I want to...

#### 🚀 Deploy the system
1. Read: [START_HERE.md](START_HERE.md)
2. Follow: [README_DEPLOYMENT.md](deployment/README_DEPLOYMENT.md)
3. Run: `deploy.bat` in root folder

#### 📦 Copy to another PC
1. Read: [COPY_CHECKLIST.md](deployment/COPY_CHECKLIST.md)
2. Copy essential files
3. Run: `deploy.bat` on new PC

#### 🐳 Learn Docker deployment
1. Read: [DOCKER_GUIDE.md](deployment/DOCKER_GUIDE.md)
2. Understand Docker commands
3. Customize docker-compose.yml

#### 📊 Use the dashboard
1. Read: [DASHBOARD_FEATURES.md](guides/DASHBOARD_FEATURES.md)
2. Explore 7 dashboard pages
3. View analytics and predictions

#### 🔮 Understand the ML pipeline
1. Read: [PIPELINE_GUIDE.md](guides/PIPELINE_GUIDE.md)
2. Learn about 6 pipeline stages
3. Understand feature engineering

#### 🔌 Use the API
1. Read: [API_ENDPOINTS.md](api/API_ENDPOINTS.md)
2. Visit: http://localhost:5000/docs
3. Test endpoints with Swagger UI

---

## 📝 Documentation by Role

### For System Administrators
- [DEPLOYMENT_PACKAGE.md](deployment/DEPLOYMENT_PACKAGE.md) - Complete deployment
- [DOCKER_GUIDE.md](deployment/DOCKER_GUIDE.md) - Docker management
- [COPY_CHECKLIST.md](deployment/COPY_CHECKLIST.md) - Deployment checklist

### For End Users
- [START_HERE.md](START_HERE.md) - Getting started
- [DASHBOARD_FEATURES.md](guides/DASHBOARD_FEATURES.md) - Using the dashboard
- [README_DEPLOYMENT.md](deployment/README_DEPLOYMENT.md) - Quick start

### For Developers
- [API_ENDPOINTS.md](api/API_ENDPOINTS.md) - API reference
- [PIPELINE_GUIDE.md](guides/PIPELINE_GUIDE.md) - Pipeline architecture
- [DOCKER_GUIDE.md](deployment/DOCKER_GUIDE.md) - Development setup

### For Data Scientists
- [PIPELINE_GUIDE.md](guides/PIPELINE_GUIDE.md) - ML pipeline details
- [DASHBOARD_FEATURES.md](guides/DASHBOARD_FEATURES.md) - Analytics features

---

## 🔍 Finding Information

### Search by Topic

**Deployment**:
- Quick start → [README_DEPLOYMENT.md](deployment/README_DEPLOYMENT.md)
- Complete guide → [DEPLOYMENT_PACKAGE.md](deployment/DEPLOYMENT_PACKAGE.md)
- Docker setup → [DOCKER_GUIDE.md](deployment/DOCKER_GUIDE.md)

**Features**:
- Dashboard → [DASHBOARD_FEATURES.md](guides/DASHBOARD_FEATURES.md)
- API → [API_ENDPOINTS.md](api/API_ENDPOINTS.md)
- Pipeline → [PIPELINE_GUIDE.md](guides/PIPELINE_GUIDE.md)

**Troubleshooting**:
- Deployment issues → [DEPLOYMENT_PACKAGE.md](deployment/DEPLOYMENT_PACKAGE.md#troubleshooting)
- Docker issues → [DOCKER_GUIDE.md](deployment/DOCKER_GUIDE.md#troubleshooting)
- General help → [START_HERE.md](START_HERE.md#troubleshooting)

---

## 📊 Documentation Statistics

- **Total Documents**: 8 files
- **Deployment Guides**: 4 files
- **User Guides**: 2 files
- **API Documentation**: 1 file
- **Architecture Docs**: 0 files (coming soon)

---

## 🆕 Recent Updates

**November 2, 2025**:
- ✅ Organized documentation into folders
- ✅ Created deployment guides
- ✅ Added API documentation
- ✅ Created user guides

---

## 💡 Tips

1. **Start with START_HERE.md** - It links to everything else
2. **Bookmark frequently used docs** - Save time navigating
3. **Check troubleshooting sections** - Most issues are documented
4. **Use Ctrl+F to search** - Find information quickly

---

## 🆘 Need Help?

1. **Check START_HERE.md** - Quick answers
2. **Search this index** - Find relevant documentation
3. **Read troubleshooting sections** - Common issues solved
4. **Check logs**: `docker-compose logs -f`

---

## 📞 Support Resources

- **Documentation**: You're here! 📚
- **API Docs**: http://localhost:5000/docs
- **Dashboard**: http://localhost:8501
- **Logs**: `docker-compose logs -f`

---

**Last Updated**: November 2, 2025  
**Version**: 1.0.0  
**Status**: ✅ Complete
