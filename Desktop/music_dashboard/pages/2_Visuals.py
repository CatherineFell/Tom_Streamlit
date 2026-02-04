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
# Cached loader
# -----------------------------
@st.cache_data(ttl=300)
def load_gigs():
    return pd.DataFrame(sheet.get_all_records())

if st.button("🔄 Refresh data"):
    st.cache_data.clear()

df = load_gigs()
if df.empty:
    st.warning("No gigs yet.")
    st.stop()

# -----------------------------
# Cleaning
# -----------------------------
df["gig_date"] = pd.to_datetime(df["gig_date"], errors="coerce")
df = df.dropna(subset=["gig_date"])

df["gig_fee"] = pd.to_numeric(df["gig_fee"], errors="coerce").fillna(0)
df["stage_time"] = pd.to_numeric(df["stage_time"], errors="coerce").replace(0, 1)

df["day_of_year"] = df["gig_date"].dt.dayofyear
df["year"] = df["gig_date"].dt.year

# -----------------------------
# Revenue comparison
# -----------------------------
st.subheader("💰 Revenue: This Year vs Last Year (To Date)")

today = dt.date.today()
doy_today = today.timetuple().tm_yday

current_year = df["year"].max()
last_year = current_year - 1

df_current = df[(df["year"] == current_year) & (df["day_of_year"] <= doy_today)]
df_last = df[(df["year"] == last_year) & (df["day_of_year"] <= doy_today)]

current_rev = df_current.groupby("day_of_year")["gig_fee"].sum().cumsum()
last_rev = df_last.groupby("day_of_year")["gig_fee"].sum().cumsum()

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(current_rev.index, current_rev.values, label=str(current_year))
ax.plot(last_rev.index, last_rev.values, label=str(last_year))
ax.legend()
ax.set_title("Cumulative Revenue")
ax.set_xlabel("Day of Year")
ax.set_ylabel("Revenue ($)")
ax.grid(True)

st.pyplot(fig)

# -----------------------------
# Gap to last year
# -----------------------------
st.subheader("📉 Gap to Last Year")

current_total = current_rev.iloc[-1] if not current_rev.empty else 0
last_total = last_rev.iloc[-1] if not last_rev.empty else 0

gap = current_total - last_total
pct = (gap / last_total * 100) if last_total > 0 else 0

st.metric(
    "Revenue vs Last Year",
    f"${current_total:,.0f}",
    delta=f"{gap:,.0f} ({pct:.1f}%)",
)

# -----------------------------
# Pay per hour
# -----------------------------
st.subheader("⏱️ Pay per Hour by Gig Type")

df["hourly_rate"] = df["gig_fee"] / df["stage_time"]
hourly = df.groupby("gig_type")["hourly_rate"].mean().sort_values(ascending=False)

st.bar_chart(hourly)

# -----------------------------
# Audience
# -----------------------------
st.subheader("👥 Total Audience Reached")
st.metric("People Played To", f"{int(df['crowd_size'].sum()):,}")


