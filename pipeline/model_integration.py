"""
Model Integration Module

This module integrates the model training pipeline with the main pipeline.
It handles:
1. Loading the best model for predictions
2. Updating models with new data
3. Comparing model performance
4. Selecting the best model for production

The integration ensures that the best performing model is always used for predictions.
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
from pipeline.config import MODELS_DIR
from pipeline.model_training_pipeline import ModelTrainingPipeline

# Create images directory if it doesn't exist
IMAGES_DIR = Path('../images')
IMAGES_DIR.mkdir(exist_ok=True)

class ModelIntegration:
    """Integrates model training with the main pipeline"""
    
    def __init__(self):
        """Initialize the integration"""
        self.model_pipeline = ModelTrainingPipeline()
        self.best_model = None
        self.best_model_name = None
        self.scaler = None
        self.feature_columns = None
    
    def load_best_model(self):
        """Load the best model for predictions"""
        print("\n🔄 Loading best model...")
        
        try:
            # Load model results to find the best model
            results_path = MODELS_DIR / "model_results.csv"
            if results_path.exists():
                results = pd.read_csv(results_path)
                best_model_idx = results['F1-Score'].idxmax()
                self.best_model_name = results.loc[best_model_idx, 'Model']
                
                # Load the best model
                model_path = MODELS_DIR / f"{self.best_model_name}.pkl"
                self.best_model = joblib.load(model_path)
                
                # Load scaler
                scaler_path = MODELS_DIR / "scaler.pkl"
                self.scaler = joblib.load(scaler_path)
                
                # Load feature columns
                feature_path = MODELS_DIR / "feature_columns.pkl"
                self.feature_columns = joblib.load(feature_path)
                
                print(f"✅ Loaded best model: {self.best_model_name}")
                print(f"   F1-Score: {results.loc[best_model_idx, 'F1-Score']:.4f}")
                
                return True
            else:
                print("⚠️ No model results found, will train new models")
                return False
                
        except Exception as e:
            print(f"❌ Error loading best model: {e}")
            return False
    
    def predict(self, features_df):
        """Generate predictions using the best model"""
        print("\n🔄 Generating predictions...")
        
        try:
            # Check if model is loaded
            if self.best_model is None:
                success = self.load_best_model()
                if not success:
                    print("❌ No model available for predictions")
                    return None
            
            # Make a copy of the features DataFrame to avoid modifying the original
            features_copy = features_df.copy()
            
            # Check for missing columns and add them with default values
            for column in self.feature_columns:
                if column not in features_copy.columns:
                    print(f"  ⚠️ Adding missing column: {column} with default value 0")
                    features_copy[column] = 0
            
            # Prepare features - use only the columns needed by the model
            X = features_copy[self.feature_columns].fillna(0)
            X_scaled = self.scaler.transform(X)
            
            # Generate predictions
            if self.best_model_name == 'isolation_forest':
                # For Isolation Forest, convert scores to binary predictions
                # Negative scores are outliers (failures)
                raw_scores = self.best_model.decision_function(X_scaled)
                # Invert scores so higher = more likely to be failure
                scores = -raw_scores
                # Normalize to 0-1 range for probability-like scores
                min_score, max_score = scores.min(), scores.max()
                proba = (scores - min_score) / (max_score - min_score)
                # Convert to binary predictions using threshold
                threshold = 0.7  # Configurable threshold
                y_pred = (proba >= threshold).astype(int)
                
                # Create predictions DataFrame
                predictions = pd.DataFrame({
                    'equipment_id': features_df['equipment_id'],
                    'prediction': y_pred,
                    'probability': proba,
                    'model_name': self.best_model_name
                })
            else:
                # For classification models
                y_pred = self.best_model.predict(X_scaled)
                proba = self.best_model.predict_proba(X_scaled)[:, 1] if hasattr(self.best_model, 'predict_proba') else None
                
                # Create predictions DataFrame
                predictions = pd.DataFrame({
                    'equipment_id': features_df['equipment_id'],
                    'prediction': y_pred,
                    'probability': proba,
                    'model_name': self.best_model_name
                })
            
            print(f"✅ Generated {len(predictions)} predictions")
            print(f"   Positive predictions: {predictions['prediction'].sum()}")
            print(f"   Average probability: {predictions['probability'].mean():.4f}")
            
            return predictions
            
        except Exception as e:
            print(f"❌ Error generating predictions: {e}")
            return None
    
    def update_models(self, new_data):
        """Update models with new data"""
        print("\n🔄 Updating models with new data...")
        
        try:
            # Check if models exist
            if not self.load_best_model():
                # Train new models
                print("⚠️ No existing models found, training new models...")
                result = self.model_pipeline.run_pipeline()
                return result['success']
            
            # Fine-tune existing models
            self.model_pipeline.fine_tune_models(new_data)
            
            # Re-evaluate and save updated models
            # Note: This requires test data, which we don't have here
            # In a real scenario, you would need to store test data or use cross-validation
            
            print("✅ Models updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error updating models: {e}")
            return False
    
    def compare_model_versions(self):
        """Compare performance of different model versions"""
        print("\n🔄 Comparing model versions...")
        
        try:
            # Get list of model result files
            result_files = list(MODELS_DIR.glob("model_results_*.csv"))
            
            if len(result_files) < 2:
                print("⚠️ Not enough model versions for comparison")
                return
            
            # Load and compare results
            all_results = []
            
            for file in result_files:
                version = file.stem.split('_')[-1]
                results = pd.read_csv(file)
                results['Version'] = version
                all_results.append(results)
            
            # Combine results
            combined_results = pd.concat(all_results)
            
            # Create comparison visualization
            self._save_version_comparison(combined_results)
            
            print("✅ Model version comparison complete")
            
        except Exception as e:
            print(f"❌ Error comparing model versions: {e}")
    
    def _save_version_comparison(self, results_df):
        """Save model version comparison visualization"""
        # Prepare data for plotting
        models = results_df['Model'].unique()
        versions = results_df['Version'].unique()
        metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        
        # Create subplots for each metric
        fig, axes = plt.subplots(len(metrics), 1, figsize=(12, 4*len(metrics)))
        
        for i, metric in enumerate(metrics):
            # Create DataFrame for this metric
            metric_df = results_df.pivot(index='Model', columns='Version', values=metric)
            
            # Plot
            ax = axes[i]
            metric_df.plot(kind='bar', ax=ax)
            
            # Set labels
            ax.set_title(f'{metric} Comparison Across Versions', fontsize=14)
            ax.set_ylabel(metric, fontsize=12)
            ax.set_xlabel('Model', fontsize=12)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            ax.legend(title='Version')
        
        plt.tight_layout()
        
        # Save figure
        filename = "model_version_comparison.png"
        filepath = IMAGES_DIR / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Model version comparison saved to {filepath}")
    
    def run_integration(self, features_df=None, new_data=None):
        """Run the complete model integration"""
        print("\n" + "="*70)
        print("🚀 STARTING MODEL INTEGRATION")
        print("="*70)
        
        start_time = time.time()
        
        # Load best model
        self.load_best_model()
        
        # Update models with new data if provided
        if new_data is not None:
            self.update_models(new_data)
            
            # Compare model versions
            self.compare_model_versions()
        
        # Generate predictions if features provided
        predictions = None
        if features_df is not None:
            predictions = self.predict(features_df)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        print("\n" + "="*70)
        print(f"✅ MODEL INTEGRATION COMPLETED IN {execution_time:.2f}s")
        print("="*70)
        
        return {
            'success': True,
            'best_model': self.best_model_name,
            'predictions': predictions,
            'execution_time': execution_time
        }


if __name__ == "__main__":
    # Create and run integration
    integration = ModelIntegration()
    result = integration.run_integration()
    
    print(f"\n✅ Best model: {result['best_model']}")
    print(f"✅ Total execution time: {result['execution_time']:.2f}s")
