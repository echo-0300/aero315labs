import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
from utils.usafa_styles import *
import ambiance as ab
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Arc
st.set_page_config(page_title="ICeT-G - Virtual Lab", page_icon="🧊", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()


st.markdown('<div class="page-title">ICeT-G</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Airspeed Corrections</div>', unsafe_allow_html=True)

with st.expander("📖  Governing Equations", expanded=True):
    col_eq1, col_eq2 = st.columns(2)

    with col_eq1:
        st.markdown('<div class="eq-label">Calibrated Airspeed</div>', unsafe_allow_html=True)
        st.latex(r"V_c = \sqrt{\frac{1}{\rho_{sl}} 7P_{SL} \left[ \left( \frac{P_0 - P_\infty}{P_{SL}} + 1 \right)^{\frac{1}{3.5}} - 1 \right]}")
        st.markdown("""
        <div class="explainer">
        The pitot static system is attempting to solve this equation using the inputs from the total and static pressure points and the known values of
        density and pressure at sea level. There is an inherent position error based on the systems installation in the aircraft which is captured by:
        </div>
        """, unsafe_allow_html=True)

        st.latex(r"V_c = V_i + \Delta V_p")
        st.markdown('<div class="eq-label">Equivalent Airspeed</div>', unsafe_allow_html=True)
        st.latex(r"V_e = \sqrt{\frac{1}{\rho_{sl}} 7P_{\infty} \left[ \left( \frac{P_0 - P_\infty}{P_{\infty}} + 1 \right)^{\frac{1}{3.5}} - 1 \right]}")
        st.markdown("""
        <div class="explainer">
        The equivalent airspeed uses the free stream pressure in place of the sea level pressure, meaning that the difference between calibrated and equivalent
        airspeed can be represented as:
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"V_e = f V_c")
        st.markdown("""
        <div class="explainer">
        f is the ratio between Equivalent and Calibrated airspeeds, which can be calculated, or looked up in a table (3.1).
                    
        </div>
        """, unsafe_allow_html=True)

    with col_eq2:
        st.markdown('<div class="eq-label">True Airspeed</div>', unsafe_allow_html=True)
        st.latex(r"V_\infty=V_e \sqrt{\frac{\rho_{SL}}{\rho_\infty}}")
        st.markdown("""
        <div class="explainer">
        The true airspeed further corrects for the free stream density being different from that at sea level.
        
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="eq-label">Ground Speed</div>', unsafe_allow_html=True)
        st.latex(r"V_g = V_\infty + V_{wind}")
        st.markdown("""
        <div class="explainer">
        Where true airspeed is the airspeed with respect to the airmass the aircraft is traveling through, ground speed accounts
        for the speed of that airmass, providing the speed of the aircraft with respect to the ground it is traveling over.
        </div>
        """, unsafe_allow_html=True)
st.divider()

col_altitude, col_gap, col_indicated, col_gap2, col_position_error, col_gap3, col_wind = st.columns([1, 0.2,1, 0.2, 1, 0.2, 1])

with col_altitude:
    st.markdown("**Select Altitude (ft)**")
    alt = st.slider("Altitude", min_value=0.0, max_value=36000.0,
                    value=5000.0, step=1.0,
                    format="h = %.2f ft",
                    label_visibility="collapsed")
with col_indicated:
    st.markdown("**Select Indicated Airspeed (knots)**")
    V_ind = st.slider("$V_i$", min_value=0.0, max_value=250.0,
                    value=150.0, step=1.0,
                    format="$V_i$ = %.2f kts",
                    label_visibility="collapsed")
with col_position_error:
    st.markdown("**Select Aircraft Position Error (knots)**")
    V_p = st.slider("$\Delta V_p$", min_value=0.0, max_value=10.0,
                    value=5.0, step=1.0,
                    format="$\Delta V_p$=%.2f kts",
                    label_visibility="collapsed")
with col_wind:
    st.markdown("**Set Headwind Speed (knots)**")
    V_w = st.slider("$V_w$", min_value=0.0, max_value=40.0,
                    value=20.0, step=1.0,
                    format="$V_w$=%.2f kts",
                    label_visibility="collapsed")

@st.fragment
def render_airspeed(alt: float, V_ind: float, V_p: float, V_w: float) -> None:
    rho_ssl = 0.002377 # slug/ft³
    P_ssl = 2116.22 # psf
    alt_m = alt * 0.3048
    atm = ab.Atmosphere(alt_m)
    P_inf = float(atm.pressure[0]) * 0.020885 #Pa to psf
    rho_inf = float(atm.density[0]) * 0.00194032 # kg/m³ to slug/ft³
    V_c = V_ind + V_p
    V_c_fts = V_c * 1.68781 #knots to ft/s
    term = ( (V_c_fts**2 * rho_ssl) / (7 * P_ssl) ) + 1 #using full V_c equation
    P_0 = P_ssl * ( (term**3.5) - 1 ) + P_inf
    V_e = np.sqrt((7 * P_inf / rho_ssl) * ((P_0 / P_inf)**(2/7) - 1)) / 1.68781
    V_inf = V_e * (rho_ssl / rho_inf) ** 0.5
    V_g = V_inf - V_w

    v_array = [V_ind, V_c, V_e, V_inf, V_g]
    v_names = ["$V_i$", "$V_c$", "$V_e$", "$V_\\infty$", "$V_g$"]
    c_array = [ACAD_WHITE, CLASS_RED, CLASS_YELLOW, GROTTO_BLUE, ACAD_GREY]

    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            st.markdown(
                f"""
                <div style="text-align: left;">
                    <div style="font-size: 28px; color: {c_array[i]}; font-weight: 600;">
                        {v_array[i]:.2f}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(f"       {v_names[i]}")
    #Guage Config
    V_max = 400.0
    fig, ax1 = plt.subplots(figsize=(5, 5))
    fig.patch.set_facecolor(BG_PRIMARY)
    ax1.set_facecolor(BG_PRIMARY)
    ax1.axis('off')

    # ─────────────────────────────────────────────────────────────
    # ax1 — Airspeed indicator (round gauge)
    # ─────────────────────────────────────────────────────────────
    cx, cy, r = 0.5, 0.5, 0.42

    # Gauge face
    ax1.add_patch(mpatches.Circle((cx, cy), r,
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
        ax1.plot([cx + r_inner * np.cos(angle_rad),
                  cx + r_outer * np.cos(angle_rad)],
                 [cy + r_inner * np.sin(angle_rad),
                  cy + r_outer * np.sin(angle_rad)],
                 color=ACAD_WHITE,
                 linewidth=1.2 if is_major else 0.6, zorder=3)
        if is_major:
            lx = cx + (r * 0.68) * np.cos(angle_rad)
            ly = cy + (r * 0.68) * np.sin(angle_rad)
            ax1.text(lx, ly, f'{spd:.0f}',
                     color=ACAD_WHITE, fontsize=6,
                     fontfamily='monospace',
                     ha='center', va='center')

    # Colored arc — green normal range (60–200 kt), red above 200
    for spd_start, spd_end, arc_color in [
            (60,  250, '#00aa44'),
            (250, 400, CLASS_RED)]:
        a_start = 225 - (270 * spd_start / V_max)
        a_end   = 225 - (270 * spd_end   / V_max)
        ax1.add_patch(Arc((cx, cy), 2 * r * 0.96, 2 * r * 0.96,
                          angle=0,
                          theta1=a_end, theta2=a_start,
                          color=arc_color, linewidth=4, zorder=2))

    # Needle
    
    for i in range (5):
        needle_deg = 225 - (270 * np.clip(v_array[i], 0, V_max) / V_max)
        needle_rad = np.radians(needle_deg)
        nx = cx + r * 0.78 * np.cos(needle_rad)
        ny = cy + r * 0.78 * np.sin(needle_rad)
        ax1.annotate('', xy=(nx, ny), xytext=(cx, cy),
                    arrowprops=dict(arrowstyle='->', color=c_array[i],
                                    lw=2.0, mutation_scale=12), zorder=5)
        
    ax1.plot(cx, cy, 'o', color=ACAD_GREY, markersize=6, zorder=6)

    # Labels
    ax1.text(cx, cy - r * 0.45, 'AIRSPEED',
             color=ACAD_GREY, fontsize=6,
             fontfamily='monospace', ha='center')
    ax1.text(cx, cy - r * 0.58, 'KNOTS',
             color=ACAD_GREY, fontsize=6,
             fontfamily='monospace', ha='center')
    ax1.text(cx, cy + r * 0.3, f'{V_ind:.1f}',
             color=CLASS_YELLOW, fontsize=11,
             fontfamily='monospace', ha='center',
             fontweight='bold')

    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)

    plt.tight_layout(pad=0.3)
    st.pyplot(fig, width='content')
    plt.close(fig)
    
render_airspeed(alt, V_ind, V_p, V_w)
