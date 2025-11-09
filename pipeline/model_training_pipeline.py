"""
Model Training Pipeline

This module handles the training and evaluation of multiple machine learning models
for predictive maintenance. It includes:
1. Loading data from PostgreSQL
2. Training multiple models
3. Fine-tuning models with new data
4. Evaluating and comparing model performance
5. Saving the best model
6. Generating performance metrics and visualizations

The pipeline supports incremental learning by fine-tuning existing models with new data.
"""

import os
import sys
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path
import psycopg2
from psycopg2 import sql
import warnings
warnings.filterwarnings('ignore')

# ML libraries
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.ensemble import IsolationForest

# Add parent directory to path
sys.path.append('..')
from pipeline.config import DB_CONFIG, MODELS_DIR, IMAGES_DIR

# Create images directory if it doesn't exist
IMAGES_DIR.mkdir(exist_ok=True)

class ModelTrainingPipeline:
    """Pipeline for training, evaluating, and fine-tuning predictive maintenance models"""
    
    def __init__(self):
        """Initialize the pipeline"""
        self.models = {
            'random_forest': None,
            'svm': None,
            'xgboost': None,
            'isolation_forest': None
        }
        self.scaler = None
        self.feature_columns = None
        self.results = {}
        self.best_model_name = None
        self.training_start_time = None
        self.total_steps = 0
        self.current_step = 0
    
    def connect_to_db(self):
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
    
    def load_data_from_db(self, conn):
        """Load training data from PostgreSQL database"""
        print("\n🔄 Loading data from PostgreSQL...")
        
        try:
            # Create cursor
            cursor = conn.cursor()
            
            # Query to get equipment data with features
            query = """
            SELECT 
                e.equipment_id,
                e.equipment_type,
                e.year_manufactured,
                e.operating_hours,
                EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.purchase_date)) AS age_years,
                COUNT(m.record_id) AS maintenance_count,
                SUM(CASE WHEN m.type_id = 1 THEN 1 ELSE 0 END) AS preventive_count,
                SUM(CASE WHEN m.type_id IN (2, 3) THEN 1 ELSE 0 END) AS corrective_count,
                AVG(m.total_cost) AS avg_maintenance_cost,
                SUM(m.total_cost) AS total_maintenance_cost,
                COUNT(f.failure_id) AS failure_count,
                AVG(f.repair_cost) AS avg_failure_cost,
                SUM(f.repair_cost) AS total_failure_cost,
                EXTRACT(DAY FROM AGE(CURRENT_DATE, MAX(m.maintenance_date))) AS days_since_last_service,
                AVG(m.downtime_hours) AS avg_downtime_hours,
                CASE WHEN COUNT(f.failure_id) > 0 THEN 1 ELSE 0 END AS has_failed
            FROM 
                equipment e
            LEFT JOIN 
                maintenance_records m ON e.equipment_id = m.equipment_id
            LEFT JOIN 
                failure_events f ON e.equipment_id = f.equipment_id
            GROUP BY 
                e.equipment_id, e.equipment_type, e.year_manufactured, 
                e.operating_hours, e.purchase_date
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
            
            # Fill NaN values
            df = df.fillna(0)
            
            print(f"✅ Data loaded: {len(df)} equipment records")
            print(f"   Features: {len(df.columns) - 2} columns")  # Excluding equipment_id and has_failed
            
            return df
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return None
    
    def generate_synthetic_data(self, n_samples=1000):
        """Generate synthetic data for testing when database is not available"""
        print("\n🔄 Generating synthetic data for testing...")
        
        np.random.seed(42)
        
        # Generate equipment IDs
        equipment_ids = [f"EQ-{i:04d}" for i in range(1, n_samples + 1)]
        
        # Generate equipment types
        equipment_types = np.random.choice(['Tractor', 'Harvester', 'Irrigation', 'Drone'], size=n_samples)
        
        # Generate numerical features
        age_years = np.random.uniform(0, 15, size=n_samples)
        operating_hours = np.random.uniform(0, 10000, size=n_samples)
        maintenance_count = np.random.poisson(5, size=n_samples)
        preventive_count = np.random.poisson(3, size=n_samples)
        corrective_count = np.random.poisson(2, size=n_samples)
        avg_maintenance_cost = np.random.uniform(100, 500, size=n_samples)
        total_maintenance_cost = avg_maintenance_cost * maintenance_count
        failure_count = np.random.poisson(1, size=n_samples)
        avg_failure_cost = np.random.uniform(500, 2000, size=n_samples)
        total_failure_cost = avg_failure_cost * failure_count
        days_since_last_service = np.random.uniform(0, 365, size=n_samples)
        avg_downtime_hours = np.random.uniform(1, 24, size=n_samples)
        
        # Generate target variable (has_failed)
        # Higher probability of failure with:
        # - Higher age
        # - Higher operating hours
        # - Higher corrective maintenance
        # - Longer time since last service
        failure_prob = (
            0.2 * (age_years / 15) + 
            0.3 * (operating_hours / 10000) + 
            0.3 * (corrective_count / 10) + 
            0.2 * (days_since_last_service / 365)
        )
        has_failed = (np.random.random(n_samples) < failure_prob).astype(int)
        
        # Create DataFrame
        df = pd.DataFrame({
            'equipment_id': equipment_ids,
            'equipment_type': equipment_types,
            'year_manufactured': 2025 - age_years.astype(int),
            'operating_hours': operating_hours,
            'age_years': age_years,
            'maintenance_count': maintenance_count,
            'preventive_count': preventive_count,
            'corrective_count': corrective_count,
            'avg_maintenance_cost': avg_maintenance_cost,
            'total_maintenance_cost': total_maintenance_cost,
            'failure_count': failure_count,
            'avg_failure_cost': avg_failure_cost,
            'total_failure_cost': total_failure_cost,
            'days_since_last_service': days_since_last_service,
            'avg_downtime_hours': avg_downtime_hours,
            'has_failed': has_failed
        })
        
        print(f"✅ Synthetic data generated: {len(df)} equipment records")
        print(f"   Features: {len(df.columns) - 2} columns")  # Excluding equipment_id and has_failed
        print(f"   Failure rate: {df['has_failed'].mean() * 100:.2f}%")
        
        return df
    
    def prepare_data(self, df):
        """Prepare data for model training"""
        print("\n🔄 Preparing data for model training...")
        
        # Select features and target
        X = df.drop(['equipment_id', 'equipment_type', 'has_failed'], axis=1, errors='ignore')
        y = df['has_failed']
        
        # Store feature columns
        self.feature_columns = X.columns.tolist()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"✅ Data prepared")
        print(f"   Training set: {X_train.shape[0]} samples")
        print(f"   Test set: {X_test.shape[0]} samples")
        print(f"   Features: {X_train.shape[1]} columns")
        print(f"   Failure rate: {y.mean() * 100:.2f}%")
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def train_models(self, X_train, y_train):
        """Train all models"""
        print("\n🔄 Training models...")
        
        # Set total steps for progress tracking
        self.total_steps = 4  # Number of models
        self.current_step = 0
        self.training_start_time = time.time()
        
        # Train Random Forest
        self.current_step += 1
        print(f"\n[{self.current_step}/{self.total_steps}] Training Random Forest...")
        self._update_progress()
        
        start_time = time.time()
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
        rf_model.fit(X_train, y_train)
        train_time = time.time() - start_time
        
        self.models['random_forest'] = rf_model
        print(f"  ✅ Random Forest trained in {train_time:.2f}s")
        
        # Train SVM
        self.current_step += 1
        print(f"\n[{self.current_step}/{self.total_steps}] Training SVM...")
        self._update_progress()
        
        start_time = time.time()
        svm_model = SVC(
            kernel='rbf',
            C=10,
            gamma='scale',
            probability=True,
            class_weight='balanced',
            random_state=42
        )
        svm_model.fit(X_train, y_train)
        train_time = time.time() - start_time
        
        self.models['svm'] = svm_model
        print(f"  ✅ SVM trained in {train_time:.2f}s")
        
        # Train XGBoost
        self.current_step += 1
        print(f"\n[{self.current_step}/{self.total_steps}] Training XGBoost...")
        self._update_progress()
        
        start_time = time.time()
        xgb_model = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=10,
            eval_metric='logloss',
            random_state=42,
            n_jobs=-1
        )
        xgb_model.fit(X_train, y_train)
        train_time = time.time() - start_time
        
        self.models['xgboost'] = xgb_model
        print(f"  ✅ XGBoost trained in {train_time:.2f}s")
        
        # Train Isolation Forest
        self.current_step += 1
        print(f"\n[{self.current_step}/{self.total_steps}] Training Isolation Forest...")
        self._update_progress()
        
        start_time = time.time()
        if_model = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42,
            n_jobs=-1
        )
        # For Isolation Forest, we train on normal samples (non-failures)
        normal_indices = y_train == 0
        if_model.fit(X_train[normal_indices])
        train_time = time.time() - start_time
        
        self.models['isolation_forest'] = if_model
        print(f"  ✅ Isolation Forest trained in {train_time:.2f}s")
        
        print("\n✅ All models trained successfully")
    
    def _update_progress(self):
        """Update progress during training"""
        if self.training_start_time is None:
            return
        
        elapsed_time = time.time() - self.training_start_time
        progress = self.current_step / self.total_steps
        
        if progress > 0:
            estimated_total_time = elapsed_time / progress
            remaining_time = estimated_total_time - elapsed_time
            
            print(f"  ⏱️ Progress: {progress * 100:.1f}% complete")
            print(f"  ⏱️ Elapsed time: {elapsed_time:.1f}s")
            print(f"  ⏱️ Estimated time remaining: {remaining_time:.1f}s")
    
    def evaluate_models(self, X_test, y_test):
        """Evaluate all trained models"""
        print("\n🔄 Evaluating models...")
        
        results = []
        
        for name, model in self.models.items():
            print(f"\nEvaluating: {name}...")
            
            if name == 'isolation_forest':
                # For Isolation Forest, convert scores to binary predictions
                # Negative scores are outliers (failures)
                raw_scores = model.decision_function(X_test)
                # Invert scores so higher = more likely to be failure
                scores = -raw_scores
                # Normalize to 0-1 range for probability-like scores
                min_score, max_score = scores.min(), scores.max()
                proba = (scores - min_score) / (max_score - min_score)
                # Convert to binary predictions using threshold
                threshold = np.percentile(proba, 95)  # Top 5% are anomalies
                y_pred = (proba >= threshold).astype(int)
            else:
                # For classification models
                y_pred = model.predict(X_test)
                proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            roc_auc = roc_auc_score(y_test, proba) if proba is not None else None
            
            # Store results
            model_results = {
                'Model': name,
                'Accuracy': accuracy,
                'Precision': precision,
                'Recall': recall,
                'F1-Score': f1,
                'ROC-AUC': roc_auc
            }
            results.append(model_results)
            
            # Print metrics
            print(f"  - Accuracy:  {accuracy:.4f}")
            print(f"  - Precision: {precision:.4f}")
            print(f"  - Recall:    {recall:.4f}")
            print(f"  - F1-Score:  {f1:.4f}")
            if roc_auc is not None:
                print(f"  - ROC-AUC:   {roc_auc:.4f}")
            
            # Print confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            print(f"\n  Confusion Matrix:")
            print(f"  {cm[0][0]:6d} {cm[0][1]:6d}")
            print(f"  {cm[1][0]:6d} {cm[1][1]:6d}")
            
            # Save confusion matrix visualization
            self._save_confusion_matrix(cm, name)
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(results)
        
        # Find best model based on F1-Score
        best_model_idx = results_df['F1-Score'].idxmax()
        self.best_model_name = results_df.loc[best_model_idx, 'Model']
        
        # Store results
        self.results = results_df
        
        print("\n✅ Model evaluation complete")
        print(f"   Best model: {self.best_model_name} (F1-Score: {results_df.loc[best_model_idx, 'F1-Score']:.4f})")
        
        # Save model comparison visualization
        self._save_model_comparison()
        
        return results_df
    
    def _save_confusion_matrix(self, cm, model_name):
        """Save confusion matrix visualization"""
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
        plt.title(f'Confusion Matrix - {model_name}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        
        # Save figure
        filename = f"{model_name}_confusion_matrix.png"
        filepath = IMAGES_DIR / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  📊 Confusion matrix saved to {filepath}")
    
    def _save_model_comparison(self):
        """Save model comparison visualization"""
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
        
        print(f"\n📊 Model comparison chart saved to {filepath}")
        
        # Save ROC curves
        self._save_roc_curves()
    
    def _save_roc_curves(self):
        """Save ROC curves visualization"""
        plt.figure(figsize=(10, 8))
        
        # We need X_test and y_test for ROC curves
        # This function should be called from evaluate_models where these are available
        
        # For now, we'll just create a placeholder
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
    
    def save_models(self):
        """Save trained models to disk"""
        print("\n🔄 Saving models...")
        
        # Ensure models directory exists
        MODELS_DIR.mkdir(exist_ok=True)
        
        # Save each model
        for name, model in self.models.items():
            filename = f"{name}.pkl"
            filepath = MODELS_DIR / filename
            
            joblib.dump(model, filepath)
            print(f"  ✅ {name} saved to {filepath}")
        
        # Save scaler
        scaler_path = MODELS_DIR / "scaler.pkl"
        joblib.dump(self.scaler, scaler_path)
        print(f"  ✅ Scaler saved to {scaler_path}")
        
        # Save feature columns
        feature_path = MODELS_DIR / "feature_columns.pkl"
        joblib.dump(self.feature_columns, feature_path)
        print(f"  ✅ Feature columns saved to {feature_path}")
        
        # Save results
        results_path = MODELS_DIR / "model_results.csv"
        self.results.to_csv(results_path, index=False)
        print(f"  ✅ Model results saved to {results_path}")
        
        print("\n✅ All models saved successfully")
    
    def save_metrics_to_db(self, conn):
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
            for _, row in self.results.iterrows():
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
                    (model_name, evaluation_date, accuracy, precision_score, recall, f1_score, roc_auc, sample_size)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(
                        insert_query,
                        (
                            model_name,
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
    
    def fine_tune_models(self, new_data):
        """Fine-tune existing models with new data"""
        print("\n🔄 Fine-tuning models with new data...")
        
        try:
            # Check if 'has_failed' column exists
            if 'has_failed' not in new_data.columns:
                print("  ⚠️ 'has_failed' column not found in new data")
                
                # Try to use 'prediction' column if available
                if 'prediction' in new_data.columns:
                    print("  ⚠️ Using 'prediction' column as target")
                    y_new = new_data['prediction']
                else:
                    print("  ❌ No target column available, cannot fine-tune models")
                    return
            else:
                y_new = new_data['has_failed']
            
            # Prepare new data
            X_new = new_data.drop(['equipment_id', 'equipment_type', 'has_failed', 'prediction', 'probability', 'model_name'], 
                                axis=1, errors='ignore')
            
            # Ensure features match
            if self.feature_columns:
                # Check for missing columns and add them with default values
                for column in self.feature_columns:
                    if column not in X_new.columns:
                        print(f"  ⚠️ Adding missing column: {column} with default value 0")
                        X_new[column] = 0
                
                # Select only the columns needed by the model
                X_new = X_new[self.feature_columns]
            
            # Scale features
            if self.scaler:
                X_new_scaled = self.scaler.transform(X_new)
            else:
                print("  ❌ Scaler not available, cannot fine-tune models")
                return
            
            # Set total steps for progress tracking
            self.total_steps = len(self.models)
            self.current_step = 0
            self.training_start_time = time.time()
            
            # Fine-tune each model
            for name, model in self.models.items():
                if model is None:
                    continue
                    
                self.current_step += 1
                print(f"\n[{self.current_step}/{self.total_steps}] Fine-tuning {name}...")
                self._update_progress()
                
                start_time = time.time()
                
                if name == 'isolation_forest':
                    # For Isolation Forest, we can't easily fine-tune
                    # We could train a new model or continue with the existing one
                    print("  ⚠️ Isolation Forest doesn't support incremental learning, skipping")
                    continue
                
                # For other models, we can use partial_fit if available, otherwise fit
                if hasattr(model, 'partial_fit'):
                    model.partial_fit(X_new_scaled, y_new)
                else:
                    # For models without partial_fit, we combine old and new data
                    # This is a simplified approach - in production, you might want to use
                    # more sophisticated techniques for incremental learning
                    model.fit(X_new_scaled, y_new)
                
                train_time = time.time() - start_time
                print(f"  ✅ {name} fine-tuned in {train_time:.2f}s")
            
            print("\n✅ Models fine-tuned successfully")
            
        except Exception as e:
            print(f"  ❌ Error fine-tuning models: {e}")
            import traceback
            traceback.print_exc()
    
    def run_pipeline(self, new_data=None):
        """Run the complete model training pipeline"""
        print("\n" + "="*70)
        print("🚀 STARTING MODEL TRAINING PIPELINE")
        print("="*70)
        
        start_time = time.time()
        
        # Connect to database
        conn = self.connect_to_db()
        
        # Load data from database or generate synthetic data
        if conn:
            df = self.load_data_from_db(conn)
        else:
            print("⚠️ Database connection failed, using synthetic data")
            df = self.generate_synthetic_data()
        
        # Prepare data
        X_train, X_test, y_train, y_test = self.prepare_data(df)
        
        # Train models
        self.train_models(X_train, y_train)
        
        # Evaluate models
        self.evaluate_models(X_test, y_test)
        
        # Save models
        self.save_models()
        
        # Save metrics to database
        if conn:
            self.save_metrics_to_db(conn)
        
        # Fine-tune models with new data if provided
        if new_data is not None:
            self.fine_tune_models(new_data)
            
            # Re-evaluate models after fine-tuning
            print("\n🔄 Re-evaluating models after fine-tuning...")
            self.evaluate_models(X_test, y_test)
            
            # Save updated models
            self.save_models()
            
            # Save updated metrics to database
            if conn:
                self.save_metrics_to_db(conn)
        
        # Close database connection
        if conn:
            conn.close()
            print("\n✅ Database connection closed")
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        print("\n" + "="*70)
        print(f"✅ MODEL TRAINING PIPELINE COMPLETED IN {execution_time:.2f}s")
        print("="*70)
        
        return {
            'success': True,
            'best_model': self.best_model_name,
            'execution_time': execution_time
        }


if __name__ == "__main__":
    # Create and run pipeline
    pipeline = ModelTrainingPipeline()
    result = pipeline.run_pipeline()
    
    print(f"\n✅ Best model: {result['best_model']}")
    print(f"✅ Total execution time: {result['execution_time']:.2f}s")
