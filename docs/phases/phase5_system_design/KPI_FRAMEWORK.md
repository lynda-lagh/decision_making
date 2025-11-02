# KPI Framework - WeeFarm Predictive Maintenance
## Key Performance Indicators & Metrics

**Project**: WeeFarm  
**Date**: November 1, 2025  
**Version**: 1.0  
**Status**: Design Phase

---

## 📊 Executive Summary

This document defines the Key Performance Indicators (KPIs) for measuring the success and effectiveness of the WeeFarm predictive maintenance system. KPIs are organized into four categories: Business KPIs, Technical KPIs, Operational KPIs, and Model Performance KPIs.

---

## 🎯 KPI Categories

### 1. Business KPIs (ROI & Cost)
Measure financial impact and return on investment

### 2. Technical KPIs (System Performance)
Measure system reliability and performance

### 3. Operational KPIs (Maintenance Effectiveness)
Measure maintenance operations efficiency

### 4. Model Performance KPIs (ML Accuracy)
Measure machine learning model effectiveness

---

## 💰 1. Business KPIs

### 1.1 Cost Reduction

**KPI**: Total Cost Reduction
- **Formula**: `(Baseline Cost - Current Cost) / Baseline Cost × 100%`
- **Target**: ≥40% reduction
- **Current**: 44% (from Phase 4 analysis)
- **Measurement**: Monthly
- **Dashboard**: Overview page, Analytics page

**Calculation Example**:
```
Baseline (no model): 8,454 TND/month
With model: 4,760 TND (SVM) or 4,787 TND (XGBoost)
Reduction: (8,454 - 4,760) / 8,454 = 43.7%
```

---

### 1.2 Maintenance Cost Savings

**KPI**: Preventive vs Corrective Cost Ratio
- **Formula**: `Preventive Cost / Corrective Cost`
- **Target**: <0.5 (preventive should be 2x cheaper)
- **Current**: 0.41 (280 TND vs 676 TND)
- **Measurement**: Monthly
- **Dashboard**: Analytics page

**Sub-KPIs**:
- Average preventive maintenance cost: 280 TND
- Average corrective maintenance cost: 676 TND
- Average failure repair cost: 1,129 TND

---

### 1.3 Return on Investment (ROI)

**KPI**: ROI Percentage
- **Formula**: `(Total Savings - System Cost) / System Cost × 100%`
- **Target**: >200% in first year
- **Measurement**: Quarterly
- **Dashboard**: Analytics page

**Calculation**:
```
Annual Savings: 466,671 TND (from Phase 3 analysis)
System Cost: ~50,000 TND (development + deployment)
ROI: (466,671 - 50,000) / 50,000 = 833%
```

---

### 1.4 Downtime Cost Avoidance

**KPI**: Total Downtime Hours Avoided
- **Formula**: `Prevented Failures × Average Downtime per Failure`
- **Target**: >500 hours/year
- **Measurement**: Monthly
- **Dashboard**: Analytics page

**Impact**:
- Average downtime per failure: 12 hours
- Cost per downtime hour: ~500 TND (lost productivity)
- Total impact: Hours × 500 TND

---

### 1.5 Equipment Utilization Rate

**KPI**: Equipment Availability
- **Formula**: `(Total Hours - Downtime Hours) / Total Hours × 100%`
- **Target**: >95%
- **Measurement**: Monthly
- **Dashboard**: Overview page

---

## 🔧 2. Technical KPIs

### 2.1 System Uptime

**KPI**: System Availability
- **Formula**: `(Total Time - Downtime) / Total Time × 100%`
- **Target**: >99.5%
- **Measurement**: Real-time
- **Dashboard**: Settings page

**Sub-KPIs**:
- API uptime: >99.9%
- Database uptime: >99.9%
- Dashboard uptime: >99.5%

---

### 2.2 Pipeline Execution Time

**KPI**: Average Pipeline Execution Time
- **Formula**: `Total Execution Time / Number of Runs`
- **Target**: <5 minutes for 100 equipment
- **Current**: 12.5 seconds (excellent!)
- **Measurement**: Per run
- **Dashboard**: Settings page, Predictions page

**Breakdown**:
- Data ingestion: <1 minute
- Feature engineering: <2 minutes
- Model prediction: <1 minute
- Decision engine: <30 seconds
- Output storage: <30 seconds

---

### 2.3 API Response Time

**KPI**: Average API Response Time
- **Formula**: `Total Response Time / Number of Requests`
- **Target**: <200ms for 95% of requests
- **Measurement**: Real-time
- **Dashboard**: Settings page

**By Endpoint**:
- GET requests: <100ms
- POST requests: <200ms
- Prediction endpoint: <500ms

---

### 2.4 Data Quality Score

**KPI**: Data Completeness
- **Formula**: `(Valid Records / Total Records) × 100%`
- **Target**: >99%
- **Current**: 100% (from Phase 3)
- **Measurement**: Daily
- **Dashboard**: Settings page

**Sub-KPIs**:
- Missing values: 0%
- Invalid dates: 0%
- Duplicate records: 0%
- Outliers handled: 100%

---

### 2.5 Database Performance

**KPI**: Query Execution Time
- **Formula**: `Average Query Time`
- **Target**: <100ms for 95% of queries
- **Measurement**: Real-time
- **Dashboard**: Settings page

---

## 🔄 3. Operational KPIs

### 3.1 Preventive Maintenance Ratio

**KPI**: Preventive Maintenance Percentage
- **Formula**: `(Preventive Maintenance Count / Total Maintenance Count) × 100%`
- **Target**: >50%
- **Current**: 38.7% (needs improvement)
- **Measurement**: Monthly
- **Dashboard**: Overview page, Analytics page

**Trend**: Should increase over time as model improves

---

### 3.2 Failure Prevention Rate

**KPI**: Failures Prevented
- **Formula**: `(Predicted Failures Prevented / Total Predicted Failures) × 100%`
- **Target**: >80%
- **Measurement**: Monthly
- **Dashboard**: Analytics page

**Calculation**:
```
Predicted failures: 28 equipment
Actually prevented: 22 equipment (with maintenance)
Prevention rate: 22/28 = 78.6%
```

---

### 3.3 Maintenance Schedule Compliance

**KPI**: On-Time Maintenance Completion
- **Formula**: `(Completed On Time / Total Scheduled) × 100%`
- **Target**: >90%
- **Measurement**: Weekly
- **Dashboard**: Maintenance Schedule page

**Sub-KPIs**:
- Overdue tasks: <5%
- Cancelled tasks: <10%
- Rescheduled tasks: <15%

---

### 3.4 Mean Time Between Failures (MTBF)

**KPI**: Average MTBF
- **Formula**: `Total Operating Hours / Number of Failures`
- **Target**: >2,000 hours (increasing trend)
- **Current**: 1,633 hours average
- **Measurement**: Monthly
- **Dashboard**: Analytics page

**By Equipment Type**:
- Tractors: 1,800 hours
- Harvesters: 1,500 hours
- Irrigation: 2,000 hours

---

### 3.5 Mean Time To Repair (MTTR)

**KPI**: Average Repair Time
- **Formula**: `Total Repair Time / Number of Repairs`
- **Target**: <8 hours
- **Measurement**: Monthly
- **Dashboard**: Analytics page

**By Severity**:
- Minor: <4 hours
- Moderate: <8 hours
- Critical: <16 hours

---

### 3.6 Technician Efficiency

**KPI**: Tasks Completed per Technician
- **Formula**: `Total Tasks Completed / Number of Technicians`
- **Target**: >20 tasks/month per technician
- **Measurement**: Monthly
- **Dashboard**: Maintenance Schedule page

**Sub-KPIs**:
- Average task duration: <4 hours
- Technician utilization: >80%
- First-time fix rate: >85%

---

### 3.7 Spare Parts Availability

**KPI**: Parts Availability Rate
- **Formula**: `(Parts Available / Parts Requested) × 100%`
- **Target**: >95%
- **Measurement**: Monthly
- **Dashboard**: Analytics page

---

## 🤖 4. Model Performance KPIs

### 4.1 Model Accuracy

**KPI**: Overall Prediction Accuracy
- **Formula**: `(Correct Predictions / Total Predictions) × 100%`
- **Target**: >75%
- **Current**: 75% (XGBoost), 45% (SVM)
- **Measurement**: Weekly
- **Dashboard**: Predictions page

**By Model**:
- SVM: 45% accuracy, 100% recall
- XGBoost: 75% accuracy, 50% recall
- Hybrid: 85% accuracy (target)

---

### 4.2 Model Precision

**KPI**: Prediction Precision
- **Formula**: `True Positives / (True Positives + False Positives)`
- **Target**: >60%
- **Current**: 60% (XGBoost), 35% (SVM)
- **Measurement**: Weekly
- **Dashboard**: Predictions page

**Impact**: Fewer false alarms = less wasted maintenance

---

### 4.3 Model Recall (Sensitivity)

**KPI**: Failure Detection Rate
- **Formula**: `True Positives / (True Positives + False Negatives)`
- **Target**: >80%
- **Current**: 100% (SVM), 50% (XGBoost)
- **Measurement**: Weekly
- **Dashboard**: Predictions page

**Critical KPI**: Missing failures is costly!

---

### 4.4 F1-Score

**KPI**: Balanced Model Performance
- **Formula**: `2 × (Precision × Recall) / (Precision + Recall)`
- **Target**: >0.70
- **Current**: 0.545 (XGBoost), 0.522 (SVM)
- **Measurement**: Weekly
- **Dashboard**: Predictions page

---

### 4.5 ROC-AUC Score

**KPI**: Model Discrimination Ability
- **Formula**: Area Under ROC Curve
- **Target**: >0.75
- **Current**: 0.667 (XGBoost), 0.393 (SVM)
- **Measurement**: Weekly
- **Dashboard**: Predictions page

---

### 4.6 False Positive Rate

**KPI**: False Alarm Rate
- **Formula**: `False Positives / (False Positives + True Negatives)`
- **Target**: <20%
- **Current**: 14% (XGBoost), 79% (SVM)
- **Measurement**: Weekly
- **Dashboard**: Predictions page

**Impact**: High false positives = wasted resources

---

### 4.7 False Negative Rate

**KPI**: Missed Failure Rate
- **Formula**: `False Negatives / (False Negatives + True Positives)`
- **Target**: <10%
- **Current**: 0% (SVM), 50% (XGBoost)
- **Measurement**: Weekly
- **Dashboard**: Predictions page

**Critical**: Missing failures leads to unexpected breakdowns

---

### 4.8 Model Drift Detection

**KPI**: Prediction Distribution Stability
- **Formula**: `KL Divergence between current and baseline distributions`
- **Target**: <0.1 (stable)
- **Measurement**: Weekly
- **Dashboard**: Settings page

**Action**: Retrain model if drift detected

---

### 4.9 Prediction Confidence

**KPI**: Average Prediction Confidence
- **Formula**: `Average Probability Score`
- **Target**: >70%
- **Measurement**: Per prediction
- **Dashboard**: Predictions page

**By Priority**:
- Critical: >80% confidence
- High: >70% confidence
- Medium: >60% confidence
- Low: >50% confidence

---

## 📊 KPI Dashboard Layout

### Overview Page KPIs
```
┌─────────────────────────────────────────────────────┐
│  Key Metrics (Top Cards)                            │
├─────────────────────────────────────────────────────┤
│  • Total Equipment: 100                             │
│  • High Risk: 17 (17%)                              │
│  • Cost Reduction: 44%                              │
│  • System Uptime: 99.8%                             │
│  • Preventive Maintenance: 38.7%                    │
│  • MTBF: 1,633 hours                                │
└─────────────────────────────────────────────────────┘
```

### Analytics Page KPIs
```
┌─────────────────────────────────────────────────────┐
│  Business KPIs                                      │
├─────────────────────────────────────────────────────┤
│  • Cost Reduction: 44%                              │
│  • ROI: 833%                                        │
│  • Downtime Avoided: 500+ hours/year                │
│  • Equipment Utilization: 95%                       │
│                                                      │
│  Operational KPIs                                   │
├─────────────────────────────────────────────────────┤
│  • Preventive Ratio: 38.7%                          │
│  • Failure Prevention: 78.6%                        │
│  • Schedule Compliance: 92%                         │
│  • MTBF: 1,633 hours                                │
│  • MTTR: 7.5 hours                                  │
└─────────────────────────────────────────────────────┘
```

### Predictions Page KPIs
```
┌─────────────────────────────────────────────────────┐
│  Model Performance KPIs                             │
├─────────────────────────────────────────────────────┤
│  SVM Model:                                         │
│  • Accuracy: 45%                                    │
│  • Precision: 35%                                   │
│  • Recall: 100% ✅                                  │
│  • F1-Score: 0.522                                  │
│                                                      │
│  XGBoost Model:                                     │
│  • Accuracy: 75% ✅                                 │
│  • Precision: 60% ✅                                │
│  • Recall: 50%                                      │
│  • F1-Score: 0.545 ✅                               │
│                                                      │
│  Hybrid System:                                     │
│  • Overall Accuracy: 85% (target)                   │
│  • False Positive Rate: 14%                         │
│  • False Negative Rate: 0%                          │
└─────────────────────────────────────────────────────┘
```

---

## 📈 KPI Targets & Thresholds

### Color-Coded Performance Levels

| KPI | 🟢 Excellent | 🟡 Good | 🟠 Warning | 🔴 Critical |
|-----|-------------|---------|-----------|-------------|
| **Cost Reduction** | >40% | 30-40% | 20-30% | <20% |
| **System Uptime** | >99.5% | 99-99.5% | 98-99% | <98% |
| **Preventive Ratio** | >50% | 40-50% | 30-40% | <30% |
| **Model Accuracy** | >80% | 70-80% | 60-70% | <60% |
| **Model Recall** | >90% | 80-90% | 70-80% | <70% |
| **MTBF** | >2000h | 1500-2000h | 1000-1500h | <1000h |
| **API Response** | <100ms | 100-200ms | 200-500ms | >500ms |
| **Schedule Compliance** | >95% | 90-95% | 85-90% | <85% |

---

## 🎯 KPI Tracking & Reporting

### Daily Monitoring
- System uptime
- API response times
- Pipeline execution
- Critical alerts

### Weekly Reporting
- Model performance metrics
- Prediction accuracy
- False positive/negative rates
- Model drift detection

### Monthly Reporting
- Business KPIs (cost, ROI)
- Operational KPIs (MTBF, MTTR)
- Maintenance effectiveness
- Technician efficiency

### Quarterly Review
- ROI analysis
- Strategic KPI review
- Target adjustments
- Model retraining decisions

---

## 📊 KPI Database Storage

### KPI Metrics Table

```sql
CREATE TABLE kpi_metrics (
    metric_id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_category VARCHAR(50), -- Business, Technical, Operational, Model
    metric_value DECIMAL(10, 4),
    target_value DECIMAL(10, 4),
    measurement_date DATE DEFAULT CURRENT_DATE,
    period VARCHAR(20), -- Daily, Weekly, Monthly, Quarterly
    status VARCHAR(20), -- Excellent, Good, Warning, Critical
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO kpi_metrics (metric_name, metric_category, metric_value, target_value, period, status) VALUES
('Cost Reduction %', 'Business', 44.0, 40.0, 'Monthly', 'Excellent'),
('Model Accuracy', 'Model', 75.0, 75.0, 'Weekly', 'Good'),
('System Uptime %', 'Technical', 99.8, 99.5, 'Daily', 'Excellent'),
('Preventive Ratio %', 'Operational', 38.7, 50.0, 'Monthly', 'Warning');
```

---

## 📈 KPI Improvement Strategies

### To Improve Cost Reduction (Target: >40%)
- ✅ Currently at 44% - maintain performance
- Increase preventive maintenance ratio
- Reduce false positives
- Optimize maintenance scheduling

### To Improve Preventive Maintenance Ratio (Target: >50%)
- ⚠️ Currently at 38.7% - needs improvement
- Act on ML predictions faster
- Schedule more preventive tasks
- Educate team on benefits

### To Improve Model Accuracy (Target: >80%)
- ⚠️ Currently at 75% - close to target
- Collect more training data (200+ equipment)
- Add sensor data (temperature, vibration)
- Retrain models quarterly
- Fine-tune hyperparameters

### To Improve MTBF (Target: >2000 hours)
- ⚠️ Currently at 1,633 hours
- Follow ML recommendations
- Increase preventive maintenance
- Better spare parts management
- Operator training

---

## 🎯 Success Criteria

### Phase 6 Success (Implementation)
- ✅ All KPIs tracked in dashboard
- ✅ Real-time KPI updates
- ✅ Automated KPI calculations
- ✅ Color-coded alerts

### 6-Month Success
- ✅ Cost reduction >40%
- ✅ Preventive ratio >45%
- ✅ Model accuracy >75%
- ✅ System uptime >99%
- ✅ ROI >200%

### 1-Year Success
- ✅ Cost reduction >45%
- ✅ Preventive ratio >50%
- ✅ Model accuracy >80%
- ✅ MTBF >2,000 hours
- ✅ ROI >500%

---

## 📊 KPI API Endpoints

### Get All KPIs
```
GET /api/v1/kpis
```

**Response**:
```json
{
  "success": true,
  "data": {
    "business": {
      "cost_reduction_percent": 44.0,
      "roi_percent": 833.0,
      "downtime_avoided_hours": 500
    },
    "technical": {
      "system_uptime_percent": 99.8,
      "avg_api_response_ms": 150,
      "pipeline_execution_seconds": 12.5
    },
    "operational": {
      "preventive_ratio_percent": 38.7,
      "failure_prevention_percent": 78.6,
      "mtbf_hours": 1633,
      "mttr_hours": 7.5
    },
    "model": {
      "svm_accuracy": 0.45,
      "svm_recall": 1.00,
      "xgb_accuracy": 0.75,
      "xgb_f1_score": 0.545
    }
  }
}
```

### Get KPI Trends
```
GET /api/v1/kpis/trends?metric=cost_reduction&period=monthly&months=6
```

---

## 📝 KPI Reporting Templates

### Executive Summary (Monthly)
```
WeeFarm KPI Report - November 2024

🎯 Key Highlights:
• Cost Reduction: 44% (Target: 40%) ✅
• ROI: 833% 
• System Uptime: 99.8% ✅
• Model Accuracy: 75% ✅

⚠️ Areas for Improvement:
• Preventive Maintenance: 38.7% (Target: 50%)
• MTBF: 1,633 hours (Target: 2,000 hours)

📈 Trends:
• Cost reduction increasing (+2% vs last month)
• Preventive ratio improving (+3% vs last month)
• Model accuracy stable
```

---

## 🎯 Conclusion

KPIs are essential for:
1. **Measuring Success**: Track ROI and cost savings
2. **Identifying Issues**: Detect problems early
3. **Driving Improvements**: Focus on what matters
4. **Demonstrating Value**: Show stakeholders impact
5. **Guiding Decisions**: Data-driven management

**All KPIs will be integrated into the dashboard and tracked automatically!**

---

**End of Document**
