"""
Stage 2b: Handle Class Imbalance
=================================
Apply techniques to balance classes for better model training
"""

import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE, ADASYN
from imblearn.under_sampling import RandomUnderSampler
from imblearn.combine import SMOTETomek
from sklearn.utils.class_weight import compute_class_weight
from collections import Counter

def balance_with_smote(X, y, random_state=42):
    """
    Balance classes using SMOTE (Synthetic Minority Over-sampling Technique)
    
    Parameters:
    -----------
    X : array-like
        Feature matrix
    y : array-like
        Target labels
    random_state : int
        Random seed
        
    Returns:
    --------
    X_balanced, y_balanced : Balanced dataset
    """
    print("\n[SMOTE] Applying Synthetic Minority Over-sampling...")
    print(f"   Original distribution: {dict(Counter(y))}")
    
    smote = SMOTE(random_state=random_state)
    X_balanced, y_balanced = smote.fit_resample(X, y)
    
    print(f"   Balanced distribution: {dict(Counter(y_balanced))}")
    print(f"   [OK] Dataset balanced with SMOTE")
    
    return X_balanced, y_balanced


def balance_with_smotetomek(X, y, random_state=42):
    """
    Balance classes using SMOTETomek (SMOTE + Tomek Links)
    
    This combines over-sampling of minority class with cleaning of borderline samples
    """
    print("\n[SMOTETomek] Applying hybrid approach...")
    print(f"   Original distribution: {dict(Counter(y))}")
    
    smt = SMOTETomek(random_state=random_state)
    X_balanced, y_balanced = smt.fit_resample(X, y)
    
    print(f"   Balanced distribution: {dict(Counter(y_balanced))}")
    print(f"   [OK] Dataset balanced with SMOTETomek")
    
    return X_balanced, y_balanced


def compute_class_weights(y):
    """
    Compute class weights for imbalanced dataset
    
    Use these weights in model training:
    - XGBoost: scale_pos_weight parameter
    - Random Forest: class_weight parameter
    - Neural Networks: class_weight in fit()
    """
    print("\n[Class Weights] Computing balanced class weights...")
    
    classes = np.unique(y)
    weights = compute_class_weight('balanced', classes=classes, y=y)
    class_weight_dict = dict(zip(classes, weights))
    
    print("   Class weights:")
    for cls, weight in class_weight_dict.items():
        print(f"      Class {cls}: {weight:.2f}")
    
    return class_weight_dict


def balance_with_adasyn(X, y, random_state=42):
    """
    Balance classes using ADASYN (Adaptive Synthetic Sampling)
    
    Similar to SMOTE but focuses more on harder-to-learn samples
    """
    print("\n[ADASYN] Applying Adaptive Synthetic Sampling...")
    print(f"   Original distribution: {dict(Counter(y))}")
    
    try:
        adasyn = ADASYN(random_state=random_state)
        X_balanced, y_balanced = adasyn.fit_resample(X, y)
        
        print(f"   Balanced distribution: {dict(Counter(y_balanced))}")
        print(f"   [OK] Dataset balanced with ADASYN")
        
        return X_balanced, y_balanced
    except Exception as e:
        print(f"   [WARNING] ADASYN failed: {e}")
        print(f"   [FALLBACK] Using SMOTE instead")
        return balance_with_smote(X, y, random_state)


def run_stage2b(data, method='smote', random_state=42):
    """
    Execute Stage 2b: Balance Classes
    
    Parameters:
    -----------
    data : dict
        Dictionary containing 'features' DataFrame and 'labels' Series
    method : str
        Balancing method: 'smote', 'smotetomek', 'adasyn', 'weights'
    random_state : int
        Random seed
        
    Returns:
    --------
    dict with balanced data or class weights
    """
    print("\n" + "="*60)
    print("STAGE 2b: HANDLE CLASS IMBALANCE")
    print("="*60)
    
    try:
        features_df = data['features']
        
        # For now, we'll return the original data with class weights
        # In actual training, you'll apply the balancing method
        
        # Prepare features and labels
        # Assuming 'priority_level' or 'risk_category' is the target
        # You'll need to adjust this based on your actual target column
        
        print(f"\n[INFO] Method selected: {method.upper()}")
        print(f"[INFO] Features shape: {features_df.shape}")
        
        # Compute class weights (always useful)
        if 'priority_level' in features_df.columns:
            y = features_df['priority_level']
            X = features_df.drop('priority_level', axis=1)
            
            class_weights = compute_class_weights(y)
            
            # Apply balancing if requested
            if method == 'smote':
                X_balanced, y_balanced = balance_with_smote(X, y, random_state)
                balanced_df = pd.DataFrame(X_balanced, columns=X.columns)
                balanced_df['priority_level'] = y_balanced
                
                return {
                    'features': balanced_df,
                    'class_weights': class_weights,
                    'method': 'smote',
                    'original_size': len(X),
                    'balanced_size': len(X_balanced)
                }
            
            elif method == 'smotetomek':
                X_balanced, y_balanced = balance_with_smotetomek(X, y, random_state)
                balanced_df = pd.DataFrame(X_balanced, columns=X.columns)
                balanced_df['priority_level'] = y_balanced
                
                return {
                    'features': balanced_df,
                    'class_weights': class_weights,
                    'method': 'smotetomek',
                    'original_size': len(X),
                    'balanced_size': len(X_balanced)
                }
            
            elif method == 'adasyn':
                X_balanced, y_balanced = balance_with_adasyn(X, y, random_state)
                balanced_df = pd.DataFrame(X_balanced, columns=X.columns)
                balanced_df['priority_level'] = y_balanced
                
                return {
                    'features': balanced_df,
                    'class_weights': class_weights,
                    'method': 'adasyn',
                    'original_size': len(X),
                    'balanced_size': len(X_balanced)
                }
            
            else:  # method == 'weights'
                print(f"\n[INFO] Using class weights only (no resampling)")
                return {
                    'features': features_df,
                    'class_weights': class_weights,
                    'method': 'weights',
                    'original_size': len(X),
                    'balanced_size': len(X)
                }
        
        else:
            print(f"\n[WARNING] No priority_level column found")
            print(f"[INFO] Returning original features")
            return {
                'features': features_df,
                'class_weights': None,
                'method': 'none'
            }
        
    except Exception as e:
        print(f"[ERROR] Error in Stage 2b: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # Test stage 2b
    print("Testing Stage 2b: Handle Class Imbalance")
    
    # Create sample imbalanced data
    from sklearn.datasets import make_classification
    
    X, y = make_classification(
        n_samples=100,
        n_features=10,
        n_classes=4,
        weights=[0.1, 0.2, 0.3, 0.4],  # Imbalanced
        random_state=42
    )
    
    print(f"\nOriginal distribution: {dict(Counter(y))}")
    
    # Test SMOTE
    X_smote, y_smote = balance_with_smote(X, y)
    print(f"After SMOTE: {dict(Counter(y_smote))}")
    
    # Test class weights
    weights = compute_class_weights(y)
    print(f"\nClass weights: {weights}")
    
    print("\n[SUCCESS] Stage 2b test complete!")
