"""
Data Validator

This module provides utilities to validate input data for the pipeline.
It checks that all required columns are present and have the correct data types.
"""

import pandas as pd
import numpy as np
from datetime import datetime, date

# Define expected data schemas
EXPECTED_SCHEMAS = {
    'equipment': {
        'required_columns': ['equipment_id', 'equipment_type', 'status'],
        'column_types': {
            'equipment_id': str,
            'equipment_type': str,
            'year_manufactured': int,
            'status': str
        }
    },
    'maintenance': {
        'required_columns': ['maintenance_id', 'equipment_id', 'maintenance_date'],
        'column_types': {
            'maintenance_id': int,
            'equipment_id': str,
            'maintenance_date': [date, datetime, str],
            'cost': [float, int]
        }
    },
    'failures': {
        'required_columns': ['failure_id', 'equipment_id', 'failure_date'],
        'column_types': {
            'failure_id': int,
            'equipment_id': str,
            'failure_date': [date, datetime, str],
            'downtime_hours': [float, int],
            'repair_cost': [float, int]
        }
    },
    'features': {
        'required_columns': ['equipment_id'],
        'column_types': {
            'equipment_id': str
        }
    },
    'predictions': {
        'required_columns': ['equipment_id', 'prediction', 'probability'],
        'column_types': {
            'equipment_id': str,
            'prediction': [int, bool],
            'probability': float
        }
    }
}

def validate_column_presence(df, required_columns, data_name="DataFrame"):
    """Validate that a DataFrame has all required columns"""
    missing_columns = []
    for col in required_columns:
        if col not in df.columns:
            missing_columns.append(col)
    
    if missing_columns:
        error_message = f"Data validation failed for {data_name}:\n"
        error_message += f"  - Missing required columns: {', '.join(missing_columns)}\n"
        return False, error_message, missing_columns
    
    return True, f"Column validation passed for {data_name}", []

def validate_column_types(df, column_types, data_name="DataFrame"):
    """Validate that columns have the correct data types"""
    type_errors = []
    
    for col, expected_types in column_types.items():
        if col in df.columns:
            # Convert expected_types to list if it's not already
            if not isinstance(expected_types, list):
                expected_types = [expected_types]
            
            # Check if column has any of the expected types
            valid_type = False
            
            # Skip validation for columns with all null values
            if df[col].isna().all():
                continue
            
            for expected_type in expected_types:
                if expected_type == str:
                    valid_type = df[col].apply(lambda x: isinstance(x, str) or pd.isna(x)).all()
                elif expected_type == int:
                    valid_type = df[col].apply(lambda x: isinstance(x, int) or pd.isna(x) or 
                                              (isinstance(x, float) and x.is_integer())).all()
                elif expected_type == float:
                    valid_type = df[col].apply(lambda x: isinstance(x, (int, float)) or pd.isna(x)).all()
                elif expected_type in [date, datetime]:
                    try:
                        pd.to_datetime(df[col])
                        valid_type = True
                    except:
                        valid_type = False
                elif expected_type == bool:
                    valid_type = df[col].apply(lambda x: isinstance(x, bool) or pd.isna(x) or 
                                              x in [0, 1, '0', '1', 'True', 'False', 'true', 'false']).all()
                
                if valid_type:
                    break
            
            if not valid_type:
                actual_type = df[col].dtype
                type_errors.append(f"{col} (expected: {[t.__name__ for t in expected_types]}, actual: {actual_type})")
    
    if type_errors:
        error_message = f"Type validation failed for {data_name}:\n"
        error_message += f"  - Type errors: {', '.join(type_errors)}\n"
        return False, error_message
    
    return True, f"Type validation passed for {data_name}"

def validate_data_integrity(df, data_name="DataFrame"):
    """Validate data integrity (no duplicates, no nulls in key columns)"""
    integrity_errors = []
    
    # Check for duplicates in ID columns
    id_columns = [col for col in df.columns if col.endswith('_id')]
    for col in id_columns:
        duplicate_count = df[col].duplicated().sum()
        if duplicate_count > 0:
            integrity_errors.append(f"Found {duplicate_count} duplicates in {col}")
    
    # Check for nulls in key columns
    key_columns = id_columns + [col for col in df.columns if col in ['equipment_id', 'prediction_date', 'failure_date']]
    for col in key_columns:
        if col in df.columns:
            null_count = df[col].isna().sum()
            if null_count > 0:
                integrity_errors.append(f"Found {null_count} null values in key column {col}")
    
    if integrity_errors:
        error_message = f"Data integrity validation failed for {data_name}:\n"
        error_message += "\n".join([f"  - {error}" for error in integrity_errors])
        return False, error_message
    
    return True, f"Data integrity validation passed for {data_name}"

def validate_data(df, data_type, add_missing_columns=True):
    """Validate data against expected schema"""
    if data_type not in EXPECTED_SCHEMAS:
        return False, f"Unknown data type: {data_type}", df
    
    schema = EXPECTED_SCHEMAS[data_type]
    required_columns = schema['required_columns']
    column_types = schema.get('column_types', {})
    
    # Validate column presence
    columns_valid, columns_message, missing_columns = validate_column_presence(df, required_columns, data_type)
    
    # Add missing columns if requested
    if not columns_valid and add_missing_columns:
        print(f"⚠️ {columns_message}")
        print(f"⚠️ Adding missing columns with default values")
        
        for col in missing_columns:
            if col in column_types:
                expected_type = column_types[col]
                if isinstance(expected_type, list):
                    expected_type = expected_type[0]
                
                # Set default value based on type
                if expected_type == str:
                    df[col] = ""
                elif expected_type == int:
                    df[col] = 0
                elif expected_type == float:
                    df[col] = 0.0
                elif expected_type in [date, datetime]:
                    df[col] = pd.NaT
                elif expected_type == bool:
                    df[col] = False
                else:
                    df[col] = None
            else:
                df[col] = None
        
        columns_valid = True
        print(f"✅ Added missing columns: {', '.join(missing_columns)}")
    
    # Validate column types
    types_valid, types_message = validate_column_types(df, column_types, data_type)
    
    # Validate data integrity
    integrity_valid, integrity_message = validate_data_integrity(df, data_type)
    
    # Combine validation results
    valid = columns_valid and types_valid and integrity_valid
    
    if not valid:
        error_message = "Data validation failed:\n"
        if not columns_valid:
            error_message += f"  {columns_message}\n"
        if not types_valid:
            error_message += f"  {types_message}\n"
        if not integrity_valid:
            error_message += f"  {integrity_message}\n"
        
        return valid, error_message, df
    
    return True, f"Data validation passed for {data_type}", df

def validate_pipeline_data(data):
    """Validate all data for the pipeline"""
    print("\n🔍 Validating pipeline data...")
    
    all_valid = True
    validation_results = {}
    validated_data = {}
    
    # Validate each data type
    for data_type, expected_schema in EXPECTED_SCHEMAS.items():
        if data_type in data:
            df = data[data_type]
            valid, message, validated_df = validate_data(df, data_type)
            
            validation_results[data_type] = {
                'valid': valid,
                'message': message
            }
            
            validated_data[data_type] = validated_df
            
            if not valid:
                all_valid = False
                print(f"❌ {message}")
            else:
                print(f"✅ {message}")
    
    if all_valid:
        print("\n✅ All data validated successfully!")
    else:
        print("\n⚠️ Data validation found issues. Proceeding with caution.")
    
    return all_valid, validation_results, validated_data

if __name__ == "__main__":
    # Test with sample data
    equipment_df = pd.DataFrame({
        'equipment_id': ['E001', 'E002', 'E003'],
        'equipment_type': ['Pump', 'Motor', 'Valve'],
        'status': ['Active', 'Active', 'Inactive']
    })
    
    valid, message, validated_df = validate_data(equipment_df, 'equipment')
    print(f"Validation result: {valid}")
    print(message)
