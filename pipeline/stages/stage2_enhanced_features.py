"""
Stage 2: Enhanced Feature Engineering
Combines equipment history features with real-time sensor features
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
import psycopg2
import sys
sys.path.append('..')
from config import DB_CONFIG
from sensor_config import SENSOR_SPECS

SENSOR_COLUMNS = [
    'engine_temperature', 'oil_pressure', 'hydraulic_pressure',
    'vibration_level', 'fuel_level', 'battery_voltage', 'rpm'
]

def load_clean_sensor_data(hours_back=24):
    """
    Load clean sensor data from database for feature engineering
    
    Args:
        hours_back: Load data from last N hours
    
    Returns:
        pd.DataFrame: Clean sensor data
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        
        query = f"""
        SELECT 
            equipment_id, timestamp,
            engine_temperature, oil_pressure, hydraulic_pressure,
            vibration_level, fuel_level, battery_voltage, rpm,
            data_quality_score
        FROM sensor_readings_clean
        WHERE timestamp >= NOW() - INTERVAL '{hours_back} hours'
          AND processing_status = 'clean'
        ORDER BY equipment_id, timestamp DESC
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        print(f"[OK] Loaded {len(df)} clean sensor readings")
        return df
        
    except Exception as e:
        print(f"[ERROR] Failed to load sensor data: {e}")
        return pd.DataFrame()

def calculate_sensor_statistics(sensor_df):
    """
    Calculate statistical features from sensor data
    
    Args:
        sensor_df: DataFrame with sensor readings
    
    Returns:
        pd.DataFrame: Sensor statistics per equipment
    """
    sensor_features = []
    
    for equipment_id in sensor_df['equipment_id'].unique():
        eq_data = sensor_df[sensor_df['equipment_id'] == equipment_id]
        
        features = {'equipment_id': equipment_id}
        
        # Calculate statistics for each sensor
        for sensor in SENSOR_COLUMNS:
            if sensor in eq_data.columns:
                values = eq_data[sensor].dropna()
                
                if len(values) > 0:
                    # Mean, std, min, max
                    features[f'{sensor}_mean'] = values.mean()
                    features[f'{sensor}_std'] = values.std()
                    features[f'{sensor}_min'] = values.min()
                    features[f'{sensor}_max'] = values.max()
                    
                    # Range
                    features[f'{sensor}_range'] = values.max() - values.min()
                    
                    # Latest value
                    features[f'{sensor}_latest'] = eq_data[sensor].iloc[0]
                    
                    # Count of readings
                    features[f'{sensor}_reading_count'] = len(values)
                else:
                    features[f'{sensor}_mean'] = 0
                    features[f'{sensor}_std'] = 0
                    features[f'{sensor}_min'] = 0
                    features[f'{sensor}_max'] = 0
                    features[f'{sensor}_range'] = 0
                    features[f'{sensor}_latest'] = 0
                    features[f'{sensor}_reading_count'] = 0
        
        # Average data quality
        features['avg_data_quality_score'] = eq_data['data_quality_score'].mean()
        
        sensor_features.append(features)
    
    return pd.DataFrame(sensor_features)

def calculate_sensor_trends(sensor_df):
    """
    Calculate trend features from sensor data
    
    Args:
        sensor_df: DataFrame with sensor readings
    
    Returns:
        pd.DataFrame: Sensor trends per equipment
    """
    trend_features = []
    
    for equipment_id in sensor_df['equipment_id'].unique():
        eq_data = sensor_df[sensor_df['equipment_id'] == equipment_id].sort_values('timestamp')
        
        features = {'equipment_id': equipment_id}
        
        # Calculate rate of change for each sensor
        for sensor in SENSOR_COLUMNS:
            if sensor in eq_data.columns and len(eq_data) > 1:
                values = eq_data[sensor].dropna()
                
                if len(values) > 1:
                    # Rate of change (delta)
                    delta = values.iloc[-1] - values.iloc[0]
                    features[f'{sensor}_delta'] = delta
                    
                    # Trend direction (positive/negative)
                    features[f'{sensor}_trend'] = 1 if delta > 0 else (-1 if delta < 0 else 0)
                    
                    # Volatility (coefficient of variation)
                    if values.mean() != 0:
                        features[f'{sensor}_volatility'] = values.std() / abs(values.mean())
                    else:
                        features[f'{sensor}_volatility'] = 0
                else:
                    features[f'{sensor}_delta'] = 0
                    features[f'{sensor}_trend'] = 0
                    features[f'{sensor}_volatility'] = 0
            else:
                features[f'{sensor}_delta'] = 0
                features[f'{sensor}_trend'] = 0
                features[f'{sensor}_volatility'] = 0
        
        trend_features.append(features)
    
    return pd.DataFrame(trend_features)

def calculate_anomaly_features(sensor_df):
    """
    Calculate anomaly-related features
    
    Args:
        sensor_df: DataFrame with sensor readings
    
    Returns:
        pd.DataFrame: Anomaly features per equipment
    """
    anomaly_features = []
    
    for equipment_id in sensor_df['equipment_id'].unique():
        eq_data = sensor_df[sensor_df['equipment_id'] == equipment_id]
        
        features = {'equipment_id': equipment_id}
        
        # Count anomalies
        features['anomaly_count_24h'] = eq_data['anomaly_detected'].sum()
        features['anomaly_rate'] = eq_data['anomaly_detected'].mean()
        
        # Count out-of-range readings
        out_of_range_count = 0
        for sensor in SENSOR_COLUMNS:
            if sensor in eq_data.columns:
                spec = SENSOR_SPECS[sensor]
                out_of_range = ((eq_data[sensor] < spec['min']) | 
                               (eq_data[sensor] > spec['max'])).sum()
                out_of_range_count += out_of_range
        
        features['out_of_range_count'] = out_of_range_count
        features['out_of_range_rate'] = out_of_range_count / (len(eq_data) * len(SENSOR_COLUMNS))
        
        anomaly_features.append(features)
    
    return pd.DataFrame(anomaly_features)

def calculate_equipment_features(equipment_df):
    """Calculate base equipment features (existing logic)"""
    features = equipment_df[['equipment_id', 'equipment_type', 'location']].copy()
    
    # Convert dates
    if 'purchase_date' in equipment_df.columns:
        equipment_df['purchase_date'] = pd.to_datetime(equipment_df['purchase_date'])
    if 'last_service_date' in equipment_df.columns:
        equipment_df['last_service_date'] = pd.to_datetime(equipment_df['last_service_date'])
    
    # Calculate age
    current_date = pd.Timestamp.now()
    if 'purchase_date' in equipment_df.columns:
        features['equipment_age_days'] = (current_date - equipment_df['purchase_date']).dt.days
        features['equipment_age_years'] = features['equipment_age_days'] / 365.25
    else:
        features['equipment_age_days'] = 0
        features['equipment_age_years'] = 0
    
    # Operating hours
    if 'operating_hours' in equipment_df.columns:
        features['operating_hours'] = equipment_df['operating_hours']
        features['usage_intensity'] = features['operating_hours'] / (features['equipment_age_years'] + 1)
    else:
        features['operating_hours'] = 0
        features['usage_intensity'] = 0
    
    # Days since last service
    if 'last_service_date' in equipment_df.columns:
        features['days_since_last_maintenance'] = (current_date - equipment_df['last_service_date']).dt.days
    else:
        features['days_since_last_maintenance'] = 999
    
    return features

def aggregate_maintenance_features(maintenance_df):
    """Aggregate maintenance history features (existing logic)"""
    
    total_counts = maintenance_df.groupby('equipment_id').size().to_frame('maintenance_count')
    
    preventive = maintenance_df[maintenance_df['type_id'] == 1].groupby('equipment_id').size().to_frame('preventive_count')
    corrective = maintenance_df[maintenance_df['type_id'] == 2].groupby('equipment_id').size().to_frame('corrective_count')
    
    cost_agg = maintenance_df.groupby('equipment_id')['total_cost'].agg([
        ('avg_maintenance_cost', 'mean'),
        ('total_maintenance_cost', 'sum'),
        ('max_maintenance_cost', 'max')
    ])
    
    downtime_agg = maintenance_df.groupby('equipment_id')['downtime_hours'].agg([
        ('avg_downtime_hours', 'mean'),
        ('total_downtime_hours', 'sum')
    ])
    
    maintenance_features = total_counts.merge(
        preventive, on='equipment_id', how='outer'
    ).merge(
        corrective, on='equipment_id', how='outer'
    ).merge(
        cost_agg, on='equipment_id', how='outer'
    ).merge(
        downtime_agg, on='equipment_id', how='outer'
    ).reset_index()
    
    maintenance_features = maintenance_features.fillna(0)
    
    return maintenance_features

def aggregate_failure_features(failure_df):
    """Aggregate failure history features (existing logic)"""
    
    failure_counts = failure_df.groupby('equipment_id').size().to_frame('failure_count')
    
    cost_agg = failure_df.groupby('equipment_id')['repair_cost'].agg([
        ('avg_failure_cost', 'mean'),
        ('total_failure_cost', 'sum'),
        ('max_failure_cost', 'max')
    ])
    
    downtime_agg = failure_df.groupby('equipment_id')['downtime_hours'].agg([
        ('avg_failure_downtime', 'mean'),
        ('total_failure_downtime', 'sum')
    ])
    
    severity_counts = failure_df.groupby(['equipment_id', 'severity']).size().unstack(fill_value=0)
    severity_counts.columns = [f'severity_{col.lower()}_count' for col in severity_counts.columns]
    
    if len(failure_df) > 0:
        mtbf = failure_df.groupby('equipment_id').apply(
            lambda x: (x['failure_date'].max() - x['failure_date'].min()).days / (len(x) - 1) if len(x) > 1 else 0
        )
        if not isinstance(mtbf, pd.DataFrame):
            mtbf = mtbf.to_frame('mtbf_days')
    else:
        mtbf = pd.DataFrame(columns=['mtbf_days'])
    
    failure_features = failure_counts.merge(
        cost_agg, on='equipment_id', how='outer'
    ).merge(
        downtime_agg, on='equipment_id', how='outer'
    ).merge(
        severity_counts, on='equipment_id', how='outer'
    ).merge(
        mtbf, on='equipment_id', how='outer'
    ).reset_index()
    
    failure_features = failure_features.fillna(0)
    
    return failure_features

def create_derived_features(df):
    """Create derived features from base features (existing logic)"""
    
    if 'total_maintenance_cost' in df.columns and 'maintenance_count' in df.columns:
        df['avg_maintenance_cost'] = df['total_maintenance_cost'] / (df['maintenance_count'] + 1)
        df['maintenance_cost_per_day'] = df['total_maintenance_cost'] / (df['equipment_age_days'] + 1)
    
    if 'failure_count' in df.columns and 'equipment_age_days' in df.columns:
        df['failure_rate_per_year'] = (df['failure_count'] / (df['equipment_age_days'] + 1)) * 365
        df['has_failures'] = (df['failure_count'] > 0).astype(int)
    
    if 'mtbf_days' in df.columns:
        df['is_reliable'] = (df['mtbf_days'] > 180).astype(int)
        df['reliability_score'] = np.clip(df['mtbf_days'] / 365, 0, 1) * 100
    
    if 'total_maintenance_cost' in df.columns and 'total_failure_cost' in df.columns:
        df['maintenance_to_failure_ratio'] = df['total_maintenance_cost'] / (df['total_failure_cost'] + 1)
        df['total_cost'] = df['total_maintenance_cost'] + df['total_failure_cost']
    
    if 'equipment_age_days' in df.columns:
        df['age_years'] = df['equipment_age_days'] / 365.25
        df['is_old'] = (df['age_years'] > 3).astype(int)
        df['is_very_old'] = (df['age_years'] > 5).astype(int)
    
    if 'total_downtime_hours' in df.columns and 'failure_count' in df.columns:
        df['avg_downtime_per_failure'] = df['total_downtime_hours'] / (df['failure_count'] + 1)
        df['downtime_per_year'] = (df['total_downtime_hours'] / (df['equipment_age_days'] + 1)) * 365
    
    if 'days_since_last_maintenance' in df.columns:
        df['needs_maintenance'] = (df['days_since_last_maintenance'] > 90).astype(int)
        df['overdue_maintenance'] = (df['days_since_last_maintenance'] > 180).astype(int)
    
    if 'failure_count' in df.columns and 'total_failure_cost' in df.columns:
        df['is_critical'] = ((df['failure_count'] > df['failure_count'].median()) & 
                            (df['total_failure_cost'] > df['total_failure_cost'].median())).astype(int)
    
    return df

def run_stage2(data):
    """Execute Stage 2: Enhanced Feature Engineering"""
    print("\n" + "="*60)
    print("STAGE 2: ENHANCED FEATURE ENGINEERING")
    print("="*60)
    
    equipment_df = data['equipment']
    maintenance_df = data['maintenance']
    failures_df = data['failures']
    
    # Equipment features
    print("\n[STEP 1] Calculating equipment features...")
    features = calculate_equipment_features(equipment_df)
    
    # Maintenance features
    print("[STEP 2] Aggregating maintenance features...")
    maintenance_features = aggregate_maintenance_features(maintenance_df)
    features = features.merge(maintenance_features, on='equipment_id', how='left')
    
    # Failure features
    print("[STEP 3] Aggregating failure features...")
    failure_features = aggregate_failure_features(failures_df)
    features = features.merge(failure_features, on='equipment_id', how='left')
    
    # Sensor features
    print("[STEP 4] Loading clean sensor data...")
    sensor_df = load_clean_sensor_data(hours_back=24)
    
    if not sensor_df.empty:
        print("[STEP 5] Calculating sensor statistics...")
        sensor_stats = calculate_sensor_statistics(sensor_df)
        features = features.merge(sensor_stats, on='equipment_id', how='left')
        
        print("[STEP 6] Calculating sensor trends...")
        sensor_trends = calculate_sensor_trends(sensor_df)
        features = features.merge(sensor_trends, on='equipment_id', how='left')
        
        print("[STEP 7] Calculating anomaly features...")
        anomaly_features = calculate_anomaly_features(sensor_df)
        features = features.merge(anomaly_features, on='equipment_id', how='left')
    else:
        print("[WARN] No sensor data available, skipping sensor features")
    
    # Derived features
    print("[STEP 8] Creating derived features...")
    features = create_derived_features(features)
    
    # Fill NaN values
    features = features.fillna(0)
    
    # Summary
    feature_cols = [col for col in features.columns if col not in ['equipment_id', 'equipment_type', 'location']]
    
    print(f"\n[COMPLETE] Stage 2 Complete!")
    print(f"   Total features calculated: {len(feature_cols)}")
    print(f"   Equipment with features: {len(features)}")
    print(f"   Feature categories:")
    print(f"     - Equipment: age, usage, maintenance")
    print(f"     - Sensor: statistics, trends, anomalies")
    print(f"     - Derived: ratios, risk indicators")
    
    return {
        'features': features,
        'feature_columns': feature_cols,
        'equipment_count': len(features)
    }

if __name__ == "__main__":
    from stage1_data_ingestion import run_stage1
    data = run_stage1()
    result = run_stage2(data)
    print(f"\nFeatures shape: {result['features'].shape}")
    print(f"Feature columns: {result['feature_columns'][:10]}")
