"""
Autonomous Dirty Data Streaming Engine
Generates 30-40% dirty sensor data every hour with system clock detection
Zero human intervention - runs 24/7 automatically
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_values
import time
import schedule
import sys
import os
from threading import Thread

sys.path.insert(0, '.')
from config import DB_CONFIG
from sensor_config import SENSOR_SPECS

class AutonomousDirtyDataStreamingEngine:
    """
    Generate extremely dirty sensor data (30-40% problematic) every hour
    Handles all data quality issues automatically
    """
    
    def __init__(self):
        self.equipment_cache = {}
        self.degradation_state = {}
        self.failure_probability = {}
        self.load_equipment()
        self.issue_stats = {
            'missing_values': 0,
            'outliers': 0,
            'duplicates': 0,
            'type_errors': 0,
            'timestamp_issues': 0,
            'range_violations': 0,
            'cross_sensor_issues': 0,
            'drift_issues': 0
        }
    
    def load_equipment(self):
        """Load equipment from database"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT equipment_id, equipment_type, operating_hours
                FROM equipment
            """)
            
            for eq_id, eq_type, hours in cursor.fetchall():
                self.equipment_cache[eq_id] = {
                    'type': eq_type,
                    'operating_hours': hours or 0,
                    'last_maintenance': None,
                    'degradation_factor': 1.0,
                    'sensor_baseline': {}
                }
            
            cursor.close()
            conn.close()
            print(f"[OK] Loaded {len(self.equipment_cache)} equipment units")
        except Exception as e:
            print(f"[ERROR] Failed to load equipment: {e}")
    
    def generate_dirty_sensor_reading(self, equipment_id, timestamp):
        """
        Generate a DIRTY sensor reading with 30-40% problematic data
        
        Returns dict with intentional data quality issues
        """
        reading = {
            'equipment_id': equipment_id,
            'timestamp': timestamp
        }
        
        # Randomly decide if this reading will have issues (30-40% chance)
        has_issues = np.random.random() < 0.35
        
        for sensor_name in SENSOR_SPECS.keys():
            spec = SENSOR_SPECS[sensor_name]
            
            if has_issues and np.random.random() < 0.3:
                # Generate one of 10 types of dirty data
                issue_type = np.random.choice([
                    'missing',      # 15-25%
                    'outlier',      # 10-15%
                    'drift',        # 5-10%
                    'type_error',   # 5-8%
                    'range_violation',  # 8-12%
                    'frozen',       # Repeated value
                    'negative',     # Impossible negative
                    'extreme',      # Way beyond limits
                    'string_error', # String instead of number
                    'zero_stuck'    # Stuck at zero
                ])
                
                if issue_type == 'missing':
                    reading[sensor_name] = None
                    self.issue_stats['missing_values'] += 1
                
                elif issue_type == 'outlier':
                    # Extreme spike
                    reading[sensor_name] = spec['max'] * np.random.uniform(1.5, 3.0)
                    self.issue_stats['outliers'] += 1
                
                elif issue_type == 'drift':
                    # Sensor drift (calibration error)
                    base = np.random.uniform(spec['min'], spec['max'])
                    reading[sensor_name] = base + np.random.uniform(5, 15)
                    self.issue_stats['drift_issues'] += 1
                
                elif issue_type == 'type_error':
                    # String instead of number
                    reading[sensor_name] = np.random.choice(['ERROR', 'N/A', '---', 'FAULT'])
                    self.issue_stats['type_errors'] += 1
                
                elif issue_type == 'range_violation':
                    # Beyond sensor limits
                    reading[sensor_name] = spec['max'] * np.random.uniform(1.2, 2.0)
                    self.issue_stats['range_violations'] += 1
                
                elif issue_type == 'frozen':
                    # Stuck value (repeated)
                    reading[sensor_name] = 75.0  # Frozen value
                    self.issue_stats['duplicates'] += 1
                
                elif issue_type == 'negative':
                    # Impossible negative
                    reading[sensor_name] = -np.random.uniform(1, 10)
                    self.issue_stats['outliers'] += 1
                
                elif issue_type == 'extreme':
                    # Way beyond physical limits
                    reading[sensor_name] = spec['max'] * np.random.uniform(2.0, 5.0)
                    self.issue_stats['outliers'] += 1
                
                elif issue_type == 'string_error':
                    # String with units
                    reading[sensor_name] = f"{np.random.uniform(spec['min'], spec['max']):.1f}°C"
                    self.issue_stats['type_errors'] += 1
                
                elif issue_type == 'zero_stuck':
                    # Stuck at zero
                    reading[sensor_name] = 0
                    self.issue_stats['zero_stuck'] = self.issue_stats.get('zero_stuck', 0) + 1
            
            else:
                # Normal reading
                reading[sensor_name] = np.random.uniform(spec['min'], spec['max'])
        
        # Add cross-sensor inconsistencies (5-7%)
        if np.random.random() < 0.06:
            temp = reading.get('engine_temperature', 0)
            # Handle case where temperature might be a string or None
            if temp is None:
                temp = 0
            elif isinstance(temp, str):
                try:
                    temp = float(temp.replace('°C', '').strip())
                except:
                    temp = 0
            
            if isinstance(temp, (int, float)) and temp > 100 and np.random.random() < 0.5:
                reading['cooling_state'] = 'OFF'  # Impossible!
                self.issue_stats['cross_sensor_issues'] += 1
        
        # Add timestamp issues (3-5%)
        if np.random.random() < 0.04:
            if np.random.random() < 0.5:
                reading['timestamp'] = None  # Missing timestamp
                self.issue_stats['timestamp_issues'] += 1
            else:
                # Future timestamp
                reading['timestamp'] = timestamp + timedelta(days=365)
                self.issue_stats['timestamp_issues'] += 1
        
        return reading
    
    def generate_hourly_batch(self):
        """
        Generate 2,779 DIRTY sensor readings for the past hour
        30-40% of data will have issues
        """
        print(f"\n{'='*80}")
        print(f"[AUTONOMOUS TRIGGER] System detected new hour at {datetime.now()}")
        print(f"{'='*80}")
        
        # Get current hour
        now = datetime.now()
        hour_start = now.replace(minute=0, second=0, microsecond=0)
        
        print(f"[STREAMING] Generating data for: {hour_start} - {now}")
        
        readings = []
        
        # Generate readings for each equipment
        for equipment_id in self.equipment_cache.keys():
            # Generate 7 readings per equipment (one per sensor roughly)
            for i in range(7):
                timestamp = hour_start + timedelta(minutes=np.random.randint(0, 60))
                reading = self.generate_dirty_sensor_reading(equipment_id, timestamp)
                readings.append(reading)
        
        df = pd.DataFrame(readings)
        
        print(f"\n[DATA GENERATION COMPLETE]")
        print(f"Total readings generated: {len(df)}")
        print(f"Missing values: {self.issue_stats['missing_values']}")
        print(f"Outliers: {self.issue_stats['outliers']}")
        print(f"Duplicates: {self.issue_stats['duplicates']}")
        print(f"Type errors: {self.issue_stats['type_errors']}")
        print(f"Timestamp issues: {self.issue_stats['timestamp_issues']}")
        print(f"Range violations: {self.issue_stats['range_violations']}")
        print(f"Cross-sensor issues: {self.issue_stats['cross_sensor_issues']}")
        print(f"Drift issues: {self.issue_stats['drift_issues']}")
        print(f"\nTotal issues: {sum(self.issue_stats.values())} ({sum(self.issue_stats.values())/len(df)*100:.1f}%)")
        
        return df
    
    def save_to_database(self, df):
        """Save dirty data to PostgreSQL (don't pre-clean)"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # Prepare data for insertion
            values = []
            for _, row in df.iterrows():
                # Convert string errors to NULL for numeric fields
                temp = row.get('engine_temperature')
                if isinstance(temp, str):
                    temp = None
                
                oil = row.get('oil_pressure')
                if isinstance(oil, str):
                    oil = None
                
                hyd = row.get('hydraulic_pressure')
                if isinstance(hyd, str):
                    hyd = None
                
                vib = row.get('vibration_level')
                if isinstance(vib, str):
                    vib = None
                
                fuel = row.get('fuel_level')
                if isinstance(fuel, str):
                    fuel = None
                
                batt = row.get('battery_voltage')
                if isinstance(batt, str):
                    batt = None
                
                rpm = row.get('rpm')
                if isinstance(rpm, str):
                    rpm = None
                
                values.append((
                    row.get('equipment_id'),
                    row.get('timestamp'),
                    temp,
                    oil,
                    hyd,
                    vib,
                    fuel,
                    batt,
                    rpm,
                    False,  # anomaly_detected
                    'raw'   # data_quality_flag
                ))
            
            # Insert into sensor_readings_raw
            insert_query = """
                INSERT INTO sensor_readings_raw 
                (equipment_id, timestamp, engine_temperature, oil_pressure, 
                 hydraulic_pressure, vibration_level, fuel_level, battery_voltage, 
                 rpm, anomaly_detected, data_quality_flag)
                VALUES %s
            """
            
            execute_values(cursor, insert_query, values)
            conn.commit()
            
            print(f"[OK] Saved {len(df)} dirty readings to database")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Failed to save to database: {e}")
    
    def run_autonomous_cycle(self):
        """
        Run one complete autonomous cycle:
        1. Detect current time from system clock
        2. Generate dirty data
        3. Save to database
        4. Pipeline will automatically clean and process
        """
        print(f"\n[CYCLE START] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Generate dirty data
        df_dirty = self.generate_hourly_batch()
        
        # Step 2: Save to database (dirty, not pre-cleaned)
        self.save_to_database(df_dirty)
        
        print(f"[CYCLE COMPLETE] Waiting for cleaning stage to process...")
        print(f"{'='*80}\n")
    
    def schedule_autonomous_execution(self):
        """
        Schedule the pipeline to run every hour at :00
        Uses system clock for timing
        """
        print("[SCHEDULER] Setting up autonomous hourly execution...")
        
        # Schedule to run at every hour
        schedule.every().hour.at(":00").do(self.run_autonomous_cycle)
        
        print("[SCHEDULER] Autonomous execution scheduled ✓")
        print("[SCHEDULER] System will run every hour at :00")
        
        # Keep scheduler running
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def start_background_scheduler(self):
        """Start scheduler in background thread"""
        scheduler_thread = Thread(target=self.schedule_autonomous_execution, daemon=True)
        scheduler_thread.start()
        print("[OK] Background scheduler started")
        return scheduler_thread

# Initialize and run
if __name__ == "__main__":
    engine = AutonomousDirtyDataStreamingEngine()
    
    print("\n" + "="*80)
    print("AUTONOMOUS DIRTY DATA STREAMING ENGINE")
    print("="*80)
    print("System Clock Detection: ✓")
    print("Autonomous Execution: ✓")
    print("Dirty Data Generation: ✓ (30-40% problematic)")
    print("Zero Human Intervention: ✓")
    print("="*80 + "\n")
    
    # Option 1: Run once immediately
    print("Running first cycle immediately...")
    engine.run_autonomous_cycle()
    
    # Option 2: Start background scheduler for hourly execution
    print("\nStarting background scheduler for hourly execution...")
    engine.start_background_scheduler()
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Autonomous streaming stopped")
