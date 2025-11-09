"""
Stage 5: Model Metrics Tracking

This module extends the KPI calculation stage to include model metrics tracking.
It handles:
1. Calculating model performance metrics
2. Tracking metrics over time
3. Comparing model performance
4. Generating visualizations
5. Saving metrics to database

The module ensures that model performance is tracked and visualized over time.
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
import psycopg2

# Add parent directory to path
sys.path.append('..')
sys.path.append('../..')

# Import pipeline modules
from config import DB_CONFIG, MODELS_DIR, IMAGES_DIR

# Create images directory if it doesn't exist
IMAGES_DIR.mkdir(exist_ok=True)

def connect_to_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        print(f"✅ Connected to database: {DB_CONFIG['database']}")
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def save_metrics_to_db(conn, metrics_df):
    """Save model metrics to database"""
    print("\n🔄 Saving metrics to database...")
    
    if conn is None:
        print("  ❌ Database connection not available")
        return
    
    try:
        # Create cursor
        cursor = conn.cursor()
        
        # Current date
        evaluation_date = datetime.now().strftime("%Y-%m-%d")
        
        # Insert metrics for each model
        for _, row in metrics_df.iterrows():
            model_name = row['Model']
            
            # Check if model metrics already exist for today
            check_query = """
            SELECT performance_id FROM model_performance
            WHERE model_name = %s AND evaluation_date = %s
            """
            cursor.execute(check_query, (model_name, evaluation_date))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                update_query = """
                UPDATE model_performance
                SET accuracy = %s, precision_score = %s, recall = %s, f1_score = %s, roc_auc = %s
                WHERE performance_id = %s
                """
                cursor.execute(
                    update_query,
                    (
                        float(row['Accuracy']),
                        float(row['Precision']),
                        float(row['Recall']),
                        float(row['F1-Score']),
                        float(row['ROC-AUC']) if pd.notna(row['ROC-AUC']) else None,
                        existing[0]
                    )
                )
                print(f"  ✅ Updated metrics for {model_name}")
            else:
                # Insert new record
                insert_query = """
                INSERT INTO model_performance
                (model_name, model_version, evaluation_date, accuracy, precision_score, recall, f1_score, roc_auc, sample_size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(
                    insert_query,
                    (
                        model_name,
                        '1.0',  # Model version
                        evaluation_date,
                        float(row['Accuracy']),
                        float(row['Precision']),
                        float(row['Recall']),
                        float(row['F1-Score']),
                        float(row['ROC-AUC']) if pd.notna(row['ROC-AUC']) else None,
                        1000  # Sample size placeholder
                    )
                )
                print(f"  ✅ Inserted metrics for {model_name}")
        
        # Commit changes
        conn.commit()
        
        # Close cursor
        cursor.close()
        
        print("\n✅ Model metrics saved to database")
        
    except Exception as e:
        print(f"  ❌ Error saving metrics to database: {e}")

def load_metrics_from_db(conn):
    """Load model metrics history from database"""
    print("\n🔄 Loading metrics history from database...")
    
    if conn is None:
        print("  ❌ Database connection not available")
        return None
    
    try:
        # Create cursor
        cursor = conn.cursor()
        
        # Query to get metrics history
        query = """
        SELECT 
            model_name, 
            model_version,
            evaluation_date, 
            accuracy, 
            precision_score, 
            recall, 
            f1_score, 
            roc_auc
        FROM 
            model_performance
        ORDER BY 
            evaluation_date, model_name
        """
        
        cursor.execute(query)
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        # Get column names
        column_names = [desc[0] for desc in cursor.description]
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=column_names)
        
        # Close cursor
        cursor.close()
        
        print(f"✅ Loaded metrics history: {len(df)} records")
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading metrics history: {e}")
        return None

def plot_metrics_history(metrics_df):
    """Plot metrics history"""
    print("\n🔄 Creating metrics history plots...")
    
    try:
        if metrics_df is None or len(metrics_df) == 0:
            print("⚠️ No metrics history available")
            return
        
        # Convert date column to datetime
        metrics_df['evaluation_date'] = pd.to_datetime(metrics_df['evaluation_date'])
        
        # Get unique models
        models = metrics_df['model_name'].unique()
        
        # Plot F1-Score history for each model
        plt.figure(figsize=(12, 8))
        
        for model in models:
            model_data = metrics_df[metrics_df['model_name'] == model]
            plt.plot(model_data['evaluation_date'], model_data['f1_score'], marker='o', label=model)
        
        # Add labels and legend
        plt.title('F1-Score History - All Models', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=14)
        plt.ylabel('F1-Score', fontsize=14)
        plt.ylim([0, 1.0])
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Format x-axis dates
        plt.gcf().autofmt_xdate()
        
        # Save figure
        filename = "model_f1_history.png"
        filepath = IMAGES_DIR / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 F1-Score history saved to {filepath}")
        
        # Plot all metrics for the best model (based on latest F1-Score)
        latest_metrics = metrics_df.sort_values('evaluation_date').groupby('model_name').last()
        best_model = latest_metrics['f1_score'].idxmax()
        
        best_model_data = metrics_df[metrics_df['model_name'] == best_model]
        
        plt.figure(figsize=(12, 8))
        
        metrics = ['accuracy', 'precision_score', 'recall', 'f1_score']
        for metric in metrics:
            plt.plot(best_model_data['evaluation_date'], best_model_data[metric], marker='o', label=metric.capitalize())
        
        # Add labels and legend
        plt.title(f'Performance Metrics History - {best_model}', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=14)
        plt.ylabel('Score', fontsize=14)
        plt.ylim([0, 1.0])
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Format x-axis dates
        plt.gcf().autofmt_xdate()
        
        # Save figure
        filename = f"{best_model}_metrics_history.png"
        filepath = IMAGES_DIR / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Best model metrics history saved to {filepath}")
        
    except Exception as e:
        print(f"❌ Error creating metrics history plots: {e}")

def run_stage5_model_metrics(data):
    """Execute Stage 5: Model Metrics Tracking"""
    print("\n" + "="*60)
    print("STAGE 5: MODEL METRICS TRACKING")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # Extract model results
        if isinstance(data, dict) and 'models' in data:
            models_info = data['models']
        else:
            print("⚠️ No model information available")
            return {}
        
        # Load model results
        results_path = MODELS_DIR / "model_results.csv"
        if results_path.exists():
            metrics_df = pd.read_csv(results_path)
            print(f"✅ Loaded model results from {results_path}")
        else:
            print("⚠️ No model results found")
            metrics_df = None
        
        # Connect to database
        conn = connect_to_db()
        
        # Save metrics to database
        if conn and metrics_df is not None:
            save_metrics_to_db(conn, metrics_df)
        
        # Load metrics history from database
        metrics_history = load_metrics_from_db(conn)
        
        # Plot metrics history
        plot_metrics_history(metrics_history)
        
        # Close database connection
        if conn:
            conn.close()
            print("\n✅ Database connection closed")
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        print(f"\n[COMPLETE] Stage 5 Model Metrics Complete!")
        print(f"   Best model: {models_info.get('best_model_name', 'Unknown')}")
        print(f"   Execution time: {execution_time:.2f}s")
        
        # Return metrics information
        return {
            'model_metrics': metrics_df,
            'metrics_history': metrics_history
        }
        
    except Exception as e:
        print(f"[ERROR] Error in Stage 5 Model Metrics: {e}")
        import traceback
        traceback.print_exc()
        return {}

if __name__ == "__main__":
    # Test stage 5 model metrics
    from stage1_data_ingestion import run_stage1
    from stage2_feature_engineering import run_stage2
    from stage3_model_training import run_stage3
    
    print("Testing model metrics tracking...")
    data = run_stage1()
    features = run_stage2(data)
    predictions = run_stage3(features)
    metrics = run_stage5_model_metrics(predictions)
    
    print("\nMetrics sample:")
    if 'model_metrics' in metrics and metrics['model_metrics'] is not None:
        print(metrics['model_metrics'].head())
