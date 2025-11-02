"""
Maintenance Operations Endpoints (POST/PUT)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from ..schemas import MaintenanceRecordCreate, FailureEventCreate

router = APIRouter()

# ===== POST: Log Maintenance Record =====

@router.post("/maintenance", status_code=status.HTTP_201_CREATED)
async def log_maintenance(
    maintenance: MaintenanceRecordCreate,
    db: Session = Depends(get_db)
):
    """Log a new maintenance record"""
    
    try:
        # Verify equipment exists
        check_query = text("SELECT equipment_id FROM equipment WHERE equipment_id = :equipment_id")
        existing = db.execute(check_query, {"equipment_id": maintenance.equipment_id}).fetchone()
        
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"Equipment {maintenance.equipment_id} not found"
            )
        
        # Insert maintenance record
        insert_query = text("""
            INSERT INTO maintenance_records (
                equipment_id, maintenance_date, type_id, description,
                technician, parts_replaced, total_cost, downtime_hours
            ) VALUES (
                :equipment_id, :maintenance_date, :type_id, :description,
                :technician, :parts_replaced, :total_cost, :downtime_hours
            )
            RETURNING record_id
        """)
        
        result = db.execute(insert_query, maintenance.dict())
        record_id = result.fetchone()[0]
        db.commit()
        
        # Update equipment last_service_date
        update_query = text("""
            UPDATE equipment 
            SET last_service_date = :maintenance_date, updated_at = CURRENT_TIMESTAMP
            WHERE equipment_id = :equipment_id
        """)
        db.execute(update_query, {
            "maintenance_date": maintenance.maintenance_date,
            "equipment_id": maintenance.equipment_id
        })
        db.commit()
        
        return {
            "message": "Maintenance record logged successfully",
            "record_id": record_id,
            "equipment_id": maintenance.equipment_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error logging maintenance: {str(e)}")

# ===== POST: Log Failure Event =====

@router.post("/failures", status_code=status.HTTP_201_CREATED)
async def log_failure(
    failure: FailureEventCreate,
    db: Session = Depends(get_db)
):
    """Log a new failure event"""
    
    try:
        # Verify equipment exists
        check_query = text("SELECT equipment_id FROM equipment WHERE equipment_id = :equipment_id")
        existing = db.execute(check_query, {"equipment_id": failure.equipment_id}).fetchone()
        
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"Equipment {failure.equipment_id} not found"
            )
        
        # Insert failure event
        insert_query = text("""
            INSERT INTO failure_events (
                equipment_id, failure_date, failure_type, severity,
                description, repair_cost, downtime_hours, prevented_by_maintenance
            ) VALUES (
                :equipment_id, :failure_date, :failure_type, :severity,
                :description, :repair_cost, :downtime_hours, :prevented_by_maintenance
            )
            RETURNING failure_id
        """)
        
        result = db.execute(insert_query, failure.dict())
        failure_id = result.fetchone()[0]
        db.commit()
        
        return {
            "message": "Failure event logged successfully",
            "failure_id": failure_id,
            "equipment_id": failure.equipment_id,
            "severity": failure.severity
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error logging failure: {str(e)}")

# ===== GET: Maintenance Types =====

@router.get("/maintenance/types")
async def get_maintenance_types():
    """Get maintenance type definitions"""
    return {
        "types": [
            {"id": 1, "name": "Preventive", "description": "Scheduled preventive maintenance"},
            {"id": 2, "name": "Corrective", "description": "Corrective maintenance after issue detected"},
            {"id": 3, "name": "Emergency", "description": "Emergency maintenance for critical failures"}
        ]
    }
