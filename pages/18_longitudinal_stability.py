import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
from utils.usafa_styles import *
import numpy as np
from utils.airfoils import Airfoil
import plotly.graph_objects as go
from PIL import Image

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Longitudinal Stability - Virtual Lab", page_icon="⚖️", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">Longitudinal Stability</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Trim α &nbsp;·&nbsp; Pitching Moment &nbsp;·&nbsp; Turn Rate</div>', unsafe_allow_html=True)

# ── Equations ─────────────────────────────────────────────────────────────────
with st.expander("📖  Governing Equations", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="eq-label">SLUF</div>', unsafe_allow_html=True)
        st.latex(r"\sum F_{c.g.}=0")

        st.markdown('<div class="eq-label">Trim</div>', unsafe_allow_html=True)
        st.latex(r"\sum M_{c.g.} = 0")
        
        st.markdown('<div class="eq-label">Trimmed SLUF</div>', unsafe_allow_html=True)
        st.latex(r"L_W + L_T = W")
        st.latex(r"0 = M_{ac} + L_W  x_W + L_T  x_T")
        st.markdown("""
        <div class="explainer">
        Recall that positive pitching moments (M) result in a nose-up movement of the aircraft.
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="eq-label">Longitudinal Static Stability</div>', unsafe_allow_html=True)
        st.latex(r"\frac{\partial C_{M_{cg}}}{\partial \alpha}=C_{M_\alpha}< 0")
        st.latex(r"C_{M_0}>0")
        st.markdown("""
        <div class="explainer">
        The change in pitching moment as the angle of attack increases must be negative, and the pitching moment for 0 lift must be 0.
        </div>
        """, unsafe_allow_html=True)
st.divider()

# ── Aircraft Parameters (same as climb) ───────────────────────────────────────
W     = 2000.0 #kg
M_ac  = 1000 #Nm


# ── Inputs ────────────────────────────────────────────────────────────────────
col_1, col_2, col_3 = st.columns(3)

with col_1:
    st.markdown("**CG Position (m)**")
    cg = st.slider(
        "cg",
        min_value=0.00, max_value=20.0,
        value=10.0, step=0.1,
        format="c.g. = %.1f m",
        label_visibility="collapsed"
    )

with col_2:
    st.markdown("**Wing AC (m)**")
    w_ac = st.slider(
        "wing_ac",
        min_value=0.0, max_value=  16.0,
        value=8.0, step=0.1,
        format=r"$AC_W$= %.1f m",
        label_visibility="collapsed"
    )
with col_3:
    st.markdown("**Tail/Canard AC (m)**")
    t_ac = st.slider(
        "tail_ac",
        min_value=0.0, max_value=17.0,
        value=16.0, step=0.1,
        format=r"$AC_{T}$ = %.1f m",
        label_visibility="collapsed"
    )
img = Image.open("assets/f15.png")

rho = 1.225
V_ref = 50.0        # m/s
S_ref = 20.0        # m
c_ref = 2.5         # mean aerodynamic chord
q = 0.5 * rho * V_ref**2
# ── Fragment ──────────────────────────────────────────────────────────────────
@st.fragment
def render_aircraft(cg: float, w_ac: float, t_ac: float) -> None:


    # ── Airfoil helper ──────────────────────────────────────────
    def get_airfoil(naca):
        foil = Airfoil.NACA4(naca)
        coords = foil.all_points
        x = np.array(coords[0])
        y = np.array(coords[1])
        mid = len(x)//2
        return x[:mid], y[:mid], x[mid:], y[mid:]

    # ── Get shapes ──────────────────────────────────────────────
    xu_w, yu_w, xl_w, yl_w = get_airfoil("2412")   # cambered wing
    xu_t, yu_t, xl_t, yl_t = get_airfoil("0010")   # symmetric tail
    scale_w = 5.0
    scale_t = 2.5
    
    # ── Position geometry ───────────────────────────────────────
    def place_airfoil(xu, yu, xl, yl, x0, scale):
        ac_real = (xu[-1] - xu[0]) * scale * 0.25
        return (
            xu * scale + x0 - ac_real,
            yu * scale,
            xl * scale + x0 - ac_real,
            yl * scale,
            x0-ac_real
        )

    xwu, ywu, xwl, ywl, w_ac = place_airfoil(xu_w, yu_w, xl_w, yl_w, w_ac, scale_w)
    xtu, ytu, xtl, ytl, t_ac = place_airfoil(xu_t, yu_t, xl_t, yl_t, t_ac, scale_t)

    # ── Plot geometry over F-15 image ───────────────────────────
    fig = go.Figure()

    fig.add_layout_image(
        dict(
            source=img,
            xref="x", yref="y",
            x=0, y=3.5,
            sizex=20, sizey=4,
            sizing="stretch",
            opacity=0.9,
            layer="below"
        )
    )

    # Wing
    fig.add_trace(go.Scatter(x=xwu, y=ywu, mode='lines', line=dict(color=USAFA_BLUE, width=3), name="Wing"))
    fig.add_trace(go.Scatter(x=xwl, y=ywl, mode='lines', line=dict(color=USAFA_BLUE, width=3), showlegend=False))

    # Tail
    fig.add_trace(go.Scatter(x=xtu, y=ytu, mode='lines', line=dict(color=CLASS_RED, width=3), name="Tail"))
    fig.add_trace(go.Scatter(x=xtl, y=ytl, mode='lines', line=dict(color=CLASS_RED, width=3), showlegend=False))

    # CG
    fig.add_trace(go.Scatter(
        x=[cg], y=[0],
        mode='markers+text',
        marker=dict(size=12, color=CLASS_YELLOW),
        text=["CG"],
        textposition="top center",
        name="CG"
    ))

    # AC markers
    fig.add_trace(go.Scatter(x=[w_ac], y=[0], mode='markers', marker=dict(size=8, color=USAFA_BLUE), name="Wing AC"))
    fig.add_trace(go.Scatter(x=[t_ac], y=[0], mode='markers', marker=dict(size=8, color=CLASS_RED), name="Tail AC"))

    fig.update_layout(
        paper_bgcolor=BG_PRIMARY,
        plot_bgcolor=BG_SECONDARY,
        height=350,
        xaxis=dict(range=[0, 20], title="x (m)", color=ACAD_GREY),
        yaxis=dict(range=[-1, 3], title="z (m)", color=ACAD_GREY),
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig, width="stretch")

    # ── Aerodynamic Model ───────────────────────────────────────
    alpha = np.linspace(-10, 15, 200)
    # Lift slopes
    a_w = 4.5   # wing lift slope
    a_t = 3.5  # tail lift slope

    # Lift
    CL_w = a_w * alpha
    CL_t = a_t * alpha
    

    # Moment arms
    xw = cg - w_ac
    xt = cg - t_ac
    
    # Moments
    CM_ac = M_ac / (q * S_ref * c_ref)
    CM = (
        CM_ac +
        CL_w * (xw / c_ref) +
        CL_t * (xt / c_ref)
    )

    # Linear fit → CM0 and slope
    p = np.polyfit(alpha, CM, 1)
    CM_alpha = p[0]
    CM0 = np.polyval(p, 0)

    # Trim (CM = 0)
    alpha_trim = -CM0 / CM_alpha if CM_alpha != 0 else np.nan

    # ── Stability classification ────────────────────────────────
    if CM_alpha < 0:
        stability = "Stable"
        color = GROTTO_BLUE
    elif CM_alpha > 0:
        stability = "Unstable"
        color = CLASS_RED
    else:
        stability = "Neutral"
        color = CLASS_YELLOW

    # ── Plot CM vs alpha ───────────────────────────────────────
    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=np.degrees(alpha),
        y=CM,
        mode='lines',
        name='C_M(α)',
        line=dict(color=color, width=3)
    ))

    # CM0 point
    fig2.add_trace(go.Scatter(
        x=[0], y=[CM0],
        mode='markers+text',
        text=["C_M0"],
        textposition="top right",
        marker=dict(color=CLASS_YELLOW, size=10),
        name="CM0"
    ))

    # Trim point
    if not np.isnan(alpha_trim):
        fig2.add_trace(go.Scatter(
            x=[np.degrees(alpha_trim)], y=[0],
            mode='markers+text',
            text=["α_trim"],
            textposition="bottom right",
            marker=dict(color=CLASS_RED, size=10),
            name="Trim"
        ))

    # Zero line
    fig2.add_hline(y=0, line_dash="dash", line_color=ACAD_GREY)
    fig2.add_vline(x=0, line_dash="dash", line_color=ACAD_GREY)

    fig2.update_layout(
        paper_bgcolor=BG_PRIMARY,
        plot_bgcolor=BG_SECONDARY,
        height=350,
        title=f"C_M vs α  —  {stability}",
        xaxis=dict(title="α (deg)", color=ACAD_GREY, range=[-10, 10]),
        yaxis=dict(title="C_M", color=ACAD_GREY, range = [-0.1, 0.1]),
        margin=dict(l=0, r=0, t=30, b=0)
    )

    st.plotly_chart(fig2, width="stretch")

render_aircraft(cg, w_ac, t_ac)

st.divider()

# ── Intuition ────────────────────────────────────────────────────────────────
with st.expander("💡  Physical Intuition"):
    st.markdown("""
    **What Does Longitudinal Stability Mean**

    - When disturbed from trimmed flight, the tail/canard provides a restoring force towards that trimmed condition, which 
    is in the opposite direction from the disturbance.

    **Aircraft Design Thoughts:**

    - Delta winged aircraft with the wing towards the aft are stabilized by a canard.
    - Traditional wing aircraft are stabilized by a tail, very near the aft end of the aircraft.
            
    """)
    st.markdown("""
    **What About Flying Wings!?**
    - Flight control computers and control surfaces on the trailing edges like split flaps make up for the natural instability.
    """)