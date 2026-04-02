"""
Page 3 – ML Ground Recommendation & Booking
Uses Random Forest model + weather API to recommend grounds.
Includes payment flow and receipt download.
"""
import os, sys, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd

from utils.ml_engine import recommend
from utils.weather   import get_weather, weather_icon
from utils.bookings  import is_available, book_ground, save_payment
from utils.pdf_gen   import generate_receipt

st.set_page_config(page_title="Recommend | CRIZCO", page_icon="🤖", layout="wide")

if not st.session_state.get("logged_in"):
    st.warning("Please login first.")
    st.stop()
if st.session_state.get("role") != "team":
    st.warning("This page is for team users only.")
    st.stop()

team_name = st.session_state.linked_name
DATA_DIR  = os.path.join(os.path.dirname(__file__), "..", "data")

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#f7f9f4}
.ph{background:linear-gradient(135deg,#1b4332,#2d6a4f);color:white;
    padding:1.2rem 2rem;border-radius:12px;margin-bottom:1.2rem}
.ph h2{margin:0;font-size:1.6rem} .ph p{margin:0;opacity:.8;font-size:.9rem}
.gc{background:white;border-radius:14px;padding:1.2rem 1.5rem;
    box-shadow:0 2px 10px rgba(0,0,0,.07);margin-bottom:.8rem;
    border-left:5px solid #2d6a4f}
.gc h3{margin:0 0 4px;color:#1b4332;font-size:1.05rem}
.gc p{margin:2px 0;font-size:.85rem;color:#555}
.score-bar-wrap{background:#e8f5e9;border-radius:6px;height:10px;margin:6px 0}
.score-bar{background:#2d6a4f;border-radius:6px;height:10px}
.badge{display:inline-block;padding:2px 10px;border-radius:20px;
       font-size:.75rem;font-weight:600;margin:2px}
.badge-green{background:#d4edda;color:#155724}
.badge-gray{background:#e2e3e5;color:#383d41}
.badge-orange{background:#fff3cd;color:#856404}
.badge-red{background:#f8d7da;color:#721c24}
.receipt-box{background:white;border-radius:12px;padding:1.5rem 2rem;
             border:2px dashed #2d6a4f;max-width:460px;margin:0 auto;
             text-align:center}
.section-title{font-size:1.1rem;font-weight:700;color:#1b4332;
               border-bottom:2px solid #2d6a4f;padding-bottom:4px;
               margin:1.2rem 0 .8rem}
</style>""", unsafe_allow_html=True)

st.markdown("""
<div class="ph">
  <h2>🤖 ML Ground Recommendation</h2>
  <p>AI-powered ground suggestions based on your team's history, weather, and preferences</p>
</div>
""", unsafe_allow_html=True)

# ── Load cities ───────────────────────────────────────────────────────────────
gdf = pd.read_csv(os.path.join(DATA_DIR, "Ground_clean_dataset.csv"))
cities     = sorted(gdf["City"].dropna().unique())
provinces  = sorted(gdf["Province"].dropna().unique())
districts  = sorted(gdf["District"].dropna().unique())

# ── Session state for booking flow ────────────────────────────────────────────
for k, v in [("rec_results", None), ("selected_ground", None),
             ("booking_done", False), ("receipt_data", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Input Area (Form Removed for instant updates) ─────────────────────────────
st.markdown("### 🎯 Enter Your Preferences")
col1, col2, col3 = st.columns(3)

with col1:
    search_by = st.radio("Search by", ["City", "District", "Province"],
                         horizontal=True, key="search_by")
    
    # This dropdown will now instantly swap when you click the radio button!
    if search_by == "City":
        location_val = st.selectbox("Select City", cities)
    elif search_by == "District":
        location_val = st.selectbox("Select District", districts)
    else:
        location_val = st.selectbox("Select Province", provinces)

    match_date = st.date_input("Match Date",
                               value=datetime.date.today() + datetime.timedelta(days=3),
                               min_value=datetime.date.today())
    timeslot   = st.selectbox("Timeslot", ["Full Day", "Morning (6AM-12PM)",
                                           "Afternoon (12PM-6PM)", "Evening (6PM-10PM)"])

with col2:
    pitch_type  = st.selectbox("Pitch Type Preference",
                               ["Any", "turf", "matting", "cement"])
    ground_type = st.selectbox("Ground Type",
                               ["Any", "Public", "School", "Club", "Private"])
    max_price   = st.slider("Max Price (LKR)", 5000, 200000, 100000, step=5000)
    top_n       = st.slider("Number of Recommendations", 3, 10, 5)

with col3:
    st.markdown("**Required Facilities**")
    need_lights   = st.checkbox("Floodlights")
    need_parking  = st.checkbox("Parking")
    need_washroom = st.checkbox("Washrooms")
    need_pavilion = st.checkbox("Pavilion")
    need_scoreboard = st.checkbox("Scoreboard")

# Swapped to a normal button
submitted = st.button("🔍 Get Recommendations", type="primary", use_container_width=True)

if submitted:
    date_str = str(match_date)

    # Fetch weather
    with st.spinner("Fetching weather forecast…"):
        weather_label = get_weather(
            location_val if search_by == "City" else "Colombo",
            date_str
        )

    # Build filter kwargs
    kwargs = dict(
        max_price=max_price,
        team_name=team_name,
        weather_label=weather_label,
        top_n=top_n,
        needs_lights=need_lights or None,
        needs_parking=need_parking or None,
        needs_washrooms=need_washroom or None,
        needs_pavilion=need_pavilion or None,
        needs_scoreboard=need_scoreboard or None,
    )
    if search_by == "City":
        kwargs["city"] = location_val
    elif search_by == "District":
        kwargs["district"] = location_val
    else:
        kwargs["province"] = location_val

    if pitch_type != "Any":
        kwargs["pitch"] = pitch_type
    if ground_type != "Any":
        kwargs["ground_type"] = ground_type

    with st.spinner("Running ML recommendation engine…"):
        results = recommend(**kwargs)

    st.session_state.rec_results     = results
    st.session_state.selected_ground = None
    st.session_state.booking_done    = False
    st.session_state.match_date      = date_str
    st.session_state.timeslot        = timeslot
    st.session_state.weather_label   = weather_label

# ── Show results ──────────────────────────────────────────────────────────────
results = st.session_state.get("rec_results")

if results is not None and not isinstance(results, type(None)):
    if hasattr(results, "empty") and results.empty:
        st.warning("No grounds found matching your criteria. Try relaxing the filters.")
    else:
        weather_label = st.session_state.get("weather_label", "Unknown")
        date_str      = st.session_state.get("match_date", "")

        # Weather banner
        wicon = weather_icon(weather_label)
        rain_warn = "rain" in weather_label.lower()
        banner_color = "#f8d7da" if rain_warn else "#d4edda"
        banner_text  = (f"⚠️ Rain forecast for {date_str}. Scores may be adjusted."
                        if rain_warn else
                        f"✅ Weather looks good for {date_str}.")
        st.markdown(f"""
        <div style="background:{banner_color};border-radius:10px;
                    padding:.7rem 1.2rem;margin-bottom:1rem;font-size:.9rem">
          {wicon} <strong>Weather:</strong> {weather_label} &nbsp;|&nbsp; {banner_text}
        </div>""", unsafe_allow_html=True)

        st.markdown(f"<div class='section-title'>🏟️ Top {len(results)} Recommended Grounds</div>",
                    unsafe_allow_html=True)

        for rank, (_, row) in enumerate(results.iterrows(), 1):
            gname   = row.get("Ground Name", "—")
            city    = row.get("City", "—")
            pitch   = row.get("Pitch", "—")
            price   = row.get("Price (LKR)", 0)
            rating  = row.get("Rating", 0)
            ml_sc   = float(row.get("ml_score",   0))
            win_r   = float(row.get("win_rate",    0))
            fin_sc  = float(row.get("final_score", 0))
            avail   = is_available(gname, date_str)

            # Facility badges
            fac_badges = ""
            for fac, label in [("Lights","💡 Lights"), ("Parking","🚗 Parking"),
                                ("Washrooms","🚿 Washrooms"), ("Pavilion","🏛️ Pavilion"),
                                ("Scoreboard","📊 Scoreboard")]:
                val = str(row.get(fac, "No")).strip().lower()
                if val == "yes":
                    fac_badges += f'<span class="badge badge-green">{label}</span>'

            score_pct = int(fin_sc * 100)
            medal = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"][rank-1]

            avail_html = (
                '<span class="badge badge-green">✅ Available</span>'
                if avail else
                '<span class="badge badge-red">❌ Already Booked</span>'
            )

            st.markdown(f"""
            <div class="gc">
              <h3>{medal} #{rank} &nbsp; {gname}</h3>
              <p>📍 {city} &nbsp;|&nbsp; 🏏 Pitch: {pitch} &nbsp;|&nbsp;
                 💰 LKR {price:,.0f}/day &nbsp;|&nbsp; ⭐ Rating: {rating}/5
                 &nbsp;|&nbsp; {avail_html}</p>
              <div style="margin:6px 0">{fac_badges}</div>
              <div style="display:flex;gap:16px;font-size:.82rem;color:#555;margin:4px 0">
                <span>🤖 ML Score: <strong>{ml_sc:.0%}</strong></span>
                <span>🏆 Win Rate: <strong>{win_r:.0%}</strong></span>
                <span>🎯 Final Score: <strong>{fin_sc:.0%}</strong></span>
              </div>
              <div class="score-bar-wrap">
                <div class="score-bar" style="width:{score_pct}%"></div>
              </div>
            </div>""", unsafe_allow_html=True)

            if avail and not st.session_state.booking_done:
                if st.button(f"📋 Book — {gname}", key=f"book_{rank}"):
                    st.session_state.selected_ground = row.to_dict()
                    st.rerun()

# ── Payment / booking flow ────────────────────────────────────────────────────
if st.session_state.get("selected_ground") and not st.session_state.booking_done:
    sg    = st.session_state.selected_ground
    gname = sg.get("Ground Name", "")
    price = float(sg.get("Price (LKR)", 0))
    date_str  = st.session_state.get("match_date", "")
    timeslot  = st.session_state.get("timeslot", "Full Day")

    st.markdown("---")
    st.markdown(f"<div class='section-title'>💳 Book: {gname}</div>",
                unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#e8f5e9;border-radius:10px;padding:1rem 1.4rem;margin-bottom:1rem">
      <strong>Booking Summary</strong><br>
      Ground: <strong>{gname}</strong> &nbsp;|&nbsp;
      Date: <strong>{date_str}</strong> &nbsp;|&nbsp;
      Timeslot: <strong>{timeslot}</strong> &nbsp;|&nbsp;
      Amount: <strong>LKR {price:,.2f}</strong>
    </div>""", unsafe_allow_html=True)

    pay_method = st.radio("Payment Method", ["💳 Card Payment", "🏦 Bank Transfer"],
                          horizontal=True)

    if pay_method == "💳 Card Payment":
        col1, col2 = st.columns(2)
        with col1:
            card_name = st.text_input("Cardholder Name")
            card_num  = st.text_input("Card Number (16 digits)", max_chars=19,
                                       placeholder="1234 5678 9012 3456")
        with col2:
            card_exp  = st.text_input("Expiry Date", placeholder="MM/YY", max_chars=5)
            card_cvv  = st.text_input("CVV", max_chars=3, type="password")

        if st.button("✅ Confirm Payment", type="primary"):
            # Basic validation
            clean_num = card_num.replace(" ", "").replace("-", "")
            if len(clean_num) != 16 or not clean_num.isdigit():
                st.error("Please enter a valid 16-digit card number.")
            elif len(card_exp) < 4:
                st.error("Please enter a valid expiry date.")
            elif len(card_cvv) != 3:
                st.error("Please enter a valid 3-digit CVV.")
            else:
                with st.spinner("Processing payment…"):
                    receipt_id = save_payment(
                        team_name, gname, date_str, timeslot,
                        price, "Card Payment"
                    )
                    book_ground(gname, date_str, team_name, timeslot)
                st.session_state.booking_done = True
                st.session_state.receipt_data = {
                    "receipt_id": receipt_id, "team_name": team_name,
                    "ground_name": gname, "date_str": date_str,
                    "timeslot": timeslot, "amount_lkr": price,
                    "method": "Card Payment"
                }
                st.rerun()

    else:  # Bank Transfer
        st.markdown("""
        <div style="background:#fff3cd;border-radius:10px;padding:1rem 1.4rem">
          <strong>Bank Transfer Details</strong><br>
          Bank: <strong>Bank of Ceylon</strong><br>
          Account Name: <strong>CRIZCO Sports (Pvt) Ltd</strong><br>
          Account Number: <strong>8872-0001-5643</strong><br>
          Branch: <strong>Colombo 07</strong><br><br>
          Please transfer the exact amount and use your team name as reference.
        </div>""", unsafe_allow_html=True)

        transfer_ref = st.text_input("Your Transfer Reference Number")
        if st.button("✅ Confirm Transfer", type="primary"):
            if not transfer_ref.strip():
                st.error("Please enter your transfer reference number.")
            else:
                with st.spinner("Confirming booking…"):
                    receipt_id = save_payment(
                        team_name, gname, date_str, timeslot,
                        price, "Bank Transfer"
                    )
                    book_ground(gname, date_str, team_name, timeslot)
                st.session_state.booking_done = True
                st.session_state.receipt_data = {
                    "receipt_id": receipt_id, "team_name": team_name,
                    "ground_name": gname, "date_str": date_str,
                    "timeslot": timeslot, "amount_lkr": price,
                    "method": f"Bank Transfer (Ref: {transfer_ref})"
                }
                st.rerun()

    if st.button("← Cancel Booking", type="secondary"):
        st.session_state.selected_ground = None
        st.rerun()

# ── Receipt ────────────────────────────────────────────────────────────────────
if st.session_state.booking_done and st.session_state.get("receipt_data"):
    rd = st.session_state.receipt_data
    st.success("🎉 Booking Confirmed! Your ground is secured.")
    st.balloons()

    st.markdown(f"""
    <div class="receipt-box">
      <div style="font-size:2.5rem;margin-bottom:.5rem">🏏</div>
      <h2 style="color:#1b4332;margin:0">Booking Confirmed!</h2>
      <hr style="border-color:#c8e6c9">
      <table style="width:100%;font-size:.9rem;text-align:left;border-collapse:collapse">
        <tr><td style="color:#888;padding:4px 0">Receipt ID</td>
            <td style="font-weight:700">{rd['receipt_id']}</td></tr>
        <tr><td style="color:#888;padding:4px 0">Team</td>
            <td>{rd['team_name']}</td></tr>
        <tr><td style="color:#888;padding:4px 0">Ground</td>
            <td>{rd['ground_name']}</td></tr>
        <tr><td style="color:#888;padding:4px 0">Date</td>
            <td>{rd['date_str']}</td></tr>
        <tr><td style="color:#888;padding:4px 0">Timeslot</td>
            <td>{rd['timeslot']}</td></tr>
        <tr><td style="color:#888;padding:4px 0">Amount</td>
            <td><strong>LKR {float(rd['amount_lkr']):,.2f}</strong></td></tr>
        <tr><td style="color:#888;padding:4px 0">Payment</td>
            <td>{rd['method']}</td></tr>
      </table>
    </div>""", unsafe_allow_html=True)

    try:
        pdf_bytes = generate_receipt(
            rd["receipt_id"], rd["team_name"], rd["ground_name"],
            rd["date_str"], rd["timeslot"], rd["amount_lkr"], rd["method"]
        )
        st.download_button(
            "⬇️ Download Receipt (PDF)",
            data=pdf_bytes,
            file_name=f"CRIZCO_Receipt_{rd['receipt_id']}.pdf",
            mime="application/pdf",
            type="primary"
        )
    except Exception as e:
        st.info(f"Receipt ready. PDF generation: {e}")

    if st.button("🔁 Make Another Booking", type="secondary"):
        st.session_state.rec_results     = None
        st.session_state.selected_ground = None
        st.session_state.booking_done    = False
        st.session_state.receipt_data    = None
        st.rerun()