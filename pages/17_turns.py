import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
from utils.usafa_styles import *
import numpy as np
import plotly.graph_objects as go

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Turns - Virtual Lab", page_icon="🌀", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">Turning Performance</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Load Factor &nbsp;·&nbsp; Turn Radius &nbsp;·&nbsp; Turn Rate</div>', unsafe_allow_html=True)

# ── Equations ─────────────────────────────────────────────────────────────────
with st.expander("📖  Governing Equations", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="eq-label">Load Factor</div>', unsafe_allow_html=True)
        st.latex(r"n = \frac{1}{\cos\phi}")

        st.markdown('<div class="eq-label">Turn Radius</div>', unsafe_allow_html=True)
        st.latex(r"r = \frac{V^2}{g \sqrt{n^2-1}}")

    with col2:
        st.markdown('<div class="eq-label">Turn Rate</div>', unsafe_allow_html=True)
        st.latex(r"\omega = \frac{g \sqrt{n^2-1}}{V}")

        st.markdown("""
        <div class="explainer">
        In a coordinated turn, lift is tilted by the bank angle (Φ).  
        The vertical component balances weight, while the horizontal component
        provides centripetal force.
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Aircraft Parameters (same as climb) ───────────────────────────────────────
W     = 6000.0
T_max = 1800.0
S     = 380.0
AR    = 3.5
h     = 10000.0

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Weight (lb)", f"{W:.0f}")
col_m2.metric("Max Thrust (lb)", f"{T_max:.0f}")
col_m3.metric("Altitude (ft)", f"{h:.0f}")
col_m4.metric("Wing Area (ft²)", f"{S:.0f}")

# ── Inputs ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Airspeed (kts)**")
    V_knots = st.slider(
        "velocity",
        min_value=100.0, max_value=350.0,
        value=250.0, step=1.0,
        format="V = %.0f kts",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("**Bank Angle (deg)**")
    phi_deg = st.slider(
        "bank",
        min_value=0.0, max_value=75.0,
        value=30.0, step=1.0,
        format="Φ = %.0f°",
        label_visibility="collapsed"
    )

# ── Fragment ──────────────────────────────────────────────────────────────────
@st.fragment
def render_turn(V_knots, phi_deg):

    # ── Physics ────────────────────────────────────────────────
    phi = np.radians(phi_deg)
    V_fts = V_knots * 1.687
    g = 32.174

    n = 1 / np.cos(phi)
    r = V_fts**2 / (g * np.tan(phi)) if phi > 0 else np.inf
    omega = g * np.tan(phi) / V_fts if phi > 0 else 0.0
    omega_deg = np.degrees(omega)

    # ── Metrics ────────────────────────────────────────────────
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Load Factor n", f"{n:.2f}")
    mc2.metric("Turn Radius", f"{r/6076:.2f} nm" if phi > 0 else "∞")
    mc3.metric("Turn Rate", f"{omega_deg:.2f} °/s")

    # ── Forces ─────────────────────────────────────────────────
    L = n * W
    T = T_max
    D = T

    # ── Aircraft Geometry (copied from climb) ──────────────────
    vis = 80.0
    half_span = (S**0.5 / 2) * vis
    chord = (S / (AR**0.5)) / S * vis * S**0.5
    fuse_len = chord * 1.5
    fuse_rad = chord * 0.12
    fuse_h = h * 0.008
    tail_half = half_span * 0.3
    tail_chord = chord * 0.35

    def rotate_yz(y, z, phi):
        y_new = y * np.cos(-phi) - z * np.sin(-phi)
        z_new = (y * np.sin(-phi) + z * np.cos(-phi))/10
        return y_new, z_new


    fig3 = go.Figure()

    # ── Wing ───────────────────────────────────────────────────
    wing_x = [0, -chord, -chord, 0, -chord, -chord]
    wing_y = [0, 0, half_span, 0, 0, -half_span]
    wing_z = [h]*6

    wing_y, wing_z = rotate_yz(np.array(wing_y), np.array(wing_z)-h, phi)
    wing_z += h

    fig3.add_trace(go.Mesh3d(
        x=wing_x, y=wing_y, z=wing_z,
        i=[0,3], j=[1,4], k=[2,5],
        color=ACAD_WHITE, opacity=0.9,
        flatshading=True, showlegend=False
    ))

    # ── Fuselage ───────────────────────────────────────────────
    fx = [ fuse_len*0.2,  fuse_len*0.2,  fuse_len*0.2,  fuse_len*0.2,
          -fuse_len*0.8, -fuse_len*0.8, -fuse_len*0.8, -fuse_len*0.8]
    fy = [ fuse_rad, -fuse_rad, -fuse_rad,  fuse_rad,
           fuse_rad, -fuse_rad, -fuse_rad,  fuse_rad]
    fz = [ fuse_h, fuse_h, -fuse_h, -fuse_h,
           fuse_h, fuse_h, -fuse_h, -fuse_h]

    fy, fz = rotate_yz(np.array(fy), np.array(fz), phi)
    fz += h

    fig3.add_trace(go.Mesh3d(
        x=fx, y=fy, z=fz,
        alphahull=0,
        color=CLASS_YELLOW, opacity=0.9,
        showlegend=False
    ))

    # ── Turn Path (320° arc) ───────────────────────────────────
    if phi > 0:
        theta = np.linspace(0, np.radians(340), 200)
        x_path = r * np.sin(theta)
        y_path = r * (1 - np.cos(theta))
        z_path = np.full_like(theta, h)

        fig3.add_trace(go.Scatter3d(
            x=x_path, y=y_path, z=z_path,
            mode='lines',
            line=dict(color=CLASS_RED, width=4),
            name='Turn Path'
        ))

    # ── Force Vectors ──────────────────────────────────────────
    scale = 0.15

    # Weight
    fig3.add_trace(go.Scatter3d(
        x=[0,0], y=[0,0], z=[h, h - W*scale / 10],
        mode='lines',
        line=dict(color=ACAD_GREY, width=6),
        name='Weight'
    ))
    # Lift (Must be orthogonal to the wing)
    L_val = n * W
    
    # We define the lift in the 'Body Frame' first: 
    # It points straight up relative to the aircraft (z-direction)
    # Then we apply the EXACT same rotation function used for the wings
    L_y_rot, L_z_rot = rotate_yz(0, L_val, phi)
    
    fig3.add_trace(go.Scatter3d(
        x=[0, 0],
        y=[0,  L_y_rot * scale],
        z=[h,  h + L_z_rot * scale],
        mode='lines',
        line=dict(color=USAFA_BLUE, width=6),
        name='Lift'
    ))


    # Thrust
    

    # ── Label ─────────────────────────────────────────────────
    fig3.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[h + 800],
        mode='text',
        text=[f'Φ = {phi_deg:.1f}°'],
        textfont=dict(color=CLASS_YELLOW, size=14),
        showlegend=False
    ))
    R_MAX = 30000 #ft
    # ── Ground ────────────────────────────────────────────────
    gx = np.linspace(-R_MAX, R_MAX, 20)
    gy = np.linspace(-10000, 2* R_MAX, 20)
    gx, gy = np.meshgrid(gx, gy)

    fig3.add_trace(go.Surface(
        x=gx, y=gy, z=np.zeros_like(gx),
        showscale=False, opacity=0.2,
        colorscale=[[0, CLASS_ROYAL], [1, USAFA_BLUE]]
    ))
    # ── Layout ────────────────────────────────────────────────
    fig3.update_layout(
        paper_bgcolor=BG_PRIMARY,
        scene=dict(
            bgcolor=BG_PRIMARY,
            xaxis=dict(
                title='X (ft)',
                color=ACAD_GREY,
                range=[-R_MAX, R_MAX]
            ),
            yaxis=dict(
                title='Y (ft)',
                color=ACAD_GREY,
                range=[-10000, 2 * R_MAX]
            ),
            zaxis=dict(
                title='Altitude (ft)',
                color=ACAD_GREY,
                range=[6000, h * 1.3]
            ),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=1),
            camera=dict(eye=dict(x=.5, y=0.5, z=0.5))
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=500
    )

    st.markdown('<div class="eq-label">Turning Flight Visualization</div>', unsafe_allow_html=True)
    st.plotly_chart(fig3, width='stretch')


render_turn(V_knots, phi_deg)

st.divider()

# ── Intuition ────────────────────────────────────────────────────────────────
with st.expander("💡  Physical Intuition"):
    st.markdown("""
    **What controls turn performance?**

    - Increasing **bank angle (Φ)** increases load factor → tighter turns
    - Higher **velocity** increases turn radius → wider turns

    **Key tradeoffs:**

    - Tight turns require **high lift → high n → structural limits**
    - Fast aircraft turn **large radius but low turn rate**
    """)