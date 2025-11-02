"""
Master script to generate all synthetic data
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_equipment import generate_equipment_data, save_equipment_data
from generate_maintenance import (
    generate_maintenance_records,
    generate_failure_events,
    save_maintenance_data,
    save_failure_data
)
import pandas as pd


def main():
    """Generate all synthetic data"""
    
    print("="*80)
    print(" SYNTHETIC DATA GENERATION FOR PREDICTIVE MAINTENANCE SYSTEM")
    print("="*80)
    print()
    
    # Step 1: Generate Equipment Data
    print("STEP 1: Generating Equipment Data")
    print("-" * 80)
    df_equipment = generate_equipment_data()
    print(f"\n✅ Generated {len(df_equipment)} equipment records")
    
    # Display equipment summary
    print("\nEquipment Summary:")
    print(df_equipment['equipment_type'].value_counts().to_string())
    
    # Save equipment data
    equipment_file = save_equipment_data(df_equipment)
    
    # Step 2: Generate Maintenance Records
    print("\n" + "="*80)
    print("STEP 2: Generating Maintenance Records")
    print("-" * 80)
    df_maintenance = generate_maintenance_records(df_equipment)
    print(f"\n✅ Generated {len(df_maintenance)} maintenance records")
    
    # Display maintenance summary
    print("\nMaintenance Summary:")
    type_names = {1: 'Preventive', 2: 'Corrective', 3: 'Predictive'}
    maint_counts = df_maintenance['type_id'].value_counts().sort_index()
    for type_id, count in maint_counts.items():
        print(f"  {type_names[type_id]}: {count}")
    
    print(f"\nTotal Cost: ${df_maintenance['total_cost'].sum():,.2f}")
    print(f"Average Cost per Maintenance: ${df_maintenance['total_cost'].mean():,.2f}")
    
    # Save maintenance data
    maintenance_file = save_maintenance_data(df_maintenance)
    
    # Step 3: Generate Failure Events
    print("\n" + "="*80)
    print("STEP 3: Generating Failure Events")
    print("-" * 80)
    df_failures = generate_failure_events(df_equipment, df_maintenance)
    print(f"\n✅ Generated {len(df_failures)} failure events")
    
    # Display failure summary
    print("\nFailure Summary:")
    print(df_failures['failure_type'].value_counts().to_string())
    
    print(f"\nBy Severity:")
    print(df_failures['severity'].value_counts().to_string())
    
    print(f"\nTotal Repair Cost: ${df_failures['repair_cost'].sum():,.2f}")
    print(f"Average Repair Cost: ${df_failures['repair_cost'].mean():,.2f}")
    print(f"Total Downtime: {df_failures['downtime_hours'].sum():,.1f} hours")
    
    preventable = df_failures['prevented_by_maintenance'].sum()
    preventable_pct = (preventable / len(df_failures)) * 100
    print(f"\nPreventable Failures: {preventable} ({preventable_pct:.1f}%)")
    
    # Save failure data
    failure_file = save_failure_data(df_failures)
    
    # Step 4: Generate Summary Statistics
    print("\n" + "="*80)
    print("OVERALL SUMMARY")
    print("="*80)
    
    print(f"\n📊 Dataset Statistics:")
    print(f"   Equipment: {len(df_equipment)} records")
    print(f"   Maintenance Records: {len(df_maintenance)} records")
    print(f"   Failure Events: {len(df_failures)} records")
    print(f"   Total Records: {len(df_equipment) + len(df_maintenance) + len(df_failures)}")
    
    print(f"\n💰 Financial Summary:")
    total_maintenance_cost = df_maintenance['total_cost'].sum()
    total_failure_cost = df_failures['repair_cost'].sum()
    total_cost = total_maintenance_cost + total_failure_cost
    print(f"   Total Maintenance Cost: ${total_maintenance_cost:,.2f}")
    print(f"   Total Failure Cost: ${total_failure_cost:,.2f}")
    print(f"   Total Cost: ${total_cost:,.2f}")
    
    print(f"\n⏱️  Downtime Summary:")
    total_maint_downtime = df_maintenance['downtime_hours'].sum()
    total_failure_downtime = df_failures['downtime_hours'].sum()
    total_downtime = total_maint_downtime + total_failure_downtime
    print(f"   Maintenance Downtime: {total_maint_downtime:,.1f} hours")
    print(f"   Failure Downtime: {total_failure_downtime:,.1f} hours")
    print(f"   Total Downtime: {total_downtime:,.1f} hours")
    
    print(f"\n📈 Key Metrics:")
    avg_maint_per_equipment = len(df_maintenance) / len(df_equipment)
    avg_failures_per_equipment = len(df_failures) / len(df_equipment)
    print(f"   Avg Maintenance per Equipment: {avg_maint_per_equipment:.1f}")
    print(f"   Avg Failures per Equipment: {avg_failures_per_equipment:.1f}")
    print(f"   Failure Rate: {(avg_failures_per_equipment / 3):.2f} per year")
    
    # Calculate MTBF (Mean Time Between Failures)
    if len(df_failures) > 0:
        total_operating_hours = df_equipment['operating_hours'].sum()
        mtbf = total_operating_hours / len(df_failures)
        print(f"   Mean Time Between Failures (MTBF): {mtbf:.0f} hours")
    
    print("\n" + "="*80)
    print("✅ DATA GENERATION COMPLETE!")
    print("="*80)
    print("\n📁 Files created:")
    print(f"   1. {equipment_file}")
    print(f"   2. {maintenance_file}")
    print(f"   3. {failure_file}")
    
    print("\n🚀 Next Steps:")
    print("   1. Review the generated data files")
    print("   2. Run exploratory data analysis (EDA)")
    print("   3. Begin feature engineering")
    print("   4. Train machine learning models")
    
    print("\n" + "="*80)
    
    return df_equipment, df_maintenance, df_failures


if __name__ == "__main__":
    df_equipment, df_maintenance, df_failures = main()
