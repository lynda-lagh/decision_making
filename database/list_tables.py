"""
List all tables and columns in the PostgreSQL database
"""

import sys
import os
import psycopg2
from sqlalchemy import create_engine, text

# Add parent directory to path
sys.path.append('..')
sys.path.append('../..')

# Import database configuration
try:
    from pipeline.config import DB_CONFIG
except ImportError:
    # Default configuration if import fails
    DB_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'weefarm_db',
        'user': 'postgres',
        'password': '0000'
    }

def list_all_tables():
    """List all tables and their columns in the database"""
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Execute query to list all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        # Fetch all results
        tables = cursor.fetchall()
        
        print("\n📊 Tables in database:")
        print("=" * 60)
        
        for table in tables:
            table_name = table[0]
            print(f"\n📋 {table_name}")
            print("-" * 60)
            
            # Get column information
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            
            # Print column details
            print(f"{'Column Name':<30} {'Data Type':<20} {'Nullable':<10}")
            print(f"{'-'*30:<30} {'-'*20:<20} {'-'*10:<10}")
            for col in columns:
                print(f"{col[0]:<30} {col[1]:<20} {'YES' if col[2] == 'YES' else 'NO':<10}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"\nTotal rows: {row_count}")
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        
        print("\n✅ Database inspection complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    list_all_tables()
