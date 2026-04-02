"""
CRIZCO — Main entry point.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from utils.init_data import init_all
from utils import auth

st.set_page_config(page_title="CRIZCO", page_icon="🏏", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #f7f9f4; }
[data-testid="stSidebar"] { background: #1b3a1b; }
[data-testid="stSidebar"] * { color: #d4edda !important; }
[data-testid="stSidebarNav"] a { padding: 0.4rem 1rem; border-radius: 6px; }
[data-testid="stSidebarNav"] a:hover { background: #2d5a2d; }
.crizco-header { background: linear-gradient(135deg, #1b4332, #2d6a4f); color: white; padding: 1.2rem 2rem; border-radius: 12px; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 12px; }
.crizco-header h1 { margin: 0; font-size: 2rem; letter-spacing: 2px; }
.crizco-header p  { margin: 0; opacity: 0.8; font-size: 0.95rem; }
.auth-card { background: white; border-radius: 16px; padding: 2rem 2.5rem; box-shadow: 0 4px 20px rgba(0,0,0,0.08); max-width: 480px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

init_all()

for key, val in [("logged_in", False), ("username", ""), ("role", ""), ("linked_name", "")]:
    if key not in st.session_state:
        st.session_state[key] = val

def logout():
    for k in ["logged_in", "username", "role", "linked_name"]:
        st.session_state[k] = "" if k != "logged_in" else False
    st.rerun()

st.markdown("""
<div class="crizco-header">
  <div>
    <h1>🏏 CRIZCO</h1>
    <p>Cricket Intelligent Zone and Coordination Organiser</p>
  </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.logged_in:
    role = st.session_state.role
    name = st.session_state.linked_name
    st.success(f"Welcome back, **{name}** ({role.replace('_', ' ').title()})")
    st.info("👈 Use the sidebar to navigate between pages.")

    if role == "team":
        st.markdown("**Your pages:**\n- 🏠 **1 Dashboard**\n- 📅 **2 Calendar**\n- 🤖 **3 Recommend**\n- 🏏 **4 Live**")
    else:
        st.markdown("**Your pages:**\n- 🏠 **5 Ground Dashboard**\n- 📅 **6 Ground Calendar**")

    if st.button("🚪 Logout", type="secondary"):
        logout()
    st.stop()

tab_login, tab_team, tab_gm = st.tabs(["🔐 Login", "🏏 Register as Team", "🏟️ Register as Ground Manager"])

with tab_login:
    st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
    st.subheader("Login to CRIZCO")
    username = st.text_input("Username", key="li_user")
    password = st.text_input("Password", type="password", key="li_pass")
    if st.button("Login", type="primary", use_container_width=True):
        user = auth.login(username.strip(), password)
        if user:
            st.session_state.logged_in  = True
            st.session_state.username   = user["username"]
            st.session_state.role       = user["role"]
            st.session_state.linked_name = user["linked_name"]
            st.rerun()
        else:
            st.error("Invalid username or password.")
    st.caption("Demo — Team: `royal_xi` / `password123`  |  Ground: `ncc_manager` / `password123`")
    st.markdown("</div>", unsafe_allow_html=True)

with tab_team:
    st.subheader("Register Your Team")
    col1, col2 = st.columns(2)
    with col1:
        rt_team    = st.text_input("Team Name", key="rt_team")
        rt_captain = st.text_input("Captain Name", key="rt_cap")
        rt_vc      = st.text_input("Vice-Captain Name", key="rt_vc")
    with col2:
        rt_contact = st.text_input("Contact Number", key="rt_contact")
        rt_user    = st.text_input("Choose Username", key="rt_user")
        rt_pass    = st.text_input("Choose Password", type="password", key="rt_pass")
        rt_pass2   = st.text_input("Confirm Password", type="password", key="rt_pass2")

    if st.button("Register Team", type="primary", key="btn_rt"):
        if not all([rt_team, rt_captain, rt_user, rt_pass]):
            st.error("Please fill all required fields.")
        elif rt_pass != rt_pass2:
            st.error("Passwords do not match.")
        else:
            ok, msg = auth.register_team(rt_user.strip(), rt_pass, rt_team.strip(), rt_captain.strip(), rt_vc.strip(), rt_contact.strip())
            if ok:
                st.success(msg + " Please login.")
            else:
                st.error(msg)

with tab_gm:
    st.subheader("Register Your Ground")
    import pandas as pd
    _gdf = pd.read_csv(os.path.join(os.path.dirname(__file__), "artifacts", "Ground_clean_dataset.csv"))

    col1, col2 = st.columns(2)
    with col1:
        gm_user    = st.text_input("Username", key="gm_user")
        gm_pass    = st.text_input("Password", type="password", key="gm_pass")
        gm_pass2   = st.text_input("Confirm Password", type="password", key="gm_pass2")
        gm_contact = st.text_input("Contact Number", key="gm_contact")
        gm_ground  = st.text_input("Ground Name", key="gm_ground")
        gm_city    = st.selectbox("City", sorted(_gdf["City"].dropna().unique()), key="gm_city")
        gm_district = st.selectbox("District", sorted(_gdf["District"].dropna().unique()), key="gm_dist")
        gm_province = st.selectbox("Province", sorted(_gdf["Province"].dropna().unique()), key="gm_prov")
        gm_type    = st.selectbox("Ground Type", ["Public", "School", "Club", "Private"], key="gm_type")
        gm_pitch   = st.selectbox("Pitch Type", ["turf", "matting", "cement"], key="gm_pitch")
    with col2:
        gm_len  = st.number_input("Length (m)", 80, 200, 120, key="gm_len")
        gm_wid  = st.number_input("Width (m)",  80, 200, 120, key="gm_wid")
        gm_rooms = st.number_input("Changing Rooms", 0, 10, 2, key="gm_rooms")
        gm_pcap  = st.number_input("Parking Capacity", 0, 1000, 50, key="gm_pcap")
        gm_price = st.number_input("Price per Day (LKR)", 5000, 250000, 50000, step=1000, key="gm_price")
        st.markdown("**Facilities**")
        gm_lights = st.checkbox("Floodlights", key="gm_lights")
        gm_park   = st.checkbox("Parking", value=True, key="gm_park")
        gm_wash   = st.checkbox("Washrooms", value=True, key="gm_wash")
        gm_pav    = st.checkbox("Pavilion", key="gm_pav")
        gm_score  = st.checkbox("Scoreboard", key="gm_score")

    if st.button("Register Ground", type="primary", key="btn_gm"):
        if not all([gm_user, gm_pass, gm_ground]):
            st.error("Please fill all required fields.")
        elif gm_pass != gm_pass2:
            st.error("Passwords do not match.")
        else:
            ok, msg = auth.register_ground_manager(
                gm_user.strip(), gm_pass, gm_ground.strip(), gm_contact.strip(),
                gm_city, gm_district, gm_province, gm_type, gm_pitch,
                gm_len, gm_wid, gm_lights, gm_park, gm_wash,
                gm_pav, gm_score, gm_rooms, gm_pcap, gm_price
            )
            if ok:
                st.success(msg + " Please login.")
            else:
                st.error(msg)