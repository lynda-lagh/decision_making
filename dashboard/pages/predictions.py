"""
Predictions Page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.api_client import get_api_client
from config import PRIORITY_COLORS

def show():
    """Display predictions page"""
    
    st.markdown('<h1 class="main-header">📊 Predictions & Risk Analysis</h1>', unsafe_allow_html=True)
    
    api = get_api_client()
    
    # Fetch predictions
    with st.spinner("Loading predictions..."):
        predictions_data = api.get_latest_predictions()
    
    if predictions_data and predictions_data.get('data'):
        df = pd.DataFrame(predictions_data['data'])
        
        # Convert risk_score to float
        df['risk_score'] = pd.to_numeric(df['risk_score'], errors='coerce')
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Predictions", len(df))
        
        with col2:
            avg_risk = df['risk_score'].mean()
            st.metric("Average Risk", f"{avg_risk:.1f}%")
        
        with col3:
            high_risk = (df['risk_score'] > 40).sum()
            st.metric("High Risk (>40%)", high_risk)
        
        with col4:
            critical = (df['risk_score'] > 70).sum()
            st.metric("Critical (>70%)", critical)
        
        st.markdown(f"**Prediction Date**: {predictions_data.get('date', 'N/A')}")
        st.markdown("---")
        
        # Risk distribution chart
        st.markdown("### 📊 Risk Score Distribution")
        
        if df['risk_score'].notna().any():
            # Create histogram with explicit settings
            fig = px.histogram(
                df,
                x='risk_score',
                nbins=20,
                title='Risk Score Distribution',
                color_discrete_sequence=['#1f77b4']
            )
            
            # Update layout for better visibility
            fig.update_layout(
                xaxis_title="Risk Score (%)",
                yaxis_title="Count",
                showlegend=False,
                height=400,
                bargap=0.1
            )
            
            # Update traces
            fig.update_traces(
                marker_line_width=1,
                marker_line_color='white'
            )
            
            st.plotly_chart(fig, theme="streamlit", use_container_width=True, key="risk_histogram")
        else:
            st.warning("⚠️ No valid risk scores to display")
        
        st.markdown("---")
        
        # Priority breakdown by equipment type
        st.markdown("### 🎯 Priority by Equipment Type")
        
        if 'priority_level' in df.columns and 'equipment_type' in df.columns:
            priority_by_type = df.groupby(['equipment_type', 'priority_level']).size().reset_index(name='count')
            
            fig2 = px.bar(
                priority_by_type,
                x='equipment_type',
                y='count',
                color='priority_level',
                title='Equipment Priority Distribution by Type',
                color_discrete_map=PRIORITY_COLORS,
                barmode='stack'
            )
            
            fig2.update_layout(
                xaxis_title="Equipment Type",
                yaxis_title="Count",
                height=400,
                legend_title="Priority Level"
            )
            
            st.plotly_chart(fig2, theme="streamlit", use_container_width=True, key="priority_by_type")
        
        st.markdown("---")
        
        # Predictions table
        st.markdown("### Predictions Table")
        st.dataframe(
            df[['equipment_id', 'equipment_type', 'risk_score', 'priority_level', 'recommended_action']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No predictions available")
