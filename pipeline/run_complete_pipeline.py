"""
Complete Pipeline: Database → Notebooks → Streamlit
Runs all analysis phases and updates results for dashboard
"""

import os
import sys
import subprocess
import pandas as pd
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)

class AnalyticsPipeline:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.notebooks_dir = os.path.join(self.base_dir, 'notebooks')
        self.results_dir = os.path.join(self.base_dir, 'results')
        self.viz_dir = os.path.join(self.base_dir, 'visualizations')
        
        # Ensure directories exist
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.viz_dir, exist_ok=True)
        
        # Notebook execution order
        self.notebooks = [
            '1_comprehensive_EDA.ipynb',
            '02_feature_engineering.ipynb',
            '03_feature_selection.ipynb',
            '04_handle_class_imbalance.ipynb',
            '05_model_training.ipynb',
            '06_time_series_forecasting.ipynb',
            '07_advanced_analytics.ipynb'
        ]
    
    def execute_notebook(self, notebook_name):
        """Execute a Jupyter notebook using nbconvert"""
        notebook_path = os.path.join(self.notebooks_dir, notebook_name)
        
        if not os.path.exists(notebook_path):
            logging.warning(f"Notebook not found: {notebook_name}")
            return False
        
        logging.info(f"Executing {notebook_name}...")
        
        try:
            cmd = [
                'jupyter', 'nbconvert',
                '--to', 'notebook',
                '--execute',
                '--inplace',
                '--ExecutePreprocessor.timeout=600',
                notebook_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logging.info(f"✅ Successfully executed {notebook_name}")
                return True
            else:
                logging.error(f"❌ Error executing {notebook_name}: {result.stderr}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Exception executing {notebook_name}: {str(e)}")
            return False
    
    def load_data_from_database(self):
        """Load fresh data from database"""
        logging.info("Loading data from database...")
        
        try:
            # Import database connection
            sys.path.append(os.path.join(self.base_dir, 'backend'))
            from app.database import engine
            from sqlalchemy import text
            
            # Load equipment data
            equipment = pd.read_sql(
                text("SELECT * FROM equipment"),
                engine
            )
            equipment.to_csv(os.path.join(self.base_dir, 'data', 'synthetic', 'equipment.csv'), index=False)
            
            # Load maintenance data
            maintenance = pd.read_sql(
                text("SELECT * FROM maintenance_records"),
                engine
            )
            maintenance.to_csv(os.path.join(self.base_dir, 'data', 'synthetic', 'maintenance_records.csv'), index=False)
            
            # Load failure data
            failures = pd.read_sql(
                text("SELECT * FROM failure_events"),
                engine
            )
            failures.to_csv(os.path.join(self.base_dir, 'data', 'synthetic', 'failure_events.csv'), index=False)
            
            logging.info(f"Loaded {len(equipment)} equipment, {len(maintenance)} maintenance records, {len(failures)} failures")
            return True
            
        except Exception as e:
            logging.error(f"Error loading from database: {str(e)}")
            return False
    
    def generate_dashboard_summary(self):
        """Generate summary statistics for dashboard"""
        logging.info("Generating dashboard summary...")
        
        try:
            # Load all results
            summary = {
                'last_updated': datetime.now().isoformat(),
                'pipeline_status': 'completed',
                'phases_completed': []
            }
            
            # Check which results exist
            result_files = {
                'root_cause_analysis': 'root_cause_analysis.csv',
                'equipment_reliability': 'equipment_reliability_metrics.csv',
                'type_reliability': 'equipment_type_reliability.csv'
            }
            
            for key, filename in result_files.items():
                filepath = os.path.join(self.results_dir, filename)
                if os.path.exists(filepath):
                    summary['phases_completed'].append(key)
            
            # Save summary
            import json
            with open(os.path.join(self.results_dir, 'pipeline_summary.json'), 'w') as f:
                json.dump(summary, f, indent=2)
            
            logging.info("✅ Dashboard summary generated")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error generating summary: {str(e)}")
            return False
    
    def run_full_pipeline(self, skip_notebooks=False):
        """Run the complete pipeline"""
        logging.info("="*80)
        logging.info("Starting Complete Analytics Pipeline")
        logging.info("="*80)
        
        # Step 1: Load fresh data from database
        if not self.load_data_from_database():
            logging.error("Failed to load data from database. Aborting.")
            return False
        
        # Step 2: Execute notebooks
        if not skip_notebooks:
            for notebook in self.notebooks:
                if not self.execute_notebook(notebook):
                    logging.warning(f"Skipping {notebook} due to errors")
                    continue
        else:
            logging.info("Skipping notebook execution (skip_notebooks=True)")
        
        # Step 3: Generate dashboard summary
        self.generate_dashboard_summary()
        
        logging.info("="*80)
        logging.info("Pipeline completed successfully!")
        logging.info("="*80)
        logging.info("Next steps:")
        logging.info("1. Review results in the 'results' folder")
        logging.info("2. Check visualizations in the 'visualizations' folder")
        logging.info("3. Start Streamlit dashboard: cd dashboard && streamlit run app.py")
        
        return True
    
    def run_phase(self, phase_number):
        """Run a specific phase only"""
        phase_map = {
            1: '1_comprehensive_EDA.ipynb',
            2: '02_feature_engineering.ipynb',
            3: '03_feature_selection.ipynb',
            4: '04_handle_class_imbalance.ipynb',
            5: '05_model_training.ipynb',
            6: '06_time_series_forecasting.ipynb',
            7: '07_advanced_analytics.ipynb'
        }
        
        if phase_number not in phase_map:
            logging.error(f"Invalid phase number: {phase_number}")
            return False
        
        notebook = phase_map[phase_number]
        logging.info(f"Running Phase {phase_number}: {notebook}")
        
        return self.execute_notebook(notebook)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Analytics Pipeline')
    parser.add_argument('--phase', type=int, help='Run specific phase only (1-7)')
    parser.add_argument('--skip-notebooks', action='store_true', help='Skip notebook execution')
    parser.add_argument('--refresh-data', action='store_true', help='Only refresh data from database')
    
    args = parser.parse_args()
    
    pipeline = AnalyticsPipeline()
    
    if args.refresh_data:
        pipeline.load_data_from_database()
    elif args.phase:
        pipeline.run_phase(args.phase)
    else:
        pipeline.run_full_pipeline(skip_notebooks=args.skip_notebooks)


if __name__ == '__main__':
    main()
