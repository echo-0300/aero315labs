import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

st.set_page_config(page_title="Manometry - Virtual Lab", page_icon="🧪", layout="wide")
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()

st.markdown('<div class="page-title">Perfect Gas Law</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Gas Properties</div>', unsafe_allow_html=True)

#Equations (static/expander)
with st.expander("📖  Governing Equations", expanded=True):
    col_eq1, col_eq2 = st.columns(2)

    with col_eq1:
        st.markdown('<div class="eq-label">Manometry Equation</div>', unsafe_allow_html=True)
        st.latex(r"\frac{P_1-P_2}{\rho g}=h_1-h_2")
        st.markdown("""
        <div class="explainer">
        The manometry equation relates the pressures in two sealed vessels to the height difference
        between a the two ends of a column of fluid suspended between the two. 
        </div>
        """, unsafe_allow_html=True)

    with col_eq2:
        st.markdown('<div class="eq-label">Equation Constants</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="explainer">
        This equation relies on the constant fluid density of the column and the constant
        acceleration due to gravity. For this lab the constants are:
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"\rho_{water}=1.94 \frac{slug}{ft^3}")
        st.latex(r"g = 32.2 \frac{ft}{s^2}")

st.divider()
p1_col, gap_col, p2_col = st.columns([.6, 0.15, 0.6])

with p1_col:
    st.markdown("Pressure 1")
    p1_slide = st.slider(
        label="p1_slide",
        min_value = 2000.00,
        max_value = 2300.00,
        value = 2116.22,
        step = 0.01,
        format = f"Pressure 1 = %.2f psf",
        label_visibility="collapsed",
        key="param"
    )

with p2_col:
    st.markdown("Pressure 1")
    p2_slide = st.slider(
        label="p2_slide",
        min_value = 2000.00,
        max_value = 2300.00,
        value = 2116.22,
        step = 0.01,
        format = f"Pressure 2 = %.2f psf",
        label_visibility="collapsed",
        key="param2"
    )

@st.fragment
def render_calcs(p1_slide: float, p2_slide: float) -> None:
    h_0 = 3.00
    rho = 1.94
    g = 32.2
    delta_h = (p1_slide - p2_slide) / rho / g
    h_1 = h_0 - 0.5 * delta_h
    h_2 = h_0 + 0.5 * delta_h

    # ── Layout constants ──────────────────────────────────────────
    tube_bottom = 0.0      # y-coordinate of U-tube base
    tube_top    = 7.0      # max visible height of columns
    col_width   = 0.4      # width of each column
    left_x      = 0.5      # left edge of left column
    right_x     = 2.0      # left edge of right column
    wall_t      = 0.05     # tube wall thickness

    USAFA_BLUE   = "#003594"
    CLASS_ROYAL  = "#002554"
    CLASS_YELLOW = "#FFC72C"
    FLUID_COLOR  = "#00BED6"
    WALL_COLOR   = "#B2B4B2"
    BG           = "#001433"

    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    # ── Draw tube walls (left column, base, right column) ─────────
    # Left column walls
    ax.add_patch(mpatches.Rectangle(
        (left_x - wall_t, tube_bottom), wall_t, tube_top,
        color=WALL_COLOR, zorder=3))
    ax.add_patch(mpatches.Rectangle(
        (left_x + col_width, tube_bottom), wall_t, tube_top,
        color=WALL_COLOR, zorder=3))
    # Right column walls
    ax.add_patch(mpatches.Rectangle(
        (right_x - wall_t, tube_bottom), wall_t, tube_top,
        color=WALL_COLOR, zorder=3))
    ax.add_patch(mpatches.Rectangle(
        (right_x + col_width, tube_bottom), wall_t, tube_top,
        color=WALL_COLOR, zorder=3))
    # Base connecting the two columns
    ax.add_patch(mpatches.Rectangle(
        (left_x, tube_bottom - wall_t),
        (right_x + col_width) - left_x, wall_t,
        color=WALL_COLOR, zorder=3))

    # ── Fluid fill ────────────────────────────────────────────────
    # Left column fluid
    ax.add_patch(mpatches.Rectangle(
        (left_x, tube_bottom), col_width, h_1,
        color=FLUID_COLOR, alpha=0.7, zorder=2))
    # Right column fluid
    ax.add_patch(mpatches.Rectangle(
        (right_x, tube_bottom), col_width, h_2,
        color=FLUID_COLOR, alpha=0.7, zorder=2))
    # Base fluid (always full)
    ax.add_patch(mpatches.Rectangle(
        (left_x + col_width, tube_bottom),
        right_x - (left_x + col_width), h_0 * 0.5,
        color=FLUID_COLOR, alpha=0.7, zorder=2))

    # ── Fluid surface lines ───────────────────────────────────────
    ax.hlines(h_1, left_x, left_x + col_width,
              color=CLASS_YELLOW, linewidth=1.5, zorder=4)
    ax.hlines(h_2, right_x, right_x + col_width,
              color=CLASS_YELLOW, linewidth=1.5, zorder=4)

    # ── Height labels ─────────────────────────────────────────────
    label_x_left  = left_x - 0.35
    label_x_right = right_x + col_width + 0.15

    ax.text(label_x_left, h_1, f'h₁ = {h_1:.3f} ft',
            color=CLASS_YELLOW, fontsize=9, fontfamily='monospace',
            va='center', ha='right', zorder=5)
    ax.text(label_x_right, h_2, f'h₂ = {h_2:.3f} ft',
            color=CLASS_YELLOW, fontsize=9, fontfamily='monospace',
            va='center', ha='left', zorder=5)

    # ── Δh annotation ─────────────────────────────────────────────
    mid_x = left_x + col_width + 0.1
    ax.annotate('', xy=(mid_x, h_2), xytext=(mid_x, h_1),
                arrowprops=dict(arrowstyle='<->', color=CLASS_YELLOW,
                                lw=1.2, mutation_scale=10), zorder=5)
    ax.text(mid_x + 0.08, (h_1 + h_2) / 2, f'Δh = {abs(delta_h):.3f} ft',
            color=CLASS_YELLOW, fontsize=8, fontfamily='monospace',
            va='center', ha='left', zorder=5)

    # ── P1 / P2 labels at column tops ─────────────────────────────
    ax.text(left_x + col_width / 2, tube_top + 0.15, 'P₁',
            color=CLASS_YELLOW, fontsize=11, fontfamily='monospace',
            ha='center', fontweight='bold', zorder=5)
    ax.text(right_x + col_width / 2, tube_top + 0.15, 'P₂',
            color=CLASS_YELLOW, fontsize=11, fontfamily='monospace',
            ha='center', fontweight='bold', zorder=5)

    ax.set_xlim(0, 3.5)
    ax.set_ylim(-0.3, tube_top + 0.4)
    ax.axis('off')
    plt.tight_layout(pad=0.4)
    st.pyplot(fig, width='stretch')
    plt.close(fig)

render_calcs(p1_slide, p2_slide)