#!/usr/bin/env python3
"""
Create only the 3 missing tables needed for the pipeline
Preserves all existing tables and data
"""

import psycopg2
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pipeline'))

from config import DB_CONFIG

def create_missing_tables():
    """Create only the 3 missing tables"""
    
    print("\n" + "="*80)
    print("CREATE MISSING DATABASE TABLES")
    print("="*80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Table 1: sensor_readings_raw
        print("\n[TABLE 1] Creating sensor_readings_raw...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings_raw (
                reading_id SERIAL PRIMARY KEY,
                equipment_id VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                engine_temperature NUMERIC,
                oil_pressure NUMERIC,
                hydraulic_pressure NUMERIC,
                vibration_level NUMERIC,
                fuel_level NUMERIC,
                battery_voltage NUMERIC,
                rpm INTEGER,
                error_codes TEXT,
                anomaly_detected BOOLEAN,
                data_quality_flag VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
            );
        """)
        print("  ✓ sensor_readings_raw created")
        
        # Table 2: sensor_readings_clean
        print("\n[TABLE 2] Creating sensor_readings_clean...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings_clean (
                reading_id SERIAL PRIMARY KEY,
                equipment_id VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                engine_temperature NUMERIC,
                oil_pressure NUMERIC,
                hydraulic_pressure NUMERIC,
                vibration_level NUMERIC,
                fuel_level NUMERIC,
                battery_voltage NUMERIC,
                rpm INTEGER,
                data_quality_score NUMERIC,
                is_valid BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
            );
        """)
        print("  ✓ sensor_readings_clean created")
        
        # Table 3: recommendations
        print("\n[TABLE 3] Creating recommendations...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                recommendation_id SERIAL PRIMARY KEY,
                equipment_id VARCHAR(50) NOT NULL,
                priority_level VARCHAR(20) NOT NULL,
                recommendation_text TEXT,
                estimated_maintenance_cost NUMERIC,
                estimated_failure_cost NUMERIC,
                recommended_action VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
            );
        """)
        print("  ✓ recommendations created")
        
        # Commit changes
        conn.commit()
        
        # Verify tables were created
        print("\n[VERIFICATION] Checking created tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('sensor_readings_raw', 'sensor_readings_clean', 'recommendations')
            ORDER BY table_name
        """)
        
        created_tables = cursor.fetchall()
        
        if len(created_tables) == 3:
            print("  ✓ All 3 tables created successfully:")
            for table in created_tables:
                print(f"    - {table[0]}")
        else:
            print(f"  ⚠ Only {len(created_tables)} tables created (expected 3)")
        
        # Show table schemas
        print("\n[SCHEMAS] Table structures:")
        
        for table_name in ['sensor_readings_raw', 'sensor_readings_clean', 'recommendations']:
            cursor.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print(f"\n  {table_name}:")
            for col_name, col_type in columns:
                print(f"    - {col_name}: {col_type}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*80)
        print("✓ TABLES CREATED SUCCESSFULLY!")
        print("="*80)
        print("\nNext steps:")
        print("  1. Run: python quick_test.py")
        print("  2. Run: python test_complete_pipeline.py")
        print("\nExisting tables remain unchanged:")
        print("  - equipment")
        print("  - maintenance_records")
        print("  - failure_events")
        print("  - predictions")
        print("  - kpi_metrics")
        print("  - maintenance_schedule")
        print("  - sensor_readings (original)")
        print("  - kpi_targets")
        print("  - kpi_history")
        print("  - model_performance")
        print("\n" + "="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_missing_tables()
    sys.exit(0 if success else 1)
