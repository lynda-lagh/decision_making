"""
WeeFarm Data Migration Script
Migrate CSV data to PostgreSQL database
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from datetime import datetime

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'weefarm_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '0000')
}

# Data file paths
DATA_DIR = 'data/synthetic'
EQUIPMENT_FILE = os.path.join(DATA_DIR, 'equipment.csv')
MAINTENANCE_FILE = os.path.join(DATA_DIR, 'maintenance_records.csv')
FAILURE_FILE = os.path.join(DATA_DIR, 'failure_events.csv')

def connect_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Connected to PostgreSQL database")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def migrate_equipment(conn):
    """Migrate equipment data"""
    print("\n📦 Migrating equipment data...")
    
    try:
        # Read CSV
        df = pd.read_csv(EQUIPMENT_FILE)
        print(f"   Found {len(df)} equipment records")
        
        # Prepare data
        df['purchase_date'] = pd.to_datetime(df['purchase_date']).dt.date
        df['last_service_date'] = pd.to_datetime(df['last_service_date']).dt.date
        
        # Insert data
        cursor = conn.cursor()
        
        insert_query = """
        INSERT INTO equipment (
            equipment_id, equipment_type, brand, model, year_manufactured,
            purchase_date, location, operating_hours, last_service_date
        ) VALUES %s
        ON CONFLICT (equipment_id) DO NOTHING
        """
        
        values = [
            (
                row['equipment_id'], row['equipment_type'], row['brand'],
                row['model'], row['year_manufactured'], row['purchase_date'],
                row['location'], row['operating_hours'], row['last_service_date']
            )
            for _, row in df.iterrows()
        ]
        
        execute_values(cursor, insert_query, values)
        conn.commit()
        
        print(f"✅ Migrated {len(df)} equipment records")
        
    except Exception as e:
        print(f"❌ Error migrating equipment: {e}")
        conn.rollback()

def migrate_maintenance(conn):
    """Migrate maintenance records"""
    print("\n🔧 Migrating maintenance records...")
    
    try:
        # Read CSV
        df = pd.read_csv(MAINTENANCE_FILE)
        print(f"   Found {len(df)} maintenance records")
        
        # Prepare data
        df['maintenance_date'] = pd.to_datetime(df['maintenance_date']).dt.date
        
        # Insert data
        cursor = conn.cursor()
        
        insert_query = """
        INSERT INTO maintenance_records (
            equipment_id, maintenance_date, type_id, description,
            technician, parts_replaced, total_cost, downtime_hours
        ) VALUES %s
        """
        
        values = [
            (
                row['equipment_id'], row['maintenance_date'], row['type_id'],
                row.get('description', ''), row.get('technician', ''),
                row.get('parts_replaced', ''), row['total_cost'], row['downtime_hours']
            )
            for _, row in df.iterrows()
        ]
        
        execute_values(cursor, insert_query, values)
        conn.commit()
        
        print(f"✅ Migrated {len(df)} maintenance records")
        
    except Exception as e:
        print(f"❌ Error migrating maintenance records: {e}")
        conn.rollback()

def migrate_failures(conn):
    """Migrate failure events"""
    print("\n⚠️  Migrating failure events...")
    
    try:
        # Read CSV
        df = pd.read_csv(FAILURE_FILE)
        print(f"   Found {len(df)} failure events")
        
        # Prepare data
        df['failure_date'] = pd.to_datetime(df['failure_date']).dt.date
        
        # Insert data
        cursor = conn.cursor()
        
        insert_query = """
        INSERT INTO failure_events (
            failure_id, equipment_id, failure_date, failure_type, severity,
            root_cause, repair_cost, downtime_hours, parts_replaced, 
            preventable, prevented_by_maintenance
        ) VALUES %s
        """
        
        values = [
            (
                row['failure_id'], row['equipment_id'], row['failure_date'], 
                row['failure_type'], row['severity'], row.get('root_cause', ''),
                row['repair_cost'], row['downtime_hours'], row.get('parts_replaced', ''),
                row.get('preventable', False), row.get('prevented_by_maintenance', False)
            )
            for _, row in df.iterrows()
        ]
        
        execute_values(cursor, insert_query, values)
        conn.commit()
        
        print(f"✅ Migrated {len(df)} failure events")
        
    except Exception as e:
        print(f"❌ Error migrating failure events: {e}")
        conn.rollback()

def verify_migration(conn):
    """Verify data migration"""
    print("\n🔍 Verifying migration...")
    
    try:
        cursor = conn.cursor()
        
        # Count records in each table
        tables = ['equipment', 'maintenance_records', 'failure_events']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} records")
        
        print("\n✅ Migration verification complete!")
        
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")

def main():
    """Main migration function"""
    print("=" * 60)
    print("WeeFarm Data Migration")
    print("=" * 60)
    
    # Connect to database
    conn = connect_db()
    if not conn:
        return
    
    try:
        # Migrate data
        migrate_equipment(conn)
        migrate_maintenance(conn)
        migrate_failures(conn)
        
        # Verify
        verify_migration(conn)
        
        print("\n" + "=" * 60)
        print("🎉 Data migration completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
    
    finally:
        conn.close()
        print("\n✅ Database connection closed")

if __name__ == "__main__":
    main()
