# 🚀 Complete Pipeline Guide: Database → Notebooks → Streamlit

## Overview

This guide explains how to run the complete analytics pipeline from database to Streamlit dashboard.

## Architecture

```
Database (SQLite/PostgreSQL)
    ↓
Data Extraction (CSV files)
    ↓
Jupyter Notebooks (7 Phases)
    ├── Phase 1: EDA
    ├── Phase 2: Feature Engineering
    ├── Phase 3: Feature Selection
    ├── Phase 4: Class Imbalance
    ├── Phase 5: Model Training
    ├── Phase 6: Time Series Forecasting
    └── Phase 7: Advanced Analytics
    ↓
Results & Visualizations
    ↓
Streamlit Dashboard
```

## 📋 Prerequisites

1. **Install required packages**:
```bash
pip install jupyter nbconvert pandas numpy matplotlib seaborn plotly streamlit scikit-learn imbalanced-learn statsmodels
```

2. **Ensure database is populated**:
```bash
python src/data_generation/generate_all_data.py
```

## 🎯 Running the Complete Pipeline

### Option 1: Full Automated Pipeline

Run everything from database to results:

```bash
python run_complete_pipeline.py
```

This will:
1. ✅ Load fresh data from database
2. ✅ Execute all 7 notebook phases
3. ✅ Generate results and visualizations
4. ✅ Create dashboard summary

### Option 2: Run Specific Phase

Run only one phase:

```bash
# Run Phase 7 (Advanced Analytics)
python run_complete_pipeline.py --phase 7

# Run Phase 5 (Model Training)
python run_complete_pipeline.py --phase 5
```

### Option 3: Refresh Data Only

Update data from database without running notebooks:

```bash
python run_complete_pipeline.py --refresh-data
```

### Option 4: Manual Notebook Execution

Run notebooks individually in Jupyter:

```bash
cd notebooks
jupyter notebook
```

Then execute in order:
1. `1_comprehensive_EDA.ipynb`
2. `02_feature_engineering.ipynb`
3. `03_feature_selection.ipynb`
4. `04_handle_class_imbalance.ipynb`
5. `05_model_training.ipynb`
6. `06_time_series_forecasting.ipynb`
7. `07_advanced_analytics.ipynb`

## 📊 Viewing Results in Streamlit

### Start the Dashboard

```bash
cd dashboard
streamlit run app.py
```

### Dashboard Features

The dashboard will show:

1. **Overview Page**
   - Real-time equipment status
   - Recent failures
   - Maintenance schedule

2. **Analytics Page** (Enhanced!)
   - 💼 Business KPIs
   - ⚙️ Operational Metrics
   - 🔍 Root Cause Analysis (Pareto charts)
   - 📊 Equipment Reliability (MTBF analysis)
   - 💰 Cost-Benefit Analysis
   - 🤖 Model Performance

3. **Predictions Page**
   - Failure predictions
   - Risk scores
   - Recommended actions

4. **Equipment Page**
   - Equipment details
   - Maintenance history
   - Failure history

## 📁 Output Files

After running the pipeline, you'll have:

### Results Folder (`results/`)
- `root_cause_analysis.csv` - Root cause breakdown
- `equipment_reliability_metrics.csv` - MTBF and reliability metrics
- `equipment_type_reliability.csv` - Type-level analysis
- `pipeline_summary.json` - Pipeline execution status

### Visualizations Folder (`visualizations/`)
- `root_cause_pareto.png` - Pareto chart
- `maintenance_type_analysis.png` - Maintenance breakdown
- `equipment_reliability_analysis.png` - Reliability charts
- `cost_analysis.png` - Cost breakdown
- Plus time series and other plots

### Data Folder (`data/synthetic/`)
- `equipment.csv` - Equipment master data
- `failure_events.csv` - Failure history
- `maintenance_records.csv` - Maintenance history

## 🔄 Updating the Dashboard

### When to Re-run Pipeline

Re-run the pipeline when:
- New data is added to the database
- You want updated analytics
- Models need retraining

### Quick Update (Data Only)

```bash
# Refresh data from database
python run_complete_pipeline.py --refresh-data

# Restart Streamlit
cd dashboard
streamlit run app.py
```

### Full Update (All Phases)

```bash
# Run complete pipeline
python run_complete_pipeline.py

# Restart Streamlit
cd dashboard
streamlit run app.py
```

## 🛠️ Customization

### Modify Analytics

Edit notebooks in `notebooks/` folder:
- Add new visualizations
- Change analysis parameters
- Add new metrics

### Modify Dashboard

Edit files in `dashboard/pages/`:
- `analytics.py` - Analytics page
- `overview.py` - Overview page
- `predictions.py` - Predictions page
- `equipment.py` - Equipment page

### Add New Data Sources

Modify `run_complete_pipeline.py`:
```python
def load_data_from_database(self):
    # Add your custom data loading here
    pass
```

## 📝 Logging

Pipeline logs are saved to `pipeline.log`:

```bash
# View logs
tail -f pipeline.log

# Or on Windows
Get-Content pipeline.log -Wait
```

## ⚠️ Troubleshooting

### Issue: Notebooks fail to execute

**Solution**: Run manually in Jupyter to see detailed errors

### Issue: Dashboard shows "No data available"

**Solution**: 
1. Check if results files exist in `results/` folder
2. Run pipeline: `python run_complete_pipeline.py`

### Issue: Database connection error

**Solution**:
1. Check database file exists
2. Verify database connection in `backend/app/database.py`

### Issue: Import errors in dashboard

**Solution**:
```bash
pip install -r requirements.txt
```

## 🎯 Best Practices

1. **Regular Updates**: Run pipeline weekly or when significant new data arrives
2. **Version Control**: Commit results and visualizations to track changes
3. **Backup**: Keep backups of database before major updates
4. **Testing**: Test pipeline on sample data first
5. **Monitoring**: Check `pipeline.log` for errors

## 📞 Support

For issues or questions:
1. Check `pipeline.log` for errors
2. Review notebook outputs in Jupyter
3. Verify data files exist in expected locations

## 🚀 Quick Start Checklist

- [ ] Database populated with data
- [ ] All dependencies installed
- [ ] Run `python run_complete_pipeline.py`
- [ ] Check `results/` folder for output files
- [ ] Start Streamlit: `cd dashboard && streamlit run app.py`
- [ ] Navigate to Analytics page
- [ ] View Root Cause, Reliability, and Cost Analysis tabs

---

**Last Updated**: November 2025
**Version**: 1.0
