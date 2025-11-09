"""
Sensor Configuration and Specifications
Defines sensor ranges, normal operating conditions, and preprocessing parameters
"""

# Sensor specifications with ranges and normal operating conditions
SENSOR_SPECS = {
    'engine_temperature': {
        'min': 60, 'max': 120, 'unit': '°C',
        'normal_range': (80, 100),
        'critical_sensor': True,
        'description': 'Engine operating temperature'
    },
    'oil_pressure': {
        'min': 2, 'max': 6, 'unit': 'bar',
        'normal_range': (3, 5),
        'critical_sensor': True,
        'description': 'Oil system pressure'
    },
    'hydraulic_pressure': {
        'min': 100, 'max': 250, 'unit': 'bar',
        'normal_range': (150, 200),
        'critical_sensor': True,
        'description': 'Hydraulic system pressure'
    },
    'vibration_level': {
        'min': 0, 'max': 10, 'unit': 'mm/s',
        'normal_range': (0, 5),
        'critical_sensor': False,
        'description': 'Equipment vibration level'
    },
    'fuel_level': {
        'min': 0, 'max': 100, 'unit': '%',
        'normal_range': (20, 100),
        'critical_sensor': False,
        'description': 'Fuel tank level'
    },
    'battery_voltage': {
        'min': 12, 'max': 14.5, 'unit': 'V',
        'normal_range': (13, 14.2),
        'critical_sensor': False,
        'description': 'Battery voltage'
    },
    'rpm': {
        'min': 0, 'max': 3000, 'unit': 'rpm',
        'normal_range': (500, 2500),
        'critical_sensor': True,
        'description': 'Engine revolutions per minute'
    }
}

# Data imperfection rates (simulation parameters)
IMPERFECTION_RATES = {
    'missing_value_rate': 0.10,      # 10% missing values
    'outlier_rate': 0.03,             # 3% outliers
    'wrong_value_rate': 0.05,         # 5% wrong values
    'duplicate_rate': 0.01,           # 1% duplicates
    'sensor_drift_rate': 0.02         # 2% sensor drift
}

# Preprocessing parameters
PREPROCESSING_CONFIG = {
    'missing_value_threshold': 0.15,  # 15% max missing allowed
    'outlier_iqr_multiplier': 1.5,    # IQR multiplier for outlier detection
    'outlier_zscore_threshold': 3,    # Z-score threshold for outliers
    'duplicate_time_window': 60,      # seconds for duplicate detection
    'quality_score_threshold': 70,    # Minimum quality score (0-100)
    'interpolation_max_gap': 3,       # hours - max gap for interpolation
    'rolling_mean_window': 24,        # hours - rolling mean window
    'sensor_drift_threshold': 0.10    # 10% - threshold for drift detection
}

# Decision thresholds
DECISION_THRESHOLDS = {
    'critical': {
        'failure_prob': 0.80,
        'rul_days': 3
    },
    'high': {
        'failure_prob': 0.60,
        'rul_days': 7
    },
    'medium': {
        'failure_prob': 0.40,
        'rul_days': 30
    },
    'low': {
        'failure_prob': 0.20,
        'rul_days': 90
    }
}

# Risk scoring weights
RISK_SCORING_WEIGHTS = {
    'failure_probability': 0.5,
    'rul_criticality': 0.3,
    'anomaly_score': 0.2
}

# Model configuration
MODEL_CONFIG = {
    'failure_probability': {
        'algorithm': 'RandomForest',
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': 42
    },
    'rul_estimation': {
        'algorithm': 'XGBoost',
        'n_estimators': 100,
        'max_depth': 6,
        'learning_rate': 0.1,
        'random_state': 42
    },
    'anomaly_detection': {
        'algorithm': 'IsolationForest',
        'n_estimators': 100,
        'contamination': 0.05,
        'random_state': 42
    }
}

# Quality score criteria
QUALITY_SCORE_CRITERIA = {
    'no_missing_values': 20,
    'no_outliers': 20,
    'no_duplicates': 20,
    'valid_ranges': 20,
    'no_anomalies': 20
}

# Quality classifications
QUALITY_CLASSIFICATIONS = {
    'clean': {'min': 70, 'max': 100},
    'suspicious': {'min': 50, 'max': 69},
    'invalid': {'min': 0, 'max': 49}
}

# Equipment types (for context)
EQUIPMENT_TYPES = [
    'Excavator',
    'Bulldozer',
    'Loader',
    'Grader',
    'Compactor',
    'Drill',
    'Pump',
    'Generator'
]

print("[OK] Sensor configuration loaded")
print(f"   Sensors defined: {len(SENSOR_SPECS)}")
print(f"   Preprocessing parameters: {len(PREPROCESSING_CONFIG)}")
print(f"   Decision thresholds: {len(DECISION_THRESHOLDS)}")
