"""
Equipment Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from ..database import get_db
from ..schemas import EquipmentCreate, EquipmentUpdate, MessageResponse

router = APIRouter()

@router.get("/equipment")
async def get_all_equipment(
    skip: int = 0,
    limit: int = 100,
    equipment_type: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all equipment with optional filters"""
    
    query = """
        SELECT 
            equipment_id,
            equipment_type,
            brand,
            model,
            year_manufactured,
            purchase_date,
            location,
            operating_hours,
            last_service_date
        FROM equipment
        WHERE 1=1
    """
    
    params = {}
    
    if equipment_type:
        query += " AND equipment_type = :equipment_type"
        params['equipment_type'] = equipment_type
    
    if location:
        query += " AND location = :location"
        params['location'] = location
    
    query += " ORDER BY equipment_id OFFSET :skip LIMIT :limit"
    params['skip'] = skip
    params['limit'] = limit
    
    result = db.execute(text(query), params)
    equipment = [dict(row._mapping) for row in result]
    
    return {
        "total": len(equipment),
        "data": equipment
    }

@router.get("/equipment/by-type/{equipment_type}")
async def get_equipment_by_type(
    equipment_type: str,
    db: Session = Depends(get_db)
):
    """Get all equipment of a specific type"""
    
    query = text("""
        SELECT 
            equipment_id,
            equipment_type,
            brand,
            model,
            year_manufactured,
            purchase_date,
            location,
            operating_hours,
            last_service_date
        FROM equipment
        WHERE equipment_type = :equipment_type
        ORDER BY equipment_id
    """)
    
    result = db.execute(query, {"equipment_type": equipment_type})
    equipment = [dict(row._mapping) for row in result]
    
    return {
        "equipment_type": equipment_type,
        "count": len(equipment),
        "data": equipment
    }

@router.get("/equipment/by-location/{location}")
async def get_equipment_by_location(
    location: str,
    db: Session = Depends(get_db)
):
    """Get all equipment at a specific location"""
    
    query = text("""
        SELECT 
            equipment_id,
            equipment_type,
            brand,
            model,
            year_manufactured,
            purchase_date,
            location,
            operating_hours,
            last_service_date
        FROM equipment
        WHERE location = :location
        ORDER BY equipment_id
    """)
    
    result = db.execute(query, {"location": location})
    equipment = [dict(row._mapping) for row in result]
    
    return {
        "location": location,
        "count": len(equipment),
        "data": equipment
    }

@router.get("/equipment/{equipment_id}")
async def get_equipment_by_id(
    equipment_id: str,
    db: Session = Depends(get_db)
):
    """Get specific equipment by ID"""
    
    query = text("""
        SELECT 
            equipment_id,
            equipment_type,
            brand,
            model,
            year_manufactured,
            purchase_date,
            location,
            operating_hours,
            last_service_date
        FROM equipment
        WHERE equipment_id = :equipment_id
    """)
    
    result = db.execute(query, {"equipment_id": equipment_id})
    equipment = result.fetchone()
    
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    return dict(equipment._mapping)

@router.get("/equipment/{equipment_id}/maintenance-history")
async def get_equipment_maintenance_history(
    equipment_id: str,
    db: Session = Depends(get_db)
):
    """Get maintenance history for specific equipment"""
    
    query = text("""
        SELECT 
            record_id,
            equipment_id,
            maintenance_date,
            type_id,
            description,
            technician,
            parts_replaced,
            total_cost,
            downtime_hours
        FROM maintenance_records
        WHERE equipment_id = :equipment_id
        ORDER BY maintenance_date DESC
    """)
    
    result = db.execute(query, {"equipment_id": equipment_id})
    history = [dict(row._mapping) for row in result]
    
    return {
        "equipment_id": equipment_id,
        "total_records": len(history),
        "maintenance_history": history
    }

@router.get("/equipment/{equipment_id}/failure-history")
async def get_equipment_failure_history(
    equipment_id: str,
    db: Session = Depends(get_db)
):
    """Get failure history for specific equipment"""
    
    query = text("""
        SELECT 
            failure_id,
            equipment_id,
            failure_date,
            failure_type,
            severity,
            description,
            repair_cost,
            downtime_hours,
            prevented_by_maintenance
        FROM failure_events
        WHERE equipment_id = :equipment_id
        ORDER BY failure_date DESC
    """)
    
    result = db.execute(query, {"equipment_id": equipment_id})
    history = [dict(row._mapping) for row in result]
    
    return {
        "equipment_id": equipment_id,
        "total_failures": len(history),
        "failure_history": history
    }

@router.get("/equipment/stats/summary")
async def get_equipment_summary(db: Session = Depends(get_db)):
    """Get equipment summary statistics"""
    
    query = text("""
        SELECT 
            COUNT(*) as total_equipment,
            COUNT(DISTINCT equipment_type) as equipment_types,
            COUNT(DISTINCT location) as locations,
            AVG(operating_hours) as avg_operating_hours,
            SUM(operating_hours) as total_operating_hours
        FROM equipment
    """)
    
    result = db.execute(query)
    stats = dict(result.fetchone()._mapping)
    
    # Get equipment by type
    type_query = text("""
        SELECT 
            equipment_type,
            COUNT(*) as count
        FROM equipment
        GROUP BY equipment_type
        ORDER BY count DESC
    """)
    
    type_result = db.execute(type_query)
    by_type = [dict(row._mapping) for row in type_result]
    
    return {
        "summary": stats,
        "by_type": by_type
    }

# ===== POST: Create Equipment =====

@router.post("/equipment", status_code=status.HTTP_201_CREATED)
async def create_equipment(
    equipment: EquipmentCreate,
    db: Session = Depends(get_db)
):
    """Create new equipment"""
    
    try:
        # Check if equipment already exists
        check_query = text("SELECT equipment_id FROM equipment WHERE equipment_id = :equipment_id")
        existing = db.execute(check_query, {"equipment_id": equipment.equipment_id}).fetchone()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Equipment with ID {equipment.equipment_id} already exists"
            )
        
        # Insert new equipment
        insert_query = text("""
            INSERT INTO equipment (
                equipment_id, equipment_type, brand, model, year_manufactured,
                purchase_date, location, operating_hours, last_service_date
            ) VALUES (
                :equipment_id, :equipment_type, :brand, :model, :year_manufactured,
                :purchase_date, :location, :operating_hours, :last_service_date
            )
        """)
        
        db.execute(insert_query, equipment.dict())
        db.commit()
        
        return {
            "message": f"Equipment {equipment.equipment_id} created successfully",
            "equipment_id": equipment.equipment_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating equipment: {str(e)}")

# ===== PUT: Update Equipment =====

@router.put("/equipment/{equipment_id}")
async def update_equipment(
    equipment_id: str,
    equipment: EquipmentUpdate,
    db: Session = Depends(get_db)
):
    """Update existing equipment"""
    
    try:
        # Check if equipment exists
        check_query = text("SELECT equipment_id FROM equipment WHERE equipment_id = :equipment_id")
        existing = db.execute(check_query, {"equipment_id": equipment_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail=f"Equipment {equipment_id} not found")
        
        # Build update query dynamically
        update_fields = []
        params = {"equipment_id": equipment_id}
        
        for field, value in equipment.dict(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = :{field}")
                params[field] = value
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_query = text(f"""
            UPDATE equipment 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE equipment_id = :equipment_id
        """)
        
        db.execute(update_query, params)
        db.commit()
        
        return {
            "message": f"Equipment {equipment_id} updated successfully",
            "equipment_id": equipment_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating equipment: {str(e)}")

# ===== DELETE: Delete Equipment =====

@router.delete("/equipment/{equipment_id}")
async def delete_equipment(
    equipment_id: str,
    db: Session = Depends(get_db)
):
    """Delete equipment (and all related records due to CASCADE)"""
    
    try:
        # Check if equipment exists
        check_query = text("SELECT equipment_id FROM equipment WHERE equipment_id = :equipment_id")
        existing = db.execute(check_query, {"equipment_id": equipment_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail=f"Equipment {equipment_id} not found")
        
        # Delete equipment (CASCADE will delete related records)
        delete_query = text("DELETE FROM equipment WHERE equipment_id = :equipment_id")
        db.execute(delete_query, {"equipment_id": equipment_id})
        db.commit()
        
        return {
            "message": f"Equipment {equipment_id} deleted successfully",
            "equipment_id": equipment_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting equipment: {str(e)}")
