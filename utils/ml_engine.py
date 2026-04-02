import os
import joblib
import pandas as pd

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def recommend(city=None, district=None, province=None, pitch=None, ground_type=None, max_price=None, team_name=None, weather_label="Clear", top_n=5, **kwargs):
    # 1. Load Artifacts
    try:
        model = joblib.load(os.path.join(ARTIFACTS_DIR, "rf_model.joblib"))
        scaler = joblib.load(os.path.join(ARTIFACTS_DIR, "scaler.joblib"))
        features = joblib.load(os.path.join(ARTIFACTS_DIR, "model_features1.joblib"))
    except FileNotFoundError:
        return pd.DataFrame() 

    # 2. Load Data
    data = pd.read_csv(os.path.join(DATA_DIR, "Ground_clean_dataset.csv"))
    team_stats = pd.read_csv(os.path.join(DATA_DIR, "team_stats.csv"))
    
    # 3. Apply Strict Filters (Matches Notebook Logic)
    if city: 
        data = data[data["City"].astype(str).str.lower().str.strip() == city.lower().strip()]
    if district: 
        data = data[data["District"].astype(str).str.lower().str.strip() == district.lower().strip()]
    if province: 
        data = data[data["Province"].astype(str).str.lower().str.strip() == province.lower().strip()]
    if pitch and pitch != "Any": 
        data = data[data["Pitch"].astype(str).str.lower().str.strip() == pitch.lower().strip()]
    if ground_type and ground_type != "Any": 
        data = data[data["Ground Type"].astype(str).str.lower().str.strip() == ground_type.lower().strip()]
    if max_price: 
        data = data[data["Price (LKR)"] <= max_price]
        
    # Facility Filters
    if kwargs.get("needs_lights"): data = data[data["Lights"].astype(str).str.upper().str.strip() == "YES"]
    if kwargs.get("needs_parking"): data = data[data["Parking"].astype(str).str.upper().str.strip() == "YES"]
    if kwargs.get("needs_washrooms"): data = data[data["Washrooms"].astype(str).str.upper().str.strip() == "YES"]
    if kwargs.get("needs_pavilion"): data = data[data["Pavilion"].astype(str).str.upper().str.strip() == "YES"]
    if kwargs.get("needs_scoreboard"): data = data[data["Scoreboard"].astype(str).str.upper().str.strip() == "YES"]

    if data.empty: 
        return pd.DataFrame()

    # Map Yes/No to 1/0 for the ML Model (Exactly how it was trained)
    ml_data = data.copy()
    for c in ["Lights", "Parking", "Washrooms", "Pavilion", "Scoreboard"]:
        if c in ml_data.columns:
            ml_data[c] = ml_data[c].astype(str).str.upper().str.strip().map({"YES": 1, "NO": 0})

    # 4. Preprocess for ML
    categorical_cols = ["City", "District", "Province", "Ground Type", "Pitch"]
    data_encoded = pd.get_dummies(ml_data, columns=categorical_cols)
    data_encoded.columns = data_encoded.columns.str.lower().str.replace(" ", "_")
    
    # Ensure all columns match model features exactly, fill missing with 0
    for col in features:
        if col not in data_encoded.columns:
            data_encoded[col] = 0
    data_encoded = data_encoded[features]
    
    # Scale and Predict
    X_scaled = scaler.transform(data_encoded)
    scores = model.predict_proba(X_scaled)[:, 1]
    data["ml_score"] = scores
    
    # 5. Calculate Team Win Rate
    data["win_rate"] = 0.0
    if team_name:
        ts = team_stats[team_stats["team_name"] == team_name]
        for idx, row in data.iterrows():
            g_stat = ts[ts["ground_name"] == row["Ground Name"]]
            if not g_stat.empty:
                played = g_stat.iloc[0]["matches_played"]
                if played > 0:
                    data.at[idx, "win_rate"] = g_stat.iloc[0]["wins"] / played

    # 6. Hybrid Score calculation
    weather_multiplier = 0.0 if "rain" in weather_label.lower() else (0.7 if "cloud" in weather_label.lower() else 1.0)
    data["weather_score"] = weather_multiplier
    data["final_score"] = (data["ml_score"] * 0.5) + (data["win_rate"] * 0.3) + (data["weather_score"] * 0.2)
    
    return data.sort_values(by="final_score", ascending=False).head(top_n)