import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from utils.usafa_styles import USAFA_CSS, render_sidebar, BG_PRIMARY, CLASS_ROYAL, CLASS_YELLOW, CLASS_RED, GROTTO_BLUE, ACAD_GREY, ACAD_WHITE
from utils.airfoils import Airfoil
from utils import aero_core as core

# ── PAGE CONFIGURATION ────────────────────────────────────────────────────────
st.set_page_config(page_title="Airfoil Aero - Virtual Lab", page_icon="🪽", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()

st.markdown('<div class="page-title">Airfoil Aerodynamics</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">From Geometry Elements to Aerodynamic Stall</div>', unsafe_allow_html=True)

# ── GOVERNING CONCEPTS EXPANDER ────────────────────────────────────────────────
with st.expander("📖  Governing Concepts", expanded=False):
    col_geo, col_aero = st.columns(2)
    
    with col_geo:
        st.markdown('<div class="eq-label">Geometric Elements & Planforms</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="explainer">
        1. Chord Line - Line connecting leading and trailing edge<br>
        2. Camber Line - Line equidistant from upper and lower surface<br>
        3. Leading and Trailing Edge (LE/TE) - front and back edges of the airfoil<br>
        4. Thickness - maximum height from lower to upper surface, as a percentage of chord<br>
        </div>
        """, unsafe_allow_html=True)

    with col_aero:
        st.markdown('<div class="eq-label">Aerodynamic Reference Parameters</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="explainer">
        1. Angle of Attack - Angle between chord line and relative wind<br>
        2. Aerodynamic Center - Point where the pitching moment is constant with respect to angle of attack<br>
        3. Center of Pressure - Point where the pitching moment is 0 - moves with respect to angle of attack<br>
        4. Aerodynamic Forces (Lift and Drag) - Lift in the vertical direction, drage opposite the relative wind<br>
        5. Pitching Moment (M) - rotational moment caused by pressure distribution on the airfoil
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── SIDEBAR CONTROLS & LAYOUT ─────────────────────────────────────────────────
col_ctrl, col_plot = st.columns([1, 2])

with col_ctrl:
    st.markdown('<div class="section-header">1. Profile Selection</div>', unsafe_allow_html=True)
    foil_type = st.radio("Airfoil Class", ["Symmetrical (NACA 0012)", "Cambered (NACA 4412)"], label_visibility="collapsed")
    naca_code = "0012" if "Symmetrical" in foil_type else "4412"
    
    st.markdown('<div class="section-header">2. Geometry Layer Toggles</div>', unsafe_allow_html=True)
    show_chord = st.checkbox("Show Chord Line", value=False)
    show_camber = st.checkbox("Show Mean Camber Line", value=False)
    show_labels = st.checkbox("Show Dimension Callouts (LE, TE, Thickness, Camber)", value=False)
    
    st.markdown('<div class="section-header">3. Aerodynamic Controls & Toggles</div>', unsafe_allow_html=True)
    aoa = st.slider("Angle of Attack (α)", min_value=-5.0, max_value=22.0, value=0.0, step=0.5, format="%0.1f°")
    
    show_wind = st.checkbox("Show Relative Wind Vector", value=True)
    show_ac = st.checkbox("Show Aerodynamic Center (AC)", value=False)
    show_cp = st.checkbox("Show Center of Pressure (CP)", value=False)
    show_forces = st.checkbox("Show Aerodynamic Force Vectors (Lift/Drag)", value=False)
    show_mac = st.checkbox("Show Pitching Moment", value=False)
    show_pressure = st.checkbox("Show Upper Surface Pressure Profile", value=False)

# ── AERODYNAMIC CALCULATIONS ──────────────────────────────────────────────────
foil = Airfoil.NACA4(naca_code)
alpha_L0_rad, cm_ac = core.thin_airfoil_coeffs(foil)
cl, cd, stalled, stall_frac = core.lift_drag_coeffs(aoa, alpha_L0_rad)
x_cp, cp_valid = core.cp_location(cl, cm_ac, stall_frac)
x_sep = core.separation_x(aoa, stalled, stall_frac)

# Extract core geometry points
coords = foil.all_points
mid = len(coords[0]) // 2
x_upper_body = coords[0][:mid]
y_upper_body = coords[1][:mid]
x_lower_body = coords[0][mid:]
y_lower_body = coords[1][mid:]
y_camber_body = foil.camber_line(x_upper_body)

# Screen space transformation pivot (Quarter Chord AC in screen space)
pivot = [0.25, 0.0]

# Rotate structural contours
x_up_s, y_up_s = core.rotate_body_to_screen(x_upper_body, y_upper_body, aoa, pivot)
x_lo_s, y_lo_s = core.rotate_body_to_screen(x_lower_body, y_lower_body, aoa, pivot)
x_cam_s, y_cam_s = core.rotate_body_to_screen(x_upper_body, y_camber_body, aoa, pivot)

# Rotate reference lines (Chord line nodes)
x_chord_body = np.array([0.0,  1.0])
y_chord_body = np.array([0.0,  0.0])
x_ch_s, y_ch_s = core.rotate_body_to_screen(x_chord_body, y_chord_body, aoa, pivot)

# ── RENDERING DASHBOARD METRICS ────────────────────────────────────────────────
with col_ctrl:
    st.markdown('<div class="section-header">Aerodynamic Coefficients</div>', unsafe_allow_html=True)
    
    regime_str = "ATTACHED FLOW" if not stalled else "STALLED SEPARATION"
    badge_color = CLASS_YELLOW if not stalled else CLASS_RED
    st.markdown(f'<div class="regime-badge" style="color: {badge_color}; border-color: {badge_color};">{regime_str}</div>', unsafe_allow_html=True)
    
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Lift Coefficient (C<sub style="text-transform: none !important;">l</sub>)</div>
            <div class="metric-value blue">{cl:.3f}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"""
        <div class="metric-card accent-red">
            <div class="metric-label">Drag Coefficient (Cd)</div>
            <div class="metric-value red">{cd:.4f}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"""
        <div class="metric-card accent-red">
            <div class="metric-label">Moment Coefficient (Cm)</div>
            <div class="metric-value yellow">{cm_ac:.4f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    if not cp_valid and show_cp:
        st.markdown("""
        <div class="info-callout" style="border-left-color: var(--class-red);">
            <strong>CP Undefined Near Zero-Lift:</strong><br>
            <span style="color: var(--text-muted); font-size: 0.8rem;">
            When $C_l \rightarrow 0$, vector division yields an asymptotic singularity ($x_{cp} = x_{ac} - \frac{C_{m_{ac}}}{C_l}$). The position marker has been automatically suppressed to prevent non-physical drawing bounds.
            </span>
        </div>
        """, unsafe_allow_html=True)

# ── MATPLOTLIB VISUALIZATION CANVAS ────────────────────────────────────────────
with col_plot:
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor(BG_PRIMARY)
    ax.set_facecolor(BG_PRIMARY)
    
    # Base reference framework limits
    ax.set_xlim(-0.4, 1.4)
    ax.set_ylim(-0.5, 0.6)
    ax.set_aspect('equal', adjustable='box')
    ax.grid(True, linestyle=':', color='#003080', alpha=0.5)
    
    # Hide axis text for a clean, clean laboratory instrument aesthetic
    ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labelleft=False)
    
    # 1. FIXED HORIZONTAL RELATIVE WIND FIELD
    if show_wind:
        for y_pos in np.linspace(-0.4, 0.4, 7):
            # Suppress wind vector lines passing directly through the airfoil core area
            if abs(y_pos) < 0.18:
                ax.annotate('', xy=(-0.08, y_pos), xytext=(-0.35, y_pos),
                            arrowprops=dict(arrowstyle="->", color=ACAD_GREY, lw=1.5, alpha=0.4))
            else:
                ax.annotate('', xy=(1.25, y_pos), xytext=(-0.35, y_pos),
                            arrowprops=dict(arrowstyle="->", color=ACAD_GREY, lw=1.2, alpha=0.25))
        ax.text(-0.35, 0.44, "RELATIVE WIND ($V_\infty$)", color=ACAD_GREY, fontname='sans-serif', fontsize=9, weight='bold')

    # 2. STRUCTURAL GEOMETRY LAYERS
    # Core airfoil perimeter skin
    ax.plot(x_up_s, y_up_s, color=GROTTO_BLUE, linewidth=2.5, label="Upper Surface")
    ax.plot(x_lo_s, y_lo_s, color=GROTTO_BLUE, linewidth=2.5, label="Lower Surface")
    
    if show_chord:
        ax.plot(x_ch_s, y_ch_s, color=CLASS_YELLOW, linestyle='-.', linewidth=1.5, label="Chord Line")
        # Inline label placed at 70% chord, tracking the AoA pitch angle
        ax.text(x_ch_s[0] + 0.7*(x_ch_s[1]-x_ch_s[0]), y_ch_s[0] + 0.7*(y_ch_s[1]-y_ch_s[0]) - 0.03, 
                "CHORD LINE", color=CLASS_YELLOW, fontsize=8, weight='bold', rotation=-aoa, ha='center')
        
    if show_camber:
        ax.plot(x_cam_s, y_cam_s, color=CLASS_RED, linestyle='--', linewidth=1.5, label="Mean Camber Line")
        # Inline label placed near mid-chord
        mid_idx = len(x_cam_s) // 2
        ax.text(x_cam_s[mid_idx], y_cam_s[mid_idx] + 0.02, 
                "MEAN CAMBER LINE", color=CLASS_RED, fontsize=8, weight='bold', rotation=-aoa, ha='center')
        
    # 3. GEOMETRY CALLOUTS & LABELS
    if show_labels:
        # Trace structural nodes for indicators
        le_s = [x_ch_s[0], y_ch_s[0]]
        te_s = [x_ch_s[1], y_ch_s[1]]
        
        # LE Label
        ax.plot(le_s[0], le_s[1], 'o', color=ACAD_WHITE, markersize=5)
        ax.text(le_s[0] - 0.04, le_s[1] + 0.01, "L.E.", color=ACAD_WHITE, fontsize=9, weight='bold', ha='right')
        
        # TE Label
        ax.plot(te_s[0], te_s[1], 'o', color=ACAD_WHITE, markersize=5)
        ax.text(te_s[0] + 0.02, te_s[1], "T.E.", color=ACAD_WHITE, fontsize=9, weight='bold', ha='left')
        
        # Calculate Max Camber (Max distance from chord line in body frame)
        idx_max_camber = np.argmax(y_camber_body)
        max_camber_val = y_camber_body[idx_max_camber]
        
        if max_camber_val > 0.001:
            # Rotate body points to screen space to anchor the callout
            cx_body = np.array([x_upper_body[idx_max_camber], x_upper_body[idx_max_camber]])
            cy_body = np.array([0.0, max_camber_val])
            cx_s, cy_s = core.rotate_body_to_screen(cx_body, cy_body, aoa, pivot)
            
            ax.annotate('', xy=(cx_s[1], cy_s[1]), xytext=(cx_s[0], cy_s[0]),
                        arrowprops=dict(arrowstyle="<->", color=CLASS_RED, lw=1.2))
            ax.text(cx_s[1] + 0.02, cy_s[1]-0.1, f"Max Camber ({max_camber_val*100:.1f}%)", 
                    color=CLASS_RED, fontsize=8, weight='bold', ha='left', va='center')

        # Calculate Max Thickness (Max distance between upper and lower surfaces)
        thickness_dist = y_upper_body - y_lower_body
        idx_max_thick = np.argmax(thickness_dist)
        max_thick_val = thickness_dist[idx_max_thick]
        
        tx_body = np.array([x_upper_body[idx_max_thick], x_upper_body[idx_max_thick]])
        ty_body = np.array([y_lower_body[idx_max_thick], y_upper_body[idx_max_thick]])
        tx_s, ty_s = core.rotate_body_to_screen(tx_body, ty_body, aoa, pivot)
        
        ax.annotate('', xy=(tx_s[1], ty_s[1]), xytext=(tx_s[0], ty_s[0]),
                    arrowprops=dict(arrowstyle="<->", color=GROTTO_BLUE, lw=1.2))
        ax.text(tx_s[0] - 0.02, (ty_s[0] + ty_s[1])/2+.1, f"Max Thickness ({max_thick_val*100:.1f}%)", 
                color=GROTTO_BLUE, fontsize=8, weight='bold', ha='right', va='center')
        
    # 4. HIGH-FIDELITY PRESSURE DISTRIBUTION MODELING
    if show_pressure:
        # Avoid division-by-zero right at the leading edge node
        x_safe = np.clip(x_upper_body, 0.001, 0.999)
        
        # 1. Base inviscid pressure distribution (Thin Airfoil Theory approximation)
        cl_clamped = max(0.05, cl) if cl >= 0 else min(-0.05, cl)
        p_dist = cl_clamped * (0.45 * np.sqrt((1.0 - x_safe) / x_safe) + 0.55 * np.sqrt(x_safe * (1.0 - x_safe)))
        
        # Enforce physical smoothness right at the trailing edge (Kutta condition)
        p_dist *= (1.0 - x_safe) ** 0.15

        # 2. Viscous Flow Separation / Stall Modification
        if stalled:
            sep_idx = int(x_sep * len(x_upper_body))
            p_base_wake = p_dist[sep_idx] * 0.25 if sep_idx < len(p_dist) else 0.03
            
            # CRITICAL: Apply heavy exponential reduction to the baseline profile past stall
            # This ensures the prominent leading edge spike shrinks radically as separation progresses
            p_dist *= np.exp(-2.5 * stall_frac)
            
            # Set the separated wake zone to a constant low-pressure plateau
            p_dist[sep_idx:] = p_base_wake

        # Scale coefficient of pressure offset to fit nicely within plot coordinate bounds
        p_scale = 0.12 
        
        # CRITICAL: Clamp the upper bounds mathematically before transformation
        # This keeps the first few leading-edge arrows from running off the canvas grid entirely
        p_dist = np.clip(p_dist, -0.2, 3.2)
        
        # Displace the distribution curve normal to the pitched surface geometry
        px_s = x_up_s
        py_s = y_up_s + p_dist * p_scale
        
        # Color distribution mapping gradient based on flow state
        p_color = CLASS_RED if stalled else CLASS_YELLOW
        ax.plot(px_s, py_s, color=p_color, linewidth=1.8, linestyle='-')
        
        # Draw normal pressure lines anchoring the profile back onto the upper skin surface
        step_inc = 4
        for i in range(0, len(px_s), step_inc):
            ax.annotate('', xy=(x_up_s[i], y_up_s[i]), xytext=(px_s[i], py_s[i]),
                        arrowprops=dict(arrowstyle="<-", color=p_color, lw=0.8, alpha=0.5))
            
        # Hard-coded label height keeps the text position strictly locked
        ax.text(0.3, 0.48, "Pressure Distribution", 
                color=p_color, fontsize=8, weight='bold', ha='center')

    # ── CRITICAL: FORCED BOUNDING BOX CONSTRAINTS ─────────────────────────────
    ax.set_xlim(-0.4, 1.4)
    ax.set_ylim(-0.4, 0.55)  # Strictly locks the canvas view size

    # 5. AERODYNAMIC REFERENCE POINTER ATTACHMENTS (AC / CP)
    if show_ac:
        # AC mapped right on the fixed structural rotation hinge point
        ax.plot(pivot[0], pivot[1], marker='^', color=GROTTO_BLUE, markersize=9, zorder=5, label="Aerodynamic Center (AC)")
        ax.text(pivot[0], pivot[1] - 0.07, "AC (25%)", color=GROTTO_BLUE, fontsize=9, weight='bold', ha='center', va='top')

    if show_cp and cp_valid:
        # Map body frame CP and rotate it dynamically into screen space coordinates
        x_cp_s, y_cp_s = core.rotate_body_to_screen(np.array([x_cp]), np.array([0.0]), aoa, pivot)
        ax.plot(x_cp_s[0], y_cp_s[0], marker='o', color=CLASS_YELLOW, markersize=9, zorder=5, label="Center of Pressure (CP)")
        ax.text(x_cp_s[0], y_cp_s[0] + 0.04, f"CP ({x_cp*100:.1f}%)", color=CLASS_YELLOW, fontsize=9, weight='bold', ha='center', va='bottom')

    # 6. RESULTANT VECTOR PORTS (LIFT / DRAG Forces acting out of the CP/AC node)
    if show_forces:
        # Determine force anchor point depending on what is activated or visible
        f_x, f_y = pivot[0], pivot[1]
        if show_cp and cp_valid:
            x_cp_s, y_cp_s = core.rotate_body_to_screen(np.array([x_cp]), np.array([0.0]), aoa, pivot)
        #     f_x, f_y = x_cp_s[0], y_cp_s[0]
            
        force_scale = 0.20
        cd_scale = 10.0
        vec_lift = cl * force_scale
        vec_drag = cd * force_scale * cd_scale
        
        # Lift Vector (Perpendicular to relative wind vector - straight UP vertically)
        if abs(cl) > 0.01:
            ax.annotate('', xy=(f_x, f_y + vec_lift), xytext=(f_x, f_y),
                        arrowprops=dict(facecolor=GROTTO_BLUE, edgecolor=GROTTO_BLUE, width=3, headwidth=8, shrink=0))
            ax.text(f_x - 0.03, f_y + vec_lift, "LIFT (L)", color=GROTTO_BLUE, fontsize=10, weight='bold', ha='right', va='center')
            
        # Drag Vector (Parallel to relative wind vector - straight RIGHT horizontally)
        if vec_drag > 0.002:
            ax.annotate('', xy=(f_x + vec_drag, f_y), xytext=(f_x, f_y),
                        arrowprops=dict(facecolor=CLASS_RED, edgecolor=CLASS_RED, width=3, headwidth=8, shrink=0))
            ax.text(f_x + vec_drag + 0.03, f_y, "DRAG (D)", color=CLASS_RED, fontsize=10, weight='bold', ha='left', va='center')
    if show_mac:
        # Scale moment magnitude and apply stall decay factor so it shrinks cleanly
        cm_eff = cm_ac * np.exp(-2.0 * stall_frac) if stalled else cm_ac
        
        # Symmetrical sections naturally yield cm_ac = 0. Only render if a moment exists.
        if abs(cm_eff) > 0.001:
            # Traditional nose-down pitch is negative; we plot a curved arrow counter-clockwise/clockwise
            is_nose_down = cm_eff < 0
            angle_start = 45 if is_nose_down else 225
            angle_end = 225 if is_nose_down else 45
            
            # Generate parametric arc geometry around the AC hinge point
            r_arc = 0.08
            theta_arc = np.linspace(np.radians(angle_start), np.radians(angle_end), 50)
            arc_x = pivot[0] + r_arc * np.cos(theta_arc)
            arc_y = pivot[1] + r_arc * np.sin(theta_arc)
            
            # Render arc ring path
            ax.plot(arc_x, arc_y, color=CLASS_YELLOW, linewidth=2)
            
            # ── HIGH-FIDELITY TANGENT ARROWHEAD ALIGNMENT ─────────────────────
            # Calculate the local directional step at the very tip of the arc
            dx = arc_x[-1] - arc_x[-2]
            dy = arc_y[-1] - arc_y[-2]
            ds = np.hypot(dx, dy)
            
            # Establish a clean segment length for the arrowhead assembly basis
            scale = 0.015
            tx = (dx / ds) * scale
            ty = (dy / ds) * scale
            
            # Draw the arrowhead perfectly locked on the terminal index coordinates
            # shrinkA=0 and shrinkB=0 ensure Matplotlib doesn't apply padding offsets
            ax.annotate('', 
                        xy=(arc_x[-1], arc_y[-1]), 
                        xytext=(arc_x[-1] - tx, arc_y[-1] - ty),
                        arrowprops=dict(arrowstyle="->", 
                                        color=CLASS_YELLOW, 
                                        lw=2.5, 
                                        mutation_scale=11,
                                        shrinkA=0, 
                                        shrinkB=0))
            
            ax.text(pivot[0]-r_arc-0.08, pivot[1], f"Moment", 
                    color=CLASS_YELLOW, fontsize=9, weight='bold', ha='center', va='bottom')
        else:
            # Explanatory prompt for symmetric sections where moment is non-existent
            ax.text(pivot[0], pivot[1] + 0.12, "M_ac = 0 (Symmetrical)", 
                    color=ACAD_GREY, fontsize=8, style='italic', ha='center', alpha=0.7)
            
    # Remove extra visual border cladding frames from plot layout box
    for spine in ['top', 'bottom', 'left', 'right']:
        ax.spines[spine].set_color('#003080')
        ax.spines[spine].set_alpha(0.3)
        
    st.pyplot(fig)