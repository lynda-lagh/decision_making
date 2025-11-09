"""
Stage 1: Data Preprocessing & Cleaning
Handles missing values, outliers, and data quality scoring
"""

import pandas as pd
import numpy as np
import psycopg2
from datetime import datetime, timedelta
import sys
sys.path.append('..')
from config import DB_CONFIG
from sensor_config import SENSOR_SPECS, PREPROCESSING_CONFIG
from utils.data_quality import (
    validate_sensor_range, detect_outliers_iqr, handle_missing_values,
    calculate_quality_score, classify_quality, remove_duplicates
)

SENSOR_COLUMNS = [
    'engine_temperature', 'oil_pressure', 'hydraulic_pressure',
    'vibration_level', 'fuel_level', 'battery_voltage', 'rpm'
]

def load_raw_sensor_data(hours_back=1):
    """
    Load raw sensor data from database
    
    Args:
        hours_back: Load data from last N hours
    
    Returns:
        pd.DataFrame: Raw sensor data
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        
        query = f"""
        SELECT 
            reading_id, equipment_id, timestamp,
            engine_temperature, oil_pressure, hydraulic_pressure,
            vibration_level, fuel_level, battery_voltage, rpm,
            error_codes, anomaly_detected, data_quality_flag
        FROM sensor_readings_raw
        WHERE timestamp >= NOW() - INTERVAL '{hours_back} hours'
        ORDER BY equipment_id, timestamp
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        print(f"[OK] Loaded {len(df)} raw sensor readings")
        return df
        
    except Exception as e:
        print(f"[ERROR] Failed to load raw sensor data: {e}")
        return pd.DataFrame()

def preprocess_sensor_data(df):
    """
    Preprocess sensor data: validate, clean, and score quality
    
    Args:
        df: Raw sensor dataframe
    
    Returns:
        pd.DataFrame: Preprocessed sensor data
    """
    df = df.copy()
    
    print("\n[STEP 1] Validating sensor ranges...")
    # Validate ranges
    for sensor in SENSOR_COLUMNS:
        if sensor in df.columns:
            invalid_mask = ~df[sensor].apply(lambda x: validate_sensor_range(x, sensor))
            invalid_count = invalid_mask.sum()
            if invalid_count > 0:
                print(f"   {sensor}: {invalid_count} invalid values")
                df.loc[invalid_mask, sensor] = np.nan
    
    print("\n[STEP 2] Handling missing values...")
    # Handle missing values
    for sensor in SENSOR_COLUMNS:
        if sensor in df.columns:
            missing_before = df[sensor].isna().sum()
            
            # Use forward fill for critical sensors
            if SENSOR_SPECS[sensor]['critical_sensor']:
                df[sensor] = df[sensor].fillna(method='ffill', limit=3)
            else:
                # Use interpolation for non-critical
                df[sensor] = df[sensor].interpolate(method='linear', limit=3)
            
            missing_after = df[sensor].isna().sum()
            if missing_before > 0:
                print(f"   {sensor}: {missing_before} → {missing_after} missing values")
    
    print("\n[STEP 3] Detecting and handling outliers...")
    # Detect and handle outliers
    for sensor in SENSOR_COLUMNS:
        if sensor in df.columns and df[sensor].dtype in [np.float64, np.int64]:
            outliers = detect_outliers_iqr(df[sensor], multiplier=1.5)
            outlier_count = outliers.sum()
            
            if outlier_count > 0:
                print(f"   {sensor}: {outlier_count} outliers detected")
                # Cap outliers to range
                spec = SENSOR_SPECS[sensor]
                df.loc[outliers, sensor] = df.loc[outliers, sensor].clip(
                    lower=spec['min'], upper=spec['max']
                )
    
    print("\n[STEP 4] Removing duplicates...")
    # Remove duplicates
    df_before = len(df)
    df = remove_duplicates(df, time_window=60)
    df_after = len(df)
    if df_before > df_after:
        print(f"   Removed {df_before - df_after} duplicate readings")
    
    print("\n[STEP 5] Calculating data quality scores...")
    # Calculate quality scores
    df['data_quality_score'] = df[SENSOR_COLUMNS].apply(
        lambda row: calculate_quality_score(row, SENSOR_COLUMNS), axis=1
    )
    df['processing_status'] = df['data_quality_score'].apply(classify_quality)
    
    # Count missing values per row
    df['missing_values_count'] = df[SENSOR_COLUMNS].isna().sum(axis=1)
    
    print(f"   Quality scores calculated")
    print(f"   Clean readings: {(df['processing_status'] == 'clean').sum()}")
    print(f"   Suspicious readings: {(df['processing_status'] == 'suspicious').sum()}")
    print(f"   Invalid readings: {(df['processing_status'] == 'invalid').sum()}")
    
    return df

def save_clean_data_to_db(df):
    """
    Save preprocessed data to sensor_readings_clean table
    
    Args:
        df: Preprocessed sensor dataframe
    
    Returns:
        int: Number of rows saved
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Prepare data
        data = []
        for _, row in df.iterrows():
            data.append((
                row['equipment_id'],
                row['timestamp'],
                row['engine_temperature'],
                row['oil_pressure'],
                row['hydraulic_pressure'],
                row['vibration_level'],
                row['fuel_level'],
                row['battery_voltage'],
                row['rpm'],
                row['error_codes'],
                row['anomaly_detected'],
                row['data_quality_score'],
                row['missing_values_count'],
                row['processing_status'],
                row.get('reading_id')
            ))
        
        # Insert
        query = """
        INSERT INTO sensor_readings_clean 
        (equipment_id, timestamp, engine_temperature, oil_pressure,
         hydraulic_pressure, vibration_level, fuel_level, battery_voltage,
         rpm, error_codes, anomaly_detected, data_quality_score,
         missing_values_count, processing_status, raw_reading_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        for row_data in data:
            cursor.execute(query, row_data)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"[OK] Saved {len(data)} clean sensor readings to database")
        return len(data)
        
    except Exception as e:
        print(f"[ERROR] Failed to save clean data: {e}")
        return 0

def run_stage1():
    """
    Execute Stage 1: Data Preprocessing
    
    Returns:
        dict: Preprocessing results
    """
    print("\n" + "="*60)
    print("STAGE 1: DATA PREPROCESSING & CLEANING")
    print("="*60)
    
    try:
        # Load raw data
        print("\n[LOADING] Raw sensor data from database...")
        df_raw = load_raw_sensor_data(hours_back=1)
        
        if df_raw.empty:
            print("[WARNING] No raw sensor data found")
            return {'success': False, 'error': 'No data to preprocess'}
        
        # Preprocess
        print("\n[PREPROCESSING] Cleaning and validating data...")
        df_clean = preprocess_sensor_data(df_raw)
        
        # Save
        print("\n[SAVING] Storing clean data to database...")
        rows_saved = save_clean_data_to_db(df_clean)
        
        # Summary
        print("\n[COMPLETE] Stage 1 Complete!")
        print(f"   Raw readings: {len(df_raw)}")
        print(f"   Clean readings: {len(df_clean)}")
        print(f"   Rows saved: {rows_saved}")
        print(f"   Avg quality score: {df_clean['data_quality_score'].mean():.1f}/100")
        
        return {
            'success': True,
            'raw_count': len(df_raw),
            'clean_count': len(df_clean),
            'rows_saved': rows_saved,
            'data': df_clean
        }
        
    except Exception as e:
        print(f"[ERROR] Stage 1 failed: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    result = run_stage1()
    if result['success']:
        print("\n[SUCCESS] Stage 1 executed successfully")
    else:
        print(f"\n[FAILED] {result.get('error', 'Unknown error')}")
