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


# ── Sliders —
sl_col1, sl_col2, sl_col3 = st.columns(3)

with sl_col1:
    st.markdown("**Freestream Velocity (ft/s)**")
    V = st.slider("velocity", min_value=1.0, max_value=200.0,
                  value=20.0, step=0.5,
                  format="V = %.1f ft/s",
                  label_visibility="collapsed")

with sl_col2:
    st.markdown("**Air Density (slug/ft³)**")
    rho = st.slider("density", min_value=0.0005, max_value=0.002377,
                    value=0.002377, step=0.00001,
                    format="ρ = %.5f slug/ft³",
                    label_visibility="collapsed")

with sl_col3:
    st.markdown("**Ramp Angle θ (°)**")
    theta = st.slider("theta", min_value=0.0, max_value=5.0,
                      value=0.0, step=0.5,
                      format="θ = %.1f°",
                      label_visibility="collapsed")

@st.fragment
def render_boundary_layer(V: float, rho: float, theta: float) -> None:

    # ── Constants — Imperial──────────────────────
    mu       = 3.737e-7   # slug/(ft·s) — standard air at SSL
    Re_tr    = 500_000
    L_plate  = 1.0     
    y_init   = 0.01 
    A1       = 0.02      
    ramp_x   = L_plate / 2
    theta_rad  = np.radians(theta)

    x_pos = np.linspace(0,1.0,100)
    y_surf = np.full_like(x_pos, y_init)
    A2 = np.full_like(x_pos, A1)
    mask = x_pos >= ramp_x
    y_surf[mask] = y_init - (x_pos[mask] - ramp_x) * np.sin(theta_rad)
    A2[mask] = A1 + y_init - y_surf[mask]
    V_local      = V * A1 / A2

    # ── Transition location ───────────────────────────────────────
    dx = .01
    dRe = (rho * V_local * dx) / mu
    Re_local = np.cumsum(dRe)
    is_turbulent = Re_local >= Re_tr
    transition_indices = np.where(is_turbulent)[0]
    if len(transition_indices) > 0:
        x_tr = x_pos[transition_indices[0]]
    else:
        x_tr = x_pos[-1]

    # ── BL thickness —  ─────────
    delta_lam = 4.91 * x_pos / np.sqrt(np.maximum(Re_local, 1e-10))
    delta_turb = 0.382 * x_pos / (np.maximum(Re_local, 1e-10)**0.2)
    transition_width = 0.02  # adjust (0.02–0.1 works well)

    w = 0.5 * (1 + np.tanh((x_pos - x_tr) / transition_width))
    delta_x = (1 - w) * delta_lam + w * delta_turb

    x_stations = np.array([0.1, 0.25, 0.4, 0.55, 0.7, 0.85])
    y_stations = np.linspace(0.0, 0.04, 100)

    def get_velocity_profiles(x_stations, y_stations, x_pos, y_surf, delta_x, Re_local, Re_tr, V_local):
        profiles = {}
        
        for x_s in x_stations:
            # Get data for this specific station
            idx = np.abs(x_pos - x_s).argmin()
            
            delta = delta_x[idx]
            Re = Re_local[idx]
            U_inf = V_local[idx]
            y_floor = y_surf[idx]  # The height of the ramp at this x
            
            # 1. Calculate height relative to the floor
            y_rel = y_stations - y_floor
            
            # 2. Initialize profile with zeros (fluid inside/below the ramp)
            u_profile = np.zeros_like(y_stations)
            
            mask_above_floor = y_rel > 0
            
            eta = np.minimum(y_rel[mask_above_floor] / delta, 1.0)
            
            if Re < Re_tr:
                # Laminar Profile
                u_profile[mask_above_floor] = U_inf * (1.5 * eta - 0.5 * eta**3)
            else:
                # Turbulent Profile
                u_profile[mask_above_floor] = U_inf * (eta**(1/7))
                
            profiles[x_s] = u_profile
            
        return profiles

    profiles = get_velocity_profiles(x_stations, y_stations, x_pos, y_surf, delta_x, Re_local, Re_tr, V_local)

        # ── Draw plate ────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 6))
    fig.patch.set_facecolor(BG_PRIMARY) 
    ax.set_facecolor(BG_PRIMARY)  
    ax.plot(x_pos, y_surf,
            color=ACAD_GREY, linewidth=2.5, zorder=4)

    ax.fill_between(x_pos,
                    y_surf,
                    y_surf - 0.08,
                    color=CLASS_ROYAL, zorder=3)

    # ── BL envelope ───────────────────────────────────────────────
    delta_scaled = delta_x  

    lam_mask  = x_pos <= x_tr
    turb_mask = x_pos > x_tr

    # Laminar region
    ax.plot(x_pos[lam_mask],
            y_surf[lam_mask] + delta_scaled[lam_mask],
            color=USAFA_BLUE, linewidth=2.0, zorder=5,
            label='Laminar BL edge')

    ax.fill_between(x_pos[lam_mask],
                    y_surf[lam_mask],
                    y_surf[lam_mask] + delta_scaled[lam_mask],
                    color=USAFA_BLUE, alpha=0.12, zorder=2)

    # Turbulent region
    if np.any(turb_mask):
        ax.plot(x_pos[turb_mask],
                y_surf[turb_mask] + delta_scaled[turb_mask],
                color=CLASS_RED, linewidth=2.0, zorder=5,
                label='Turbulent BL edge')

        ax.fill_between(x_pos[turb_mask],
                        y_surf[turb_mask],
                        y_surf[turb_mask] + delta_scaled[turb_mask],
                        color=CLASS_RED, alpha=0.12, zorder=2)

    # ── Transition marker ─────────────────────────────────────────
    if x_tr <= L_plate:
        idx_tr = np.abs(x_pos - x_tr).argmin()
        tr_x   = x_pos[idx_tr]
        tr_y   = y_surf[idx_tr]
        tr_d   = delta_scaled[idx_tr]

        ax.plot([tr_x, tr_x],
                [tr_y, tr_y + .025],
                color=CLASS_YELLOW, linewidth=1.2,
                linestyle='--', zorder=6)

        ax.text(tr_x, tr_y + .03,
                f'Transition\nx = {tr_x:.3f} ft\nRe = {Re_tr:,}',
                color=CLASS_YELLOW, fontsize=7,
                fontfamily='monospace',
                ha='center', va='bottom')
    else:
        ax.text(0.6, 0.35,
                'Transition beyond plate\n(fully laminar)',
                color=CLASS_YELLOW, fontsize=7,
                fontfamily='monospace',
                ha='center', style='italic', alpha=0.8)

        # ── Velocity profiles at chosen stations ──────────────────────
    n_vectors = 50
    y_max = 0.04

    bl_edge_x = []
    bl_edge_y = []

    for x_s in x_stations:
        idx = np.abs(x_pos - x_s).argmin()

        y_floor = y_surf[idx]
        U_inf   = V_local[idx]
        Re      = Re_local[idx]
        delta   = delta_x[idx]

        y_pts = np.linspace(y_floor, y_max, n_vectors)

        for y in y_pts:
            y_rel = y - y_floor

            if y_rel <= 0:
                continue

            eta = min(y_rel / delta, 1.0)

            # Velocity profile
            if Re < Re_tr:
                u = U_inf * (1.5 * eta - 0.5 * eta**3)
                color = USAFA_BLUE
            else:
                u = U_inf * (eta ** (1/7))
                color = CLASS_RED

            u_norm = u / U_inf

            arrow_len = u_norm * 0.12

            ax.annotate('',
                        xy=(x_s + arrow_len, y),
                        xytext=(x_s, y),
                        arrowprops=dict(arrowstyle='->',
                                        color=color,
                                        lw=0.8,
                                        mutation_scale=5),
                        zorder=7)

        # ── Boundary layer edge extraction ────────────────────────
        # Find where velocity reaches ~99% freestream
        profile = profiles[x_s]

        idx_edge = np.argmax(profile >= 0.99 * U_inf)

        if profile[idx_edge] >= 0.99 * U_inf:
            y_edge = y_stations[idx_edge]
        else:
            y_edge = y_floor + delta  # fallback

        bl_edge_x.append(x_s)
        bl_edge_y.append(y_edge)

    # ── Freestream arrows ─────────────────────────────────────────
    for y_fs in [0.055, 0.65, 0.75]:
        ax.annotate('',
                    xy=(0.18, y_fs),
                    xytext=(0.02, y_fs),
                    arrowprops=dict(arrowstyle='->',
                                    color=GROTTO_BLUE,
                                    lw=1.2,
                                    mutation_scale=8,
                                    alpha=0.7))

    ax.text(0.10, 0.050,
            f'V∞ = {V:.1f} ft/s',
            color=GROTTO_BLUE, fontsize=7,
            fontfamily='monospace',
            ha='center', alpha=0.8)

    # ── Stats readout ─────────────────────────────────────────────
    Re_end = Re_local[-1]

    ax.text(0.0, -0.018,
            f'Re (plate end) = {Re_end:,.0f}     '
            f'ρ = {rho:.5f} slug/ft³     '
            f'μ = {mu:.2e} slug/ft·s     '
            f'θ = {theta:.1f}°',
            color=ACAD_GREY, fontsize=7,
            fontfamily='monospace')
    

    # ── Legend ────────────────────────────────────────────────────
    ax.legend(loc='upper left',
            facecolor=CLASS_ROYAL,
            edgecolor=USAFA_BLUE,
            labelcolor=ACAD_WHITE,
            fontsize=7,
            framealpha=0.9)

    ax.set_xlim(0.0, L_plate)
    ax.set_ylim(-0.01, 0.04)
    ax.tick_params(axis='x', labelcolor=ACAD_GREY)
    ax.tick_params(axis='y', labelcolor=ACAD_GREY)

    
    st.pyplot(fig, width='content')
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