# 🚀 START HERE - Docker Deployment

**Welcome!** This is your starting point for deploying the WeeFarm Predictive Maintenance System with Docker.

---

## ⚡ Super Quick Start (Copy & Paste)

Open Command Prompt and run:

```bash
cd c:\Users\lynda\OneDrive\Bureau\sousou\docker
start-docker-improved.bat
```

Wait 5-10 minutes, then open:
- Dashboard: http://localhost:8501
- API Docs: http://localhost:5000/docs

**That's it!** 🎉

---

## 📚 Documentation Structure

Choose your path:

### 🎯 **I just want to get started NOW**
→ Run `start-docker-improved.bat` and follow the prompts

### 📖 **I want step-by-step instructions**
→ Read `DOCKER_DEPLOYMENT_GUIDE.md` (comprehensive guide)

### ⚡ **I need quick command reference**
→ See `QUICK_REFERENCE.md` (command cheat sheet)

### ✅ **I want to verify everything works**
→ Follow `DOCKER_CHECKLIST.md` (verification checklist)

### 🔧 **I want to understand the setup**
→ Read `README.md` (architecture and details)

---

## 🎬 First Time Setup (3 Minutes)

### Prerequisites
1. **Install Docker Desktop**
   - Download: https://www.docker.com/products/docker-desktop
   - Install and restart computer if needed
   
2. **Start Docker Desktop**
   - Open Docker Desktop application
   - Wait for whale icon in system tray
   - Should show "Docker Desktop is running"

### Deployment
1. **Open Command Prompt**
   - Press `Win + R`
   - Type `cmd` and press Enter

2. **Navigate to docker folder**
   ```bash
   cd c:\Users\lynda\OneDrive\Bureau\sousou\docker
   ```

3. **Run deployment script**
   ```bash
   start-docker-improved.bat
   ```

4. **Wait for completion**
   - First time: 5-10 minutes (downloads and builds)
   - Shows progress and status
   - Opens browser automatically (if you choose 'y')

5. **Verify it works**
   - Dashboard: http://localhost:8501 ✅
   - API Docs: http://localhost:5000/docs ✅

---

## 🎯 What You Get

After deployment, you'll have **4 running services**:

| Service | Port | What It Does |
|---------|------|--------------|
| **Dashboard** | 8501 | 7-page Streamlit web interface |
| **API** | 5000 | FastAPI REST API with docs |
| **Pipeline** | - | Autonomous data processing |
| **Database** | 5432 | PostgreSQL data storage |

---

## 🔧 Essential Commands

### Daily Use
```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Helper Scripts
Located in `docker/` folder:

- `start-docker-improved.bat` - **Main deployment script** ⭐
- `stop-docker.bat` - Stop all services
- `view-logs.bat` - Interactive log viewer
- `restart-service.bat` - Restart specific service
- `rebuild.bat` - Full rebuild

Just double-click any `.bat` file to run it!

---

## 🆘 Troubleshooting

### Problem: "Docker is not running"
**Solution**: Open Docker Desktop and wait for it to start

### Problem: "Port already in use"
**Solution**: 
```bash
docker-compose down
# Or change port in docker-compose.yml
```

### Problem: "Build failed"
**Solution**:
```bash
docker system prune -a
docker-compose build --no-cache
```

### Problem: "Container won't start"
**Solution**:
```bash
docker-compose logs <service_name>
# Check the error message
```

### Still stuck?
1. Check logs: `docker-compose logs -f`
2. Try clean restart: `docker-compose down && docker-compose up -d`
3. See `DOCKER_DEPLOYMENT_GUIDE.md` for detailed troubleshooting

---

## 📊 What to Do After Deployment

### Immediate (First 5 Minutes)
1. ✅ Open dashboard: http://localhost:8501
2. ✅ Navigate through all 7 pages
3. ✅ Check API docs: http://localhost:5000/docs
4. ✅ Verify no errors in logs: `docker-compose logs`

### Short Term (First Hour)
1. 📚 Read through dashboard pages
2. 🧪 Test API endpoints
3. 📊 Review model performance
4. 🔍 Check data quality metrics

### Long Term
1. 📅 Set up regular monitoring
2. 💾 Configure backups
3. 🔐 Review security settings
4. 📈 Optimize performance

---

## 🎓 Learning Path

### Beginner
1. Start with `start-docker-improved.bat`
2. Explore the dashboard
3. Learn basic commands from `QUICK_REFERENCE.md`

### Intermediate
1. Read `DOCKER_DEPLOYMENT_GUIDE.md`
2. Understand `docker-compose.yml`
3. Customize configuration
4. Use helper scripts

### Advanced
1. Modify Dockerfiles
2. Add custom services
3. Implement monitoring
4. Production deployment

---

## 📁 File Structure

```
docker/
├── START_HERE.md                    ← You are here!
├── README.md                        ← Architecture overview
├── QUICK_REFERENCE.md               ← Command cheat sheet
├── DOCKER_DEPLOYMENT_GUIDE.md       ← Full guide (in parent folder)
├── DOCKER_CHECKLIST.md              ← Verification checklist (in parent folder)
│
├── docker-compose.yml               ← Main configuration
├── Dockerfile.backend               ← Backend image
├── Dockerfile.dashboard             ← Dashboard image
├── .dockerignore                    ← Build exclusions
│
├── start-docker-improved.bat        ← Main deployment ⭐
├── stop-docker.bat                  ← Stop services
├── view-logs.bat                    ← Log viewer
├── restart-service.bat              ← Service restart
└── rebuild.bat                      ← Full rebuild
```

---

## 🎯 Quick Decision Tree

**Are you deploying for the first time?**
- YES → Run `start-docker-improved.bat`
- NO → Continue below

**Do you need to make changes?**
- YES → Edit code, then run `rebuild.bat`
- NO → Continue below

**Is something not working?**
- YES → Run `view-logs.bat` to see what's wrong
- NO → Continue below

**Do you want to restart a service?**
- YES → Run `restart-service.bat`
- NO → Continue below

**Do you want to stop everything?**
- YES → Run `stop-docker.bat`
- NO → You're all set! 🎉

---

## 💡 Pro Tips

1. **Bookmark URLs**: Save http://localhost:8501 and http://localhost:5000/docs
2. **Keep logs open**: Run `docker-compose logs -f` in a separate window
3. **Use helper scripts**: They're faster than typing commands
4. **Check status regularly**: `docker-compose ps` shows health
5. **Read the docs**: Each guide covers different aspects

---

## 🎉 Success Indicators

You know it's working when:

- ✅ `docker-compose ps` shows all 4 containers "Up"
- ✅ Dashboard loads at http://localhost:8501
- ✅ API docs load at http://localhost:5000/docs
- ✅ No errors in `docker-compose logs`
- ✅ You can navigate all dashboard pages
- ✅ Data is displaying correctly

---

## 📞 Next Steps

1. **Deploy Now**: Run `start-docker-improved.bat`
2. **Verify**: Follow `DOCKER_CHECKLIST.md`
3. **Learn**: Read `DOCKER_DEPLOYMENT_GUIDE.md`
4. **Explore**: Open http://localhost:8501

---

## 🚀 Ready to Start?

```bash
cd c:\Users\lynda\OneDrive\Bureau\sousou\docker
start-docker-improved.bat
```

**Good luck!** 🍀

---

**Questions?** Check the documentation files listed above or view logs with `docker-compose logs -f`
