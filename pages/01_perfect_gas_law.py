import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
import utils.usafa_styles as brand
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Arc, FancyArrowPatch
import matplotlib.cm as cm

st.set_page_config(page_title="Perfect Gas Law - Virtual Lab", page_icon="💨", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()


# Page Header (static)
st.markdown('<div class="page-title">Perfect Gas Law</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Gas Properties</div>', unsafe_allow_html=True)

# Equations (static/expander)
with st.expander("📖  Governing Equations", expanded=True):
    col_eq1, col_eq2 = st.columns(2)

    with col_eq1:
        st.markdown('<div class="eq-label">Gas Property Relationship</div>', unsafe_allow_html=True)
        st.latex(r"P=\rho RT")
        st.markdown("""
        <div class="explainer">
        The ideal gas law describes the relationship between <i>pressure</i> (<b>p</b>), <i>density</i> (ρ),
        and </i>absolute temperature</i> (<b>T</b>) in an ideal gas, where <b>R</b> is the specific gas constant
        for the gas in question.
        </div>
        """, unsafe_allow_html=True)

    with col_eq2:
        st.markdown('<div class="eq-label">Unit Reminder</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="explainer">
        Ensuring that the units used for each value are standard units and are consistent
        within the Imperial or SI framework is essential.
        </div>
        """, unsafe_allow_html=True)

st.divider()

# Controls

units_col, gap_col, prob_col = st.columns([.6, 0.15, .6])
with units_col:
    st.markdown("**Select Units**")
    units = st.selectbox("Unit Type?",options=("SI","Imperial"), label_visibility = "hidden")
    match units:
        case "SI":
            st.latex(r"R_{air}=287\frac{J}{kgK}")
            R_val = 287
        case "Imperial":
            st.latex(r"R_{air}=1716\frac{ftlb}{slugR}")
            R_val = 1716
with prob_col:
    st.markdown("**Select Fixed Parameter**")
    param = st.selectbox("Fixed Param?", options=("Pressure","Density", "Temperature"), label_visibility = "hidden")
    match units, param:
        case "SI", "Pressure":
            st.latex(r"P=101325 Pa")
            press = 101325
        case "Imperial", "Pressure":
            st.latex(r"P=2116.22\text{psf}")
            press = 2116.22
        case "SI", "Density":
            st.latex(r"\rho=1.225\frac{kg}{m^3}")
            dens = 1.225
        case "Imperial", "Density":
            st.latex(r"\rho=.00237 \frac{slug}{ft^3}")
            dens = .00237
        case "SI", "Temperature":
            st.latex(r"T=288.15K")
            temp = 288.15
        case "Imperial", "Temperature":
            st.latex(r"T= 518.67R")
            temp = 518.67
def update_slider(units:str, param:str):
    match units:
        case "SI":
            unit = "SI"
        case "Imperial":
            unit = "Imp"

    match param:
        case "Pressure":
            param_name = "Temperature"
            if unit == "SI":
                param_max = 1000.00
                param_init = 288.15
                param_min = 0.01
                param_label = "K"
            else:
                param_max = 1000.00
                param_init = 518.67
                param_min = 0.01
                param_label = "R"
        case "Density":
            param_name = "Pressure"
            if unit == "SI":
                param_max = 1000000.00
                param_init = 101000.00
                param_min = 0.01
                param_label = "Pa"
            else:
                param_max = 15000.00
                param_init = 2116.22
                param_min = 0.01
                param_label = "psf"
        case "Temperature":
            param_name = "Pressure"
            if unit == "SI":
                param_max = 1000000.0
                param_init = 101000.0
                param_min = 0.01
                param_label = "Pa"
            else:
                param_max = 15000.00
                param_init = 2116.22
                param_min = 0.01
                param_label = "psf"

    return param_name, param_max, param_init, param_min, param_label

param_name, param_max, param_init, param_min, param_label = update_slider(units, param)

slide = st.slider(
        label="param_slider",
        min_value=param_min, max_value=param_max,
        value=param_init, step=0.01,
        format=f"{param_name} = %.2f{param_label}",
        label_visibility="collapsed",
        key="param"
    )


    #Fragment: Calculator/Visualization
@st.fragment
def render_calcs(slide: float, units: str, param: str) -> None:

    # ── Standard sea level constants ──────────────────────────────
    if units == "SI":
        p_ssl, rho_ssl, t_ssl = 101325.0, 1.225, 288.15
        R_val = 287
        t_unit, p_unit, rho_unit = "K", "Pa", "kg/m³"
    else:
        p_ssl, rho_ssl, t_ssl = 2116.22, 0.002377, 518.67
        R_val = 1716
        t_unit, p_unit, rho_unit = "°R", "psf", "slug/ft³"

    # ── Solve for all three state variables ───────────────────────
    if param == "Pressure":
        p_curr  = press
        t_curr  = slide
        rho_curr = p_curr / (R_val * t_curr)
        eqn_str, output_str, output_unit = r"\frac{P}{RT}", r"\rho", rho_unit

    elif param == "Temperature":
        t_curr  = temp
        p_curr  = slide
        rho_curr = p_curr / (R_val * t_curr)
        eqn_str, output_str, output_unit = r"\frac{P}{RT}", r"\rho", rho_unit

    elif param == "Density":
        rho_curr = dens
        p_curr   = slide
        t_curr   = p_curr / (rho_curr * R_val)
        eqn_str, output_str, output_unit = r"\frac{P}{\rho R}", r"T", t_unit

    final_val = rho_curr if output_str == r'\rho' else t_curr
    st.latex(fr"{output_str} = {eqn_str} = {final_val:,.4f} \text{{ }}{output_unit}")

    # ── Normalized T for colormap (0=cold, 1=hot) ─────────────────
    if units == "SI":
        t_min, t_max = 0.01, 1000.0
    else:
        t_min, t_max = 0.01, 1800.0
    normalized_T = np.clip((t_curr - t_min) / (t_max - t_min), 0, 1)

    # ── Pressure gauge range ──────────────────────────────────────
    if units == "SI":
        p_min_gauge, p_max_gauge = 0, 1000000.0
    else:
        p_min_gauge, p_max_gauge = 0, 15000.0

    # ── Layout constants ──────────────────────────────────────────
    cyl_left   = 0.1
    cyl_right  = 0.9
    cyl_bottom = 0.05
    cyl_top    = 0.85
    cyl_height = cyl_top - cyl_bottom
    cyl_width  = cyl_right - cyl_left
    wall_t     = 0.03

    # Piston position — mid stroke at std day
    piston_y = cyl_bottom + (rho_ssl / rho_curr) * (cyl_height * 0.5)
    piston_y = np.clip(piston_y, cyl_bottom + 0.05, cyl_top - 0.05)
    gas_height = piston_y - cyl_bottom

    # ── Figure ────────────────────────────────────────────────────
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5, 4),
                                   gridspec_kw={'width_ratios': [1.2, 1]})
    fig.patch.set_facecolor(brand.BG_PRIMARY)
    for ax in (ax1, ax2):
        ax.set_facecolor(brand.BG_PRIMARY)
        ax.axis('off')

    # ── AX1: Cylinder ─────────────────────────────────────────────

    # Walls
    for x, w in [(cyl_left - wall_t, wall_t),       # left
                 (cyl_right, wall_t)]:               # right
        ax1.add_patch(mpatches.Rectangle(
            (x, cyl_bottom), w, cyl_height,
            color=brand.ACAD_GREY, zorder=3))
    ax1.add_patch(mpatches.Rectangle(               # bottom
        (cyl_left - wall_t, cyl_bottom - wall_t),
        cyl_width + 2 * wall_t, wall_t,
        color=brand.ACAD_GREY, zorder=3))

    # Gas fill
    ax1.add_patch(mpatches.Rectangle(
        (cyl_left, cyl_bottom), cyl_width, gas_height,
        color=brand.USAFA_BLUE, alpha=0.15, zorder=1))

    # Scatter — fixed seed for stable positions
    n_dots = 80
    rng   = np.random.default_rng(42)
    dot_x = rng.uniform(cyl_left + 0.04, cyl_right - 0.04, n_dots)
    dot_y = rng.uniform(cyl_bottom + 0.02, cyl_bottom + gas_height - 0.02, n_dots)
    dot_color = cm.coolwarm(normalized_T)
    ax1.scatter(dot_x, dot_y, color=dot_color, s=8, alpha=0.8, zorder=2)

    # Piston + rod
    ax1.add_patch(mpatches.Rectangle(
        (cyl_left, piston_y), cyl_width, 0.04,
        color=brand.ACAD_GREY, zorder=4))
    ax1.plot([cyl_left + cyl_width / 2] * 2,
             [piston_y + 0.04, cyl_top + 0.08],
             color=brand.ACAD_GREY, linewidth=3, zorder=4)

    # Labels
    ax1.text(cyl_left + cyl_width / 2, cyl_bottom - 0.1,
             f'ρ = {rho_curr:.5f} {rho_unit}',
             color=brand.CLASS_YELLOW, fontsize=7,
             fontfamily='monospace', ha='center', va='top')
    ax1.text(cyl_left + cyl_width / 2, cyl_top + 0.15,
             f'T = {t_curr:.1f} {t_unit}',
             color=cm.coolwarm(normalized_T), fontsize=7,
             fontfamily='monospace', ha='center')

    ax1.set_xlim(0, 1.1)
    ax1.set_ylim(-0.2, cyl_top + 0.3)

    # ── AX2: Pressure gauge ───────────────────────────────────────
    cx, cy, r = 0.5, 0.3, 0.38

    ax2.add_patch(Arc((cx, cy), 2*r, 2*r,
                      angle=0, theta1=0, theta2=180,
                      color=brand.ACAD_GREY, linewidth=6, zorder=2))

    p_norm   = np.clip((p_curr - p_min_gauge) / (p_max_gauge - p_min_gauge), 0, 1)
    fill_deg = p_norm * 180
    ax2.add_patch(Arc((cx, cy), 2*r, 2*r,
                      angle=0, theta1=0, theta2=fill_deg,
                      color=brand.CLASS_YELLOW, linewidth=6, zorder=3))

    needle_angle = np.radians(p_norm * 180)
    nx = cx + r * 0.85 * np.cos(needle_angle)
    ny = cy + r * 0.85 * np.sin(needle_angle)
    ax2.annotate('', xy=(nx, ny), xytext=(cx, cy),
                 arrowprops=dict(arrowstyle='->',
                                 color=brand.CLASS_YELLOW,
                                 lw=1.5, mutation_scale=10), zorder=5)
    ax2.plot(cx, cy, 'o', color=brand.ACAD_GREY, markersize=5, zorder=6)

    ax2.text(cx - r - 0.04, cy, '0',
             color=brand.ACAD_GREY, fontsize=7,
             fontfamily='monospace', ha='right', va='center')
    ax2.text(cx + r + 0.04, cy, f'{p_max_gauge:.0f}',
             color=brand.ACAD_GREY, fontsize=7,
             fontfamily='monospace', ha='left', va='center')
    ax2.text(cx, cy - 0.12, f'P = {p_curr:.1f} {p_unit}',
             color=brand.CLASS_YELLOW, fontsize=8,
             fontfamily='monospace', ha='center', va='top',
             fontweight='bold')

    ax2.set_xlim(0, 1)
    ax2.set_ylim(-0.1, 0.85)

    plt.tight_layout(pad=0.3)
    st.pyplot(fig, width='content')
    plt.close(fig)

render_calcs(slide, units, param)