import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from ambiance import Atmosphere


st.set_page_config(page_title="Standard Atmosphere - Virtual Lab", page_icon="🌡️", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()

st.markdown('<div class="page-title">Standard Atmosphere</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Lapse Rates  &nbsp;·&nbsp;  Speed of Sound</div>', unsafe_allow_html=True)

with st.expander("📖  Governing Equations", expanded=True):
    col_eq1, col_eq2 = st.columns(2)

    with col_eq1:
        st.markdown('<div class="eq-label">Gradient Layer Pressures and Densities</div>', unsafe_allow_html=True)
        st.latex(r"\frac{P}{P_1}=\left ( \frac{T}{T_1}\right )^{-\frac{g}{T_h R}}")
        st.latex(r"\frac{\rho}{\rho_1}=\left ( \frac{T}{T_1}\right )^{-\frac{g}{T_h R}+1}")
        
        st.markdown('<div class="eq-label">Isothermal Layer Pressures and Densities</div>', unsafe_allow_html=True)
        st.latex(r"\frac{P}{P_1}=e^{-\frac{g}{RT}(h-h_1)}")
        st.latex(r"\frac{\rho}{\rho_1}=e^{-\frac{g}{RT}(h-h_1)}")
        st.markdown("""
        <div class="explainer">
        The atmosphere is divided into layers where the temperature behaves differently. In layers
        where the temperature varies with altitude (the troposphere where we live), the first two equations
        apply. In layers where the temperature is constant (tropopause), the second two equations apply.
        
        The subscript 1 indicates the value at the bottom of the layer being solved for. So in a troposphere
        problem, the subscript 1 indicates mean sea level.
        </div>
        """, unsafe_allow_html=True)

    with col_eq2:
        st.markdown('<div class="eq-label">Standard Atmosphere Tables &amp; Speed of Sound</div>', unsafe_allow_html=True)
        st.latex(r" a = \sqrt{\gamma R T}")
        st.markdown("""
        <div class="explainer">
        The speed of sound (a) varies with the temperature of the medium as well as its ratio of specific heats (γ).
        In the tabulation of standard atmosphere data in Appendix B, the value of a is shown as well. 
        </div>
        """, unsafe_allow_html=True)

st.divider()

ctrl_col, gap_col, slider_col = st.columns([.5, 0.5,2])
with ctrl_col:
    st.markdown("**Select Units**")
    units = st.selectbox("Unit Type?",options=("SI","Imperial"), label_visibility = "hidden")
    match units:
         case "SI":
              alt_units = "m"
              alt_max = 47000.00
         case "Imperial":
              alt_units = "ft"
              alt_max = 150000.00
with slider_col:
    st.markdown("**Altitude**")
    alt_slide = st.slider(
        label="mach_slider",
        min_value=0.0, max_value=alt_max,
        value=0.0, step=0.01,
        format="M = %.2f",
        label_visibility="collapsed",
        key="mach"
    )

def render_atmosphere(alt_slide: float, units: str) -> None:
    """
    alt_slide : current altitude in feet (imperial) or meters (SI)
    units     : 'Imperial' or 'SI'
    """

    # ── Unit conversion ───────────────────────────────────────────
    # ambiance works in meters
    if units == 'Imperial':
        alt_m      = alt_slide * 0.3048
        alt_label  = 'Altitude (ft)'
        t_label    = 'Temperature (°R)'
        p_label    = 'Pressure (psf)'
        rho_label  = 'Density (slug/ft³)'
        alt_max_m  = 47000          # ~154,000 ft, top of ambiance range
    else:
        alt_m      = alt_slide
        alt_label  = 'Altitude (m)'
        t_label    = 'Temperature (K)'
        p_label    = 'Pressure (Pa)'
        rho_label  = 'Density (kg/m³)'
        alt_max_m  = 47000

    # ── Build profile arrays ──────────────────────────────────────
    alt_array_m = np.linspace(0, alt_max_m, 500)
    atm_array   = Atmosphere(alt_array_m)
    T_array     = atm_array.temperature          # K
    P_array     = atm_array.pressure             # Pa
    rho_array   = atm_array.density              # kg/m³

    # Convert profile to display units
    if units == 'Imperial':
        alt_disp   = alt_array_m / 0.3048
        T_disp     = T_array * 1.8               # K → °R
        P_disp     = P_array * 0.020885          # Pa → psf
        rho_disp   = rho_array * 0.00194032      # kg/m³ → slug/ft³
        alt_m_mark = alt_m
        alt_disp_mark = alt_slide
    else:
        alt_disp      = alt_array_m
        T_disp        = T_array
        P_disp        = P_array
        rho_disp      = rho_array
        alt_m_mark    = alt_m
        alt_disp_mark = alt_slide

    # ── Current state ─────────────────────────────────────────────
    atm_pt  = Atmosphere(alt_m_mark)
    T_pt    = atm_pt.temperature[0]
    P_pt    = atm_pt.pressure[0]
    rho_pt  = atm_pt.density[0]

    if units == 'Imperial':
        T_pt   = T_pt   * 1.8
        P_pt   = P_pt   * 0.020885
        rho_pt = rho_pt * 0.00194032

    # ── Layer definitions (in meters) ─────────────────────────────
    layers = [
        (0,     11000,  'Troposphere',   '#003594', 0.18),
        (11000, 20000,  'Tropopause',    '#002554', 0.25),
        (20000, 32000,  'Stratosphere',  '#001d47', 0.20),
        (32000, 47000,  'Stratosphere II',     '#001433', 0.15),
    ]

    # ── Colors ────────────────────────────────────────────────────
    from utils.usafa_styles import (USAFA_BLUE, CLASS_YELLOW, CLASS_RED,
                                    GROTTO_BLUE, ACAD_GREY, BG_PRIMARY)
    LAYER_COLORS = [l[3] for l in layers]

    # ── Figure ────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(9, 4),
                             sharey=True,
                             gridspec_kw={'wspace': 0.08})
    fig.patch.set_facecolor(BG_PRIMARY)

    plot_data = [
        (axes[0], T_disp,   T_pt,   t_label,   CLASS_RED,    'TEMPERATURE'),
        (axes[1], P_disp,   P_pt,   p_label,   GROTTO_BLUE,  'PRESSURE'),
        (axes[2], rho_disp, rho_pt, rho_label, CLASS_YELLOW, 'DENSITY'),
    ]

    for ax, profile, pt_val, xlabel, color, title in plot_data:
        ax.set_facecolor(BG_PRIMARY)

        # Layer shading
        for (bot_m, top_m, name, lcolor, alpha) in layers:
            if units == 'Imperial':
                bot_d = bot_m / 0.3048
                top_d = top_m / 0.3048
            else:
                bot_d, top_d = bot_m, top_m
            top_d = min(top_d, alt_disp[-1])
            ax.axhspan(bot_d, top_d, color=lcolor, alpha=alpha, zorder=1)

        # Profile line
        ax.plot(profile, alt_disp, color=color, linewidth=1.8, zorder=3)

        # Current altitude marker line
        ax.axhline(alt_disp_mark, color=ACAD_GREY,
                   linewidth=1.0, linestyle='--', alpha=0.7, zorder=4)

        # Current value dot
        ax.plot(pt_val, alt_disp_mark, 'o',
                color=color, markersize=7, zorder=5)

        # Drop line to x-axis
        ax.plot([pt_val, pt_val], [0, alt_disp_mark],
                color=color, linewidth=0.8, linestyle=':',
                alpha=0.5, zorder=4)

        # Current value label
        ax.text(pt_val, alt_disp_mark + 3000,
                f'{pt_val:.3f}',
                color="#ffffff", fontsize=7, fontfamily='monospace',
                ha='center', va='bottom', zorder=6)

        # Axes styling
        ax.set_xlabel(xlabel, color=ACAD_GREY,
                      fontfamily='monospace', fontsize=7)
        ax.set_title(title, color=color,
                     fontfamily='monospace', fontsize=8,
                     fontweight='bold', pad=6)
        ax.tick_params(colors=ACAD_GREY, labelsize=6)
        for spine in ax.spines.values():
            spine.set_edgecolor('#003080')

    # ── Shared y-axis label and layer annotations (left panel only) ──
    axes[0].set_ylabel(alt_label, color=ACAD_GREY,
                       fontfamily='monospace', fontsize=7)

    for (bot_m, top_m, name, _, _) in layers:
        mid_m = (bot_m + top_m) / 2
        mid_d = mid_m / 0.3048 if units == 'Imperial' else mid_m
        if mid_d < alt_disp[-1]:
            axes[0].text(-0.6, mid_d, name,
                         transform=axes[0].get_yaxis_transform(),
                         color=ACAD_GREY, fontsize=6,
                         fontfamily='monospace', va='center',
                         alpha=0.8)

    
    st.pyplot(fig, width='stretch')
    plt.close(fig)

render_atmosphere(alt_slide, units)