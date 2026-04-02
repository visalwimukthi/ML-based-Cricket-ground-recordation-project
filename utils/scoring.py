import os, uuid
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
RESULTS_FILE = os.path.join(DATA_DIR, "match_results.csv")
TEAM_STATS_FILE = os.path.join(DATA_DIR, "team_stats.csv")

def get_live_matches():
    return [] 

def get_completed_matches():
    if not os.path.exists(RESULTS_FILE):
        return []
    df = pd.read_csv(RESULTS_FILE)
    return df.to_dict('records')

def new_match(team_a, team_b, ground, overs, toss_winner, toss_choice):
    return {
        "match_id": str(uuid.uuid4())[:8],
        "team_a": team_a, "team_b": team_b, "ground": ground, "total_overs": overs,
        "toss_winner": toss_winner, "toss_choice": toss_choice,
        "current_inning": 1,
        "batting_first": toss_winner if toss_choice == "Bat" else (team_b if toss_winner == team_a else team_a),
        "bowling_first": team_b if (toss_winner if toss_choice == "Bat" else (team_b if toss_winner == team_a else team_a)) == team_a else team_a,
        "innings": [
            {"team": toss_winner if toss_choice == "Bat" else (team_b if toss_winner == team_a else team_a), "bowling_team": team_b if (toss_winner if toss_choice == "Bat" else (team_b if toss_winner == team_a else team_a)) == team_a else team_a, "score": 0, "wickets": 0, "balls": 0, "overs_done": 0, "players": {}, "bowling": {}, "current_batsmen": [], "current_bowler": "", "balls_log": [], "fall_of_wickets": []},
            None
        ]
    }

def current_inning(match):
    return match["innings"][match["current_inning"] - 1]

def balls_in_over(inn):
    return inn["balls"] % 6

def over_number(inn):
    return (inn["balls"] // 6) + 1

def deliver(match, event, extras=0):
    inn = current_inning(match)
    batsman = inn["current_batsmen"][0]
    bowler = inn["current_bowler"]
    
    result = {"wicket": False, "new_over": False}
    inn["balls_log"].append({"event": event, "batsman": batsman, "bowler": bowler})
    
    if event == "wicket":
        inn["wickets"] += 1
        inn["players"][batsman]["out"] = True
        inn["bowling"][bowler]["wickets"] += 1
        inn["current_batsmen"].pop(0) 
        inn["fall_of_wickets"].append((inn["score"], inn["wickets"], batsman))
        inn["balls"] += 1
        inn["players"][batsman]["balls"] += 1
        result["wicket"] = True
    elif event.startswith("run_"):
        runs = int(event.split("_")[1])
        inn["score"] += runs
        inn["players"][batsman]["runs"] += runs
        inn["players"][batsman]["balls"] += 1
        inn["bowling"][bowler]["runs"] += runs
        if runs == 4: inn["players"][batsman]["fours"] += 1
        if runs == 6: inn["players"][batsman]["sixes"] += 1
        inn["balls"] += 1
        if runs % 2 != 0: inn["current_batsmen"].reverse() 
    elif event in ["wide", "noball"]:
        inn["score"] += 1
        inn["bowling"][bowler]["runs"] += 1

    inn["overs_done"] = inn["balls"] // 6
    inn["bowling"][bowler]["overs"] = inn["overs_done"]
    inn["bowling"][bowler]["balls"] = balls_in_over(inn)

    if balls_in_over(inn) == 0 and event not in ["wide", "noball"]:
        inn["current_batsmen"].reverse() 
        result["new_over"] = True
        
    return result

def inning_complete(match):
    inn = current_inning(match)
    return inn["wickets"] == 10 or inn["overs_done"] >= match["total_overs"]

def start_second_inning(match, openers, bowler):
    match["current_inning"] = 2
    match["innings"][1] = {
        "team": match["bowling_first"], "bowling_team": match["batting_first"], "score": 0, "wickets": 0, "balls": 0, "overs_done": 0,
        "players": {openers[0]: {"runs":0,"balls":0,"fours":0,"sixes":0,"out":False}, openers[1]: {"runs":0,"balls":0,"fours":0,"sixes":0,"out":False}},
        "bowling": {bowler: {"overs":0,"balls":0,"runs":0,"wickets":0,"maidens":0}},
        "current_batsmen": openers, "current_bowler": bowler, "balls_log": [], "fall_of_wickets": []
    }

def finish_match(match):
    inn1 = match["innings"][0]
    inn2 = match["innings"][1]
    
    if inn2["score"] > inn1["score"]: match["winner"] = inn2["team"]
    elif inn1["score"] > inn2["score"]: match["winner"] = inn1["team"]
    else: match["winner"] = "Tie"
    
    # 1. Save match details to results CSV
    df = pd.DataFrame([{"match_id": match["match_id"], "team_a": inn1["team"], "team_b": inn2["team"], "date": match.get("date",""), "ground": match.get("ground",""), "overs": match["total_overs"], "winner": match["winner"], "team_a_score": inn1["score"], "team_a_wickets": inn1["wickets"], "team_b_score": inn2["score"], "team_b_wickets": inn2["wickets"]}])
    df.to_csv(RESULTS_FILE, mode='a', header=False, index=False)

    # 2. Update team_stats.csv so dashboards update instantly!
    if os.path.exists(TEAM_STATS_FILE):
        ts_df = pd.read_csv(TEAM_STATS_FILE)
    else:
        ts_df = pd.DataFrame(columns=["team_name", "ground_name", "matches_played", "wins"])

    ground = match.get("ground", "")
    winner = match["winner"]

    for team in [inn1["team"], inn2["team"]]:
        mask = (ts_df["team_name"] == team) & (ts_df["ground_name"] == ground)
        
        if mask.any():
            # Team has played here before, update their stats
            idx = ts_df[mask].index[0]
            ts_df.at[idx, "matches_played"] = float(ts_df.at[idx, "matches_played"]) + 1.0
            if team == winner:
                ts_df.at[idx, "wins"] = float(ts_df.at[idx, "wins"]) + 1.0
        else:
            # Team's first time playing here, add a new row
            new_row = {
                "team_name": team, 
                "ground_name": ground, 
                "matches_played": 1.0, 
                "wins": 1.0 if team == winner else 0.0
            }
            ts_df = pd.concat([ts_df, pd.DataFrame([new_row])], ignore_index=True)

    # Save the updated stats back
    ts_df.to_csv(TEAM_STATS_FILE, index=False)