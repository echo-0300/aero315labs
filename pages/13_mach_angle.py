import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Arc
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.usafa_styles import USAFA_CSS, SIDEBAR_BRAND_HTML, render_sidebar
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Mach Angle — AeroFundamentals",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(USAFA_CSS, unsafe_allow_html=True)

render_sidebar()

# ── Page Header (static) ──────────────────────────────────────────────────────
st.markdown('<div class="page-title">Mach Angle</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Compressibility  &nbsp;·&nbsp;  Supersonic Flow Geometry</div>', unsafe_allow_html=True)

# ── Equations (static) ────────────────────────────────────────────────────────
with st.expander("📖  Governing Equations", expanded=True):
    col_eq1, col_eq2 = st.columns(2)

    with col_eq1:
        st.markdown('<div class="eq-label">Mach Angle (Cone Half-Angle)</div>', unsafe_allow_html=True)
        st.latex(r"\mu = \arcsin\!\left(\frac{1}{M}\right)")
        st.markdown("""
        <div class="explainer">
        The Mach angle <em>μ</em> defines the half-angle of the Mach cone — the boundary between
        the zone of action (where the aircraft's presence is felt) and the zone of silence.
        At <em>M</em> = 1, μ = 90°. As <em>M</em> → ∞, μ → 0°.
        </div>
        """, unsafe_allow_html=True)

    with col_eq2:
        st.markdown('<div class="eq-label">Mach Number &amp; Speed of Sound</div>', unsafe_allow_html=True)
        st.latex(r"M = \frac{V}{a} \qquad a = \sqrt{\gamma R T}")
        st.markdown("""
        <div class="explainer">
        <em>V</em> = flow velocity, <em>a</em> = local speed of sound,
        <em>γ</em> = 1.4 (air), <em>R</em> = 287 J/(kg·K).
        The speed of sound depends only on temperature —
        not on pressure or density directly.
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Controls (outside fragments — drives state) ───────────────────────────────
ctrl_col, gap_col, badge_col = st.columns([2, 0.15, 1])

with ctrl_col:
    st.markdown("**Mach Number**")
    mach = st.slider(
        label="mach_slider",
        min_value=1.01, max_value=5.0,
        value=2.0, step=0.01,
        format="M = %.2f",
        label_visibility="collapsed",
        key="mach"
    )

with badge_col:
    if mach < 1.2:
        regime, r_color = "TRANSONIC",  "#A6192E"
    elif mach < 4.99:
        regime, r_color = "SUPERSONIC", "#FFC72C"
    else:
        regime, r_color = "HYPERSONIC", "#00BED6"

    st.markdown(
        f"<div style='font-family:\"Barlow Condensed\",\"Trebuchet MS\",sans-serif;"
        f"font-size:0.8rem;font-weight:700;letter-spacing:0.15em;"
        f"padding:0.3rem 0.9rem;border-radius:3px;"
        f"border:1px solid {r_color};color:{r_color};"
        f"display:inline-block;margin-top:1.6rem;text-transform:uppercase;'>"
        f"{regime}</div>",
        unsafe_allow_html=True
    )

# ── Fragment: Metrics ─────────────────────────────────────────────────────────
@st.fragment
def render_metrics(mach: float) -> None:
    mu_rad    = np.arcsin(1.0 / mach)
    mu_deg    = np.degrees(mu_rad)
    shock_deg = 90.0 - mu_deg

    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="metric-label">Mach Number</div>
                <div class="metric-value">{mach:.2f}</div>
            </div>
            <div class="metric-card accent-yellow">
                <div class="metric-label">Mach Angle &mu;</div>
                <div class="metric-value yellow">{mu_deg:.1f}&deg;</div>
            </div>
            <div class="metric-card accent-red">
                <div class="metric-label">Cone Half-Angle</div>
                <div class="metric-value red">{mu_deg:.1f}&deg;</div>
            </div>
            <div class="metric-card accent-grotto">
                <div class="metric-label">Shock from Flow Axis</div>
                <div class="metric-value blue">{shock_deg:.1f}&deg;</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

render_metrics(mach)

# ── Fragment: Visualization ───────────────────────────────────────────────────
@st.fragment
def render_visualization(mach: float) -> None:
    mu_rad = np.arcsin(1.0 / mach)
    mu_deg = np.degrees(mu_rad)

    # USAFA brand colors for Matplotlib
    USAFA_BLUE   = "#003594"
    CLASS_ROYAL  = "#002554"
    CLASS_YELLOW = "#FFC72C"
    CLASS_RED    = "#A6192E"
    GROTTO       = "#00BED6"
    ACAD_GREY    = "#B2B4B2"
    BG           = "#001433"

    fig, ax = plt.subplots(figsize=(12, 5.5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    # Grid — subtle Class Royal tone
    for x in np.arange(-8, 6, 1):
        ax.axvline(x, color="#002554", linewidth=0.4, alpha=0.6)
    for y in np.arange(-4, 5, 1):
        ax.axhline(y, color="#002554", linewidth=0.4, alpha=0.6)

    nose_x      = 3.0
    body_length = 4.5

    img = mpimg.imread("assets\sr71.png")

# Positioning (tweak these)
    img_extent = [
        nose_x - body_length-1,  # left
        nose_x - 0.1,          # right
        -1.45,                  # bottom
        1.45                    # top
    ]

    ax.imshow(img, extent=img_extent, zorder=5)

    # Mach cone filled region 
    line_len = 11.0
    dx = line_len * np.cos(mu_rad)
    dy = line_len * np.sin(mu_rad)

    cone_patch = plt.Polygon(
        [[nose_x, 0], [nose_x - dx, dy], [nose_x - dx, -dy]],
        closed=True, facecolor=USAFA_BLUE, alpha=0.10,
        edgecolor='none', zorder=2
    )
    ax.add_patch(cone_patch)

    # Shock lines — Class Yellow
    for sign in (1, -1):
        ax.plot(
            [nose_x, nose_x - dx], [0, sign * dy],
            color=CLASS_YELLOW, linewidth=2.0, linestyle='--',
            alpha=0.95, zorder=6,
            label=(f'μ = {mu_deg:.1f}°' if sign == 1 else None)
        )

    # Angle arc — Class Red
    arc = Arc(
        (nose_x, 0), width=3.4, height=3.4,
        angle=180, theta1=-mu_deg, theta2=mu_deg,
        color=CLASS_RED, linewidth=1.8, zorder=7
    )
    ax.add_patch(arc)

    # μ annotation
    label_angle = np.radians(180 - mu_deg * 0.5)
    ax.text(
        nose_x + 1.7 * np.cos(label_angle),
        1.7 * np.sin(label_angle),
        f'μ = {mu_deg:.0f}°',
        color=CLASS_RED, fontsize=9.5,
        fontfamily='monospace', ha='center', va='center',
        fontweight='bold', zorder=8
    )

    # Freestream arrow
    ax.annotate(
        '', xy=(nose_x + 0.3, 0), xytext=(nose_x + 2.8, 0),
        arrowprops=dict(arrowstyle='->', color=GROTTO, lw=2.0, mutation_scale=16),
        zorder=7
    )
    ax.text(nose_x + 1.6, 0.28, f'M = {mach:.2f}',
            color=GROTTO, fontsize=9.5, fontfamily='monospace',
            ha='center', fontweight='bold', zorder=8)

    # Zone labels 
    x_pos = nose_x + 0.1
    y_pos = dy / 4.0

    ax.text(
        x_pos, -y_pos,
        'ZONE OF SILENCE',
        color=ACAD_GREY,
        fontsize=7.5,
        fontfamily='monospace',
        ha='center',
        va='center',
        alpha=0.6,
    )

    ax.text(
        x_pos, y_pos,
        'ZONE OF SILENCE',
        color=ACAD_GREY,
        fontsize=7.5,
        fontfamily='monospace',
        ha='center',
        va='center',
        alpha=0.6,
    )
    ax.text(nose_x - 7, 0, 'ZONE OF\nACTION',
            color=CLASS_YELLOW, fontsize=10, fontfamily='monospace',
            ha='center', va='center', alpha=0.8)

    ax.set_xlim(-8, 5.5)
    ax.set_ylim(-4, 4)
    ax.axis('off')

    ax.legend(
        loc='lower left', facecolor=CLASS_ROYAL,
        edgecolor=USAFA_BLUE, labelcolor='white',
        fontsize=9, framealpha=0.95
    )

    plt.tight_layout(pad=0.4)
    st.pyplot(fig, width='stretch')
    plt.close(fig)

render_visualization(mach)

# ── Static explainer (never re-renders) ──────────────────────────────────────
st.divider()
with st.expander("💡  Physical Interpretation"):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        **Zone of Silence vs. Zone of Action**

        At supersonic speeds, pressure disturbances from the aircraft cannot propagate
        upstream. The Mach cone boundary separates the *zone of action* or inside the cone,
        where the aircraft's presence is felt, from the *zone of silence* outside,
        where the flow is completely undisturbed upstream of the disturbance.
        """)
    with c2:
        st.markdown("""
        **Physical Intuition**

        - At **M = 1.0**, μ = 90° — the "cone" is a normal bow shock, detached from the nose.
        - As **M → ∞**, μ → 0° — the cone collapses to the flight path axis.
        - The Mach cone is the origin point for the mach waves emitted along the flight path;
                     each mach wave travels at *a* while the aircraft advances at *V = Ma*.
        """)
