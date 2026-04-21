import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
from utils.usafa_styles import *
import numpy as np
import matplotlib.pyplot as plt
st.set_page_config(page_title="Bernoulli Equation - Virtual Lab", page_icon="🧔🏼", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()

st.markdown('<div class="page-title">Bernoulli Equation</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Total Pressure = Static + Dynamic</div>', unsafe_allow_html=True)

with st.expander("📖  Governing Equations", expanded=True):
    col_eq1, col_eq2 = st.columns(2)

    with col_eq1:
        st.markdown('<div class="eq-label">Bernoulli Equation</div>', unsafe_allow_html=True)
        st.latex(r"P_1 + q_1 = P_2+q_2=P_0")
        st.markdown('<div class="eq-label">Dynamic Pressure</div>', unsafe_allow_html=True)
        st.latex(r"q=\frac{1}{2}\rho V^2")
        st.markdown("""
        <div class="explainer">
        The total pressure is equal to the static pressure and the dynamic pressure added together.
        The dynamic pressure (q) is determined by the velocity of the fluid and its density.
        </div>
        """, unsafe_allow_html=True)

    with col_eq2:
        st.markdown('<div class="eq-label">Assumptions</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="explainer">
        1. Steady - no change with respect to time<br>
        2. Inviscid - no viscosity (friction forces)<br>
        3. Incompressible - constant density<br>
        4. Flow along a streamline<br>
        5. No body forces - neglects gravity and others inside the fluid<br>
        </div>
        """, unsafe_allow_html=True)

st.divider()

V2_slider = st.slider("Velocity 2 Control (m/s)", min_value= 0.0, max_value = 100.0,
                      value = 20.0, step = .01,
                      format="V₂ = %.2f m/s",
                      label_visibility="collapsed")

@st.fragment
def render_calcs(V2):
    P1 = 101325
    rho_air = 1.1225 #kg/m^3
    A1 = 2 #m^2
    V1 = 20 #m/s
    V2 = V2_slider
    A2 = (V1 / (V2 + 1E-2)) * A1 
    P0 = P1 + 0.5 * rho_air * V1 **2
    P2 = P0 - 0.5 * rho_air * V2 **2

    def draw_arrow(x, height, velocity, color):
        ax.arrow(
            x - 0.8, 0,
            .4 * velocity / V1, 0,  # normalized
            head_width=0.15,
            head_length=0.2,
            fc=color, ec=color,
            linewidth=2
        )

    # --- 3. Plotting ---
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor(BG_PRIMARY)
    ax.set_facecolor(BG_PRIMARY)

    # DRAW VENTURI TUBE (Top Section)
    if A2/A1 > 15:
        area_rule = 15
    else:
        area_rule = A2/A1
    x_tube = np.array([-3, -1, 1, 3])
    y_top = np.array([1, 1, area_rule, area_rule]) # Simplified geometry
    ax.plot(x_tube, y_top, color=ACAD_WHITE, lw=2)
    ax.plot(x_tube, -y_top, color=ACAD_WHITE, lw=2)
    
    draw_arrow(-3, 0, V1, GROTTO_BLUE)
    draw_arrow(1.8, 0, V2, CLASS_YELLOW)

    if A2/A1 > 1.31:
        y_pos_label = -2.8
    else:
        y_pos_label = -2
    ax.text(-3, -2, f"P₁: {P1:.1f} Pa\nA₁={A1:.2f} m²\nV₁={V1:.2f} m/s", color=ACAD_WHITE, ha='center')
    ax.text(3, y_pos_label, f"P₂: {P2:.1f} Pa\nA₂={A2:.2f} m²\nV₂={V2:.2f} m/s", color=CLASS_YELLOW, ha='center')
    ax.text(0, 2, f"P₀: {P0:.1f} Pa", color=CLASS_RED, ha='center', fontweight='bold')

    ax.set_ylim(-2, 2)
    ax.axis('off')
    st.pyplot(fig)
render_calcs(V2_slider)

st.divider()
with st.expander("💡  Physical Interpretation"):
    st.markdown("""
        **Conservation of Energy**
        - Since energy is conserved inside the fluid, as it accelerates some if its energy becomes kinetic energy
            lowering the pressure of the fluid.
        """)
    st.markdown("""
        **Practical Consideration**
        - What value are you left with if you stop the flow? Can this be useful in determining
         your altitude?
        """)