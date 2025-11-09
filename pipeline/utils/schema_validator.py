"""
Database Schema Validator

This module provides utilities to validate the database schema against expected structure.
It checks that all required tables and columns exist with the correct data types.
"""

import psycopg2
import pandas as pd
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append('..')
sys.path.append('../..')

# Import database configuration
try:
    from pipeline.config import DB_CONFIG
except ImportError:
    # Default configuration if import fails
    DB_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'weefarm_db',
        'user': 'postgres',
        'password': '0000'
    }

# Define expected schema
EXPECTED_SCHEMA = {
    'equipment': {
        'equipment_id': 'character varying',
        'equipment_type': 'character varying',
        'manufacturer': 'character varying',
        'model': 'character varying',
        'year_manufactured': 'integer',
        'purchase_date': 'date',
        'installation_date': 'date',
        'location': 'character varying',
        'status': 'character varying'
    },
    'maintenance': {
        'maintenance_id': 'integer',
        'equipment_id': 'character varying',
        'maintenance_date': 'date',
        'maintenance_type': 'character varying',
        'cost': 'numeric',
        'technician': 'character varying',
        'description': 'text'
    },
    'failures': {
        'failure_id': 'integer',
        'equipment_id': 'character varying',
        'failure_date': 'date',
        'failure_type': 'character varying',
        'severity': 'character varying',
        'downtime_hours': 'numeric',
        'repair_cost': 'numeric',
        'description': 'text'
    },
    'predictions': {
        'prediction_id': 'integer',
        'equipment_id': 'character varying',
        'prediction_date': 'date',
        'svm_prediction': 'integer',
        'svm_probability': 'numeric',
        'xgb_prediction': 'integer',
        'xgb_probability': 'numeric',
        'risk_score': 'numeric',
        'priority_level': 'character varying',
        'recommended_action': 'text'
    },
    'maintenance_schedule': {
        'schedule_id': 'integer',
        'equipment_id': 'character varying',
        'scheduled_date': 'date',
        'priority_level': 'character varying',
        'risk_score': 'numeric',
        'status': 'character varying',
        'assigned_technician': 'character varying',
        'estimated_cost': 'numeric',
        'estimated_duration_hours': 'numeric'
    },
    'model_performance': {
        'performance_id': 'integer',
        'model_name': 'character varying',
        'model_version': 'character varying',
        'evaluation_date': 'date',
        'accuracy': 'numeric',
        'precision_score': 'numeric',
        'recall': 'numeric',
        'f1_score': 'numeric',
        'roc_auc': 'numeric',
        'sample_size': 'integer'
    },
    'kpi_metrics': {
        'metric_id': 'integer',
        'metric_name': 'character varying',
        'metric_category': 'character varying',
        'metric_value': 'numeric',
        'target_value': 'numeric',
        'measurement_date': 'date',
        'period': 'character varying',
        'status': 'character varying'
    }
}

def connect_to_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        print(f"✅ Connected to database: {DB_CONFIG['database']}")
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def get_table_schema(conn, table_name):
    """Get schema for a specific table"""
    try:
        cursor = conn.cursor()
        
        # Get column information
        cursor.execute(f"""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        # Convert to dictionary
        schema = {col[0]: col[1] for col in columns}
        
        cursor.close()
        
        return schema
    except Exception as e:
        print(f"❌ Error getting schema for table {table_name}: {e}")
        return {}

def validate_table_schema(conn, table_name, expected_schema):
    """Validate schema for a specific table"""
    actual_schema = get_table_schema(conn, table_name)
    
    if not actual_schema:
        return False, f"Table '{table_name}' does not exist or could not be accessed"
    
    # Check for missing columns
    missing_columns = []
    for col_name, col_type in expected_schema.items():
        if col_name not in actual_schema:
            missing_columns.append(col_name)
    
    # Check for type mismatches
    type_mismatches = []
    for col_name, expected_type in expected_schema.items():
        if col_name in actual_schema and not actual_schema[col_name].startswith(expected_type):
            type_mismatches.append(f"{col_name} (expected: {expected_type}, actual: {actual_schema[col_name]})")
    
    if missing_columns or type_mismatches:
        error_message = f"Schema validation failed for table '{table_name}':\n"
        if missing_columns:
            error_message += f"  - Missing columns: {', '.join(missing_columns)}\n"
        if type_mismatches:
            error_message += f"  - Type mismatches: {', '.join(type_mismatches)}\n"
        return False, error_message
    
    return True, f"Schema validation passed for table '{table_name}'"

def validate_database_schema(conn=None, expected_schema=EXPECTED_SCHEMA):
    """Validate schema for all tables in the database"""
    if conn is None:
        conn = connect_to_db()
        if conn is None:
            return False, "Could not connect to database"
    
    print("\n🔍 Validating database schema...")
    
    all_valid = True
    validation_results = {}
    
    for table_name, expected_columns in expected_schema.items():
        valid, message = validate_table_schema(conn, table_name, expected_columns)
        validation_results[table_name] = {
            'valid': valid,
            'message': message
        }
        
        if not valid:
            all_valid = False
            print(f"❌ {message}")
        else:
            print(f"✅ {message}")
    
    if all_valid:
        print("\n✅ All tables validated successfully!")
    else:
        print("\n❌ Schema validation failed for some tables")
    
    return all_valid, validation_results

def validate_dataframe_schema(df, expected_columns, table_name="DataFrame"):
    """Validate that a DataFrame has all required columns"""
    missing_columns = []
    for col in expected_columns:
        if col not in df.columns:
            missing_columns.append(col)
    
    if missing_columns:
        error_message = f"Schema validation failed for {table_name}:\n"
        error_message += f"  - Missing columns: {', '.join(missing_columns)}\n"
        return False, error_message, missing_columns
    
    return True, f"Schema validation passed for {table_name}", []

if __name__ == "__main__":
    # Test the schema validation
    conn = connect_to_db()
    if conn:
        valid, results = validate_database_schema(conn)
        conn.close()
        
        if valid:
            print("\n✅ Database schema is valid and ready for pipeline execution")
        else:
            print("\n❌ Database schema validation failed. Please fix the issues before running the pipeline")
            
            # Print detailed results
            print("\nDetailed validation results:")
            for table_name, result in results.items():
                status = "✅" if result['valid'] else "❌"
                print(f"{status} {table_name}: {result['message']}")
    else:
        print("❌ Could not connect to database")
