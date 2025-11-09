"""
Stage 4: Decision Engine
Assign priority levels and generate maintenance recommendations
"""

import pandas as pd
from datetime import datetime, timedelta
import sys
sys.path.append('..')
from config import RISK_THRESHOLDS

def assign_priority(risk_score):
    """Assign priority level based on risk score"""
    if risk_score >= RISK_THRESHOLDS['critical']:
        return 'Critical'
    elif risk_score >= RISK_THRESHOLDS['high']:
        return 'High'
    elif risk_score >= RISK_THRESHOLDS['medium']:
        return 'Medium'
    else:
        return 'Low'

def generate_recommendation(priority, equipment_type):
    """Generate maintenance recommendation based on priority"""
    recommendations = {
        'Critical': f'URGENT: Schedule immediate maintenance for {equipment_type}. High failure risk detected.',
        'High': f'Schedule maintenance within 1 week for {equipment_type}. Elevated failure risk.',
        'Medium': f'Schedule maintenance within 2 weeks for {equipment_type}. Moderate risk detected.',
        'Low': f'Monitor {equipment_type} closely. Maintenance can be scheduled during regular intervals.'
    }
    return recommendations.get(priority, 'Monitor equipment status.')

def calculate_scheduled_date(priority):
    """Calculate recommended maintenance date based on priority"""
    today = datetime.now().date()
    
    schedule_days = {
        'Critical': 1,   # Tomorrow
        'High': 7,       # Within 1 week
        'Medium': 14,    # Within 2 weeks
        'Low': 30        # Within 1 month
    }
    
    days = schedule_days.get(priority, 30)
    return today + timedelta(days=days)

def run_stage4(data):
    """Execute Stage 4: Decision Engine"""
    print("\n" + "="*60)
    print("STAGE 4: DECISION ENGINE")
    print("="*60)
    
    try:
        predictions_df = data['predictions'].copy()
        
        print(" Assigning priority levels...")
        
        # Assign priorities
        predictions_df['priority_level'] = predictions_df['risk_score'].apply(assign_priority)
        
        # Check if equipment_type column exists
        if 'equipment_type' not in predictions_df.columns:
            print("\n[WARN] 'equipment_type' column not found, using generic equipment type")
            # Add a generic equipment type
            predictions_df['equipment_type'] = 'equipment'
        
        # Generate recommendations
        predictions_df['recommended_action'] = predictions_df.apply(
            lambda row: generate_recommendation(row['priority_level'], row['equipment_type']),
            axis=1
        )
        
        # Calculate scheduled dates
        predictions_df['recommended_date'] = predictions_df['priority_level'].apply(calculate_scheduled_date)
        
        # Count by priority
        priority_counts = predictions_df['priority_level'].value_counts()
        
        print(f"\n[COMPLETE] Stage 4 Complete!")
        print(f"   Priority distribution:")
        for priority in ['Critical', 'High', 'Medium', 'Low']:
            count = priority_counts.get(priority, 0)
            print(f"      {priority}: {count} equipment")
        
        return {
            'decisions': predictions_df
        }
        
    except Exception as e:
        print(f"[ERROR] Error in Stage 4: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    # Test stage 4
    from stage1_data_ingestion import run_stage1
    from stage2_feature_engineering import run_stage2
    from stage3_model_prediction import run_stage3
    
    data = run_stage1()
    features = run_stage2(data)
    predictions = run_stage3(features)
    decisions = run_stage4(predictions)
    
    print(f"\nDecisions sample:")
    print(decisions['decisions'][['equipment_id', 'risk_score', 'priority_level', 'recommended_date']].head(10))
