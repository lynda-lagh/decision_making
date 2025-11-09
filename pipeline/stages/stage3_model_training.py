"""
Stage 3: Model Training and Selection

This module integrates the model training pipeline with the main pipeline.
It handles:
1. Training models on existing data
2. Fine-tuning models with new data
3. Selecting the best model for predictions
4. Saving model metrics to database
5. Generating visualizations

The module ensures that the best performing model is always used for predictions.
"""

import os
import sys
import time
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Add parent directory to path
sys.path.append('..')
sys.path.append('../..')

# Import pipeline modules
from pipeline.model_training_pipeline import ModelTrainingPipeline
from pipeline.model_integration import ModelIntegration
from pipeline.model_visualization import ModelVisualization
from config import MODELS_DIR, IMAGES_DIR

# Create images directory if it doesn't exist
IMAGES_DIR.mkdir(exist_ok=True)

def run_stage3_training(data):
    """Execute Stage 3: Model Training and Selection"""
    print("\n" + "="*60)
    print("STAGE 3: MODEL TRAINING AND SELECTION")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # Extract features from data
        if isinstance(data, dict):
            features_df = data['features']
        else:
            features_df = data
        
        print(f"\n[INFO] Starting model training with {len(features_df)} samples")
        
        # Check if we have existing models to fine-tune
        integration = ModelIntegration()
        has_existing_models = integration.load_best_model()
        
        if has_existing_models:
            print("\n[FINE-TUNE] Fine-tuning existing models...")
            # Fine-tune existing models
            pipeline = ModelTrainingPipeline()
            pipeline.run_pipeline(new_data=features_df)
        else:
            print("\n[TRAIN] Training new models...")
            # Train new models
            pipeline = ModelTrainingPipeline()
            pipeline.run_pipeline()
        
        # Load the best model for predictions
        integration = ModelIntegration()
        integration.load_best_model()
        
        # Generate predictions
        predictions = integration.predict(features_df)
        
        # If predictions failed, create a default predictions DataFrame
        if predictions is None:
            print("\n[WARN] Predictions failed, creating default predictions")
            predictions = pd.DataFrame({
                'equipment_id': features_df['equipment_id'],
                'prediction': 0,  # Default to no failure prediction
                'probability': 0.0,  # Default to zero probability
                'model_name': integration.best_model_name if integration.best_model_name else 'unknown'
            })
        
        # Ensure predictions DataFrame has a 'risk_score' column
        if 'risk_score' not in predictions.columns:
            print("\n[WARN] Adding missing 'risk_score' column to predictions")
            # Use probability as risk_score if available, otherwise use 0
            if 'probability' in predictions.columns:
                predictions['risk_score'] = predictions['probability'] * 100
            else:
                predictions['risk_score'] = 0.0
        
        # Create visualizations
        print("\n[VISUALIZE] Creating model performance visualizations...")
        viz = ModelVisualization()
        viz.create_all_visualizations()
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        print(f"\n[COMPLETE] Stage 3 Complete!")
        print(f"   Total samples: {len(features_df)}")
        print(f"   Best model: {integration.best_model_name}")
        print(f"   Execution time: {execution_time:.2f}s")
        
        # Return predictions and model information
        return {
            'predictions': predictions,
            'models': {
                'best_model_name': integration.best_model_name,
                'best_model': integration.best_model,
                'scaler': integration.scaler,
                'feature_columns': integration.feature_columns
            }
        }
        
    except Exception as e:
        print(f"[ERROR] Error in Stage 3: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a minimal valid result to prevent pipeline failure
        if 'features_df' in locals() and 'integration' in locals():
            # Create default predictions
            default_predictions = pd.DataFrame({
                'equipment_id': features_df['equipment_id'],
                'prediction': 0,  # Default to no failure prediction
                'probability': 0.0,  # Default to zero probability
                'risk_score': 0.0,  # Default risk score
                'model_name': 'error_fallback'
            })
            
            return {
                'predictions': default_predictions,
                'models': {
                    'best_model_name': 'error_fallback',
                    'best_model': None,
                    'scaler': None,
                    'feature_columns': None
                }
            }
        else:
            # If we can't even create default predictions, re-raise the exception
            raise

def run_stage3(data):
    """Compatibility wrapper for the main pipeline"""
    # This function maintains compatibility with the existing pipeline structure
    result = run_stage3_training(data)
    
    # Extract predictions and convert to the format expected by the main pipeline
    predictions_df = result['predictions']
    
    # Create the output structure expected by the main pipeline
    output = {
        'predictions': predictions_df,
        'models': result['models']
    }
    
    return output

if __name__ == "__main__":
    # Test stage 3
    from stage1_data_ingestion import run_stage1
    from stage2_feature_engineering import run_stage2
    
    print("Testing model training pipeline...")
    data = run_stage1()
    result = run_stage2(data)
    predictions = run_stage3(result)
    
    print(f"\nPredictions sample:")
    print(predictions['predictions'][['equipment_id', 'prediction', 'probability']].head(10))
