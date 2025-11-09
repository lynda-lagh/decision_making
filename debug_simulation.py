#!/usr/bin/env python3
"""
Debug simulation layer to find the integer out of range issue
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pipeline'))

from simulation_layer import generate_hourly_data

# Generate sample data
print("Generating sample sensor data...")
df = generate_hourly_data(equipment_count=5)

print("\nData types:")
print(df.dtypes)

print("\nFirst 5 rows:")
print(df.head())

print("\nData ranges:")
for col in df.columns:
    if df[col].dtype in ['int64', 'float64']:
        print(f"\n{col}:")
        print(f"  Min: {df[col].min()}")
        print(f"  Max: {df[col].max()}")
        print(f"  Mean: {df[col].mean()}")
        print(f"  NaN count: {df[col].isna().sum()}")
        
        # Check for out of range integers
        if col == 'rpm':
            print(f"  Sample values: {df[col].head().tolist()}")
            # Check if any values are too large for 32-bit integer
            max_int32 = 2147483647
            if df[col].max() > max_int32:
                print(f"  ⚠️ WARNING: RPM values exceed 32-bit integer limit!")
            # Check for negative values
            if df[col].min() < 0:
                print(f"  ⚠️ WARNING: Negative RPM values found!")

print("\n" + "="*80)
print("Checking for problematic values...")

# Check each column for potential database issues
for col in df.columns:
    if col == 'rpm':
        invalid = df[df[col] < 0]
        if len(invalid) > 0:
            print(f"⚠️ {col}: {len(invalid)} negative values")
            print(f"   Values: {invalid[col].tolist()}")
        
        # Check for extremely large values
        invalid = df[df[col] > 10000]
        if len(invalid) > 0:
            print(f"⚠️ {col}: {len(invalid)} values > 10000")
            print(f"   Values: {invalid[col].tolist()}")

print("\nDone!")
