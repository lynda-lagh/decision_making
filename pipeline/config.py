"""
WeeFarm ML Pipeline Configuration
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / 'models'
DATA_DIR = BASE_DIR / 'data'

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'weefarm_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '0000')
}

# Model paths
SVM_MODEL_PATH = MODELS_DIR / 'svm_model.pkl'
XGBOOST_MODEL_PATH = MODELS_DIR / 'xgboost_model.pkl'
FEATURE_SELECTOR_PATH = MODELS_DIR / 'feature_selector.pkl'

# Feature engineering settings
TOP_N_FEATURES = 10
FEATURE_COLUMNS = [
    'age_years', 'operating_hours', 'usage_intensity',
    'maintenance_count', 'preventive_count', 'corrective_count',
    'avg_maintenance_cost', 'total_maintenance_cost',
    'failure_count', 'avg_failure_cost', 'total_failure_cost',
    'days_since_last_service', 'avg_downtime_hours'
]

# Decision thresholds
RISK_THRESHOLDS = {
    'critical': 70,  # >70% risk
    'high': 40,      # 40-70% risk
    'medium': 20,    # 20-40% risk
    'low': 0         # <20% risk
}

# KPI targets
KPI_TARGETS = {
    'cost_reduction': 40.0,
    'roi': 200.0,
    'system_uptime': 99.5,
    'preventive_ratio': 50.0,
    'mtbf': 2000.0,
    'mttr': 8.0,
    'model_accuracy': 75.0,
    'model_recall': 80.0
}

# Pipeline settings
PIPELINE_NAME = 'WeeFarm Predictive Maintenance Pipeline'
PIPELINE_VERSION = '1.0'
LOG_LEVEL = 'INFO'

# Maintenance schedule settings
TECHNICIANS = [
    'Ahmed Ben Ali',
    'Mohamed Trabelsi',
    'Fatma Mansour',
    'Salah Gharbi',
    'Leila Hamdi'
]

ESTIMATED_COSTS = {
    'Critical': 500.0,
    'High': 350.0,
    'Medium': 250.0,
    'Low': 150.0
}

ESTIMATED_DURATION = {
    'Critical': 4.0,
    'High': 3.0,
    'Medium': 2.0,
    'Low': 1.5
}

print("[OK] Pipeline configuration loaded")
print(f"   Database: {DB_CONFIG['database']}")
print(f"   Models directory: {MODELS_DIR}")
