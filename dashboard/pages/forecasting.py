"""
Time Series Forecasting Page
Displays failure forecasts and trends
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from utils.api_client import get_api_client
import os

def load_forecast_data():
    """Load time series forecast data"""
    try:
        base_path = os.path.join(os.path.dirname(__file__), '..', '..')
        
        # Load failure events for historical data
        failures_df = pd.read_csv(os.path.join(base_path, 'data', 'synthetic', 'failure_events.csv'))
        failures_df['failure_date'] = pd.to_datetime(failures_df['failure_date'])
        
        return failures_df
    except Exception as e:
        st.error(f"Error loading forecast data: {e}")
        return None

def create_daily_failures_forecast(failures_df, forecast_days=30):
    """Create daily failure forecast"""
    
    # Aggregate to daily level
    daily_failures = failures_df.groupby(failures_df['failure_date'].dt.date).size().reset_index()
    daily_failures.columns = ['date', 'failure_count']
    daily_failures['date'] = pd.to_datetime(daily_failures['date'])
    daily_failures = daily_failures.sort_values('date')
    
    # Simple moving average forecast
    window = 7
    daily_failures['ma_7'] = daily_failures['failure_count'].rolling(window=window).mean()
    
    # Generate forecast dates
    last_date = daily_failures['date'].max()
    forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_days, freq='D')
    
    # Simple forecast using last MA value with some variation
    last_ma = daily_failures['ma_7'].iloc[-1]
    forecast_values = np.random.poisson(lam=last_ma, size=forecast_days)
    
    forecast_df = pd.DataFrame({
        'date': forecast_dates,
        'forecast': forecast_values,
        'lower_bound': forecast_values * 0.7,
        'upper_bound': forecast_values * 1.3
    })
    
    return daily_failures, forecast_df

def show():
    """Display time series forecasting page"""
    
    st.markdown('<h1 class="main-header">📈 Time Series Forecasting</h1>', unsafe_allow_html=True)
    
    # Load data
    failures_df = load_forecast_data()
    
    if failures_df is None:
        st.warning("No forecast data available. Run the pipeline to generate forecasts.")
        return
    
    # Tabs for different forecasts
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Daily Failures Forecast",
        "📉 Trend Analysis", 
        "🔮 Equipment-Level Forecast",
        "📋 Forecast Summary"
    ])
    
    with tab1:
        st.markdown("### 📊 Daily Failure Forecast (Next 30 Days)")
        
        # Forecast controls
        col1, col2 = st.columns([3, 1])
        with col2:
            forecast_days = st.slider("Forecast Days", 7, 90, 30)
        
        # Generate forecast
        daily_failures, forecast_df = create_daily_failures_forecast(failures_df, forecast_days)
        
        # Plot
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=daily_failures['date'],
            y=daily_failures['failure_count'],
            mode='lines+markers',
            name='Historical Failures',
            line=dict(color='#3498db', width=2),
            marker=dict(size=4)
        ))
        
        # 7-day moving average
        fig.add_trace(go.Scatter(
            x=daily_failures['date'],
            y=daily_failures['ma_7'],
            mode='lines',
            name='7-Day Moving Average',
            line=dict(color='#e74c3c', width=2, dash='dash')
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=forecast_df['date'],
            y=forecast_df['forecast'],
            mode='lines+markers',
            name='Forecast',
            line=dict(color='#2ecc71', width=2),
            marker=dict(size=6)
        ))
        
        # Confidence interval
        fig.add_trace(go.Scatter(
            x=forecast_df['date'].tolist() + forecast_df['date'].tolist()[::-1],
            y=forecast_df['upper_bound'].tolist() + forecast_df['lower_bound'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(46, 204, 113, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Confidence Interval',
            showlegend=True
        ))
        
        fig.update_layout(
            title='Daily Failure Forecast',
            xaxis_title='Date',
            yaxis_title='Number of Failures',
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Forecast metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Avg Daily Failures (Historical)", f"{daily_failures['failure_count'].mean():.1f}")
        with col2:
            st.metric("Forecasted Avg (Next 30d)", f"{forecast_df['forecast'].mean():.1f}")
        with col3:
            total_forecast = forecast_df['forecast'].sum()
            st.metric("Total Forecasted Failures", f"{total_forecast:.0f}")
        with col4:
            trend = "↑" if forecast_df['forecast'].mean() > daily_failures['failure_count'].mean() else "↓"
            st.metric("Trend", trend)
    
    with tab2:
        st.markdown("### 📉 Failure Trend Analysis")
        
        # Monthly trends
        monthly_failures = failures_df.groupby(failures_df['failure_date'].dt.to_period('M')).agg({
            'failure_id': 'count',
            'repair_cost': 'sum',
            'downtime_hours': 'sum'
        }).reset_index()
        monthly_failures.columns = ['month', 'failure_count', 'total_cost', 'total_downtime']
        monthly_failures['month'] = monthly_failures['month'].astype(str)
        
        # Plot monthly trends
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=monthly_failures['month'],
            y=monthly_failures['failure_count'],
            name='Failure Count',
            marker_color='#3498db'
        ))
        
        fig.update_layout(
            title='Monthly Failure Trends',
            xaxis_title='Month',
            yaxis_title='Number of Failures',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Cost and downtime trends
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(
                monthly_failures,
                x='month',
                y='total_cost',
                title='Monthly Repair Costs',
                markers=True
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.line(
                monthly_failures,
                x='month',
                y='total_downtime',
                title='Monthly Downtime Hours',
                markers=True,
                color_discrete_sequence=['#e74c3c']
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### 🔮 Equipment-Level Forecast")
        
        # Top 10 equipment by failure count
        equipment_failures = failures_df.groupby('equipment_id').agg({
            'failure_id': 'count',
            'repair_cost': 'sum'
        }).reset_index()
        equipment_failures.columns = ['equipment_id', 'failure_count', 'total_cost']
        equipment_failures = equipment_failures.sort_values('failure_count', ascending=False).head(10)
        
        # Calculate failure rate and forecast
        equipment_failures['failure_rate_per_month'] = equipment_failures['failure_count'] / 12  # Assuming 1 year of data
        equipment_failures['forecasted_failures_30d'] = (equipment_failures['failure_rate_per_month'] / 30 * 30).round()
        
        st.markdown("#### Top 10 Equipment - Failure Forecast (Next 30 Days)")
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=equipment_failures['equipment_id'],
            y=equipment_failures['failure_count'],
            name='Historical Failures',
            marker_color='#3498db'
        ))
        
        fig.add_trace(go.Bar(
            x=equipment_failures['equipment_id'],
            y=equipment_failures['forecasted_failures_30d'],
            name='Forecasted (30d)',
            marker_color='#2ecc71'
        ))
        
        fig.update_layout(
            title='Equipment Failure Forecast',
            xaxis_title='Equipment ID',
            yaxis_title='Number of Failures',
            height=400,
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Equipment forecast table
        st.markdown("#### Detailed Forecast")
        display_df = equipment_failures[['equipment_id', 'failure_count', 'failure_rate_per_month', 'forecasted_failures_30d', 'total_cost']]
        display_df.columns = ['Equipment ID', 'Historical Failures', 'Rate/Month', 'Forecast (30d)', 'Total Cost']
        st.dataframe(display_df, use_container_width=True)
    
    with tab4:
        st.markdown("### 📋 Forecast Summary & Insights")
        
        # Overall statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📊 Historical Stats")
            total_failures = len(failures_df)
            avg_daily = daily_failures['failure_count'].mean()
            st.metric("Total Failures", f"{total_failures:,}")
            st.metric("Avg Daily Failures", f"{avg_daily:.1f}")
        
        with col2:
            st.markdown("#### 🔮 Forecast (30d)")
            forecast_total = forecast_df['forecast'].sum()
            forecast_avg = forecast_df['forecast'].mean()
            st.metric("Forecasted Failures", f"{forecast_total:.0f}")
            st.metric("Forecasted Daily Avg", f"{forecast_avg:.1f}")
        
        with col3:
            st.markdown("#### 💰 Cost Impact")
            avg_cost = failures_df['repair_cost'].mean()
            forecasted_cost = forecast_total * avg_cost
            st.metric("Avg Repair Cost", f"${avg_cost:,.0f}")
            st.metric("Forecasted Cost (30d)", f"${forecasted_cost:,.0f}")
        
        # Insights
        st.markdown("---")
        st.markdown("### 💡 Key Insights")
        
        # Calculate trend
        recent_avg = daily_failures.tail(30)['failure_count'].mean()
        older_avg = daily_failures.head(30)['failure_count'].mean()
        trend_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        
        if trend_pct > 10:
            st.warning(f"""
            **⚠️ Increasing Failure Trend Detected**
            - Failures have increased by {trend_pct:.1f}% compared to earlier periods
            - Recommend: Increase preventive maintenance frequency
            - Focus on top 10 failing equipment
            """)
        elif trend_pct < -10:
            st.success(f"""
            **✅ Decreasing Failure Trend**
            - Failures have decreased by {abs(trend_pct):.1f}%
            - Current maintenance strategy is effective
            - Continue monitoring high-risk equipment
            """)
        else:
            st.info(f"""
            **📊 Stable Failure Rate**
            - Failure rate is relatively stable (±{abs(trend_pct):.1f}%)
            - Maintain current maintenance schedule
            - Monitor for seasonal patterns
            """)
        
        # Recommendations
        st.markdown("### 🎯 Recommendations")
        st.markdown(f"""
        1. **Preventive Maintenance**: Schedule maintenance for {int(forecast_total * 0.7)} equipment in next 30 days
        2. **Resource Planning**: Allocate budget of ${forecasted_cost:,.0f} for repairs
        3. **Critical Equipment**: Focus on top 10 equipment accounting for {equipment_failures['failure_count'].sum() / total_failures * 100:.1f}% of failures
        4. **Trend Monitoring**: Review forecast accuracy weekly and adjust predictions
        """)

if __name__ == "__main__":
    show()
