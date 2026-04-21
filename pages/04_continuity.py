import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from utils.usafa_styles import *
st.set_page_config(page_title="Continuity - Virtual Lab", page_icon="➡️", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()

st.markdown('<div class="page-title">Continuity Equation</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Fluid Flow Properties</div>', unsafe_allow_html=True)

with st.expander("📖  Governing Equations", expanded=True):
    col_eq1, col_eq2 = st.columns(2)

    with col_eq1:
        st.markdown('<div class="eq-label">Mass Flow Rate</div>', unsafe_allow_html=True)
        st.latex(r"\dot{m}=\rho AV")
        st.markdown("""
        <div class="explainer">
        Mass flow rate (ṁ) is defined as the rate at which a mass is flowing through a plane perpendicular to
        a 1-D steady flow. 
        </div>
        """, unsafe_allow_html=True)

    with col_eq2:
        st.markdown('<div class="eq-label">Continuity Equation</div>', unsafe_allow_html=True)
        st.latex(r"\rho_1A_1V_1=\rho_2A_2V_2")
        st.markdown("""
        <div class="explainer">
        In a steady flow, the mass flow equation implies that the mass flow at any two points in the flow
        must be equal. Therefore, the continuity equation is a representation of the conservation of mass
        in the flow. 
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Station 1 reference values (fixed) ───────────────────────────
rho1 = 1.225    # kg/m³  (SSL)
A1   = 1.0      # m²
V1   = 10.0     # m/s

mdot = rho1 * A1 * V1

st.markdown("### Station 2 Controls")
sl_col1, sl_col2 = st.columns(2)
with sl_col1:
    st.markdown("**Area (m²)**")
    A2 = st.slider("A2", min_value=0.5, max_value=5.0,
                   value=1.0, step=0.01,
                   format="A₂ = %.2f m²",
                   label_visibility="collapsed")
with sl_col2:
    st.markdown("**Density (kg/m³)**")
    rho2 = st.slider("rho2", min_value=0.5, max_value=3.0,
                     value=1.225, step=0.001,
                     format="ρ₂ = %.3f kg/m³",
                     label_visibility="collapsed")

@st.fragment
def render_visual(rho1, A1, V1, rho2, A2):

    mdot = rho1 * A1 * V1
    V2   = mdot / (rho2 * A2)

    # --- Figure setup ---
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor(BG_PRIMARY)
    ax.set_facecolor(BG_PRIMARY)

    # --- Tube geometry ---
    x1, x2 = -2.5, 2.5

    h1 = 1.0
    h2 = A2 / A1  # scale height

    # Tube walls
    ax.plot([x1, x1], [-h1/2, h1/2], color=ACAD_WHITE)
    ax.plot([x2, x2], [-h2/2, h2/2], color=ACAD_WHITE)

    # Top & bottom lines
    ax.plot([x1, x2], [h1/2, h2/2], color=ACAD_GREY, alpha=0.6)
    ax.plot([x1, x2], [-h1/2, -h2/2], color=ACAD_GREY, alpha=0.6)

    # --- Particles (density) ---
    def draw_particles(x_center, height, density, color):
        n = int(40 * density / rho1)  # relative scaling
        xs = x_center + 0.3 * (np.random.rand(n) - 0.5)
        ys = height * (np.random.rand(n) - 0.5)
        ax.scatter(xs, ys, s=10, color=color, alpha=0.8)

    draw_particles(x1, h1, rho1, GROTTO_BLUE)
    draw_particles(x2, h2, rho2, CLASS_YELLOW)

    # --- Velocity arrows ---
    def draw_arrow(x, height, velocity, color):
        ax.arrow(
            x - 0.8, 0,
            .4 * velocity / V1, 0,  # normalized
            head_width=0.15,
            head_length=0.2,
            fc=color, ec=color,
            linewidth=2
        )

    draw_arrow(x1, h1, V1, GROTTO_BLUE)
    draw_arrow(x2-0.2, h2, V2, CLASS_YELLOW)

    # --- Labels ---
    ax.text(x1, -1.2, f"ρ₁={rho1:.2f} kg/m³\nA₁={A1:.2f} m²\nV₁={V1:.2f} m/s",
            color=ACAD_WHITE, ha='center', fontsize=9)

    ax.text(x2, -h2/2-.5, f"ρ₂={rho2:.2f} kg/m³\nA₂={A2:.2f} m²\nV₂={V2:.2f} m/s",
            color=ACAD_WHITE, ha='center', fontsize=9)

    # --- Styling ---
    ax.set_xlim(-4, 4)
    ax.set_ylim(-2, 2)
    ax.axis('off')

    plt.tight_layout()
    st.pyplot(fig, width='stretch')
    plt.close(fig)

render_visual(rho1,A1,V1, rho2,A2)

st.divider()
with st.expander("💡  Physical Interpretation"):
    st.markdown("""
        **Practical Intuition**

        - When the area at station 2 decreases, if the density stays constant the flow must accelerate.
        - This is analgous to covering the end of a hose partially with your thumb, since water is incompressible
            the decreased area at the mouth of the hose forces the fluid to accelerate.
        """)