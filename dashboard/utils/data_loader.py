"""
Data Loader for Streamlit Dashboard
Loads data from pipeline results and database
"""

import pandas as pd
import os
import json
from datetime import datetime

class DashboardDataLoader:
    def __init__(self):
        self.base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        self.results_dir = os.path.join(self.base_dir, 'results')
        self.data_dir = os.path.join(self.base_dir, 'data', 'synthetic')
    
    def get_pipeline_status(self):
        """Get pipeline execution status"""
        try:
            summary_path = os.path.join(self.results_dir, 'pipeline_summary.json')
            if os.path.exists(summary_path):
                with open(summary_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading pipeline status: {e}")
            return None
    
    def load_root_cause_analysis(self):
        """Load root cause analysis results"""
        try:
            filepath = os.path.join(self.results_dir, 'root_cause_analysis.csv')
            if os.path.exists(filepath):
                return pd.read_csv(filepath)
            return None
        except Exception as e:
            print(f"Error loading root cause analysis: {e}")
            return None
    
    def load_equipment_reliability(self):
        """Load equipment reliability metrics"""
        try:
            filepath = os.path.join(self.results_dir, 'equipment_reliability_metrics.csv')
            if os.path.exists(filepath):
                return pd.read_csv(filepath)
            return None
        except Exception as e:
            print(f"Error loading equipment reliability: {e}")
            return None
    
    def load_type_reliability(self):
        """Load equipment type reliability"""
        try:
            filepath = os.path.join(self.results_dir, 'equipment_type_reliability.csv')
            if os.path.exists(filepath):
                return pd.read_csv(filepath)
            return None
        except Exception as e:
            print(f"Error loading type reliability: {e}")
            return None
    
    def load_failures(self):
        """Load failure events data"""
        try:
            filepath = os.path.join(self.data_dir, 'failure_events.csv')
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                df['failure_date'] = pd.to_datetime(df['failure_date'])
                return df
            return None
        except Exception as e:
            print(f"Error loading failures: {e}")
            return None
    
    def load_maintenance(self):
        """Load maintenance records"""
        try:
            filepath = os.path.join(self.data_dir, 'maintenance_records.csv')
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                df['maintenance_date'] = pd.to_datetime(df['maintenance_date'])
                return df
            return None
        except Exception as e:
            print(f"Error loading maintenance: {e}")
            return None
    
    def load_equipment(self):
        """Load equipment data"""
        try:
            filepath = os.path.join(self.data_dir, 'equipment.csv')
            if os.path.exists(filepath):
                return pd.read_csv(filepath)
            return None
        except Exception as e:
            print(f"Error loading equipment: {e}")
            return None
    
    def calculate_summary_metrics(self):
        """Calculate summary metrics for dashboard"""
        failures = self.load_failures()
        maintenance = self.load_maintenance()
        equipment = self.load_equipment()
        
        if failures is None or maintenance is None or equipment is None:
            return None
        
        metrics = {
            'total_equipment': len(equipment),
            'total_failures': len(failures),
            'total_maintenance': len(maintenance),
            'avg_downtime': failures['downtime_hours'].mean(),
            'total_cost': failures['repair_cost'].sum() + maintenance['total_cost'].sum(),
            'prevention_rate': (failures['prevented_by_maintenance'].sum() / len(failures) * 100),
            'critical_failures': len(failures[failures['severity'] == 'Critical']),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return metrics
    
    def get_all_analytics_data(self):
        """Load all analytics data at once"""
        return {
            'root_cause': self.load_root_cause_analysis(),
            'equipment_reliability': self.load_equipment_reliability(),
            'type_reliability': self.load_type_reliability(),
            'failures': self.load_failures(),
            'maintenance': self.load_maintenance(),
            'equipment': self.load_equipment(),
            'summary_metrics': self.calculate_summary_metrics(),
            'pipeline_status': self.get_pipeline_status()
        }
