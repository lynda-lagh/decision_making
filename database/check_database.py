"""
Quick script to check database status
"""

from backend.app.database import engine
from sqlalchemy import inspect, text

def check_database():
    """Check database tables and data"""
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("=" * 60)
    print("DATABASE STATUS CHECK")
    print("=" * 60)
    
    print(f"\n📊 Found {len(tables)} tables:")
    for table in tables:
        print(f"  - {table}")
    
    # Check data counts
    print("\n📈 Data Counts:")
    
    with engine.connect() as conn:
        if 'equipment' in tables:
            result = conn.execute(text("SELECT COUNT(*) FROM equipment"))
            count = result.scalar()
            print(f"  - Equipment: {count}")
        
        if 'failure_events' in tables:
            result = conn.execute(text("SELECT COUNT(*) FROM failure_events"))
            count = result.scalar()
            print(f"  - Failure Events: {count}")
        
        if 'maintenance_records' in tables:
            result = conn.execute(text("SELECT COUNT(*) FROM maintenance_records"))
            count = result.scalar()
            print(f"  - Maintenance Records: {count}")
        
        if 'predictions' in tables:
            result = conn.execute(text("SELECT COUNT(*) FROM predictions"))
            count = result.scalar()
            print(f"  - Predictions: {count}")
        
        if 'maintenance_schedule' in tables:
            result = conn.execute(text("SELECT COUNT(*) FROM maintenance_schedule"))
            count = result.scalar()
            print(f"  - Scheduled Tasks: {count}")
        
        if 'kpi_metrics' in tables:
            result = conn.execute(text("SELECT COUNT(*) FROM kpi_metrics"))
            count = result.scalar()
            print(f"  - KPI Metrics: {count}")
    
    print("\n" + "=" * 60)
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    
    if len(tables) == 0:
        print("  ⚠️  No tables found! Run database migration:")
        print("     python database/migrate_data.py")
    
    if 'equipment' in tables:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM equipment"))
            if result.scalar() == 0:
                print("  ⚠️  No equipment data! Generate data:")
                print("     python src/data_generation/generate_all_data.py")
    
    if 'predictions' not in tables or 'maintenance_schedule' not in tables:
        print("  ⚠️  Missing predictions/schedule tables!")
        print("     These are created by the pipeline")
    
    print("\n✅ To populate dashboard:")
    print("  1. Ensure data exists: python src/data_generation/generate_all_data.py")
    print("  2. Run pipeline: python run_complete_pipeline.py")
    print("  3. Start API: cd backend && python -m app.main")
    print("  4. Start dashboard: cd dashboard && streamlit run app.py")

if __name__ == "__main__":
    check_database()
