import streamlit as st
import streamlit as st
import sys
import os

if 'history' not in st.session_state:
    st.session_state.history = []

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app import load_cities, generate_travel_plan, estimate_total_cost

st.set_page_config(
    page_title="Udta Hi Phiru",
    page_icon="🎒",
    layout="centered"
)

# ---- CUSTOM CSS ----
st.markdown("""
<style>
.big-title {
    font-size: 40px;
    font-weight: 800;
    text-align: center;
}
.sub {
    text-align: center;
    color: #aaa;
    margin-bottom: 30px;
}
.chat-user {
    background-color: #1f2937;
    color: #e5e7eb;
    padding: 14px;
    border-radius: 14px;
    margin: 12px 0;
    font-size: 15px;
}

.chat-bot {
    background-color: #111827;
    color: #f9fafb;
    padding: 14px;
    border-radius: 14px;
    margin: 12px 0;
    font-size: 15px;
}

body {
    background: radial-gradient(circle at top, #0f172a, #020617);
}

.card {
    background: linear-gradient(145deg, #020617, #0f172a);
    border: 1px solid #1e293b;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 22px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.4);
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    margin: 25px 0 10px;
}

.badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 13px;
    background: #1e293b;
    color: #e5e7eb;
    margin-right: 6px;
}

.gradient-text {
    background: linear-gradient(90deg, #38bdf8, #a78bfa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
<style>
.card:hover {
    transform: translateY(-4px);
    transition: all 0.25s ease;
    box-shadow: 0 30px 60px rgba(0,0,0,0.55);
}

.recommended {
    border: 2px solid #22c55e;
}

.footer {
    text-align: center;
    color: #94a3b8;
    font-size: 13px;
    margin: 40px 0 10px;
}

.card:empty {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# ---- HEADER ----
st.markdown("<div class='big-title gradient-text'>🪂 Udta Hi Phiru ✈️</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Because I am an Engineer, not a Doctor 😎🛠️</div>", unsafe_allow_html=True)


cities = load_cities()

st.markdown("<div class='card'>", unsafe_allow_html=True)
source_city = st.selectbox(
    "🏠 Where are you starting from?",
    cities,
    index=cities.index("Delhi") if "Delhi" in cities else 0
)

destination_city = st.selectbox(
    "📍 Where you going bestie?",
    cities
)

transport_mode = st.selectbox(
    "🚦 How do you want to travel?",
    ["Bus", "Train", "Flight", "Car"]
)

budget = st.slider("💰 How broke are we? (₹)", 1000, 50000, 3000, step=500)

days = st.slider("📆 How many days can you escape?", 1, 10, 3)

interest = st.selectbox(
    "✨ What’s the vibe?",
    ["Adventure 🏔️", "Food 🍜", "Culture 🏛️", "Relax 😴"]
)
st.markdown("</div>", unsafe_allow_html=True)


# ---- BUTTON ----
if st.button("🚀 Plan my trip, Bro", use_container_width=True):
    with st.spinner("Cooking your trip plan 🍳🤖"):
        plan = generate_travel_plan(
            source_city,
            destination_city,
            budget,
            days,
            interest,
            transport_mode
        )

    cost = estimate_total_cost(
        source_city,
        destination_city,
        days,
        transport_mode
    )

    budget_diff = budget - cost['total_cost']
    if budget_diff >= 0:
        budget_status = f"✅ Within budget (₹{budget_diff} left)"
        budget_color = "green"
    else:
        budget_status = f"❌ Over budget by ₹{abs(budget_diff)}"
        budget_color = "red"

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 💳 Budget Usage")
    st.progress(min(cost['total_cost'] / budget, 1.0))
    st.markdown(f"<span style='color:{budget_color}; font-weight:600'>{budget_status}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## 💬 Trip Chat")

    st.markdown(
        f"<div class='chat-user'>👤 <b>You:</b><br>"
        f"I want to travel from <b>{source_city}</b> to <b>{destination_city}</b> "
        f"by <b>{transport_mode}</b> for <b>{days}</b> days within ₹{budget}.</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<div class='chat-bot'>🤖 <b>Trip Buddy:</b><br>"
        f"🛣️ <b>Distance:</b> {cost['distance']} km<br>"
        f"🚦 <b>Selected Mode:</b> {cost['mode']}<br>"
        f"💸 <b>Travel:</b> ₹{cost['travel_cost']}<br>"
        f"🏨 <b>Stay:</b> ₹{cost['stay_cost']}<br>"
        f"🍽️ <b>Food:</b> ₹{cost['food_cost']}<br>"
        f"💰 <b>Total:</b> ₹{cost['total_cost']}<br>"
        f"📍 <i>Destination type:</i> {cost['city_type']}"
        f"</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🚦 Transport Cost Comparison")

    modes = ["Bus", "Train", "Flight", "Car"]
    comparison = []
    min_cost = None
    best_mode = None

    for m in modes:
        c = estimate_total_cost(source_city, destination_city, days, m)
        comparison.append({"Mode": m, "Travel Cost (₹)": c['travel_cost']})
        if min_cost is None or c['travel_cost'] < min_cost:
            min_cost = c['travel_cost']
            best_mode = m

    for row in comparison:
        badge = "💸 Cheapest" if row['Mode'] == best_mode else ""
        st.markdown(
            f"<div class='badge { 'recommended' if row['Mode']==best_mode else '' }'>"
            f"{row['Mode']} – ₹{row['Travel Cost (₹)']} {badge}"
            f"</div>",
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.session_state.history.append(
        f"{source_city} → {destination_city} | {transport_mode} | ₹{cost['total_cost']}"
    )

st.markdown("---")
st.markdown("## 🕘 Recent Trips")
if st.session_state.history:
    for h in st.session_state.history[-3:][::-1]:
        st.markdown(f"- {h}")
else:
    st.caption("No trips yet. Plan one!")

st.markdown(
    "<div class='footer'>Built with ❤️ using Streamlit | Udta Hi Phiru © 2026</div>",
    unsafe_allow_html=True
)
