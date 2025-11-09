"""
Data Quality Utilities
Functions for data validation, quality scoring, and preprocessing
"""

import pandas as pd
import numpy as np
from scipy import stats
import sys
sys.path.append('..')
from sensor_config import SENSOR_SPECS, QUALITY_SCORE_CRITERIA, QUALITY_CLASSIFICATIONS

def validate_sensor_range(value, sensor_name):
    """
    Validate if sensor value is within acceptable range
    
    Args:
        value: Sensor reading value
        sensor_name: Name of the sensor
    
    Returns:
        bool: True if valid, False otherwise
    """
    if pd.isna(value):
        return False
    
    if sensor_name not in SENSOR_SPECS:
        return True
    
    spec = SENSOR_SPECS[sensor_name]
    return spec['min'] <= value <= spec['max']

def detect_outliers_iqr(series, multiplier=1.5):
    """
    Detect outliers using Interquartile Range (IQR) method
    
    Args:
        series: Pandas series of values
        multiplier: IQR multiplier (default 1.5)
    
    Returns:
        np.array: Boolean array indicating outliers
    """
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    
    return (series < lower_bound) | (series > upper_bound)

def detect_outliers_zscore(series, threshold=3):
    """
    Detect outliers using Z-score method
    
    Args:
        series: Pandas series of values
        threshold: Z-score threshold (default 3)
    
    Returns:
        np.array: Boolean array indicating outliers
    """
    z_scores = np.abs(stats.zscore(series.dropna()))
    return z_scores > threshold

def handle_missing_values(df, sensor_name, method='forward_fill', max_gap=3):
    """
    Handle missing values in sensor data
    
    Args:
        df: DataFrame with sensor data
        sensor_name: Name of the sensor column
        method: 'forward_fill' or 'interpolate'
        max_gap: Maximum gap in hours for interpolation
    
    Returns:
        pd.Series: Series with handled missing values
    """
    series = df[sensor_name].copy()
    
    if method == 'forward_fill':
        # Forward fill with limit
        series = series.fillna(method='ffill', limit=max_gap)
    elif method == 'interpolate':
        # Linear interpolation with limit
        series = series.interpolate(method='linear', limit=max_gap)
    
    return series

def calculate_quality_score(row, sensor_columns):
    """
    Calculate data quality score for a row (0-100)
    
    Args:
        row: DataFrame row
        sensor_columns: List of sensor column names
    
    Returns:
        float: Quality score (0-100)
    """
    score = 0
    
    # Check for missing values
    missing_count = row[sensor_columns].isna().sum()
    if missing_count == 0:
        score += QUALITY_SCORE_CRITERIA['no_missing_values']
    
    # Check for outliers (simplified - would need full context)
    score += QUALITY_SCORE_CRITERIA['no_outliers'] * (1 - min(missing_count / len(sensor_columns), 1))
    
    # Check for duplicates (would need to compare with previous row)
    score += QUALITY_SCORE_CRITERIA['no_duplicates']
    
    # Check for valid ranges
    valid_count = 0
    for col in sensor_columns:
        if pd.notna(row[col]) and validate_sensor_range(row[col], col):
            valid_count += 1
    
    if valid_count == len(sensor_columns):
        score += QUALITY_SCORE_CRITERIA['valid_ranges']
    
    # Check for anomalies (simplified)
    score += QUALITY_SCORE_CRITERIA['no_anomalies'] * 0.5
    
    return min(score, 100)

def classify_quality(score):
    """
    Classify data quality based on score
    
    Args:
        score: Quality score (0-100)
    
    Returns:
        str: Classification ('clean', 'suspicious', or 'invalid')
    """
    for classification, range_dict in QUALITY_CLASSIFICATIONS.items():
        if range_dict['min'] <= score <= range_dict['max']:
            return classification
    return 'invalid'

def remove_duplicates(df, time_window=60):
    """
    Remove duplicate readings within time window
    
    Args:
        df: DataFrame with sensor data
        time_window: Time window in seconds
    
    Returns:
        pd.DataFrame: DataFrame with duplicates removed
    """
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # Keep first occurrence
        df = df.drop_duplicates(subset=['equipment_id', 'timestamp'], keep='first')
    
    return df

def detect_sensor_drift(series, window=24, threshold=0.10):
    """
    Detect sensor drift (gradual shifts in values)
    
    Args:
        series: Pandas series of values
        window: Rolling window size (hours)
        threshold: Drift threshold (10% = 0.10)
    
    Returns:
        np.array: Boolean array indicating drift
    """
    rolling_mean = series.rolling(window=window, center=True).mean()
    baseline_mean = series.mean()
    
    drift = np.abs((rolling_mean - baseline_mean) / baseline_mean) > threshold
    return drift

def validate_dataframe(df, sensor_columns):
    """
    Comprehensive validation of sensor dataframe
    
    Args:
        df: DataFrame with sensor data
        sensor_columns: List of sensor column names
    
    Returns:
        dict: Validation report
    """
    report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df[sensor_columns].isna().sum().to_dict(),
        'missing_percentage': (df[sensor_columns].isna().sum() / len(df) * 100).to_dict(),
        'data_types': df[sensor_columns].dtypes.to_dict(),
        'numeric_columns': df[sensor_columns].select_dtypes(include=[np.number]).columns.tolist(),
        'non_numeric_columns': df[sensor_columns].select_dtypes(exclude=[np.number]).columns.tolist()
    }
    
    return report

print("[OK] Data quality utilities loaded")
