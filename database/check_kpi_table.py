"""
Check the KPI metrics table structure
"""

import psycopg2

def check_kpi_table():
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='weefarm_db',
            user='postgres',
            password='0000'
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Check if kpi_metrics table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'kpi_metrics'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("❌ KPI metrics table does not exist!")
            return
        
        # Get column information
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'kpi_metrics'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        print("\n📊 KPI Metrics Table Structure:")
        print("-" * 60)
        print(f"{'Column Name':<30} {'Data Type':<20} {'Nullable':<10}")
        print(f"{'-'*30:<30} {'-'*20:<20} {'-'*10:<10}")
        
        for col in columns:
            print(f"{col[0]:<30} {col[1]:<20} {'YES' if col[2] == 'YES' else 'NO':<10}")
        
        # Get row count
        cursor.execute("SELECT COUNT(*) FROM kpi_metrics")
        row_count = cursor.fetchone()[0]
        print(f"\nTotal rows: {row_count}")
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_kpi_table()
