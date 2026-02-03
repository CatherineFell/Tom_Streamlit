import streamlit as st
import pandas as pd
from pathlib import Path

st.title("🎤 Gig Inputs")


DATA_PATH = Path("data/gigs.csv")

# Make sure the directory exists
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)


if DATA_PATH.exists():
    df = pd.read_csv(DATA_PATH, parse_dates=["gig_date", "booking_date"])
else:
    df = pd.DataFrame(columns=[
        "gig_date",
        "booking_date",
        "gig_type",
        "pay_amount",
        "hours_played",
        "travel_cost",
        "crowd_size",
        "year"
    ])

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

if submitted:
    new_row = {
        "gig_date": gig_date,
        "booking_date": booking_date,
        "gig_type": gig_type,
        "pay_amount": pay_amount,
        "hours_played": hours_played,
        "travel_cost": travel_cost,
        "crowd_size": crowd_size,
        "year": gig_date.year
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DATA_PATH, index=False)

    st.success("✅ Gig added successfully!")

