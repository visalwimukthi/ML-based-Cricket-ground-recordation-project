import os
import pandas as pd
import uuid

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
BOOK_FILE = os.path.join(DATA_DIR, "bookings.csv")
PAY_FILE = os.path.join(DATA_DIR, "payments.csv")

def get_bookings_for_month(year, month):
    df = pd.read_csv(BOOK_FILE)
    df["date"] = pd.to_datetime(df["date"], errors='coerce')
    return df[(df["date"].dt.year == year) & (df["date"].dt.month == month)]

def is_available(ground_name, date_str):
    df = pd.read_csv(BOOK_FILE)
    clash = df[(df["ground_name"] == ground_name) & (df["date"] == date_str)]
    return clash.empty

def book_ground(ground_name, date_str, team_name, timeslot):
    new_book = pd.DataFrame([{"ground_name": ground_name, "date": date_str, "booked_by": team_name, "timeslot": timeslot}])
    new_book.to_csv(BOOK_FILE, mode='a', header=False, index=False)

def save_payment(team_name, ground_name, date_str, timeslot, amount, method):
    receipt_id = "REC-" + str(uuid.uuid4())[:8].upper()
    new_pay = pd.DataFrame([{"receipt_id": receipt_id, "team_name": team_name, "ground_name": ground_name, "date": date_str, "timeslot": timeslot, "amount": amount, "method": method}])
    new_pay.to_csv(PAY_FILE, mode='a', header=False, index=False)
    return receipt_id