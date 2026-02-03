import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import datetime as dt

st.title("📊 Performance Visuals")

# --- Load Data ---
DATA_PATH = Path("data/gigs.csv")

if not DATA_PATH.exists():
    st.warning("No gigs yet. Add data first.")
    st.stop()

# Read CSV
df = pd.read_csv(DATA_PATH, parse_dates=["gig_date", "booking_date"], dayfirst=True)

# Ensure gig_date is datetime (coerce invalids to NaT)
df["gig_date"] = pd.to_datetime(df["gig_date"], errors="coerce")
df = df.dropna(subset=["gig_date"])  # drop rows where gig_date couldn't be parsed

# Ensure other numeric columns are numeric
df["pay_amount"] = pd.to_numeric(df["pay_amount"], errors="coerce").fillna(0)
df["hours_played"] = pd.to_numeric(df["hours_played"], errors="coerce").replace(0, 1)  # avoid div by zero
df["crowd_size"] = pd.to_numeric(df["crowd_size"], errors="coerce").fillna(0)

# Add day-of-year column
df["day_of_year"] = df["gig_date"].dt.dayofyear
df["year"] = df["gig_date"].dt.year

# --- Revenue Comparison ---
st.subheader("💰 Revenue: This Year vs Last Year (To Date)")

today = dt.date.today()
day_of_year_today = today.timetuple().tm_yday

current_year = df["year"].max()
last_year = current_year - 1

# Filter by year and up to today's day-of-year
df_current = df[(df["year"] == current_year) & (df["day_of_year"] <= day_of_year_today)]
df_last = df[(df["year"] == last_year) & (df["day_of_year"] <= day_of_year_today)]

# Cumulative revenue
current_rev = df_current.groupby("day_of_year")["pay_amount"].sum().cumsum()
last_rev = df_last.groupby("day_of_year")["pay_amount"].sum().cumsum()

# Plot revenue
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(current_rev.index, current_rev.values, label=str(current_year), marker="o")
ax.plot(last_rev.index, last_rev.values, label=str(last_year), marker="o")
ax.set_xlabel("Day of Year")
ax.set_ylabel("Cumulative Revenue ($)")
ax.set_title("Cumulative Revenue: This Year vs Last Year")
ax.legend()
ax.grid(True)

st.pyplot(fig)

# --- Pay per Hour by Gig Type ---
st.subheader("⏱️ Pay per Hour by Gig Type")

# Avoid division by zero
df["hourly_rate"] = df["pay_amount"] / df["hours_played"]
hourly = df.groupby("gig_type")["hourly_rate"].mean().sort_values(ascending=False)

st.bar_chart(hourly)

# --- Total Audience ---
st.subheader("👥 Total Audience Reached")
total_crowd = int(df["crowd_size"].sum())
st.metric("People Played To", f"{total_crowd:,}")


