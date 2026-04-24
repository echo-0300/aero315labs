import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
from utils.usafa_styles import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(page_title="3D Wing Lift - Virtual Lab", page_icon="🛩️", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()

st.markdown('<div class="page-title">3D Wing Lift</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Finite Wing Effects with NACA 2412</div>', unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────
cl_alpha_2d = 0.105  # per degree
alpha0 = -2.0        # degrees

# ── Governing Concepts ────────────────────────────────────────
with st.expander("📖 Governing Concepts", expanded=True):
    col_1, col_2 = st.columns(2)
    with col_1:
        st.markdown(f"""
        <div class="explainer">
        This module uses a <b>NACA 2412</b> airfoil with:
        <br><br>
        Lift curve slope: <b>c<sub>lα</sub> = {cl_alpha_2d}</b> per degree  
        Zero-lift angle: <b>α₀ = {alpha0}°</b>
        <br><br>
        Finite wing effects reduce lift slope due to induced drag, resulting in a lift curve slope of:
        </div>
        """, unsafe_allow_html=True)

        st.latex(r"""
        C_{L_\alpha} = \frac{c_{l_\alpha}}{1 + \frac{56.7\frac{^\circ}{rad}c_{l_\alpha}}{\pi e AR}}
        """)
    with col_2:
        st.markdown("""
        <div class="explainer">
        The airfoil lift curve must also be adjusted for compressibility effects as M increases:
        </div>
        """, unsafe_allow_html=True)

        st.latex(r"""
        c_l = \frac{c_{l, M=0}}{\sqrt{1 - M^2}}
        """)
        st.markdown("""
        <div class="explainer">
        The aspect ratio of the wing as well as its span efficiency factor are two primary ways of improving wing performance:
        </div>
        """, unsafe_allow_html=True)

        st.latex(r"""
        AR = \frac{b^2}{c}
        """)

st.divider()

# ── Sliders ───────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Mach Number (M)**")
    M = st.slider("M", 0.0, 0.85, 0.2, step=0.01, label_visibility="collapsed")

with col2:
    st.markdown("**Aspect Ratio (AR)**")
    AR = st.slider("AR", 2.0, 15.0, 8.0, step=0.5, label_visibility="collapsed")

with col3:
    st.markdown("**Oswald Efficiency (e)**")
    e = st.slider("e", 0.5, 1.0, 0.8, step=0.01, label_visibility="collapsed")

@st.fragment
def render_plot(M, AR, e) -> None:
    # ── Angle Sweep ───────────────────────────────────────────────
    alpha = np.linspace(-10, 15, 100)
    fig, (ax_plan, ax_lift) = plt.subplots(
    2, 1,
    figsize=(6, 8),
    gridspec_kw={"height_ratios": [1, 2]}
    )

    fig.patch.set_facecolor(BG_PRIMARY)

    # ── PLANFORM (Top Plot) ───────────────────────────────────────
    ax_plan.set_facecolor(BG_PRIMARY)

    chord = 3.0
    span = AR * chord

    # Center the wing at origin
    y0 = -chord / 2
    x0 = -span / 2

    rect = mpatches.Rectangle(
        (x0, y0),
        span,
        chord,
        linewidth=2,
        edgecolor=CLASS_ROYAL,
        facecolor='none'
    )

    ax_plan.add_patch(rect)

    # Formatting
    ax_plan.set_aspect('equal', adjustable='box')
    ax_plan.set_title("Rectangular Wing Planform", color=ACAD_GREY)

    ax_plan.set_xlabel("Spanwise Direction", color=ACAD_GREY)
    ax_plan.set_ylabel("Chord (c=3)", color=ACAD_GREY)

    ax_plan.tick_params(axis='x', labelcolor=ACAD_GREY)
    ax_plan.tick_params(axis='y', labelcolor=ACAD_GREY)

    ax_plan.grid(True, linestyle='--', alpha=0.4)

    # Optional: set limits with padding
    ax_plan.set_xlim(-25,25)
    ax_plan.set_ylim(-2,2)
    # 2D incompressible
    cl_M0 = cl_alpha_2d * (alpha - alpha0)

    # Compressibility correction
    beta = np.sqrt(1 - M**2) if M < 1 else np.nan
    cl_comp = cl_M0 / beta

    # Finite wing correction
    CL_alpha = cl_alpha_2d / (1 + (cl_alpha_2d * 57.3 / (np.pi * e * AR)))
    CL = CL_alpha * (alpha - alpha0) / beta

    # ── Plot ──────────────────────────────────────────────────────
    fig1, ax1 = plt.subplots()
    fig1.patch.set_facecolor(BG_PRIMARY)
    ax1.set_facecolor(BG_PRIMARY)
    fig.patch.set_facecolor(BG_PRIMARY)
    ax_lift.set_facecolor(BG_PRIMARY)

    ax_lift.plot(alpha, cl_M0, label="$c_l$ (M=0)", color=CLASS_ROYAL, linewidth=2)
    ax_lift.plot(alpha, cl_comp, label="$c_l$ (compressible)", color=CLASS_YELLOW, linewidth=2)
    ax_lift.plot(alpha, CL, label="$C_L$ (finite wing)", color=CLASS_RED, linewidth=2)

    ax_lift.set_xlabel("Angle of Attack ($\circ$)", color=ACAD_GREY)
    ax_lift.set_ylabel("Lift Coefficient", color=ACAD_GREY)

    ax_lift.tick_params(axis='x', labelcolor=ACAD_GREY)
    ax_lift.tick_params(axis='y', labelcolor=ACAD_GREY)

    ax_lift.grid(True, linestyle='--', alpha=0.6)
    ax_lift.set_xlim(-3,10)
    ax_lift.set_ylim(-0.5, 3)
    ax_lift.legend()

    st.pyplot(fig)

render_plot(M, AR, e)

st.divider()
with st.expander("💡  Physical Interpretation"):
    st.markdown("""
        **Airfoil Lift v. Wing Lift**

        - Airfoil values are idealized, not accounting for induced drag and other inefficiencies.
        - The full aircraft lift curve slope will always be less than that of its airfoil.
        """)
    st.markdown("""
        **Aspect Ratio and Oswald Effieciency**

        - Increasing both of these values decreases the amount of induced drag due to lift, and increase the
                lift curve slope of the wing.
        """)