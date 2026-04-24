import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
from utils.usafa_styles import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

st.set_page_config(page_title="Boundary Layer - Virtual Lab", page_icon="🍰", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()

st.markdown('<div class="page-title">Boundary Layer</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Laminar & Turbulent Flow Over a Surface</div>', unsafe_allow_html=True)

with st.expander("📖  Governing Equations", expanded=True):
    col_eq1, col_eq2 = st.columns(2)

    with col_eq1:
        st.markdown('<div class="eq-label">Reynolds Number</div>', unsafe_allow_html=True)
        st.latex(r"Re_x = \frac{\rho V x}{\mu}")
        st.markdown("""
        <div class="explainer">
        The Reynolds number (Re) is a dimensionless ratio comparing <b>inertial forces</b> to
        <b>viscous forces</b> in a flow. At low Re, viscous forces dominate and the flow remains
        smooth and orderly — this is <b>laminar flow</b>. As Re increases, inertial forces take
        over and the flow becomes chaotic — this is <b>turbulent flow</b>.
        <br><br>
        Here, <b>ρ</b> is density, <b>V</b> is freestream velocity, <b>x</b> is distance along
        the surface, and <b>μ</b> is dynamic viscosity (1.789×10⁻⁵ Pa·s for air at SSL).
        </div>
        """, unsafe_allow_html=True)

    with col_eq2:
        st.markdown('<div class="eq-label">Transition & Pressure Gradient Effects</div>', unsafe_allow_html=True)
        st.latex(r"Re_{tr} \approx 500{,}000")
        st.markdown("""
        <div class="explainer">
        Transition from laminar to turbulent flow on a flat plate typically occurs around
        <b>Re ≈ 500,000</b>. The exact location depends on surface roughness, freestream
        turbulence, and — critically — the <b>pressure gradient</b> along the surface.
        <br><br>
        A <b>favorable pressure gradient</b> (flow accelerating, ramp angled down) delays
        transition, keeping the boundary layer laminar longer. An <b>adverse pressure gradient</b>
        (flow decelerating, ramp angled up) promotes earlier transition and can cause
        <b>flow separation</b> in extreme cases.
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Sliders ───────────────────────────────────────────────────────────────────
sl_col1, sl_col2, sl_col3 = st.columns(3)

with sl_col1:
    st.markdown("**Freestream Velocity (m/s)**")
    V = st.slider("velocity", min_value=1.0, max_value=100.0,
                  value=30.0, step=0.5,
                  format="V = %.1f m/s",
                  label_visibility="collapsed")

with sl_col2:
    st.markdown("**Air Density (kg/m³)**")
    rho = st.slider("density", min_value=0.1, max_value=1.225,
                    value=1.225, step=0.001,
                    format="ρ = %.3f kg/m³",
                    label_visibility="collapsed")

with sl_col3:
    st.markdown("**Ramp Angle θ (°)**")
    theta = st.slider("theta", min_value=-20.0, max_value=20.0,
                      value=0.0, step=0.5,
                      format="θ = %.1f°",
                      label_visibility="collapsed")

@st.fragment
def render_boundary_layer(V: float, rho: float, theta: float) -> None:

    # ── Constants ─────────────────────────────────────────────────
    mu       = 1.789e-5   # dynamic viscosity, kg/(m·s) — air at SSL
    Re_tr    = 500_000    # flat plate transition Reynolds number
    L_plate  = 2.0        # total plate length (m)
    ramp_x   = L_plate / 2  # ramp located at midpoint
    y_scaling = 20.0

    # ── Transition location ───────────────────────────────────────
    # Base transition x from flat plate Re_tr
    x_tr_base = (Re_tr * mu) / (rho * V)

    # Ramp effect — adverse (θ > 0) moves transition upstream,
    # favorable (θ < 0) moves it downstream. Clamped to plate bounds.
    ramp_factor = 1.0 - (theta / 90.0) * 0.85
    x_tr = np.clip(x_tr_base * ramp_factor, 0.05, L_plate * 1.5)

    # ── Boundary layer thickness functions ────────────────────────
    def delta_laminar(x):
        Re_x = rho * V * x / mu
        Re_x = np.maximum(Re_x, 1e-6)
        return 5.0 * x / np.sqrt(Re_x)

    def delta_turbulent(x, x_ref, delta_ref):
        # Turbulent BL growth from transition point, anchored to delta at x_tr
        Re_x = rho * V * x / mu
        Re_x = np.maximum(Re_x, 1e-6)
        delta_turb_abs = 0.37 * x / (Re_x ** 0.2)
        # Offset so it's continuous at transition
        delta_ref_turb = 0.37 * x_ref / ((rho * V * x_ref / mu) ** 0.2)
        return delta_turb_abs - delta_ref_turb + delta_ref

    # ── Plate geometry with ramp ──────────────────────────────────
    theta_rad  = np.radians(theta)
    ramp_rise  = (L_plate / 2) * np.tan(theta_rad)

    # Plate y-coordinates: flat to ramp_x, then angled to end
    plate_x = np.array([0, ramp_x, L_plate])
    plate_y = np.array([0, 0,      ramp_rise])

    # ── Figure ────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 5))
    fig.patch.set_facecolor(BG_PRIMARY)
    ax.set_facecolor(BG_PRIMARY)

    # ── Draw plate ────────────────────────────────────────────────
    ax.plot(plate_x, plate_y, color=ACAD_GREY, linewidth=2.5, zorder=4)
    ax.fill_between([0, ramp_x, L_plate], [0, 0, ramp_rise],
                    [-0.08, -0.08, ramp_rise - 0.08],
                    color=CLASS_ROYAL, zorder=3)

    # ── BL envelope points & profile stations ────────────────────
    n_points    = 300
    x_lam       = np.linspace(0.001, min(x_tr, L_plate), n_points)
    x_turb      = np.linspace(x_tr,  L_plate, n_points) if x_tr < L_plate else np.array([])

    # Compute delta along plate, accounting for ramp geometry
    def plate_y_at(x):
        """Interpolate plate surface y at position x."""
        return np.interp(x, plate_x, plate_y)

    delta_lam_vals  = delta_laminar(x_lam)
    delta_at_tr     = delta_laminar(x_tr) if x_tr <= L_plate else delta_laminar(L_plate)

    # BL envelope y = plate surface y + delta
    env_lam_y = (plate_y_at(x_lam) + delta_lam_vals) * y_scaling

    # Draw laminar envelope
    ax.plot(x_lam, env_lam_y,
            color=USAFA_BLUE, linewidth=2.0,
            linestyle='-', zorder=5, label='Laminar BL edge')
    ax.fill_between(x_lam, plate_y_at(x_lam), env_lam_y,
                    color=USAFA_BLUE, alpha=0.10, zorder=2)

    if len(x_turb) > 1:
        delta_turb_vals = delta_turbulent(x_turb, x_tr, delta_at_tr)
        env_turb_y      = plate_y_at(x_turb) + delta_turb_vals * y_scaling

        ax.plot(x_turb, env_turb_y,
                color=CLASS_RED, linewidth=2.0,
                linestyle='-', zorder=5, label='Turbulent BL edge')
        ax.fill_between(x_turb, plate_y_at(x_turb), env_turb_y,
                        color=CLASS_RED, alpha=0.10, zorder=2)

    # ── Transition line ───────────────────────────────────────────
    if x_tr <= L_plate:
        tr_plate_y = plate_y_at(x_tr)
        tr_delta   = delta_at_tr * y_scaling
        ax.plot([x_tr, x_tr],
                [tr_plate_y, tr_plate_y + tr_delta * 1.6],
                color=CLASS_YELLOW, linewidth=1.2,
                linestyle='--', zorder=6)
        ax.text(x_tr, tr_plate_y + tr_delta * 1.7,
                f'Transition\nx = {x_tr:.2f} m',
                color=CLASS_YELLOW, fontsize=7,
                fontfamily='monospace', ha='center', va='bottom')
    else:
        ax.text(L_plate * 0.7, 0.28,
                'Transition beyond\nplate length',
                color=CLASS_YELLOW, fontsize=7,
                fontfamily='monospace', ha='center',
                style='italic', alpha=0.8)

    # ── Velocity profile stations ─────────────────────────────────
    n_stations  = 8
    stations    = np.linspace(0.15, L_plate - 0.05, n_stations)
    n_vectors   = 12   # arrows per station

    for x_s in stations:
        is_turbulent = x_s > x_tr
        py           = plate_y_at(x_s)

        if x_s <= min(x_tr, L_plate):
            delta_s = delta_laminar(x_s)
        else:
            delta_s = delta_turbulent(x_s, x_tr, delta_at_tr)

        delta_s = max(delta_s, 0.01) * y_scaling

        # y positions for vectors within BL
        y_pts = np.linspace(0, delta_s, n_vectors)

        for y_pt in y_pts:
            eta = y_pt / delta_s   # normalized height 0→1

            # Profile shape: laminar = parabolic, turbulent = 1/7 power law
            if is_turbulent:
                u_norm = eta ** (1/7)
            else:
                u_norm = 2 * eta - eta ** 2

            arrow_len = u_norm * 0.25   # scale to plot units
            color     = CLASS_RED if is_turbulent else USAFA_BLUE

            ax.annotate('',
                        xy=(x_s + arrow_len, py + y_pt),
                        xytext=(x_s, py + y_pt),
                        arrowprops=dict(arrowstyle='->',
                                        color=color,
                                        lw=0.8,
                                        mutation_scale=5),
                        zorder=7)

    # ── Freestream arrows ─────────────────────────────────────────
    for y_fs in [0.32, 0.42, 0.52]:
        ax.annotate('',
                    xy=(0.25, y_fs), xytext=(0.02, y_fs),
                    arrowprops=dict(arrowstyle='->',
                                    color=GROTTO_BLUE,
                                    lw=1.2, mutation_scale=8,
                                    alpha=0.7))
    ax.text(0.02, 0.56, f'V∞ = {V:.1f} m/s',
            color=GROTTO_BLUE, fontsize=7,
            fontfamily='monospace', alpha=0.8)

    # ── Re readout ────────────────────────────────────────────────
    Re_plate = rho * V * L_plate / mu
    ax.text(L_plate * 0.01, -0.13,
            f'Re at plate end = {Re_plate:,.0f}     '
            f'ρ = {rho:.3f} kg/m³     '
            f'μ = {mu:.2e} Pa·s     '
            f'θ = {theta:.1f}°',
            color=ACAD_GREY, fontsize=7,
            fontfamily='monospace')

    # ── Legend ────────────────────────────────────────────────────
    ax.legend(loc='upper left',
              facecolor=CLASS_ROYAL,
              edgecolor=USAFA_BLUE,
              labelcolor=ACAD_WHITE,
              fontsize=7, framealpha=0.9)

    ax.set_xlim(-0.1, L_plate + 0.15)
    ax.set_ylim(-0.18, 0.65)
    ax.axis('off')

    plt.tight_layout(pad=0.4)
    st.pyplot(fig, width='stretch')
    plt.close(fig)

render_boundary_layer(V, rho, theta)

st.divider()
with st.expander("💡  Physical Interpretation"):
    st.markdown("""
        **Laminar vs. Turbulent Velocity Profiles**

        - In the **laminar** region, the velocity profile is parabolic — velocity increases
          smoothly from zero at the wall to the freestream value. Viscous forces keep the
          flow organized in parallel layers.
        - In the **turbulent** region, the profile is much **fuller** — momentum is mixed
          across the boundary layer by chaotic eddies, so velocity near the wall is higher
          than in laminar flow. This is visible in the blunter arrow profiles downstream
          of transition.
        """)
    st.markdown("""
        **Effect of the Ramp**

        - A **downward ramp** (θ < 0) accelerates the flow, creating a favorable pressure
          gradient. This stabilizes the boundary layer and delays transition downstream.
        - An **upward ramp** (θ > 0) decelerates the flow, creating an adverse pressure
          gradient. This destabilizes the boundary layer and promotes early transition.
          At extreme angles, the flow can separate entirely from the surface.
        """)
    st.markdown("""
        **Why Does This Matter?**

        - Laminar boundary layers produce **less skin friction drag** than turbulent ones,
          which is why aircraft designers try to maintain laminar flow as long as possible.
        - However, turbulent boundary layers are more resistant to separation, which is why
          golf balls have dimples — the induced turbulence keeps the flow attached longer,
          reducing the large separated wake that would otherwise dominate the drag.
        """)