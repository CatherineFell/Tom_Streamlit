import streamlit as st
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
        [
            "Pub",
            "Wedding",
            "Corporate",
            "Festival Original",
            "Festival Tribute",
            "Original",
            "Tribute",
            "Other",
        ],
    )

    gig_fee = st.number_input("Gig Fee ($)", min_value=0.0)
    stage_time = st.number_input("Stage Time (hours)", min_value=0.0, step=0.25)
    time_away_from_home = st.number_input(
        "Time Away From Home (hours)", min_value=0.0, step=0.5
    )

    travel_cost = st.number_input("Travel Cost ($)", min_value=0.0)

    gig_quality = st.selectbox("Gig Quality", ["High", "Medium", "Low"])
    gig_enjoyment = st.slider("Gig Enjoyment", 1, 5, 3)
    connections_potential = st.slider("Connections Potential", 1, 5, 3)

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
        float(gig_fee),
        float(stage_time),
        float(time_away_from_home),
        float(travel_cost),
        gig_quality,
        int(gig_enjoyment),
        int(connections_potential),
        int(crowd_size),
        gig_date.year,
    ]

    sheet.append_row(new_row)

    # Clear cached reads in visuals page
    st.cache_data.clear()

    st.success("✅ Gig added successfully!")


