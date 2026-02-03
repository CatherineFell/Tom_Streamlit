import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.title("🎤 Gig Inputs")

# -----------------------------
# Google Sheets setup
# -----------------------------
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

client = gspread.authorize(creds)
sheet = client.open("streamlit_inputs").sheet1  # MUST match your sheet name

# -----------------------------
# Optional: load existing data
# -----------------------------
rows = sheet.get_all_records()
df = pd.DataFrame(rows)

# -----------------------------
# Gig input form
# -----------------------------
with st.form("gig_form"):
    gig_date = st.date_input("Gig Date")
    booking_date = st.date_input("Booking Date")
    gig_type = st.selectbox(
        "Gig Type",
        ["Bar", "Wedding", "Festival", "Private Event", "Other"]
    )
    pay_amount = st.number_input("Pay Amount ($)", min_value=0.0)
    hours_played = st.number_input("Hours Played", min_value=0.1)
    travel_cost = st.number_input("Travel Cost ($)", min_value=0.0)
    crowd_size = st.number_input("Crowd Size", min_value=0, step=1)

    submitted = st.form_submit_button("Add Gig")

# -----------------------------
# Save to Google Sheets
# -----------------------------
if submitted:
    sheet.append_row([
        gig_date.isoformat(),
        booking_date.isoformat(),
        gig_type,
        pay_amount,
        hours_played,
        travel_cost,
        crowd_size,
        gig_date.year,
        datetime.utcnow().isoformat()
    ])

    st.success("✅ Gig added successfully!")

# -----------------------------
# Optional: show saved gigs
# -----------------------------
if not df.empty:
    st.subheader("Saved Gigs")
    st.dataframe(df)

