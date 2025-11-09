"""
Error Handler

This module provides utilities for handling errors in the pipeline.
It includes functions for logging errors, creating fallback responses,
and recovering from common failure scenarios.
"""

import sys
import traceback
import logging
import pandas as pd
import numpy as np
from datetime import datetime, date
import os
from pathlib import Path

# Configure logging
log_dir = Path("../logs")
log_dir.mkdir(exist_ok=True)

# Create logger
logger = logging.getLogger("pipeline")
logger.setLevel(logging.DEBUG)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create file handler
log_file = log_dir / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

# Create formatters
console_format = logging.Formatter('%(levelname)s - %(message)s')
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Set formatters
console_handler.setFormatter(console_format)
file_handler.setFormatter(file_format)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

class PipelineError(Exception):
    """Base class for pipeline errors"""
    def __init__(self, message, stage=None, recoverable=False):
        self.message = message
        self.stage = stage
        self.recoverable = recoverable
        super().__init__(self.message)

class DataError(PipelineError):
    """Error for data-related issues"""
    def __init__(self, message, stage=None, recoverable=True):
        super().__init__(message, stage, recoverable)

class DatabaseError(PipelineError):
    """Error for database-related issues"""
    def __init__(self, message, stage=None, recoverable=False):
        super().__init__(message, stage, recoverable)

class ModelError(PipelineError):
    """Error for model-related issues"""
    def __init__(self, message, stage=None, recoverable=True):
        super().__init__(message, stage, recoverable)

def log_error(error, stage=None):
    """Log an error with detailed information"""
    error_type = type(error).__name__
    error_message = str(error)
    
    if stage:
        logger.error(f"[{stage}] {error_type}: {error_message}")
    else:
        logger.error(f"{error_type}: {error_message}")
    
    # Log traceback
    logger.debug(traceback.format_exc())
    
    # Return formatted error message
    if stage:
        return f"[ERROR] [{stage}] {error_type}: {error_message}"
    else:
        return f"[ERROR] {error_type}: {error_message}"

def create_fallback_predictions(equipment_df):
    """Create fallback predictions when prediction fails"""
    logger.warning("Creating fallback predictions")
    
    # Create a basic predictions DataFrame with all equipment
    predictions = pd.DataFrame({
        'equipment_id': equipment_df['equipment_id'],
        'prediction': 0,  # Default to no failure prediction
        'probability': 0.0,  # Default to zero probability
        'risk_score': 0.0,  # Default to zero risk score
        'model_name': 'fallback_model'
    })
    
    # Add additional columns
    predictions['priority_level'] = 'Low'
    predictions['recommended_action'] = 'Monitor equipment status.'
    predictions['recommended_date'] = date.today()
    
    # Add model-specific columns
    predictions['svm_prediction'] = 0
    predictions['svm_probability'] = 0.0
    predictions['xgb_prediction'] = 0
    predictions['xgb_probability'] = 0.0
    
    logger.info(f"Created fallback predictions for {len(equipment_df)} equipment")
    
    return predictions

def create_fallback_kpis():
    """Create fallback KPIs when KPI calculation fails"""
    logger.warning("Creating fallback KPIs")
    
    # Create basic KPIs
    kpis = {
        'equipment_availability': {
            'value': 100.0,
            'target': 95.0,
            'category': 'Operational',
            'status': 'Good'
        },
        'maintenance_compliance': {
            'value': 100.0,
            'target': 90.0,
            'category': 'Maintenance',
            'status': 'Good'
        },
        'failure_rate': {
            'value': 0.0,
            'target': 5.0,
            'category': 'Reliability',
            'status': 'Good'
        }
    }
    
    logger.info(f"Created {len(kpis)} fallback KPIs")
    
    return kpis

def handle_stage_error(error, stage, data=None):
    """Handle errors in pipeline stages with appropriate fallbacks"""
    error_message = log_error(error, stage)
    
    # Create appropriate fallback based on stage
    fallback_data = None
    
    if stage == "Data Ingestion":
        # Critical error, cannot proceed without data
        logger.critical("Data ingestion failed, cannot proceed with pipeline")
        raise DatabaseError(f"Data ingestion failed: {error}", stage, False)
    
    elif stage == "Feature Engineering":
        if data and 'equipment' in data:
            # Create minimal features
            equipment_df = data['equipment']
            fallback_data = {
                'features': pd.DataFrame({
                    'equipment_id': equipment_df['equipment_id']
                })
            }
            logger.warning(f"Created minimal features for {len(equipment_df)} equipment")
        else:
            logger.critical("Feature engineering failed and no equipment data available")
            raise DataError(f"Feature engineering failed: {error}", stage, False)
    
    elif stage == "Model Training" or stage == "Model Prediction":
        if data and ('features' in data or 'equipment' in data):
            # Use equipment data if available, otherwise features
            equipment_df = data.get('equipment', data.get('features'))
            fallback_data = {
                'predictions': create_fallback_predictions(equipment_df),
                'models': {
                    'best_model_name': 'fallback_model',
                    'best_model': None,
                    'scaler': None,
                    'feature_columns': None
                }
            }
        else:
            logger.critical("Model stage failed and no equipment/features data available")
            raise ModelError(f"Model stage failed: {error}", stage, False)
    
    elif stage == "Decision Engine":
        if data and 'predictions' in data:
            # Use existing predictions but add default decisions
            predictions_df = data['predictions']
            predictions_df['priority_level'] = 'Low'
            predictions_df['recommended_action'] = 'Monitor equipment status.'
            predictions_df['recommended_date'] = date.today()
            
            fallback_data = {
                'decisions': predictions_df
            }
            logger.warning(f"Created fallback decisions for {len(predictions_df)} predictions")
        else:
            logger.critical("Decision engine failed and no predictions data available")
            raise DataError(f"Decision engine failed: {error}", stage, False)
    
    elif stage == "KPI Calculation":
        fallback_data = {
            'kpis': create_fallback_kpis()
        }
        
        # Add decisions if available
        if data and 'decisions' in data:
            fallback_data['decisions'] = data['decisions']
    
    elif stage == "Output Storage":
        # Non-critical error, pipeline has completed but storage failed
        logger.error(f"Output storage failed: {error}")
        fallback_data = data  # Return original data
    
    else:
        # Unknown stage
        logger.error(f"Error in unknown stage '{stage}': {error}")
        fallback_data = data  # Return original data
    
    return error_message, fallback_data

def safe_execute(func, stage_name, *args, **kwargs):
    """Safely execute a function with error handling"""
    try:
        logger.info(f"Starting {stage_name}")
        result = func(*args, **kwargs)
        logger.info(f"Completed {stage_name}")
        return result, None
    except Exception as e:
        error_message = log_error(e, stage_name)
        return None, error_message

if __name__ == "__main__":
    # Test error handling
    try:
        # Simulate an error
        raise ValueError("Test error")
    except Exception as e:
        error_message = log_error(e, "Test Stage")
        print(error_message)
