import streamlit as st

st.title("🧠 Gig Decision Tool")

st.markdown("""
This tool estimates whether a gig is **worth taking**, based on:
- Money
- Time cost
- Enjoyment & future value

You can **control how much each factor matters**.
""")

# -----------------------------
# Inputs
# -----------------------------
st.subheader("Gig Details")

gig_fee = st.number_input("Gig Fee ($)", 0.0)
stage_time = st.number_input("Stage Time (hours)", 0.1)
time_away = st.number_input("Total Time Away From Home (hours)", 0.1)
travel_cost = st.number_input("Travel Cost ($)", 0.0)

quality = st.selectbox("Gig Quality", ["High", "Medium", "Low"])
enjoyment = st.slider("Gig Enjoyment", 1, 5, 3)
connections = st.slider("Connections Potential", 1, 5, 3)

# -----------------------------
# Weighting
# -----------------------------
st.subheader("⚖️ What Matters to You")

w_money = st.slider("Money Importance", 0.0, 1.0, 0.4)
w_time = st.slider("Time Cost Importance", 0.0, 1.0, 0.3)
w_experience = st.slider("Experience / Future Value", 0.0, 1.0, 0.3)

# -----------------------------
# Scoring
# -----------------------------
quality_map = {"High": 5, "Medium": 3, "Low": 1}

money_score = (gig_fee - travel_cost) / max(time_away, 1)
time_score = 1 / time_away
experience_score = (quality_map[quality] + enjoyment + connections) / 15

decision_score = (
    money_score * w_money
    + time_score * w_time
    + experience_score * w_experience * 10
)

# -----------------------------
# Output
# -----------------------------
st.subheader("📊 Decision Result")

if decision_score >= 8:
    verdict = "🔥 Strong Yes"
elif decision_score >= 5:
    verdict = "👍 Probably Worth It"
elif decision_score >= 3:
    verdict = "⚠️ Borderline"
else:
    verdict = "❌ Not Worth It"

st.metric("Decision Score", f"{decision_score:.2f}")
st.success(verdict)

st.markdown("""
**How this works**
- Money is adjusted for travel and time away
- Experience combines enjoyment, quality, and connections
- Weights let you decide what you care about *this season*
""")

