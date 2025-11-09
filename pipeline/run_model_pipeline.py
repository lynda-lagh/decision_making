"""
Model Pipeline Runner

This script runs the complete model pipeline, including:
1. Training models on existing data from PostgreSQL
2. Fine-tuning models with new input data
3. Evaluating and comparing model performance
4. Selecting the best model for production
5. Generating visualizations and metrics

The pipeline can be run in different modes:
- train: Train new models on existing data
- finetune: Fine-tune existing models with new data
- predict: Generate predictions using the best model
- visualize: Create visualizations of model performance
"""

import os
import sys
import time
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append('..')
from pipeline.model_training_pipeline import ModelTrainingPipeline
from pipeline.model_integration import ModelIntegration
from pipeline.model_visualization import ModelVisualization

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run the model pipeline')
    
    parser.add_argument('--mode', type=str, default='train',
                        choices=['train', 'finetune', 'predict', 'visualize', 'all'],
                        help='Pipeline mode: train, finetune, predict, visualize, or all')
    
    parser.add_argument('--data-file', type=str,
                        help='Path to CSV file with new data for fine-tuning or prediction')
    
    parser.add_argument('--output-dir', type=str, default='../images',
                        help='Directory to save output files')
    
    return parser.parse_args()

def load_data_from_file(file_path):
    """Load data from CSV file"""
    print(f"\n🔄 Loading data from {file_path}...")
    
    try:
        df = pd.read_csv(file_path)
        print(f"✅ Data loaded: {len(df)} records")
        print(f"   Columns: {', '.join(df.columns)}")
        return df
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

def run_train_mode():
    """Run the pipeline in train mode"""
    print("\n" + "="*70)
    print("🚀 RUNNING PIPELINE IN TRAIN MODE")
    print("="*70)
    
    # Create and run training pipeline
    pipeline = ModelTrainingPipeline()
    result = pipeline.run_pipeline()
    
    # Create visualizations
    viz = ModelVisualization()
    viz.create_all_visualizations()
    
    return result

def run_finetune_mode(data_file):
    """Run the pipeline in finetune mode"""
    print("\n" + "="*70)
    print("🚀 RUNNING PIPELINE IN FINETUNE MODE")
    print("="*70)
    
    # Load new data
    new_data = load_data_from_file(data_file)
    if new_data is None:
        return {'success': False, 'error': 'Failed to load new data'}
    
    # Create and run integration
    integration = ModelIntegration()
    result = integration.run_integration(new_data=new_data)
    
    # Create visualizations
    viz = ModelVisualization()
    viz.create_all_visualizations()
    
    return result

def run_predict_mode(data_file):
    """Run the pipeline in predict mode"""
    print("\n" + "="*70)
    print("🚀 RUNNING PIPELINE IN PREDICT MODE")
    print("="*70)
    
    # Load features
    features_df = load_data_from_file(data_file)
    if features_df is None:
        return {'success': False, 'error': 'Failed to load features'}
    
    # Create and run integration
    integration = ModelIntegration()
    result = integration.run_integration(features_df=features_df)
    
    # Save predictions if available
    if result['predictions'] is not None:
        output_file = f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        output_path = Path(args.output_dir) / output_file
        result['predictions'].to_csv(output_path, index=False)
        print(f"✅ Predictions saved to {output_path}")
    
    return result

def run_visualize_mode():
    """Run the pipeline in visualize mode"""
    print("\n" + "="*70)
    print("🚀 RUNNING PIPELINE IN VISUALIZE MODE")
    print("="*70)
    
    # Create visualizations
    viz = ModelVisualization()
    viz.create_all_visualizations()
    
    return {'success': True}

def run_all_mode(data_file):
    """Run the pipeline in all mode"""
    print("\n" + "="*70)
    print("🚀 RUNNING PIPELINE IN ALL MODE")
    print("="*70)
    
    # Train models
    train_result = run_train_mode()
    
    # Fine-tune models if data file provided
    finetune_result = None
    if data_file:
        finetune_result = run_finetune_mode(data_file)
    
    # Generate predictions if data file provided
    predict_result = None
    if data_file:
        predict_result = run_predict_mode(data_file)
    
    return {
        'train_result': train_result,
        'finetune_result': finetune_result,
        'predict_result': predict_result
    }

def display_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█'):
    """Display progress bar"""
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    if iteration == total:
        print()

def display_time_remaining(start_time, current_step, total_steps):
    """Display time remaining"""
    elapsed_time = time.time() - start_time
    if current_step > 0:
        estimated_total_time = elapsed_time * total_steps / current_step
        remaining_time = estimated_total_time - elapsed_time
        
        # Format time
        hours, remainder = divmod(remaining_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            time_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        elif minutes > 0:
            time_str = f"{int(minutes)}m {int(seconds)}s"
        else:
            time_str = f"{int(seconds)}s"
        
        print(f"⏱️ Estimated time remaining: {time_str}")

if __name__ == "__main__":
    # Parse arguments
    args = parse_arguments()
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Record start time
    start_time = time.time()
    
    # Run pipeline in specified mode
    result = None
    
    if args.mode == 'train':
        result = run_train_mode()
    elif args.mode == 'finetune':
        if args.data_file:
            result = run_finetune_mode(args.data_file)
        else:
            print("❌ Data file required for finetune mode")
            sys.exit(1)
    elif args.mode == 'predict':
        if args.data_file:
            result = run_predict_mode(args.data_file)
        else:
            print("❌ Data file required for predict mode")
            sys.exit(1)
    elif args.mode == 'visualize':
        result = run_visualize_mode()
    elif args.mode == 'all':
        result = run_all_mode(args.data_file)
    
    # Calculate execution time
    execution_time = time.time() - start_time
    
    # Format time
    hours, remainder = divmod(execution_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        time_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        time_str = f"{int(minutes)}m {int(seconds)}s"
    else:
        time_str = f"{int(seconds)}s"
    
    print("\n" + "="*70)
    print(f"✅ PIPELINE EXECUTION COMPLETED IN {time_str}")
    print("="*70)
    
    # Print summary
    if result and isinstance(result, dict) and result.get('success'):
        if args.mode == 'predict' and result.get('predictions') is not None:
            print(f"\n📊 Generated {len(result['predictions'])} predictions")
            print(f"   Positive predictions: {result['predictions']['prediction'].sum()}")
            print(f"   Using model: {result['best_model']}")
        elif args.mode == 'train' or args.mode == 'finetune':
            print(f"\n🏆 Best model: {result['best_model']}")
    
    print(f"\n✅ All outputs saved to {output_dir}")
    print("✅ Done!")
