"""
Simulation Layer: Real-time Sensor Data Generation
Generates realistic sensor data with degradation patterns and imperfections
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_values
import sys
sys.path.append('.')
from config import DB_CONFIG
from sensor_config import SENSOR_SPECS, IMPERFECTION_RATES, EQUIPMENT_TYPES

# Ensure pandas is available for type checking
pd = pd

def generate_sensor_reading(equipment_id, equipment_type, timestamp, degradation_factor=1.0):
    """
    Generate a single sensor reading with realistic values and imperfections
    
    Args:
        equipment_id: Equipment identifier
        equipment_type: Type of equipment
        timestamp: Reading timestamp
        degradation_factor: Factor for equipment degradation (0.0-2.0)
    
    Returns:
        dict: Sensor reading with all values
    """
    reading = {
        'equipment_id': equipment_id,
        'timestamp': timestamp,
        'engine_temperature': None,
        'oil_pressure': None,
        'hydraulic_pressure': None,
        'vibration_level': None,
        'fuel_level': None,
        'battery_voltage': None,
        'rpm': None,
        'error_codes': None,
        'anomaly_detected': False,
        'data_quality_flag': 'good'
    }
    
    # Generate base sensor values
    reading['engine_temperature'] = np.random.normal(90, 5) * degradation_factor
    reading['oil_pressure'] = np.random.normal(4, 0.5) * degradation_factor
    reading['hydraulic_pressure'] = np.random.normal(175, 15) * degradation_factor
    reading['vibration_level'] = np.random.normal(2.5, 1) * degradation_factor
    reading['fuel_level'] = np.random.uniform(20, 100)
    reading['battery_voltage'] = np.random.normal(13.5, 0.3)
    reading['rpm'] = int(np.random.normal(1500, 200) * degradation_factor)
    
    # Introduce imperfections
    missing_prob = IMPERFECTION_RATES['missing_value_rate']
    outlier_prob = IMPERFECTION_RATES['outlier_rate']
    wrong_prob = IMPERFECTION_RATES['wrong_value_rate']
    
    sensors = ['engine_temperature', 'oil_pressure', 'hydraulic_pressure', 
               'vibration_level', 'fuel_level', 'battery_voltage', 'rpm']
    
    for sensor in sensors:
        rand = np.random.random()
        
        # Missing value
        if rand < missing_prob:
            reading[sensor] = None
            reading['data_quality_flag'] = 'suspicious'
        
        # Outlier
        elif rand < missing_prob + outlier_prob:
            spec = SENSOR_SPECS[sensor]
            reading[sensor] = np.random.uniform(spec['min'], spec['max']) * 2
            reading['data_quality_flag'] = 'suspicious'
        
        # Wrong value (outside range)
        elif rand < missing_prob + outlier_prob + wrong_prob:
            spec = SENSOR_SPECS[sensor]
            reading[sensor] = np.random.uniform(spec['max'] + 10, spec['max'] + 50)
            reading['data_quality_flag'] = 'suspicious'
    
    # Detect anomalies
    if reading['engine_temperature'] and reading['engine_temperature'] > 110:
        reading['anomaly_detected'] = True
        reading['error_codes'] = 'TEMP_HIGH'
    
    if reading['oil_pressure'] and reading['oil_pressure'] < 2.5:
        reading['anomaly_detected'] = True
        reading['error_codes'] = 'OIL_PRESSURE_LOW'
    
    return reading

def get_existing_equipment(limit=None):
    """
    Get existing equipment IDs from database
    
    Args:
        limit: Maximum number of equipment to retrieve
    
    Returns:
        list: List of (equipment_id, equipment_type) tuples
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        if limit:
            cursor.execute("SELECT equipment_id, equipment_type FROM equipment LIMIT %s", (limit,))
        else:
            cursor.execute("SELECT equipment_id, equipment_type FROM equipment")
        
        equipment = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return equipment
    except Exception as e:
        print(f"[WARNING] Could not load equipment from database: {e}")
        return []

def generate_hourly_data(equipment_count=100, timestamp=None):
    """
    Generate sensor data for all equipment for one hour
    
    Args:
        equipment_count: Number of equipment to generate data for
        timestamp: Timestamp for the reading (default: now)
    
    Returns:
        pd.DataFrame: DataFrame with sensor readings
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    # Get existing equipment from database
    existing_equipment = get_existing_equipment(limit=equipment_count)
    
    if not existing_equipment:
        print("[WARNING] No equipment found in database, using generated IDs")
        existing_equipment = [(f'EQ-{str(i+1).zfill(3)}', np.random.choice(EQUIPMENT_TYPES)) 
                            for i in range(equipment_count)]
    
    readings = []
    
    for i, (equipment_id, equipment_type) in enumerate(existing_equipment):
        # Degradation factor increases with equipment age
        degradation_factor = 1.0 + (i / len(existing_equipment)) * 0.5
        
        reading = generate_sensor_reading(
            equipment_id=equipment_id,
            equipment_type=equipment_type,
            timestamp=timestamp,
            degradation_factor=degradation_factor
        )
        
        readings.append(reading)
    
    df = pd.DataFrame(readings)
    return df

def insert_sensor_data_to_db(df):
    """
    Insert sensor readings into PostgreSQL database
    
    Args:
        df: DataFrame with sensor readings
    
    Returns:
        int: Number of rows inserted
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Prepare data for insertion
        data = []
        for _, row in df.iterrows():
            # Convert values to proper types
            rpm_val = int(row['rpm']) if pd.notna(row['rpm']) else None
            anomaly_val = bool(row['anomaly_detected']) if pd.notna(row['anomaly_detected']) else False
            
            data.append((
                str(row['equipment_id']),
                row['timestamp'],
                float(row['engine_temperature']) if pd.notna(row['engine_temperature']) else None,
                float(row['oil_pressure']) if pd.notna(row['oil_pressure']) else None,
                float(row['hydraulic_pressure']) if pd.notna(row['hydraulic_pressure']) else None,
                float(row['vibration_level']) if pd.notna(row['vibration_level']) else None,
                float(row['fuel_level']) if pd.notna(row['fuel_level']) else None,
                float(row['battery_voltage']) if pd.notna(row['battery_voltage']) else None,
                rpm_val,
                str(row['error_codes']) if pd.notna(row['error_codes']) else None,
                anomaly_val,
                str(row['data_quality_flag']) if pd.notna(row['data_quality_flag']) else 'good'
            ))
        
        # Insert data
        query = """
        INSERT INTO sensor_readings_raw 
        (equipment_id, timestamp, engine_temperature, oil_pressure, 
         hydraulic_pressure, vibration_level, fuel_level, battery_voltage, 
         rpm, error_codes, anomaly_detected, data_quality_flag)
        VALUES %s
        """
        
        execute_values(cursor, query, data)
        conn.commit()
        
        rows_inserted = len(data)
        cursor.close()
        conn.close()
        
        print(f"[OK] Inserted {rows_inserted} sensor readings into database")
        return rows_inserted
        
    except Exception as e:
        print(f"[ERROR] Failed to insert sensor data: {e}")
        return 0

def run_simulation_layer(equipment_count=100):
    """
    Execute simulation layer: generate and store sensor data
    
    Args:
        equipment_count: Number of equipment to simulate
    
    Returns:
        dict: Simulation results
    """
    print("\n" + "="*60)
    print("SIMULATION LAYER: SENSOR DATA GENERATION")
    print("="*60)
    
    try:
        # Generate data
        print(f"\n[STEP 1] Generating sensor data for {equipment_count} equipment...")
        df = generate_hourly_data(equipment_count=equipment_count)
        print(f"[OK] Generated {len(df)} sensor readings")
        
        # Insert to database
        print(f"\n[STEP 2] Inserting data into PostgreSQL...")
        rows_inserted = insert_sensor_data_to_db(df)
        
        # Summary
        print(f"\n[COMPLETE] Simulation layer complete!")
        print(f"   Readings generated: {len(df)}")
        print(f"   Readings inserted: {rows_inserted}")
        print(f"   Timestamp: {df['timestamp'].iloc[0]}")
        
        return {
            'success': True,
            'readings_generated': len(df),
            'readings_inserted': rows_inserted,
            'data': df
        }
        
    except Exception as e:
        print(f"[ERROR] Simulation layer failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    result = run_simulation_layer(equipment_count=100)
    if result['success']:
        print("\n[SUCCESS] Simulation layer executed successfully")
    else:
        print(f"\n[FAILED] {result['error']}")
