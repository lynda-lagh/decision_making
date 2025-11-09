#!/usr/bin/env python
# coding: utf-8

# # Complete Model Training Process
# 
# This script demonstrates the full model training process for all models in the predictive maintenance system:
# 1. Data loading and preprocessing
# 2. Feature engineering
# 3. Training baseline models
# 4. Training advanced models
# 5. Creating the hybrid model
# 6. Model evaluation and comparison

# ## Import Libraries

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import time
import warnings
warnings.filterwarnings('ignore')

# Data preprocessing
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE

# Metrics
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Models
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

# Set plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

print("✅ Libraries imported successfully")

# ## 1. Data Loading and Preprocessing

print("\n🔄 Loading data...")

# Load data (using synthetic data since we don't have access to the actual data)
# In a real scenario, you would load your actual dataset
def generate_synthetic_data(n_samples=200000, n_features=21, failure_rate=0.03, random_state=42):
    """Generate synthetic data for predictive maintenance"""
    np.random.seed(random_state)
    
    # Generate features
    X = np.random.randn(n_samples, n_features)
    
    # Generate target variable with specified failure rate
    y = np.zeros(n_samples)
    failure_indices = np.random.choice(n_samples, size=int(n_samples * failure_rate), replace=False)
    y[failure_indices] = 1
    
    # Create feature names
    feature_names = [
        'temp_vibration_ratio', 'pressure_temp_ratio', 'temp_coolant_diff',
        'vibration', 'vibration_change_24h', 'vibration_rolling_std_24h',
        'temperature_change_7d', 'oil_pressure_rolling_std_24h', 'oil_pressure',
        'temperature_rolling_std_24h', 'temperature_is_increasing',
        'vibration_is_increasing', 'temperature_rolling_mean_24h', 'temperature',
        'vibration_rolling_mean_24h', 'pressure_change_24h', 'pressure',
        'humidity_rolling_mean_24h', 'humidity', 'voltage_rolling_std_24h', 'voltage'
    ]
    
    # Create DataFrame
    df = pd.DataFrame(X, columns=feature_names)
    df['is_anomaly'] = y
    
    # Add equipment_id and timestamp columns
    equipment_ids = [f"EQ-{i:03d}" for i in range(1, 401)]
    df['equipment_id'] = np.random.choice(equipment_ids, size=n_samples)
    
    # Create timestamps spanning 5 years
    start_date = pd.Timestamp('2020-01-01')
    end_date = pd.Timestamp('2025-01-01')
    timestamps = pd.date_range(start=start_date, end=end_date, periods=n_samples)
    df['timestamp'] = np.random.choice(timestamps, size=n_samples)
    
    return df

# Generate synthetic data
df = generate_synthetic_data()
print(f"Data shape: {df.shape}")
print(f"Anomaly rate: {df['is_anomaly'].mean()*100:.2f}%")
print("\nSample data:")
print(df.head())

# ## 2. Feature Engineering

print("\n🔄 Preparing features...")

# Select features
X = df.drop(['is_anomaly', 'equipment_id', 'timestamp'], axis=1)
y = df['is_anomaly']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Train: {X_train.shape}, Test: {X_test.shape}")

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("✅ Features scaled")

# Handle class imbalance with SMOTE
smote = SMOTE(random_state=42, sampling_strategy=0.5)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train_scaled, y_train)
print(f"Original training data shape: {X_train_scaled.shape}")
print(f"Balanced training data shape: {X_train_balanced.shape}")
print(f"Original anomaly rate: {y_train.mean()*100:.2f}%")
print(f"Balanced anomaly rate: {y_train_balanced.mean()*100:.2f}%")

# ## 3. Training Baseline Models

print("\n🔄 Training baseline models...")

# Define baseline models
baseline_models = {
    'Logistic Regression': LogisticRegression(
        max_iter=1000, 
        random_state=42, 
        class_weight='balanced'
    ),
    'Decision Tree': DecisionTreeClassifier(
        max_depth=5, 
        min_samples_split=10,
        class_weight='balanced', 
        random_state=42
    ),
    'Random Forest': RandomForestClassifier(
        n_estimators=100, 
        max_depth=10, 
        random_state=42, 
        n_jobs=-1, 
        class_weight='balanced'
    )
}

# Train and evaluate baseline models
baseline_results = []

for name, model in baseline_models.items():
    print(f"\nTraining: {name}...")
    start_time = time.time()
    
    # Train model
    model.fit(X_train_balanced, y_train_balanced)
    train_time = time.time() - start_time
    
    # Make predictions
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1] if hasattr(model, 'predict_proba') else None
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba) if y_pred_proba is not None else None
    
    # Store results
    baseline_results.append({
        'Model': name,
        'Accuracy': accuracy,
        'Precision': precision,
        'Recall': recall,
        'F1-Score': f1,
        'ROC-AUC': roc_auc,
        'Train Time (s)': train_time
    })
    
    # Print metrics
    print(f"  ✅ Trained in {train_time:.2f}s")
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

# Create DataFrame with results
baseline_results_df = pd.DataFrame(baseline_results)
print("\n✅ Baseline models trained and evaluated")
print("\nBaseline Model Results:")
print(baseline_results_df.to_string(index=False))

# ## 4. Training Advanced Models

print("\n🔄 Training advanced models...")

# Define advanced models
advanced_models = {
    'SVM': SVC(
        kernel='rbf', 
        C=10, 
        gamma='scale',
        probability=True, 
        class_weight='balanced', 
        random_state=42
    ),
    'XGBoost': XGBClassifier(
        n_estimators=100, 
        max_depth=6, 
        learning_rate=0.1, 
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=10,  # Handle class imbalance
        eval_metric='logloss',
        random_state=42, 
        n_jobs=-1
    )
}

# Train and evaluate advanced models
advanced_results = []

for name, model in advanced_models.items():
    print(f"\nTraining: {name}...")
    start_time = time.time()
    
    # Train model
    model.fit(X_train_balanced, y_train_balanced)
    train_time = time.time() - start_time
    
    # Make predictions
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1] if hasattr(model, 'predict_proba') else None
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba) if y_pred_proba is not None else None
    
    # Store results
    advanced_results.append({
        'Model': name,
        'Accuracy': accuracy,
        'Precision': precision,
        'Recall': recall,
        'F1-Score': f1,
        'ROC-AUC': roc_auc,
        'Train Time (s)': train_time
    })
    
    # Print metrics
    print(f"  ✅ Trained in {train_time:.2f}s")
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

# Create DataFrame with results
advanced_results_df = pd.DataFrame(advanced_results)
print("\n✅ Advanced models trained and evaluated")
print("\nAdvanced Model Results:")
print(advanced_results_df.to_string(index=False))

# ## 5. Creating the Hybrid Model

print("\n🔄 Creating hybrid SVM+XGBoost model...")

# Get trained models
svm_model = advanced_models['SVM']
xgb_model = advanced_models['XGBoost']

# Function to create hybrid predictions
def hybrid_predict(X, svm_model, xgb_model):
    """
    Generate hybrid predictions using SVM and XGBoost models
    
    Args:
        X: Feature matrix
        svm_model: Trained SVM model
        xgb_model: Trained XGBoost model
        
    Returns:
        y_pred: Binary predictions
        y_pred_proba: Probability predictions
    """
    # Get individual model predictions
    svm_proba = svm_model.predict_proba(X)[:, 1]
    xgb_proba = xgb_model.predict_proba(X)[:, 1]
    
    # Weighted combination (0.4*SVM + 0.6*XGBoost)
    hybrid_proba = 0.4 * svm_proba + 0.6 * xgb_proba
    
    # Convert probabilities to predictions (threshold = 0.5)
    hybrid_pred = (hybrid_proba >= 0.5).astype(int)
    
    return hybrid_pred, hybrid_proba

# Generate hybrid predictions
start_time = time.time()
y_hybrid_pred, y_hybrid_proba = hybrid_predict(X_test_scaled, svm_model, xgb_model)
hybrid_time = time.time() - start_time

# Calculate metrics for hybrid model
hybrid_accuracy = accuracy_score(y_test, y_hybrid_pred)
hybrid_precision = precision_score(y_test, y_hybrid_pred)
hybrid_recall = recall_score(y_test, y_hybrid_pred)
hybrid_f1 = f1_score(y_test, y_hybrid_pred)
hybrid_roc_auc = roc_auc_score(y_test, y_hybrid_proba)

# Print metrics
print(f"\nHybrid Model (SVM+XGBoost) Results:")
print(f"  - Accuracy:  {hybrid_accuracy:.4f}")
print(f"  - Precision: {hybrid_precision:.4f}")
print(f"  - Recall:    {hybrid_recall:.4f}")
print(f"  - F1-Score:  {hybrid_f1:.4f}")
print(f"  - ROC-AUC:   {hybrid_roc_auc:.4f}")

# Print confusion matrix
hybrid_cm = confusion_matrix(y_test, y_hybrid_pred)
print(f"\nConfusion Matrix:")
print(f"{hybrid_cm[0][0]:6d} {hybrid_cm[0][1]:6d}")
print(f"{hybrid_cm[1][0]:6d} {hybrid_cm[1][1]:6d}")

# Add hybrid model to results
hybrid_results = [{
    'Model': 'Hybrid (SVM+XGBoost)',
    'Accuracy': hybrid_accuracy,
    'Precision': hybrid_precision,
    'Recall': hybrid_recall,
    'F1-Score': hybrid_f1,
    'ROC-AUC': hybrid_roc_auc,
    'Train Time (s)': advanced_models['SVM'].train_time + advanced_models['XGBoost'].train_time
}]

# ## 6. Model Evaluation and Comparison

print("\n🔄 Comparing all models...")

# Combine all results
all_results = pd.concat([
    baseline_results_df,
    advanced_results_df,
    pd.DataFrame(hybrid_results)
])

# Sort by F1-Score
all_results = all_results.sort_values('F1-Score', ascending=False).reset_index(drop=True)

print("\nAll Models Comparison:")
print(all_results.to_string(index=False))

# Plot model comparison
plt.figure(figsize=(14, 8))

# Set width of bars
barWidth = 0.15
metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
models = all_results['Model'].tolist()

# Set position of bars on X axis
r = np.arange(len(models))

# Make the plot
for i, metric in enumerate(metrics):
    values = all_results[metric].tolist()
    plt.bar(r + i * barWidth, values, width=barWidth, label=metric)

# Add labels and legend
plt.xlabel('Models', fontweight='bold', fontsize=14)
plt.ylabel('Score', fontweight='bold', fontsize=14)
plt.title('Model Comparison', fontweight='bold', fontsize=16)
plt.xticks(r + barWidth * 2, models, rotation=45, ha='right')
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('../report_figures/model_comparison.png', dpi=300, bbox_inches='tight')
plt.show()

# Plot ROC curves
plt.figure(figsize=(10, 8))

# Generate ROC curve for each model
for model_name in models:
    if model_name == 'Hybrid (SVM+XGBoost)':
        fpr, tpr, _ = roc_curve(y_test, y_hybrid_proba)
        roc_auc = auc(fpr, tpr)
    else:
        # Find the model in our dictionaries
        if model_name in baseline_models:
            model = baseline_models[model_name]
        else:
            model = advanced_models[model_name]
        
        # Get probabilities
        if hasattr(model, 'predict_proba'):
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
            fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
            roc_auc = auc(fpr, tpr)
        else:
            continue
    
    plt.plot(fpr, tpr, lw=2, label=f'{model_name} (AUC = {roc_auc:.3f})')

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

plt.tight_layout()
plt.savefig('../report_figures/roc_curves.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n✅ All models trained, evaluated, and compared successfully!")
print("✅ Figures saved to ../report_figures/")
