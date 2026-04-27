import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
from utils.usafa_styles import *
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Mach Wave - Virtual Lab", page_icon="⭕", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()

# ── Page Header (static) ──────────────────────────────────────────────────────
st.markdown('<div class="page-title">Mach Wave</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Doppler Shift &nbsp;·&nbsp;  Shock Wave Geometry</div>', unsafe_allow_html=True)

# ── Equations (static) ────────────────────────────────────────────────────────
with st.expander("📖  Governing Equations", expanded=True):
    col_eq1, col_eq2 = st.columns(2)

    with col_eq1:
        st.markdown('<div class="eq-label">Mach Angle (Cone Half-Angle)</div>', unsafe_allow_html=True)
        st.latex(r"\mu = \arcsin\!\left(\frac{a}{V_\infty}\right)")
        st.markdown("""
        <div class="explainer">
        The Mach angle <em>μ</em> defines the half-angle of the Mach cone. At a given point, disturbances
        from the passing aircraft propogate outward at the speed of sound. The mach cone is the envelope containing
        these disturbances (sounds).
        </div>
        """, unsafe_allow_html=True)

    with col_eq2:
        st.markdown('<div class="eq-label">Wave Spacing - Doppler Shift</div>', unsafe_allow_html=True)
        st.latex(r"\text{Upstream Sound Propogation Speed Relative to Aircraft} = a-V")
        st.latex(r"\text{Downstream Sound Propogation Speed Aircraft} = a+V")
        st.markdown("""
        <div class="explainer">
        As V approaches a, the spacing between upstream soundwaves decreases, increasing the perceived frequency of sound generated.
        Downstream this spacing increases, which lowers the frequency of perceived sound. This effect is the doppler shift.
        When V > a, the sound can no longer propogate upstream, forming a Mach cone and shockwave dividing the regions of sound and silence.
        </div>
        """, unsafe_allow_html=True)

st.divider()

col_mach, col_space, col_badge = st.columns([1,.2,1])

with col_mach:
    st.markdown("**Mach Number**")
    mach = st.slider(
            label="mach_slider",
            min_value=0.0, max_value=5.0,
            value=0.5, step=0.01,
            format="M = %.2f",
            label_visibility="collapsed",
            key="mach"
        )
with col_badge:
    if mach < 0.85:
        regime, r_color = "SUBSONIC",  GROTTO_BLUE
    elif mach < 1.2:
        regime, r_color = "TRANSONIC",  CLASS_YELLOW
    elif mach < 4.99:
        regime, r_color = "SUPERSONIC", CLASS_RED
    else:
        regime, r_color = "HYPERSONIC", ACAD_GREY

    st.markdown(
            f"<div style='font-family:\"Barlow Condensed\",\"Trebuchet MS\",sans-serif;"
            f"font-size:0.8rem;font-weight:700;letter-spacing:0.15em;"
            f"padding:0.4rem 0.9rem;border-radius:3px;margin-bottom:50px;"
            f"border:1px solid {r_color};color:{r_color};"
            f"display:inline-block;margin-top:1.6rem;text-transform:uppercase;'>"
            f"{regime}</div>",
            unsafe_allow_html=True
        )
    
@st.fragment
def render_wave(mach: float) -> None:
    a   = 1116.4          # ft/s speed of sound
    V   = mach * a        # aircraft velocity ft/s
    mu  = np.degrees(np.arcsin(1 / mach)) if mach > 1 else None
    t   = np.array([0, 1, 2, 3, 4])   # time steps (seconds)
    t_now = t[-1]


    emit_x = t * V

    radii  = (t_now - t) * a

    # ── Metrics ───────────────────────────────────────────────────
    with col_mach:
        st.metric(label='Speed of Sound', value=f'{a:.1f} ft/s')
    with col_badge:
        if mach > 1:
            st.metric(label='Mach Angle (μ)', value=f'{mu:.2f}°')

    # ── Build sphere surface for one sphere ───────────────────────
    def make_sphere(cx, r, n=30):
        """Return x, y, z surface arrays for a sphere centered at (cx,0,0)."""
        u = np.linspace(0, 2 * np.pi, n)
        v = np.linspace(0, np.pi, n)
        x = cx + r * np.outer(np.cos(u), np.sin(v))
        y =      r * np.outer(np.sin(u), np.sin(v))
        z =      r * np.outer(np.ones(n), np.cos(v))
        return x, y, z

    # ── Mach cone surface ─────────────────────────────────────────
    def make_cone(x_tip, mu_deg, length, n=60):
        """Return x, y, z for a cone with tip at x_tip extending left."""
        mu_rad   = np.radians(mu_deg)
        x_linear = np.linspace(0, -length, n)
        theta    = np.linspace(0, 2 * np.pi, n)
        X, T     = np.meshgrid(x_linear, theta)
        R        = np.abs(X) * np.tan(mu_rad)
        Xc       = x_tip + X
        Yc       = R * np.cos(T)
        Zc       = R * np.sin(T)
        return Xc, Yc, Zc

    # ── Color scale for spheres ───────
    sphere_colors = [
        '#1a2a4a', '#1e3a6e', '#003594',
        '#0055cc', '#00BED6'
    ]

    fig = go.Figure()

    # ── Draw spheres ──────────────────────────────────────────────
    for i, (cx, r) in enumerate(zip(emit_x, radii)):
        if r <= 0:
            continue
        sx, sy, sz = make_sphere(cx, r, n=40)
        fig.add_trace(go.Surface(
            x=sx, y=sy, z=sz,
            colorscale=[[0, sphere_colors[i]], [1, sphere_colors[i]]],
            showscale=False,
            opacity=0.18 + i * 0.06,
            hovertemplate=f't={t[i]}s  r={r:.0f}ft<extra></extra>',
            name=f't = {t[i]}s'
        ))

    # ── Draw Mach cone (M>1 only) ─────────────────────────────────
    if mach > 1:
        cone_length = t_now * V   # full length of aircraft path
        x_tip       = t_now * V   # tip at current aircraft position
        Xc, Yc, Zc  = make_cone(x_tip, mu, cone_length, n=80)
        fig.add_trace(go.Surface(
            x=Xc, y=Yc, z=Zc,
            colorscale=[[0, CLASS_RED], [1, '#ff6b6b']],
            showscale=False,
            opacity=0.20,
            hovertemplate=f'Mach cone  μ={mu:.1f}°<extra></extra>',
            name='Mach cone'
        ))

    # ── Aircraft position marker ──────────────────────────────────
    x_ac = t_now * V
    fig.add_trace(go.Scatter3d(
        x=[x_ac], y=[0], z=[0],
        mode='markers+text',
        marker=dict(size=6, color=CLASS_YELLOW, symbol='diamond'),
        text=[f'  M={mach:.2f}'],
        textfont=dict(color=CLASS_YELLOW, size=10),
        name='Aircraft',
        hovertemplate=f'Aircraft  x={x_ac:.0f}ft<extra></extra>'
    ))

    # ── Flight path line ──────────────────────────────────────────
    fig.add_trace(go.Scatter3d(
        x=[0, x_ac], y=[0, 0], z=[0, 0],
        mode='lines',
        line=dict(color=CLASS_YELLOW, width=2, dash='dash'),
        name='Flight path',
        hoverinfo='skip'
    ))

    # ── Emission point markers ────────────────────────────────────
    valid = radii > 0
    fig.add_trace(go.Scatter3d(
        x=emit_x[valid], y=np.zeros(valid.sum()), z=np.zeros(valid.sum()),
        mode='markers',
        marker=dict(size=3, color=GROTTO_BLUE),
        name='Emission points',
        hovertemplate='Emitted at x=%{x:.0f}ft<extra></extra>'
    ))

    # ── Layout ────────────────────────────────────────────────────
    max_r   = radii.max()
    x_range = [-(max_r * 0.3), x_ac + max_r * 0.3]
    ax_range = [-max_r * 1.1, max_r * 1.1]

    fig.update_layout(
        paper_bgcolor='#001433',
        scene=dict(
            bgcolor='#001433',
            xaxis=dict(title='x (ft)', color='#B2B4B2',
                       gridcolor='#1e2d5a', range=x_range,
                       backgroundcolor='#001433'),
            yaxis=dict(title='y (ft)', color='#B2B4B2',
                       gridcolor='#1e2d5a', range=ax_range,
                       backgroundcolor='#001433'),
            zaxis=dict(title='z (ft)', color='#B2B4B2',
                       gridcolor='#1e2d5a', range=ax_range,
                       backgroundcolor='#001433'),
            aspectmode='manual',
            aspectratio=dict(x=2.0, y=1.0, z=1.0),
            camera=dict(eye=dict(x=1.5, y=1.2, z=0.8))
        ),
        legend=dict(
            bgcolor='#002554', bordercolor=CLASS_ROYAL,
            font=dict(color='#B2B4B2', size=9)
        ),
        margin=dict(l=0, r=0, t=20, b=0),
        height=500,
    )

    st.plotly_chart(fig, width='stretch')

render_wave(mach)