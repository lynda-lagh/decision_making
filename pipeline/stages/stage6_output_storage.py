"""
Stage 6: Output & Storage
Save predictions, maintenance schedule, and KPIs to PostgreSQL database
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, date
import sys
import random
sys.path.append('..')
from config import DB_CONFIG, TECHNICIANS, ESTIMATED_COSTS, ESTIMATED_DURATION

def save_predictions(conn, predictions_df):
    """Save predictions to database"""
    print("[SAVE] Saving predictions to database...")
    
    try:
        cursor = conn.cursor()
        
        # Clear existing predictions for today
        cursor.execute("DELETE FROM predictions WHERE prediction_date = CURRENT_DATE")
        
        # Prepare data
        values = [
            (
                row['equipment_id'],
                date.today(),
                int(row['svm_prediction']) if pd.notna(row['svm_prediction']) else 0,
                float(row['svm_probability']) if pd.notna(row['svm_probability']) else 0.0,
                int(row['xgb_prediction']) if pd.notna(row['xgb_prediction']) else 0,
                float(row['xgb_probability']) if pd.notna(row['xgb_probability']) else 0.0,
                float(row['risk_score']),
                row['priority_level'],
                row['recommended_action']
            )
            for _, row in predictions_df.iterrows()
        ]
        
        # Insert predictions
        insert_query = """
        INSERT INTO predictions (
            equipment_id, prediction_date, svm_prediction, svm_probability,
            xgb_prediction, xgb_probability, risk_score, priority, recommended_action
        ) VALUES %s
        """
        
        execute_values(cursor, insert_query, values)
        conn.commit()
        
        print(f"   [OK] Saved {len(predictions_df)} predictions")
        
    except Exception as e:
        print(f"   [ERROR] Error saving predictions: {e}")
        conn.rollback()
        raise

def save_maintenance_schedule(conn, predictions_df):
    """Generate and save maintenance schedule"""
    print("[SAVE] Generating maintenance schedule...")
    
    try:
        cursor = conn.cursor()
        
        # Clear existing schedule for future dates
        cursor.execute("DELETE FROM maintenance_schedule WHERE scheduled_date >= CURRENT_DATE AND status = 'Scheduled'")
        
        # Generate schedule for high-risk equipment
        high_risk = predictions_df[predictions_df['risk_score'] > 20].copy()
        
        values = [
            (
                row['equipment_id'],
                row['recommended_date'],
                row['priority_level'],
                ESTIMATED_COSTS.get(row['priority_level'], 250.0),
                ESTIMATED_DURATION.get(row['priority_level'], 2.0),
                random.choice(TECHNICIANS),
                'Scheduled'
            )
            for _, row in high_risk.iterrows()
        ]
        
        # Insert schedule
        insert_query = """
        INSERT INTO maintenance_schedule (
            equipment_id, scheduled_date, priority, estimated_cost, estimated_duration,
            assigned_technician, status
        ) VALUES %s
        """
        
        execute_values(cursor, insert_query, values)
        conn.commit()
        
        print(f"   [OK] Generated {len(high_risk)} maintenance tasks")
        
    except Exception as e:
        print(f"   [ERROR] Error saving schedule: {e}")
        conn.rollback()
        raise

def save_kpis(conn, kpis_dict):
    """Save KPIs to database"""
    print("[SAVE] Saving KPIs to database...")
    
    try:
        cursor = conn.cursor()
        
        # Clear existing KPIs for today
        cursor.execute("DELETE FROM kpi_metrics WHERE calculation_date::date = CURRENT_DATE")
        
        # Prepare KPI data
        values = [
            (
                kpi_name,
                float(kpi_data['value']),
                None,  # target_value
                None,  # unit
                kpi_data['category']
            )
            for kpi_name, kpi_data in kpis_dict.items()
        ]
        
        # Insert KPIs
        insert_query = """
        INSERT INTO kpi_metrics (
            metric_name, metric_value, target_value, unit, category
        ) VALUES %s
        """
        
        execute_values(cursor, insert_query, values)
        conn.commit()
        
        print(f"   [OK] Saved {len(kpis_dict)} KPIs")
        
    except Exception as e:
        print(f"   [ERROR] Error saving KPIs: {e}")
        conn.rollback()
        raise

def run_stage6(data):
    """Execute Stage 6: Output & Storage"""
    print("\n" + "="*60)
    print("STAGE 6: OUTPUT & STORAGE")
    print("="*60)
    
    try:
        decisions_df = data['decisions']
        kpis_dict = data['kpis']
        
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        print("[OK] Connected to PostgreSQL database")
        
        # Save all data
        save_predictions(conn, decisions_df)
        save_maintenance_schedule(conn, decisions_df)
        save_kpis(conn, kpis_dict)
        
        # Close connection
        conn.close()
        
        print(f"\n[COMPLETE] Stage 6 Complete!")
        print(f"   All data saved to database successfully")
        
        return {
            'success': True,
            'predictions_saved': len(decisions_df),
            'kpis_saved': len(kpis_dict)
        }
        
    except Exception as e:
        print(f"[ERROR] Error in Stage 6: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    # Test stage 6
    from stage1_data_ingestion import run_stage1
    from stage2_feature_engineering import run_stage2
    from stage3_model_prediction import run_stage3
    from stage4_decision_engine import run_stage4
    from stage5_kpi_calculation import run_stage5
    
    data = run_stage1()
    features = run_stage2(data)
    predictions = run_stage3(features)
    decisions = run_stage4(predictions)
    
    # Add original data for KPI calculation
    decisions['maintenance'] = data['maintenance']
    decisions['failures'] = data['failures']
    decisions['models'] = predictions.get('models', {})
    
    kpis = run_stage5(decisions)
    result = run_stage6(kpis)
    
    print(f"\nPipeline complete!")
    print(f"   Predictions saved: {result['predictions_saved']}")
    print(f"   KPIs saved: {result['kpis_saved']}")
