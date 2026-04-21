import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
st.set_page_config(page_title="Pitot Static System - Virtual Lab", page_icon="💨", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()


st.markdown('<div class="page-title">Pitot Static Systems</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Applying Bernoulli to Aircraft Systems</div>', unsafe_allow_html=True)

with st.expander("📖  Governing Equations", expanded=True):
    col_eq1, col_eq2 = st.columns(2)

    with col_eq1:
        st.markdown('<div class="eq-label">Bernoulli Equation for Pitot Static System</div>', unsafe_allow_html=True)
        st.latex(r"P_0=P_\infty+\frac{1}{2}\rho V_\infty^2")
        st.markdown("""
        <div class="explainer">
        A pitot tube stops the air to find the total pressure (P₀), and measures the static pressure with
        ports parallel to the free stream. This allows for the calculation of the free stream velocity.
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"V_\infty=\sqrt{\frac{2(P_0-P_\infty)}{\rho}}")

    with col_eq2:
        st.markdown('<div class="eq-label">Limitations</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="explainer">
        The placement and design of the pitot tube are critical to the accuracy of the calculations.
        The next lab details the necessary adjustments due to the limitations of a pitot static system.
        </div>
        """, unsafe_allow_html=True)
st.divider()

col_airspeed, col_gap, col_altitude = st.columns([1, 0.5,1])

with col_airspeed:
    st.markdown("**Set Free Stream Pressure**")
    airspeed_slider = st.slider("Free Stream Pressure (psi)", min_value= 0.0, max_value = 50.0,
                      value = 14.7, step = 0.1,
                      format="P = %.2f psi",
                      label_visibility="collapsed")
with col_altitude:
    st.markdown("**Set Altitude**")
    altitude_slider = st.slider("Altitude (ft)", min_value= 0, max_value = 30000,
                      value = 5000, step = 1,
                      format="Alt = %.2f ft",
                      label_visibility="collapsed")