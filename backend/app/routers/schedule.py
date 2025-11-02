"""
Maintenance Schedule Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import date, timedelta
from ..database import get_db
from ..schemas import ScheduleUpdate

router = APIRouter()

@router.get("/schedule")
async def get_maintenance_schedule(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get maintenance schedule with optional filters"""
    
    try:
        query = """
            SELECT 
                ms.schedule_id,
                ms.equipment_id,
                e.equipment_type,
                e.location,
                ms.scheduled_date,
                ms.priority_level,
                ms.risk_score,
                ms.status,
                ms.assigned_technician,
                ms.estimated_cost,
                ms.estimated_duration_hours
            FROM maintenance_schedule ms
            JOIN equipment e ON ms.equipment_id = e.equipment_id
            WHERE 1=1
        """
        
        params = {}
        
        if status:
            query += " AND ms.status = :status"
            params['status'] = status
        
        if priority_level:
            query += " AND ms.priority_level = :priority_level"
            params['priority_level'] = priority_level
        
        query += " ORDER BY ms.scheduled_date OFFSET :skip LIMIT :limit"
        params['skip'] = skip
        params['limit'] = limit
        
        result = db.execute(text(query), params)
        schedule = [dict(row._mapping) for row in result]
        
        return {
            "total": len(schedule),
            "data": schedule
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/schedule/upcoming")
async def get_upcoming_maintenance(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get upcoming maintenance tasks (next N days)"""
    
    end_date = date.today() + timedelta(days=days)
    
    query = text("""
        SELECT 
            ms.schedule_id,
            ms.equipment_id,
            e.equipment_type,
            e.location,
            ms.scheduled_date,
            ms.priority_level,
            ms.risk_score,
            ms.assigned_technician,
            ms.estimated_cost,
            ms.estimated_duration_hours
        FROM maintenance_schedule ms
        JOIN equipment e ON ms.equipment_id = e.equipment_id
        WHERE ms.status = 'Scheduled'
        AND ms.scheduled_date BETWEEN CURRENT_DATE AND :end_date
        ORDER BY ms.scheduled_date, ms.priority_level
    """)
    
    result = db.execute(query, {"end_date": end_date})
    upcoming = [dict(row._mapping) for row in result]
    
    return {
        "period": f"Next {days} days",
        "start_date": date.today().isoformat(),
        "end_date": end_date.isoformat(),
        "count": len(upcoming),
        "tasks": upcoming
    }

@router.get("/schedule/overdue")
async def get_overdue_maintenance(db: Session = Depends(get_db)):
    """Get overdue maintenance tasks"""
    
    query = text("""
        SELECT 
            ms.schedule_id,
            ms.equipment_id,
            e.equipment_type,
            e.location,
            ms.scheduled_date,
            ms.priority_level,
            ms.risk_score,
            ms.assigned_technician,
            CURRENT_DATE - ms.scheduled_date as days_overdue
        FROM maintenance_schedule ms
        JOIN equipment e ON ms.equipment_id = e.equipment_id
        WHERE ms.status = 'Scheduled'
        AND ms.scheduled_date < CURRENT_DATE
        ORDER BY ms.scheduled_date
    """)
    
    result = db.execute(query)
    overdue = [dict(row._mapping) for row in result]
    
    return {
        "count": len(overdue),
        "tasks": overdue
    }

@router.get("/schedule/by-technician/{technician}")
async def get_technician_schedule(
    technician: str,
    db: Session = Depends(get_db)
):
    """Get schedule for specific technician"""
    
    query = text("""
        SELECT 
            ms.schedule_id,
            ms.equipment_id,
            e.equipment_type,
            e.location,
            ms.scheduled_date,
            ms.priority_level,
            ms.status,
            ms.estimated_duration_hours
        FROM maintenance_schedule ms
        JOIN equipment e ON ms.equipment_id = e.equipment_id
        WHERE ms.assigned_technician = :technician
        AND ms.status = 'Scheduled'
        ORDER BY ms.scheduled_date
    """)
    
    result = db.execute(query, {"technician": technician})
    tasks = [dict(row._mapping) for row in result]
    
    # Calculate total hours
    total_hours = sum(task.get('estimated_duration_hours', 0) or 0 for task in tasks)
    
    return {
        "technician": technician,
        "total_tasks": len(tasks),
        "total_estimated_hours": total_hours,
        "tasks": tasks
    }

@router.get("/schedule/stats/summary")
async def get_schedule_summary(db: Session = Depends(get_db)):
    """Get schedule summary statistics"""
    
    query = text("""
        SELECT 
            COUNT(*) as total_tasks,
            COUNT(CASE WHEN status = 'Scheduled' THEN 1 END) as scheduled_count,
            COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed_count,
            COUNT(CASE WHEN status = 'In Progress' THEN 1 END) as in_progress_count,
            COUNT(CASE WHEN priority_level = 'Critical' THEN 1 END) as critical_count,
            COUNT(CASE WHEN priority_level = 'High' THEN 1 END) as high_count,
            SUM(estimated_cost) as total_estimated_cost,
            SUM(estimated_duration_hours) as total_estimated_hours
        FROM maintenance_schedule
        WHERE status = 'Scheduled'
    """)
    
    result = db.execute(query)
    stats = dict(result.fetchone()._mapping)
    
    return stats

# ===== PUT: Update Schedule =====

@router.put("/schedule/{schedule_id}")
async def update_schedule(
    schedule_id: int,
    schedule: ScheduleUpdate,
    db: Session = Depends(get_db)
):
    """Update maintenance schedule task"""
    
    try:
        # Check if schedule exists
        check_query = text("SELECT schedule_id FROM maintenance_schedule WHERE schedule_id = :schedule_id")
        existing = db.execute(check_query, {"schedule_id": schedule_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail=f"Schedule task {schedule_id} not found")
        
        # Build update query dynamically
        update_fields = []
        params = {"schedule_id": schedule_id}
        
        for field, value in schedule.dict(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = :{field}")
                params[field] = value
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_query = text(f"""
            UPDATE maintenance_schedule 
            SET {', '.join(update_fields)}
            WHERE schedule_id = :schedule_id
        """)
        
        db.execute(update_query, params)
        db.commit()
        
        return {
            "message": f"Schedule task {schedule_id} updated successfully",
            "schedule_id": schedule_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating schedule: {str(e)}")

# ===== PUT: Mark Schedule as Completed =====

@router.put("/schedule/{schedule_id}/complete")
async def complete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Mark schedule task as completed"""
    
    try:
        # Check if schedule exists
        check_query = text("SELECT schedule_id, equipment_id FROM maintenance_schedule WHERE schedule_id = :schedule_id")
        existing = db.execute(check_query, {"schedule_id": schedule_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail=f"Schedule task {schedule_id} not found")
        
        # Update status to Completed
        update_query = text("""
            UPDATE maintenance_schedule 
            SET status = 'Completed'
            WHERE schedule_id = :schedule_id
        """)
        
        db.execute(update_query, {"schedule_id": schedule_id})
        db.commit()
        
        return {
            "message": f"Schedule task {schedule_id} marked as completed",
            "schedule_id": schedule_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error completing schedule: {str(e)}")

# ===== DELETE: Cancel Schedule =====

@router.delete("/schedule/{schedule_id}")
async def cancel_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Cancel/delete a scheduled maintenance task"""
    
    try:
        # Check if schedule exists
        check_query = text("SELECT schedule_id FROM maintenance_schedule WHERE schedule_id = :schedule_id")
        existing = db.execute(check_query, {"schedule_id": schedule_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail=f"Schedule task {schedule_id} not found")
        
        # Delete schedule
        delete_query = text("DELETE FROM maintenance_schedule WHERE schedule_id = :schedule_id")
        db.execute(delete_query, {"schedule_id": schedule_id})
        db.commit()
        
        return {
            "message": f"Schedule task {schedule_id} cancelled successfully",
            "schedule_id": schedule_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error cancelling schedule: {str(e)}")
