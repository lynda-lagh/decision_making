"""
WeeFarm Predictive Maintenance Dashboard
Main Streamlit Application
"""

import streamlit as st
from config import PAGE_TITLE, PAGE_ICON, LAYOUT

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .priority-critical {
        color: #d62728;
        font-weight: bold;
    }
    .priority-high {
        color: #ff7f0e;
        font-weight: bold;
    }
    .priority-medium {
        color: #ff9800;
        font-weight: bold;
    }
    .priority-low {
        color: #2ca02c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🚜 WeeFarm")
st.sidebar.markdown("### Predictive Maintenance System")

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Overview", "🔧 Equipment", "📊 Predictions", "📅 Schedule", "📈 Analytics", "🔮 Forecasting", "⚙️ Settings"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**System Status**")
st.sidebar.success("✅ API Connected")
st.sidebar.info("✅ Database Online")
st.sidebar.markdown("---")
st.sidebar.markdown("**Version**: 1.0.0")
st.sidebar.markdown("**Phase**: 6 - Application Development")

# Main content area
if page == "🏠 Overview":
    from pages import overview
    overview.show()

elif page == "🔧 Equipment":
    from pages import equipment
    equipment.show()

elif page == "📊 Predictions":
    from pages import predictions
    predictions.show()

elif page == "📅 Schedule":
    from pages import schedule
    schedule.show()

elif page == "📈 Analytics":
    from pages import analytics
    analytics.show()

elif page == "🔮 Forecasting":
    from pages import forecasting
    forecasting.show()

elif page == "⚙️ Settings":
    from pages import settings
    settings.show()
