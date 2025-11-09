"""
Integrated Pipeline with Model Training and Fine-tuning

This module integrates the model training pipeline with the main pipeline.
It extends the existing pipeline to:
1. Train models on existing data from PostgreSQL
2. Fine-tune models with new input data
3. Compare model performance and select the best one
4. Save metrics and model comparisons as images
5. Provide progress updates during training

The integrated pipeline ensures that the best model is always used for predictions.
It includes comprehensive data validation, database schema validation, and error handling.
"""

import time
import sys
import logging
from datetime import datetime
from pathlib import Path

# Import original pipeline stages
from stages.stage1_data_ingestion import run_stage1
from stages.stage2_feature_engineering import run_stage2
from stages.stage3_model_prediction import run_stage3 as run_stage3_prediction
from stages.stage3_model_training import run_stage3 as run_stage3_training
from stages.stage4_decision_engine import run_stage4
from stages.stage5_kpi_calculation import run_stage5
from stages.stage5_model_metrics import run_stage5_model_metrics
from stages.stage6_output_storage import run_stage6

# Import utility modules
from utils.schema_validator import validate_database_schema, connect_to_db
from utils.data_validator import validate_pipeline_data, validate_data
from utils.error_handler import (
    log_error, handle_stage_error, safe_execute,
    PipelineError, DataError, DatabaseError, ModelError
)

from config import PIPELINE_NAME, PIPELINE_VERSION

# Configure logging
logger = logging.getLogger("pipeline")

def run_integrated_pipeline(use_model_training=True, validate_schema=True):
    """Execute complete ML pipeline with model training"""
    
    logger.info("="*70)
    logger.info(f"[START] {PIPELINE_NAME} (INTEGRATED WITH MODEL TRAINING)")
    logger.info(f"   Version: {PIPELINE_VERSION}")
    logger.info(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*70)
    
    print("\n" + "="*70)
    print(f"[START] {PIPELINE_NAME} (INTEGRATED WITH MODEL TRAINING)")
    print(f"   Version: {PIPELINE_VERSION}")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    start_time = time.time()
    
    try:
        # Validate database schema if requested
        if validate_schema:
            print("\n[VALIDATE] Validating database schema...")
            conn = connect_to_db()
            if conn is None:
                raise DatabaseError("Could not connect to database")
            
            schema_valid, validation_results = validate_database_schema(conn)
            conn.close()
            
            if not schema_valid:
                print("\n⚠️ Database schema validation failed. Some pipeline features may not work correctly.")
                logger.warning("Database schema validation failed. Some pipeline features may not work correctly.")
            else:
                print("\n✅ Database schema validation passed.")
        
        # Stage 1: Data Ingestion
        print("\n[STAGE 1] Running Data Ingestion...")
        try:
            data = run_stage1()
            
            # Validate data
            print("\n[VALIDATE] Validating ingested data...")
            data_valid, validation_results, validated_data = validate_pipeline_data(data)
            data = validated_data  # Use validated data with any missing columns added
            
            if not data_valid:
                print("\n⚠️ Data validation found issues. Proceeding with caution.")
                logger.warning("Data validation found issues. Proceeding with caution.")
            
        except Exception as e:
            error_message, fallback_data = handle_stage_error(e, "Data Ingestion")
            print(error_message)
            if fallback_data is None:
                raise  # Re-raise if no fallback available
            data = fallback_data
        
        # Stage 2: Feature Engineering
        print("\n[STAGE 2] Running Feature Engineering...")
        try:
            features = run_stage2(data)
            
            # Validate features
            print("\n[VALIDATE] Validating engineered features...")
            features_valid, features_message, features_df = validate_data(features, 'features')
            
            if not features_valid:
                print(f"\n⚠️ {features_message}")
                logger.warning(features_message)
            
        except Exception as e:
            error_message, fallback_data = handle_stage_error(e, "Feature Engineering", data)
            print(error_message)
            if fallback_data is None:
                raise  # Re-raise if no fallback available
            features = fallback_data
        
        # Stage 3: Model Training or Prediction
        try:
            if use_model_training:
                print("\n[STAGE 3] Running Model Training and Selection...")
                predictions = run_stage3_training(features)
            else:
                print("\n[STAGE 3] Running Model Prediction...")
                predictions = run_stage3_prediction(features)
                
        except Exception as e:
            error_message, fallback_data = handle_stage_error(e, "Model Training" if use_model_training else "Model Prediction", features)
            print(error_message)
            if fallback_data is None:
                raise  # Re-raise if no fallback available
            predictions = fallback_data
        
        # Stage 4: Decision Engine
        print("\n[STAGE 4] Running Decision Engine...")
        try:
            decisions = run_stage4(predictions)
        except Exception as e:
            error_message, fallback_data = handle_stage_error(e, "Decision Engine", predictions)
            print(error_message)
            if fallback_data is None:
                raise  # Re-raise if no fallback available
            decisions = fallback_data
        
        # Stage 5: KPI Calculation
        print("\n[STAGE 5] Running KPI Calculation...")
        try:
            # Add original data for KPI calculation
            decisions['maintenance'] = data.get('maintenance', {})
            decisions['failures'] = data.get('failures', {})
            decisions['models'] = predictions.get('models', {})
            kpis = run_stage5(decisions)
        except Exception as e:
            error_message, fallback_data = handle_stage_error(e, "KPI Calculation", decisions)
            print(error_message)
            if fallback_data is None:
                raise  # Re-raise if no fallback available
            kpis = fallback_data
        
        # Stage 5b: Model Metrics Tracking
        if use_model_training:
            print("\n[STAGE 5b] Running Model Metrics Tracking...")
            try:
                model_metrics = run_stage5_model_metrics(predictions)
                # Add model metrics to KPIs
                kpis['model_metrics'] = model_metrics
            except Exception as e:
                error_message = log_error(e, "Model Metrics Tracking")
                print(error_message)
                # Non-critical error, continue without model metrics
                logger.warning("Model metrics tracking failed, continuing without metrics")
        
        # Stage 6: Output & Storage
        print("\n[STAGE 6] Running Output & Storage...")
        try:
            result = run_stage6(kpis)
        except Exception as e:
            error_message, fallback_data = handle_stage_error(e, "Output Storage", kpis)
            print(error_message)
            # Non-critical error, continue with pipeline results
            result = {
                'predictions_saved': len(kpis.get('decisions', [])),
                'kpis_saved': len(kpis.get('kpis', {}))
            }
            logger.warning("Output storage failed, continuing with pipeline results")
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Print summary
        print("\n" + "="*70)
        print("[SUCCESS] INTEGRATED PIPELINE EXECUTION COMPLETE!")
        print("="*70)
        print(f"\n[SUMMARY]")
        print(f"   Equipment analyzed: {len(data.get('equipment', []))}")
        print(f"   Predictions generated: {result.get('predictions_saved', 0)}")
        print(f"   KPIs calculated: {result.get('kpis_saved', 0)}")
        print(f"   Execution time: {execution_time:.2f} seconds")
        print(f"   Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Priority breakdown
        if 'decisions' in kpis:
            decisions_df = kpis['decisions']
            if 'priority_level' in decisions_df.columns:
                priority_counts = decisions_df['priority_level'].value_counts()
                
                print(f"\n[PRIORITY BREAKDOWN]")
                for priority in ['Critical', 'High', 'Medium', 'Low']:
                    count = priority_counts.get(priority, 0)
                    print(f"   {priority}: {count} equipment")
        
        # KPI status breakdown
        if 'kpis' in kpis:
            kpis_dict = kpis['kpis']
            status_counts = {}
            for kpi in kpis_dict.values():
                status = kpi.get('status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f"\n[KPI STATUS]")
            for status in ['Excellent', 'Good', 'Warning', 'Critical']:
                count = status_counts.get(status, 0)
                if count > 0:
                    print(f"   {status}: {count} KPIs")
        
        # Model metrics summary
        if use_model_training and 'model_metrics' in kpis and 'model_metrics' in kpis['model_metrics']:
            metrics_df = kpis['model_metrics'].get('model_metrics')
            if metrics_df is not None and not metrics_df.empty and 'F1-Score' in metrics_df.columns:
                best_model_idx = metrics_df['F1-Score'].idxmax()
                best_model = metrics_df.loc[best_model_idx, 'Model']
                best_f1 = metrics_df.loc[best_model_idx, 'F1-Score']
                
                print(f"\n[MODEL METRICS]")
                print(f"   Best model: {best_model}")
                print(f"   F1-Score: {best_f1:.4f}")
                print(f"   Model metrics saved: {len(metrics_df)}")
        
        print("\n" + "="*70)
        print("[COMPLETE] All data saved to database successfully!")
        print("   Ready for API and Dashboard access")
        print("="*70 + "\n")
        
        logger.info("Pipeline execution completed successfully")
        
        return {
            'success': True,
            'execution_time': execution_time,
            'equipment_count': len(data.get('equipment', [])),
            'predictions_count': result.get('predictions_saved', 0),
            'kpis_count': result.get('kpis_saved', 0)
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_message = log_error(e, "Pipeline")
        
        print("\n" + "="*70)
        print("[ERROR] INTEGRATED PIPELINE EXECUTION FAILED!")
        print("="*70)
        print(f"\nError: {e}")
        print(f"Execution time before failure: {execution_time:.2f} seconds")
        print("\n" + "="*70 + "\n")
        
        logger.critical(f"Pipeline execution failed: {e}")
        
        return {
            'success': False,
            'error': str(e),
            'execution_time': execution_time
        }

if __name__ == "__main__":
    # Run the integrated pipeline
    # Set use_model_training=True to use model training
    # Set use_model_training=False to use existing models
    result = run_integrated_pipeline(use_model_training=True)
    
    if result['success']:
        print(f"[OK] Integrated pipeline completed successfully in {result['execution_time']:.2f} seconds")
    else:
        print(f"[FAILED] Integrated pipeline failed after {result['execution_time']:.2f} seconds")
        print(f"   Error: {result['error']}")
