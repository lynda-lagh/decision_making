"""
Stage 1: Data Ingestion
Load equipment, maintenance, and failure data from PostgreSQL
"""

import pandas as pd
import psycopg2
from datetime import datetime
import sys
sys.path.append('..')
from config import DB_CONFIG

def load_equipment_data(conn):
    """Load equipment data from database"""
    query = """
    SELECT 
        equipment_id,
        equipment_type,
        brand,
        model,
        year_manufactured,
        purchase_date,
        location,
        operating_hours,
        last_service_date
    FROM equipment
    ORDER BY equipment_id
    """
    
    df = pd.read_sql(query, conn)
    print(f"   [OK] Loaded {len(df)} equipment records")
    return df

def load_maintenance_data(conn):
    """Load maintenance records from database"""
    query = """
    SELECT 
        equipment_id,
        maintenance_date,
        type_id,
        total_cost,
        downtime_hours
    FROM maintenance_records
    ORDER BY equipment_id, maintenance_date
    """
    
    df = pd.read_sql(query, conn)
    print(f"   [OK] Loaded {len(df)} maintenance records")
    return df

def load_failure_data(conn):
    """Load failure events from database"""
    query = """
    SELECT 
        equipment_id,
        failure_date,
        severity,
        repair_cost,
        downtime_hours,
        prevented_by_maintenance
    FROM failure_events
    ORDER BY equipment_id, failure_date
    """
    
    df = pd.read_sql(query, conn)
    print(f"   [OK] Loaded {len(df)} failure events")
    return df

def run_stage1():
    """Execute Stage 1: Data Ingestion"""
    print("\n" + "="*60)
    print("STAGE 1: DATA INGESTION")
    print("="*60)
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        print("[OK] Connected to PostgreSQL database")
        
        # Load data
        equipment_df = load_equipment_data(conn)
        maintenance_df = load_maintenance_data(conn)
        failure_df = load_failure_data(conn)
        
        # Close connection
        conn.close()
        
        print(f"\n[COMPLETE] Stage 1 Complete!")
        print(f"   Equipment: {len(equipment_df)} records")
        print(f"   Maintenance: {len(maintenance_df)} records")
        print(f"   Failures: {len(failure_df)} records")
        
        return {
            'equipment': equipment_df,
            'maintenance': maintenance_df,
            'failures': failure_df
        }
        
    except Exception as e:
        print(f"[ERROR] Error in Stage 1: {e}")
        raise

if __name__ == "__main__":
    data = run_stage1()
    print(f"\nEquipment sample:")
    print(data['equipment'].head())
