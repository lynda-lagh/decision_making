"""
Stage 2: Feature Engineering
Calculate features for each equipment based on historical data
"""

import pandas as pd
import numpy as np
from datetime import datetime, date

def calculate_age(equipment_df):
    """Calculate equipment age in years"""
    current_date = date.today()
    equipment_df['age_years'] = equipment_df['purchase_date'].apply(
        lambda x: (current_date - x).days / 365.25 if pd.notna(x) else 0
    )
    return equipment_df

def calculate_usage_intensity(equipment_df):
    """Calculate usage intensity (hours per year)"""
    equipment_df['usage_intensity'] = equipment_df.apply(
        lambda row: row['operating_hours'] / row['age_years'] if row['age_years'] > 0 else 0,
        axis=1
    )
    return equipment_df

def calculate_days_since_service(equipment_df):
    """Calculate days since last service"""
    current_date = date.today()
    equipment_df['days_since_last_service'] = equipment_df['last_service_date'].apply(
        lambda x: (current_date - x).days if pd.notna(x) else 999
    )
    return equipment_df

def calculate_equipment_features(equipment_df):
    """Calculate base equipment features"""
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
    """Aggregate maintenance history features"""
    
    # Count by type
    maintenance_counts = maintenance_df.groupby(['equipment_id', 'type_id']).size().unstack(fill_value=0)
    maintenance_counts.columns = [f'type_{col}_count' for col in maintenance_counts.columns]
    
    # Total maintenance count
    total_counts = maintenance_df.groupby('equipment_id').size().to_frame('maintenance_count')
    
    # Preventive (type 1) and Corrective (type 2) counts
    preventive = maintenance_df[maintenance_df['type_id'] == 1].groupby('equipment_id').size().to_frame('preventive_count')
    corrective = maintenance_df[maintenance_df['type_id'] == 2].groupby('equipment_id').size().to_frame('corrective_count')
    
    # Cost aggregations
    cost_agg = maintenance_df.groupby('equipment_id')['total_cost'].agg([
        ('avg_maintenance_cost', 'mean'),
        ('total_maintenance_cost', 'sum'),
        ('max_maintenance_cost', 'max')
    ])
    
    # Downtime aggregations
    downtime_agg = maintenance_df.groupby('equipment_id')['downtime_hours'].agg([
        ('avg_downtime_hours', 'mean'),
        ('total_downtime_hours', 'sum')
    ])
    
    # Merge all maintenance features
    maintenance_features = total_counts.merge(
        preventive, on='equipment_id', how='outer'
    ).merge(
        corrective, on='equipment_id', how='outer'
    ).merge(
        cost_agg, on='equipment_id', how='outer'
    ).merge(
        downtime_agg, on='equipment_id', how='outer'
    ).reset_index()
    
    # Fill NaN with 0
    maintenance_features = maintenance_features.fillna(0)
    
    return maintenance_features

def create_derived_features(df):
    """Create derived features from base features (matching notebook approach)"""
    
    # Maintenance efficiency metrics
    if 'total_maintenance_cost' in df.columns and 'maintenance_count' in df.columns:
        df['avg_maintenance_cost'] = df['total_maintenance_cost'] / (df['maintenance_count'] + 1)
        df['maintenance_cost_per_day'] = df['total_maintenance_cost'] / (df['equipment_age_days'] + 1)
    
    # Failure rate metrics
    if 'failure_count' in df.columns and 'equipment_age_days' in df.columns:
        df['failure_rate_per_year'] = (df['failure_count'] / (df['equipment_age_days'] + 1)) * 365
        df['has_failures'] = (df['failure_count'] > 0).astype(int)
    
    # MTBF reliability indicator
    if 'mtbf_days' in df.columns:
        df['is_reliable'] = (df['mtbf_days'] > 180).astype(int)  # >6 months MTBF = reliable
        df['reliability_score'] = np.clip(df['mtbf_days'] / 365, 0, 1) * 100  # 0-100 score
    
    # Maintenance vs Failure cost ratio
    if 'total_maintenance_cost' in df.columns and 'total_failure_cost' in df.columns:
        df['maintenance_to_failure_ratio'] = df['total_maintenance_cost'] / (df['total_failure_cost'] + 1)
        df['total_cost'] = df['total_maintenance_cost'] + df['total_failure_cost']
    
    # Age-based risk indicators
    if 'equipment_age_days' in df.columns:
        df['age_years'] = df['equipment_age_days'] / 365.25
        df['is_old'] = (df['age_years'] > 3).astype(int)
        df['is_very_old'] = (df['age_years'] > 5).astype(int)
    
    # Downtime metrics
    if 'total_downtime_hours' in df.columns and 'failure_count' in df.columns:
        df['avg_downtime_per_failure'] = df['total_downtime_hours'] / (df['failure_count'] + 1)
        df['downtime_per_year'] = (df['total_downtime_hours'] / (df['equipment_age_days'] + 1)) * 365
    
    # Maintenance frequency indicators
    if 'days_since_last_maintenance' in df.columns:
        df['needs_maintenance'] = (df['days_since_last_maintenance'] > 90).astype(int)
        df['overdue_maintenance'] = (df['days_since_last_maintenance'] > 180).astype(int)
    
    # Critical equipment indicator (high failures + high cost)
    if 'failure_count' in df.columns and 'total_failure_cost' in df.columns:
        df['is_critical'] = ((df['failure_count'] > df['failure_count'].median()) & 
                            (df['total_failure_cost'] > df['total_failure_cost'].median())).astype(int)
    
    return df

def aggregate_failure_features(failure_df):
    """Aggregate failure history features"""
    
    # Failure counts
    failure_counts = failure_df.groupby('equipment_id').size().to_frame('failure_count')
    
    # Cost aggregations
    cost_agg = failure_df.groupby('equipment_id')['repair_cost'].agg([
        ('avg_failure_cost', 'mean'),
        ('total_failure_cost', 'sum'),
        ('max_failure_cost', 'max')
    ])
    
    # Downtime aggregations
    downtime_agg = failure_df.groupby('equipment_id')['downtime_hours'].agg([
        ('avg_failure_downtime', 'mean'),
        ('total_failure_downtime', 'sum')
    ])
    
    # Severity counts
    severity_counts = failure_df.groupby(['equipment_id', 'severity']).size().unstack(fill_value=0)
    severity_counts.columns = [f'severity_{col.lower()}_count' for col in severity_counts.columns]
    
    # Calculate MTBF (Mean Time Between Failures)
    if len(failure_df) > 0:
        mtbf = failure_df.groupby('equipment_id').apply(
            lambda x: (x['failure_date'].max() - x['failure_date'].min()).days / (len(x) - 1) if len(x) > 1 else 0
        )
        if not isinstance(mtbf, pd.DataFrame):
            mtbf = mtbf.to_frame('mtbf_days')
    else:
        mtbf = pd.DataFrame(columns=['mtbf_days'])
    
    # Merge all failure features
    failure_features = failure_counts.merge(
        cost_agg, on='equipment_id', how='outer'
    ).merge(
        downtime_agg, on='equipment_id', how='outer'
    ).merge(
        severity_counts, on='equipment_id', how='outer'
    ).merge(
        mtbf, on='equipment_id', how='outer'
    ).reset_index()
    
    # Fill NaN with 0
    failure_features = failure_features.fillna(0)
    
    return failure_features

def run_stage2(data):
    """Execute Stage 2: Feature Engineering"""
    print("\n" + "="*60)
    print("STAGE 2: FEATURE ENGINEERING")
    print("="*60)
    
    equipment_df = data['equipment']
    maintenance_df = data['maintenance']
    failures_df = data['failures']
    
    print(" Calculating equipment features...")
    features = calculate_equipment_features(equipment_df)
    
    print(" Aggregating maintenance features...")
    maintenance_features = aggregate_maintenance_features(maintenance_df)
    features = features.merge(maintenance_features, on='equipment_id', how='left')
    
    print(" Aggregating failure features...")
    failure_features = aggregate_failure_features(failures_df)
    features = features.merge(failure_features, on='equipment_id', how='left')
    
    print(" Creating derived features...")
    features = create_derived_features(features)
    
    # Fill NaN values
    features = features.fillna(0)
    
    # Feature summary
    feature_cols = [col for col in features.columns if col not in ['equipment_id', 'equipment_type', 'location']]
    
    print(f"\n[COMPLETE] Stage 2 Complete!")
    print(f"   Total features calculated: {len(feature_cols)}")
    print(f"   Equipment with features: {len(features)}")
    print(f"   Feature categories:")
    print(f"     - Equipment: age, usage")
    print(f"     - Maintenance: count, cost, frequency")
    print(f"     - Failures: count, MTBF, severity")
    print(f"     - Derived: ratios, trends, risk indicators")
    
    return features

if __name__ == "__main__":
    # Test stage 2
    from stage1_data_ingestion import run_stage1
    data = run_stage1()
    result = run_stage2(data)
    print(f"\nFeatures sample:")
    print(result['features'][result['feature_columns']].head())
