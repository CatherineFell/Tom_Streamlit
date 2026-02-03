import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

st.title("🎤 Gig Inputs")

# -----------------------------
# Google Sheets setup
# -----------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES,
)

client = gspread.authorize(creds)

# Use spreadsheet ID (more reliable than name)
SHEET_ID = "1--vUOkH21zM5nsTwBuqlNv-9z-JJALCo5QSU-7OzUjA"
sheet = client.open_by_key(SHEET_ID).sheet1

# -----------------------------
# Input form
# -----------------------------
with st.form("gig_form"):
    gig_date = st.date_input("Gig Date", value=date.today())
    booking_date = st.date_input("Booking Date", value=date.today())
    gig_type = st.selectbox(
        "Gig Type",
        ["Bar", "Wedding", "Festival", "Private Event", "Other"],
    )
    pay_amount = st.number_input("Pay Amount ($)", min_value=0.0)
    hours_played = st.number_input("Hours Played", min_value=0.1)
    travel_cost = st.number_input("Travel Cost ($)", min_value=0.0)
    crowd_size = st.number_input("Crowd Size", min_value=0, step=1)

    submitted = st.form_submit_button("Add Gig")

# -----------------------------
# Submit handler
# -----------------------------
if submitted:
    new_row = [
        gig_date.isoformat(),
        booking_date.isoformat(),
        gig_type,
        float(pay_amount),
        float(hours_played),
        float(travel_cost),
        int(crowd_size),
        gig_date.year,
    ]

    sheet.append_row(new_row)

    # Clear cached reads in Visuals
    st.cache_data.clear()

    st.success("✅ Gig added successfully!")

