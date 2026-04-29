# utils/usafa_styles.py
# Official USAFA brand CSS — sourced from usafa.edu/brand/
# Colors: usafa.edu/brand/brand-colors/
# Typography: usafa.edu/brand/typography/
#
# Primary palette:
#   Academy Blue  #003594  (Pantone 661 C)
#   Class Royal   #002554  (Pantone 655 C)
#   Academy Grey  #B2B4B2  (Pantone 421 C)
#   White         #FFFFFF
#
# Secondary palette:
#   Class Red     #A6192E  (Pantone 187 C)
#   Class Yellow  #FFC72C  (Pantone 123 C)
#
# Emblem accent (Grotto Blue used sparingly for data/interactive elements):
#   Grotto Blue   #00BED6
#
# Typography:
#   Headings  → Cera (licensed; approximated with Barlow Condensed via Google Fonts)
#   Body      → Ideal Sans (licensed; approximated with Source Sans 3 via Google Fonts)
#   Fallback  → Trebuchet MS (USAFA-approved web-safe alternative)

USAFA_CSS = """
<style>
    /* ── USAFA Brand Fonts ─────────────────────────────────────────
       Cera (headings) → Barlow Condensed as closest open-source match
       Ideal Sans (body) → Source Sans 3 as closest open-source match
       Trebuchet MS retained as USAFA-approved fallback per brand guide
    ──────────────────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Source+Sans+3:wght@300;400;600&display=swap');

    /* ── USAFA Brand Color Variables ──────────────────────────────
       Mapped directly from usafa.edu/brand/brand-colors/
    ──────────────────────────────────────────────────────────────── */
    :root {
        /* Primary */
        --usafa-blue:    #003594;   /* Academy Blue  — Pantone 661 C */
        --class-royal:   #002554;   /* Class Royal   — Pantone 655 C */
        --academy-grey:  #B2B4B2;   /* Academy Grey  — Pantone 421 C */
        --academy-white: #FFFFFF;

        /* Secondary */
        --class-red:     #A6192E;   /* Class Red     — Pantone 187 C */
        --class-yellow:  #FFC72C;   /* Class Yellow  — Pantone 123 C */

        /* Emblem accent — Grotto Blue (used for interactive/data elements) */
        --grotto-blue:   #00BED6;

        /* Derived UI tones — dark versions of brand blues for backgrounds */
        --bg-primary:    #001433;   /* deep navy derived from Class Royal */
        --bg-secondary:  #001d47;   /* slightly lighter for sidebar        */
        --bg-card:       #002060;   /* card surface                        */
        --border:        #003080;   /* subtle border                       */
        --text-primary:  #E8EBF4;   /* near-white on dark navy             */
        --text-muted:    #8899CC;   /* muted blue-grey                     */
    }

    /* ── Global ─────────────────────────────────────────────────── */
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-family: 'Source Sans 3', 'Trebuchet MS', sans-serif;
    }

    /* ── Sidebar ─────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: var(--bg-secondary);
        border-right: 3px solid var(--usafa-blue);
    }

    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        font-family: 'Barlow Condensed', 'Trebuchet MS', sans-serif;
        color: var(--class-yellow);
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.2em;
        text-transform: uppercase;
    }

    /* ── Page title block ────────────────────────────────────────── */
    .page-title {
        font-family: 'Barlow Condensed', 'Trebuchet MS', sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        color: var(--academy-white);
        letter-spacing: 0.04em;
        text-transform: uppercase;
        line-height: 1;
        margin-bottom: 0.2rem;
    }

    .page-subtitle {
        font-family: 'Barlow Condensed', 'Trebuchet MS', sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--class-yellow);
        letter-spacing: 0.25em;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }

    /* ── Accent rule (Academy Blue left-border) ──────────────────── */
    .eq-box {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-left: 4px solid var(--usafa-blue);
        border-radius: 4px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }

    .eq-label {
        font-family: 'Barlow Condensed', 'Trebuchet MS', sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        color: var(--class-yellow);
        letter-spacing: 0.2em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    /* ── Metric cards ────────────────────────────────────────────── */
    .metric-row {
        display: flex;
        gap: 0.75rem;
        margin: 1rem 0;
    }

    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-top: 3px solid var(--usafa-blue);
        border-radius: 4px;
        padding: 1rem 1.25rem;
        flex: 1;
        text-align: center;
    }

    .metric-card.accent-red    { border-top-color: var(--class-red);    }
    .metric-card.accent-yellow { border-top-color: var(--class-yellow); }
    .metric-card.accent-grotto { border-top-color: var(--grotto-blue);  }

    .metric-label {
        font-family: 'Barlow Condensed', 'Trebuchet MS', sans-serif;
        font-size: 0.65rem;
        font-weight: 700;
        color: var(--text-muted);
        letter-spacing: 0.2em;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }

    .metric-value {
        font-family: 'Barlow Condensed', 'Trebuchet MS', sans-serif;
        font-size: 1.6rem;
        font-weight: 800;
        color: var(--academy-white);
        letter-spacing: 0.02em;
    }

    .metric-value.blue   { color: var(--grotto-blue);  }
    .metric-value.red    { color: var(--class-red);    }
    .metric-value.yellow { color: var(--class-yellow); }

    /* ── Hero / home card ────────────────────────────────────────── */
    .hero-container {
        background: linear-gradient(135deg, var(--class-royal) 0%, var(--bg-card) 100%);
        border: 1px solid var(--border);
        border-left: 6px solid var(--class-yellow);
        border-radius: 4px;
        padding: 2.5rem 3rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }

    /* Subtle grid texture overlay */
    .hero-container::before {
        content: '';
        position: absolute;
        inset: 0;
        background:
            repeating-linear-gradient(0deg,   transparent, transparent 48px,
                rgba(255,255,255,0.03) 48px, rgba(255,255,255,0.03) 49px),
            repeating-linear-gradient(90deg,  transparent, transparent 48px,
                rgba(255,255,255,0.03) 48px, rgba(255,255,255,0.03) 49px);
        pointer-events: none;
    }

    .hero-title {
        font-family: 'Barlow Condensed', 'Trebuchet MS', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: var(--academy-white);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 0 0 0.3rem 0;
        line-height: 1;
    }

    .hero-subtitle {
        font-family: 'Barlow Condensed', 'Trebuchet MS', sans-serif;
        font-size: 0.85rem;
        font-weight: 700;
        color: var(--class-yellow);
        letter-spacing: 0.3em;
        text-transform: uppercase;
        margin-bottom: 1.25rem;
    }

    .hero-description {
        font-family: 'Source Sans 3', 'Trebuchet MS', sans-serif;
        font-size: 1rem;
        color: var(--text-primary);
        line-height: 1.75;
        max-width: 680px;
        font-weight: 300;
    }

    /* ── Lab cards ───────────────────────────────────────────────── */
    .lab-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 1rem;
        margin-top: 1.25rem;
    }

    .lab-card {
        height: 100%;
        min-height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .lab-card.red    { border-top-color: var(--class-red);    }
    .lab-card.yellow { border-top-color: var(--class-yellow); }
    .lab-card.grotto { border-top-color: var(--grotto-blue);  }

    .lab-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.25);
    }

    .lab-card-icon  {
        font-size: 1.6rem;
        margin-bottom: 0.6rem;
    }

    .lab-card-title {
        font-family: 'Barlow Condensed', 'Trebuchet MS', sans-serif;
        font-size: 0.85rem;
        font-weight: 700;
        color: var(--class-yellow);
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }

    .lab-card.red    .lab-card-title { color: var(--class-red);   }
    .lab-card.grotto .lab-card-title { color: var(--grotto-blue); }

    .lab-card-desc {
        font-family: 'Source Sans 3', 'Trebuchet MS', sans-serif;
        font-size: 0.875rem;
        color: var(--text-muted);
        line-height: 1.6;
        font-weight: 300;
    }

    /* ── Section divider label ───────────────────────────────────── */
    .section-header {
        font-family: 'Barlow Condensed', 'Trebuchet MS', sans-serif;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.3em;
        text-transform: uppercase;
        color: var(--text-muted);
        border-bottom: 1px solid var(--border);
        padding-bottom: 0.4rem;
        margin: 1.75rem 0 1rem 0;
    }

    /* ── Info callout ─────────────────────────────────────────────── */
    .info-callout {
        background: rgba(0, 53, 148, 0.12);
        border: 1px solid rgba(0, 53, 148, 0.4);
        border-left: 3px solid var(--usafa-blue);
        border-radius: 4px;
        padding: 0.9rem 1.1rem;
        font-family: 'Source Sans 3', 'Trebuchet MS', sans-serif;
        font-size: 0.875rem;
        color: var(--text-primary);
        margin-top: 1.75rem;
    }

    /* ── Regime / flight-phase badge ─────────────────────────────── */
    .regime-badge {
        display: inline-block;
        font-family: 'Barlow Condensed', 'Trebuchet MS', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        padding: 0.25rem 0.7rem;
        border-radius: 3px;
        text-transform: uppercase;
        border: 1px solid;
    }

    /* ── Body copy / explainer text ──────────────────────────────── */
    .explainer {
        font-family: 'Source Sans 3', 'Trebuchet MS', sans-serif;
        font-size: 0.9rem;
        color: var(--text-muted);
        line-height: 1.75;
        font-weight: 300;
        margin-top: 0.6rem;
    }

    /* ── Streamlit component overrides ──────────────────────────── */
    .stSlider [data-baseweb="slider"] { padding: 0.5rem 0; }

    h1, h2, h3 {
        font-family: 'Barlow Condensed', 'Trebuchet MS', sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* Expander header */
    [data-testid="stExpander"] summary {
        font-family: 'Barlow Condensed', 'Trebuchet MS', sans-serif;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: var(--text-primary);
    }
</style>
"""

# ── Sidebar HTML (shared across all pages) ────────────────────────────────────
SIDEBAR_BRAND_HTML = """
<div style='padding: 1rem 0 1.5rem 0; border-bottom: 1px solid #003080; margin-bottom: 1rem;'>
    <div style='font-family: "Barlow Condensed", "Trebuchet MS", sans-serif;
                font-size: 0.8rem; font-weight: 700; letter-spacing: 0.3em;
                color: #B2B4B2; text-transform: uppercase; margin-bottom: 0.15rem;'>
        U.S. Air Force Academy
    </div>
    <div style='font-family: "Barlow Condensed", "Trebuchet MS", sans-serif;
                font-size: 1.3rem; font-weight: 800; letter-spacing: 0.06em;
                color: #FFFFFF; text-transform: uppercase; line-height: 1;'>
        DFAN AERO315
    </div>
    <div style='font-family: "Barlow Condensed", "Trebuchet MS", sans-serif;
                font-size: 0.65rem; font-weight: 600; letter-spacing: 0.2em;
                color: #FFC72C; text-transform: uppercase; margin-top: 0.2rem;'>
        Virtual Labs
    </div>
</div>
"""

def render_sidebar() -> None:
    import streamlit as st
    with st.sidebar:
        st.markdown(SIDEBAR_BRAND_HTML, unsafe_allow_html=True)
        st.markdown("### Navigation")
        st.page_link("app.py",                            label="🏠  Home")
        st.divider()
        st.markdown("### Pressure & Atmosphere")
        st.page_link("pages/01_perfect_gas_law.py",       label="💨  Perfect Gas Law")
        st.page_link("pages/02_manometry.py",             label="🧪  Manometry")
        st.page_link("pages/03_standard_atmosphere.py",   label="🌡️  Standard Day Atmosphere")
        st.divider()
        st.markdown("### Fluid Flow")
        st.page_link("pages/04_continuity.py",            label="➡️  Continuity")
        st.page_link("pages/05_stream_tube.py",           label="💧  Stream Tube")
        st.page_link("pages/06_bernoulli.py",             label="🧔🏼  Bernoulli Equation")
        st.divider()
        st.markdown("### Aircraft Pressure Measurement")
        st.page_link("pages/07_pitot_static.py",          label="💨  Pitot-Static & Dynamic Pressure")
        st.page_link("pages/08_altimetry.py",             label="🧭  Altimeter & Pressure Setting")
        st.page_link("pages/09_icetg.py",                 label="🧊  ICeT-G Airspeeds")
        st.divider()
        st.markdown("### Airfoils")
        st.page_link("pages/10_boundary_layer.py",        label="🍰  Boundary Layer")
        st.page_link("pages/11_airfoils.py",              label="🪽  2-D Airfoils")
        st.page_link("pages/12_3d_wing_lift.py",          label="✈️  3-D Wing Lift")
        st.divider()
        st.markdown("### Compressibility")
        st.page_link("pages/13_mach_angle.py",            label="📐  Mach Angle")
        st.page_link("pages/14_mach_wave.py",             label="⭕  Mach Wave")
        st.divider()
        st.markdown("### Performance")
        st.page_link("pages/15_glide.py",                 label="🍂  Glides")
        st.page_link("pages/16_climb.py",                 label="🗻  Climbs")
        st.page_link("pages/17_turns.py",                 label="🛞  Turns")
        st.divider()
        st.markdown("### Stability")
        st.page_link("pages/18_longitudinal_stability.py",label="⚖️  Longitudinal Stability")
        st.page_link("pages/19_lateral_directional.py",   label="🎯  Lateral-Direction Stability")
        st.page_link("pages/20_dynamic_instability.py",   label="🧨  Dynamic Instability")
        st.markdown(
            "<div style='font-family:\"Barlow Condensed\",\"Trebuchet MS\",sans-serif;"
            "font-size:0.65rem;color:#B2B4B2;letter-spacing:0.1em;margin-top:1rem;'>"
            "v0.1.2 &nbsp;·&nbsp; AY2025-2026</div>",
            unsafe_allow_html=True
        )

# ── USAFA Brand Colors ────────────────────────────────────────────────────────
USAFA_BLUE   = "#003594"
CLASS_ROYAL  = "#002554"
CLASS_YELLOW = "#FFC72C"
CLASS_RED    = "#A6192E"
GROTTO_BLUE  = "#00BED6"
ACAD_GREY    = "#B2B4B2"
ACAD_WHITE   = "#FFFFFF"
BG_PRIMARY   = "#001433"
BG_SECONDARY = "#001d47"
BG_CARD      = "#002060"