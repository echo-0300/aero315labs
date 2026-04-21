import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
from utils.usafa_styles import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

st.set_page_config(page_title="Stream Tube - Virtual Lab", page_icon="💧", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()

st.markdown('<div class="page-title">Stream Tube Lab</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Venturi Effect</div>', unsafe_allow_html=True)

# Equations (static/expander)
with st.expander("📖  Governing Equations", expanded=True):
    col_eq1, col_eq2 = st.columns(2)

    with col_eq1:
        st.markdown('<div class="eq-label">Incompressible Continuity Equation</div>', unsafe_allow_html=True)
        st.latex(r"V_2=\frac{A_1 V_1}{A_2}")
        st.markdown("""
        <div class="explainer">
        When a flow is assumed to be incompressible the density can be cancelled out, resulting in the
        velocity at station 2 depending on the ratio between the areas.
        </div>
        """, unsafe_allow_html=True)

    with col_eq2:
        st.markdown('<div class="eq-label">Manometry Reminder</div>', unsafe_allow_html=True)
        st.latex(r"\delta h = \frac{P_1-P_2}{\rho g}")
        st.markdown("""
        <div class="explainer">
        The changing velocity of the flow changes the pressure, which can be seen in the changing height
        of the water column.
        </div>
        """, unsafe_allow_html=True)

st.divider()
A2_slider = st.slider("Area 2 Control (ft²)", min_value= 0.5, max_value = 3.0,
                      value = 1.0, step = .01,
                      format="A₂ = %.2f m²",
                      label_visibility="collapsed")
@st.fragment
def render_venturi_lab(A2):
    P1 = 2116.22      # psf (Fixed Station 1)
    V1 = 50.0         # ft/s
    A1 = 2.0          # ft^2
    rho_water = 1.94  # slug/ft^3 (Manometer Fluid)
    rho_air = .00237
    g = 32.2
    
    V2 = (A1 * V1) / A2
    
    P2 = P1 + 0.5 * rho_air * (V1**2 - V2**2)
    
    delta_h = (P1 - P2) / (rho_water * g)
    
    # Manometer heights (relative to a center line)
    h_base = 2.0
    h1 = h_base - 0.5 * delta_h
    h2 = h_base + 0.5 * delta_h

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
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(BG_PRIMARY)
    ax.set_facecolor(BG_PRIMARY)

    # DRAW VENTURI TUBE (Top Section)
    x_tube = np.array([-3, -1, 1, 3])
    y_top = np.array([1, 1, A2/A1, A2/A1]) # Simplified geometry
    ax.plot(x_tube, y_top, color=ACAD_WHITE, lw=2)
    ax.plot(x_tube, -y_top, color=ACAD_WHITE, lw=2)
    
    draw_arrow(-3, h1, V1, GROTTO_BLUE)
    draw_arrow(2-0.2, h2, V2, CLASS_YELLOW)

    # DRAW MANOMETER (Bottom Section)
    m_x_left, m_x_right = -2, 2
    wall_w = 0.2
    # Manometer Walls
    for x in [m_x_left, m_x_right]:
        ax.plot([x-wall_w, x-wall_w], [-1.5, -4], color=ACAD_GREY)
        ax.plot([x+wall_w, x+wall_w], [-1.5, -4], color=ACAD_GREY)
    ax.plot([m_x_left-wall_w, m_x_right+wall_w], [-4, -4], color=ACAD_GREY)

    # Fluid Fill
    ax.add_patch(mpatches.Rectangle((m_x_left-wall_w, -4), wall_w*2, h1, color=GROTTO_BLUE, alpha=0.6))
    ax.add_patch(mpatches.Rectangle((m_x_right-wall_w, -4), wall_w*2, h2, color=GROTTO_BLUE, alpha=0.6))
    ax.add_patch(mpatches.Rectangle((m_x_left+wall_w, -4), m_x_right-m_x_left-wall_w*2, 0.5, color=GROTTO_BLUE, alpha=0.6))

    # --- 4. Labels and Interaction ---
    ax.text(m_x_left, -1.2, f"P₁: {P1:.1f} psf", color=ACAD_WHITE, ha='center')
    ax.text(m_x_right, -1.2, f"P₂: {P2:.1f} psf", color=CLASS_YELLOW, ha='center')
    ax.text(0, -3.3, f"Δh: {abs(delta_h):.3f} ft", color=CLASS_RED, ha='center', fontweight='bold')

    ax.set_ylim(-4.5, 2)
    ax.axis('off')
    st.pyplot(fig)


render_venturi_lab(A2_slider) 
st.divider()
with st.expander("💡  Physical Interpretation"):
    st.markdown("""
        **Counter Intuitive Idea**
        - The faster a fluid flows, the lower its internal pressure. This will be made
          more clear with the Bernoulli Equation, covered in the next lab.
        """)
    st.markdown("""
        **Practical Implication**
        - This effect explains why objects are pulled towards fast moving flow, like trash
        getting sucked out the window of a car.
        """)