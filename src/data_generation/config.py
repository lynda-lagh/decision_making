"""
Configuration file for synthetic data generation
"""

import random
from datetime import datetime

# Seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Data generation parameters - Tunisian context
# Optimized for ML training with sufficient data volume
NUM_EQUIPMENT = 400  # 400 equipment units (larger dataset)
START_DATE = datetime(2020, 1, 1)  # Extended to 5 years for better patterns
END_DATE = datetime(2024, 12, 31)  # Full 5 years of data
YEARS_OF_DATA = 5  # 5 years provides robust seasonal patterns

# Expected data volume with these parameters:
# - Equipment: 100 units
# - Maintenance: ~3,600-4,000 records
# - Failures: ~600-800 events
# - Total: ~4,500 events (excellent for ML)

# Currency note: All costs in Tunisian Dinar (TND)
# Approximate conversion: 1 USD ≈ 3.1 TND (2024)
CURRENCY = 'TND'

# Equipment configuration - Adapted for Tunisian Agriculture
EQUIPMENT_TYPES = {
    'Tractor': {
        'prefix': 'TRC',
        'brands': ['New Holland', 'Massey Ferguson', 'John Deere', 'Case IH', 'Landini', 'Deutz-Fahr'],
        'models': ['TD5.85', 'MF 5710', '5075E', 'Farmall 75C', 'Powerfarm 95', 'Agrofarm 420'],
        'purchase_cost_range': (80000, 200000),  # TND (Tunisian Dinar)
        'annual_hours_range': (400, 900),  # Higher usage in Tunisia
        'proportion': 0.45  # More tractors in Tunisian farms
    },
    'Harvester': {
        'prefix': 'HRV',
        'brands': ['New Holland', 'Case IH', 'John Deere', 'CLAAS'],
        'models': ['TC5.80', 'Axial-Flow 6140', 'S660', 'TUCANO 450'],
        'purchase_cost_range': (600000, 1200000),  # TND - Adapted for Tunisian market
        'annual_hours_range': (150, 350),  # Seasonal use (wheat, barley harvest)
        'proportion': 0.15
    },
    'Irrigation System': {
        'prefix': 'IRR',
        'brands': ['Valley', 'Reinke', 'Irritec', 'Netafim', 'Rivulis'],  # Include drip irrigation brands
        'models': ['Pivot 8000', 'RPM', 'Drip System Pro', 'UniRam', 'T-Tape'],
        'purchase_cost_range': (40000, 120000),  # TND - Critical for Tunisian agriculture
        'annual_hours_range': (1200, 2500),  # High usage due to climate
        'proportion': 0.20  # Higher proportion due to water scarcity
    },
    'Planter': {
        'prefix': 'PLT',
        'brands': ['Massey Ferguson', 'Gaspardo', 'Monosem', 'Amazone'],
        'models': ['MF 500', 'SP 8', 'NG Plus', 'ED 602-K'],
        'purchase_cost_range': (35000, 90000),  # TND
        'annual_hours_range': (80, 200),  # Seasonal planting
        'proportion': 0.12
    },
    'Sprayer': {
        'prefix': 'SPR',
        'brands': ['Hardi', 'Kuhn', 'Amazone', 'Berthoud'],
        'models': ['Commander 4400', 'Deltis 1302', 'UX 5201', 'Boxer 2000'],
        'purchase_cost_range': (120000, 280000),  # TND
        'annual_hours_range': (120, 300),
        'proportion': 0.08
    }
}

# Maintenance configuration
# Adjusted proportions for realistic Tunisian farm operations
MAINTENANCE_TYPES = {
    1: {'name': 'Preventive', 'proportion': 0.40},  # Increased preventive (goal)
    2: {'name': 'Corrective', 'proportion': 0.50},  # Still majority but reduced
    3: {'name': 'Predictive', 'proportion': 0.10}   # Emerging practice
}

# Annual maintenance frequency by equipment type
# Optimized for realistic Tunisian agricultural usage
MAINTENANCE_FREQUENCY = {
    'Tractor': (4, 6),  # 4-6 times per year (high usage)
    'Harvester': (3, 5),  # 3-5 times (seasonal intensive use)
    'Irrigation System': (5, 8),  # 5-8 times (critical, high maintenance)
    'Planter': (2, 4),  # 2-4 times (seasonal use)
    'Sprayer': (3, 5)   # 3-5 times (regular use)
}

# Maintenance cost parameters (mean, std) - log-normal distribution
MAINTENANCE_COST_PARAMS = {
    'Preventive': (250, 150),
    'Corrective': (600, 400),
    'Predictive': (400, 250)
}

# Downtime hours for maintenance (mean, std)
MAINTENANCE_DOWNTIME = {
    'Preventive': (2, 1),
    'Corrective': (6, 3),
    'Predictive': (3, 1.5)
}

# Failure configuration
FAILURE_TYPES = {
    'Engine': {'proportion': 0.25, 'severity_dist': {'Minor': 0.5, 'Moderate': 0.35, 'Critical': 0.15}},
    'Hydraulic': {'proportion': 0.20, 'severity_dist': {'Minor': 0.6, 'Moderate': 0.30, 'Critical': 0.10}},
    'Electrical': {'proportion': 0.15, 'severity_dist': {'Minor': 0.7, 'Moderate': 0.25, 'Critical': 0.05}},
    'Mechanical': {'proportion': 0.15, 'severity_dist': {'Minor': 0.5, 'Moderate': 0.40, 'Critical': 0.10}},
    'Tire': {'proportion': 0.15, 'severity_dist': {'Minor': 0.8, 'Moderate': 0.15, 'Critical': 0.05}},
    'Belt': {'proportion': 0.05, 'severity_dist': {'Minor': 0.7, 'Moderate': 0.25, 'Critical': 0.05}},
    'Other': {'proportion': 0.05, 'severity_dist': {'Minor': 0.6, 'Moderate': 0.30, 'Critical': 0.10}}
}

# Failure frequency (failures per year per equipment)
# Adjusted for Tunisian climate and usage patterns
FAILURE_RATE = {
    'Tractor': (0.8, 2.0),  # Higher due to intensive use
    'Harvester': (1.0, 2.5),  # High stress during harvest season
    'Irrigation System': (1.2, 3.0),  # High usage, water quality issues
    'Planter': (0.5, 1.5),  # Seasonal, moderate failures
    'Sprayer': (0.7, 1.8)   # Chemical exposure, moderate failures
}

# Failure cost and downtime by severity
FAILURE_PARAMS = {
    'Minor': {
        'cost': (200, 500),
        'downtime': (2, 6)
    },
    'Moderate': {
        'cost': (500, 2000),
        'downtime': (6, 24)
    },
    'Critical': {
        'cost': (2000, 10000),
        'downtime': (24, 120)
    }
}

# Seasonal patterns - Adapted for Tunisian agricultural calendar
# Higher values = more activity
# Tunisia: Cereals (wheat, barley) planted Oct-Dec, harvested May-Jun
#          Olives harvested Nov-Jan, Citrus year-round
SEASONAL_MAINTENANCE = {
    1: 1.2,   # January - Post-olive harvest maintenance
    2: 1.4,   # February - Winter maintenance peak
    3: 1.3,   # March - Pre-planting preparation
    4: 0.9,   # April - Spring planting season
    5: 0.7,   # May - Harvest preparation (cereals)
    6: 0.6,   # June - Cereal harvest (busy, less maintenance)
    7: 1.1,   # July - Post-harvest maintenance
    8: 1.2,   # August - Summer maintenance
    9: 1.0,   # September - Pre-planting prep
    10: 0.8,  # October - Autumn planting (cereals)
    11: 0.7,  # November - Planting + olive harvest
    12: 1.1   # December - Winter prep
}

SEASONAL_FAILURES = {
    1: 0.9,   # January - Moderate usage (olive harvest)
    2: 0.7,   # February - Lower usage
    3: 1.1,   # March - Increasing usage (preparation)
    4: 1.3,   # April - Spring work intensifies
    5: 1.6,   # May - Peak usage (cereal harvest prep)
    6: 1.8,   # June - Peak usage (cereal harvest)
    7: 1.4,   # July - High usage (summer crops)
    8: 1.2,   # August - Moderate usage (heat stress on equipment)
    9: 1.1,   # September - Preparation for autumn
    10: 1.4,  # October - Autumn planting (cereals)
    11: 1.5,  # November - Planting + olive harvest
    12: 1.0   # December - Moderate usage
}

# Technician names - Tunisian names
TECHNICIAN_NAMES = [
    'Mohamed Ben Ali', 'Ahmed Trabelsi', 'Karim Hamdi', 'Youssef Gharbi',
    'Mehdi Jebali', 'Bilel Mansouri', 'Rami Bouazizi', 'Sofiane Khelifi',
    'Nabil Chebbi', 'Firas Dridi', 'Walid Sassi', 'Hichem Mejri',
    'Sami Ben Salem', 'Tarek Oueslati', 'Amine Bouzid', 'Maher Agrebi'
]

# Farm locations - Tunisian agricultural regions and field names
FARM_LOCATIONS = [
    'Champ Nord (Béja)',      # North Field (Béja region)
    'Champ Sud (Kairouan)',   # South Field (Kairouan region)
    'Parcelle Est (Jendouba)', # East Field (Jendouba region)
    'Parcelle Ouest (Siliana)', # West Field (Siliana region)
    'Hangar Principal',        # Main Barn
    'Atelier Mécanique',       # Mechanical Workshop
    'Dépôt Matériel',          # Equipment Storage
    'Zone Irrigation (Bizerte)', # Irrigation Zone (Bizerte)
    'Champ Céréales (Manouba)', # Cereals Field (Manouba)
    'Verger (Cap Bon)',        # Orchard (Cap Bon)
    'Oliveraie (Sfax)',        # Olive Grove (Sfax)
    'Serre (Nabeul)'           # Greenhouse (Nabeul)
]

# Equipment status
EQUIPMENT_STATUS = ['Active', 'Under Maintenance', 'Retired']

# Age distribution parameters (years)
EQUIPMENT_AGE_MEAN = 8
EQUIPMENT_AGE_STD = 4
EQUIPMENT_AGE_MIN = 1
EQUIPMENT_AGE_MAX = 20
