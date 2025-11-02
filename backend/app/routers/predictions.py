"""
Predictions Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import date
from ..database import get_db

router = APIRouter()

@router.get("/predictions")
async def get_all_predictions(
    skip: int = 0,
    limit: int = 100,
    priority_level: Optional[str] = None,
    min_risk_score: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Get all predictions with optional filters"""
    
    query = """
        SELECT 
            p.prediction_id,
            p.equipment_id,
            e.equipment_type,
            e.location,
            p.prediction_date,
            p.svm_prediction,
            p.svm_probability,
            p.xgb_prediction,
            p.xgb_probability,
            p.risk_score,
            p.priority_level,
            p.recommended_action
        FROM predictions p
        JOIN equipment e ON p.equipment_id = e.equipment_id
        WHERE 1=1
    """
    
    params = {}
    
    if priority_level:
        query += " AND p.priority_level = :priority_level"
        params['priority_level'] = priority_level
    
    if min_risk_score is not None:
        query += " AND p.risk_score >= :min_risk_score"
        params['min_risk_score'] = min_risk_score
    
    query += " ORDER BY p.risk_score DESC OFFSET :skip LIMIT :limit"
    params['skip'] = skip
    params['limit'] = limit
    
    result = db.execute(text(query), params)
    predictions = [dict(row._mapping) for row in result]
    
    return {
        "total": len(predictions),
        "data": predictions
    }

@router.get("/predictions/latest")
async def get_latest_predictions(
    db: Session = Depends(get_db)
):
    """Get latest predictions (today's predictions)"""
    
    query = text("""
        SELECT 
            p.prediction_id,
            p.equipment_id,
            e.equipment_type,
            e.location,
            p.prediction_date,
            p.risk_score,
            p.priority_level,
            p.recommended_action
        FROM predictions p
        JOIN equipment e ON p.equipment_id = e.equipment_id
        WHERE p.prediction_date = CURRENT_DATE
        ORDER BY p.risk_score DESC
    """)
    
    result = db.execute(query)
    predictions = [dict(row._mapping) for row in result]
    
    return {
        "date": date.today().isoformat(),
        "total": len(predictions),
        "data": predictions
    }

@router.get("/predictions/stats/summary")
async def get_predictions_summary(db: Session = Depends(get_db)):
    """Get predictions summary statistics"""
    
    query = text("""
        SELECT 
            COUNT(*) as total_predictions,
            AVG(risk_score) as avg_risk_score,
            MAX(risk_score) as max_risk_score,
            MIN(risk_score) as min_risk_score,
            COUNT(CASE WHEN priority_level = 'Critical' THEN 1 END) as critical_count,
            COUNT(CASE WHEN priority_level = 'High' THEN 1 END) as high_count,
            COUNT(CASE WHEN priority_level = 'Medium' THEN 1 END) as medium_count,
            COUNT(CASE WHEN priority_level = 'Low' THEN 1 END) as low_count
        FROM predictions
        WHERE prediction_date = CURRENT_DATE
    """)
    
    result = db.execute(query)
    stats = dict(result.fetchone()._mapping)
    
    return stats

@router.get("/predictions/high-risk")
async def get_high_risk_equipment(
    threshold: float = 40.0,
    db: Session = Depends(get_db)
):
    """Get high-risk equipment (risk score above threshold)"""
    
    query = text("""
        SELECT 
            p.equipment_id,
            e.equipment_type,
            e.location,
            p.risk_score,
            p.priority_level,
            p.recommended_action
        FROM predictions p
        JOIN equipment e ON p.equipment_id = e.equipment_id
        WHERE p.prediction_date = CURRENT_DATE
        AND p.risk_score >= :threshold
        ORDER BY p.risk_score DESC
    """)
    
    result = db.execute(query, {"threshold": threshold})
    high_risk = [dict(row._mapping) for row in result]
    
    return {
        "threshold": threshold,
        "count": len(high_risk),
        "equipment": high_risk
    }

@router.get("/predictions/{equipment_id}")
async def get_equipment_prediction(
    equipment_id: str,
    db: Session = Depends(get_db)
):
    """Get latest prediction for specific equipment"""
    
    query = text("""
        SELECT 
            p.prediction_id,
            p.equipment_id,
            e.equipment_type,
            e.brand,
            e.model,
            e.location,
            p.prediction_date,
            p.svm_prediction,
            p.svm_probability,
            p.xgb_prediction,
            p.xgb_probability,
            p.risk_score,
            p.priority_level,
            p.recommended_action
        FROM predictions p
        JOIN equipment e ON p.equipment_id = e.equipment_id
        WHERE p.equipment_id = :equipment_id
        ORDER BY p.prediction_date DESC
        LIMIT 1
    """)
    
    result = db.execute(query, {"equipment_id": equipment_id})
    prediction = result.fetchone()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="No prediction found for this equipment")
    
    return dict(prediction._mapping)
