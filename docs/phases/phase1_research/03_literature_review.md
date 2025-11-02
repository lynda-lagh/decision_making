# Phase 1: Literature Review - Predictive Maintenance & Time Series

## 1. Predictive Maintenance Overview

### Definition
Predictive Maintenance (PdM) uses data analysis, machine learning, and condition monitoring to predict when equipment failure might occur, enabling proactive maintenance scheduling.

## 2. Key Machine Learning Approaches

### Classification Models (Failure Prediction)

**Random Forest**
- Predict if equipment will fail in next N days
- Handles non-linear relationships
- Feature importance ranking
- Typical Accuracy: 75-90%

**XGBoost/LightGBM**
- High-accuracy failure prediction
- Handles imbalanced data well
- Typical Accuracy: 80-95%

### Time Series Forecasting

**ARIMA/SARIMA**
- Maintenance cost forecasting
- Good for seasonal patterns
- Best for agricultural equipment

**Prophet (Facebook)**
- Business time series with holidays/events
- Handles missing data automatically
- Easy to use

**LSTM Networks**
- Complex sequential patterns
- Requires larger datasets
- Captures long-term dependencies

## 3. Feature Engineering

### Time-Based Features
- Rolling statistics (mean, std, min, max)
- Lag features (previous costs, days since maintenance)
- Seasonal indicators (planting/harvest season)

### Equipment Features
- Age, operating hours
- Maintenance frequency
- Failure rate, MTBF

## 4. Evaluation Metrics

**Classification**: Accuracy, Precision, Recall, F1-Score
**Regression**: MAE, RMSE, MAPE, R²
**Time Series**: MAPE < 15% is good

## 5. Best Practices

1. Start with simple baseline models
2. Handle imbalanced data (failures are rare)
3. Use time series cross-validation
4. Monitor model performance over time
5. Make predictions interpretable

## 6. Recommended Approach for This Project

**Phase 5 Models**:
1. Random Forest for failure prediction
2. SARIMA for cost forecasting
3. Prophet for maintenance scheduling

**Tools**: scikit-learn, statsmodels, prophet, pandas, plotly
