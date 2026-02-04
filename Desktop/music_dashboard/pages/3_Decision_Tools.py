import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.title("🧠 Decision Tools")
st.caption("Evaluate future gigs using your own priorities.")

# -----------------------------
# How this works
# -----------------------------
with st.expander("ℹ️ How this decision is calculated"):
    st.markdown(
        """
This tool scores a potential gig using **three dimensions**:

### 1️⃣ Money
- Net pay (fee − travel)
- Effective hourly rate (based on time away from home)
- Compared against your *historical averages*

### 2️⃣ Career Impact
- Gig quality (Low / Medium / High)
- Potential to create future opportunities

### 3️⃣ Personal Enjoyment
- How enjoyable you expect the gig to be

You can **control how much each factor matters** using the sliders below.
Think of them as *what you care about right now*, not forever.
"""
    )

# -----------------------------
# Weight controls (NEW)
# -----------------------------
st.subheader("🎛️ Impact Weighting")

col_w1, col_w2, col_w3 = st.columns(3)

with col_w1:
    money_weight = st.slider("Money importance", 0.0, 1.0, 0.5, 0.05)

with col_w2:
    career_weight = st.slider("Career impact importance", 0.0, 1.0, 0.3, 0.05)

with col_w3:
    enjoyment_weight = st.slider("Enjoyment importance", 0.0, 1.0, 0.2, 0.05)

total_weight = money_weight + career_weight + enjoyment_weight

if total_weight == 0:
    st.warning("At least one weighting must be greater than zero.")
    st.stop()

# Normalise weights so they always sum to 1
money_weight /= total_weight
career_weight /= total_weight
enjoyment_weight /= total_weight

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
# Cached data loader
# -----------------------------
@st.cache_data(ttl=300)
def load_gigs():
    return pd.DataFrame(sheet.get_all_records())

df = load_gigs()

if df.empty:
    st.warning("Not enough historical data yet.")
    st.stop()

# -----------------------------
# Historical baselines
# -----------------------------
df["pay_amount"] = pd.to_numeric(df["pay_amount"], errors="coerce").fillna(0)
df["travel_cost"] = pd.to_numeric(df["travel_cost"], errors="coerce").fillna(0)
df["hours_played"] = pd.to_numeric(df["hours_played"], errors="coerce").replace(0, 1)

df["net_pay"] = df["pay_amount"] - df["travel_cost"]
df["hourly_rate"] = df["net_pay"] / df["hours_played"]

avg_hourly = df["hourly_rate"].mean()
median_hourly = df["hourly_rate"].median()

# -----------------------------
# Future gig evaluator
# -----------------------------
st.subheader("🎯 Evaluate a Potential Gig")

with st.form("gig_decision_form"):
    fee = st.number_input("Gig Fee ($)", min_value=0.0)
    travel_cost = st.number_input("Travel Cost ($)", min_value=0.0)
    time_away = st.number_input("Total Time Away From Home (hours)", min_value=0.1)

    gig_quality = st.selectbox("Gig Quality", ["Low", "Medium", "High"])
    enjoyment = st.slider("Expected Enjoyment (1–5)", 1, 5, 3)
    connections = st.slider("Connections Potential (1–5)", 1, 5, 3)

    evaluate = st.form_submit_button("Evaluate Gig")

# -----------------------------
# Decision logic
# -----------------------------
if evaluate:
    net_pay = fee - travel_cost
    effective_hourly = net_pay / time_away

    # Normalised money score (relative to your average)
    money_score = min(effective_hourly / avg_hourly, 2.0)

    # Career score
    quality_weight = {"Low": 1, "Medium": 2, "High": 3}[gig_quality]
    career_score = (quality_weight * connections) / 15  # normalised 0–1

    # Enjoyment score
    enjoyment_score = enjoyment / 5

    # Final weighted score
    final_score = (
        money_score * money_weight
        + career_score * career_weight
        + enjoyment_score * enjoyment_weight
    )

    st.markdown("### 📊 Evaluation Breakdown")

    col1, col2, col3 = st.columns(3)
    col1.metric("Net Pay", f"${net_pay:,.0f}")
    col2.metric("Effective Hourly", f"${effective_hourly:,.2f}/hr")
    col3.metric("Final Score", f"{final_score:.2f}")

    st.markdown(
        f"""
**Score components:**
- Money score: `{money_score:.2f}` × weight `{money_weight:.2f}`
- Career score: `{career_score:.2f}` × weight `{career_weight:.2f}`
- Enjoyment score: `{enjoyment_score:.2f}` × weight `{enjoyment_weight:.2f}`
"""
    )

    # -----------------------------
    # Recommendation
    # -----------------------------
    if final_score >= 0.9:
        st.success("✅ Strong yes — aligns well with your current priorities.")
    elif final_score >= 0.65:
        st.info("🟡 Maybe — acceptable, but not exceptional.")
    else:
        st.warning("❌ Probably not worth it given your current weighting.")

    st.caption(
        "Try adjusting the sliders to see how your priorities change the outcome."
    )
