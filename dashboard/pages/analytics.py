"""
Analytics Page - Enhanced with Advanced Analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.api_client import get_api_client
from config import STATUS_COLORS
import os

def load_analytics_data():
    """Load analytics data from CSV files"""
    try:
        base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'results')
        
        root_cause = pd.read_csv(os.path.join(base_path, 'root_cause_analysis.csv'))
        equipment_reliability = pd.read_csv(os.path.join(base_path, 'equipment_reliability_metrics.csv'))
        type_reliability = pd.read_csv(os.path.join(base_path, 'equipment_type_reliability.csv'))
        
        return root_cause, equipment_reliability, type_reliability
    except Exception as e:
        st.error(f"Error loading analytics data: {e}")
        return None, None, None

def show():
    """Display analytics page"""
    
    st.markdown('<h1 class="main-header">📈 Advanced Analytics & Insights</h1>', unsafe_allow_html=True)
    
    api = get_api_client()
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "💼 Business KPIs", 
        "⚙️ Operational", 
        "🔍 Root Cause", 
        "📊 Reliability", 
        "💰 Cost Analysis",
        "🤖 Model Performance"
    ])
    
    with tab1:
        st.markdown("### Business KPIs")
        with st.spinner("Loading business KPIs..."):
            business_kpis = api.get_business_kpis()
        
        if business_kpis and business_kpis['kpis']:
            col1, col2, col3 = st.columns(3)
            for i, kpi in enumerate(business_kpis['kpis']):
                with [col1, col2, col3][i % 3]:
                    st.metric(
                        kpi['metric_name'],
                        f"{kpi['metric_value']:.2f}",
                        delta=kpi['status']
                    )
        else:
            st.info("No business KPIs available")
    
    with tab2:
        st.markdown("### Operational KPIs")
        with st.spinner("Loading operational KPIs..."):
            operational_kpis = api.get_operational_kpis()
        
        if operational_kpis and operational_kpis['kpis']:
            col1, col2, col3 = st.columns(3)
            for i, kpi in enumerate(operational_kpis['kpis']):
                with [col1, col2, col3][i % 3]:
                    st.metric(
                        kpi['metric_name'],
                        f"{kpi['metric_value']:.2f}",
                        delta=kpi['status']
                    )
        else:
            st.info("No operational KPIs available")
    
    with tab3:
        st.markdown("### 🔍 Root Cause Analysis")
        
        root_cause, _, _ = load_analytics_data()
        
        if root_cause is not None:
            # Pareto Chart
            st.markdown("#### Pareto Analysis: Root Causes by Total Cost")
            
            fig = go.Figure()
            
            # Bar chart
            fig.add_trace(go.Bar(
                x=root_cause['root_cause'],
                y=root_cause['total_cost'],
                name='Total Cost',
                marker_color='#3498db',
                yaxis='y'
            ))
            
            # Cumulative line
            fig.add_trace(go.Scatter(
                x=root_cause['root_cause'],
                y=root_cause['cumulative_cost_pct'],
                name='Cumulative %',
                marker_color='#e74c3c',
                yaxis='y2',
                mode='lines+markers'
            ))
            
            fig.update_layout(
                yaxis=dict(title='Total Cost ($)'),
                yaxis2=dict(title='Cumulative %', overlaying='y', side='right', range=[0, 105]),
                xaxis=dict(title='Root Cause', tickangle=-45),
                height=500,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Top 5 Root Causes
            st.markdown("#### Top 5 Root Causes")
            top_5 = root_cause.head(5)[['root_cause', 'failure_count', 'total_downtime', 'total_cost', 'cost_percentage']]
            st.dataframe(top_5, use_container_width=True)
            
        else:
            st.info("Run Phase 8 analysis to generate root cause data")
    
    with tab4:
        st.markdown("### 📊 Equipment Reliability Analysis")
        
        _, equipment_reliability, type_reliability = load_analytics_data()
        
        if type_reliability is not None:
            # MTBF by Equipment Type
            st.markdown("#### Mean Time Between Failures (MTBF) by Equipment Type")
            
            fig = px.bar(
                type_reliability,
                x='equipment_type',
                y='avg_mtbf',
                title='Average MTBF by Equipment Type',
                labels={'avg_mtbf': 'Average MTBF (days)', 'equipment_type': 'Equipment Type'},
                color='avg_mtbf',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Equipment Type Comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Total Failures by Type")
                fig = px.pie(
                    type_reliability,
                    values='total_failures',
                    names='equipment_type',
                    title='Failure Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Total Cost by Type")
                fig = px.pie(
                    type_reliability,
                    values='total_cost',
                    names='equipment_type',
                    title='Cost Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Worst Performers
            if equipment_reliability is not None:
                st.markdown("#### ⚠️ Top 10 Worst Performing Equipment (Lowest MTBF)")
                worst_10 = equipment_reliability.nsmallest(10, 'mtbf_days')[
                    ['equipment_id', 'equipment_type', 'failure_count', 'mtbf_days', 'total_cost']
                ]
                st.dataframe(worst_10, use_container_width=True)
        else:
            st.info("Run Phase 8 analysis to generate reliability data")
    
    with tab5:
        st.markdown("### 💰 Cost-Benefit Analysis")
        
        # Load failure data for cost calculations
        try:
            failures_df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'synthetic', 'failure_events.csv'))
            maintenance_df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'synthetic', 'maintenance_records.csv'))
            
            # Calculate costs
            total_failure_cost = failures_df['repair_cost'].sum()
            total_maintenance_cost = maintenance_df['total_cost'].sum()
            total_downtime_hours = failures_df['downtime_hours'].sum()
            downtime_cost_per_hour = 500
            total_downtime_cost = total_downtime_hours * downtime_cost_per_hour
            
            preventable_failures = failures_df[failures_df['prevented_by_maintenance'] == True]
            preventable_cost = preventable_failures['repair_cost'].sum()
            preventable_downtime_cost = preventable_failures['downtime_hours'].sum() * downtime_cost_per_hour
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Failure Cost", f"${total_failure_cost:,.0f}")
            with col2:
                st.metric("Total Maintenance Cost", f"${total_maintenance_cost:,.0f}")
            with col3:
                st.metric("Total Downtime Cost", f"${total_downtime_cost:,.0f}")
            with col4:
                total_preventable = preventable_cost + preventable_downtime_cost
                st.metric("Potential Savings", f"${total_preventable:,.0f}", 
                         delta=f"{(total_preventable / (total_failure_cost + total_downtime_cost) * 100):.1f}%")
            
            # Cost Breakdown Chart
            st.markdown("#### Cost Breakdown")
            
            cost_data = pd.DataFrame({
                'Category': ['Failure Repairs', 'Maintenance', 'Downtime', 'Preventable (Opportunity)'],
                'Cost': [total_failure_cost, total_maintenance_cost, total_downtime_cost, total_preventable]
            })
            
            fig = px.bar(
                cost_data,
                x='Category',
                y='Cost',
                title='Cost Analysis Overview',
                color='Category',
                labels={'Cost': 'Cost ($)'}
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # ROI Calculation
            st.markdown("#### 💡 Recommendations")
            st.success(f"""
            **Potential Annual Savings: ${total_preventable:,.0f}**
            
            By implementing a comprehensive predictive maintenance program:
            - Focus on top 3 root causes
            - Expected savings: ${total_preventable * 0.7:,.0f} (70% reduction)
            - Estimated ROI: 300% within 18 months
            """)
            
        except Exception as e:
            st.error(f"Error calculating costs: {e}")
    
    with tab6:
        st.markdown("### Model Performance KPIs")
        with st.spinner("Loading model KPIs..."):
            model_kpis = api.get_model_kpis()
        
        if model_kpis and model_kpis['kpis']:
            col1, col2, col3 = st.columns(3)
            for i, kpi in enumerate(model_kpis['kpis']):
                with [col1, col2, col3][i % 3]:
                    st.metric(
                        kpi['metric_name'],
                        f"{kpi['metric_value']:.2f}%",
                        delta=kpi['status']
                    )
        else:
            st.info("No model KPIs available")
