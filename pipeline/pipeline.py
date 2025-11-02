"""
WeeFarm ML Pipeline - Main Orchestrator
Runs all 6 stages of the predictive maintenance pipeline
"""

import time
from datetime import datetime
from stages.stage1_data_ingestion import run_stage1
from stages.stage2_feature_engineering import run_stage2
from stages.stage3_model_prediction import run_stage3
from stages.stage4_decision_engine import run_stage4
from stages.stage5_kpi_calculation import run_stage5
from stages.stage6_output_storage import run_stage6
from config import PIPELINE_NAME, PIPELINE_VERSION

def run_pipeline():
    """Execute complete ML pipeline"""
    
    print("\n" + "="*70)
    print(f"[START] {PIPELINE_NAME}")
    print(f"   Version: {PIPELINE_VERSION}")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    start_time = time.time()
    
    try:
        # Stage 1: Data Ingestion
        print("\n[STAGE 1] Running Data Ingestion...")
        data = run_stage1()
        
        # Stage 2: Feature Engineering
        print("\n[STAGE 2] Running Feature Engineering...")
        features = run_stage2(data)
        
        # Stage 3: Model Prediction
        print("\n[STAGE 3] Running Model Prediction...")
        predictions = run_stage3(features)
        
        # Stage 4: Decision Engine
        print("\n[STAGE 4] Running Decision Engine...")
        decisions = run_stage4(predictions)
        
        # Stage 5: KPI Calculation
        print("\n[STAGE 5] Running KPI Calculation...")
        # Add original data for KPI calculation
        decisions['maintenance'] = data['maintenance']
        decisions['failures'] = data['failures']
        decisions['models'] = predictions.get('models', {})
        kpis = run_stage5(decisions)
        
        # Stage 6: Output & Storage
        print("\n[STAGE 6] Running Output & Storage...")
        result = run_stage6(kpis)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Print summary
        print("\n" + "="*70)
        print("[SUCCESS] PIPELINE EXECUTION COMPLETE!")
        print("="*70)
        print(f"\n[SUMMARY]")
        print(f"   Equipment analyzed: {len(data['equipment'])}")
        print(f"   Predictions generated: {result['predictions_saved']}")
        print(f"   KPIs calculated: {result['kpis_saved']}")
        print(f"   Execution time: {execution_time:.2f} seconds")
        print(f"   Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Priority breakdown
        decisions_df = kpis['decisions']
        priority_counts = decisions_df['priority_level'].value_counts()
        
        print(f"\n[PRIORITY BREAKDOWN]")
        for priority in ['Critical', 'High', 'Medium', 'Low']:
            count = priority_counts.get(priority, 0)
            print(f"   {priority}: {count} equipment")
        
        # KPI status breakdown
        kpis_dict = kpis['kpis']
        status_counts = {}
        for kpi in kpis_dict.values():
            status = kpi['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n[KPI STATUS]")
        for status in ['Excellent', 'Good', 'Warning', 'Critical']:
            count = status_counts.get(status, 0)
            if count > 0:
                print(f"   {status}: {count} KPIs")
        
        print("\n" + "="*70)
        print("[COMPLETE] All data saved to database successfully!")
        print("   Ready for API and Dashboard access")
        print("="*70 + "\n")
        
        return {
            'success': True,
            'execution_time': execution_time,
            'equipment_count': len(data['equipment']),
            'predictions_count': result['predictions_saved'],
            'kpis_count': result['kpis_saved']
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        print("\n" + "="*70)
        print("[ERROR] PIPELINE EXECUTION FAILED!")
        print("="*70)
        print(f"\nError: {e}")
        print(f"Execution time before failure: {execution_time:.2f} seconds")
        print("\n" + "="*70 + "\n")
        
        import traceback
        traceback.print_exc()
        
        return {
            'success': False,
            'error': str(e),
            'execution_time': execution_time
        }

if __name__ == "__main__":
    result = run_pipeline()
    
    if result['success']:
        print(f"[OK] Pipeline completed successfully in {result['execution_time']:.2f} seconds")
    else:
        print(f"[FAILED] Pipeline failed after {result['execution_time']:.2f} seconds")
        print(f"   Error: {result['error']}")
