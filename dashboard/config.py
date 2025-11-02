"""
Streamlit Dashboard Configuration
"""

import os

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000/api/v1")

# Page Configuration
PAGE_TITLE = "WeeFarm Predictive Maintenance"
PAGE_ICON = "🚜"
LAYOUT = "wide"

# Theme Colors
PRIMARY_COLOR = "#1f77b4"
SECONDARY_COLOR = "#ff7f0e"
SUCCESS_COLOR = "#2ca02c"
WARNING_COLOR = "#ff9800"
DANGER_COLOR = "#d62728"

# Priority Colors
PRIORITY_COLORS = {
    "Critical": "#d62728",
    "High": "#ff7f0e",
    "Medium": "#ff9800",
    "Low": "#2ca02c"
}

# Status Colors
STATUS_COLORS = {
    "Excellent": "#2ca02c",
    "Good": "#8bc34a",
    "Warning": "#ff9800",
    "Critical": "#d62728"
}

# Chart Configuration
CHART_HEIGHT = 400
CHART_TEMPLATE = "plotly_white"
