import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
from utils.usafa_styles import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Arc

st.set_page_config(page_title="Altimetry - Virtual Lab", page_icon="🧭", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()

st.markdown('<div class="page-title">Altimetry</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Pressure Altitude & Altimeter Settings</div>', unsafe_allow_html=True)

with st.expander("📖  Governing Equations", expanded=True):
    col_eq1, col_eq2 = st.columns(2)

    with col_eq1:
        st.markdown('<div class="eq-label">Pressure Altitude</div>', unsafe_allow_html=True)
        st.latex(r"h = \frac{T_{SL}}{L}\left[1 - \left(\frac{P_\infty}{P_{SL}}\right)^{\frac{RL}{g}}\right]")
        st.markdown("""
        <div class="explainer">
        Pressure altitude is derived by comparing the measured static pressure (P∞) to the standard
        sea level pressure (P = 2116.22 psf). The lapse rate (L), sea level temperature (T_SL),
        gravitational acceleration (g), and gas constant (R) define the pressure-altitude
        relationship in the troposphere, below ~36,000 ft where temperature decreases linearly with altitude.
        </div>
        """, unsafe_allow_html=True)

    with col_eq2:
        st.markdown('<div class="eq-label">Altimeter Setting & Kollsman Window</div>', unsafe_allow_html=True)
        st.latex(r"h_{indicated} = h_{pressure} + 1000 \times (P_{set} - 29.92)")
        st.markdown("""
        <div class="explainer">
        An altimeter measures pressure altitude, but accounts for non-standard sea level pressure
        via the <b>Kollsman window</b> — a knob-adjustable reference pressure set by the pilot in
        <b>inches of mercury (inHg)</b>, sometimes reported as <b>millimeters of mercury (mmHg)</b>.
        <br><br>
        Standard sea level pressure is 29.92 inHg.
        Each inHg difference from standard shifts indicated altitude
        by approximately 1,000 ft.
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Sliders ───────────────────────────────────────────────────────────────────
st.markdown("**Set Static Pressure (psf)**")
P_inf = st.slider("P_inf", min_value=400.0, max_value=2116.22,
                  value=2116.22, step=1.0,
                  format="P∞ = %.2f psf",
                  label_visibility="collapsed")

st.markdown("**Set Altimeter Setting (inHg)** — standard = 29.92")
alt_setting_inhg = st.slider("alt_setting", min_value=27.50, max_value=31.50,
                              value=29.92, step=0.01,
                              format="%.2f inHg",
                              label_visibility="collapsed")

@st.fragment
def render_altimeter(P_inf: float, alt_setting_inhg: float) -> None:

    # ── Constants ─────────────────────────────────────────────────
    P_ssl   = 2116.22   # psf
    T_sl    = 518.67    # °R
    L       = 0.003566  # °R/ft  (lapse rate)
    g       = 32.174    # ft/s²
    R       = 1716.5    # ft·lb/(slug·°R)
    std_inhg = 29.92

    # ── Pressure altitude (based on P_inf vs P_ssl standard) ──────
    h_pressure = (T_sl / L) * (1 - (P_inf / P_ssl) ** (R * L / g))

    # ── Indicated altitude (corrected for altimeter setting) ───────
    # Each 1 inHg deviation from standard ≈ 1000 ft shift
    h_indicated = h_pressure + 1000 * (alt_setting_inhg - std_inhg)


    # ── Gauge config ──────────────────────────────────────────────
    alt_max    = 36000.0   # ft display max
    needle_alt = np.clip(h_indicated, 0, alt_max)

    # ── Figure layout ─────────────────────────────────────────────
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4),
                                   gridspec_kw={'width_ratios': [1.5, 1]})
    fig.patch.set_facecolor(BG_PRIMARY)
    for ax in (ax1, ax2):
        ax.set_facecolor(BG_PRIMARY)
        ax.axis('off')

    # ─────────────────────────────────────────────────────────────
    # AX1 — Altimeter diagram
    # ─────────────────────────────────────────────────────────────

    # ── Atmosphere column — left side ─────────────────────────────
    col_left   = 0.05
    col_right  = 0.22
    col_bottom = 0.08
    col_top    = 0.92
    col_h      = col_top - col_bottom

    # Atmosphere gradient bands (troposphere layers by color)
    layer_colors = ['#001d47', '#002060', '#002554', '#003080', '#003594']
    n_layers = len(layer_colors)
    for i, lc in enumerate(layer_colors):
        y0 = col_bottom + i * (col_h / n_layers)
        ax1.add_patch(mpatches.Rectangle(
            (col_left, y0), col_right - col_left, col_h / n_layers,
            facecolor=lc, edgecolor='none', zorder=1))

    # Column border
    ax1.add_patch(mpatches.FancyBboxPatch(
        (col_left, col_bottom), col_right - col_left, col_h,
        boxstyle="round,pad=0.005",
        facecolor='none', edgecolor=ACAD_GREY,
        linewidth=1.0, zorder=3))

    # Aircraft marker on the column
    aircraft_y = col_bottom + np.clip(h_indicated / alt_max, 0, 1) * col_h
    ax1.plot([col_left - 0.01, col_right + 0.01],
             [aircraft_y, aircraft_y],
             color=CLASS_YELLOW, linewidth=1.5,
             linestyle='--', zorder=4)
    ax1.text(col_right + 0.02, aircraft_y, '✈',
             color=CLASS_YELLOW, fontsize=10, va='center', zorder=5)

    # Pressure marker on the column
    pressure_y = col_bottom + np.clip(h_pressure / alt_max, 0, 1) * col_h
    ax1.plot([col_left - 0.01, col_right + 0.01],
             [pressure_y, pressure_y],
             color=GROTTO_BLUE, linewidth=1.0,
             linestyle=':', zorder=4)

    # Altitude labels on column
    for alt_mark in [0, 10000, 20000, 30000, 36000]:
        y_mark = col_bottom + (alt_mark / alt_max) * col_h
        ax1.plot([col_left, col_left + 0.02],
                 [y_mark, y_mark],
                 color=ACAD_GREY, linewidth=0.6, zorder=3)
        ax1.text(col_left - 0.01, y_mark,
                 f"{alt_mark//1000}k",
                 color=ACAD_GREY, fontsize=6,
                 fontfamily='monospace', ha='right', va='center')

    ax1.text((col_left + col_right) / 2, col_top + 0.04,
             'ALT', color=ACAD_GREY, fontsize=6,
             fontfamily='monospace', ha='center')

    


    # ── Value readouts ────────────────────────────────────────────
    ax1.text(0.30, 0.82,
             f'P∞          = {P_inf:.1f} psf',
             color=GROTTO_BLUE, fontsize=8, fontfamily='monospace')
    ax1.text(0.30, 0.72,
             f'Pressure Alt = {h_pressure:,.0f} ft',
             color=GROTTO_BLUE, fontsize=8, fontfamily='monospace')
    ax1.text(0.30, 0.62,
             f'Altimeter    = {alt_setting_inhg:.2f} inHg',
             color=CLASS_YELLOW, fontsize=8, fontfamily='monospace')
    ax1.text(0.30, 0.52,
             f'Indicated Alt= {h_indicated:,.0f} ft',
             color=CLASS_YELLOW, fontsize=8,
             fontfamily='monospace', fontweight='bold')

    # Deviation annotation
    dev = h_indicated - h_pressure
    dev_color = CLASS_RED if abs(dev) > 100 else ACAD_GREY
    ax1.text(0.30, 0.42,
             f'Deviation    = {dev:+,.0f} ft',
             color=dev_color, fontsize=8, fontfamily='monospace')

    ax1.set_xlim(0, 1.05)
    ax1.set_ylim(0, 1.1)

    # ─────────────────────────────────────────────────────────────
    # AX2 — Altimeter gauge (round)
    # ─────────────────────────────────────────────────────────────
    cx, cy, r = 0.5, 0.5, 0.42

    # Gauge face
    ax2.add_patch(mpatches.Circle((cx, cy), r,
                                   facecolor='#050d1a',
                                   edgecolor=ACAD_GREY,
                                   linewidth=3, zorder=1))

    # Tick marks — every 1000 ft, labeled every 5000
    n_ticks = 51
    for i in range(n_ticks):
        alt_t     = i * (alt_max / (n_ticks - 1))
        angle_deg = 225 - (270 * alt_t / alt_max)
        angle_rad = np.radians(angle_deg)
        is_major  = (i % 5 == 0)
        r_inner   = r * (0.80 if is_major else 0.88)
        r_outer   = r * 0.95
        ax2.plot([cx + r_inner * np.cos(angle_rad),
                  cx + r_outer * np.cos(angle_rad)],
                 [cy + r_inner * np.sin(angle_rad),
                  cy + r_outer * np.sin(angle_rad)],
                 color=ACAD_WHITE,
                 linewidth=1.2 if is_major else 0.5, zorder=3)
        if is_major:
            lx = cx + (r * 0.68) * np.cos(angle_rad)
            ly = cy + (r * 0.68) * np.sin(angle_rad)
            ax2.text(lx, ly, f'{alt_t/1000:.0f}0',
                     color=ACAD_WHITE, fontsize=5.5,
                     fontfamily='monospace',
                     ha='center', va='center')

    # Pressure altitude needle (Grotto Blue — secondary)
    p_needle_deg = 225 - (270 * np.clip(h_pressure, 0, alt_max) / alt_max)
    p_needle_rad = np.radians(p_needle_deg)
    px = cx + r * 0.65 * np.cos(p_needle_rad)
    py = cy + r * 0.65 * np.sin(p_needle_rad)
    ax2.annotate('', xy=(px, py), xytext=(cx, cy),
                 arrowprops=dict(arrowstyle='->', color=GROTTO_BLUE,
                                 lw=1.5, mutation_scale=10), zorder=4)

    # Indicated altitude needle (white — primary)
    needle_deg = 225 - (270 * np.clip(h_indicated, 0, alt_max) / alt_max)
    needle_rad = np.radians(needle_deg)
    nx = cx + r * 0.78 * np.cos(needle_rad)
    ny = cy + r * 0.78 * np.sin(needle_rad)
    ax2.annotate('', xy=(nx, ny), xytext=(cx, cy),
                 arrowprops=dict(arrowstyle='->', color=ACAD_WHITE,
                                 lw=2.0, mutation_scale=12), zorder=5)

    ax2.plot(cx, cy, 'o', color=ACAD_GREY, markersize=6, zorder=6)

    # Needle legend
    ax2.plot([cx - r*0.35, cx - r*0.15], [cy - r*0.55, cy - r*0.55],
             color=ACAD_WHITE, linewidth=2.0)
    ax2.text(cx - r*0.12, cy - r*0.55, 'indicated',
             color=ACAD_WHITE, fontsize=5.5,
             fontfamily='monospace', va='center')
    ax2.plot([cx - r*0.35, cx - r*0.15], [cy - r*0.68, cy - r*0.68],
             color=GROTTO_BLUE, linewidth=1.5)
    ax2.text(cx - r*0.12, cy - r*0.68, 'pressure',
             color=GROTTO_BLUE, fontsize=5.5,
             fontfamily='monospace', va='center')

    # Labels
    ax2.text(cx, cy + r * 0.28, f'{h_indicated:,.0f}',
             color=CLASS_YELLOW, fontsize=10,
             fontfamily='monospace', ha='center', fontweight='bold')
    ax2.text(cx, cy + r * 0.14, 'ft indicated x100',
             color=ACAD_GREY, fontsize=5.5,
             fontfamily='monospace', ha='center')
    ax2.text(cx, cy - r * 0.38, 'ALTIMETER',
             color=ACAD_GREY, fontsize=6,
             fontfamily='monospace', ha='center')

    # ── Kollsman window ───────────────────────────────────────────
    kw_left   = 0.32
    kw_right  = 0.66
    kw_bottom = 0.39
    kw_top    = 0.46

    ax2.add_patch(mpatches.FancyBboxPatch(
        (kw_left, kw_bottom), kw_right - kw_left, kw_top - kw_bottom,
        boxstyle="round,pad=0.01",
        facecolor='#0a0e1a', edgecolor=ACAD_GREY,
        linewidth=1.5, zorder=3))

    # inHg display
    ax2.text((kw_left + kw_right) / 2, (kw_bottom + kw_top) / 2,
             f'{alt_setting_inhg:.2f}',
             color=CLASS_YELLOW, fontsize=14,
             fontfamily='monospace', ha='center', va='center',
             fontweight='bold')
    ax2.text(kw_right - .03, (kw_bottom + kw_top) / 2,
             'inHg',
             color=ACAD_GREY, fontsize=7,
             fontfamily='monospace', ha='center', va='center')

    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)

    plt.tight_layout(pad=0.3)
    st.pyplot(fig, width='stretch')
    plt.close(fig)

render_altimeter(P_inf, alt_setting_inhg)

st.divider()
with st.expander("💡  Physical Interpretation"):
    st.markdown("""
        **Pressure Altitude vs. Indicated Altitude**

        - **Pressure altitude** is what the atmosphere is actually doing — derived purely from
          the measured static pressure compared to standard sea level (2116.22 psf / 29.92 inHg).
        - **Indicated altitude** is what the altimeter displays after the pilot dials in the
          local altimeter setting via the Kollsman window.
        - What condiditions might cause inaccurate altitude indications?
        """)
    st.markdown("""
        **Why the Kollsman Window Matters**

        - If the local sea level pressure is higher than standard (e.g. 30.42 inHg), the altimeter
          will read ~500 ft higher than pressure altitude — the aircraft is actually lower than
          the instrument suggests without the correction.
        - Pilots receive the current altimeter setting from air traffic control and update
          their Kollsman window to ensure terrain clearance accuracy.
        """)