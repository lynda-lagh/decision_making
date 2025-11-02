"""
KPIs Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import date
from ..database import get_db

router = APIRouter()

@router.get("/kpis")
async def get_all_kpis(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all KPIs with optional category filter"""
    
    query = """
        SELECT 
            metric_id,
            metric_name,
            metric_category,
            metric_value,
            target_value,
            measurement_date,
            period,
            status,
            notes
        FROM kpi_metrics
        WHERE measurement_date = CURRENT_DATE
    """
    
    params = {}
    
    if category:
        query += " AND metric_category = :category"
        params['category'] = category
    
    query += " ORDER BY metric_category, metric_name"
    
    result = db.execute(text(query), params)
    kpis = [dict(row._mapping) for row in result]
    
    return {
        "date": date.today().isoformat(),
        "total": len(kpis),
        "data": kpis
    }

@router.get("/kpis/categories")
async def get_kpi_categories(db: Session = Depends(get_db)):
    """Get KPIs grouped by category"""
    
    query = text("""
        SELECT 
            metric_category,
            COUNT(*) as metric_count,
            AVG(metric_value) as avg_value
        FROM kpi_metrics
        WHERE measurement_date = CURRENT_DATE
        GROUP BY metric_category
        ORDER BY metric_category
    """)
    
    result = db.execute(query)
    categories = [dict(row._mapping) for row in result]
    
    return {
        "date": date.today().isoformat(),
        "categories": categories
    }

@router.get("/kpis/business")
async def get_business_kpis(db: Session = Depends(get_db)):
    """Get business KPIs"""
    
    query = text("""
        SELECT 
            metric_name,
            metric_value,
            target_value,
            status
        FROM kpi_metrics
        WHERE measurement_date = CURRENT_DATE
        AND metric_category = 'Business'
        ORDER BY metric_name
    """)
    
    result = db.execute(query)
    kpis = [dict(row._mapping) for row in result]
    
    return {
        "category": "Business",
        "count": len(kpis),
        "kpis": kpis
    }

@router.get("/kpis/operational")
async def get_operational_kpis(db: Session = Depends(get_db)):
    """Get operational KPIs"""
    
    query = text("""
        SELECT 
            metric_name,
            metric_value,
            target_value,
            status
        FROM kpi_metrics
        WHERE measurement_date = CURRENT_DATE
        AND metric_category = 'Operational'
        ORDER BY metric_name
    """)
    
    result = db.execute(query)
    kpis = [dict(row._mapping) for row in result]
    
    return {
        "category": "Operational",
        "count": len(kpis),
        "kpis": kpis
    }

@router.get("/kpis/technical")
async def get_technical_kpis(db: Session = Depends(get_db)):
    """Get technical KPIs"""
    
    query = text("""
        SELECT 
            metric_name,
            metric_value,
            target_value,
            status
        FROM kpi_metrics
        WHERE measurement_date = CURRENT_DATE
        AND metric_category = 'Technical'
        ORDER BY metric_name
    """)
    
    result = db.execute(query)
    kpis = [dict(row._mapping) for row in result]
    
    return {
        "category": "Technical",
        "count": len(kpis),
        "kpis": kpis
    }

@router.get("/kpis/model")
async def get_model_kpis(db: Session = Depends(get_db)):
    """Get model performance KPIs"""
    
    query = text("""
        SELECT 
            metric_name,
            metric_value,
            target_value,
            status
        FROM kpi_metrics
        WHERE measurement_date = CURRENT_DATE
        AND metric_category = 'Model'
        ORDER BY metric_name
    """)
    
    result = db.execute(query)
    kpis = [dict(row._mapping) for row in result]
    
    return {
        "category": "Model",
        "count": len(kpis),
        "kpis": kpis
    }

@router.get("/kpis/dashboard")
async def get_dashboard_kpis(db: Session = Depends(get_db)):
    """Get key KPIs for dashboard"""
    
    query = text("""
        SELECT 
            metric_name,
            metric_category,
            metric_value,
            target_value,
            status
        FROM kpi_metrics
        WHERE measurement_date = CURRENT_DATE
        AND metric_name IN (
            'Cost Reduction %',
            'ROI %',
            'System Uptime %',
            'MTBF Hours',
            'MTTR Hours',
            'Preventive Maintenance Ratio %',
            'XGBoost Accuracy',
            'Failure Prevention Rate %'
        )
        ORDER BY metric_category, metric_name
    """)
    
    result = db.execute(query)
    kpis = [dict(row._mapping) for row in result]
    
    return {
        "date": date.today().isoformat(),
        "key_kpis": kpis
    }

@router.get("/kpis/summary")
async def get_kpis_summary(db: Session = Depends(get_db)):
    """Get KPIs summary statistics"""
    
    query = text("""
        SELECT 
            COUNT(*) as total_kpis,
            COUNT(CASE WHEN status = 'Excellent' THEN 1 END) as excellent_count,
            COUNT(CASE WHEN status = 'Good' THEN 1 END) as good_count,
            COUNT(CASE WHEN status = 'Warning' THEN 1 END) as warning_count,
            COUNT(CASE WHEN status = 'Critical' THEN 1 END) as critical_count
        FROM kpi_metrics
        WHERE measurement_date = CURRENT_DATE
    """)
    
    result = db.execute(query)
    summary = dict(result.fetchone()._mapping)
    
    return summary
