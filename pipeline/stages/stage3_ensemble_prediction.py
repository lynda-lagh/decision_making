"""
Stage 3: Ensemble Prediction Models
Three-model ensemble: Failure Probability, RUL Estimation, Anomaly Detection
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib
import sys
sys.path.append('..')
from config import MODELS_DIR

class EnsemblePredictor:
    """Three-model ensemble for predictive maintenance"""
    
    def __init__(self):
        self.rf_model = None  # Failure Probability
        self.xgb_model = None  # RUL Estimation
        self.if_model = None  # Anomaly Detection
        self.scaler = StandardScaler()
        self.feature_names = None
        
    def train_failure_probability_model(self, X, y):
        """
        Train Random Forest for failure probability prediction
        
        Args:
            X: Feature matrix
            y: Binary target (0=no failure, 1=failure)
        """
        print("   Training Failure Probability Model (Random Forest)...")
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.rf_model.fit(X, y)
        print(f"   [OK] Model trained with accuracy: {self.rf_model.score(X, y):.3f}")
        
    def train_rul_estimation_model(self, X, y):
        """
        Train XGBoost for RUL (Remaining Useful Life) estimation
        
        Args:
            X: Feature matrix
            y: RUL in days (regression target)
        """
        print("   Training RUL Estimation Model (XGBoost)...")
        self.xgb_model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1
        )
        self.xgb_model.fit(X, y)
        print(f"   [OK] Model trained with R² score: {self.xgb_model.score(X, y):.3f}")
        
    def train_anomaly_detection_model(self, X):
        """
        Train Isolation Forest for anomaly detection
        
        Args:
            X: Feature matrix (unsupervised)
        """
        print("   Training Anomaly Detection Model (Isolation Forest)...")
        self.if_model = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42,
            n_jobs=-1
        )
        self.if_model.fit(X)
        print(f"   [OK] Model trained")
        
    def predict_failure_probability(self, X):
        """
        Predict failure probability
        
        Returns:
            np.array: Probability of failure (0-1)
        """
        if self.rf_model is None:
            return np.zeros(len(X))
        
        probabilities = self.rf_model.predict_proba(X)[:, 1]
        return probabilities
    
    def predict_rul(self, X):
        """
        Predict Remaining Useful Life
        
        Returns:
            np.array: Days until failure
        """
        if self.xgb_model is None:
            return np.full(len(X), 365)
        
        rul = self.xgb_model.predict(X)
        # Clip to reasonable range (0-365 days)
        rul = np.clip(rul, 0, 365)
        return rul
    
    def predict_anomaly(self, X):
        """
        Predict anomaly score
        
        Returns:
            np.array: Anomaly score (0-100, higher = more anomalous)
        """
        if self.if_model is None:
            return np.zeros(len(X))
        
        # Get anomaly scores (-1 to 1, convert to 0-100)
        scores = self.if_model.score_samples(X)
        # Normalize to 0-100
        anomaly_scores = 50 + (scores * 50)  # Rough normalization
        anomaly_scores = np.clip(anomaly_scores, 0, 100)
        return anomaly_scores
    
    def predict_ensemble(self, X):
        """
        Generate ensemble predictions
        
        Returns:
            dict: All three predictions
        """
        failure_prob = self.predict_failure_probability(X)
        rul = self.predict_rul(X)
        anomaly_score = self.predict_anomaly(X)
        
        return {
            'failure_probability': failure_prob,
            'rul_days': rul,
            'anomaly_score': anomaly_score
        }
    
    def save_models(self, model_dir=MODELS_DIR):
        """Save trained models"""
        joblib.dump(self.rf_model, model_dir / 'rf_failure_probability.pkl')
        joblib.dump(self.xgb_model, model_dir / 'xgb_rul_estimation.pkl')
        joblib.dump(self.if_model, model_dir / 'if_anomaly_detection.pkl')
        print(f"[OK] Models saved to {model_dir}")
    
    def load_models(self, model_dir=MODELS_DIR):
        """Load trained models"""
        try:
            self.rf_model = joblib.load(model_dir / 'rf_failure_probability.pkl')
            self.xgb_model = joblib.load(model_dir / 'xgb_rul_estimation.pkl')
            self.if_model = joblib.load(model_dir / 'if_anomaly_detection.pkl')
            print(f"[OK] Models loaded from {model_dir}")
            return True
        except:
            print(f"[WARN] Could not load models from {model_dir}")
            return False

def generate_synthetic_training_data(features_df, n_samples=None):
    """
    Generate synthetic training data for model training
    (In production, use real historical data)
    
    Args:
        features_df: Feature dataframe
    
    Returns:
        tuple: (X, y_failure, y_rul)
    """
    if n_samples is None:
        n_samples = len(features_df)
    
    # Use actual features
    feature_cols = [col for col in features_df.columns 
                   if col not in ['equipment_id', 'equipment_type', 'location']]
    X = features_df[feature_cols].fillna(0).values
    
    # Synthetic failure target (based on features)
    # Equipment with high failure count, high age, low reliability = more likely to fail
    failure_score = (
        (features_df['failure_count'].fillna(0) / (features_df['failure_count'].max() + 1)) * 0.4 +
        (features_df['equipment_age_years'].fillna(0) / (features_df['equipment_age_years'].max() + 1)) * 0.3 +
        (1 - features_df['reliability_score'].fillna(50) / 100) * 0.3
    )
    y_failure = (failure_score > 0.5).astype(int)
    
    # Synthetic RUL target (days until failure)
    y_rul = (
        (1 - failure_score) * 365 +  # Base RUL
        np.random.normal(0, 30, len(failure_score))  # Add noise
    )
    y_rul = np.clip(y_rul, 1, 365)
    
    return X, y_failure, y_rul

def run_stage3(features_data):
    """Execute Stage 3: Ensemble Prediction"""
    print("\n" + "="*60)
    print("STAGE 3: ENSEMBLE PREDICTION MODELS")
    print("="*60)
    
    features_df = features_data['features']
    feature_cols = features_data['feature_columns']
    
    # Prepare features
    print("\n[STEP 1] Preparing features...")
    X = features_df[feature_cols].fillna(0).values
    print(f"   Feature matrix shape: {X.shape}")
    
    # Generate synthetic training data (in production, use real historical data)
    print("\n[STEP 2] Generating training data...")
    X_train, y_failure, y_rul = generate_synthetic_training_data(features_df)
    print(f"   Training samples: {len(X_train)}")
    print(f"   Failure samples: {y_failure.sum()}")
    
    # Initialize ensemble
    print("\n[STEP 3] Training ensemble models...")
    predictor = EnsemblePredictor()
    
    # Train models
    predictor.train_failure_probability_model(X_train, y_failure)
    predictor.train_rul_estimation_model(X_train, y_rul)
    predictor.train_anomaly_detection_model(X_train)
    
    # Generate predictions
    print("\n[STEP 4] Generating predictions...")
    predictions = predictor.predict_ensemble(X)
    
    # Create results dataframe
    results_df = features_df[['equipment_id', 'equipment_type', 'location']].copy()
    results_df['failure_probability'] = predictions['failure_probability']
    results_df['rul_days'] = predictions['rul_days'].astype(int)
    results_df['anomaly_score'] = predictions['anomaly_score']
    
    # Calculate confidence scores
    print("\n[STEP 5] Calculating confidence scores...")
    results_df['confidence_score'] = (
        (1 - np.abs(predictions['failure_probability'] - 0.5) * 2) * 100
    )
    
    # Save models
    print("\n[STEP 6] Saving models...")
    predictor.save_models()
    
    # Summary
    print(f"\n[COMPLETE] Stage 3 Complete!")
    print(f"   Predictions generated: {len(results_df)}")
    print(f"   Avg failure probability: {results_df['failure_probability'].mean():.3f}")
    print(f"   Avg RUL: {results_df['rul_days'].mean():.0f} days")
    print(f"   Avg anomaly score: {results_df['anomaly_score'].mean():.1f}")
    print(f"   Avg confidence: {results_df['confidence_score'].mean():.1f}%")
    
    return {
        'success': True,
        'predictions': results_df,
        'predictor': predictor,
        'models': {
            'failure_probability': predictor.rf_model,
            'rul_estimation': predictor.xgb_model,
            'anomaly_detection': predictor.if_model
        }
    }

if __name__ == "__main__":
    from stage2_enhanced_features import run_stage2
    from stage1_data_ingestion import run_stage1
    
    data = run_stage1()
    features_data = run_stage2(data)
    result = run_stage3(features_data)
    
    print(f"\nPredictions sample:")
    print(result['predictions'][['equipment_id', 'failure_probability', 'rul_days', 'anomaly_score']].head())
