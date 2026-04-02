"""
Page 1 – Team Dashboard
Shows team stats, win rates, ground history, captain info.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd

from utils import auth
from utils.scoring import get_completed_matches

st.set_page_config(page_title="Dashboard | CRIZCO", page_icon="🏏", layout="wide")

# ── Auth guard ────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.warning("Please login first.")
    st.stop()
if st.session_state.get("role") != "team":
    st.warning("This page is for team users only.")
    st.stop()

team_name = st.session_state.linked_name
DATA_DIR  = os.path.join(os.path.dirname(__file__), "..", "data")

# ── Shared CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#f7f9f4}
.ph{background:linear-gradient(135deg,#1b4332,#2d6a4f);color:white;
    padding:1.2rem 2rem;border-radius:12px;margin-bottom:1.2rem}
.ph h2{margin:0;font-size:1.6rem} .ph p{margin:0;opacity:.8;font-size:.9rem}
.mc{background:white;border-radius:12px;padding:1.2rem 1.5rem;
    box-shadow:0 2px 8px rgba(0,0,0,.06);text-align:center;margin-bottom:.6rem}
.mc .val{font-size:2rem;font-weight:700;color:#1b4332}
.mc .lbl{font-size:.82rem;color:#666;margin-top:2px}
.info-card{background:white;border-radius:12px;padding:1.2rem 1.5rem;
           box-shadow:0 2px 8px rgba(0,0,0,.06);margin-bottom:1rem}
</style>""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="ph">
  <h2>🏏 {team_name}</h2>
  <p>Team Dashboard — Season Overview</p>
</div>
""", unsafe_allow_html=True)

# ── Load team info ────────────────────────────────────────────────────────────
team_info = auth.get_team_info(team_name)
captain   = team_info.get("captain", "—")
vice_cap  = team_info.get("vice_captain", "—")
contact   = team_info.get("contact", "—")

# ── Load stats safely ─────────────────────────────────────────────────────────
ts_path = os.path.join(DATA_DIR, "team_stats.csv")
team_stats = pd.DataFrame()

if os.path.exists(ts_path):
    try:
        ts = pd.read_csv(ts_path)
        ts.columns = ts.columns.str.strip()
        if "team_name" in ts.columns:
            team_stats = ts[ts["team_name"] == team_name].copy()
    except pd.errors.EmptyDataError:
        pass

if not team_stats.empty and "matches_played" in team_stats.columns:
    total_matches = int(pd.to_numeric(team_stats["matches_played"], errors='coerce').fillna(0).sum())
    total_wins    = int(pd.to_numeric(team_stats["wins"], errors='coerce').fillna(0).sum())
    win_rate      = round((total_wins / total_matches * 100) if total_matches else 0, 1)
    grounds_count = len(team_stats["ground_name"].unique()) if "ground_name" in team_stats.columns else 0
else:
    total_matches, total_wins, win_rate, grounds_count = 0, 0, 0.0, 0

# ── Captain card ──────────────────────────────────────────────────────────────
col_a, col_b = st.columns([2, 1])
with col_a:
    st.markdown("<div class='section-title'>👤 Team Profile</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="info-card">
      <table style="width:100%;font-size:.95rem">
        <tr><td style="color:#888;width:45%">Captain</td>
            <td><strong>{captain}</strong></td></tr>
        <tr><td style="color:#888">Vice Captain</td>
            <td><strong>{vice_cap}</strong></td></tr>
        <tr><td style="color:#888">Contact</td>
            <td>{contact}</td></tr>
        <tr><td style="color:#888">Username</td>
            <td>{st.session_state.username}</td></tr>
      </table>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("<div class='section-title'>🏅 Quick Stats</div>", unsafe_allow_html=True)
    for val, lbl, icon in [
        (total_matches, "Matches Played", "🏏"),
        (total_wins,    "Matches Won",    "🏆"),
        (f"{win_rate}%","Win Rate",       "📈"),
        (grounds_count, "Grounds Used",   "🏟️"),
    ]:
        st.markdown(f"""
        <div class="mc">
          <div class="val">{icon} {val}</div>
          <div class="lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

# ── Ground performance table ──────────────────────────────────────────────────
st.markdown("<div class='section-title'>🏟️ Performance by Ground</div>", unsafe_allow_html=True)

if team_stats.empty or "matches_played" not in team_stats.columns:
    st.info("No match data found for your team yet. Score a match to see your stats!")
else:
    disp = team_stats.copy()
    disp["matches_played"] = pd.to_numeric(disp["matches_played"], errors='coerce').fillna(0).astype(int)
    disp["wins"]           = pd.to_numeric(disp["wins"], errors='coerce').fillna(0).astype(int)
    disp["Win Rate"]       = disp.apply(
        lambda r: f"{round(r['wins']/r['matches_played']*100,1)}%"
        if r["matches_played"] > 0 else "—", axis=1
    )
    disp = disp.rename(columns={
        "team_name": "Team", "ground_name": "Ground",
        "matches_played": "Played", "wins": "Won"
    })[["Ground", "Played", "Won", "Win Rate"]].sort_values("Played", ascending=False)

    st.dataframe(disp, use_container_width=True, hide_index=True)

# ── Recent completed matches ──────────────────────────────────────────────────
st.markdown("<div class='section-title'>📋 Recent Matches</div>", unsafe_allow_html=True)

completed = get_completed_matches()
team_matches = [m for m in completed if m.get("team_a") == team_name or m.get("team_b") == team_name]

if not team_matches:
    st.info("No completed matches recorded yet.")
else:
    for m in reversed(team_matches[-5:]):
        # Safe dict gets prevent crashes if old CSV data is missing columns
        team_a_val = m.get("team_a", "Unknown")
        team_b_val = m.get("team_b", "Unknown")
        winner_val = m.get("winner", "Unknown")
        
        opp = team_b_val if team_a_val == team_name else team_a_val
        won = (winner_val == team_name)
        color = "#d4edda" if won else "#f8d7da"
        result_text = "Won ✅" if won else ("Lost ❌" if winner_val != "Tie" else "Tie 🤝")
        
        m_date = m.get('date', 'Unknown Date')
        m_ground = m.get('ground', '—')
        m_overs = m.get('overs', 'N/A')

        st.markdown(f"""
        <div style="background:{color};border-radius:10px;padding:.7rem 1.2rem;
                    margin-bottom:.5rem;display:flex;justify-content:space-between;
                    align-items:center">
          <div>
            <strong>{team_name}</strong> vs <strong>{opp}</strong>
            <span style="color:#555;font-size:.85rem;margin-left:8px">
              📅 {m_date} | 🏟️ {m_ground} | {m_overs} overs
            </span>
          </div>
          <div><strong>{result_text}</strong></div>
        </div>
        """, unsafe_allow_html=True)