"""
Run Integrated Pipeline with Progress Tracking

This script runs the integrated pipeline with model training and fine-tuning.
It provides:
1. Progress tracking with estimated time remaining
2. Command-line arguments for different modes
3. Detailed logging of each stage
4. Summary of results
5. Data validation and error handling
6. Database schema validation

Usage:
    python run_integrated_pipeline.py --mode [train|predict|all] --output-dir [path] [--skip-validation]
"""

import os
import sys
import time
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add pipeline directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'pipeline'))

# Import integrated pipeline
from pipeline.integrated_pipeline import run_integrated_pipeline

# Import utility modules
from pipeline.utils.schema_validator import validate_database_schema, connect_to_db
from pipeline.utils.error_handler import log_error

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run the integrated pipeline')
    
    parser.add_argument('--mode', type=str, default='all',
                        choices=['train', 'predict', 'all'],
                        help='Pipeline mode: train (with model training), predict (use existing models), or all')
    
    parser.add_argument('--output-dir', type=str, default='images',
                        help='Directory to save output files')
    
    parser.add_argument('--skip-validation', action='store_true',
                        help='Skip database schema validation')
    
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level')
    
    parser.add_argument('--log-file', type=str, default=None,
                        help='Log file path (default: auto-generated in logs directory)')
    
    return parser.parse_args()

def display_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█'):
    """Display progress bar"""
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    if iteration == total:
        print()

def display_time_remaining(start_time, current_step, total_steps):
    """Display time remaining"""
    elapsed_time = time.time() - start_time
    if current_step > 0:
        estimated_total_time = elapsed_time * total_steps / current_step
        remaining_time = estimated_total_time - elapsed_time
        
        # Format time
        hours, remainder = divmod(remaining_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            time_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        elif minutes > 0:
            time_str = f"{int(minutes)}m {int(seconds)}s"
        else:
            time_str = f"{int(seconds)}s"
        
        print(f"⏱️ Estimated time remaining: {time_str}")

def setup_logging(args):
    """Set up logging configuration"""
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Set up logging level
    log_level = getattr(logging, args.log_level)
    
    # Set up log file
    if args.log_file:
        log_file = args.log_file
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f"pipeline_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Get logger
    logger = logging.getLogger('pipeline')
    logger.info(f"Logging initialized at level {args.log_level}")
    logger.info(f"Log file: {log_file}")
    
    return logger

def validate_database(args):
    """Validate database schema"""
    if args.skip_validation:
        print("\n⚠️ Database schema validation skipped")
        return True
    
    print("\n🔍 Validating database schema...")
    conn = connect_to_db()
    if conn is None:
        print("\n❌ Could not connect to database")
        return False
    
    valid, results = validate_database_schema(conn)
    conn.close()
    
    if not valid:
        print("\n⚠️ Database schema validation failed. Some pipeline features may not work correctly.")
        print("   Run with --skip-validation to bypass this check.")
        
        # Print detailed results
        print("\nDetailed validation results:")
        for table_name, result in results.items():
            status = "✅" if result['valid'] else "❌"
            print(f"{status} {table_name}: {result['message']}")
        
        return False
    else:
        print("\n✅ Database schema validation passed.")
        return True

def run_pipeline_with_progress():
    """Run the integrated pipeline with progress tracking"""
    args = parse_arguments()
    
    # Set up logging
    logger = setup_logging(args)
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Set pipeline mode
    use_model_training = args.mode in ['train', 'all']
    
    print("\n" + "="*70)
    print(f"🚀 RUNNING INTEGRATED PIPELINE")
    print(f"   Mode: {args.mode}")
    print(f"   Output directory: {output_dir}")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Validate database schema
    schema_valid = validate_database(args)
    
    # Record start time
    start_time = time.time()
    
    try:
        # Run the integrated pipeline
        result = run_integrated_pipeline(
            use_model_training=use_model_training,
            validate_schema=not args.skip_validation
        )
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Format time
        hours, remainder = divmod(execution_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            time_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        elif minutes > 0:
            time_str = f"{int(minutes)}m {int(seconds)}s"
        else:
            time_str = f"{int(seconds)}s"
        
        print("\n" + "="*70)
        print(f"✅ PIPELINE EXECUTION COMPLETED IN {time_str}")
        print("="*70)
        
        # Print summary
        if result['success']:
            print(f"\n📊 Equipment analyzed: {result['equipment_count']}")
            print(f"📊 Predictions generated: {result['predictions_count']}")
            print(f"📊 KPIs calculated: {result['kpis_count']}")
            logger.info(f"Pipeline completed successfully in {time_str}")
        else:
            print(f"\n❌ Pipeline failed: {result['error']}")
            logger.error(f"Pipeline failed: {result['error']}")
        
        print(f"\n✅ All outputs saved to {output_dir}")
        print("✅ Done!")
        
        return result['success']
        
    except Exception as e:
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Format time
        hours, remainder = divmod(execution_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            time_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        elif minutes > 0:
            time_str = f"{int(minutes)}m {int(seconds)}s"
        else:
            time_str = f"{int(seconds)}s"
        
        # Log error
        error_message = log_error(e, "Pipeline Runner")
        
        print("\n" + "="*70)
        print(f"❌ PIPELINE EXECUTION FAILED IN {time_str}")
        print("="*70)
        print(f"\nError: {e}")
        print("\n" + "="*70)
        
        print(f"\n✅ Log file: {args.log_file or 'logs/pipeline_*.log'}")
        print("✅ Done!")
        
        return False

if __name__ == "__main__":
    run_pipeline_with_progress()
