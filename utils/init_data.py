import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def init_all():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. Define the files and their exact columns
    files = {
        "users.csv": ["username", "password", "role", "linked_name"],
        "teams.csv": ["team_name", "captain", "vice_captain", "contact"],
        "bookings.csv": ["ground_name", "date", "booked_by", "timeslot"],
        "payments.csv": ["receipt_id", "team_name", "ground_name", "date", "timeslot", "amount", "method"],
        "match_results.csv": ["match_id", "team_a", "team_b", "date", "ground", "overs", "winner", "team_a_score", "team_a_wickets", "team_b_score", "team_b_wickets"],
        "team_stats.csv": ["team_name", "ground_name", "matches_played", "wins"]
    }
    
    # 2. Expanded Historical Data for Realistic ML Predictions
    historical_stats = [
        # Royal College XI
        ["Royal College XI","Colombo Sinhalese Sports Club Ground",10,7],
        ["Royal College XI","Colombo Nondescripts Cricket Club Ground",8,5],
        ["Royal College XI","Colombo Colts Cricket Club Ground",7,4],
        ["Royal College XI","Colombo City Cricket Park",6,3],
        ["Royal College XI","Colombo P Sara Oval",6,3],
        
        # St. Joseph's College XI
        ["St. Joseph's College XI","Colombo Sinhalese Sports Club Ground",10,7],
        ["St. Joseph's College XI","Colombo Nondescripts Cricket Club Ground",8,4],
        ["St. Joseph's College XI","Colombo City Cricket Park",7,3],
        ["St. Joseph's College XI","Colombo Colts Cricket Club Ground",6,2],
        ["St. Joseph's College XI","Colombo P Sara Oval",7,3],
        
        # Colombo CC
        ["Colombo CC","Colombo Sinhalese Sports Club Ground",12,9],
        ["Colombo CC","Colombo Nondescripts Cricket Club Ground",10,7],
        ["Colombo CC","Colombo Colts Cricket Club Ground",9,6],
        ["Colombo CC","Colombo P Sara Oval",8,5],
        ["Colombo CC","Panadura Municipal Cricket Ground",7,3],
        
        # Sinhalese SC
        ["Sinhalese SC","Colombo Sinhalese Sports Club Ground",15,12],
        ["Sinhalese SC","Colombo Nondescripts Cricket Club Ground",12,8],
        ["Sinhalese SC","Colombo Colts Cricket Club Ground",10,7],
        ["Sinhalese SC","Colombo P Sara Oval",9,6],
        
        # Nondescripts Cricket Club (NCC)
        ["NCC Club","Colombo Nondescripts Cricket Club Ground",14,11],
        ["NCC Club","Colombo Sinhalese Sports Club Ground",10,6],
        ["NCC Club","Colombo Colts Cricket Club Ground",9,5],
        ["NCC Club","Colombo P Sara Oval",9,5],
        ["NCC Club","Colombo Bloomfield Cricket & Athletic Club Ground",8,4],
        
        # Moors Sports Club
        ["Moors Sports Club","Colombo Moors Sports Club Ground",12,9],
        ["Moors Sports Club","Colombo Sinhalese Sports Club Ground",8,4],
        ["Moors Sports Club","Colombo Colts Cricket Club Ground",7,3],
        ["Moors Sports Club","Colombo City Cricket Park",8,5],
        
        # Tamil Union C&AC
        ["Tamil Union C&AC","Colombo P Sara Oval",14,10],
        ["Tamil Union C&AC","Colombo Sinhalese Sports Club Ground",9,4],
        ["Tamil Union C&AC","Colombo Nondescripts Cricket Club Ground",8,3],
        ["Tamil Union C&AC","Colombo Colts Cricket Club Ground",7,3],
        
        # Ananda College XI
        ["Ananda College XI","Colombo Ananda College Ground",10,8],
        ["Ananda College XI","Colombo Sinhalese Sports Club Ground",9,5],
        ["Ananda College XI","Colombo Nondescripts Cricket Club Ground",7,3],
        ["Ananda College XI","Colombo Colts Cricket Club Ground",8,4],
        
        # Nalanda College XI
        ["Nalanda College XI","Colombo Nalanda College Ground",10,7],
        ["Nalanda College XI","Colombo Sinhalese Sports Club Ground",8,4],
        ["Nalanda College XI","Colombo Nondescripts Cricket Club Ground",7,3],
        ["Nalanda College XI","Colombo Colts Cricket Club Ground",9,5],
        
        # Piliyandala CC (Local Team)
        ["Piliyandala CC","Piliyandala Public Ground",10,7],
        ["Piliyandala CC","Piliyandala Central College Ground",8,5],
        ["Piliyandala CC","Piliyandala Sports Complex",6,4],
        ["Piliyandala CC","Colombo City Cricket Park",5,2],
        ["Piliyandala CC","Moratuwa Urban Council Ground",4,2],
        
        # Moratuwa SC
        ["Moratuwa SC","Moratuwa Urban Council Ground",10,7],
        ["Moratuwa SC","Panadura Municipal Cricket Ground",7,3],
        ["Moratuwa SC","Kalutara Municipal Sports Ground",8,4],
        ["Moratuwa SC","Colombo Sinhalese Sports Club Ground",6,3]
    ]

    # 3. Create files if they are missing and inject demo data
    for file, cols in files.items():
        path = os.path.join(DATA_DIR, file)
        
        if not os.path.exists(path):
            df = pd.DataFrame(columns=cols)
            
            # Inject demo accounts
            if file == "users.csv":
                df = pd.DataFrame([
                    {"username": "royal_xi", "password": "password123", "role": "team", "linked_name": "Royal College XI"},
                    {"username": "colombo_cc", "password": "password123", "role": "team", "linked_name": "Colombo CC"},
                    {"username": "piliyandala_cc", "password": "1234", "role": "team", "linked_name": "Piliyandala CC"},
                    {"username": "ncc_manager", "password": "password123", "role": "ground_manager", "linked_name": "Colombo Nondescripts Cricket Club Ground"}
                ])
            
            # Inject demo team info
            elif file == "teams.csv":
                df = pd.DataFrame([
                    {"team_name": "Royal College XI", "captain": "Visal", "vice_captain": "Ravindu", "contact": "0771234567"},
                    {"team_name": "Colombo CC", "captain": "Mahela", "vice_captain": "Kumar", "contact": "0777654321"},
                    {"team_name": "Piliyandala CC", "captain": "Pasan", "vice_captain": "Thivina", "contact": "0776109329"}
                ])
                
            # Inject your expanded historical notebook data
            elif file == "team_stats.csv":
                df = pd.DataFrame(historical_stats, columns=cols)
                
            df.to_csv(path, index=False)