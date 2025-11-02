"""
Schedule Page
"""

import streamlit as st
import pandas as pd
from utils.api_client import get_api_client

def show():
    """Display schedule page"""
    
    st.markdown('<h1 class="main-header">📅 Maintenance Schedule</h1>', unsafe_allow_html=True)
    
    api = get_api_client()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 All Tasks", "⏰ Upcoming", "⚠️ Overdue"])
    
    with tab1:
        with st.spinner("Loading schedule..."):
            schedule_data = api.get_schedule()
        
        if schedule_data and schedule_data['data']:
            df = pd.DataFrame(schedule_data['data'])
            st.markdown(f"### Total Tasks: {len(df)}")
            st.dataframe(
                df[['equipment_id', 'equipment_type', 'scheduled_date', 'priority_level', 'status', 'assigned_technician']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No scheduled tasks")
    
    with tab2:
        with st.spinner("Loading upcoming tasks..."):
            upcoming_data = api.get_upcoming_maintenance(days=7)
        
        if upcoming_data and upcoming_data['count'] > 0:
            df = pd.DataFrame(upcoming_data['tasks'])
            st.markdown(f"### Upcoming Tasks (Next 7 Days): {upcoming_data['count']}")
            st.dataframe(
                df[['equipment_id', 'equipment_type', 'scheduled_date', 'priority_level', 'assigned_technician']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ No tasks scheduled for the next 7 days")
    
    with tab3:
        with st.spinner("Loading overdue tasks..."):
            overdue_data = api.get_overdue_maintenance()
        
        if overdue_data and overdue_data['count'] > 0:
            df = pd.DataFrame(overdue_data['tasks'])
            st.warning(f"### ⚠️ Overdue Tasks: {overdue_data['count']}")
            st.dataframe(
                df[['equipment_id', 'equipment_type', 'scheduled_date', 'priority_level', 'days_overdue']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ No overdue tasks!")
