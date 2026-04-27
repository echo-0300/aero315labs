import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
from utils.usafa_styles import *
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Glide - Virtual Lab", page_icon="🍂", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()

# ── Page Header (static) ──────────────────────────────────────────────────────
st.markdown('<div class="page-title">Glide Performance</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Maximum Range &nbsp;·&nbsp;  Minimum Sink Rate</div>', unsafe_allow_html=True)

# ── Equations (static) ────────────────────────────────────────────────────────
with st.expander("📖  Governing Equations", expanded=True):
    col_eq1, col_eq2 = st.columns(2)

    with col_eq1:
        st.markdown('<div class="eq-label">Glide (Power Off) Performance</div>', unsafe_allow_html=True)
        st.latex(r"D=W \sin (\gamma)")
        st.latex(r"L=W \cos (\gamma)")
        st.markdown("""
        <div class="explainer">
        The glide performance is defined by the the lift, drag, weight, and flight path angle (<em>γ</em>).
        Where a positve γ is downwards.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="eq-label">Maximum Glide Range</div>', unsafe_allow_html=True)
        st.latex(r"\tan \gamma=\frac{h}{R}")
        st.latex(r"\frac{L}{D}=\frac{R}{h}")
        st.markdown("""
        <div class="explainer">
        Glide range is maximized when the flight path angle is minimized (while still sustaining steady flight). This
        is achieved at the maximum lift to drag ratio.
        </div>
        """, unsafe_allow_html=True)
    with col_eq2:
        st.markdown('<div class="eq-label">Minimum Sink Rate</div>', unsafe_allow_html=True)
        st.latex(r"V_\infty \sin\gamma = \frac{P_R}{W}")
        st.markdown("""
        <div class="explainer">
        Sink rate is minimized by flying at the velocity for minimum power required. 
        </div>
        """, unsafe_allow_html=True)

st.divider()

#----- Plane Geo
W = 4000 #lb
CD0 = 0.02
e0 = 0.90
k = 0.0570
h = 15000 #ft
n = 1 #load factor
rho = .001496 #slug/ft^3

col_1, col_2, col_3, col_4 = st.columns([1,1,1,1])

with col_1:
    st.metric(label="Weight (lbs)", value = W, format='%.1f lbs')
    S = st.slider(
            label="Planform Area (ft²)",
            min_value=60.0, max_value=200.0,
            value=100.0, step=1.0,
            format="S = %.2f ft²",
            label_visibility="visible",
            key="planform"
        )
with col_2:
    st.metric(label=r"$C_{D_0}$", value = CD0, format='%.4f')
    c_ft = st.slider(
            label="Chord (ft)",
            min_value=2.0, max_value=12.0,
            value=7.0, step=0.1,
            format=r"$c$ = %.2f ft",
            label_visibility="visible",
            key="c"
        )
    
    
with col_3:
    st.metric(label=r"Altitude (ft)", value = h, format='%.1f ft')
    V_knots = st.slider(
            label="Velocity (kts)",
            min_value=60.0, max_value=240.0,
            value=160.0, step=1.0,
            format=r"$V$ = %.2f knots",
            label_visibility="visible",
            key="V"
        )
    
with col_4:
    st.metric(label=r"Oswald Efficiency Factor", value = e0, format='%.2f')

@st.fragment
def render_perf(S: float, c_ft: float, V_knots: float):
    V_fts = V_knots * 1.687
    AR = S / c_ft ** 2
    k = 1 / (np.pi * e0 * AR)
    q = 0.5 * rho * V_fts **2

    V_range_fts = np.linspace(60, 240, 100) * 1.687 
    q_array = 0.5 * rho * V_range_fts ** 2
    Cl_array = np.linspace(-1.6, 1.6, 100)
    Cd_array = CD0 + k * Cl_array ** 2

    Cl_V_curve = (W * n) / (q_array * S)
    Cd_V_curve = CD0 + k * Cl_V_curve ** 2
    LD_array = Cl_V_curve / Cd_V_curve

    idx = np.argmax(LD_array)
    V_star = (V_range_fts[idx] / 1.687)
    Cl_star = Cl_V_curve[idx]
    Cd_star = Cd_V_curve[idx]
    max_ld = LD_array[idx]

    # Current Flight Condition
    Cl_curr = (W * n) / (q * S)
    Cd_curr = CD0 + k * Cl_curr ** 2
    LD_curr = Cl_curr / Cd_curr
    D = Cd_curr * q * S
    glide_ratio = LD_curr
    gamma_deg = np.rad2deg(np.atan(1 / glide_ratio))
    R = W / D
    slope        = Cd_star / Cl_star
    Cl_line_pts  = np.array([0, max(Cl_array)])
    V_knots_axis = V_range_fts / 1.687

    plot_theme = dict(
        paper_bgcolor=BG_PRIMARY,
        plot_bgcolor=BG_SECONDARY,
        font=dict(family='Barlow Condensed, Trebuchet MS, sans-serif',
                  color=ACAD_GREY, size=11),
        title_font=dict(color=ACAD_WHITE, size=13,
                        family='Barlow Condensed, Trebuchet MS, sans-serif')
    )

    # ── Drag Polar ────────────────────────────────────────────────
    fig_polar = go.Figure()

    fig_polar.add_trace(go.Scatter(
        x=Cl_array, y=Cd_array, mode='lines',
        name='Drag Polar',
        line=dict(color=USAFA_BLUE, width=2)
    ))
    fig_polar.add_trace(go.Scatter(
        x=[Cl_curr], y=[Cd_curr], mode='markers',
        name='Current Condition',
        marker=dict(size=12, symbol='x', color=GROTTO_BLUE, line=dict(width=2))
    ))
    fig_polar.add_trace(go.Scatter(
        x=Cl_line_pts, y=slope * Cl_line_pts, mode='lines',
        name='Max L/D Tangent',
        line=dict(dash='dash', color=CLASS_YELLOW, width=1.5)
    ))

    fig_polar.update_layout(
        **plot_theme,
        height=350,
        title=dict(text='DRAG POLAR', x=0.05),
        xaxis=dict(title='Coefficient of Lift (CL)',
                   gridcolor='#1e2d5a', zerolinecolor='#1e2d5a',
                   linecolor='#003080', color=ACAD_GREY),
        yaxis=dict(title='Coefficient of Drag (CD)',
                   gridcolor='#1e2d5a', zerolinecolor='#1e2d5a',
                   linecolor='#003080', color=ACAD_GREY),
        legend=dict(bgcolor=CLASS_ROYAL, bordercolor=USAFA_BLUE,
                    font=dict(color=ACAD_WHITE, size=9),
                    x=0.75, y=0.99)
    )

    # ── L/D vs Velocity ───────────────────────────────────────────
    fig_ld = go.Figure()

    fig_ld.add_trace(go.Scatter(
        x=V_knots_axis, y=LD_array, mode='lines',
        name='L/D Curve',
        line=dict(color=USAFA_BLUE, width=2)
    ))
    fig_ld.add_trace(go.Scatter(
        x=[V_knots], y=[LD_curr], mode='markers',
        name='Current V',
        marker=dict(size=12, symbol='x', color=GROTTO_BLUE, line=dict(width=2))
    ))
    fig_ld.add_trace(go.Scatter(
        x=[V_star], y=[max_ld], mode='markers+text',
        name=f'Best Glide  V* = {V_star:.0f} kt',
        text=[f'  {V_star:.0f} kt'],
        textposition='middle right',
        textfont=dict(color=CLASS_YELLOW, size=10),
        marker=dict(size=10, symbol='circle-open',
                    color=CLASS_YELLOW, line=dict(width=2))
    ))

    fig_ld.add_vline(x=V_star, line_dash='dot', line_color=CLASS_YELLOW,
                     line_width=1, opacity=0.5)

    fig_ld.update_layout(
        **plot_theme,
        height=350,
        title=dict(text='LIFT-TO-DRAG RATIO vs VELOCITY', x=0.05),
        xaxis=dict(title='Velocity (kts)',
                   gridcolor='#1e2d5a', zerolinecolor='#1e2d5a',
                   linecolor='#003080', color=ACAD_GREY),
        yaxis=dict(title='L/D',
                   gridcolor='#1e2d5a', zerolinecolor='#1e2d5a',
                   linecolor='#003080', color=ACAD_GREY),
        legend=dict(bgcolor=CLASS_ROYAL, bordercolor=USAFA_BLUE,
                    font=dict(color=ACAD_WHITE, size=9),
                    x=0.75, y=0.99)
    )

    with st.expander("📊  Performance Charts", expanded=True):
        st.plotly_chart(fig_polar, width='content')
        st.plotly_chart(fig_ld,    width='content')

    span = S / c_ft
    gamma_rad = np.arctan(1 / glide_ratio)
    total_range = h * glide_ratio

    fig2 = go.Figure()

    # ── Aircraft scale — real geometry * visibility factor ────────
    vis = 80.0                        # visibility multiplier
    half_span  = (span / 2) * vis     # ft, scaled to be visible
    chord      = c_ft * vis
    fuse_len   = c_ft * vis * 2
    fuse_rad   = (c_ft * vis) * 0.05
    fuse_h     = h * 0.001
    tail_half  = half_span * 0.35
    tail_chord = chord * 0.4

    # ── Wing ──────────────────────────────────────────────────────
    wing_x = [ 0, -chord, -chord,  0,    0, -chord, -chord,  0]
    wing_y = [ 0,  0,  half_span,  half_span,
               0,  0, -half_span, -half_span]
    wing_z = [h] * 8

    fig2.add_trace(go.Mesh3d(
        x=wing_x, y=wing_y, z=wing_z,
        i=[0, 0, 4, 4], j=[1, 2, 5, 6], k=[2, 3, 6, 7],
        color=ACAD_WHITE, opacity=0.9, flatshading=True,
        name='Wing', showlegend=False
    ))

    # ── Tail ──────────────────────────────────────────────────────
    tail_x = [-fuse_len*0.8, -fuse_len*0.8 - tail_chord,
              -fuse_len*0.8 - tail_chord, -fuse_len*0.8,
              -fuse_len*0.8, -fuse_len*0.8 - tail_chord,
              -fuse_len*0.8 - tail_chord, -fuse_len*0.8]
    tail_y = [ 0,  0,  tail_half,  tail_half,
               0,  0, -tail_half, -tail_half]
    tail_z = [h] * 8

    fig2.add_trace(go.Mesh3d(
        x=tail_x, y=tail_y, z=tail_z,
        i=[0, 0, 4, 4], j=[1, 2, 5, 6], k=[2, 3, 6, 7],
        color=ACAD_WHITE, opacity=0.9, flatshading=True,
        name='Tail', showlegend=False
    ))

    # ── Fuselage ──────────────────────────────────────────────────
    fig2.add_trace(go.Mesh3d(
        x=[ fuse_len*0.2,  fuse_len*0.2,  fuse_len*0.2,  fuse_len*0.2,
           -fuse_len*0.8, -fuse_len*0.8, -fuse_len*0.8, -fuse_len*0.8],
        y=[ fuse_rad, -fuse_rad, -fuse_rad,  fuse_rad,
            fuse_rad, -fuse_rad, -fuse_rad,  fuse_rad],
        z=[ h + fuse_h, h + fuse_h, h - fuse_h, h - fuse_h,
            h + fuse_h, h + fuse_h, h - fuse_h, h - fuse_h],
        alphahull=0, color=CLASS_YELLOW, opacity=0.9,
        name='Fuselage', showlegend=False
    ))

    # ── Glide path ────────────────────────────────────────────────
    fig2.add_trace(go.Scatter3d(
        x=[0, total_range], y=[0, 0], z=[h, 0],
        mode='lines', name='Glide Path',
        line=dict(color=CLASS_RED, width=4)
    ))

    # ── Horizontal reference line ─────────────────────────────────
    fig2.add_trace(go.Scatter3d(
        x=[0, total_range * 0.25], y=[0, 0], z=[h, h],
        mode='lines',
        line=dict(color=ACAD_GREY, width=2, dash='dash'),
        showlegend=False
    ))

    # ── γ label ───────────────────────────────────────────────────
    label_x = total_range * 0.15
    label_z = h - label_x * np.tan(gamma_rad)
    fig2.add_trace(go.Scatter3d(
        x=[label_x], y=[0], z=[label_z],
        mode='text',
        text=[f'γ = {gamma_deg:.1f}°'],
        textfont=dict(color=CLASS_YELLOW, size=13),
        showlegend=False
    ))

    # ── Impact point ──────────────────────────────────────────────
    fig2.add_trace(go.Scatter3d(
        x=[total_range], y=[0], z=[0],
        mode='markers+text',
        marker=dict(size=6, color=CLASS_RED, symbol='cross'),
        text=[f'  R = {total_range/6076:.1f} nm'],
        textfont=dict(color=CLASS_RED, size=10),
        showlegend=False
    ))

    # ── Ground plane ──────────────────────────────────────────────
    gx = np.linspace(0, total_range * 1.05, 10)
    gy = np.linspace(-half_span * 3, half_span * 3, 10)
    gx, gy = np.meshgrid(gx, gy)
    fig2.add_trace(go.Surface(
        x=gx, y=gy, z=np.zeros_like(gx),
        showscale=False, opacity=0.25,
        colorscale=[[0, CLASS_ROYAL], [1, USAFA_BLUE]],
        name='Ground', showlegend=False
    ))

    # ── x-axis tick labels in nm, data in ft ─────────────────────
    n_ticks   = 6
    tick_ft   = np.linspace(0, total_range * 1.05, n_ticks)
    tick_nm   = tick_ft / 6076
    tickvals  = tick_ft.tolist()
    ticktext  = [f'{v:.1f}' for v in tick_nm]

    # ── Layout ────────────────────────────────────────────────────
    fig2.update_layout(
        paper_bgcolor=BG_PRIMARY,
        scene=dict(
            bgcolor=BG_PRIMARY,
            xaxis=dict(
                title='Distance (nm)', color=ACAD_GREY,
                gridcolor='#1e2d5a', backgroundcolor=BG_PRIMARY,
                tickvals=tickvals, ticktext=ticktext
            ),
            yaxis=dict(
                title='Lateral (ft)', color=ACAD_GREY,
                gridcolor='#1e2d5a', backgroundcolor=BG_PRIMARY,
                range=[-half_span * 3, half_span * 3]
            ),
            zaxis=dict(
                title='Altitude (ft)', color=ACAD_GREY,
                gridcolor='#1e2d5a', backgroundcolor=BG_PRIMARY,
                range=[0, h * 1.15]
            ),
            aspectmode='manual',
            aspectratio=dict(x=2.0, y=0.5, z=1.0),
            camera=dict(eye=dict(x=1.4, y=1.4, z=0.7))
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=500
    )
    st.markdown('<div class="eq-label">Glide Distance</div>', unsafe_allow_html=True)
    st.plotly_chart(fig2, width='stretch')
render_perf(S, c_ft, V_knots)

