"""
Page 4 – Live Scoring & Watching
Full ball-by-ball scoring engine + live match watching.
"""
import os, sys, json, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd

from utils import scoring as sc
from utils.pdf_gen import generate_scorecard

st.set_page_config(page_title="Live | CRIZCO", page_icon="🏏", layout="wide")

if not st.session_state.get("logged_in"):
    st.warning("Please login first.")
    st.stop()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#0a1628}
[data-testid="stAppViewContainer"] *{color:#e8f4fd}
[data-testid="stSidebar"]{background:#051020}
.ph{background:linear-gradient(135deg,#0d2137,#1a3a5c);color:white;
    padding:1.2rem 2rem;border-radius:12px;margin-bottom:1.2rem;
    border:1px solid #1e4d7b}
.ph h2{margin:0;font-size:1.6rem} .ph p{margin:0;opacity:.7;font-size:.9rem}
.score-panel{background:#0d2137;border-radius:16px;padding:1.5rem;
             border:1px solid #1e4d7b;text-align:center;margin-bottom:1rem}
.score-big{font-size:4rem;font-weight:800;color:#4fc3f7;line-height:1}
.score-sub{font-size:1rem;color:#90caf9;margin-top:4px}
.team-label{font-size:1.1rem;font-weight:700;color:#81d4fa;margin-bottom:4px}
.over-info{font-size:1rem;color:#b0bec5;margin-top:6px}
.ball-log{display:flex;gap:5px;flex-wrap:wrap;margin:8px 0}
.ball-dot{width:32px;height:32px;border-radius:50%;display:inline-flex;
          align-items:center;justify-content:center;font-size:.8rem;
          font-weight:700}
.ball-0{background:#37474f;color:#90a4ae}
.ball-1,.ball-2,.ball-3{background:#1565c0;color:white}
.ball-4{background:#2e7d32;color:white}
.ball-6{background:#e65100;color:white}
.ball-W{background:#b71c1c;color:white}
.ball-X{background:#5d4037;color:#bcaaa4}
.btn-ball{border-radius:10px;font-size:1rem;font-weight:700;
          padding:.5rem .8rem;border:none;cursor:pointer;width:100%}
.btn-0{background:#37474f;color:#cfd8dc}
.btn-1,.btn-2,.btn-3{background:#1565c0;color:white}
.btn-4{background:#2e7d32;color:white;font-size:1.2rem}
.btn-6{background:#e65100;color:white;font-size:1.2rem}
.btn-W{background:#b71c1c;color:white;font-size:1.1rem}
.btn-extra{background:#4a148c;color:#e1bee7}
.bat-row{background:#0d2137;border-radius:8px;padding:.5rem .8rem;
         margin:2px 0;display:flex;justify-content:space-between;
         border:1px solid #1e4d7b;font-size:.88rem}
.bat-active{border-color:#4fc3f7;background:#122a45}
.bow-row{background:#0d2137;border-radius:8px;padding:.4rem .8rem;
         margin:2px 0;display:flex;justify-content:space-between;
         border:1px solid #1e4d7b;font-size:.85rem}
.match-card{background:#0d2137;border-radius:12px;padding:1rem 1.4rem;
            border:1px solid #1e4d7b;margin-bottom:.8rem}
.mc-title{font-size:1rem;font-weight:700;color:#81d4fa;margin:0 0 4px}
.mc-detail{font-size:.83rem;color:#b0bec5;margin:2px 0}
.section-title{font-size:1.05rem;font-weight:700;color:#4fc3f7;
               border-bottom:1px solid #1e4d7b;padding-bottom:4px;
               margin:1rem 0 .6rem}
.winner-banner{background:linear-gradient(135deg,#e65100,#bf360c);
               border-radius:14px;padding:1.5rem;text-align:center;
               margin:1rem 0}
.winner-banner h2{margin:0 0 4px;font-size:2rem;color:white}
.winner-banner p{margin:0;color:#ffccbc;font-size:1rem}
</style>""", unsafe_allow_html=True)

st.markdown("""
<div class="ph">
  <h2>🏏 Live Cricket</h2>
  <p>Score matches live · Watch ongoing games</p>
</div>""", unsafe_allow_html=True)

tab_watch, tab_score = st.tabs(["📺 Live Watch", "🏏 Score a Match"])

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — LIVE WATCH
# ══════════════════════════════════════════════════════════════════════════════
with tab_watch:
    st.markdown("<div class='section-title'>🔴 Ongoing Matches</div>",
                unsafe_allow_html=True)

    live = sc.get_live_matches()
    if not live:
        st.info("No live matches at the moment. Come back when a match is in progress!")
    else:
        for m in live:
            with st.expander(
                f"🔴 {m['team_a']} vs {m['team_b']}  "
                f"| {m['ground']} | {m['date']} | {m['overs']} overs"
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class='score-panel'>
                      <div class='team-label'>{m['team_a']}</div>
                      <div class='score-big'>{m.get('team_a_score',0)}/{m.get('team_a_wickets',0)}</div>
                    </div>""", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class='score-panel'>
                      <div class='team-label'>{m['team_b']}</div>
                      <div class='score-big'>{m.get('team_b_score',0)}/{m.get('team_b_wickets',0)}</div>
                    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div class='section-title'>✅ Completed Matches</div>",
                unsafe_allow_html=True)
    completed = sc.get_completed_matches()
    if not completed:
        st.info("No completed matches yet.")
    else:
        for m in reversed(completed[-10:]):
            st.markdown(f"""
            <div class='match-card'>
              <div class='mc-title'>
                {m['team_a']} vs {m['team_b']}
                &nbsp;|&nbsp; 🏆 {m.get('winner','—')}
              </div>
              <div class='mc-detail'>
                📅 {m['date']} | 🏟️ {m.get('ground','—')} | {m['overs']} overs
              </div>
              <div class='mc-detail'>
                {m['team_a']}: {m.get('team_a_score',0)}/{m.get('team_a_wickets',0)}
                &nbsp;|&nbsp;
                {m['team_b']}: {m.get('team_b_score',0)}/{m.get('team_b_wickets',0)}
              </div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — SCORE A MATCH
# ══════════════════════════════════════════════════════════════════════════════
with tab_score:

    # Initialise match state keys
    for k, v in [
        ("match", None),
        ("scoring_step", "setup"),    # setup | toss | openers | scoring | innings2_setup | done
        ("need_new_batsman", False),
        ("need_new_bowler", False),
        ("match_done", False),
    ]:
        if k not in st.session_state:
            st.session_state[k] = v

    def reset_match():
        for k in ["match","scoring_step","need_new_batsman",
                  "need_new_bowler","match_done"]:
            st.session_state.pop(k, None)
        st.rerun()

    step = st.session_state.scoring_step

    # ── MATCH DONE / SUMMARY ──────────────────────────────────────────────────
    if step == "done" or st.session_state.match_done:
        match = st.session_state.match
        inn1  = match["innings"][0]
        inn2  = match["innings"][1] or {}
        wd    = match.get("winner_detail", f"Winner: {match.get('winner','?')}")

        st.markdown(f"""
        <div class='winner-banner'>
          <h2>🏆 Match Completed!</h2>
          <p>{wd}</p>
        </div>""", unsafe_allow_html=True)

        # Scorecard
        for i, inn in enumerate([inn1, inn2]):
            if not inn:
                continue
            st.markdown(f"<div class='section-title'>📋 {inn['team']} — "
                        f"{inn['score']}/{inn['wickets']} "
                        f"({inn.get('overs_done',0)}.{inn['balls']%6} ov)</div>",
                        unsafe_allow_html=True)

            # Batting
            bat_rows = []
            for name, p in inn.get("players",{}).items():
                sr = round(p["runs"]/p["balls"]*100,1) if p["balls"] else 0
                bat_rows.append({
                    "Batsman": name,
                    "Runs": p["runs"],
                    "Balls": p["balls"],
                    "4s": p.get("fours",0),
                    "6s": p.get("sixes",0),
                    "SR": sr,
                    "Status": "Out" if p.get("out") else "Not Out",
                })
            if bat_rows:
                st.dataframe(pd.DataFrame(bat_rows), use_container_width=True,
                             hide_index=True)

            # Bowling
            bow_rows = []
            for name, b in inn.get("bowling",{}).items():
                ov = b.get("overs",0) + round(b.get("balls",0)/6, 1)
                eco = round(b["runs"]/ov, 2) if ov else 0
                bow_rows.append({
                    "Bowler": name,
                    "Overs": f"{b.get('overs',0)}.{b.get('balls',0)%6}",
                    "Wickets": b["wickets"],
                    "Runs": b["runs"],
                    "Economy": eco,
                })
            if bow_rows:
                st.dataframe(pd.DataFrame(bow_rows), use_container_width=True,
                             hide_index=True)

        # FOW
        for i, inn in enumerate([inn1, inn2]):
            if not inn:
                continue
            fow = inn.get("fall_of_wickets", [])
            if fow:
                st.markdown(f"**Fall of Wickets — {inn['team']}:** "
                            + "  ".join(f"{score}/{wk} ({pl})"
                                        for score, wk, pl in fow))

        # Download scorecard
        try:
            match_for_pdf = {
                "match_id": match["match_id"],
                "date": match.get("date",""),
                "ground": match.get("ground",""),
                "overs": match["total_overs"],
                "winner": match.get("winner",""),
                "innings": [
                    {
                        "team": inn["team"],
                        "score": inn["score"],
                        "wickets": inn["wickets"],
                        "players": [
                            {"name": n, **p}
                            for n, p in inn.get("players",{}).items()
                        ],
                        "bowling": [
                            {"name": n, **b}
                            for n, b in inn.get("bowling",{}).items()
                        ],
                    }
                    for inn in [inn1, inn2] if inn
                ]
            }
            pdf_bytes = generate_scorecard(match_for_pdf)
            st.download_button(
                "⬇️ Download Scorecard (PDF)",
                data=pdf_bytes,
                file_name=f"Scorecard_{match['match_id']}.pdf",
                mime="application/pdf",
                type="primary"
            )
        except Exception as e:
            st.info(f"Scorecard ready. PDF generation note: {e}")

        if st.button("🔁 Start New Match", type="secondary"):
            reset_match()
        st.stop()

    # ── STEP: SETUP ──────────────────────────────────────────────────────────
    if step == "setup":
        st.markdown("### ⚙️ Match Setup")
        col1, col2 = st.columns(2)
        with col1:
            team_a = st.text_input("Team A Name",
                                   value=st.session_state.get("linked_name","Team A"),
                                   key="s_team_a")
            team_b = st.text_input("Team B Name", value="Team B", key="s_team_b")
            overs  = st.selectbox("Overs", [2, 20, 50], key="s_overs",
                                  help="2 overs = demo match")
        with col2:
            ground_path = os.path.join(DATA_DIR, "Ground_clean_dataset.csv")
            gdf = pd.read_csv(ground_path)
            grounds_list = ["(No ground)"] + sorted(gdf["Ground Name"].dropna().unique())
            ground = st.selectbox("Ground", grounds_list, key="s_ground")
            match_date = st.date_input("Match Date", value=datetime.date.today(),
                                       key="s_date")

        if st.button("➡️ Next: Toss", type="primary"):
            if not team_a.strip() or not team_b.strip():
                st.error("Please enter both team names.")
            else:
                st.session_state._setup = {
                    "team_a": team_a.strip(),
                    "team_b": team_b.strip(),
                    "overs": int(overs),
                    "ground": ground if ground != "(No ground)" else "",
                    "date": str(match_date),
                }
                st.session_state.scoring_step = "toss"
                st.rerun()

    # ── STEP: TOSS ────────────────────────────────────────────────────────────
    elif step == "toss":
        s = st.session_state._setup
        st.markdown(f"### 🪙 Toss — {s['team_a']} vs {s['team_b']}")
        toss_winner = st.radio("Who won the toss?", [s["team_a"], s["team_b"]],
                               key="s_toss_w")
        toss_choice = st.radio("They choose to…", ["Bat", "Field"],
                               horizontal=True, key="s_toss_c")
        if st.button("➡️ Next: Opening Players", type="primary"):
            st.session_state._toss = {
                "toss_winner": toss_winner,
                "toss_choice": toss_choice,
            }
            st.session_state.scoring_step = "openers"
            st.rerun()

    # ── STEP: OPENERS ─────────────────────────────────────────────────────────
    elif step == "openers":
        s = st.session_state._setup
        t = st.session_state._toss
        batting_first = t["toss_winner"] if t["toss_choice"]=="Bat" else (
            s["team_b"] if t["toss_winner"]==s["team_a"] else s["team_a"]
        )
        bowling_first = s["team_b"] if batting_first==s["team_a"] else s["team_a"]

        st.markdown(f"### 🏏 Opening Players")
        st.info(f"**{batting_first}** bats first. **{bowling_first}** bowls first.")

        col1, col2 = st.columns(2)
        with col1:
            opener1 = st.text_input("Opening Batsman 1 (Striker)", key="o1")
            opener2 = st.text_input("Opening Batsman 2 (Non-Striker)", key="o2")
        with col2:
            bowler1 = st.text_input("Opening Bowler", key="ob1")

        if st.button("🏏 Start Match!", type="primary"):
            if not all([opener1.strip(), opener2.strip(), bowler1.strip()]):
                st.error("Please enter all player names.")
            else:
                match = sc.new_match(
                    s["team_a"], s["team_b"], s["ground"],
                    s["overs"], t["toss_winner"], t["toss_choice"]
                )
                match["date"] = s["date"]
                inn = sc.current_inning(match)
                inn["current_batsmen"] = [opener1.strip(), opener2.strip()]
                inn["current_bowler"]  = bowler1.strip()
                # Init player records
                for nm in [opener1.strip(), opener2.strip()]:
                    inn["players"][nm] = {"runs":0,"balls":0,"fours":0,"sixes":0,"out":False}
                inn["bowling"][bowler1.strip()] = {"overs":0,"balls":0,"runs":0,
                                                    "wickets":0,"maidens":0}
                st.session_state.match = match
                st.session_state.scoring_step = "scoring"
                st.rerun()

    # ── STEP: SCORING ─────────────────────────────────────────────────────────
    elif step == "scoring":
        match = st.session_state.match
        inn   = sc.current_inning(match)
        overs = match["total_overs"]

        # Check inning completion
        if sc.inning_complete(match):
            if match["current_inning"] == 1:
                st.session_state.scoring_step = "innings2_setup"
                st.rerun()
            else:
                sc.finish_match(match)
                st.session_state.scoring_step = "done"
                st.session_state.match_done   = True
                st.rerun()

        batting_team = inn["team"]
        bowling_team = inn["bowling_team"]
        striker      = inn["current_batsmen"][0] if inn["current_batsmen"] else "?"
        non_striker  = inn["current_batsmen"][1] if len(inn["current_batsmen"])>1 else "?"
        bowler       = inn["current_bowler"] or "?"
        balls_in_ov  = sc.balls_in_over(inn)
        over_num     = sc.over_number(inn)

        # Target for 2nd inning
        target_html = ""
        if match["current_inning"] == 2:
            target    = match["innings"][0]["score"] + 1
            needed    = target - inn["score"]
            balls_rem = (overs - inn["overs_done"]) * 6 - balls_in_ov
            target_html = (f"<div style='color:#ffd54f;font-size:.9rem;margin-top:4px'>"
                           f"Target: {target} | Need: {needed} from {balls_rem} balls</div>")

        # Scoreboard
        col_score, col_bat, col_bowl = st.columns([2, 2, 2])

        with col_score:
            st.markdown(f"""
            <div class='score-panel'>
              <div class='team-label'>🏏 {batting_team} (Inning {match['current_inning']})</div>
              <div class='score-big'>{inn['score']}/{inn['wickets']}</div>
              <div class='score-sub'>Over {inn['overs_done']}.{balls_in_ov} / {overs}</div>
              {target_html}
              <div class='over-info'>
                🎯 Bowling: <strong>{bowling_team}</strong>
              </div>
            </div>""", unsafe_allow_html=True)

            # Last 6 balls this over
            last_balls = inn["balls_log"][-balls_in_ov:] if balls_in_ov else []
            dots = ""
            for b in last_balls:
                ev = b["event"]
                if ev.startswith("run_"):
                    r = ev.split("_")[1]
                    cls = f"ball-{r}"
                    lbl = r
                elif ev == "wicket":
                    cls, lbl = "ball-W", "W"
                elif ev in ("wide","noball"):
                    cls, lbl = "ball-X", ev[0].upper()
                else:
                    cls, lbl = "ball-X", "E"
                dots += f'<span class="ball-dot {cls}">{lbl}</span>'
            st.markdown(f"<div style='margin-top:.5rem'>"
                        f"<div style='font-size:.8rem;color:#90caf9;margin-bottom:4px'>"
                        f"This over:</div>"
                        f"<div class='ball-log'>{dots}</div></div>",
                        unsafe_allow_html=True)

        with col_bat:
            st.markdown(f"<div class='section-title'>🏏 Batting</div>",
                        unsafe_allow_html=True)
            for name, p in inn["players"].items():
                if p.get("out"):
                    continue
                is_str = (name == striker)
                cls = "bat-row bat-active" if is_str else "bat-row"
                indicator = "⚡" if is_str else "&nbsp;&nbsp;"
                sr = round(p["runs"]/p["balls"]*100,1) if p["balls"] else 0
                st.markdown(f"""
                <div class='{cls}'>
                  <span>{indicator} {name}{'*' if is_str else ''}</span>
                  <span><strong>{p['runs']}</strong>({p['balls']}) 4s:{p['fours']} 6s:{p['sixes']} SR:{sr}</span>
                </div>""", unsafe_allow_html=True)

        with col_bowl:
            st.markdown(f"<div class='section-title'>🎯 Bowling</div>",
                        unsafe_allow_html=True)
            for name, b in inn["bowling"].items():
                is_cur = (name == bowler)
                cls = "bow-row bat-active" if is_cur else "bow-row"
                ov = f"{b['overs']}.{b['balls']%6}"
                eco = round(b["runs"]/b["overs"],2) if b["overs"] else 0
                st.markdown(f"""
                <div class='{cls}'>
                  <span>{'🎯 ' if is_cur else ''}{name}</span>
                  <span>{ov}ov | {b['wickets']}W | {b['runs']}R | Eco:{eco}</span>
                </div>""", unsafe_allow_html=True)

        # ── Prompts for new bowler / next batsman ────────────────────────────
        if st.session_state.get("need_new_bowler"):
            with st.form("new_bowler_form"):
                st.warning(f"End of Over {inn['overs_done']}. Enter new bowler:")
                new_bowl = st.text_input("New Bowler Name", key="nb_name")
                if st.form_submit_button("✅ Set Bowler"):
                    if new_bowl.strip():
                        inn["current_bowler"] = new_bowl.strip()
                        if new_bowl.strip() not in inn["bowling"]:
                            inn["bowling"][new_bowl.strip()] = {
                                "overs":0,"balls":0,"runs":0,"wickets":0,"maidens":0
                            }
                        st.session_state.need_new_bowler = False
                        st.rerun()
            st.stop()

        if st.session_state.get("need_new_batsman"):
            with st.form("new_bat_form"):
                st.warning("Wicket! Enter the next batsman:")
                new_bat = st.text_input("Next Batsman Name", key="nbat_name")
                if st.form_submit_button("✅ Send In Batsman"):
                    if new_bat.strip():
                        inn["current_batsmen"].insert(0, new_bat.strip())
                        inn["players"][new_bat.strip()] = {
                            "runs":0,"balls":0,"fours":0,"sixes":0,"out":False
                        }
                        st.session_state.need_new_batsman = False
                        st.rerun()
            st.stop()

        # ── Scoring buttons ──────────────────────────────────────────────────
        st.markdown("---")
        st.markdown(f"<div style='text-align:center;color:#90caf9;margin-bottom:.5rem'>"
                    f"🎯 {bowler} bowling to ⚡ {striker}</div>",
                    unsafe_allow_html=True)

        def do_delivery(event, extras_runs=0):
            result = sc.deliver(match, event, extras_runs)
            if result.get("wicket"):
                st.session_state.need_new_batsman = (inn["wickets"] < 10)
            if result.get("new_over"):
                st.session_state.need_new_bowler = True
            st.rerun()

        # Runs
        bcols = st.columns(7)
        labels = [("0", "btn-0"), ("1", "btn-1"), ("2", "btn-2"),
                  ("3", "btn-3"), ("4 ▪ FOUR", "btn-4"),
                  ("6 ▪ SIX", "btn-6"), ("W ▪ OUT", "btn-W")]
        for i, (lbl, cls) in enumerate(labels):
            with bcols[i]:
                if st.button(lbl, key=f"run_{i}", use_container_width=True):
                    if lbl.startswith("W"):
                        do_delivery("wicket")
                    elif "4" in lbl:
                        do_delivery("run_4")
                    elif "6" in lbl:
                        do_delivery("run_6")
                    else:
                        do_delivery(f"run_{lbl}")

        # Extras
        ecols = st.columns(4)
        extras = [("Wide", "wide"), ("No Ball", "noball"),
                  ("Bye +1", "bye_1"), ("Leg Bye +1", "legbye_1")]
        for i, (lbl, ev) in enumerate(extras):
            with ecols[i]:
                if st.button(lbl, key=f"ex_{i}", use_container_width=True):
                    do_delivery(ev)

        # FOW info
        fow = inn.get("fall_of_wickets", [])
        if fow:
            st.markdown("<div style='font-size:.8rem;color:#90caf9;margin-top:.5rem'>"
                        "Fall of Wickets: " +
                        " | ".join(f"{sc}/{wk} ({pl})" for sc,wk,pl in fow) +
                        "</div>", unsafe_allow_html=True)

    # ── STEP: 2ND INNING SETUP ────────────────────────────────────────────────
    elif step == "innings2_setup":
        match = st.session_state.match
        inn1  = match["innings"][0]

        batting_team2 = match["bowling_first"]
        bowling_team2 = match["batting_first"]
        target        = inn1["score"] + 1

        st.markdown(f"""
        <div class='winner-banner' style='background:linear-gradient(135deg,#1a237e,#283593)'>
          <h2>⏱️ Innings Break</h2>
          <p>{inn1['team']}: {inn1['score']}/{inn1['wickets']}</p>
          <p style='margin-top:6px;font-size:1.1rem;color:#c5cae9'>
            {batting_team2} needs <strong>{target}</strong> to win
          </p>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"### 🏏 Second Innings — {batting_team2} vs {bowling_team2}")
        col1, col2 = st.columns(2)
        with col1:
            opener1_2 = st.text_input("Opening Batsman 1 (Striker)", key="o1_2")
            opener2_2 = st.text_input("Opening Batsman 2 (Non-Striker)", key="o2_2")
        with col2:
            bowler1_2 = st.text_input("Opening Bowler", key="ob1_2")

        if st.button("🏏 Start Second Innings!", type="primary"):
            if not all([opener1_2.strip(), opener2_2.strip(), bowler1_2.strip()]):
                st.error("Please enter all player names.")
            else:
                sc.start_second_inning(
                    match,
                    [opener1_2.strip(), opener2_2.strip()],
                    bowler1_2.strip()
                )
                st.session_state.scoring_step = "scoring"
                st.session_state.need_new_batsman = False
                st.session_state.need_new_bowler  = False
                st.rerun()