"""
Equipment Page
"""

import streamlit as st
import pandas as pd
from utils.api_client import get_api_client

def show():
    """Display equipment page"""
    
    st.markdown('<h1 class="main-header">🔧 Equipment Management</h1>', unsafe_allow_html=True)
    
    api = get_api_client()
    
    # Get all equipment first to extract unique values for filters
    all_equipment = api.get_equipment()
    
    # Extract unique types and locations
    if all_equipment and all_equipment.get('data'):
        df_all = pd.DataFrame(all_equipment['data'])
        equipment_types = ["All"] + sorted(df_all['equipment_type'].unique().tolist())
        locations = ["All"] + sorted(df_all['location'].unique().tolist())
    else:
        equipment_types = ["All", "Harvester", "Tractor", "Planter", "Sprayer"]
        locations = ["All"]
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        equipment_type = st.selectbox("Equipment Type", equipment_types)
    with col2:
        location = st.selectbox("Location", locations)
    
    # Fetch equipment based on filters using dedicated endpoints
    with st.spinner("Loading equipment..."):
        # Use specific endpoints for better performance
        if equipment_type != "All" and location == "All":
            # Filter by type only - using dedicated endpoint
            st.caption(f"📡 Using endpoint: /api/v1/equipment/by-type/{equipment_type}")
            equipment_data = api.get_equipment_by_type(equipment_type)
        elif location != "All" and equipment_type == "All":
            # Filter by location only - using dedicated endpoint
            st.caption(f"📡 Using endpoint: /api/v1/equipment/by-location/{location}")
            equipment_data = api.get_equipment_by_location(location)
        elif equipment_type != "All" and location != "All":
            # Both filters - use general endpoint with parameters
            st.caption(f"📡 Using endpoint: /api/v1/equipment?equipment_type={equipment_type}&location={location}")
            equipment_data = api.get_equipment(
                equipment_type=equipment_type,
                location=location
            )
        else:
            # No filters - get all
            st.caption("📡 Using endpoint: /api/v1/equipment (all)")
            equipment_data = api.get_equipment()
    
    if equipment_data and equipment_data.get('data'):
        df = pd.DataFrame(equipment_data['data'])
        
        # Show filtered count
        st.markdown(f"### Total Equipment: {len(df)}")
        
        # Show active filters
        if equipment_type != "All" or location != "All":
            filters_applied = []
            if equipment_type != "All":
                filters_applied.append(f"Type: {equipment_type}")
            if location != "All":
                filters_applied.append(f"Location: {location}")
            st.info(f"🔍 Filters applied: {', '.join(filters_applied)}")
        
        # Display table
        st.dataframe(
            df[['equipment_id', 'equipment_type', 'brand', 'model', 'location', 'operating_hours']],
            use_container_width=True,
            hide_index=True
        )
        
        # Show equipment details on selection
        st.markdown("---")
        st.markdown("### 📋 Equipment Details")
        
        selected_equipment = st.selectbox(
            "Select equipment to view details:",
            options=["None"] + df['equipment_id'].tolist()
        )
        
        if selected_equipment != "None":
            equipment_details = api.get_equipment_by_id(selected_equipment)
            
            if equipment_details:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Equipment ID", equipment_details.get('equipment_id', 'N/A'))
                    st.metric("Type", equipment_details.get('equipment_type', 'N/A'))
                    st.metric("Brand", equipment_details.get('brand', 'N/A'))
                
                with col2:
                    st.metric("Model", equipment_details.get('model', 'N/A'))
                    st.metric("Location", equipment_details.get('location', 'N/A'))
                    st.metric("Year", equipment_details.get('year_manufactured', 'N/A'))
                
                with col3:
                    st.metric("Operating Hours", f"{equipment_details.get('operating_hours', 0):.0f}")
                    st.metric("Purchase Date", equipment_details.get('purchase_date', 'N/A'))
                    st.metric("Last Service", equipment_details.get('last_service_date', 'N/A'))
    else:
        st.warning("⚠️ No equipment found matching the selected filters")
