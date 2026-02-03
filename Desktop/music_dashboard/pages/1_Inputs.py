import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from google.oauth2.service_account import Credentials
import datetime as dt

st.title("📊 Performance Visuals")

# -----------------------------
# Google Sheets setup
# -----------------------------
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"]
)

client = gspread.authorize(creds)
sheet = client.open("streamlit_inputs").sheet1

# -----------------------------
# Cached data loader (NEW)
# -----------------------------
@st.cache_data(ttl=300)  # cache for 5 minutes
def load_gigs_from_sheet():
    rows = sheet.get_all_records()
    return pd.DataFrame(rows)

# Optional manual refresh
if st.button("🔄 Refresh data"):
    st.cache_data.clear()

# -----------------------------
# Load data
# -----------------------------
df = load_gigs_from_sheet()

if df.empty:
    st.warning("No gigs yet. Add data first.")
    st.stop()

# -----------------------------
# Data cleaning
# -----------------------------
df["gig_date"] = pd.to_datetime(df["gig_date"], errors="coerce")
df = df.dropna(subset=["gig_date"])

df["pay_amount"] = pd.to_numeric(df["pay_amount"], errors="coerce").fillna(0)
df["hours_played"] = (
    pd.to_numeric(df["hours_played"], errors="coerce")
    .replace(0, 1)  # avoid division by zero
)
df["crowd_size"] = pd.to_numeric(df["crowd_size"], errors="coerce").fillna(0)

df["day_of_year"] = df["gig_date"].dt.dayofyear
df["year"] = df["gig_date"].dt.year

# -----------------------------
# Revenue comparison
# -----------------------------
st.subheader("💰 Revenue: This Year vs Last Year (To Date)")

today = dt.date.today()
day_of_year_today = today.timetuple().tm_yday

current_year = df["year"].max()
last_year = current_year - 1

df_current = df[
    (df["year"] == current_year)
    & (df["day_of_year"] <= day_of_year_today)
]

df_last = df[
    (df["year"] == last_year)
    & (df["day_of_year"] <= day_of_year_today)
]

current_rev = df_current.groupby("day_of_year")["pay_amount"].sum().cumsum()
last_rev = df_last.groupby("day_of_year")["pay_amount"].sum().cumsum()

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(current_rev.index, current_rev.values, label=str(current_year), marker="o")
ax.plot(last_rev.index, last_rev.values, label=str(last_year), marker="o")
ax.set_xlabel("Day of Year")
ax.set_ylabel("Cumulative Revenue ($)")
ax.set_title("Cumulative Revenue: This Year vs Last Year")
ax.legend()
ax.grid(True)

st.pyplot(fig)

# -----------------------------
# Pay per hour by gig type
# -----------------------------
st.subheader("⏱️ Pay per Hour by Gig Type")

df["hourly_rate"] = df["pay_amount"] / df["hours_played"]
hourly = (
    df.groupby("gig_type")["hourly_rate"]
    .mean()
    .sort_values(ascending=False)
)

st.bar_chart(hourly)

# -----------------------------
# Total audience
# -----------------------------
st.subheader("👥 Total Audience Reached")

total_crowd = int(df["crowd_size"].sum())
st.metric("People Played To", f"{total_crowd:,}")



