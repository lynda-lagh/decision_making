"""
Stage 6: Enhanced Storage & Output
Save predictions, recommendations, and KPIs to PostgreSQL
"""

import pandas as pd
import psycopg2
from datetime import datetime
import sys
sys.path.append('..')
from config import DB_CONFIG

def save_predictions_to_db(predictions_df):
    """
    Save predictions to predictions table
    
    Args:
        predictions_df: DataFrame with predictions
    
    Returns:
        int: Number of rows inserted
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        data = []
        for _, row in predictions_df.iterrows():
            data.append((
                row['equipment_id'],
                datetime.now(),
                float(row['failure_probability']),
                int(row['rul_days']),
                float(row['anomaly_score']),
                float(row['confidence_score']),
                'v1.0'
            ))
        
        query = """
        INSERT INTO predictions 
        (equipment_id, prediction_date, failure_probability, rul_days, 
         anomaly_score, confidence_score, model_version)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        for row_data in data:
            cursor.execute(query, row_data)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"[OK] Saved {len(data)} predictions to database")
        return len(data)
        
    except Exception as e:
        print(f"[ERROR] Failed to save predictions: {e}")
        return 0

def save_recommendations_to_db(decisions_df):
    """
    Save recommendations to recommendations table
    
    Args:
        decisions_df: DataFrame with decisions
    
    Returns:
        int: Number of rows inserted
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        data = []
        for _, row in decisions_df.iterrows():
            data.append((
                row['equipment_id'],
                row['priority_level'],
                row['recommendation_text'],
                float(row['estimated_maintenance_cost']),
                float(row['estimated_failure_cost']),
                row['recommended_action']
            ))
        
        query = """
        INSERT INTO recommendations 
        (equipment_id, priority_level, recommendation_text, 
         estimated_maintenance_cost, estimated_failure_cost, recommended_action)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        for row_data in data:
            cursor.execute(query, row_data)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"[OK] Saved {len(data)} recommendations to database")
        return len(data)
        
    except Exception as e:
        print(f"[ERROR] Failed to save recommendations: {e}")
        return 0

def save_kpis_to_db(equipment_df, decisions_df):
    """
    Save KPIs to kpis table
    
    Args:
        equipment_df: Equipment data
        decisions_df: Decisions with health scores
    
    Returns:
        int: Number of rows inserted
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Calculate health scores
        data = []
        for _, row in decisions_df.iterrows():
            # Health score based on multiple factors
            health_score = (
                (1 - row['failure_probability']) * 40 +  # Lower failure prob = higher health
                (row['rul_days'] / 365) * 30 +  # Longer RUL = higher health
                (1 - row['anomaly_score'] / 100) * 30  # Lower anomalies = higher health
            )
            health_score = max(0, min(100, health_score))
            
            # Reliability score
            reliability_score = (1 - row['failure_probability']) * 100
            
            # Availability status
            if row['priority_level'] == 'CRITICAL':
                availability = 'At Risk'
            elif row['priority_level'] == 'HIGH':
                availability = 'Degraded'
            elif row['priority_level'] == 'MEDIUM':
                availability = 'Caution'
            else:
                availability = 'Operational'
            
            data.append((
                row['equipment_id'],
                health_score,
                reliability_score,
                availability,
                0.0,  # MTBF (would calculate from history)
                0.0,  # MTTR (would calculate from history)
                datetime.now()
            ))
        
        query = """
        INSERT INTO kpis 
        (equipment_id, health_score, reliability_score, availability_status, 
         mtbf_hours, mttr_hours, calculated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        for row_data in data:
            cursor.execute(query, row_data)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"[OK] Saved {len(data)} KPIs to database")
        return len(data)
        
    except Exception as e:
        print(f"[ERROR] Failed to save KPIs: {e}")
        return 0

def generate_summary_report(decisions_df):
    """
    Generate summary report
    
    Args:
        decisions_df: Decisions dataframe
    
    Returns:
        dict: Summary statistics
    """
    report = {
        'total_equipment': len(decisions_df),
        'critical_count': len(decisions_df[decisions_df['priority_level'] == 'CRITICAL']),
        'high_count': len(decisions_df[decisions_df['priority_level'] == 'HIGH']),
        'medium_count': len(decisions_df[decisions_df['priority_level'] == 'MEDIUM']),
        'low_count': len(decisions_df[decisions_df['priority_level'] == 'LOW']),
        'normal_count': len(decisions_df[decisions_df['priority_level'] == 'NORMAL']),
        'total_maintenance_cost': decisions_df['estimated_maintenance_cost'].sum(),
        'total_failure_cost': decisions_df['estimated_failure_cost'].sum(),
        'total_net_benefit': decisions_df['net_benefit'].sum(),
        'avg_failure_probability': decisions_df['failure_probability'].mean(),
        'avg_rul_days': decisions_df['rul_days'].mean(),
        'avg_risk_score': decisions_df['risk_score'].mean(),
        'avg_roi': decisions_df['roi'].mean()
    }
    
    return report

def run_stage6(kpis_data):
    """Execute Stage 6: Enhanced Storage & Output"""
    print("\n" + "="*60)
    print("STAGE 6: STORAGE & OUTPUT")
    print("="*60)
    
    try:
        decisions_df = kpis_data['decisions']
        
        # Step 1: Save predictions
        print("\n[STEP 1] Saving predictions...")
        predictions_saved = save_predictions_to_db(decisions_df)
        
        # Step 2: Save recommendations
        print("[STEP 2] Saving recommendations...")
        recommendations_saved = save_recommendations_to_db(decisions_df)
        
        # Step 3: Save KPIs
        print("[STEP 3] Saving KPIs...")
        kpis_saved = save_kpis_to_db(decisions_df, decisions_df)
        
        # Step 4: Generate report
        print("[STEP 4] Generating summary report...")
        report = generate_summary_report(decisions_df)
        
        # Summary
        print(f"\n[COMPLETE] Stage 6 Complete!")
        print(f"   Predictions saved: {predictions_saved}")
        print(f"   Recommendations saved: {recommendations_saved}")
        print(f"   KPIs saved: {kpis_saved}")
        print(f"\n[SUMMARY]")
        print(f"   Total equipment: {report['total_equipment']}")
        print(f"   Critical: {report['critical_count']}")
        print(f"   High: {report['high_count']}")
        print(f"   Medium: {report['medium_count']}")
        print(f"   Low: {report['low_count']}")
        print(f"   Normal: {report['normal_count']}")
        print(f"   Total maintenance cost: ${report['total_maintenance_cost']:.2f}")
        print(f"   Total failure cost: ${report['total_failure_cost']:.2f}")
        print(f"   Expected net benefit: ${report['total_net_benefit']:.2f}")
        print(f"   Average ROI: {report['avg_roi']:.1f}%")
        
        return {
            'success': True,
            'predictions_saved': predictions_saved,
            'recommendations_saved': recommendations_saved,
            'kpis_saved': kpis_saved,
            'report': report
        }
        
    except Exception as e:
        print(f"[ERROR] Stage 6 failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    from stage4_risk_scoring import run_stage4
    from stage3_ensemble_prediction import run_stage3
    from stage2_enhanced_features import run_stage2
    from stage1_data_ingestion import run_stage1
    
    data = run_stage1()
    features_data = run_stage2(data)
    predictions_data = run_stage3(features_data)
    decisions_data = run_stage4(predictions_data)
    
    result = run_stage6(decisions_data)
    print(f"\nStorage result: {result}")
