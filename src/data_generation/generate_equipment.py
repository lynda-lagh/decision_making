"""
Generate synthetic equipment data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from config import *


def generate_equipment_data(num_equipment=NUM_EQUIPMENT):
    """
    Generate synthetic equipment data
    
    Parameters:
    -----------
    num_equipment : int
        Number of equipment records to generate
        
    Returns:
    --------
    pd.DataFrame
        Equipment data
    """
    
    np.random.seed(RANDOM_SEED)
    random.seed(RANDOM_SEED)
    
    equipment_list = []
    equipment_counter = {}
    
    # Initialize counters for each type
    for eq_type in EQUIPMENT_TYPES.keys():
        equipment_counter[eq_type] = 1
    
    # Calculate number of each equipment type
    type_counts = {}
    for eq_type, config in EQUIPMENT_TYPES.items():
        type_counts[eq_type] = int(num_equipment * config['proportion'])
    
    # Adjust to ensure total equals num_equipment
    total = sum(type_counts.values())
    if total < num_equipment:
        # Add remaining to Tractor (most common)
        type_counts['Tractor'] += (num_equipment - total)
    
    for eq_type, count in type_counts.items():
        config = EQUIPMENT_TYPES[eq_type]
        
        for i in range(count):
            # Generate equipment ID
            equipment_id = f"{config['prefix']}-{equipment_counter[eq_type]:03d}"
            equipment_counter[eq_type] += 1
            
            # Random brand and model
            brand = random.choice(config['brands'])
            model = random.choice(config['models'])
            
            # Generate age using normal distribution
            age = int(np.clip(
                np.random.normal(EQUIPMENT_AGE_MEAN, EQUIPMENT_AGE_STD),
                EQUIPMENT_AGE_MIN,
                EQUIPMENT_AGE_MAX
            ))
            
            year_manufactured = datetime.now().year - age
            
            # Purchase date (sometime in the year of manufacture or next year)
            purchase_year = year_manufactured + random.randint(0, 1)
            purchase_month = random.randint(1, 12)
            purchase_day = random.randint(1, 28)
            purchase_date = datetime(purchase_year, purchase_month, purchase_day)
            
            # Purchase cost
            cost_min, cost_max = config['purchase_cost_range']
            purchase_cost = round(random.uniform(cost_min, cost_max), 2)
            
            # Operating hours (based on age and annual usage)
            hours_min, hours_max = config['annual_hours_range']
            avg_annual_hours = (hours_min + hours_max) / 2
            # Add some variation
            operating_hours = int(age * avg_annual_hours * random.uniform(0.8, 1.2))
            
            # Current status (most are active)
            status_weights = [0.85, 0.10, 0.05]  # Active, Under Maintenance, Retired
            current_status = random.choices(EQUIPMENT_STATUS, weights=status_weights)[0]
            
            # Last service date (within last 3 months for active equipment)
            if current_status == 'Active':
                days_since_service = random.randint(30, 90)
                last_service_date = datetime.now() - timedelta(days=days_since_service)
            elif current_status == 'Under Maintenance':
                last_service_date = datetime.now() - timedelta(days=random.randint(1, 7))
            else:  # Retired
                last_service_date = datetime.now() - timedelta(days=random.randint(180, 365))
            
            # Next service due
            if current_status != 'Retired':
                # Based on hours or time (whichever comes first)
                next_service_due = last_service_date + timedelta(days=random.randint(60, 120))
            else:
                next_service_due = None
            
            # Location
            location = random.choice(FARM_LOCATIONS)
            
            # Create equipment record
            equipment = {
                'equipment_id': equipment_id,
                'equipment_type': eq_type,
                'brand': brand,
                'model': model,
                'year_manufactured': year_manufactured,
                'purchase_date': purchase_date.strftime('%Y-%m-%d'),
                'purchase_cost': purchase_cost,
                'current_status': current_status,
                'operating_hours': operating_hours,
                'last_service_date': last_service_date.strftime('%Y-%m-%d') if last_service_date else None,
                'next_service_due': next_service_due.strftime('%Y-%m-%d') if next_service_due else None,
                'location': location,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            equipment_list.append(equipment)
    
    # Create DataFrame
    df_equipment = pd.DataFrame(equipment_list)
    
    # Sort by equipment_id
    df_equipment = df_equipment.sort_values('equipment_id').reset_index(drop=True)
    
    return df_equipment


def save_equipment_data(df, filename='equipment.csv'):
    """Save equipment data to CSV"""
    import os
    # Use absolute path
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, 'data', 'synthetic')
    
    # Create directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    filepath = os.path.join(data_dir, filename)
    df.to_csv(filepath, index=False)
    print(f"✅ Equipment data saved to {filepath}")
    print(f"   Total records: {len(df)}")
    print(f"\n   Equipment by type:")
    print(df['equipment_type'].value_counts().to_string())
    return filepath


if __name__ == "__main__":
    print("Generating synthetic equipment data...")
    print(f"Number of equipment: {NUM_EQUIPMENT}")
    print(f"Random seed: {RANDOM_SEED}\n")
    
    # Generate data
    df_equipment = generate_equipment_data()
    
    # Display sample
    print("\nSample equipment records:")
    print(df_equipment.head(10).to_string())
    
    # Display statistics
    print("\n" + "="*80)
    print("EQUIPMENT STATISTICS")
    print("="*80)
    print(f"\nTotal Equipment: {len(df_equipment)}")
    print(f"\nBy Type:")
    print(df_equipment['equipment_type'].value_counts())
    print(f"\nBy Status:")
    print(df_equipment['current_status'].value_counts())
    print(f"\nBy Brand:")
    print(df_equipment['brand'].value_counts())
    print(f"\nAge Statistics:")
    current_year = datetime.now().year
    df_equipment['age'] = current_year - df_equipment['year_manufactured']
    print(df_equipment['age'].describe())
    print(f"\nOperating Hours Statistics:")
    print(df_equipment['operating_hours'].describe())
    print(f"\nPurchase Cost Statistics:")
    print(df_equipment['purchase_cost'].describe())
    
    # Save to file
    print("\n" + "="*80)
    save_equipment_data(df_equipment)
