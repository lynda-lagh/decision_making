"""
Stage 4: Decision Engine with Risk Scoring
Combines predictions into actionable maintenance recommendations
"""

import pandas as pd
import numpy as np
import sys
sys.path.append('..')
from sensor_config import DECISION_THRESHOLDS, RISK_SCORING_WEIGHTS

def calculate_rul_criticality(rul_days):
    """
    Convert RUL days to criticality score (0-100)
    
    Args:
        rul_days: Days until failure
    
    Returns:
        float: Criticality score (0-100)
    """
    if rul_days <= 3:
        return 100
    elif rul_days <= 7:
        return 75
    elif rul_days <= 30:
        return 50
    elif rul_days <= 90:
        return 25
    else:
        return 0

def calculate_risk_score(failure_prob, rul_days, anomaly_score):
    """
    Calculate composite risk score using weighted ensemble
    
    Args:
        failure_prob: Failure probability (0-1)
        rul_days: Days until failure
        anomaly_score: Anomaly score (0-100)
    
    Returns:
        float: Risk score (0-100)
    """
    # Convert inputs to 0-100 scale
    failure_prob_score = failure_prob * 100
    rul_criticality = calculate_rul_criticality(rul_days)
    
    # Apply weights
    risk_score = (
        failure_prob_score * RISK_SCORING_WEIGHTS['failure_probability'] +
        rul_criticality * RISK_SCORING_WEIGHTS['rul_criticality'] +
        anomaly_score * RISK_SCORING_WEIGHTS['anomaly_score']
    )
    
    return np.clip(risk_score, 0, 100)

def assign_priority_level(failure_prob, rul_days):
    """
    Assign priority level based on thresholds
    
    Args:
        failure_prob: Failure probability (0-1)
        rul_days: Days until failure
    
    Returns:
        str: Priority level (CRITICAL, HIGH, MEDIUM, LOW, NORMAL)
    """
    thresholds = DECISION_THRESHOLDS
    
    if failure_prob > thresholds['critical']['failure_prob'] and rul_days < thresholds['critical']['rul_days']:
        return 'CRITICAL'
    elif failure_prob > thresholds['high']['failure_prob'] and rul_days < thresholds['high']['rul_days']:
        return 'HIGH'
    elif failure_prob > thresholds['medium']['failure_prob'] and rul_days < thresholds['medium']['rul_days']:
        return 'MEDIUM'
    elif failure_prob > thresholds['low']['failure_prob']:
        return 'LOW'
    else:
        return 'NORMAL'

def get_maintenance_recommendation(priority_level, failure_prob, rul_days, equipment_type):
    """
    Generate maintenance recommendation based on priority
    
    Args:
        priority_level: Priority level
        failure_prob: Failure probability
        rul_days: Days until failure
        equipment_type: Type of equipment
    
    Returns:
        str: Maintenance recommendation
    """
    recommendations = {
        'CRITICAL': f'URGENT: Immediate maintenance required. Equipment failure imminent ({failure_prob*100:.0f}% probability in {rul_days} days). Perform emergency inspection and repair.',
        'HIGH': f'Schedule maintenance within 7 days. High failure risk ({failure_prob*100:.0f}% probability). Estimated RUL: {rul_days} days.',
        'MEDIUM': f'Plan maintenance within 30 days. Moderate failure risk ({failure_prob*100:.0f}% probability). Estimated RUL: {rul_days} days.',
        'LOW': f'Monitor closely. Low failure risk ({failure_prob*100:.0f}% probability). Continue normal operation.',
        'NORMAL': f'No action required. Equipment operating normally. Continue regular maintenance schedule.'
    }
    
    return recommendations.get(priority_level, 'Unknown priority level')

def estimate_maintenance_cost(priority_level, equipment_type):
    """
    Estimate maintenance cost based on priority
    
    Args:
        priority_level: Priority level
        equipment_type: Type of equipment
    
    Returns:
        float: Estimated cost in currency units
    """
    base_costs = {
        'CRITICAL': 1000,
        'HIGH': 500,
        'MEDIUM': 300,
        'LOW': 150,
        'NORMAL': 0
    }
    
    # Adjust based on equipment type (example)
    type_multipliers = {
        'Excavator': 1.5,
        'Bulldozer': 1.4,
        'Loader': 1.2,
        'Grader': 1.1,
        'Compactor': 1.0,
        'Drill': 1.3,
        'Pump': 0.8,
        'Generator': 1.2
    }
    
    base_cost = base_costs.get(priority_level, 0)
    multiplier = type_multipliers.get(equipment_type, 1.0)
    
    return base_cost * multiplier

def estimate_failure_cost(priority_level, equipment_type, operating_hours=None):
    """
    Estimate cost of failure if not maintained
    
    Args:
        priority_level: Priority level
        equipment_type: Type of equipment
        operating_hours: Annual operating hours
    
    Returns:
        float: Estimated failure cost
    """
    # Base failure costs (repair + downtime + lost production)
    base_failure_costs = {
        'CRITICAL': 5000,
        'HIGH': 3000,
        'MEDIUM': 1500,
        'LOW': 500,
        'NORMAL': 0
    }
    
    type_multipliers = {
        'Excavator': 2.0,
        'Bulldozer': 1.8,
        'Loader': 1.5,
        'Grader': 1.3,
        'Compactor': 1.2,
        'Drill': 1.6,
        'Pump': 1.0,
        'Generator': 1.4
    }
    
    base_cost = base_failure_costs.get(priority_level, 0)
    multiplier = type_multipliers.get(equipment_type, 1.0)
    
    return base_cost * multiplier

def cost_benefit_analysis(maintenance_cost, failure_cost, failure_prob):
    """
    Perform cost-benefit analysis
    
    Args:
        maintenance_cost: Cost of preventive maintenance
        failure_cost: Cost of failure if not maintained
        failure_prob: Probability of failure
    
    Returns:
        dict: Analysis results
    """
    expected_failure_cost = failure_cost * failure_prob
    net_benefit = expected_failure_cost - maintenance_cost
    roi = (net_benefit / maintenance_cost * 100) if maintenance_cost > 0 else 0
    
    should_maintain = expected_failure_cost > maintenance_cost
    
    return {
        'maintenance_cost': maintenance_cost,
        'failure_cost': failure_cost,
        'expected_failure_cost': expected_failure_cost,
        'net_benefit': net_benefit,
        'roi': roi,
        'should_maintain': should_maintain
    }

def run_stage4(predictions_data):
    """Execute Stage 4: Decision Engine"""
    print("\n" + "="*60)
    print("STAGE 4: DECISION ENGINE - RISK SCORING & RECOMMENDATIONS")
    print("="*60)
    
    predictions_df = predictions_data['predictions'].copy()
    
    # Step 1: Calculate risk scores
    print("\n[STEP 1] Calculating risk scores...")
    predictions_df['risk_score'] = predictions_df.apply(
        lambda row: calculate_risk_score(
            row['failure_probability'],
            row['rul_days'],
            row['anomaly_score']
        ),
        axis=1
    )
    print(f"   Risk scores calculated")
    print(f"   Avg risk score: {predictions_df['risk_score'].mean():.1f}/100")
    
    # Step 2: Assign priority levels
    print("\n[STEP 2] Assigning priority levels...")
    predictions_df['priority_level'] = predictions_df.apply(
        lambda row: assign_priority_level(
            row['failure_probability'],
            row['rul_days']
        ),
        axis=1
    )
    
    priority_counts = predictions_df['priority_level'].value_counts()
    print(f"   Priority distribution:")
    for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'NORMAL']:
        count = priority_counts.get(priority, 0)
        print(f"     {priority}: {count} equipment")
    
    # Step 3: Generate recommendations
    print("\n[STEP 3] Generating maintenance recommendations...")
    predictions_df['recommendation_text'] = predictions_df.apply(
        lambda row: get_maintenance_recommendation(
            row['priority_level'],
            row['failure_probability'],
            row['rul_days'],
            row['equipment_type']
        ),
        axis=1
    )
    
    # Step 4: Estimate costs
    print("\n[STEP 4] Estimating maintenance and failure costs...")
    predictions_df['estimated_maintenance_cost'] = predictions_df.apply(
        lambda row: estimate_maintenance_cost(
            row['priority_level'],
            row['equipment_type']
        ),
        axis=1
    )
    
    predictions_df['estimated_failure_cost'] = predictions_df.apply(
        lambda row: estimate_failure_cost(
            row['priority_level'],
            row['equipment_type']
        ),
        axis=1
    )
    
    # Step 5: Cost-benefit analysis
    print("\n[STEP 5] Performing cost-benefit analysis...")
    cba_results = predictions_df.apply(
        lambda row: cost_benefit_analysis(
            row['estimated_maintenance_cost'],
            row['estimated_failure_cost'],
            row['failure_probability']
        ),
        axis=1,
        result_type='expand'
    )
    
    predictions_df = pd.concat([predictions_df, cba_results], axis=1)
    
    # Step 6: Determine recommended action
    print("\n[STEP 6] Determining recommended actions...")
    predictions_df['recommended_action'] = predictions_df.apply(
        lambda row: 'PERFORM_MAINTENANCE' if row['should_maintain'] else 'MONITOR',
        axis=1
    )
    
    # Summary
    print(f"\n[COMPLETE] Stage 4 Complete!")
    print(f"   Decisions generated: {len(predictions_df)}")
    print(f"   Total maintenance cost: ${predictions_df['estimated_maintenance_cost'].sum():.2f}")
    print(f"   Total failure cost (if not maintained): ${predictions_df['estimated_failure_cost'].sum():.2f}")
    print(f"   Expected net benefit: ${predictions_df['net_benefit'].sum():.2f}")
    print(f"   Avg ROI: {predictions_df['roi'].mean():.1f}%")
    
    # Show top critical equipment
    critical_equipment = predictions_df[predictions_df['priority_level'] == 'CRITICAL'].sort_values('risk_score', ascending=False)
    if len(critical_equipment) > 0:
        print(f"\n   Top CRITICAL equipment:")
        for idx, row in critical_equipment.head(3).iterrows():
            print(f"     - {row['equipment_id']}: Risk {row['risk_score']:.0f}/100, RUL {row['rul_days']} days")
    
    return {
        'success': True,
        'decisions': predictions_df,
        'summary': {
            'total_equipment': len(predictions_df),
            'critical_count': len(predictions_df[predictions_df['priority_level'] == 'CRITICAL']),
            'high_count': len(predictions_df[predictions_df['priority_level'] == 'HIGH']),
            'total_maintenance_cost': predictions_df['estimated_maintenance_cost'].sum(),
            'total_failure_cost': predictions_df['estimated_failure_cost'].sum(),
            'expected_net_benefit': predictions_df['net_benefit'].sum()
        }
    }

if __name__ == "__main__":
    from stage3_ensemble_prediction import run_stage3
    from stage2_enhanced_features import run_stage2
    from stage1_data_ingestion import run_stage1
    
    data = run_stage1()
    features_data = run_stage2(data)
    predictions_data = run_stage3(features_data)
    result = run_stage4(predictions_data)
    
    print(f"\nDecisions sample:")
    print(result['decisions'][['equipment_id', 'priority_level', 'risk_score', 'rul_days']].head())
