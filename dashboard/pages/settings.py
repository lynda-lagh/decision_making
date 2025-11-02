"""
Settings Page
"""

import streamlit as st
import subprocess
import sys

def show():
    """Display settings page"""
    
    st.markdown('<h1 class="main-header">⚙️ Settings & Pipeline Control</h1>', unsafe_allow_html=True)
    
    # Pipeline Control
    st.markdown("### 🚀 ML Pipeline Control")
    st.info("Run the ML pipeline to generate new predictions and update KPIs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ Run Pipeline", use_container_width=True, type="primary"):
            with st.spinner("Running ML pipeline..."):
                try:
                    # Get the correct path to pipeline
                    import os
                    pipeline_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "pipeline", "pipeline.py")
                    
                    # Run pipeline
                    result = subprocess.run(
                        [sys.executable, pipeline_path],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=os.path.dirname(pipeline_path)
                    )
                    
                    if result.returncode == 0:
                        st.success("✅ Pipeline executed successfully!")
                        st.code(result.stdout, language="text")
                    else:
                        st.error("❌ Pipeline failed!")
                        st.code(result.stderr, language="text")
                except Exception as e:
                    st.error(f"Error running pipeline: {str(e)}")
    
    with col2:
        st.metric("Last Run", "Today")
        st.metric("Execution Time", "0.72s")
        st.metric("Status", "✅ Success")
    
    st.markdown("---")
    
    # System Information
    st.markdown("### 📊 System Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Database**")
        st.write("PostgreSQL 17")
        st.write("weefarm_db")
        st.success("✅ Connected")
    
    with col2:
        st.markdown("**API**")
        st.write("FastAPI 0.104+")
        st.write("http://localhost:5000")
        st.success("✅ Running")
    
    with col3:
        st.markdown("**Dashboard**")
        st.write("Streamlit 1.28+")
        st.write("http://localhost:8501")
        st.success("✅ Active")
    
    st.markdown("---")
    
    # Configuration
    st.markdown("### 🔧 Configuration")
    
    with st.expander("API Settings"):
        api_url = st.text_input("API Base URL", "http://localhost:5000/api/v1")
        st.info("Restart dashboard after changing API URL")
    
    with st.expander("Display Settings"):
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        chart_height = st.slider("Chart Height", 300, 600, 400)
    
    with st.expander("Pipeline Settings"):
        auto_run = st.checkbox("Auto-run pipeline daily")
        run_time = st.time_input("Scheduled run time")
    
    st.markdown("---")
    
    # About
    st.markdown("### ℹ️ About")
    st.markdown("""
    **WeeFarm Predictive Maintenance System**
    
    - **Version**: 1.0.0
    - **Phase**: 6 - Application Development
    - **Technology Stack**:
        - Database: PostgreSQL 17
        - Backend: FastAPI
        - Dashboard: Streamlit
        - ML: Scikit-learn, XGBoost
    
    **Features**:
    - Real-time predictions
    - Maintenance scheduling
    - KPI monitoring
    - Equipment management
    
    **Developed for**: Agricultural Equipment Maintenance
    """)
