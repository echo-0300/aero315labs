import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils.usafa_styles import USAFA_CSS, render_sidebar

st.set_page_config(
    page_title="AeroFundamentals Lab — USAFA",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(USAFA_CSS, unsafe_allow_html=True)

render_sidebar()

st.markdown("""
<div class="hero-container">
    <div class="hero-title">Aero 315 Virtual Labs</div>
    <div class="hero-subtitle">Interactive Visualization Suite&nbsp;&middot;&nbsp; DFAN</div>
    <div class="hero-description">
        Each virtual lab focuses on a core concept for AERO315. The labs highlight any
            critical equations for the topic and provide an interactive visualization to 
            help build conceptual intuitions.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-header">Available Labs</div>', unsafe_allow_html=True)

def lab_card(page, icon, title, desc, color=""):
    return f"""
    <a href="/{page}" target="_self" style="text-decoration: none;">
        <div class="lab-card {color}">
            <div class="lab-card-icon">{icon}</div>
            <div class="lab-card-title">{title}</div>
            <div class="lab-card-desc">{desc}</div>
        </div>
    </a>
    """

labs = [
    # --- Pressure & Atmosphere ---
    ("perfect_gas_law", "💨", "Perfect Gas Law",
     "Relate pressure, temperature, and density. Explore how changes in one variable influences the others.", "yellow"),

    ("manometry", "🧪", "Manometry",
     "Visualize pressure measurement using fluid columns.", "red"),

    ("standard_atmosphere", "🌡️", "Standard Atmosphere",
     "Understand how temperature, pressure, and density vary with altitude and identify atmospheric layers.", "grotto"),

    # --- Fluid Flow ---
    ("continuity", "➡️", "Continuity",
     "Understand conservation of mass in flow. See how velocity changes with area and density variations.", "yellow"),

    ("stream_tube", "💧", "Stream Tube",
     "Track fluid elements through a varying stream tube and visualize how area and velocity evolve along the flow.", "grotto"),

    ("bernoulli", "🧔🏼", "Bernoulli Equation",
     "Relate pressure, velocity in an idealized fluid. Explore energy conservation along a streamline.", "red"),

    # --- Aircraft Pressure Measurement ---
    ("pitot_static", "💨", "Pitot-Static",
     "Measure dynamic pressure to infer airspeed. Connect stagnation pressure to velocity in subsonic and compressible flow.", "yellow"),

    ("altimetry", "🧭", "Altimetry",
     "Explore pressure altitude and altimeter settings. Understand how conditions on the day affects altitude readings.", "grotto"),

    ("icetg", "🧊", "ICeT-G Airspeeds",
     "Compare indicated, calibrated, equivalent, and true airspeeds with reference to their groundspeed equivalent.", "red"),

    # --- Airfoils ---
    ("boundary_layer", "🍰", "Boundary Layer",
     "Visualize laminar and turbulent boundary layers and their growth along a surface.", "yellow"),

    ("airfoils", "🪽", "2-D Airfoils",
     "Examine lift generation, pressure distribution, and angle-of-attack effects on airfoil performance.", "grotto"),

    ("3d_wing_lift", "✈️", "3-D Wing Lift",
     "Understand finite wing effects, induced drag, and spanwise lift distribution.", "red"),

    # --- Compressibility ---
    ("mach_angle", "📐", "Mach Angle",
     "Visualize Mach cone geometry and how the cone angle varies with Mach number.", "yellow"),

    ("mach_wave", "⭕", "Mach Wave",
     "Explore wave propagation from supersonic flight.", "grotto"),

    # --- Performance ---
    ("glide", "🍂", "Glide",
     "Analyze glide performance, sink rate, and best glide conditions for aircraft.", "red"),

    ("climb", "🗻", "Climb",
     "Examine climb performance, excess power, and rate vs. angle of climb.", "yellow"),

    ("turns", "🛞", "Turns",
     "Understand coordinated turns, load factor, and turning performance limits.", "grotto"),
]

# --- Render grid ---
cols = st.columns(4)

for i, lab in enumerate(labs):
    with cols[i % 4]:
        st.markdown(lab_card(*lab), unsafe_allow_html=True)
