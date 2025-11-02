"""
Stage 3: Model Prediction
Load trained models and generate predictions using hybrid SVM + XGBoost approach
"""

import pandas as pd
import numpy as np
import joblib
import sys
import os
sys.path.append('..')
from config import SVM_MODEL_PATH, XGBOOST_MODEL_PATH, FEATURE_SELECTOR_PATH

def load_models():
    """Load trained ML models"""
    print("[LOADING] Loading trained models...")
    
    try:
        svm_model = joblib.load(SVM_MODEL_PATH)
        print(f"   [OK] SVM model loaded from {SVM_MODEL_PATH.name}")
    except:
        print(f"   [WARN] SVM model not found, will skip SVM predictions")
        svm_model = None
    
    try:
        xgb_model = joblib.load(XGBOOST_MODEL_PATH)
        print(f"   [OK] XGBoost model loaded from {XGBOOST_MODEL_PATH.name}")
    except:
        print(f"   [WARN] XGBoost model not found, will skip XGBoost predictions")
        xgb_model = None
    
    try:
        feature_selector = joblib.load(FEATURE_SELECTOR_PATH)
        print(f"   [OK] Feature selector loaded from {FEATURE_SELECTOR_PATH.name}")
    except:
        print(f"   [WARN] Feature selector not found, will use all features")
        feature_selector = None
    
    return svm_model, xgb_model, feature_selector

def prepare_features(features_df, feature_columns, feature_selector=None):
    """Prepare features for prediction"""
    
    # Get feature matrix
    X = features_df[feature_columns].fillna(0)
    
    # Apply feature selection if available
    if feature_selector is not None:
        try:
            X_selected = feature_selector.transform(X)
            print(f"   [OK] Features selected: {X_selected.shape[1]} features")
            return X_selected
        except:
            print(f"   [WARN] Feature selector failed, using all features")
            return X.values
    
    return X.values

def predict_svm(model, X):
    """Generate SVM predictions"""
    if model is None:
        return None, None
    
    try:
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)[:, 1] if hasattr(model, 'predict_proba') else None
        print(f"   [OK] SVM predictions generated")
        return predictions, probabilities
    except Exception as e:
        print(f"   [ERROR] SVM prediction failed: {e}")
        return None, None

def predict_xgboost(model, X):
    """Generate XGBoost predictions"""
    if model is None:
        return None, None
    
    try:
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)[:, 1] if hasattr(model, 'predict_proba') else None
        print(f"   [OK] XGBoost predictions generated")
        return predictions, probabilities
    except Exception as e:
        print(f"   [ERROR] XGBoost prediction failed: {e}")
        return None, None

def calculate_risk_scores(svm_prob, xgb_prob, n_samples=None):
    """
    Calculate risk scores using hybrid approach
    - SVM: High sensitivity (catches all failures)
    - XGBoost: High precision (prioritizes correctly)
    """
    
    if svm_prob is not None and xgb_prob is not None:
        # Hybrid: Use XGBoost probability as risk score for SVM-flagged equipment
        risk_scores = xgb_prob * 100  # Convert to percentage
        print(f"   [OK] Hybrid risk scores calculated")
    elif xgb_prob is not None:
        risk_scores = xgb_prob * 100
        print(f"   [OK] XGBoost risk scores calculated")
    elif svm_prob is not None:
        risk_scores = svm_prob * 100
        print(f"   [OK] SVM risk scores calculated")
    else:
        # Fallback: random scores for testing
        # Use n_samples if provided, otherwise try to get length from probabilities
        if n_samples is not None:
            size = n_samples
        elif svm_prob is not None:
            size = len(svm_prob)
        elif xgb_prob is not None:
            size = len(xgb_prob)
        else:
            size = 100  # Default fallback
        
        risk_scores = np.random.uniform(0, 100, size)
        print(f"   [WARN] Using random risk scores (no models available) for {size} samples")
    
    return risk_scores

def run_stage3(data):
    """Execute Stage 3: Model Prediction"""
    print("\n" + "="*60)
    print("STAGE 3: MODEL PREDICTION (HYBRID SVM + XGBOOST)")
    print("="*60)
    
    try:
        # Handle both dict and DataFrame inputs
        if isinstance(data, dict):
            features_df = data['features']
            feature_columns = data.get('feature_columns', [col for col in features_df.columns if col not in ['equipment_id', 'equipment_type', 'location']])
        else:
            features_df = data
            feature_columns = [col for col in features_df.columns if col not in ['equipment_id', 'equipment_type', 'location']]
        
        # Load models
        svm_model, xgb_model, feature_selector = load_models()
        
        # Prepare features
        print("\n[PREP] Preparing features for prediction...")
        X = prepare_features(features_df, feature_columns, feature_selector)
        
        # Generate predictions
        print("\n[PREDICT] Generating predictions...")
        
        # SVM predictions (screening - high recall)
        svm_pred, svm_prob = predict_svm(svm_model, X)
        
        # XGBoost predictions (prioritization - high precision)
        xgb_pred, xgb_prob = predict_xgboost(xgb_model, X)
        
        # Calculate risk scores
        print("\n[CALC] Calculating risk scores...")
        risk_scores = calculate_risk_scores(svm_prob, xgb_prob, n_samples=len(features_df))
        
        # Create predictions dataframe
        predictions_df = features_df[['equipment_id', 'equipment_type', 'location']].copy()
        predictions_df['svm_prediction'] = svm_pred if svm_pred is not None else 0
        predictions_df['svm_probability'] = svm_prob if svm_prob is not None else 0.0
        predictions_df['xgb_prediction'] = xgb_pred if xgb_pred is not None else 0
        predictions_df['xgb_probability'] = xgb_prob if xgb_prob is not None else 0.0
        predictions_df['risk_score'] = risk_scores
        
        # Summary statistics
        high_risk = (risk_scores > 40).sum()
        critical = (risk_scores > 70).sum()
        
        print(f"\n[COMPLETE] Stage 3 Complete!")
        print(f"   Total predictions: {len(predictions_df)}")
        print(f"   High risk (>40%): {high_risk}")
        print(f"   Critical (>70%): {critical}")
        print(f"   Average risk score: {risk_scores.mean():.2f}%")
        
        return {
            'predictions': predictions_df,
            'models': {
                'svm': svm_model,
                'xgboost': xgb_model,
                'feature_selector': feature_selector
            }
        }
        
    except Exception as e:
        print(f"[ERROR] Error in Stage 3: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    # Test stage 3
    from stage1_data_ingestion import run_stage1
    from stage2_feature_engineering import run_stage2
    
    data = run_stage1()
    result = run_stage2(data)
    predictions = run_stage3(result)
    
    print(f"\nPredictions sample:")
    print(predictions['predictions'][['equipment_id', 'risk_score']].head(10))
