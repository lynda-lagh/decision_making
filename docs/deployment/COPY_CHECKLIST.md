# 📋 Copy Checklist - Deploy to New PC

## ✅ Essential Files to Copy

### 📁 Required Folders (MUST COPY):

```
☑ backend/                    # FastAPI backend code
☑ dashboard/                  # Streamlit dashboard
☑ src/                        # Data generation scripts
☑ database/                   # Database migration scripts
☑ pipeline/                   # ML pipeline (6 stages)
```

### 📄 Required Files (MUST COPY):

```
☑ docker-compose.yml          # Docker orchestration
☑ Dockerfile.backend          # Backend Docker image
☑ Dockerfile.dashboard        # Dashboard Docker image
☑ requirements.txt            # Python dependencies
☑ .dockerignore              # Docker ignore rules
☑ .env.docker                # Environment variables
☑ deploy.bat                 # Windows deployment script
☑ README_DEPLOYMENT.md       # Quick start guide
☑ DEPLOYMENT_PACKAGE.md      # Complete guide
```

### 📁 Optional Folders (Nice to have):

```
☐ models/                     # Pre-trained ML models (empty is OK)
☐ data/                       # Data files (will be regenerated)
☐ results/                    # Analysis results (will be regenerated)
☐ visualizations/            # Charts (will be regenerated)
☐ notebooks/                 # Jupyter notebooks (for reference)
```

### 📄 Optional Files (Documentation):

```
☐ DOCKER_GUIDE.md            # Docker deployment guide
☐ DASHBOARD_FEATURES.md      # Dashboard documentation
☐ API_ENDPOINTS.md           # API documentation
☐ PIPELINE_GUIDE.md          # Pipeline documentation
☐ README.md                  # Main README
```

---

## 📦 Packaging Options

### Option 1: ZIP File (Recommended)

**What to include**:
```
sousou.zip
├── backend/
├── dashboard/
├── src/
├── database/
├── pipeline/
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.dashboard
├── requirements.txt
├── .dockerignore
├── .env.docker
├── deploy.bat
└── README_DEPLOYMENT.md
```

**Size**: ~5-10 MB (without data/models)

**Create ZIP**:
```bash
# Windows
# Right-click folder → Send to → Compressed (zipped) folder

# Or use 7-Zip
7z a sousou.zip sousou/
```

---

### Option 2: Git Repository

**What to include**:
```bash
# Initialize git
git init

# Add files
git add backend/ dashboard/ src/ database/ pipeline/
git add docker-compose.yml Dockerfile.* requirements.txt
git add .dockerignore .env.docker deploy.bat
git add *.md

# Commit
git commit -m "Initial commit - WeeFarm Predictive Maintenance"

# Push to GitHub/GitLab
git remote add origin <your-repo-url>
git push -u origin main
```

**On new PC**:
```bash
git clone <your-repo-url>
cd sousou
deploy.bat
```

---

### Option 3: USB/External Drive

**Copy entire folder**:
```
1. Copy 'sousou' folder to USB drive
2. On new PC: Copy folder to desired location
3. Run: deploy.bat
```

---

## 🚫 What NOT to Copy

### Don't copy these (will be regenerated):

```
✗ __pycache__/               # Python cache
✗ *.pyc                      # Compiled Python
✗ .ipynb_checkpoints/        # Jupyter checkpoints
✗ node_modules/              # Node packages (if any)
✗ venv/                      # Virtual environment
✗ sousou/                    # Virtual environment
✗ .git/                      # Git history (optional)
✗ *.log                      # Log files
✗ .DS_Store                  # Mac files
✗ Thumbs.db                  # Windows files
```

### Don't copy these (sensitive):

```
✗ .env                       # Local environment (use .env.docker instead)
✗ *.key                      # Private keys
✗ *.pem                      # Certificates
✗ credentials.json           # API credentials
```

---

## 📏 Size Estimates

### Minimal Package (Essential only):
- **Size**: ~5 MB
- **Contents**: Code + Docker files
- **Time to copy**: < 1 minute

### Standard Package (With docs):
- **Size**: ~10 MB
- **Contents**: Code + Docker + Documentation
- **Time to copy**: < 2 minutes

### Complete Package (Everything):
- **Size**: ~50-100 MB
- **Contents**: Code + Docker + Data + Models + Notebooks
- **Time to copy**: 5-10 minutes

---

## ✅ Verification After Copy

On the new PC, verify you have:

```bash
# Check essential files exist
dir docker-compose.yml
dir Dockerfile.backend
dir Dockerfile.dashboard
dir requirements.txt
dir deploy.bat

# Check folders exist
dir backend
dir dashboard
dir src
dir database
dir pipeline
```

---

## 🚀 Deployment on New PC

### Step 1: Install Docker Desktop
Download from: https://www.docker.com/products/docker-desktop

### Step 2: Copy Files
Use one of the packaging options above

### Step 3: Deploy
```bash
cd path\to\sousou
deploy.bat
```

### Step 4: Verify
Open: http://localhost:8501

---

## 📝 Quick Reference

### Minimum Files Needed:
```
✅ backend/
✅ dashboard/
✅ src/
✅ database/
✅ pipeline/
✅ docker-compose.yml
✅ Dockerfile.backend
✅ Dockerfile.dashboard
✅ requirements.txt
✅ deploy.bat
```

**Total**: ~5 MB

### Time to Deploy on New PC:
- Docker installation: 5 minutes
- Copy files: 1-2 minutes
- Run deploy.bat: 5-10 minutes
- **Total**: ~15-20 minutes

---

## 🎯 Success Checklist

After deployment on new PC:

- [ ] Docker Desktop installed and running
- [ ] Files copied to new location
- [ ] `deploy.bat` executed successfully
- [ ] Dashboard accessible at http://localhost:8501
- [ ] API accessible at http://localhost:5000/docs
- [ ] Data visible in dashboard (400 equipment)
- [ ] All 7 dashboard pages working

---

## 💡 Tips

1. **Use ZIP for single transfer** - Easiest for one-time deployment
2. **Use Git for multiple PCs** - Best for team deployment
3. **Use USB for offline** - When no internet available
4. **Test on VM first** - Verify package completeness
5. **Document changes** - Note any customizations made

---

## 🆘 If Something's Missing

If deployment fails, check:

1. **All folders present?** - Verify backend/, dashboard/, src/, database/, pipeline/
2. **Docker files present?** - Check docker-compose.yml, Dockerfiles
3. **Requirements present?** - Verify requirements.txt
4. **Deploy script present?** - Check deploy.bat exists

---

## 📞 Support

If you encounter issues:

1. Check `DEPLOYMENT_PACKAGE.md` for detailed guide
2. Review `DOCKER_GUIDE.md` for Docker help
3. Run `docker-compose logs -f` to see errors
4. Verify all files from checklist are present

---

**Ready to copy?** Use this checklist to ensure nothing is missing! ✅
