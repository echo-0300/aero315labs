import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
from utils.usafa_styles import *
import numpy as np
from utils.airfoils import Airfoil
import plotly.graph_objects as go
from PIL import Image

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Lateral - Directional Stability - Virtual Lab", page_icon="🎯", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">Lateral-Directional Stability</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Sideslip Angle  &nbsp;·&nbsp; Rolling and Yawing Moments &nbsp;·&nbsp; Turn Rate</div>', unsafe_allow_html=True)

# ── Equations ─────────────────────────────────────────────────────────────────
with st.expander("📖  Governing Equations", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="eq-label">Lateral Static Stability</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="explainer">
        When an aircraft is disturbed around the z-axis (yaw), a sideslip angle (β) is generated. Positive β is wind
        in the pilots right ear. Postive Lateral stability is the tendancy for a positive yawing moment (nose-right) when disturbed with a positive β.
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="eq-label">Directional Static Stability</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="explainer">
        Postive Lateral stability is the tendancy for a negative rolling moment (right wing down) when disturbed with a positive β.
        </div>
        """, unsafe_allow_html=True)
st.divider()


img1 = Image.open("assets/sr71.png")
img1 = img1.rotate(90, expand=True)
img2 = Image.open("assets/sr71aft.png")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Select Stability**")
    stability = st.selectbox("Stability?",options=("Positive","Neutral","Negative"), label_visibility = "hidden")
with col2:
    st.markdown("**Side-slip Angle (β)**")
    beta = st.slider(
            "β",
            min_value=-5.00, max_value=5.0,
            value=2.0, step=0.1,
            format="β = %.1f deg",
            label_visibility="collapsed"
        )

# ── Fragment ──────────────────────────────────────────────────────────────────
@st.fragment
def render_plots(stability: str) -> None:

    beta_rad = np.radians(beta)

    # ── Stability slopes (notional) ─────────────────────────────
    if stability == "Positive":
        CN_slope = 0.05
        CL_slope = -0.04
        color = GROTTO_BLUE
    elif stability == "Negative":
        CN_slope = -0.05
        CL_slope = 0.04
        color = CLASS_RED
    else:
        CN_slope = 0.0
        CL_slope = 0.0
        color = CLASS_YELLOW

    x0, y0 = 10, 10         # origin point (aircraft CG-ish)
    L = 2                  # arrow length scaling
    # ===========================================================
    # ── TOP VIEW (Yawing) ──────────────────────────────────────
    # ===========================================================
    col1, col2 = st.columns(2)

    with col1:

        fig_top = go.Figure()

        # Background image
        fig_top.add_layout_image(
            dict(
                source=img1,
                xref="x", yref="y",
                x=6, y=8,
                sizex=20, sizey=8,
                sizing="contain",
                opacity=0.8,
                layer="below"
            )
        )

        # Tail force (direction depends on stability)
        force_dir = np.sign(CN_slope) * np.sign(beta)
        
        if beta == 0 or stability == "Neutral":
            pass
        else:
            fig_top.add_annotation(
                x=10 + 2 * np.abs(beta) * -force_dir, y=1,   # arrow tip
                ax=10, ay=1,                 # arrow base
                xref="x", yref="y",
                axref="x", ayref="y",
                showarrow=True,
                arrowhead=3,
                arrowsize=1.5,
                arrowwidth=4,
                arrowcolor=CLASS_RED,
            )
            fig_top.add_annotation(
                x=x0-.3, y=1.5,
                text="Tail Lift",
                showarrow=False,
                font=dict(color=CLASS_RED, size=12),
                xshift=10
                )

        dx = -L * np.sin(beta_rad)
        dy =  L * np.cos(beta_rad)

        fig_top.add_annotation(
            x=x0 , y=y0 - dy,   # arrow tip
            ax=x0 - 5*dx, ay=y0,           # baser
            xref="x", yref="y",
            axref="x", ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=CLASS_YELLOW
        )

        # Label for V∞
        fig_top.add_annotation(
            x=x0 + 0.5, y=y0 - dy,
            text="V∞",
            showarrow=False,
            font=dict(color=CLASS_YELLOW, size=12),
            xshift=10
        )

        
        # Beta label
        fig_top.add_annotation(
            x=x0 - 1.0, y=y0-dy,
            text=f"β = {beta:.1f}°",
            font=dict(color=CLASS_YELLOW, size=14),
            showarrow=False
        )
        fig_top.add_vline(x=10, line_dash="dash", line_color=ACAD_GREY, layer="below")
        fig_top.update_layout(
            paper_bgcolor=BG_PRIMARY,
            plot_bgcolor=BG_SECONDARY,
            xaxis=dict(range=[0,20], visible=False),
            yaxis=dict(range=[0,10], visible=False),
            height=600,
            margin=dict(l=0,r=0,t=0,b=0)
        )

        st.markdown('<div class="eq-label">Yawing Response</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_top, width="stretch")

    # ── CN vs Beta ──────────────────────────────────────────────
    with col2:

        beta_range = np.linspace(-5, 5, 100)
        CN = CN_slope * beta_range

        fig_cn = go.Figure()

        fig_cn.add_trace(go.Scatter(
            x=beta_range,
            y=CN,
            mode='lines',
            line=dict(color=color, width=3),
            name="C_N(β)"
        ))

        # Tracking point
        CN_current = CN_slope * beta
        fig_cn.add_trace(go.Scatter(
            x=[beta],
            y=[CN_current],
            mode='markers',
            marker=dict(size=10, color=CLASS_YELLOW),
            name="Current"
        ))

        fig_cn.add_hline(y=0, line_dash="dash", line_color=ACAD_GREY)
        fig_cn.add_vline(x=0, line_dash="dash", line_color=ACAD_GREY)

        fig_cn.update_layout(
            paper_bgcolor=BG_PRIMARY,
            plot_bgcolor=BG_SECONDARY,
            height=350,
            title=f"C_N vs β  —  {stability}",
            xaxis=dict(title="β (deg)", color=ACAD_GREY),
            yaxis=dict(title="C_N", color=ACAD_GREY),
            margin=dict(l=0,r=0,t=30,b=0)
        )

        st.plotly_chart(fig_cn, width="stretch")

    # ===========================================================
    # ── AFT VIEW (Rolling) ─────────────────────────────────────
    # ===========================================================
    col3, col4 = st.columns(2)

    with col3:

        fig_aft = go.Figure()

        fig_aft.add_layout_image(
            dict(
                source=img2,
                xref="x", yref="y",
                x=0, y=7,
                sizex=20, sizey=20,
                sizing="contain",
                opacity=0.8,
                layer="below"
            )
        )
        fig_aft.add_annotation(
            x=x0 , y=y0 - 3,   # arrow tip
            ax=x0 - 5*dx, ay=y0,           # base
            xref="x", yref="y",
            axref="x", ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=CLASS_YELLOW
        )

        # Label for V∞
        fig_aft.add_annotation(
            x=x0 + 0.5, y=y0 - 3,
            text="V∞",
            showarrow=False,
            font=dict(color=CLASS_YELLOW, size=12),
            xshift=10
        )
        # Differential lift
        lift_diff = CL_slope * beta

        # Left wing
        fig_aft.add_annotation(
            x=3, y=2 + 3*(1 + lift_diff),
            ax=3, ay=2,
            xref="x", yref="y",
            axref="x", ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowwidth=4,
            arrowcolor=USAFA_BLUE
        )

        # Right wing
        fig_aft.add_annotation(
            x=17, y=2 + 3*(1 - lift_diff),
            ax=17, ay=2,
            xref="x", yref="y",
            axref="x", ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowwidth=4,
            arrowcolor=USAFA_BLUE
        )

        fig_aft.add_annotation(
            x=8.5, y=7,
            text=f"β = {beta:.1f}°",
            font=dict(color=CLASS_YELLOW, size=14),
            showarrow=False
        )
        fig_aft.add_vline(x=10, line_dash="dash", line_color=ACAD_GREY, layer="below")
        fig_aft.update_layout(
            paper_bgcolor=BG_PRIMARY,
            plot_bgcolor=BG_SECONDARY,
            xaxis=dict(range=[0,20], visible=False),
            yaxis=dict(range=[0,10], visible=False),
            height=350,
            margin=dict(l=0,r=0,t=0,b=0)
        )

        st.markdown('<div class="eq-label">Rolling Response</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_aft, width="stretch")

    # ── CL (rolling moment) vs Beta ─────────────────────────────
    with col4:

        CL = CL_slope * beta_range

        fig_cl = go.Figure()

        fig_cl.add_trace(go.Scatter(
            x=beta_range,
            y=CL,
            mode='lines',
            line=dict(color=color, width=3),
            name="C_L(β)"
        ))

        CL_current = CL_slope * beta

        fig_cl.add_trace(go.Scatter(
            x=[beta],
            y=[CL_current],
            mode='markers',
            marker=dict(size=10, color=CLASS_YELLOW),
            name="Current"
        ))

        fig_cl.add_hline(y=0, line_dash="dash", line_color=ACAD_GREY)
        fig_cl.add_vline(x=0, line_dash="dash", line_color=ACAD_GREY)
        fig_cl.update_layout(
            paper_bgcolor=BG_PRIMARY,
            plot_bgcolor=BG_SECONDARY,
            height=350,
            title=f"C_L vs β  —  {stability}",
            xaxis=dict(title="β (deg)", color=ACAD_GREY),
            yaxis=dict(title="C_L", color=ACAD_GREY),
            margin=dict(l=0,r=0,t=30,b=0)
        )

        st.plotly_chart(fig_cl, width="stretch")
render_plots(stability)
st.divider()

# ── Intuition ────────────────────────────────────────────────────────────────
with st.expander("💡  Physical Intuition"):
    st.markdown("""
    **What is Going On?**
    - For both axis, positive stability is that which reduces the side-slip. In yaw, canceling out the β by yawing towards the freestream velocity,
    and in roll, by rolling to move the freestream inline with the aircrafts nose (x-axis).
            
    """)
    st.markdown("""
    **Why Lateral and Directional Together**

    - Due to the asymmetric lift generated by sideslip angles, roll and yaw are coupled (they effect each other), so are typically
        discussed together.

    **Aircraft Design Thoughts:**

    - Tall vertical tails are common across aircraft scales, why?
    - The F-4 has wings with dihedral tips and a tail with anhedral, what's going on?
            
    """)