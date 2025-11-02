"""
Generate synthetic maintenance records and failure events
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from config import *


def generate_maintenance_records(df_equipment):
    """
    Generate synthetic maintenance records for equipment
    
    Parameters:
    -----------
    df_equipment : pd.DataFrame
        Equipment data
        
    Returns:
    --------
    pd.DataFrame
        Maintenance records
    """
    
    np.random.seed(RANDOM_SEED)
    random.seed(RANDOM_SEED)
    
    maintenance_list = []
    record_id = 1
    
    for _, equipment in df_equipment.iterrows():
        equipment_id = equipment['equipment_id']
        eq_type = equipment['equipment_type']
        purchase_date = datetime.strptime(equipment['purchase_date'], '%Y-%m-%d')
        
        # Calculate years of operation
        years_in_service = (END_DATE - purchase_date).days / 365.25
        
        # Get maintenance frequency for this equipment type
        freq_min, freq_max = MAINTENANCE_FREQUENCY[eq_type]
        annual_frequency = random.uniform(freq_min, freq_max)
        
        # Total number of maintenance events
        total_maintenance = int(years_in_service * annual_frequency)
        
        # Generate maintenance dates
        for _ in range(total_maintenance):
            # Random date between purchase and end date
            days_range = (END_DATE - purchase_date).days
            random_days = random.randint(0, days_range)
            maintenance_date = purchase_date + timedelta(days=random_days)
            
            # Apply seasonal pattern
            month = maintenance_date.month
            seasonal_factor = SEASONAL_MAINTENANCE[month]
            
            # Decide if this maintenance happens (based on seasonal factor)
            if random.random() > (seasonal_factor / max(SEASONAL_MAINTENANCE.values())):
                continue
            
            # Determine maintenance type
            type_probs = [MAINTENANCE_TYPES[i]['proportion'] for i in [1, 2, 3]]
            type_id = random.choices([1, 2, 3], weights=type_probs)[0]
            type_name = MAINTENANCE_TYPES[type_id]['name']
            
            # Generate cost (log-normal distribution)
            cost_mean, cost_std = MAINTENANCE_COST_PARAMS[type_name]
            parts_cost = max(0, np.random.lognormal(np.log(cost_mean), 0.5) * random.uniform(0.3, 0.7))
            labor_cost = max(0, np.random.lognormal(np.log(cost_mean), 0.5) * random.uniform(0.3, 0.7))
            total_cost = round(parts_cost + labor_cost, 2)
            parts_cost = round(parts_cost, 2)
            labor_cost = round(labor_cost, 2)
            
            # Generate downtime hours
            downtime_mean, downtime_std = MAINTENANCE_DOWNTIME[type_name]
            downtime_hours = max(0.5, np.random.normal(downtime_mean, downtime_std))
            downtime_hours = round(downtime_hours, 1)
            
            # Labor hours (usually slightly less than downtime)
            labor_hours = round(downtime_hours * random.uniform(0.7, 0.9), 1)
            
            # Generate description based on type
            descriptions = generate_maintenance_description(eq_type, type_name)
            description = random.choice(descriptions)
            
            # Parts replaced
            parts = generate_parts_list(eq_type, type_name)
            
            # Technician
            technician = random.choice(TECHNICIAN_NAMES)
            
            # Notes - Tunisian context
            notes_options = [
                'Entretien de routine',
                'Travaux terminés comme prévu',
                'Aucun problème détecté',
                'Ajustements mineurs effectués',
                'Tous systèmes vérifiés',
                'Préparation saison récolte',
                'Adaptation climat chaud',
                None
            ]
            notes = random.choice(notes_options)
            
            # Create maintenance record
            record = {
                'record_id': record_id,
                'equipment_id': equipment_id,
                'maintenance_date': maintenance_date.strftime('%Y-%m-%d'),
                'type_id': type_id,
                'description': description,
                'parts_replaced': parts,
                'labor_hours': labor_hours,
                'parts_cost': parts_cost,
                'labor_cost': labor_cost,
                'total_cost': total_cost,
                'downtime_hours': downtime_hours,
                'technician_name': technician,
                'notes': notes,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            maintenance_list.append(record)
            record_id += 1
    
    # Create DataFrame
    df_maintenance = pd.DataFrame(maintenance_list)
    
    # Sort by date
    df_maintenance = df_maintenance.sort_values('maintenance_date').reset_index(drop=True)
    df_maintenance['record_id'] = range(1, len(df_maintenance) + 1)
    
    return df_maintenance


def generate_failure_events(df_equipment, df_maintenance):
    """
    Generate synthetic failure events
    
    Parameters:
    -----------
    df_equipment : pd.DataFrame
        Equipment data
    df_maintenance : pd.DataFrame
        Maintenance records
        
    Returns:
    --------
    pd.DataFrame
        Failure events
    """
    
    np.random.seed(RANDOM_SEED + 1)
    random.seed(RANDOM_SEED + 1)
    
    failure_list = []
    failure_id = 1
    
    for _, equipment in df_equipment.iterrows():
        equipment_id = equipment['equipment_id']
        eq_type = equipment['equipment_type']
        purchase_date = datetime.strptime(equipment['purchase_date'], '%Y-%m-%d')
        
        # Calculate years of operation
        years_in_service = (END_DATE - purchase_date).days / 365.25
        
        # Get failure rate for this equipment type
        rate_min, rate_max = FAILURE_RATE[eq_type]
        annual_failure_rate = random.uniform(rate_min, rate_max)
        
        # Total number of failures
        total_failures = int(years_in_service * annual_failure_rate)
        
        # Generate failure dates
        for _ in range(total_failures):
            # Random date between purchase and end date
            days_range = (END_DATE - purchase_date).days
            random_days = random.randint(0, days_range)
            failure_date = purchase_date + timedelta(days=random_days)
            
            # Apply seasonal pattern
            month = failure_date.month
            seasonal_factor = SEASONAL_FAILURES[month]
            
            # Decide if this failure happens (based on seasonal factor)
            if random.random() > (seasonal_factor / max(SEASONAL_FAILURES.values())):
                continue
            
            # Determine failure type
            failure_type_probs = [FAILURE_TYPES[ft]['proportion'] for ft in FAILURE_TYPES.keys()]
            failure_type = random.choices(list(FAILURE_TYPES.keys()), weights=failure_type_probs)[0]
            
            # Determine severity based on failure type
            severity_dist = FAILURE_TYPES[failure_type]['severity_dist']
            severity = random.choices(
                list(severity_dist.keys()),
                weights=list(severity_dist.values())
            )[0]
            
            # Generate cost and downtime based on severity
            cost_range = FAILURE_PARAMS[severity]['cost']
            downtime_range = FAILURE_PARAMS[severity]['downtime']
            
            repair_cost = round(random.uniform(*cost_range), 2)
            downtime_hours = round(random.uniform(*downtime_range), 1)
            
            # Generate description
            description = generate_failure_description(failure_type, severity)
            
            # Root cause
            root_cause = generate_root_cause(failure_type)
            
            # Could it have been prevented?
            # Higher chance for preventive if it's a wear-related failure
            prevented_prob = 0.7 if failure_type in ['Engine', 'Hydraulic', 'Belt', 'Tire'] else 0.4
            prevented_by_maintenance = random.random() < prevented_prob
            
            # Create failure record
            record = {
                'failure_id': failure_id,
                'equipment_id': equipment_id,
                'failure_date': failure_date.strftime('%Y-%m-%d'),
                'failure_type': failure_type,
                'severity': severity,
                'description': description,
                'root_cause': root_cause,
                'downtime_hours': downtime_hours,
                'repair_cost': repair_cost,
                'prevented_by_maintenance': prevented_by_maintenance,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            failure_list.append(record)
            failure_id += 1
    
    # Create DataFrame
    df_failures = pd.DataFrame(failure_list)
    
    # Sort by date
    df_failures = df_failures.sort_values('failure_date').reset_index(drop=True)
    df_failures['failure_id'] = range(1, len(df_failures) + 1)
    
    return df_failures


def generate_maintenance_description(eq_type, maint_type):
    """Generate realistic maintenance descriptions - Tunisian context"""
    
    descriptions = {
        'Preventive': [
            'Vidange et remplacement des filtres (Oil change and filter replacement)',
            'Inspection de routine et graissage (Routine inspection and lubrication)',
            'Contrôle saisonnier avant récolte (Seasonal check before harvest)',
            'Vérification niveaux liquides (Fluid levels check)',
            'Inspection courroies et durites (Belt and hose inspection)',
            'Contrôle pression pneus (Tire pressure check)',
            'Vérification batterie et nettoyage (Battery check and cleaning)',
            'Remplacement filtre à air (Air filter replacement)',
            'Changement filtre carburant (Fuel filter replacement)',
            'Vidange huile hydraulique (Hydraulic fluid change)',
            'Entretien système irrigation goutte-à-goutte (Drip irrigation maintenance)',
            'Préparation équipement saison des céréales (Cereal season prep)'
        ],
        'Corrective': [
            'Réparation fuite hydraulique (Hydraulic leak repair)',
            'Remplacement courroies usées (Worn belt replacement)',
            'Réparation circuit électrique (Electrical wiring repair)',
            'Réparation système carburant (Fuel system repair)',
            'Remplacement durite endommagée (Damaged hose replacement)',
            'Réparation direction (Steering mechanism repair)',
            'Réparation système freinage (Brake system repair)',
            'Remplacement capteur défectueux (Faulty sensor replacement)',
            'Réparation transmission (Transmission repair)',
            'Réparation système refroidissement (Cooling system repair)',
            'Réparation pompe irrigation (Irrigation pump repair)',
            'Réparation suite surchauffe moteur (Overheating repair)'
        ],
        'Predictive': [
            'Remplacement pièce montrant usure (Wear-based replacement)',
            'Remplacement préventif suite inspection (Preventive replacement)',
            'Correction vibrations anormales (Vibration issue correction)',
            'Remplacement avant défaillance (Pre-failure replacement)',
            'Remplacement joints proactif (Proactive seal replacement)',
            'Remplacement roulement (bruit détecté) (Bearing replacement - noise)',
            'Remplacement durite dégradée (Degraded hose replacement)'
        ]
    }
    
    return descriptions[maint_type]


def generate_parts_list(eq_type, maint_type):
    """Generate realistic parts lists - Tunisian/French terminology"""
    
    common_parts = {
        'Preventive': [
            'Filtre à huile', 'Filtre à air', 'Filtre carburant', 
            'Graisse', 'Huile moteur', 'Huile hydraulique',
            'Filtre hydraulique', 'Joint torique'
        ],
        'Corrective': [
            'Durite', 'Courroie', 'Joint', 'Roulement', 
            'Capteur', 'Relais', 'Fusible', 'Flexible hydraulique',
            'Piston', 'Pompe', 'Injecteur'
        ],
        'Predictive': [
            'Kit joints', 'Roulement', 'Courroie', 
            'Durite', 'Filtre', 'Flexible'
        ]
    }
    
    num_parts = random.randint(1, 4)
    parts = random.sample(common_parts[maint_type], min(num_parts, len(common_parts[maint_type])))
    
    return ', '.join(parts) if parts else None


def generate_failure_description(failure_type, severity):
    """Generate realistic failure descriptions"""
    
    descriptions = {
        'Engine': [
            'Engine overheating during operation',
            'Loss of power under load',
            'Engine oil leak detected',
            'Excessive smoke from exhaust',
            'Engine stalling intermittently',
            'Fuel system malfunction'
        ],
        'Hydraulic': [
            'Hydraulic hose burst during operation',
            'Hydraulic pump failure',
            'Hydraulic cylinder leak',
            'Loss of hydraulic pressure',
            'Hydraulic fluid contamination',
            'Hydraulic valve malfunction'
        ],
        'Electrical': [
            'Battery failure',
            'Alternator not charging',
            'Wiring harness damage',
            'Sensor malfunction',
            'Starter motor failure',
            'Electrical short circuit'
        ],
        'Mechanical': [
            'Transmission gear failure',
            'Bearing failure causing noise',
            'Drive shaft damage',
            'Clutch failure',
            'Gearbox malfunction',
            'Mechanical linkage broken'
        ],
        'Tire': [
            'Tire puncture',
            'Excessive tire wear',
            'Tire sidewall damage',
            'Tire blowout',
            'Wheel bearing failure'
        ],
        'Belt': [
            'Drive belt snapped',
            'Belt slipping under load',
            'Excessive belt wear',
            'Belt tensioner failure'
        ],
        'Other': [
            'Cab door malfunction',
            'Seat adjustment failure',
            'Mirror damage',
            'Light fixture broken',
            'Gauge malfunction'
        ]
    }
    
    base_desc = random.choice(descriptions[failure_type])
    
    if severity == 'Critical':
        base_desc += ' - Complete equipment shutdown'
    elif severity == 'Moderate':
        base_desc += ' - Reduced operational capability'
    
    return base_desc


def generate_root_cause(failure_type):
    """Generate realistic root causes"""
    
    causes = {
        'Engine': ['Lack of maintenance', 'Worn component', 'Contaminated fuel', 'Overheating', 'Age-related wear'],
        'Hydraulic': ['Worn hose', 'Exceeded service life', 'Contaminated fluid', 'Seal failure', 'Pressure spike'],
        'Electrical': ['Corroded connection', 'Worn component', 'Water damage', 'Vibration damage', 'Age-related failure'],
        'Mechanical': ['Normal wear', 'Lack of lubrication', 'Overload', 'Misalignment', 'Fatigue failure'],
        'Tire': ['Road hazard', 'Excessive wear', 'Improper inflation', 'Overload', 'Age degradation'],
        'Belt': ['Normal wear', 'Improper tension', 'Misalignment', 'Age degradation', 'Overload'],
        'Other': ['Accidental damage', 'Normal wear', 'Environmental factors', 'Operator error', 'Age-related']
    }
    
    return random.choice(causes[failure_type])


def save_maintenance_data(df, filename='maintenance_records.csv'):
    """Save maintenance data to CSV"""
    import os
    # Use absolute path
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, 'data', 'synthetic')
    
    # Create directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    filepath = os.path.join(data_dir, filename)
    df.to_csv(filepath, index=False)
    print(f"✅ Maintenance data saved to {filepath}")
    print(f"   Total records: {len(df)}")
    return filepath


def save_failure_data(df, filename='failure_events.csv'):
    """Save failure data to CSV"""
    import os
    # Use absolute path
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, 'data', 'synthetic')
    
    # Create directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    filepath = os.path.join(data_dir, filename)
    df.to_csv(filepath, index=False)
    print(f"✅ Failure data saved to {filepath}")
    print(f"   Total records: {len(df)}")
    return filepath


if __name__ == "__main__":
    import os
    # Load equipment data
    print("Loading equipment data...")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    equipment_file = os.path.join(base_dir, 'data', 'synthetic', 'equipment.csv')
    df_equipment = pd.read_csv(equipment_file)
    print(f"Loaded {len(df_equipment)} equipment records\n")
    
    # Generate maintenance records
    print("Generating maintenance records...")
    df_maintenance = generate_maintenance_records(df_equipment)
    
    print("\nSample maintenance records:")
    print(df_maintenance.head(10).to_string())
    
    print("\n" + "="*80)
    print("MAINTENANCE STATISTICS")
    print("="*80)
    print(f"\nTotal Maintenance Records: {len(df_maintenance)}")
    print(f"\nBy Type:")
    print(df_maintenance['type_id'].value_counts().sort_index())
    print(f"\nCost Statistics:")
    print(df_maintenance['total_cost'].describe())
    print(f"\nDowntime Statistics:")
    print(df_maintenance['downtime_hours'].describe())
    
    # Save maintenance data
    print("\n" + "="*80)
    save_maintenance_data(df_maintenance)
    
    # Generate failure events
    print("\n" + "="*80)
    print("Generating failure events...")
    df_failures = generate_failure_events(df_equipment, df_maintenance)
    
    print("\nSample failure events:")
    print(df_failures.head(10).to_string())
    
    print("\n" + "="*80)
    print("FAILURE STATISTICS")
    print("="*80)
    print(f"\nTotal Failure Events: {len(df_failures)}")
    print(f"\nBy Type:")
    print(df_failures['failure_type'].value_counts())
    print(f"\nBy Severity:")
    print(df_failures['severity'].value_counts())
    print(f"\nCost Statistics:")
    print(df_failures['repair_cost'].describe())
    print(f"\nDowntime Statistics:")
    print(df_failures['downtime_hours'].describe())
    print(f"\nPreventable Failures: {df_failures['prevented_by_maintenance'].sum()} ({df_failures['prevented_by_maintenance'].mean()*100:.1f}%)")
    
    # Save failure data
    print("\n" + "="*80)
    save_failure_data(df_failures)
    
    print("\n" + "="*80)
    print("✅ DATA GENERATION COMPLETE!")
    print("="*80)
