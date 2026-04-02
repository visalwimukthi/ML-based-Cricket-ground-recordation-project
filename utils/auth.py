import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
TEAMS_FILE = os.path.join(DATA_DIR, "teams.csv")

def login(username, password):
    # FIX: dtype=str forces Pandas to treat everything (like "1234") as text!
    df = pd.read_csv(USERS_FILE, dtype=str)
    user = df[(df['username'] == username) & (df['password'] == password)]
    if not user.empty:
        return user.iloc[0].to_dict()
    return None

def register_team(user, pwd, team, cap, vc, contact):
    df = pd.read_csv(USERS_FILE, dtype=str)
    if user in df['username'].values:
        return False, "Username already exists."
    
    new_user = pd.DataFrame([{"username": user, "password": pwd, "role": "team", "linked_name": team}])
    new_user.to_csv(USERS_FILE, mode='a', header=False, index=False)
    
    new_team = pd.DataFrame([{"team_name": team, "captain": cap, "vice_captain": vc, "contact": contact}])
    new_team.to_csv(TEAMS_FILE, mode='a', header=False, index=False)
    return True, "Team registered successfully!"

def register_ground_manager(user, pwd, ground_name, contact, city, dist, prov, gtype, pitch, length, width, lights, park, wash, pav, score, rooms, pcap, price):
    df = pd.read_csv(USERS_FILE, dtype=str)
    if user in df['username'].values:
        return False, "Username already exists."
        
    new_user = pd.DataFrame([{"username": user, "password": pwd, "role": "ground_manager", "linked_name": ground_name}])
    new_user.to_csv(USERS_FILE, mode='a', header=False, index=False)
    return True, "Ground registered successfully!"

def get_team_info(team_name):
    df = pd.read_csv(TEAMS_FILE, dtype=str)
    team = df[df['team_name'] == team_name]
    return team.iloc[0].to_dict() if not team.empty else {}