import os, sys, calendar, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st
from utils.bookings import get_bookings_for_month

st.set_page_config(page_title="Calendar | CRIZCO", page_icon="📅", layout="wide")

if not st.session_state.get("logged_in"):
    st.warning("Please login first.")
    st.stop()

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#f7f9f4}
.ph{background:linear-gradient(135deg,#1b4332,#2d6a4f);color:white;padding:1.2rem 2rem;border-radius:12px;margin-bottom:1.2rem}
.cal-wrap{background:white;border-radius:16px;padding:1.2rem;box-shadow:0 4px 16px rgba(0,0,0,.08)}
.cal-hdr{display:grid;grid-template-columns:repeat(7,1fr);gap:4px;margin-bottom:4px}
.cal-hdr-cell{text-align:center;font-weight:700;font-size:.8rem;color:#666;padding:6px 0;background:#f0f7f0;border-radius:6px}
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:4px}
.cal-cell{background:#fafffe;border:1px solid #e8f5e9;border-radius:8px;min-height:82px;padding:5px 7px;position:relative}
.cal-cell.today{border:2px solid #2d6a4f;background:#f0fdf4}
.cal-cell.has-booking{background:#fff8e1}
.day-num{font-weight:700;font-size:.9rem;color:#333;margin-bottom:3px}
.day-num.today-num{background:#1b4332;color:white;border-radius:50%;width:22px;height:22px;display:inline-flex;align-items:center;justify-content:center;font-size:.78rem}
.event-pill{background:#c8e6c9;color:#1b5e20;border-radius:4px;padding:1px 5px;font-size:.7rem;margin-top:2px;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.event-pill-self{background:#fff3cd;color:#856404}
.empty-cell{min-height:82px}
.legend-dot{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:5px;vertical-align:middle}
</style>""", unsafe_allow_html=True)

st.markdown('<div class="ph"><h2>📅 Ground Availability Calendar</h2><p>See which grounds are booked and when</p></div>', unsafe_allow_html=True)

today = datetime.date.today()
months = ["January","February","March","April","May","June","July","August","September","October","November","December"]

col1, col2, col3 = st.columns([2, 2, 4])
with col1: sel_month = st.selectbox("Month", months, index=today.month - 1, key="cal_month")
with col2: sel_year  = st.number_input("Year", 2024, 2028, today.year, key="cal_year")
with col3: search_ground = st.text_input("Filter by ground name (optional)", key="cal_filter")

month_num = months.index(sel_month) + 1
bookings_df = get_bookings_for_month(int(sel_year), month_num)

day_events: dict = {}
for _, row in bookings_df.iterrows():
    d = row["date"].day
    entry = (row.get("ground_name","?"), row.get("booked_by","?"))
    if search_ground and search_ground.lower() not in entry[0].lower():
        continue
    day_events.setdefault(d, []).append(entry)

cal_matrix = calendar.monthcalendar(int(sel_year), month_num)
my_team    = st.session_state.get("linked_name", "")

st.markdown(f"### {sel_month} {sel_year}")

cal_html = ['<div class="cal-wrap"><div class="cal-hdr">']
for d in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]:
    cal_html.append(f'<div class="cal-hdr-cell">{d}</div>')
cal_html.append('</div><div class="cal-grid">')

for week in cal_matrix:
    for day in week:
        if day == 0:
            cal_html.append('<div class="empty-cell"></div>')
        else:
            is_today = (day == today.day and month_num == today.month and int(sel_year) == today.year)
            has_ev   = day in day_events
            cls = "cal-cell today" if is_today else ("cal-cell has-booking" if has_ev else "cal-cell")
            num_html = f'<span class="day-num today-num">{day}</span>' if is_today else f'<span class="day-num">{day}</span>'
            pills = ""
            for gname, booker in day_events.get(day, []):
                pill_cls = "event-pill-self" if booker == my_team else ""
                short = gname if len(gname) <= 18 else gname[:16] + "…"
                pills += f'<span class="event-pill {pill_cls}" title="{gname} — {booker}">{short}</span>'
            cal_html.append(f'<div class="{cls}">{num_html}{pills}</div>')
cal_html.append('</div></div>')
st.markdown("".join(cal_html), unsafe_allow_html=True)

st.markdown("""<div style="margin-top:.8rem;font-size:.82rem;color:#555;display:flex;gap:16px">
  <span><span class="legend-dot" style="background:#c8e6c9"></span>Other team booking</span>
  <span><span class="legend-dot" style="background:#fff3cd"></span>Your team's booking</span>
  <span><span class="legend-dot" style="background:#f0fdf4;border:2px solid #2d6a4f"></span>Today</span></div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("#### Bookings This Month")
if bookings_df.empty:
    st.info(f"No bookings found for {sel_month} {sel_year}.")
else:
    show = bookings_df.copy()
    show["date"] = show["date"].dt.strftime("%Y-%m-%d")
    st.dataframe(show.rename(columns={"ground_name": "Ground", "date": "Date", "booked_by": "Booked By"})[["Date","Ground","Booked By"]].sort_values("Date"), use_container_width=True, hide_index=True)