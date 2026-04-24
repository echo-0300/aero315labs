import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
from utils.usafa_styles import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Arc
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

col_press, col_gap, col_altitude = st.columns([1, 0.5,1])
st.markdown("**Select Freestream Pressure (Altitude)**")
P_inf = st.slider("P_inf", min_value=500.0, max_value=2116.22,
                  value=2116.22, step=1.0,
                  format="P∞ = %.2f psf",
                  label_visibility="collapsed")

st.markdown("**Select Total Pressure (always greater than P∞)**")
P_0 = st.slider("P_0", min_value=float(P_inf + 1.0), max_value=float(P_inf * 1.25),
                value=float(P_inf + 1.0), step=1.0,
                format="P₀ = %.2f psf",
                label_visibility="collapsed")
    
@st.fragment
def render_pitot(P_0: float, P_inf: float) -> None:

    rho_ssl = 0.002377  # slug/ft³
    delta_p = P_0 - P_inf

    # Guard for invalid state
    if delta_p <= 0:
        st.warning("P₀ must be greater than P∞ — check your inputs.")
        return

    V_ias = np.sqrt(2 * delta_p / rho_ssl)

    # ── Gauge config ──────────────────────────────────────────────
    V_max  = 300.0   # knots display max
    V_knots = V_ias * 0.592484   # ft/s → knots

    # ── Figure layout ─────────────────────────────────────────────
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4),
                                   gridspec_kw={'width_ratios': [2, 1]})
    fig.patch.set_facecolor(BG_PRIMARY)
    for ax in (ax1, ax2):
        ax.set_facecolor(BG_PRIMARY)
        ax.axis('off')

    # ─────────────────────────────────────────────────────────────
    # AX1 — Pitot-static diagram
    # ─────────────────────────────────────────────────────────────

   # ── Pitot tube body ───────────────────────────────────────────
    tube_y      = 0.65
    tube_left   = 0.05
    tube_right  = 0.55
    tube_h      = 0.06
    tube_mid    = tube_h / 2
    tip_x       = 0.05
    inner_r     = 0.018   # radius of the inner bore

    # Main tube body — drawn as outline only so bore is visible
    ax1.add_patch(mpatches.FancyBboxPatch(
        (tip_x + 0.08, tube_y - tube_mid),
        tube_right - tip_x - 0.08, tube_h,
        boxstyle="round,pad=0.005",
        facecolor=ACAD_GREY, edgecolor=ACAD_WHITE,
        linewidth=0.8, zorder=3))

    # Pointed tip
    tip = plt.Polygon(
        [[tip_x,        tube_y],
         [tip_x + 0.08, tube_y + tube_mid],
         [tip_x + 0.08, tube_y - tube_mid]],
        closed=True, facecolor=ACAD_GREY,
        edgecolor=ACAD_WHITE, linewidth=0.8, zorder=4)
    ax1.add_patch(tip)

    # Inner bore — dark tunnel running tip to right end
    ax1.add_patch(mpatches.Rectangle(
        (tip_x - 0.045, tube_y - inner_r),
        tube_right - tip_x + 0.04, inner_r * 2,
        facecolor=BG_PRIMARY, edgecolor='none', zorder=5))

    # Bore opening at tip (small dark circle at the point)
    ax1.add_patch(mpatches.Circle(
        (tip_x, tube_y), inner_r,
        facecolor=BG_PRIMARY, edgecolor='none', zorder=6))

    # Bore exit at right end — this is where P0 line originates
    bore_exit_x = tube_right
    bore_exit_y = tube_y

    # Total pressure port label (tip)
    ax1.annotate('P₀\n(total)', xy=(tip_x + 0.05, tube_y+.02),
                 xytext=(tip_x - 0.01, tube_y + 0.2),
                 color=GROTTO_BLUE, fontsize=7,
                 fontfamily='monospace', ha='center',
                 arrowprops=dict(arrowstyle='->', color=GROTTO_BLUE,
                                 lw=1.0, mutation_scale=8))

    # ── Static ports (small circles on tube sides) ────────────────
    static_x = tube_left + 0.25
    for dy in (tube_h / 2, -tube_h / 2):
        ax1.add_patch(mpatches.Circle(
            (static_x, tube_y + dy), 0.012,
            facecolor=BG_PRIMARY, edgecolor=ACAD_WHITE,
            linewidth=0.8, zorder=5))

    ax1.annotate('P∞\n(static)', xy=(static_x, tube_y - tube_h / 2),
                 xytext=(static_x + 0.08, tube_y - 0.2),
                 color=CLASS_YELLOW, fontsize=7,
                 fontfamily='monospace', ha='center',
                 arrowprops=dict(arrowstyle='->', color=CLASS_YELLOW,
                                 lw=1.0, mutation_scale=8))

    # ── Pressure lines running down to instrument ─────────────────
    line_bot  = 0.1
    p0_line_x = tip_x + 0.04
    ps_line_x = static_x

    # Total pressure line
    ax1.plot([bore_exit_x, 0.72, 0.72],
             [bore_exit_y, bore_exit_y, line_bot],
             color=GROTTO_BLUE, linewidth=1.5,
             linestyle='--', zorder=2)

    # Static pressure line
    ax1.plot([ps_line_x, ps_line_x, 0.72],
             [tube_y - tube_h / 2, line_bot, line_bot],
             color=CLASS_YELLOW, linewidth=1.5,
             linestyle='--', zorder=2)

    # ── Differential pressure label ───────────────────────────────
    ax1.annotate('', xy=(0.72, line_bot + 0.07),
                 xytext=(0.68, line_bot),
                 arrowprops=dict(arrowstyle='<->',
                                 color=CLASS_RED,
                                 lw=1.2, mutation_scale=8))
    ax1.text(0.75, (line_bot + line_bot + 0.05) / 2,
             f'ΔP = {delta_p:.1f} psf',
             color=CLASS_RED, fontsize=12,
             fontfamily='monospace', va='center')

    # ── Freestream arrows ─────────────────────────────────────────
    arrow_ys = [0.35, 0.5, 0.65, 0.80, 0.95]
    for y in arrow_ys:
        if abs(y - tube_y) > 0.1:   # skip arrows overlapping tube
            ax1.annotate('', xy=(0.45, y), xytext=(0.15, y),
                         arrowprops=dict(arrowstyle='->',
                                         color=USAFA_BLUE,
                                         lw=1.0, mutation_scale=7,
                                         alpha=0.6))

    ax1.text(0.3, 0.03, 'freestream →',
             color=USAFA_BLUE, fontsize=7,
             fontfamily='monospace', ha='center', alpha=0.6)

    # ── Value readouts ────────────────────────────────────────────
    ax1.text(0.75, 0.18,
             f'P₀  = {P_0:.1f} psf',
             color=GROTTO_BLUE, fontsize=8,
             fontfamily='monospace')
    ax1.text(0.75, 0.05,
             f'P∞  = {P_inf:.1f} psf',
             color=CLASS_YELLOW, fontsize=8,
             fontfamily='monospace')

    ax1.set_xlim(0, 1.05)
    ax1.set_ylim(0, 1.1)

    # ─────────────────────────────────────────────────────────────
    # AX2 — Airspeed indicator (round gauge)
    # ─────────────────────────────────────────────────────────────
    cx, cy, r = 0.5, 0.5, 0.42

    # Gauge face
    ax2.add_patch(mpatches.Circle((cx, cy), r,
                                   facecolor='#050d1a',
                                   edgecolor=ACAD_GREY,
                                   linewidth=3, zorder=1))

    # Tick marks and speed labels
    n_ticks = 13
    for i in range(n_ticks):
        spd        = i * (V_max / (n_ticks - 1))
        # gauge runs from 225° (bottom-left) to -45° (bottom-right)
        angle_deg  = 225 - (270 * spd / V_max)
        angle_rad  = np.radians(angle_deg)
        is_major   = (i % 2 == 0)
        r_inner    = r * (0.80 if is_major else 0.87)
        r_outer    = r * 0.95
        ax2.plot([cx + r_inner * np.cos(angle_rad),
                  cx + r_outer * np.cos(angle_rad)],
                 [cy + r_inner * np.sin(angle_rad),
                  cy + r_outer * np.sin(angle_rad)],
                 color=ACAD_WHITE,
                 linewidth=1.2 if is_major else 0.6, zorder=3)
        if is_major:
            lx = cx + (r * 0.68) * np.cos(angle_rad)
            ly = cy + (r * 0.68) * np.sin(angle_rad)
            ax2.text(lx, ly, f'{spd:.0f}',
                     color=ACAD_WHITE, fontsize=6,
                     fontfamily='monospace',
                     ha='center', va='center')

    # Colored arc — green normal range (60–200 kt), red above 200
    for spd_start, spd_end, arc_color in [
            (60,  200, '#00aa44'),
            (200, 300, CLASS_RED)]:
        a_start = 225 - (270 * spd_start / V_max)
        a_end   = 225 - (270 * spd_end   / V_max)
        ax2.add_patch(Arc((cx, cy), 2 * r * 0.96, 2 * r * 0.96,
                          angle=0,
                          theta1=a_end, theta2=a_start,
                          color=arc_color, linewidth=4, zorder=2))

    # Needle
    needle_deg = 225 - (270 * np.clip(V_knots, 0, V_max) / V_max)
    needle_rad = np.radians(needle_deg)
    nx = cx + r * 0.78 * np.cos(needle_rad)
    ny = cy + r * 0.78 * np.sin(needle_rad)
    ax2.annotate('', xy=(nx, ny), xytext=(cx, cy),
                 arrowprops=dict(arrowstyle='->', color=ACAD_WHITE,
                                 lw=2.0, mutation_scale=12), zorder=5)
    ax2.plot(cx, cy, 'o', color=ACAD_GREY, markersize=6, zorder=6)

    # Labels
    ax2.text(cx, cy - r * 0.45, 'AIRSPEED',
             color=ACAD_GREY, fontsize=6,
             fontfamily='monospace', ha='center')
    ax2.text(cx, cy - r * 0.58, 'KNOTS',
             color=ACAD_GREY, fontsize=6,
             fontfamily='monospace', ha='center')
    ax2.text(cx, cy + r * 0.3, f'{V_knots:.1f}',
             color=CLASS_YELLOW, fontsize=11,
             fontfamily='monospace', ha='center',
             fontweight='bold')

    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)

    plt.tight_layout(pad=0.3)
    st.pyplot(fig, width='stretch')
    plt.close(fig)

render_pitot(P_0,P_inf)

st.divider()
with st.expander("💡  Physical Interpretation"):
    st.markdown("""
        **Total Pressure > Free Stream Pressure**

        - When the aircraft is in motion it is forcing air into the total pressure port, which captures the higher pressure value.
        - The static ports (parallel to the flow) attempt to capture only the internal pressure of the air, without any of the effects of the velocity.
        """)
    st.markdown("""
        **Limitations**

        - There is no simple way to measure the density of the outside air, so the system assumes a constant density and uses a nominal sea level value.
        - Does this effect mean the 'real' airspeed is higher or lower than the value indicated on the guage?
        """)