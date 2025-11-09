# Quick Start Guide

This guide will help you quickly set up and run the Predictive Maintenance Management System for Agricultural Equipment.

## Prerequisites

- **Docker Desktop** (Windows/Mac/Linux) - [Download here](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download here](https://git-scm.com/downloads)
- At least 4GB of free RAM and 5GB of free disk space

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd sousou
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root with the following content:

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=0000
POSTGRES_DB=weefarm_db

# Backend API
API_HOST=0.0.0.0
API_PORT=5000

# Dashboard
DASHBOARD_PORT=8501
```

### 3. Start the Application

#### Option A: Using Docker Compose (Recommended)

```bash
# From the project root directory
docker-compose -f docker/docker-compose.yml up --build -d
```

### 4. Verify and Access the Running Services

After the build completes (this may take several minutes for the first time), verify all containers are running:

```bash
docker-compose -f docker/docker-compose.yml ps
```

You should see three services with status "Up":
- db (PostgreSQL)
- backend (FastAPI)
- dashboard (Streamlit)

### 5. Initialize the Database (First Run Only)

Run the database initialization script inside the backend container:

```bash
docker-compose -f docker/docker-compose.yml exec backend python database/create_tables.py
docker-compose -f docker/docker-compose.yml exec backend python database/create_missing_tables.py
docker-compose -f docker/docker-compose.yml exec backend python database/migrate_data.py
```

#### Option B: Manual Setup

1. **Set up Python Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Start the Database**:
   ```bash
   docker-compose -f docker/docker-compose.yml up -d db
   ```

3. **Initialize the Database**:
   ```bash
   python database/create_tables.py
   python database/create_missing_tables.py
   python database/migrate_data.py
   ```

4. **Start the Backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
   ```

5. **Start the Dashboard** (in a new terminal):
   ```bash
   streamlit run app_complete_dashboard.py
   ```

## Accessing the Application

- **Dashboard**: http://localhost:8501
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/docs
- **Database Adminer** (if enabled): http://localhost:8080
  - System: PostgreSQL
  - Server: db
  - Username: postgres
  - Password: 0000
  - Database: weefarm_db

## Project Structure

- `backend/` - FastAPI application
- `dashboard/` - Streamlit dashboard
- `database/` - Database scripts and migrations
- `data/` - Data files (raw, processed, synthetic)
- `models/` - Trained ML models
- `notebooks/` - Jupyter notebooks for analysis
- `src/` - Source code (data processing, ML models, etc.)
- `docker/` - Docker configuration files

## Common Commands

### Docker Commands

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Stop all services
docker-compose -f docker/docker-compose.yml down

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Rebuild and restart a specific service
docker-compose -f docker/docker-compose.yml up -d --build <service_name>
```

### Database Commands

```bash
# Run database migrations
python database/migrate_data.py

# Reset the database (warning: deletes all data)
python database/reset_database.py
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   - If you get port conflicts, check which process is using the port and stop it:
     ```bash
     # On Linux/Mac
     lsof -i :5000
     
     # On Windows
     netstat -ano | findstr :5000
     ```

2. **Docker Issues**
   - Make sure Docker Desktop is running
   - Try restarting Docker Desktop
   - Run `docker system prune -a -f --volumes` to clean up

3. **Database Connection Issues**
   - Make sure the database is running: `docker ps | grep db`
   - Check logs: `docker-compose -f docker/docker-compose.yml logs db`

## Support

For support, please open an issue in the GitHub repository or contact the development team.

## License

[Add your license information here]
