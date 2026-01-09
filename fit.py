import streamlit as st
import google.generativeai as genai
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- API & MODEL CONFIG ---
GENAI_API_KEY = "AIzaSyBWG6VzGEfgR1u-fsVQPHPIupFTjYeQEq0" 
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="OLYMPIAN PRO 2026",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE INITIALIZATION ---
if 'workout_history' not in st.session_state:
    st.session_state.workout_history = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- NEW PREMIUM SLATE & GOLD THEME ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;700&display=swap');
    
    /* Premium Midnight Mesh Background */
    .stApp {
        background-color: #0f172a;
        background-image: 
            radial-gradient(at 0% 0%, rgba(30, 58, 138, 0.5) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(15, 23, 42, 1) 0px, transparent 50%),
            url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2v-4h4v-2h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2v-4h4v-2H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        background-attachment: fixed;
        color: #f8fafc;
    }

    /* Typography */
    h1, h2, h3 { 
        font-family: 'Orbitron', sans-serif; 
        text-transform: uppercase; 
        letter-spacing: 2px;
        color: #f8fafc;
    }
    
    .gold-glow { 
        color: #fbbf24; 
        text-shadow: 0 0 20px rgba(251, 191, 36, 0.4); 
    }

    /* Premium Glass Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(251, 191, 36, 0.2);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    
    /* BMI Box Styling */
    .bmi-box {
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        margin-top: 15px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.2);
    }

    /* Professional Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%) !important;
        color: #0f172a !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(251, 191, 36, 0.4);
    }

    /* Sidebar Tweaks */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95) !important;
        border-right: 1px solid rgba(251, 191, 36, 0.1);
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 4px;
        color: #94a3b8;
        font-family: 'Orbitron', sans-serif;
    }

    .stTabs [aria-selected="true"] {
        color: #fbbf24 !important;
        border-bottom-color: #fbbf24 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- WORKOUT DATA ---
WORKOUT_DB = {
    "Chest": {
        "Bodyweight": {"img": "https://images.unsplash.com/photo-1598971639058-fab3c32f850c?q=80&w=1200", "ex": ["Standard Pushups", "Diamond Pushups", "Wide Pushups"]},
        "Dumbbell": {"img": "https://images.unsplash.com/photo-1581009146145-b5ef03a7403e?q=80&w=1200", "ex": ["DB Bench Press", "Incline DB Flys", "DB Pullovers"]},
        "Barbell": {"img": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1200", "ex": ["Barbell Bench Press", "Incline Barbell Press", "Close Grip Bench"]}
    },
    "Back": {
        "Bodyweight": {"img": "https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?q=80&w=1200", "ex": ["Pullups", "Chin-ups", "Inverted Rows"]},
        "Dumbbell": {"img": "https://images.unsplash.com/photo-1603287611437-4c7468c5d14e?q=80&w=1200", "ex": ["Single Arm DB Row", "DB Renegade Row", "DB Shrugs"]},
        "Barbell": {"img": "https://images.unsplash.com/photo-1534367507873-d2d7e24c797f?q=80&w=1200", "ex": ["Conventional Deadlift", "Bent Over Rows", "Pendlay Rows"]}
    },
    "Legs": {
        "Bodyweight": {"img": "https://images.unsplash.com/photo-1434608519344-49d77a699e1d?q=80&w=1200", "ex": ["Air Squats", "Walking Lunges", "Bulgarian Split Squats"]},
        "Dumbbell": {"img": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?q=80&w=1200", "ex": ["Goblet Squats", "DB RDLs", "DB Step-ups"]},
        "Barbell": {"img": "https://images.unsplash.com/photo-1534258936925-c58bed479fcb?q=80&w=1200", "ex": ["Back Squat", "Front Squat", "Barbell Hip Thrusts"]}
    },
    "Shoulders": {
        "Bodyweight": {"img": "https://images.unsplash.com/photo-1544033527-b192daee1f5b?q=80&w=1200", "ex": ["Pike Pushups", "Handstand Holds", "Dive Bomber Pushups"]},
        "Dumbbell": {"img": "https://images.unsplash.com/photo-1590487988256-9ed24133863e?q=80&w=1200", "ex": ["Arnold Press", "Lateral Raises", "DB Front Raises"]},
        "Barbell": {"img": "https://images.unsplash.com/photo-1590239926044-245842813151?q=80&w=1200", "ex": ["Military Press", "Push Press", "Upright Rows"]}
    }
}

# --- SIDEBAR: BIOMETRIC ANALYTICS ---
with st.sidebar:
    st.markdown("<h2 class='gold-glow'>BIOMETRIC HUB</h2>", unsafe_allow_html=True)
    
    st.subheader("⚖️ BMI ANALYZER")
    height = st.number_input("Height (cm)", 100, 250, 175)
    weight = st.number_input("Weight (kg)", 30.0, 250.0, 75.0)
    
    bmi = weight / ((height/100)**2)
    st.markdown(f"### CURRENT BMI: <span style='color:#fbbf24'>{bmi:.1f}</span>", unsafe_allow_html=True)
    
    if bmi < 18.5:
        st.markdown("<div class='bmi-box' style='background:#3b82f6; color:white;'>STATUS: UNDERWEIGHT</div>", unsafe_allow_html=True)
    elif 18.5 <= bmi < 25:
        st.markdown("<div class='bmi-box' style='background:#10b981; color:white;'>STATUS: OPTIMAL</div>", unsafe_allow_html=True)
    elif 25 <= bmi < 30:
        st.markdown("<div class='bmi-box' style='background:#f59e0b; color:white;'>STATUS: OVERWEIGHT</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='bmi-box' style='background:#ef4444; color:white;'>STATUS: OBESE</div>", unsafe_allow_html=True)
    
    st.divider()
    user_goal = st.selectbox("TRAINING FOCUS", ["Fat Loss", "Muscle Gain", "Pure Strength", "Endurance"])
    
    if st.button("RESET ALL DATA"):
        st.session_state.workout_history = []
        st.rerun()

# --- MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center;' class='gold-glow'>OLYMPIAN PRO 2026</h1>", unsafe_allow_html=True)

tab_train, tab_stats, tab_ai = st.tabs(["🏋️ TRAINING", "📊 ANALYTICS", "🧠 AI COACH"])

# --- TAB 1: TRAINING ---
with tab_train:
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.subheader("🛠️ SETUP")
        muscle = st.selectbox("MUSCLE GROUP", list(WORKOUT_DB.keys()))
        equip = st.radio("EQUIPMENT", ["Bodyweight", "Dumbbell", "Barbell"], horizontal=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.subheader("📝 LOG SETS")
        selected_exercises = WORKOUT_DB[muscle][equip]["ex"]
        
        for ex in selected_exercises:
            with st.expander(f"{ex}", expanded=False):
                col_s, col_r, col_w = st.columns(3)
                s = col_s.number_input("Sets", 0, 10, key=f"s_{ex}")
                r = col_r.number_input("Reps", 0, 50, key=f"r_{ex}")
                w = col_w.number_input("Kg", 0, 500, key=f"w_{ex}")
                if st.button(f"LOG {ex.upper()}", key=f"btn_{ex}"):
                    vol = s * r * w
                    st.session_state.workout_history.append({
                        "time": datetime.now().strftime("%H:%M"),
                        "exercise": ex,
                        "volume": vol,
                        "details": f"{s}x{r} @ {w}kg"
                    })
                    st.toast(f"Logged: {ex}")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        img_url = WORKOUT_DB[muscle][equip]["img"]
        st.markdown(f"""
            <div style='border-radius: 20px; overflow: hidden; border: 2px solid rgba(251, 191, 36, 0.3);'>
                <img src='{img_url}' style='width: 100%; display: block;'>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br><div class='metric-card'>", unsafe_allow_html=True)
        st.subheader("📥 SESSION ACTIVITY")
        if not st.session_state.workout_history:
            st.info("Performance buffer empty. Log a set to begin.")
        else:
            for entry in reversed(st.session_state.workout_history[-5:]):
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.05); padding:10px; border-radius:10px; margin-bottom:8px; border-left:4px solid #fbbf24;'>
                    <span style='color:#fbbf24; font-weight:bold;'>{entry['time']}</span> | {entry['exercise']} | {entry['details']}
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: ANALYTICS ---
with tab_stats:
    if not st.session_state.workout_history:
        st.warning("Data required for visualization. Begin your training session.")
    else:
        df = pd.DataFrame(st.session_state.workout_history)
        
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.subheader("📈 INTENSITY OVERVIEW")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=df['volume'], 
            mode='lines+markers', 
            line=dict(color='#fbbf24', width=4),
            marker=dict(size=10, color='#1e293b', line=dict(color='#fbbf24', width=2))
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font_color="#94a3b8", 
            margin=dict(l=0, r=0, t=30, b=0),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        m_col1, m_col2 = st.columns(2)
        m_col1.metric("TOTAL TONNAGE", f"{df['volume'].sum()} KG", delta_color="normal")
        m_col2.metric("PEAK SET VOLUME", f"{df['volume'].max()} KG", delta_color="normal")

# --- TAB 3: AI COACH ---
with tab_ai:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.subheader("🧠 NEURAL COACHING")
    st.caption(f"Profile: BMI {bmi:.1f} | Goal: {user_goal}")
    
    user_query = st.chat_input("Ask about biomechanics, nutrition, or recovery...")
    
    if user_query:
        st.chat_message("user").write(user_query)
        with st.spinner("Analyzing performance data..."):
            prompt = f"""
            You are the OLYMPIAN PRO AI Coach. 
            Athlete Data: BMI {bmi:.1f}, Goal: {user_goal}, Focus: {muscle}.
            Equip: {equip}.
            Be professional, scientific, and encouraging. Answer: {user_query}
            """
            response = model.generate_content(prompt)
            st.chat_message("assistant").write(response.text)
    st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<br><hr><center><small style='color: #64748b;'>OLYMPIAN PRO 2026 | DESIGNED FOR ELITE PERFORMANCE | VERSION 4.2.0</small></center>", unsafe_allow_html=True)