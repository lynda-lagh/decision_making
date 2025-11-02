# 🎯 START HERE - WeeFarm Predictive Maintenance

## 👋 Welcome!

This is a **complete, production-ready** predictive maintenance system. Everything you need is included!

---

## ⚡ Quick Start (Choose One)

### 🖥️ Option 1: Deploy on THIS Computer

```bash
# Just run this:
deploy.bat
```

Then open: http://localhost:8501

---

### 📦 Option 2: Deploy on ANOTHER Computer

**Step 1**: Copy these files to new PC:
- See `COPY_CHECKLIST.md` for complete list
- Minimum: backend/, dashboard/, src/, database/, pipeline/, docker-compose.yml, Dockerfiles, requirements.txt, deploy.bat

**Step 2**: On new PC, install Docker Desktop:
- Download: https://www.docker.com/products/docker-desktop

**Step 3**: Run deployment:
```bash
deploy.bat
```

**Step 4**: Access dashboard:
- Open: http://localhost:8501

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **README_DEPLOYMENT.md** | Quick start guide (READ THIS FIRST!) |
| **DEPLOYMENT_PACKAGE.md** | Complete deployment guide |
| **COPY_CHECKLIST.md** | What to copy to new PC |
| **DOCKER_GUIDE.md** | Docker deployment details |
| **DASHBOARD_FEATURES.md** | Dashboard features & pages |
| **API_ENDPOINTS.md** | API documentation |
| **PIPELINE_GUIDE.md** | ML pipeline guide |

---

## 🎯 What's Included

### 📊 Current Data:
- ✅ **400 Equipment** units
- ✅ **9,093 Maintenance** records
- ✅ **2,634 Failure** events
- ✅ **400 Predictions** with risk scores
- ✅ **~300 Maintenance tasks** scheduled
- ✅ **20 KPIs** calculated

### 🌐 Services:
- ✅ **Dashboard** (Streamlit) - http://localhost:8501
- ✅ **API** (FastAPI) - http://localhost:5000
- ✅ **Database** (PostgreSQL) - localhost:5432

### 📱 Dashboard Pages:
1. **Overview** - System status & alerts
2. **Equipment** - 400 equipment details
3. **Predictions** - Risk scores & priorities
4. **Schedule** - Maintenance tasks
5. **Analytics** - Cost-benefit analysis
6. **Forecasting** - 30-day predictions
7. **Settings** - Configuration

---

## 🚀 Common Tasks

### Start System
```bash
docker-compose up -d
```

### Stop System
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f
```

### Regenerate Data
```bash
docker-compose exec backend python src/data_generation/generate_all_data.py
docker-compose exec backend python database/create_tables.py
docker-compose exec backend python database/migrate_data.py
docker-compose exec backend python pipeline/pipeline.py
```

### Check Status
```bash
docker-compose ps
```

---

## 🎓 Learning Path

### New to the Project?
1. Read: `README_DEPLOYMENT.md`
2. Run: `deploy.bat`
3. Explore: http://localhost:8501
4. Check API: http://localhost:5000/docs

### Want to Deploy Elsewhere?
1. Read: `COPY_CHECKLIST.md`
2. Copy files to new PC
3. Run: `deploy.bat` on new PC

### Want to Customize?
1. Read: `DEPLOYMENT_PACKAGE.md`
2. Edit: `src/data_generation/config.py` (change data volume)
3. Edit: `docker-compose.yml` (change ports/settings)

### Want to Understand the Code?
1. Read: `PIPELINE_GUIDE.md` (ML pipeline)
2. Read: `API_ENDPOINTS.md` (API structure)
3. Read: `DASHBOARD_FEATURES.md` (Dashboard features)

---

## ✅ Verification

System is working if:
- ✅ Dashboard loads at http://localhost:8501
- ✅ Shows 400 equipment
- ✅ Predictions page has data
- ✅ Charts are visible
- ✅ API docs load at http://localhost:5000/docs

---

## 🐛 Troubleshooting

### Issue: "Port already in use"
**Fix**: Edit `docker-compose.yml`, change port numbers

### Issue: "Docker not running"
**Fix**: Start Docker Desktop application

### Issue: "No data in dashboard"
**Fix**: Run data generation scripts (see "Regenerate Data" above)

### Issue: "Container won't start"
**Fix**: Check logs with `docker-compose logs -f`

---

## 📞 Need Help?

1. **Check logs**: `docker-compose logs -f`
2. **Read docs**: See documentation list above
3. **Verify Docker**: Ensure Docker Desktop is running
4. **Check ports**: Make sure 5000, 5432, 8501 are available

---

## 🎯 Next Steps

### For Development:
- Explore notebooks in `notebooks/` folder
- Modify pipeline in `pipeline/stages/`
- Customize dashboard in `dashboard/pages/`

### For Production:
- Change database password in `docker-compose.yml`
- Set up HTTPS with reverse proxy
- Configure backups
- Enable monitoring

### For Deployment:
- Follow `DEPLOYMENT_PACKAGE.md`
- Use `COPY_CHECKLIST.md` for file list
- Run `deploy.bat` on target machine

---

## 🎉 Success!

If you can see the dashboard with data, **you're all set!** 

Enjoy your predictive maintenance system! 🚀

---

## 📝 Quick Reference

| What | Where | How |
|------|-------|-----|
| **Start** | Any PC | `deploy.bat` |
| **Dashboard** | Browser | http://localhost:8501 |
| **API** | Browser | http://localhost:5000/docs |
| **Logs** | Terminal | `docker-compose logs -f` |
| **Stop** | Terminal | `docker-compose down` |
| **Help** | Docs | Read `README_DEPLOYMENT.md` |

---

**Version**: 1.0.0  
**Last Updated**: November 2, 2025  
**Status**: ✅ Production Ready

---

**🚀 Ready? Run `deploy.bat` and let's go!**
