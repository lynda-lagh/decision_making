"""
Real-time Streaming Engine
Generates and streams sensor data every hour with realistic degradation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_values
import time
import schedule
import sys
sys.path.insert(0, '.')
from config import DB_CONFIG
from sensor_config import SENSOR_SPECS

class RealisticSensorSimulator:
    """
    Simulate realistic sensor data with:
    - Equipment degradation over time
    - Seasonal variations
    - Random failures
    - Maintenance effects
    """
    
    def __init__(self):
        self.equipment_cache = {}
        self.degradation_state = {}
        self.failure_probability = {}
        self.load_equipment()
    
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
                    'degradation_factor': 1.0
                }
                self.degradation_state[eq_id] = 1.0
                self.failure_probability[eq_id] = 0.01  # 1% base failure rate
            
            cursor.close()
            conn.close()
            
            print(f"[OK] Loaded {len(self.equipment_cache)} equipment")
            
        except Exception as e:
            print(f"[ERROR] Failed to load equipment: {e}")
    
    def get_seasonal_factor(self, timestamp):
        """
        Get seasonal factor (higher in summer, lower in winter)
        Represents seasonal stress on equipment
        """
        month = timestamp.month
        # Summer (June-August): 1.3x stress
        # Winter (December-February): 0.8x stress
        if month in [6, 7, 8]:
            return 1.3
        elif month in [12, 1, 2]:
            return 0.8
        else:
            return 1.0
    
    def update_degradation(self, equipment_id, hours_elapsed=1):
        """
        Update equipment degradation based on:
        - Operating hours
        - Age
        - Maintenance history
        """
        if equipment_id not in self.degradation_state:
            return 1.0
        
        # Degradation increases with operating hours
        base_degradation = 1.0 + (hours_elapsed / 10000)  # 0.01% per hour
        
        # Operating hours effect
        eq_data = self.equipment_cache.get(equipment_id, {})
        hours = eq_data.get('operating_hours', 0)
        
        # Equipment degrades faster with age
        if hours > 5000:
            base_degradation *= 1.2  # 20% faster degradation
        if hours > 10000:
            base_degradation *= 1.5  # 50% faster degradation
        
        # Update degradation state
        self.degradation_state[equipment_id] *= base_degradation
        
        # Update failure probability
        self.failure_probability[equipment_id] = min(
            0.5,  # Max 50% failure probability
            0.01 + (self.degradation_state[equipment_id] - 1.0) * 0.1
        )
        
        return self.degradation_state[equipment_id]
    
    def generate_sensor_reading(self, equipment_id, timestamp):
        """
        Generate realistic sensor reading with degradation
        """
        eq_data = self.equipment_cache.get(equipment_id)
        if not eq_data:
            return None
        
        # Update degradation
        degradation = self.update_degradation(equipment_id)
        seasonal = self.get_seasonal_factor(timestamp)
        
        # Base values from sensor specs
        specs = SENSOR_SPECS
        
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
        
        # Generate sensor values with degradation
        # Temperature increases with degradation
        temp_base = 85 + (degradation - 1.0) * 20  # Up to 105°C when degraded
        reading['engine_temperature'] = np.clip(
            np.random.normal(temp_base, 3) * seasonal,
            specs['engine_temperature']['min'],
            specs['engine_temperature']['max'] + 10  # Allow slight overage
        )
        
        # Oil pressure decreases with degradation
        oil_base = 4.5 - (degradation - 1.0) * 1.5  # Down to 3 bar when degraded
        reading['oil_pressure'] = np.clip(
            np.random.normal(oil_base, 0.3),
            specs['oil_pressure']['min'] - 0.5,  # Allow slight underage
            specs['oil_pressure']['max']
        )
        
        # Hydraulic pressure stable but increases with load
        hydraulic_base = 175 + (degradation - 1.0) * 30
        reading['hydraulic_pressure'] = np.clip(
            np.random.normal(hydraulic_base, 10),
            specs['hydraulic_pressure']['min'],
            specs['hydraulic_pressure']['max'] + 20
        )
        
        # Vibration increases significantly with degradation
        vibration_base = 2.0 + (degradation - 1.0) * 3.0
        reading['vibration_level'] = np.clip(
            np.random.normal(vibration_base, 0.5),
            specs['vibration_level']['min'],
            specs['vibration_level']['max'] + 5
        )
        
        # Fuel level random
        reading['fuel_level'] = np.random.uniform(20, 100)
        
        # Battery voltage decreases with degradation
        battery_base = 13.5 - (degradation - 1.0) * 0.5
        reading['battery_voltage'] = np.clip(
            np.random.normal(battery_base, 0.2),
            specs['battery_voltage']['min'],
            specs['battery_voltage']['max']
        )
        
        # RPM affected by degradation
        rpm_base = 1500 - (degradation - 1.0) * 200
        reading['rpm'] = int(np.clip(
            np.random.normal(rpm_base, 100),
            specs['rpm']['min'],
            specs['rpm']['max']
        ))
        
        # Anomaly detection
        if reading['engine_temperature'] > 110:
            reading['anomaly_detected'] = True
            reading['error_codes'] = 'TEMP_HIGH'
            reading['data_quality_flag'] = 'suspicious'
        
        if reading['oil_pressure'] < 2.5:
            reading['anomaly_detected'] = True
            reading['error_codes'] = 'OIL_PRESSURE_LOW'
            reading['data_quality_flag'] = 'suspicious'
        
        if reading['vibration_level'] > 8:
            reading['anomaly_detected'] = True
            reading['error_codes'] = 'VIBRATION_HIGH'
            reading['data_quality_flag'] = 'suspicious'
        
        # Random failures (based on degradation)
        if np.random.random() < self.failure_probability[equipment_id]:
            reading['anomaly_detected'] = True
            reading['error_codes'] = 'EQUIPMENT_FAILURE'
            reading['data_quality_flag'] = 'critical'
        
        return reading
    
    def generate_hourly_batch(self, timestamp=None):
        """
        Generate sensor readings for all equipment for current hour
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        readings = []
        for equipment_id in self.equipment_cache.keys():
            reading = self.generate_sensor_reading(equipment_id, timestamp)
            if reading:
                readings.append(reading)
        
        return pd.DataFrame(readings)

class StreamingEngine:
    """
    Real-time streaming engine
    Sends data every hour to database
    """
    
    def __init__(self):
        self.simulator = RealisticSensorSimulator()
        self.stream_count = 0
        self.start_time = datetime.now()
    
    def save_batch_to_db(self, df):
        """Save batch of sensor readings to database"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            data = []
            for _, row in df.iterrows():
                data.append((
                    str(row['equipment_id']),
                    row['timestamp'],
                    float(row['engine_temperature']) if pd.notna(row['engine_temperature']) else None,
                    float(row['oil_pressure']) if pd.notna(row['oil_pressure']) else None,
                    float(row['hydraulic_pressure']) if pd.notna(row['hydraulic_pressure']) else None,
                    float(row['vibration_level']) if pd.notna(row['vibration_level']) else None,
                    float(row['fuel_level']) if pd.notna(row['fuel_level']) else None,
                    float(row['battery_voltage']) if pd.notna(row['battery_voltage']) else None,
                    int(row['rpm']) if pd.notna(row['rpm']) else None,
                    str(row['error_codes']) if pd.notna(row['error_codes']) else None,
                    bool(row['anomaly_detected']),
                    str(row['data_quality_flag'])
                ))
            
            query = """
            INSERT INTO sensor_readings_raw 
            (equipment_id, timestamp, engine_temperature, oil_pressure, 
             hydraulic_pressure, vibration_level, fuel_level, battery_voltage, 
             rpm, error_codes, anomaly_detected, data_quality_flag)
            VALUES %s
            """
            
            execute_values(cursor, query, data)
            conn.commit()
            cursor.close()
            conn.close()
            
            return len(data)
            
        except Exception as e:
            print(f"[ERROR] Failed to save batch: {e}")
            return 0
    
    def stream_hourly(self):
        """Stream data every hour"""
        self.stream_count += 1
        timestamp = datetime.now()
        
        print("\n" + "="*80)
        print(f"[STREAM #{self.stream_count}] Real-time Sensor Data Stream")
        print(f"Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Generate batch
        print("\n[STEP 1] Generating sensor data for all equipment...")
        df = self.simulator.generate_hourly_batch(timestamp)
        print(f"[OK] Generated {len(df)} sensor readings")
        
        # Analyze batch
        anomalies = len(df[df['anomaly_detected']])
        critical = len(df[df['data_quality_flag'] == 'critical'])
        suspicious = len(df[df['data_quality_flag'] == 'suspicious'])
        
        print(f"\n[ANALYSIS]")
        print(f"  - Total readings: {len(df)}")
        print(f"  - Anomalies detected: {anomalies}")
        print(f"  - Critical issues: {critical}")
        print(f"  - Suspicious readings: {suspicious}")
        
        # Show sample data
        print(f"\n[SAMPLE DATA]")
        sample = df.head(3)
        for idx, row in sample.iterrows():
            print(f"  {row['equipment_id']}: Temp={row['engine_temperature']:.1f}°C, " +
                  f"Oil={row['oil_pressure']:.1f}bar, Vibration={row['vibration_level']:.1f}mm/s, " +
                  f"Anomaly={row['anomaly_detected']}")
        
        # Save to database
        print(f"\n[STEP 2] Saving to database...")
        saved = self.save_batch_to_db(df)
        print(f"[OK] Saved {saved} readings to database")
        
        # Statistics
        uptime = datetime.now() - self.start_time
        print(f"\n[STATISTICS]")
        print(f"  - Stream uptime: {uptime}")
        print(f"  - Total batches: {self.stream_count}")
        print(f"  - Total readings: {self.stream_count * len(df)}")
        print(f"  - Readings per hour: {len(df)}")
        
        print("\n" + "="*80)
    
    def start_streaming(self, test_mode=False):
        """
        Start real-time streaming
        
        Args:
            test_mode: If True, run once. If False, schedule hourly.
        """
        print("\n" + "="*80)
        print("REAL-TIME STREAMING ENGINE STARTED")
        print("="*80)
        print(f"Start time: {datetime.now()}")
        print(f"Mode: {'TEST (one-time)' if test_mode else 'PRODUCTION (hourly)'}")
        print("="*80)
        
        if test_mode:
            # Run once for testing
            self.stream_hourly()
            print("\n[TEST] Streaming test complete")
        else:
            # Schedule hourly
            schedule.every().hour.at(":00").do(self.stream_hourly)
            
            print("\n[SCHEDULED] Streaming scheduled for every hour at :00")
            print("Press Ctrl+C to stop\n")
            
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                print("\n[STOPPED] Streaming stopped by user")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-time Sensor Data Streaming')
    parser.add_argument('--test', action='store_true', help='Run in test mode (one-time)')
    parser.add_argument('--hours', type=int, default=1, help='Run for N hours (test mode)')
    
    args = parser.parse_args()
    
    engine = StreamingEngine()
    
    if args.test:
        # Test mode: run multiple times
        for i in range(args.hours):
            engine.stream_hourly()
            if i < args.hours - 1:
                print("\n[TEST] Waiting 5 seconds before next batch...\n")
                time.sleep(5)
    else:
        # Production mode: schedule hourly
        engine.start_streaming(test_mode=False)

if __name__ == "__main__":
    main()
