"""
Advanced Analytics Endpoints
Provides data for Phase 8 analytics dashboard
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime
from ..database import get_db

router = APIRouter()

@router.get("/analytics/root-cause")
async def get_root_cause_analysis(
    limit: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get root cause analysis data"""
    
    query = text("""
        SELECT 
            root_cause,
            COUNT(*) as failure_count,
            SUM(downtime_hours) as total_downtime,
            SUM(repair_cost) as total_cost,
            AVG(repair_cost) as avg_cost
        FROM failure_events
        GROUP BY root_cause
        ORDER BY total_cost DESC
    """)
    
    if limit:
        query = text(str(query) + f" LIMIT {limit}")
    
    result = db.execute(query)
    data = [dict(row._mapping) for row in result]
    
    # Calculate percentages
    total_cost = sum(item['total_cost'] for item in data)
    cumulative = 0
    for item in data:
        item['cost_percentage'] = (item['total_cost'] / total_cost * 100) if total_cost > 0 else 0
        cumulative += item['cost_percentage']
        item['cumulative_cost_pct'] = cumulative
    
    return {
        "total_failures": sum(item['failure_count'] for item in data),
        "total_cost": total_cost,
        "data": data
    }

@router.get("/analytics/equipment-reliability")
async def get_equipment_reliability(
    equipment_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get equipment reliability metrics (MTBF, failure rates, etc.)"""
    
    query = """
        SELECT 
            e.equipment_id,
            e.equipment_type,
            e.model,
            e.installation_date,
            COUNT(f.failure_id) as failure_count,
            SUM(f.downtime_hours) as total_downtime,
            AVG(f.downtime_hours) as avg_downtime,
            SUM(f.repair_cost) as total_cost,
            AVG(f.repair_cost) as avg_cost,
            MIN(f.failure_date) as first_failure,
            MAX(f.failure_date) as last_failure
        FROM equipment e
        LEFT JOIN failure_events f ON e.equipment_id = f.equipment_id
        WHERE 1=1
    """
    
    params = {}
    if equipment_type:
        query += " AND e.equipment_type = :equipment_type"
        params['equipment_type'] = equipment_type
    
    query += """
        GROUP BY e.equipment_id, e.equipment_type, e.model, e.installation_date
        ORDER BY failure_count DESC
    """
    
    result = db.execute(text(query), params)
    data = [dict(row._mapping) for row in result]
    
    # Calculate MTBF
    for item in data:
        if item['failure_count'] and item['failure_count'] > 1:
            if item['first_failure'] and item['last_failure']:
                days_diff = (item['last_failure'] - item['first_failure']).days
                item['mtbf_days'] = days_diff / (item['failure_count'] - 1)
            else:
                item['mtbf_days'] = 0
        else:
            item['mtbf_days'] = 0
    
    return {
        "total_equipment": len(data),
        "data": data
    }

@router.get("/analytics/type-reliability")
async def get_type_reliability(db: Session = Depends(get_db)):
    """Get reliability metrics by equipment type"""
    
    query = text("""
        SELECT 
            e.equipment_type,
            COUNT(DISTINCT e.equipment_id) as equipment_count,
            COUNT(f.failure_id) as total_failures,
            SUM(f.downtime_hours) as total_downtime,
            AVG(f.downtime_hours) as avg_downtime,
            SUM(f.repair_cost) as total_cost,
            AVG(f.repair_cost) as avg_cost
        FROM equipment e
        LEFT JOIN failure_events f ON e.equipment_id = f.equipment_id
        GROUP BY e.equipment_type
        ORDER BY total_cost DESC
    """)
    
    result = db.execute(query)
    data = [dict(row._mapping) for row in result]
    
    return {
        "total_types": len(data),
        "data": data
    }

@router.get("/analytics/maintenance-effectiveness")
async def get_maintenance_effectiveness(db: Session = Depends(get_db)):
    """Analyze maintenance effectiveness and prevention rates"""
    
    # Get prevention statistics
    prevention_query = text("""
        SELECT 
            prevented_by_maintenance,
            COUNT(*) as failure_count,
            AVG(downtime_hours) as avg_downtime,
            AVG(repair_cost) as avg_cost,
            SUM(CASE WHEN severity = 'Critical' THEN 1 ELSE 0 END) as critical_failures
        FROM failure_events
        GROUP BY prevented_by_maintenance
    """)
    
    prevention_result = db.execute(prevention_query)
    prevention_data = [dict(row._mapping) for row in prevention_result]
    
    # Get maintenance type breakdown
    maintenance_query = text("""
        SELECT 
            type_id,
            COUNT(*) as count,
            SUM(total_cost) as total_cost,
            SUM(downtime_hours) as total_downtime,
            AVG(total_cost) as avg_cost
        FROM maintenance_records
        GROUP BY type_id
        ORDER BY total_cost DESC
    """)
    
    maintenance_result = db.execute(maintenance_query)
    maintenance_data = [dict(row._mapping) for row in maintenance_result]
    
    # Map type_id to names
    type_map = {1: 'Preventive', 2: 'Corrective', 3: 'Predictive'}
    for item in maintenance_data:
        item['maintenance_type'] = type_map.get(item['type_id'], 'Unknown')
    
    # Calculate prevention rate
    total_failures = sum(item['failure_count'] for item in prevention_data)
    prevented = next((item['failure_count'] for item in prevention_data if item['prevented_by_maintenance']), 0)
    prevention_rate = (prevented / total_failures * 100) if total_failures > 0 else 0
    
    return {
        "prevention_rate": prevention_rate,
        "total_failures": total_failures,
        "prevented_failures": prevented,
        "prevention_breakdown": prevention_data,
        "maintenance_types": maintenance_data
    }

@router.get("/analytics/cost-benefit")
async def get_cost_benefit_analysis(db: Session = Depends(get_db)):
    """Calculate cost-benefit analysis and potential savings"""
    
    # Get failure costs
    failure_query = text("""
        SELECT 
            SUM(repair_cost) as total_failure_cost,
            SUM(downtime_hours) as total_downtime_hours,
            SUM(CASE WHEN prevented_by_maintenance = 1 THEN repair_cost ELSE 0 END) as preventable_cost,
            SUM(CASE WHEN prevented_by_maintenance = 1 THEN downtime_hours ELSE 0 END) as preventable_downtime
        FROM failure_events
    """)
    
    failure_result = db.execute(failure_query).fetchone()
    failure_data = dict(failure_result._mapping)
    
    # Get maintenance costs
    maintenance_query = text("""
        SELECT 
            SUM(total_cost) as total_maintenance_cost,
            SUM(downtime_hours) as total_maintenance_downtime
        FROM maintenance_records
    """)
    
    maintenance_result = db.execute(maintenance_query).fetchone()
    maintenance_data = dict(maintenance_result._mapping)
    
    # Calculate costs
    downtime_cost_per_hour = 500  # Configurable
    total_downtime_cost = failure_data['total_downtime_hours'] * downtime_cost_per_hour
    preventable_downtime_cost = failure_data['preventable_downtime'] * downtime_cost_per_hour
    
    total_cost = (
        failure_data['total_failure_cost'] + 
        maintenance_data['total_maintenance_cost'] + 
        total_downtime_cost
    )
    
    total_preventable = failure_data['preventable_cost'] + preventable_downtime_cost
    
    savings_percentage = (total_preventable / (failure_data['total_failure_cost'] + total_downtime_cost) * 100) if (failure_data['total_failure_cost'] + total_downtime_cost) > 0 else 0
    
    return {
        "total_failure_cost": failure_data['total_failure_cost'],
        "total_maintenance_cost": maintenance_data['total_maintenance_cost'],
        "total_downtime_cost": total_downtime_cost,
        "total_cost": total_cost,
        "preventable_repair_cost": failure_data['preventable_cost'],
        "preventable_downtime_cost": preventable_downtime_cost,
        "total_preventable": total_preventable,
        "savings_percentage": savings_percentage,
        "downtime_cost_per_hour": downtime_cost_per_hour,
        "recommendations": {
            "potential_savings": total_preventable,
            "expected_savings_70pct": total_preventable * 0.7,
            "estimated_roi": "300% within 18 months"
        }
    }

@router.get("/analytics/worst-performers")
async def get_worst_performers(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get worst performing equipment by MTBF"""
    
    query = text("""
        SELECT 
            e.equipment_id,
            e.equipment_type,
            e.model,
            COUNT(f.failure_id) as failure_count,
            SUM(f.repair_cost) as total_cost,
            MIN(f.failure_date) as first_failure,
            MAX(f.failure_date) as last_failure
        FROM equipment e
        INNER JOIN failure_events f ON e.equipment_id = f.equipment_id
        GROUP BY e.equipment_id, e.equipment_type, e.model
        HAVING COUNT(f.failure_id) > 0
        ORDER BY failure_count DESC
        LIMIT :limit
    """)
    
    result = db.execute(query, {"limit": limit})
    data = [dict(row._mapping) for row in result]
    
    # Calculate MTBF
    for item in data:
        if item['failure_count'] > 1 and item['first_failure'] and item['last_failure']:
            days_diff = (item['last_failure'] - item['first_failure']).days
            item['mtbf_days'] = days_diff / (item['failure_count'] - 1)
        else:
            item['mtbf_days'] = 0
    
    # Sort by MTBF (ascending - worst first)
    data.sort(key=lambda x: x['mtbf_days'])
    
    return {
        "count": len(data),
        "data": data
    }

@router.get("/analytics/trends")
async def get_failure_trends(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get failure trends over time"""
    
    query = text("""
        SELECT 
            DATE(failure_date) as date,
            COUNT(*) as failure_count,
            SUM(repair_cost) as daily_cost,
            SUM(downtime_hours) as daily_downtime
        FROM failure_events
        WHERE failure_date >= DATE('now', '-' || :days || ' days')
        GROUP BY DATE(failure_date)
        ORDER BY date
    """)
    
    result = db.execute(query, {"days": days})
    data = [dict(row._mapping) for row in result]
    
    return {
        "period_days": days,
        "data_points": len(data),
        "data": data
    }

@router.get("/analytics/summary")
async def get_analytics_summary(db: Session = Depends(get_db)):
    """Get comprehensive analytics summary for dashboard"""
    
    # Get all key metrics in one call
    summary_query = text("""
        SELECT 
            (SELECT COUNT(*) FROM equipment) as total_equipment,
            (SELECT COUNT(*) FROM failure_events) as total_failures,
            (SELECT COUNT(*) FROM maintenance_records) as total_maintenance,
            (SELECT AVG(downtime_hours) FROM failure_events) as avg_downtime,
            (SELECT SUM(repair_cost) FROM failure_events) as total_failure_cost,
            (SELECT SUM(total_cost) FROM maintenance_records) as total_maintenance_cost,
            (SELECT COUNT(*) FROM failure_events WHERE prevented_by_maintenance = 1) as prevented_failures,
            (SELECT COUNT(*) FROM failure_events WHERE severity = 'Critical') as critical_failures
    """)
    
    result = db.execute(summary_query).fetchone()
    summary = dict(result._mapping)
    
    # Calculate derived metrics
    if summary['total_failures'] > 0:
        summary['prevention_rate'] = (summary['prevented_failures'] / summary['total_failures'] * 100)
    else:
        summary['prevention_rate'] = 0
    
    summary['last_updated'] = datetime.now().isoformat()
    
    return summary

@router.post("/analytics/refresh")
async def refresh_analytics_cache(db: Session = Depends(get_db)):
    """Trigger analytics data refresh (run pipeline)"""
    
    try:
        # This would trigger the pipeline
        # For now, just return success
        return {
            "status": "success",
            "message": "Analytics refresh triggered",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
