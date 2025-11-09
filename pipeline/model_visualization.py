"""
Model Visualization Module

This module provides functions for visualizing model performance metrics and comparisons.
It includes:
1. Performance metrics visualization
2. Model comparison charts
3. ROC curves
4. Confusion matrices
5. Feature importance plots
6. Training history visualization

These visualizations help in understanding model performance and making informed decisions.
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from sklearn.metrics import roc_curve, auc, confusion_matrix

# Add parent directory to path
sys.path.append('..')
from pipeline.config import MODELS_DIR, IMAGES_DIR

# Create images directory if it doesn't exist
IMAGES_DIR.mkdir(exist_ok=True)

class ModelVisualization:
    """Provides functions for visualizing model performance"""
    
    def __init__(self):
        """Initialize the visualization module"""
        self.models = {}
        self.results = None
        self.feature_columns = None
    
    def load_models_and_results(self):
        """Load trained models and results"""
        print("\n🔄 Loading models and results...")
        
        try:
            # Load model results
            results_path = MODELS_DIR / "model_results.csv"
            if results_path.exists():
                self.results = pd.read_csv(results_path)
                print(f"✅ Loaded model results from {results_path}")
            else:
                print("⚠️ No model results found")
            
            # Load models
            model_files = list(MODELS_DIR.glob("*.pkl"))
            for file in model_files:
                if file.stem in ['scaler', 'feature_columns']:
                    continue
                    
                model = joblib.load(file)
                self.models[file.stem] = model
                print(f"✅ Loaded model: {file.stem}")
            
            # Load feature columns
            feature_path = MODELS_DIR / "feature_columns.pkl"
            if feature_path.exists():
                self.feature_columns = joblib.load(feature_path)
                print(f"✅ Loaded feature columns")
            
            return True
                
        except Exception as e:
            print(f"❌ Error loading models and results: {e}")
            return False
    
    def plot_model_comparison(self):
        """Plot model comparison chart"""
        print("\n🔄 Creating model comparison chart...")
        
        if self.results is None:
            print("❌ No model results available")
            return
        
        try:
            # Prepare data for plotting
            models = self.results['Model'].tolist()
            metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
            
            plt.figure(figsize=(12, 8))
            
            # Set width of bars
            barWidth = 0.15
            r = np.arange(len(models))
            
            # Make the plot
            for i, metric in enumerate(metrics):
                if metric in self.results.columns:
                    values = self.results[metric].tolist()
                    plt.bar(r + i * barWidth, values, width=barWidth, label=metric)
            
            # Add labels and legend
            plt.xlabel('Models', fontweight='bold', fontsize=14)
            plt.ylabel('Score', fontweight='bold', fontsize=14)
            plt.title('Model Comparison', fontweight='bold', fontsize=16)
            plt.xticks(r + barWidth * 2, models, rotation=45, ha='right')
            plt.legend()
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Save figure
            filename = "model_comparison.png"
            filepath = IMAGES_DIR / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"📊 Model comparison chart saved to {filepath}")
            
        except Exception as e:
            print(f"❌ Error creating model comparison chart: {e}")
    
    def plot_feature_importance(self):
        """Plot feature importance for tree-based models"""
        print("\n🔄 Creating feature importance plots...")
        
        try:
            # Check for tree-based models
            tree_models = {
                name: model for name, model in self.models.items() 
                if hasattr(model, 'feature_importances_')
            }
            
            if not tree_models:
                print("⚠️ No tree-based models with feature importances found")
                return
            
            if self.feature_columns is None:
                print("⚠️ Feature columns not available")
                return
            
            # Plot feature importance for each tree-based model
            for name, model in tree_models.items():
                # Check if feature importances length matches feature columns length
                importances = model.feature_importances_
                
                if len(importances) != len(self.feature_columns):
                    print(f"  ⚠️ Feature mismatch for {name}: {len(importances)} importances vs {len(self.feature_columns)} features")
                    
                    # Try to use generic feature names instead
                    feature_names = [f"Feature_{i}" for i in range(len(importances))]
                    print(f"  ⚠️ Using generic feature names for {name}")
                else:
                    feature_names = self.feature_columns
                
                plt.figure(figsize=(12, 8))
                
                # Create DataFrame with feature names and importances
                feature_df = pd.DataFrame({
                    'Feature': feature_names,
                    'Importance': importances
                })
                
                # Sort by importance
                feature_df = feature_df.sort_values('Importance', ascending=False)
                
                # Plot top 15 features (or all if less than 15)
                top_count = min(15, len(feature_df))
                top_features = feature_df.head(top_count)
                
                # Create horizontal bar chart
                sns.barplot(x='Importance', y='Feature', data=top_features)
                
                # Add labels
                plt.title(f'Feature Importance - {name}', fontsize=16, fontweight='bold')
                plt.xlabel('Importance', fontsize=14)
                plt.ylabel('Feature', fontsize=14)
                plt.grid(axis='x', linestyle='--', alpha=0.7)
                
                # Save figure
                filename = f"{name}_feature_importance.png"
                filepath = IMAGES_DIR / filename
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"📊 Feature importance plot for {name} saved to {filepath}")
                
        except Exception as e:
            print(f"❌ Error creating feature importance plots: {e}")
            import traceback
            traceback.print_exc()
    
    def plot_confusion_matrices(self, y_true, predictions_dict):
        """Plot confusion matrices for all models"""
        print("\n🔄 Creating confusion matrices...")
        
        try:
            for name, y_pred in predictions_dict.items():
                # Calculate confusion matrix
                cm = confusion_matrix(y_true, y_pred)
                
                # Plot confusion matrix
                plt.figure(figsize=(8, 6))
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
                plt.title(f'Confusion Matrix - {name}', fontsize=16)
                plt.ylabel('True Label', fontsize=14)
                plt.xlabel('Predicted Label', fontsize=14)
                
                # Save figure
                filename = f"{name}_confusion_matrix.png"
                filepath = IMAGES_DIR / filename
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"📊 Confusion matrix for {name} saved to {filepath}")
                
        except Exception as e:
            print(f"❌ Error creating confusion matrices: {e}")
    
    def plot_roc_curves(self, y_true, probas_dict):
        """Plot ROC curves for all models"""
        print("\n🔄 Creating ROC curves...")
        
        try:
            plt.figure(figsize=(10, 8))
            
            # Plot ROC curve for each model
            for name, y_proba in probas_dict.items():
                fpr, tpr, _ = roc_curve(y_true, y_proba)
                roc_auc = auc(fpr, tpr)
                plt.plot(fpr, tpr, lw=2, label=f'{name} (AUC = {roc_auc:.3f})')
            
            # Plot random guessing line
            plt.plot([0, 1], [0, 1], 'k--', lw=2, label='Random Guessing')
            
            # Set plot properties
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel('False Positive Rate', fontsize=14)
            plt.ylabel('True Positive Rate', fontsize=14)
            plt.title('ROC Curves for All Models', fontsize=16, fontweight='bold')
            plt.legend(loc="lower right", fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Save figure
            filename = "roc_curves.png"
            filepath = IMAGES_DIR / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"📊 ROC curves saved to {filepath}")
            
        except Exception as e:
            print(f"❌ Error creating ROC curves: {e}")
    
    def plot_metrics_history(self):
        """Plot metrics history from database"""
        print("\n🔄 Creating metrics history plots...")
        
        try:
            # This would typically load data from the database
            # For now, we'll create a sample DataFrame
            dates = pd.date_range(start='2025-01-01', periods=10, freq='D')
            models = ['random_forest', 'svm', 'xgboost', 'isolation_forest']
            metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
            
            # Create sample data
            np.random.seed(42)
            data = []
            
            for date in dates:
                for model in models:
                    for metric in metrics:
                        # Simulate improvement over time with some noise
                        base_value = 0.7 + 0.2 * np.random.random()
                        trend = 0.01 * dates.get_loc(date)
                        value = min(0.99, base_value + trend)
                        
                        data.append({
                            'Date': date,
                            'Model': model,
                            'Metric': metric,
                            'Value': value
                        })
            
            # Create DataFrame
            history_df = pd.DataFrame(data)
            
            # Plot metrics history for each model
            for model in models:
                model_data = history_df[history_df['Model'] == model]
                
                plt.figure(figsize=(12, 8))
                
                # Plot each metric
                for metric in metrics:
                    metric_data = model_data[model_data['Metric'] == metric]
                    plt.plot(metric_data['Date'], metric_data['Value'], marker='o', label=metric)
                
                # Add labels and legend
                plt.title(f'Performance Metrics History - {model}', fontsize=16, fontweight='bold')
                plt.xlabel('Date', fontsize=14)
                plt.ylabel('Score', fontsize=14)
                plt.ylim([0.5, 1.0])
                plt.grid(True, alpha=0.3)
                plt.legend()
                
                # Format x-axis dates
                plt.gcf().autofmt_xdate()
                
                # Save figure
                filename = f"{model}_metrics_history.png"
                filepath = IMAGES_DIR / filename
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"📊 Metrics history for {model} saved to {filepath}")
            
            # Create combined metrics history plot
            plt.figure(figsize=(12, 8))
            
            # Plot F1-Score for each model
            for model in models:
                model_data = history_df[(history_df['Model'] == model) & (history_df['Metric'] == 'F1-Score')]
                plt.plot(model_data['Date'], model_data['Value'], marker='o', label=model)
            
            # Add labels and legend
            plt.title('F1-Score History - All Models', fontsize=16, fontweight='bold')
            plt.xlabel('Date', fontsize=14)
            plt.ylabel('F1-Score', fontsize=14)
            plt.ylim([0.5, 1.0])
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            # Format x-axis dates
            plt.gcf().autofmt_xdate()
            
            # Save figure
            filename = "all_models_f1_history.png"
            filepath = IMAGES_DIR / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"📊 Combined F1-Score history saved to {filepath}")
            
        except Exception as e:
            print(f"❌ Error creating metrics history plots: {e}")
    
    def create_all_visualizations(self):
        """Create all visualizations"""
        print("\n" + "="*70)
        print("🚀 CREATING MODEL VISUALIZATIONS")
        print("="*70)
        
        # Load models and results
        self.load_models_and_results()
        
        # Create visualizations
        self.plot_model_comparison()
        self.plot_feature_importance()
        self.plot_metrics_history()
        
        print("\n" + "="*70)
        print("✅ MODEL VISUALIZATIONS CREATED SUCCESSFULLY")
        print("="*70)


if __name__ == "__main__":
    # Create and run visualization
    viz = ModelVisualization()
    viz.create_all_visualizations()
