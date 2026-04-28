import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
from utils.usafa_styles import *
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Climb - Virtual Lab", page_icon="🗻", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">Climb Performance</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Maximum Angle &nbsp;·&nbsp; Maximum Rate</div>', unsafe_allow_html=True)

# ── Equations ─────────────────────────────────────────────────────────────────
with st.expander("📖  Governing Equations", expanded=True):
    col_eq1, col_eq2 = st.columns(2)

    with col_eq1:
        st.markdown('<div class="eq-label">Climb Angle</div>', unsafe_allow_html=True)
        st.latex(r"\sin\gamma = \frac{T - D}{W}")
        st.latex(r"\gamma = \sin^{-1}\!\left(\frac{T-D}{W}\right)")
        st.markdown("""
        <div class="explainer">
        The climb angle (γ) is determined by the excess thrust available above what is
        required to overcome drag. Maximum climb angle occurs at the velocity where
        the difference (T − D) is greatest.
        </div>
        """, unsafe_allow_html=True)

    with col_eq2:
        st.markdown('<div class="eq-label">Rate of Climb</div>', unsafe_allow_html=True)
        st.latex(r"R/C = V_\infty \sin\gamma = \frac{(T-D)\,V_\infty}{W} = \frac{P_A - P_R}{W}")
        st.markdown("""
        <div class="explainer">
        Rate of climb (R/C) depends on <b>excess power</b> — the difference between
        power available (PA) and power required (PR). Maximum R/C occurs at a different
        (higher) airspeed than maximum climb angle, since velocity amplifies the
        power surplus even as the thrust margin narrows.
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Aircraft parameters (fixed) ───────────────────────────────────────────────
W     = 6000.0   # lb
T_max = 1800.0   # lb  (max thrust, assumed constant — jet)
CD0   = 0.018
e0    = 0.82
AR    = 3.5      # delta wing — low AR
h     = 10000    # ft
rho   = 0.001756 # slug/ft³ at ~10,000 ft
S     = 380.0    # ft²  — notional fighter planform
n     = 1.0

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Weight (lb)",      f"{W:.0f}")
col_m2.metric("Max Thrust (lb)",  f"{T_max:.0f}")
col_m3.metric("Altitude (ft)",    f"{h:,}")
col_m4.metric("Wing Area (ft²)",  f"{S:.0f}")

st.markdown("**Airspeed (kts)**")
V_knots = st.slider("velocity", min_value=100.0, max_value=350.0,
                     value=250.0, step=1.0,
                     format="V = %.0f kts",
                     label_visibility="collapsed")

@st.fragment
def render_climb(V_knots: float) -> None:

    # ── Derived ───────────────────────────────────────────────────
    k            = 1.0 / (np.pi * e0 * AR)
    V_fts        = V_knots * 1.687
    q            = 0.5 * rho * V_fts**2

    # Velocity sweep
    V_range_kts  = np.linspace(100, 350, 300)
    V_range_fts  = V_range_kts * 1.687
    q_arr        = 0.5 * rho * V_range_fts**2

    CL_arr       = (W * n) / (q_arr * S)
    CD_arr       = CD0 + k * CL_arr**2
    D_arr        = CD_arr * q_arr * S          # drag required (lb)
    PR_arr       = D_arr * V_range_fts         # power required (ft·lb/s)
    PA_arr       = np.full_like(PR_arr, T_max * V_range_fts)  # PA = T * V

    # Excess thrust & power
    excess_T     = T_max - D_arr
    excess_P     = PA_arr - PR_arr

    # Current condition
    CL_curr      = (W * n) / (q * S)
    CD_curr      = CD0 + k * CL_curr**2
    D_curr       = CD_curr * q * S
    PR_curr      = D_curr * V_fts
    PA_curr      = T_max * V_fts
    excess_T_curr = T_max - D_curr
    excess_P_curr = PA_curr - PR_curr

    gamma_rad    = np.arcsin(np.clip(excess_T_curr / W, -1, 1))
    gamma_deg    = np.degrees(gamma_rad)
    RC           = V_fts * np.sin(gamma_rad)   # ft/s
    RC_fpm       = RC * 60                      # ft/min

    # Best angle — max (T-D)
    idx_gamma    = np.argmax(excess_T)
    V_gamma_kts  = V_range_kts[idx_gamma]
    gamma_max    = np.degrees(np.arcsin(np.clip(excess_T[idx_gamma] / W, -1, 1)))

    # Best rate — max (PA-PR)
    idx_rc       = np.argmax(excess_P)
    V_rc_kts     = V_range_kts[idx_rc]
    RC_max_fpm   = excess_P[idx_rc] / W * 60

    # ── Metrics ───────────────────────────────────────────────────
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc2.metric("Climb Angle γ",    f"{gamma_deg:.1f}°")
    mc3.metric("Rate of Climb",    f"{RC_fpm:.0f} fpm")
    

    # ── Plot theme ────────────────────────────────────────────────
    plot_theme = dict(
        paper_bgcolor=BG_PRIMARY,
        plot_bgcolor=BG_SECONDARY,
        font=dict(family='Barlow Condensed, Trebuchet MS, sans-serif',
                  color=ACAD_GREY, size=11),
        title_font=dict(color=ACAD_WHITE, size=13,
                        family='Barlow Condensed, Trebuchet MS, sans-serif'),
    )
    ax_style = dict(gridcolor='#1e2d5a', zerolinecolor='#1e2d5a',
                    linecolor='#003080', color=ACAD_GREY)
    leg_style = dict(bgcolor=CLASS_ROYAL, bordercolor=USAFA_BLUE,
                     font=dict(color=ACAD_WHITE, size=9), x=0.75, y=0.99)

    with st.expander("📊  Performance Charts", expanded=True):

        # ── Thrust / Drag vs Airspeed ─────────────────────────────
        fig_td = go.Figure()

        fig_td.add_trace(go.Scatter(
            x=V_range_kts, y=D_arr, mode='lines',
            name='Thrust Required (Drag)',
            line=dict(color=USAFA_BLUE, width=2)
        ))
        fig_td.add_trace(go.Scatter(
            x=V_range_kts, y=np.full_like(V_range_kts, T_max), mode='lines',
            name='Thrust Available',
            line=dict(color=CLASS_RED, width=2, dash='dash')
        ))
        fig_td.add_trace(go.Scatter(
            x=[V_knots], y=[D_curr], mode='markers',
            name='Current Condition',
            marker=dict(size=12, symbol='x', color=GROTTO_BLUE, line=dict(width=2))
        ))

        # Best angle marker
        fig_td.add_trace(go.Scatter(
            x=[V_gamma_kts], y=[D_arr[idx_gamma]], mode='markers+text',
            name=f'Max γ  ({V_gamma_kts:.0f} kts)',
            text=[f'  max γ = {gamma_max:.1f}°'],
            textposition='top right',
            textfont=dict(color=CLASS_YELLOW, size=9),
            marker=dict(size=10, symbol='circle-open',
                        color=CLASS_YELLOW, line=dict(width=2))
        ))

        # Excess thrust shading between T_max and D
        fig_td.add_trace(go.Scatter(
            x=np.concatenate([V_range_kts, V_range_kts[::-1]]),
            y=np.concatenate([np.full_like(V_range_kts, T_max), D_arr[::-1]]),
            fill='toself', fillcolor='rgba(0,53,148,0.12)',
            line=dict(width=0), showlegend=False,
            hoverinfo='skip'
        ))

        fig_td.add_vline(x=V_gamma_kts, line_dash='dot',
                         line_color=CLASS_YELLOW, line_width=1, opacity=0.5)

        fig_td.update_layout(
            **plot_theme,
            height=350,
            title=dict(text='THRUST AVAILABLE & REQUIRED vs AIRSPEED', x=0.05),
            xaxis=dict(title='Airspeed (kts)', **ax_style),
            yaxis=dict(title='Thrust / Drag (lb)', **ax_style),
            legend=leg_style
        )

        st.plotly_chart(fig_td, width='stretch')

        # ── Power Available / Required vs Airspeed ────────────────
        fig_pw = go.Figure()

        fig_pw.add_trace(go.Scatter(
            x=V_range_kts, y=PR_arr / 550, mode='lines',
            name='Power Required',
            line=dict(color=USAFA_BLUE, width=2)
        ))
        fig_pw.add_trace(go.Scatter(
            x=V_range_kts, y=PA_arr / 550, mode='lines',
            name='Power Available',
            line=dict(color=CLASS_RED, width=2, dash='dash')
        ))
        fig_pw.add_trace(go.Scatter(
            x=[V_knots], y=[PR_curr / 550], mode='markers',
            name='Current Condition',
            marker=dict(size=12, symbol='x', color=GROTTO_BLUE, line=dict(width=2))
        ))

        # Best R/C marker
        fig_pw.add_trace(go.Scatter(
            x=[V_rc_kts], y=[PR_arr[idx_rc] / 550], mode='markers+text',
            name=f'Max R/C  ({V_rc_kts:.0f} kts)',
            text=[f'  max R/C = {RC_max_fpm:.0f} fpm'],
            textposition='top right',
            textfont=dict(color=CLASS_YELLOW, size=9),
            marker=dict(size=10, symbol='circle-open',
                        color=CLASS_YELLOW, line=dict(width=2))
        ))

        # Excess power shading
        fig_pw.add_trace(go.Scatter(
            x=np.concatenate([V_range_kts, V_range_kts[::-1]]),
            y=np.concatenate([PA_arr / 550, PR_arr[::-1] / 550]),
            fill='toself', fillcolor='rgba(0,53,148,0.12)',
            line=dict(width=0), showlegend=False,
            hoverinfo='skip'
        ))

        fig_pw.add_vline(x=V_rc_kts, line_dash='dot',
                         line_color=CLASS_YELLOW, line_width=1, opacity=0.5)
        fig_pw.add_vline(x=V_gamma_kts, line_dash='dot',
                         line_color=ACAD_GREY, line_width=1, opacity=0.4)

        fig_pw.update_layout(
            **plot_theme,
            height=350,
            title=dict(text='POWER AVAILABLE & REQUIRED vs AIRSPEED', x=0.05),
            xaxis=dict(title='Airspeed (kts)', **ax_style),
            yaxis=dict(title='Power (hp)', **ax_style),
            legend=leg_style
        )

        st.plotly_chart(fig_pw, width='stretch')

    # ── 3D climb trajectory ───────────────────────────────────────
    climb_range  = 50000        # ft horizontal distance to show
    climb_alt    = V_fts * np.sin(gamma_rad) * (climb_range / V_fts)  # alt gained

    vis          = 80.0
    half_span    = (S**0.5 / 2) * vis
    chord        = (S / (AR**0.5)) / S * vis * S**0.5
    fuse_len     = chord * 1.5
    fuse_rad     = chord * 0.12
    fuse_h       = h * 0.008
    tail_half    = half_span * 0.3
    tail_chord   = chord * 0.35

    fig3 = go.Figure()

    # ── Delta wing (triangle) — 3 vertices each side ──────────────
    # Triangle: LE tip at nose (x=0), TE span at x=-chord
    wing_x = [0, -chord, -chord,   0, -chord, -chord]
    wing_y = [0,  0,      half_span, 0,  0,    -half_span]
    wing_z = [h,  h,      h,         h,  h,      h]

    fig3.add_trace(go.Mesh3d(
        x=wing_x, y=wing_y, z=wing_z,
        i=[0, 3], j=[1, 4], k=[2, 5],
        color=ACAD_WHITE, opacity=0.9, flatshading=True,
        name='Wing', showlegend=False
    ))

    # ── Tail ──────────────────────────────────────────────────────
    tail_x = [-fuse_len*0.8, -fuse_len*0.8 - tail_chord,
              -fuse_len*0.8 - tail_chord, -fuse_len*0.8,
              -fuse_len*0.8, -fuse_len*0.8 - tail_chord,
              -fuse_len*0.8 - tail_chord, -fuse_len*0.8]
    tail_y = [0, 0,  tail_half,  tail_half,
              0, 0, -tail_half, -tail_half]
    tail_z = [h] * 8

    fig3.add_trace(go.Mesh3d(
        x=tail_x, y=tail_y, z=tail_z,
        i=[0, 0, 4, 4], j=[1, 2, 5, 6], k=[2, 3, 6, 7],
        color=ACAD_WHITE, opacity=0.9, flatshading=True,
        name='Tail', showlegend=False
    ))

    # ── Fuselage ──────────────────────────────────────────────────
    fig3.add_trace(go.Mesh3d(
        x=[ fuse_len*0.2,  fuse_len*0.2,  fuse_len*0.2,  fuse_len*0.2,
           -fuse_len*0.8, -fuse_len*0.8, -fuse_len*0.8, -fuse_len*0.8],
        y=[ fuse_rad, -fuse_rad, -fuse_rad,  fuse_rad,
            fuse_rad, -fuse_rad, -fuse_rad,  fuse_rad],
        z=[ h + fuse_h, h + fuse_h, h - fuse_h, h - fuse_h,
            h + fuse_h, h + fuse_h, h - fuse_h, h - fuse_h],
        alphahull=0, color=CLASS_YELLOW, opacity=0.9,
        name='Fuselage', showlegend=False
    ))

    # ── Climb path ────────────────────────────────────────────────
    fig3.add_trace(go.Scatter3d(
        x=[0, climb_range], y=[0, 0], z=[h, h + climb_alt],
        mode='lines', name='Climb Path',
        line=dict(color=CLASS_RED, width=4)
    ))

    # ── Horizontal reference ──────────────────────────────────────
    fig3.add_trace(go.Scatter3d(
        x=[0, climb_range * 0.4], y=[0, 0], z=[h, h],
        mode='lines',
        line=dict(color=ACAD_GREY, width=2, dash='dash'),
        showlegend=False
    ))

    # ── γ label ───────────────────────────────────────────────────
    fig3.add_trace(go.Scatter3d(
        x=[climb_range * 0.2], y=[0],
        z=[h + climb_range * 0.2 * np.tan(gamma_rad) * 0.5],
        mode='text',
        text=[f'γ = {gamma_deg:.1f}°'],
        textfont=dict(color=CLASS_YELLOW, size=13),
        showlegend=False
    ))

    # ── Ground plane ──────────────────────────────────────────────
    gx = np.linspace(0, climb_range * 1.05, 10)
    gy = np.linspace(-half_span * 3, half_span * 3, 10)
    gx, gy = np.meshgrid(gx, gy)
    fig3.add_trace(go.Surface(
        x=gx, y=gy, z=np.zeros_like(gx),
        showscale=False, opacity=0.20,
        colorscale=[[0, CLASS_ROYAL], [1, USAFA_BLUE]],
        name='Ground', showlegend=False
    ))

    # ── x-axis ticks in nm ────────────────────────────────────────
    tick_ft   = np.linspace(0, climb_range * 1.05, 6)
    tickvals  = tick_ft.tolist()
    ticktext  = [f'{v/6076:.2f}' for v in tick_ft]

    alt_max = max(h + climb_alt * 1.2, h * 1.15)

    fig3.update_layout(
        paper_bgcolor=BG_PRIMARY,
        scene=dict(
            bgcolor=BG_PRIMARY,
            xaxis=dict(title='Distance (nm)', color=ACAD_GREY,
                       gridcolor='#1e2d5a', backgroundcolor=BG_PRIMARY,
                       tickvals=tickvals, ticktext=ticktext),
            yaxis=dict(title='Lateral (ft)', color=ACAD_GREY,
                       gridcolor='#1e2d5a', backgroundcolor=BG_PRIMARY,
                       range=[-half_span * 3, half_span * 3]),
            zaxis=dict(title='Altitude (ft)', color=ACAD_GREY,
                       gridcolor='#1e2d5a', backgroundcolor=BG_PRIMARY,
                       range=[0, alt_max]),
            aspectmode='manual',
            aspectratio=dict(x=2.0, y=0.5, z=1.0),
            camera=dict(eye=dict(x=1.4, y=1.4, z=0.7))
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=500
    )

    st.markdown('<div class="eq-label">Climb Trajectory</div>', unsafe_allow_html=True)
    st.plotly_chart(fig3, width='stretch')

render_climb(V_knots)

st.divider()
with st.expander("💡  Physical Intuition"):
    st.markdown("""
        **What's the difference?**

        - **Maximum climb angle** - this uses excess thrust to get over an obstacle before reaching it. (**Climb v. Distance**)
        - **Maximum rate of climb** - this uses excess power (T*V) to get as high as possible in a given ammount of time. (**Climb v. Time**)
        """)
    st.markdown("""
        **What happens at high speeds?**

        - If **Thrust Available** < **Thrust Required** an aircraft must descend (-γ) to maintain airspeed.
        - This occurs at the same point where **Power Available** < **Power Required**.
        """)