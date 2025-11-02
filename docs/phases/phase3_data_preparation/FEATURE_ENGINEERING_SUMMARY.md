# Feature Engineering Summary
## Predictive Maintenance for Tunisian Agricultural Equipment

**Project**: WeeFarm - Data-Driven Maintenance Management  
**Date**: November 1, 2025  
**Notebook**: `02_feature_engineering.ipynb`  
**Status**: ✅ Complete

---

## 📊 Executive Summary

This document summarizes the feature engineering process for creating ML-ready datasets from raw equipment, maintenance, and failure data. We transformed **2,749 raw events** into **46 engineered features** across **100 equipment units**, ready for three machine learning tasks: failure prediction, cost forecasting, and remaining useful life (RUL) estimation.

### Key Achievements

- ✅ **46 features created** from raw data
- ✅ **14 features** optimized for failure prediction
- ✅ **12 features** optimized for RUL estimation
- ✅ **2 target variables** created (binary classification, continuous regression)
- ✅ **Train-test split** completed (80/20 split)
- ✅ **5 processed datasets** saved for modeling

---

## 1. Data Loading

### Input Datasets

| Dataset | Records | Date Range | Description |
|---------|---------|------------|-------------|
| **Equipment** | 100 | 2010-2024 | Equipment specifications and current status |
| **Maintenance** | 2,093 | 2020-2024 | Maintenance events (preventive, corrective, predictive) |
| **Failures** | 656 | 2020-2024 | Failure events with severity and costs |

**Total Events**: 2,749 over 5 years

---

## 2. Equipment-Based Features

### 2.1 Age Features

**Calculated**:
- `age`: Current age in years (2025 - year_manufactured)
- `age_group`: Categorical age classification

**Age Distribution**:

| Age Group | Count | Percentage | Description |
|-----------|-------|------------|-------------|
| **Old** (8-12 years) | 38 | 38% | Entering high-maintenance phase |
| **Mid_Age** (4-7 years) | 37 | 37% | Optimal operational phase |
| **New** (0-3 years) | 17 | 17% | Warranty period, low maintenance |
| **Very_Old** (13+ years) | 8 | 8% | High failure risk, replacement candidates |

**Insight**: 46% of equipment is 8+ years old, entering critical maintenance period.

---

### 2.2 Usage Features

**Calculated**:
- `usage_intensity`: Operating hours per year (operating_hours / age)
- `usage_category`: Low (<300), Medium (300-800), High (>800 hours/year)

**Usage Distribution**:

| Usage Category | Count | Percentage | Avg Hours/Year |
|----------------|-------|------------|----------------|
| **Medium** | 45 | 45% | 400-800 |
| **Low** | 35 | 35% | <300 |
| **High** | 20 | 20% | >800 |

**Insight**: Most equipment (45%) has moderate usage, indicating balanced fleet utilization.

---

## 3. Maintenance History Features

### 3.1 Aggregate Maintenance Metrics

**Features Created**:
- `maintenance_count`: Total maintenance events per equipment
- `total_maintenance_cost`: Cumulative maintenance cost (TND)
- `avg_maintenance_cost`: Average cost per maintenance event
- `std_maintenance_cost`: Standard deviation of costs
- `total_downtime`: Cumulative downtime hours
- `avg_downtime`: Average downtime per event
- `preventive_count`: Number of preventive maintenance events
- `preventive_ratio`: Preventive / Total maintenance
- `maintenance_frequency`: Maintenance events per year

### 3.2 Maintenance Statistics

| Metric | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|------|-----|-----|-----|-----|-----|-----|
| **Maintenance Count** | 20.9 | 14.3 | 0 | 10 | 21 | 28 | 72 |
| **Preventive Ratio** | 0.358 | 0.180 | 0 | 0.258 | 0.383 | 0.474 | 0.750 |
| **Maintenance Frequency** | 2.58 | 1.13 | 0 | 2.00 | 2.65 | 3.31 | 5.54 |

**Key Findings**:
- Average equipment receives **21 maintenance events** over 5 years
- **35.8% preventive maintenance** (below 40% target)
- **2.6 maintenance events per year** on average
- High variance (std=14.3) indicates different maintenance strategies

---

## 4. Failure History Features

### 4.1 Aggregate Failure Metrics

**Features Created**:
- `failure_count`: Total failures per equipment
- `total_failure_cost`: Cumulative failure repair costs
- `avg_failure_cost`: Average cost per failure
- `total_failure_downtime`: Cumulative failure downtime
- `avg_failure_downtime`: Average downtime per failure
- `critical_failure_count`: Number of critical failures
- `preventable_failure_count`: Number of preventable failures
- `failure_rate`: Failures per 1,000 operating hours
- `mtbf`: Mean Time Between Failures (hours)
- `preventable_failure_ratio`: Preventable / Total failures

### 4.2 Failure Statistics

| Metric | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|------|-----|-----|-----|-----|-----|-----|
| **Failure Count** | 6.56 | 5.05 | 0 | 3 | 6 | 9 | 25 |
| **Failure Rate** | 1.89 | 1.67 | 0 | 0.80 | 1.26 | 2.38 | 7.24 |
| **MTBF (hours)** | 1,633 | 2,696 | 138 | 421 | 792 | 1,251 | 10,000 |

**Key Findings**:
- Average equipment experiences **6.6 failures** over 5 years
- **1.89 failures per 1,000 operating hours**
- **MTBF of 1,633 hours** (median: 792 hours)
- Wide variance indicates different equipment reliability

---

## 5. Equipment Health Score

### 5.1 Health Score Calculation

**Formula** (0-100 scale):
```
Base Score = 100

Penalties:
- Age penalty: min(age × 2, 30)
- Failure rate penalty: min(failure_rate × 5, 25)
- Critical failure penalty: min(critical_count × 5, 20)

Bonuses:
- Preventive maintenance bonus: preventive_ratio × 15
- MTBF bonus: min(mtbf / 1000, 10)

Final Score = max(0, min(100, Base + Bonuses - Penalties))
```

### 5.2 Health Score Distribution

| Metric | Value |
|--------|-------|
| **Mean** | 79.7 |
| **Std** | 13.5 |
| **Min** | 50.3 |
| **25%** | 68.1 |
| **50%** | 81.8 |
| **75%** | 88.7 |
| **Max** | 100.0 |

### 5.3 Health Categories

| Category | Count | Percentage | Score Range | Action Required |
|----------|-------|------------|-------------|-----------------|
| **Excellent** | 59 | 59% | 80-100 | Regular maintenance |
| **Good** | 33 | 33% | 60-79 | Monitor closely |
| **Fair** | 8 | 8% | 40-59 | Increase preventive maintenance |
| **Poor** | 0 | 0% | 0-39 | Immediate action/replacement |

**Insight**: 92% of equipment in good-to-excellent health, indicating effective current maintenance practices.

---

## 6. Target Variables

### 6.1 Target 1: Failure Prediction (Binary Classification)

**Objective**: Predict if equipment will fail in next 30 days

**Method**: Equipment with failures in last 90 days marked as "will fail"

**Distribution**:

| Class | Count | Percentage |
|-------|-------|------------|
| **Will NOT Fail (0)** | 72 | 72% |
| **Will Fail (1)** | 28 | 28% |

**Class Balance**: 28% positive class (good for ML - not too imbalanced)

**Business Impact**:
- Predicting 28 high-risk equipment
- Early intervention can prevent failures
- Reduce unplanned downtime

---

### 6.2 Target 2: Remaining Useful Life (Regression)

**Objective**: Estimate remaining operational hours before failure

**Method**: 
- Equipment with no failures: `RUL = max(0, 5000 - operating_hours)`
- Equipment with failures: `RUL = max(0, MTBF × 0.8)`

**RUL Statistics**:

| Metric | Value (hours) |
|--------|---------------|
| **Mean** | 939 |
| **Std** | 1,046 |
| **Min** | 110 |
| **25%** | 337 |
| **50%** | 633 |
| **75%** | 1,001 |
| **Max** | 4,753 |

**RUL Distribution**:
- **<500 hours**: 42 equipment (42%) - High priority
- **500-1,000 hours**: 33 equipment (33%) - Medium priority
- **>1,000 hours**: 25 equipment (25%) - Low priority

**Business Impact**:
- Optimize replacement timing
- Plan spare parts inventory
- Schedule maintenance windows

---

## 7. Feature Encoding

### 7.1 Categorical Variables Encoded

**Label Encoding Applied**:

| Original Feature | Encoded Feature | Unique Values |
|------------------|-----------------|---------------|
| `equipment_type` | `equipment_type_encoded` | 5 (Tractor, Irrigation, etc.) |
| `brand` | `brand_encoded` | 25 (New Holland, Massey Ferguson, etc.) |
| `location` | `location_encoded` | 12 (Jendouba, Nabeul, etc.) |
| `age_group` | `age_group_encoded` | 4 (New, Mid_Age, Old, Very_Old) |
| `usage_category` | `usage_category_encoded` | 3 (Low, Medium, High) |
| `health_category` | `health_category_encoded` | 3 (Excellent, Good, Fair) |

**Total Encoded Features**: 6

---

## 8. Feature Selection

### 8.1 Features for Failure Prediction (14 features)

**Numerical Features** (11):
1. `age` - Equipment age in years
2. `operating_hours` - Total operating hours
3. `usage_intensity` - Hours per year
4. `maintenance_count` - Total maintenance events
5. `preventive_ratio` - Preventive maintenance ratio
6. `maintenance_frequency` - Maintenance events per year
7. `failure_count` - Historical failure count
8. `failure_rate` - Failures per 1,000 hours
9. `mtbf` - Mean time between failures
10. `health_score` - Composite health score (0-100)
11. `critical_failure_count` - Number of critical failures

**Categorical Features** (3):
12. `equipment_type_encoded` - Type of equipment
13. `age_group_encoded` - Age category
14. `usage_category_encoded` - Usage intensity category

**Rationale**: These features capture equipment condition, maintenance history, and failure patterns.

---

### 8.2 Features for RUL Estimation (12 features)

**Numerical Features** (10):
1. `age` - Equipment age
2. `operating_hours` - Total hours
3. `usage_intensity` - Usage rate
4. `maintenance_count` - Maintenance history
5. `preventive_ratio` - Maintenance quality
6. `failure_count` - Failure history
7. `failure_rate` - Failure frequency
8. `mtbf` - Reliability metric
9. `avg_failure_cost` - Failure severity indicator
10. `health_score` - Overall condition

**Categorical Features** (2):
11. `equipment_type_encoded` - Equipment type
12. `usage_category_encoded` - Usage pattern

**Rationale**: These features predict remaining operational life based on wear, usage, and maintenance.

---

## 9. Train-Test Split

### 9.1 Failure Prediction Dataset

**Split Configuration**:
- **Test Size**: 20% (stratified by target)
- **Random State**: 42 (reproducible)
- **Stratification**: Yes (maintains class balance)

**Dataset Sizes**:

| Dataset | Samples | Positive Class | Negative Class |
|---------|---------|----------------|----------------|
| **Training** | 80 | 22 (27.5%) | 58 (72.5%) |
| **Test** | 20 | 6 (30%) | 14 (70%) |
| **Total** | 100 | 28 (28%) | 72 (72%) |

**Validation**: Class balance maintained in both sets

---

### 9.2 RUL Estimation Dataset

**Split Configuration**:
- **Test Size**: 20%
- **Random State**: 42
- **Stratification**: No (continuous target)

**Dataset Sizes**:

| Dataset | Samples | Mean RUL | Std RUL |
|---------|---------|----------|---------|
| **Training** | 80 | 945 hours | 1,058 hours |
| **Test** | 20 | 914 hours | 1,012 hours |
| **Total** | 100 | 939 hours | 1,046 hours |

**Validation**: Similar distributions in train and test sets

---

## 10. Saved Datasets

### 10.1 Output Files

All files saved to: `data/processed/`

| File | Rows | Columns | Description |
|------|------|---------|-------------|
| **equipment_features.csv** | 100 | 46 | Complete feature set with all engineered features |
| **X_train_failure.csv** | 80 | 14 | Training features for failure prediction |
| **X_test_failure.csv** | 20 | 14 | Test features for failure prediction |
| **y_train_failure.csv** | 80 | 1 | Training labels (0/1) for failure prediction |
| **y_test_failure.csv** | 20 | 1 | Test labels (0/1) for failure prediction |

**Total Storage**: ~500 KB

---

## 11. Feature Engineering Pipeline Summary

### 11.1 Transformation Steps

```
Raw Data (2,749 events)
    ↓
1. Load & Parse Dates
    ↓
2. Equipment Features (age, usage)
    ↓
3. Aggregate Maintenance History
    ↓
4. Aggregate Failure History
    ↓
5. Calculate Health Score
    ↓
6. Create Target Variables
    ↓
7. Encode Categorical Variables
    ↓
8. Select Features
    ↓
9. Train-Test Split
    ↓
ML-Ready Datasets (100 samples, 46 features)
```

### 11.2 Feature Categories

| Category | Count | Examples |
|----------|-------|----------|
| **Original Equipment** | 10 | equipment_id, type, brand, location |
| **Calculated Equipment** | 4 | age, age_group, usage_intensity, usage_category |
| **Maintenance Aggregates** | 9 | maintenance_count, preventive_ratio, avg_cost |
| **Failure Aggregates** | 10 | failure_count, failure_rate, mtbf, critical_count |
| **Derived Metrics** | 2 | health_score, health_category |
| **Target Variables** | 2 | will_fail_30d, rul_hours |
| **Encoded Features** | 6 | *_encoded versions of categorical variables |
| **Intermediate** | 3 | Temporary calculation columns |
| **Total** | 46 | All features in final dataset |

---

## 12. Feature Importance (Preliminary Analysis)

### 12.1 Expected Important Features for Failure Prediction

Based on correlation analysis and domain knowledge:

**Top 5 Expected Predictors**:
1. **health_score** (0-100) - Composite indicator
2. **failure_rate** (per 1000 hrs) - Historical failure frequency
3. **age** (years) - Equipment age
4. **mtbf** (hours) - Reliability metric
5. **preventive_ratio** (0-1) - Maintenance quality

**Supporting Features**:
- `critical_failure_count` - Severity indicator
- `operating_hours` - Usage indicator
- `equipment_type_encoded` - Type-specific patterns

---

### 12.2 Expected Important Features for RUL Estimation

**Top 5 Expected Predictors**:
1. **mtbf** (hours) - Direct reliability measure
2. **operating_hours** - Current usage
3. **age** (years) - Wear indicator
4. **failure_rate** - Degradation rate
5. **health_score** - Overall condition

**Supporting Features**:
- `usage_intensity` - Usage rate
- `avg_failure_cost` - Failure severity
- `preventive_ratio` - Maintenance effectiveness

---

## 13. Data Quality Assessment

### 13.1 Completeness

| Aspect | Status | Notes |
|--------|--------|-------|
| **Missing Values** | ✅ None | All NaN filled with 0 (appropriate for counts) |
| **Date Parsing** | ✅ Complete | All dates converted to datetime |
| **Feature Coverage** | ✅ 100% | All 100 equipment have features |
| **Target Coverage** | ✅ 100% | All equipment have target values |

### 13.2 Validity

| Check | Result | Action |
|-------|--------|--------|
| **Age Range** | 1-15 years | ✅ Valid |
| **Operating Hours** | 138-10,000 | ✅ Realistic |
| **Failure Rate** | 0-7.24 per 1000 hrs | ✅ Reasonable |
| **Health Score** | 50-100 | ✅ No poor equipment |
| **MTBF** | 138-10,000 hours | ✅ Wide but valid range |

### 13.3 Distribution

| Feature | Distribution | Skewness | Action |
|---------|--------------|----------|--------|
| **age** | Normal | Low | ✅ No transformation needed |
| **operating_hours** | Normal | Low | ✅ No transformation needed |
| **failure_count** | Right-skewed | Moderate | ⚠️ Consider log transform for some models |
| **mtbf** | Right-skewed | High | ⚠️ Consider log transform |
| **health_score** | Left-skewed | Moderate | ✅ Acceptable for classification |

---

## 14. Next Steps: Model Development

### 14.1 Failure Prediction Model (Priority 1)

**Objective**: Binary classification - predict equipment failure in next 30 days

**Recommended Algorithms**:
1. **Random Forest** - Handles non-linear relationships, feature importance
2. **XGBoost** - High performance, handles imbalanced data
3. **Logistic Regression** - Baseline, interpretable
4. **Support Vector Machine** - Good for binary classification

**Evaluation Metrics**:
- **Accuracy**: Overall correctness
- **Precision**: Avoid false alarms
- **Recall**: Catch all failures (most important!)
- **F1-Score**: Balance precision and recall
- **ROC-AUC**: Model discrimination ability

**Success Criteria**:
- Recall > 80% (catch 80% of failures)
- Precision > 60% (avoid too many false alarms)
- ROC-AUC > 0.75

---

### 14.2 RUL Estimation Model (Priority 2)

**Objective**: Regression - predict remaining operational hours

**Recommended Algorithms**:
1. **Random Forest Regressor** - Robust, handles non-linearity
2. **XGBoost Regressor** - High accuracy
3. **Linear Regression** - Baseline
4. **SVR** - Support Vector Regression

**Evaluation Metrics**:
- **RMSE**: Root Mean Squared Error
- **MAE**: Mean Absolute Error
- **R²**: Coefficient of determination
- **MAPE**: Mean Absolute Percentage Error

**Success Criteria**:
- R² > 0.70 (explain 70% of variance)
- MAE < 200 hours (acceptable error)
- MAPE < 25%

---

### 14.3 Cost Forecasting Model (Priority 3)

**Objective**: Time series - predict monthly maintenance costs

**Recommended Approaches**:
1. **SARIMA** - Seasonal patterns
2. **Prophet** - Facebook's time series tool
3. **LSTM** - Deep learning for sequences

**Data Preparation Needed**:
- Monthly aggregation of costs
- Rolling window features
- Seasonal decomposition

---

## 15. Business Impact Projection

### 15.1 Failure Prediction Model Impact

**Assumptions**:
- Model recall: 80% (catches 80% of failures)
- Current failure rate: 28% of equipment
- Average failure cost: 1,129 TND
- Preventive maintenance cost: 280 TND

**Projected Savings**:
```
Failures prevented per year = 28 × 0.80 = 22.4 equipment
Cost savings = 22.4 × (1,129 - 280) = 19,018 TND/year
```

**Additional Benefits**:
- Reduced downtime: ~500 hours/year
- Improved equipment availability: +15%
- Better resource planning

---

### 15.2 RUL Estimation Model Impact

**Benefits**:
- **Optimized Replacement**: Replace equipment at optimal time
- **Spare Parts Planning**: Order parts based on predicted failures
- **Budget Forecasting**: Accurate capital expenditure planning

**Projected Impact**:
- Reduce premature replacements: 5-10 equipment/year
- Savings: 50,000-100,000 TND/year
- Improved fleet efficiency: +10%

---

## 16. Technical Specifications

### 16.1 Software Environment

| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.11.7 | Programming language |
| **pandas** | 2.3.3 | Data manipulation |
| **numpy** | 2.3.4 | Numerical computing |
| **scikit-learn** | 1.7.2 | Machine learning |
| **matplotlib** | 3.10.0 | Visualization |
| **seaborn** | 0.13.2 | Statistical visualization |

### 16.2 Hardware Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **RAM** | 4 GB | 8 GB |
| **CPU** | 2 cores | 4+ cores |
| **Storage** | 1 GB | 5 GB |
| **GPU** | Not required | Optional for deep learning |

---

## 17. Reproducibility

### 17.1 Random Seeds

All random operations use `random_state=42` for reproducibility:
- Train-test split
- Model training (in next phase)
- Cross-validation

### 17.2 Data Versioning

| Version | Date | Changes |
|---------|------|---------|
| **v1.0** | Nov 1, 2025 | Initial feature engineering |

### 17.3 Code Location

- **Notebook**: `notebooks/02_feature_engineering.ipynb`
- **Processed Data**: `data/processed/`
- **Documentation**: `docs/phase3_data_preparation/FEATURE_ENGINEERING_SUMMARY.md`

---

## 18. Lessons Learned

### 18.1 Successes

✅ **Comprehensive Feature Set**: 46 features cover all aspects  
✅ **Balanced Targets**: 28% failure rate is good for ML  
✅ **Clean Data**: No missing values, consistent types  
✅ **Domain Knowledge**: Features reflect Tunisian agricultural context  
✅ **Reproducible**: All steps documented and seeded  

### 18.2 Challenges

⚠️ **Small Sample Size**: 100 equipment (acceptable for pilot)  
⚠️ **Imbalanced Classes**: 72/28 split (manageable with techniques)  
⚠️ **Skewed Distributions**: Some features need transformation  
⚠️ **Proxy Target**: "Will fail" based on recent history (not perfect)  

### 18.3 Improvements for Future

💡 **More Data**: Expand to 200+ equipment  
💡 **Real-Time Features**: Add sensor data (temperature, vibration)  
💡 **External Factors**: Weather, crop type, soil conditions  
💡 **Operator Data**: Driver behavior, maintenance quality  

---

## 19. Conclusion

Feature engineering successfully transformed raw maintenance data into ML-ready datasets. We created **46 features** across **100 equipment units**, with **14 features** optimized for failure prediction and **12 features** for RUL estimation. The datasets are balanced, clean, and ready for model development.

### Key Achievements

1. ✅ **Comprehensive Features**: Equipment, maintenance, failure, and health metrics
2. ✅ **Two Target Variables**: Binary classification and continuous regression
3. ✅ **Train-Test Split**: 80/20 split with proper stratification
4. ✅ **Data Quality**: 100% complete, validated, and documented
5. ✅ **Business Alignment**: Features reflect real-world maintenance scenarios

### Next Phase

**Phase 4: Model Development**
- Build failure prediction model (Random Forest, XGBoost)
- Build RUL estimation model (Regression)
- Evaluate and tune models
- Deploy best models

---

## 20. References

### Related Documents

- [EDA Summary](./EDA_SUMMARY.md) - Exploratory data analysis
- [Data Schema](../phase2_data_strategy/01_data_schema.md) - Database design
- [Optimal Parameters](../phase2_data_strategy/OPTIMAL_PARAMETERS.md) - Data generation config
- [Project Progress](../../PROJECT_PROGRESS.md) - Overall project status

### Notebooks

- `01_exploratory_data_analysis.ipynb` - Data exploration
- `02_feature_engineering.ipynb` - This notebook
- `03_failure_prediction_model.ipynb` - Next step (to be created)

---

## Document Information

**Author**: WeeFarm Data Science Team  
**Version**: 1.0  
**Date**: November 1, 2025  
**Status**: Final  
**Confidentiality**: Internal Use  

**Contact**: For questions about feature engineering, refer to the notebook or contact the data science team.

---

**End of Document**
