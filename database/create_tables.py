"""
Create database tables for WeeFarm
"""

import psycopg2
import os

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'weefarm_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '0000')
}

def create_tables():
    """Create all necessary tables"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("Creating tables...")
    
    # Equipment table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            equipment_id VARCHAR(50) PRIMARY KEY,
            equipment_type VARCHAR(100),
            brand VARCHAR(100),
            model VARCHAR(100),
            year_manufactured INTEGER,
            purchase_date DATE,
            location VARCHAR(200),
            operating_hours FLOAT,
            last_service_date DATE
        )
    """)
    print("✅ Equipment table created")
    
    # Maintenance records table (drop and recreate to fix schema)
    cur.execute("DROP TABLE IF EXISTS maintenance_records CASCADE")
    cur.execute("""
        CREATE TABLE maintenance_records (
            equipment_id VARCHAR(50) REFERENCES equipment(equipment_id),
            maintenance_date DATE,
            type_id INTEGER,
            description TEXT,
            technician VARCHAR(200),
            parts_replaced TEXT,
            total_cost FLOAT,
            downtime_hours FLOAT,
            next_service_date DATE
        )
    """)
    print("✅ Maintenance records table created")
    
    # Failure events table (drop and recreate to fix schema)
    cur.execute("DROP TABLE IF EXISTS failure_events CASCADE")
    cur.execute("""
        CREATE TABLE failure_events (
            failure_id VARCHAR(50) PRIMARY KEY,
            equipment_id VARCHAR(50) REFERENCES equipment(equipment_id),
            failure_date TIMESTAMP,
            failure_type VARCHAR(100),
            severity VARCHAR(50),
            root_cause VARCHAR(200),
            repair_cost FLOAT,
            downtime_hours FLOAT,
            parts_replaced TEXT,
            preventable BOOLEAN,
            prevented_by_maintenance BOOLEAN
        )
    """)
    print("✅ Failure events table created")
    
    # Predictions table (drop and recreate to fix schema)
    cur.execute("DROP TABLE IF EXISTS predictions CASCADE")
    cur.execute("""
        CREATE TABLE predictions (
            prediction_id SERIAL PRIMARY KEY,
            equipment_id VARCHAR(50) REFERENCES equipment(equipment_id),
            prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            svm_prediction INTEGER,
            svm_probability FLOAT,
            xgb_prediction INTEGER,
            xgb_probability FLOAT,
            risk_score FLOAT,
            failure_probability FLOAT,
            recommended_action TEXT,
            priority VARCHAR(50)
        )
    """)
    print("✅ Predictions table created")
    
    # Maintenance schedule table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS maintenance_schedule (
            task_id SERIAL PRIMARY KEY,
            equipment_id VARCHAR(50) REFERENCES equipment(equipment_id),
            scheduled_date DATE,
            task_type VARCHAR(100),
            priority VARCHAR(50),
            estimated_duration FLOAT,
            estimated_cost FLOAT,
            assigned_technician VARCHAR(200),
            status VARCHAR(50) DEFAULT 'Pending'
        )
    """)
    print("✅ Maintenance schedule table created")
    
    # KPI metrics table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS kpi_metrics (
            kpi_id SERIAL PRIMARY KEY,
            metric_name VARCHAR(100),
            metric_value FLOAT,
            target_value FLOAT,
            unit VARCHAR(50),
            category VARCHAR(50),
            calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ KPI metrics table created")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("\n✅ All tables created successfully!")

if __name__ == "__main__":
    try:
        create_tables()
    except Exception as e:
        print(f"❌ Error: {e}")
