"""
Feedback Loop: Model Improvement & Retraining
Tracks prediction accuracy and triggers model retraining
"""

import pandas as pd
import numpy as np
import psycopg2
from datetime import datetime, timedelta
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
import sys
sys.path.append('.')
from config import DB_CONFIG

class FeedbackLoop:
    """Manage feedback and model retraining"""
    
    def __init__(self):
        self.accuracy_threshold = 0.75
        self.retraining_interval_days = 90
        self.last_retrain_date = None
    
    def capture_actual_event(self, equipment_id, prediction_date, actual_failure, actual_rul, actual_cost):
        """
        Capture actual event for comparison with prediction
        
        Args:
            equipment_id: Equipment identifier
            prediction_date: Date of prediction
            actual_failure: Whether failure actually occurred (True/False)
            actual_rul: Actual RUL in days
            actual_cost: Actual maintenance/failure cost
        
        Returns:
            dict: Event record
        """
        event = {
            'equipment_id': equipment_id,
            'prediction_date': prediction_date,
            'actual_failure': actual_failure,
            'actual_rul': actual_rul,
            'actual_cost': actual_cost,
            'captured_date': datetime.now()
        }
        
        return event
    
    def calculate_prediction_accuracy(self, predictions_df, actual_events_df):
        """
        Calculate prediction accuracy metrics
        
        Args:
            predictions_df: DataFrame with predictions
            actual_events_df: DataFrame with actual events
        
        Returns:
            dict: Accuracy metrics
        """
        # Merge predictions with actual events
        merged = predictions_df.merge(
            actual_events_df,
            on='equipment_id',
            how='inner'
        )
        
        if len(merged) == 0:
            return {
                'samples': 0,
                'accuracy': 0,
                'precision': 0,
                'recall': 0,
                'f1_score': 0
            }
        
        # Convert failure probability to binary prediction (threshold 0.5)
        y_pred = (merged['failure_probability'] > 0.5).astype(int)
        y_true = merged['actual_failure'].astype(int)
        
        # Calculate metrics
        metrics = {
            'samples': len(merged),
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1_score': f1_score(y_true, y_pred, zero_division=0)
        }
        
        # RUL accuracy (mean absolute error)
        rul_mae = np.mean(np.abs(merged['rul_days'] - merged['actual_rul']))
        metrics['rul_mae'] = rul_mae
        
        # Cost accuracy (mean absolute percentage error)
        cost_mape = np.mean(np.abs(
            (merged['estimated_maintenance_cost'] - merged['actual_cost']) / 
            (merged['actual_cost'] + 1)
        )) * 100
        metrics['cost_mape'] = cost_mape
        
        return metrics
    
    def should_retrain(self, accuracy_metrics, days_since_last_retrain=None):
        """
        Determine if models should be retrained
        
        Args:
            accuracy_metrics: Accuracy metrics dictionary
            days_since_last_retrain: Days since last retraining
        
        Returns:
            bool: True if retraining recommended
        """
        # Retrain if accuracy drops below threshold
        if accuracy_metrics['accuracy'] < self.accuracy_threshold:
            return True
        
        # Retrain if F1 score drops significantly
        if accuracy_metrics['f1_score'] < 0.70:
            return True
        
        # Retrain on schedule (quarterly)
        if days_since_last_retrain is None or days_since_last_retrain >= self.retraining_interval_days:
            return True
        
        return False
    
    def generate_retraining_report(self, accuracy_metrics):
        """
        Generate retraining report
        
        Args:
            accuracy_metrics: Accuracy metrics
        
        Returns:
            str: Report text
        """
        report = f"""
        PREDICTION ACCURACY REPORT
        ===========================
        
        Samples Analyzed: {accuracy_metrics['samples']}
        
        Classification Metrics:
          - Accuracy: {accuracy_metrics['accuracy']:.3f}
          - Precision: {accuracy_metrics['precision']:.3f}
          - Recall: {accuracy_metrics['recall']:.3f}
          - F1 Score: {accuracy_metrics['f1_score']:.3f}
        
        Regression Metrics:
          - RUL MAE: {accuracy_metrics['rul_mae']:.1f} days
          - Cost MAPE: {accuracy_metrics['cost_mape']:.1f}%
        
        Recommendation:
        """
        
        if accuracy_metrics['accuracy'] < self.accuracy_threshold:
            report += f"\n  ⚠️  RETRAIN RECOMMENDED - Accuracy below {self.accuracy_threshold:.1%} threshold"
        elif accuracy_metrics['f1_score'] < 0.70:
            report += "\n  ⚠️  RETRAIN RECOMMENDED - F1 score below 0.70"
        else:
            report += "\n  ✓ Models performing well - Continue monitoring"
        
        return report
    
    def update_simulation_parameters(self, actual_events_df):
        """
        Update simulation parameters based on real patterns
        
        Args:
            actual_events_df: DataFrame with actual events
        
        Returns:
            dict: Updated parameters
        """
        updates = {
            'degradation_rate_adjustment': 1.0,
            'sensor_drift_adjustment': 1.0,
            'missing_value_rate_adjustment': 1.0,
            'outlier_rate_adjustment': 1.0
        }
        
        # Calculate actual failure rate
        if len(actual_events_df) > 0:
            actual_failure_rate = actual_events_df['actual_failure'].mean()
            
            # Adjust degradation rate based on actual failures
            if actual_failure_rate > 0.3:
                updates['degradation_rate_adjustment'] = 1.2  # Increase degradation
            elif actual_failure_rate < 0.1:
                updates['degradation_rate_adjustment'] = 0.8  # Decrease degradation
        
        return updates

def run_feedback_loop(predictions_df, actual_events_df=None):
    """
    Execute feedback loop
    
    Args:
        predictions_df: DataFrame with predictions
        actual_events_df: DataFrame with actual events (optional)
    
    Returns:
        dict: Feedback loop results
    """
    print("\n" + "="*60)
    print("FEEDBACK LOOP: MODEL IMPROVEMENT")
    print("="*60)
    
    try:
        feedback = FeedbackLoop()
        
        # Step 1: Calculate accuracy
        print("\n[STEP 1] Calculating prediction accuracy...")
        if actual_events_df is None or len(actual_events_df) == 0:
            print("   [INFO] No actual events available for comparison")
            accuracy_metrics = {
                'samples': 0,
                'accuracy': 0,
                'precision': 0,
                'recall': 0,
                'f1_score': 0,
                'rul_mae': 0,
                'cost_mape': 0
            }
        else:
            accuracy_metrics = feedback.calculate_prediction_accuracy(predictions_df, actual_events_df)
            print(f"   Samples analyzed: {accuracy_metrics['samples']}")
            print(f"   Accuracy: {accuracy_metrics['accuracy']:.3f}")
            print(f"   F1 Score: {accuracy_metrics['f1_score']:.3f}")
        
        # Step 2: Check if retraining needed
        print("\n[STEP 2] Checking retraining requirements...")
        should_retrain = feedback.should_retrain(accuracy_metrics)
        
        if should_retrain:
            print("   ⚠️  RETRAINING RECOMMENDED")
        else:
            print("   ✓ Models performing well")
        
        # Step 3: Generate report
        print("\n[STEP 3] Generating accuracy report...")
        report = feedback.generate_retraining_report(accuracy_metrics)
        print(report)
        
        # Step 4: Update simulation parameters
        print("\n[STEP 4] Updating simulation parameters...")
        if actual_events_df is not None and len(actual_events_df) > 0:
            parameter_updates = feedback.update_simulation_parameters(actual_events_df)
            print(f"   Parameter updates:")
            for param, value in parameter_updates.items():
                print(f"     - {param}: {value:.2f}x")
        else:
            parameter_updates = {}
            print("   [INFO] No parameter updates (insufficient data)")
        
        # Summary
        print(f"\n[COMPLETE] Feedback Loop Complete!")
        print(f"   Accuracy: {accuracy_metrics['accuracy']:.3f}")
        print(f"   Retraining needed: {'Yes' if should_retrain else 'No'}")
        
        return {
            'success': True,
            'accuracy_metrics': accuracy_metrics,
            'should_retrain': should_retrain,
            'parameter_updates': parameter_updates,
            'report': report
        }
        
    except Exception as e:
        print(f"[ERROR] Feedback loop failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    # Example usage
    from pipeline.stages.stage4_risk_scoring import run_stage4
    from pipeline.stages.stage3_ensemble_prediction import run_stage3
    from pipeline.stages.stage2_enhanced_features import run_stage2
    from pipeline.stages.stage1_data_ingestion import run_stage1
    
    data = run_stage1()
    features_data = run_stage2(data)
    predictions_data = run_stage3(features_data)
    decisions_data = run_stage4(predictions_data)
    
    # Create sample actual events
    predictions_df = decisions_data['predictions']
    actual_events = pd.DataFrame({
        'equipment_id': predictions_df['equipment_id'].head(20),
        'actual_failure': np.random.randint(0, 2, 20),
        'actual_rul': np.random.randint(10, 365, 20),
        'actual_cost': np.random.randint(100, 2000, 20)
    })
    
    result = run_feedback_loop(predictions_df, actual_events)
    print(f"\nFeedback loop result: {result['success']}")
