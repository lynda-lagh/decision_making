"""
Overview Page - Dashboard Home
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.api_client import get_api_client
from config import PRIORITY_COLORS

def show():
    """Display overview page"""
    
    st.markdown('<h1 class="main-header">🏠 System Overview</h1>', unsafe_allow_html=True)
    
    # Get API client
    api = get_api_client()
    
    # Fetch data
    with st.spinner("Loading dashboard data..."):
        predictions_summary = api.get_predictions_summary()
        schedule_summary = api.get_schedule_summary()
        equipment_summary = api.get_equipment_summary()
        kpis_summary = api.get_kpis_summary()
        high_risk = api.get_high_risk_equipment(threshold=40.0)
        upcoming = api.get_upcoming_maintenance(days=7)
    
    # Key Metrics Row
    st.markdown("### 📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if equipment_summary:
            total_equipment = equipment_summary['summary']['total_equipment']
            st.metric("Total Equipment", f"{total_equipment}")
        else:
            st.metric("Total Equipment", "N/A")
    
    with col2:
        if high_risk:
            high_risk_count = high_risk['count']
            st.metric("High Risk Equipment", f"{high_risk_count}", delta=f"{high_risk_count}% of total", delta_color="inverse")
        else:
            st.metric("High Risk Equipment", "N/A")
    
    with col3:
        if upcoming:
            upcoming_count = upcoming['count']
            st.metric("Upcoming Tasks (7 days)", f"{upcoming_count}")
        else:
            st.metric("Upcoming Tasks", "N/A")
    
    with col4:
        if predictions_summary:
            avg_risk = predictions_summary.get('avg_risk_score', 0)
            st.metric("Average Risk Score", f"{avg_risk:.1f}%")
        else:
            st.metric("Average Risk Score", "N/A")
    
    st.markdown("---")
    
    # Priority Distribution and Schedule Status
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Priority Distribution")
        if predictions_summary:
            # Extract counts safely and convert to int
            critical_count = int(predictions_summary.get('critical_count', 0) or 0)
            high_count = int(predictions_summary.get('high_count', 0) or 0)
            medium_count = int(predictions_summary.get('medium_count', 0) or 0)
            low_count = int(predictions_summary.get('low_count', 0) or 0)
            
            # Check if we have any data
            total_count = critical_count + high_count + medium_count + low_count
            
            if total_count > 0:
                # Create DataFrame explicitly
                import pandas as pd
                priority_df = pd.DataFrame({
                    'Priority': ['Critical', 'High', 'Medium', 'Low'],
                    'Count': [critical_count, high_count, medium_count, low_count]
                })
                
                fig = px.bar(
                    priority_df,
                    x='Priority',
                    y='Count',
                    color='Priority',
                    color_discrete_map=PRIORITY_COLORS,
                    title=f"Total Equipment: {total_count}"
                )
                fig.update_layout(
                    showlegend=False, 
                    height=400,
                    xaxis_title="Priority Level",
                    yaxis_title="Number of Equipment",
                    yaxis=dict(range=[0, max(critical_count, high_count, medium_count, low_count) * 1.2])
                )
                fig.update_traces(
                    text=priority_df['Count'],
                    textposition='outside', 
                    textfont_size=14
                )
                st.plotly_chart(fig, use_container_width=True, key="priority_chart")
                
                # Show summary below chart
                st.caption(f"🔴 Critical: {critical_count} | 🟠 High: {high_count} | 🟡 Medium: {medium_count} | 🟢 Low: {low_count}")
            else:
                st.warning("⚠️ No priority data available. Run the pipeline first!")
                if st.button("📊 View Raw Data", key="debug_priority"):
                    st.json(predictions_summary)
        else:
            st.error("❌ Could not fetch prediction data from API")
            st.info("💡 Make sure the backend is running and the pipeline has been executed.")
    
    with col2:
        st.markdown("### 📅 Schedule Status")
        if schedule_summary:
            # Extract counts and convert to int
            scheduled_count = int(schedule_summary.get('scheduled_count', 0) or 0)
            critical_count = int(schedule_summary.get('critical_count', 0) or 0)
            high_count = int(schedule_summary.get('high_count', 0) or 0)
            
            total_schedule = scheduled_count + critical_count + high_count
            
            if total_schedule > 0:
                schedule_data = {
                    'Status': ['Scheduled', 'Critical', 'High'],
                    'Count': [scheduled_count, critical_count, high_count]
                }
                
                fig = px.pie(
                    schedule_data,
                    values='Count',
                    names='Status',
                    color='Status',
                    color_discrete_map={
                        'Scheduled': '#2196F3',
                        'Critical': '#d62728',
                        'High': '#ff7f0e'
                    },
                    title=f"Total Tasks: {total_schedule}",
                    hole=0.4  # Donut chart
                )
                fig.update_traces(textposition='inside', textinfo='percent+label+value')
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show summary
                st.caption(f"📋 Scheduled: {scheduled_count} | 🔴 Critical: {critical_count} | 🟠 High: {high_count}")
            else:
                st.warning("⚠️ No scheduled tasks. Generate schedule by running the pipeline!")
                if st.button("📊 View Raw Data", key="debug_schedule"):
                    st.json(schedule_summary)
        else:
            st.error("❌ Could not fetch schedule data from API")
            st.info("💡 Make sure the backend is running and the pipeline has been executed.")
    
    st.markdown("---")
    
    # High Risk Equipment Alert
    st.markdown("### 🚨 High Risk Equipment (Risk > 40%)")
    if high_risk and high_risk.get('count', 0) > 0:
        equipment_list = high_risk.get('equipment', [])
        
        if equipment_list:
            # Create columns for better layout
            for i, eq in enumerate(equipment_list[:5]):  # Show top 5
                priority = eq.get('priority_level', 'Unknown')
                risk_score = eq.get('risk_score', 0)
                equipment_id = eq.get('equipment_id', 'N/A')
                equipment_type = eq.get('equipment_type', 'N/A')
                location = eq.get('location', 'N/A')
                action = eq.get('recommended_action', 'No action specified')
                
                # Create expandable section for each equipment
                with st.expander(f"{'🔴' if priority == 'Critical' else '🟠'} **{equipment_id}** - {equipment_type} | Risk: {risk_score:.1f}% | {priority}", expanded=(i==0)):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Risk Score", f"{risk_score:.1f}%")
                    with col2:
                        st.metric("Priority", priority)
                    with col3:
                        st.metric("Location", location)
                    
                    st.markdown(f"**Recommended Action:** {action}")
                    
                    # Progress bar for risk
                    if risk_score >= 70:
                        st.progress(risk_score/100, text=f"Critical Risk: {risk_score:.1f}%")
                    elif risk_score >= 40:
                        st.progress(risk_score/100, text=f"High Risk: {risk_score:.1f}%")
            
            if high_risk['count'] > 5:
                st.info(f"➕ **{high_risk['count'] - 5} more high-risk equipment** - View all in Predictions page")
        else:
            st.warning("⚠️ High-risk equipment data structure is unexpected")
    else:
        st.success("✅ No high-risk equipment detected! All systems operating normally.")
    
    st.markdown("---")
    
    # KPI Status
    st.markdown("### 📈 KPI Status")
    if kpis_summary:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            excellent = kpis_summary.get('excellent_count', 0)
            st.metric("Excellent", f"{excellent}", delta="🟢")
        
        with col2:
            good = kpis_summary.get('good_count', 0)
            st.metric("Good", f"{good}", delta="🟡")
        
        with col3:
            warning = kpis_summary.get('warning_count', 0)
            st.metric("Warning", f"{warning}", delta="🟠")
        
        with col4:
            critical = kpis_summary.get('critical_count', 0)
            st.metric("Critical", f"{critical}", delta="🔴")
    else:
        st.info("No KPI data available")
    
    # Refresh button
    st.markdown("---")
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.rerun()
