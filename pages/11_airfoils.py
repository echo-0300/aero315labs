import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
from utils.usafa_styles import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from utils.airfoils import Airfoil

st.set_page_config(page_title="Airfoils - Virtual Lab", page_icon="🪽", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()

st.markdown('<div class="page-title">NACA Airfoil Geometry</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Camber and Thickness</div>', unsafe_allow_html=True)

with st.expander("📖  Governing Concepts", expanded=True):
    col_eq1, col_eq2 = st.columns(2)

    with col_eq1:
        st.markdown('<div class="eq-label">NACA 4 Digit Airfoils</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="explainer">
        The NACA 4-Digit airfoil series defines three parameters with its digits. The airfoils are 
        normalized by the chord length so all of the parameters are in reference to the chord:
        <br>
        1. <b>First Digit</b> - Maximum Camber - percentage of chord
        <br>
        2. <b>Second Digit</b> - Position of Maximum Camber - tenths of chord
        <br>
        3. <b>Third/Fourth Digits</b> - Maximum Thickness - percentage of chord
        </div>
        """, unsafe_allow_html=True)

    with col_eq2:
        st.markdown('<div class="eq-label">Symmetrical NACA Airfoils</div>', unsafe_allow_html=True)
        st.latex(r"00-\text{XX}")
        st.markdown("""
        <div class="explainer">
        Symmetrical airfoils have 0 values for the first two digits representing their lack of camber.
        These airfoils are typically used for horizontal or vertical tail surfaces, and are the simplest
        to design and build.
        </div>
        \n
        """, unsafe_allow_html=True)
        st.markdown('<div class="eq-label">Cambered NACA Airfoils</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="explainer">
        There are many more types of cambered airfoils, including the 4-Digit Airfoils shown in this lab.
        More complex designs include reflex airfoils with negative camber near the trail edge, supercritical
        airfoils, designed to allow for faster subsonic flight, and many more.
        </div>
        """, unsafe_allow_html=True)
st.divider()

sl_col1, sl_col2, sl_col3 = st.columns(3)

with sl_col1:
    st.markdown("**First: Max Camber**")
    d1 = st.slider("1", min_value=1.0, max_value=9.0,
                      value=0.0, step=1.0,
                      format="%.0f",
                      label_visibility="collapsed")

with sl_col2:
    st.markdown("**Second Digit: X-Position of Max Camber**")
    d2 = st.slider("2", min_value=0.0, max_value=9.0,
                    value=0.0, step=1.0,
                    format="%.0f",
                    label_visibility="collapsed")

with sl_col3:
    st.markdown("**Third/Fourth Digit: Max Thickness**")
    d34 = st.slider("34", min_value=1.0, max_value=20.0,
                      value=12.0, step=1.0,
                      format="%.0f",
                      label_visibility="collapsed")
d34 = int(d34)
if d34<10:
    d34 = str(0)+str(d34)
else:
    pass
naca = str(int(d2)) + str(int(d1)) + str(d34)

@st.fragment
def render_airfoil(naca: str) -> None:
    foil = Airfoil.NACA4(naca)
    # The library returns [ [upper_x_1, upper_x_2, ... lower_x_1, ...], [upper_y_2, lower_y_2..., lower_y_1, ...] ] 
    coords = foil.all_points 


    all_x = coords[0]
    all_y = coords[1]

    # Find the midpoint to split the upper and lower halves
    mid = len(all_x) // 2

    x_upper = all_x[:mid]
    y_upper = all_y[:mid]
    x_lower = all_x[mid:]
    y_lower = all_y[mid:]
    camber = foil.camber_line(x_upper)
    # To avoid the line through the middle, we plot them as two separate lines
    # or join them so they "loop" correctly.
    fig, ax = plt.subplots()
    fig.patch.set_facecolor(BG_PRIMARY)
    ax.set_facecolor(BG_PRIMARY)
    ax.plot(x_upper, camber, color=CLASS_RED,linewidth=2, label="Camber")
    ax.plot(x_upper, y_upper, color=GROTTO_BLUE, linewidth=2, label="Upper")
    ax.plot(x_lower, y_lower, color=GROTTO_BLUE, linewidth=2, label="Lower")
    ax.tick_params(axis='x', labelcolor=ACAD_GREY)
    ax.tick_params(axis='y', labelcolor=ACAD_GREY)
    ax.set_aspect('equal', adjustable='box')
    ax.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig)

render_airfoil(naca)