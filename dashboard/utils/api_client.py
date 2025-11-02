"""
API Client for FastAPI Backend
"""

import requests
import streamlit as st
from typing import Optional, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import API_BASE_URL

class APIClient:
    """Client for interacting with FastAPI backend"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make GET request"""
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {str(e)}")
            return None
    
    def _post(self, endpoint: str, data: Dict) -> Optional[Dict]:
        """Make POST request"""
        try:
            response = requests.post(f"{self.base_url}{endpoint}", json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {str(e)}")
            return None
    
    def _put(self, endpoint: str, data: Dict) -> Optional[Dict]:
        """Make PUT request"""
        try:
            response = requests.put(f"{self.base_url}{endpoint}", json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {str(e)}")
            return None
    
    def _delete(self, endpoint: str) -> Optional[Dict]:
        """Make DELETE request"""
        try:
            response = requests.delete(f"{self.base_url}{endpoint}", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {str(e)}")
            return None
    
    # Equipment endpoints
    def get_equipment(self, equipment_type: Optional[str] = None, location: Optional[str] = None):
        """Get all equipment"""
        params = {}
        if equipment_type:
            params['equipment_type'] = equipment_type
        if location:
            params['location'] = location
        return self._get("/equipment", params)
    
    def get_equipment_by_id(self, equipment_id: str):
        """Get specific equipment"""
        return self._get(f"/equipment/{equipment_id}")
    
    def get_equipment_summary(self):
        """Get equipment summary statistics"""
        return self._get("/equipment/stats/summary")
    
    def get_equipment_by_type(self, equipment_type: str):
        """Get equipment by type"""
        return self._get(f"/equipment/by-type/{equipment_type}")
    
    def get_equipment_by_location(self, location: str):
        """Get equipment by location"""
        return self._get(f"/equipment/by-location/{location}")
    
    # Predictions endpoints
    def get_predictions(self, priority_level: Optional[str] = None, min_risk_score: Optional[float] = None):
        """Get all predictions"""
        params = {}
        if priority_level:
            params['priority_level'] = priority_level
        if min_risk_score:
            params['min_risk_score'] = min_risk_score
        return self._get("/predictions", params)
    
    def get_latest_predictions(self):
        """Get latest predictions"""
        return self._get("/predictions/latest")
    
    def get_predictions_summary(self):
        """Get predictions summary"""
        return self._get("/predictions/stats/summary")
    
    def get_high_risk_equipment(self, threshold: float = 40.0):
        """Get high-risk equipment"""
        return self._get("/predictions/high-risk", {"threshold": threshold})
    
    # Schedule endpoints
    def get_schedule(self, status: Optional[str] = None):
        """Get maintenance schedule"""
        params = {}
        if status:
            params['status'] = status
        return self._get("/schedule", params)
    
    def get_upcoming_maintenance(self, days: int = 7):
        """Get upcoming maintenance"""
        return self._get("/schedule/upcoming", {"days": days})
    
    def get_overdue_maintenance(self):
        """Get overdue maintenance"""
        return self._get("/schedule/overdue")
    
    def get_schedule_summary(self):
        """Get schedule summary"""
        return self._get("/schedule/stats/summary")
    
    def update_schedule(self, schedule_id: int, data: Dict):
        """Update schedule task"""
        return self._put(f"/schedule/{schedule_id}", data)
    
    def complete_schedule(self, schedule_id: int):
        """Mark schedule as completed"""
        return self._put(f"/schedule/{schedule_id}/complete", {})
    
    # KPIs endpoints
    def get_kpis(self, category: Optional[str] = None):
        """Get all KPIs"""
        params = {}
        if category:
            params['category'] = category
        return self._get("/kpis", params)
    
    def get_dashboard_kpis(self):
        """Get key KPIs for dashboard"""
        return self._get("/kpis/dashboard")
    
    def get_kpis_summary(self):
        """Get KPIs summary"""
        return self._get("/kpis/summary")
    
    def get_business_kpis(self):
        """Get business KPIs"""
        return self._get("/kpis/business")
    
    def get_operational_kpis(self):
        """Get operational KPIs"""
        return self._get("/kpis/operational")
    
    def get_technical_kpis(self):
        """Get technical KPIs"""
        return self._get("/kpis/technical")
    
    def get_model_kpis(self):
        """Get model KPIs"""
        return self._get("/kpis/model")
    
    # Analytics Endpoints
    def get_root_cause_analysis(self, limit: Optional[int] = None):
        """Get root cause analysis"""
        params = {"limit": limit} if limit else None
        return self._get("/analytics/root-cause", params=params)
    
    def get_equipment_reliability(self, equipment_type: Optional[str] = None):
        """Get equipment reliability metrics"""
        params = {"equipment_type": equipment_type} if equipment_type else None
        return self._get("/analytics/equipment-reliability", params=params)
    
    def get_type_reliability(self):
        """Get reliability by equipment type"""
        return self._get("/analytics/type-reliability")
    
    def get_maintenance_effectiveness(self):
        """Get maintenance effectiveness analysis"""
        return self._get("/analytics/maintenance-effectiveness")
    
    def get_cost_benefit_analysis(self):
        """Get cost-benefit analysis"""
        return self._get("/analytics/cost-benefit")
    
    def get_worst_performers(self, limit: int = 10):
        """Get worst performing equipment"""
        return self._get("/analytics/worst-performers", params={"limit": limit})
    
    def get_failure_trends(self, days: int = 30):
        """Get failure trends"""
        return self._get("/analytics/trends", params={"days": days})
    
    def get_analytics_summary(self):
        """Get analytics summary"""
        return self._get("/analytics/summary")
    
    def refresh_analytics(self):
        """Trigger analytics refresh"""
        return self._post("/analytics/refresh", {})

# Create global API client instance
@st.cache_resource
def get_api_client():
    """Get cached API client instance"""
    return APIClient()
