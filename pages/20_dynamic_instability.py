import streamlit as st
import numpy as np
import plotly.graph_objects as go
from utils.usafa_styles import USAFA_CSS, render_sidebar
from utils.usafa_styles import *

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Dynamic Stability - Virtual Lab",
    page_icon="📉",
    layout="wide"
)
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()

# ── Header ────────────────────────────────────────────────────
st.markdown('<div class="page-title">Dynamic Stability</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Time Response of Aircraft Modes</div>', unsafe_allow_html=True)

# ── Controls ───────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Dynamic Mode**")
    mode = st.selectbox(
        "mode",
        ["Short-Period", "Phugoid", "Dutch Roll", "Spiral"],
        label_visibility="collapsed"
    )

zeta=0.0
omega=3.3
# ── Time Base ──────────────────────────────────────────────────
t = np.linspace(0, 20, 400)

def response(t, zeta, omega):
    return np.exp(-zeta * omega * t) * np.cos(omega * t)

# ── Plot Helper ────────────────────────────────────────────────
def make_plot(y_dict, title):
    fig = go.Figure()

    for name, y in y_dict.items():
        fig.add_trace(go.Scatter(
            x=t,
            y=y,
            mode='lines',
            name=name
        ))

    fig.update_layout(
        paper_bgcolor=BG_PRIMARY,
        plot_bgcolor=BG_SECONDARY,
        height=400,
        title=title,
        xaxis=dict(title="Time (s)", color=ACAD_GREY),
        yaxis=dict(title="Response", color=ACAD_GREY),
        margin=dict(l=0, r=0, t=40, b=0)
    )

    st.plotly_chart(fig, width="stretch")

# ── Mode Logic ─────────────────────────────────────────────────
if mode == "Short-Period":

    alpha = response(t, zeta, omega)

    make_plot(
        {"α (Angle of Attack)": alpha},
        "Short-Period Mode: α vs Time"
    )

elif mode == "Phugoid":

    alpha = 0.2 * response(t, zeta, omega/12)
    altitude = np.sin(0.3 * t - np.pi/2) 
    velocity = np.cos(0.3 * t)

    make_plot(
        {
            "Altitude (h)": altitude,
            "Velocity (V)": velocity,
            "α (small)": alpha
        },
        "Phugoid Mode: h, V, α vs Time"
    )

elif mode == "Dutch Roll":

    beta = response(t, zeta, omega)
    phi = 0.7 * np.exp(-zeta * omega * t) * np.sin(omega * t)

    make_plot(
        {
            "β (Sideslip)": beta,
            "φ (Bank Angle)": phi
        },
        "Dutch Roll Mode: β & φ vs Time"
    )

elif mode == "Spiral":

    growth = 0.2 * (1 - zeta)  # unstable if zeta < 1

    phi = np.exp(growth * t)
    psi = np.exp(growth * t) * 0.8

    make_plot(
        {
            "φ (Bank Angle)": phi,
            "ψ (Heading)": psi
        },
        "Spiral Mode: Divergence"
    )

# ── Intuition ─────────────────────────────────────────────────
st.divider()

with st.expander("💡 Physical Intuition"):

    st.markdown("""
    **Short-Period**
    - Fast oscillation in angle of attack
    - Highly damped in stable aircraft

    **Phugoid**
    - Exchange between altitude and velocity
    - Very lightly damped (long period)

    **Dutch Roll**
    - Coupled yaw and roll oscillation
    - Common in swept-wing aircraft

    **Spiral Mode**
    - Non-oscillatory divergence
    - Slowly increasing bank and heading change
    """)