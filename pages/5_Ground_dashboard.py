import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ground Dashboard | CRIZCO", page_icon="🏟️", layout="wide")

if not st.session_state.get("logged_in") or st.session_state.get("role") != "ground_manager":
    st.warning("Access Denied. Please log in as a Ground Manager.")
    st.stop()

ground_name = st.session_state.linked_name
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

st.markdown("## 🏟️ Ground Manager Dashboard")
st.markdown(f"### Welcome, Manager of **{ground_name}**")

# Load Ground Info
gdf = pd.read_csv(os.path.join(DATA_DIR, "Ground_clean_dataset.csv"))
my_ground = gdf[gdf["Ground Name"] == ground_name]

if not my_ground.empty:
    st.markdown("#### Facility Details")
    st.dataframe(my_ground.drop(columns=["Ground Name"]), hide_index=True)

# Load Bookings
st.markdown("---")
st.markdown("#### 📅 Upcoming Bookings")
b_path = os.path.join(DATA_DIR, "bookings.csv")
if os.path.exists(b_path):
    bookings = pd.read_csv(b_path)
    my_bookings = bookings[bookings["ground_name"] == ground_name]
    
    if not my_bookings.empty:
        # Bar chart for bookings per month
        my_bookings['date'] = pd.to_datetime(my_bookings['date'])
        my_bookings['month'] = my_bookings['date'].dt.strftime('%Y-%m')
        monthly_counts = my_bookings.groupby('month').size()
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("**Bookings Trend**")
            st.bar_chart(monthly_counts)
        with col2:
            st.markdown("**Booking List**")
            st.dataframe(my_bookings[['date', 'booked_by', 'timeslot']].sort_values("date"), hide_index=True, use_container_width=True)
    else:
        st.info("No bookings found for your ground yet.")
else:
    st.info("Booking database not initialized yet.")