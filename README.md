# AeroFundamentals Lab

Interactive aerodynamics simulation suite built with Streamlit.

## Setup

```bash
pip install -r requirements.txt
```

## Run locally

```bash
streamlit run app.py
```

## Project Structure

```
aero_demos/
├── app.py                       # Home page / main menu
├── pages/
│   ├── 01_mach_angle.py         # Mach cone & oblique shock geometry
│   ├── 02_pitot_static.py       # Pitot-static & dynamic pressure (placeholder)
│   ├── 03_standard_atmosphere.py# ISA standard atmosphere (placeholder)
│   └── 04_altimetry.py          # Altimeter & Kollsman window (placeholder)
├── requirements.txt
└── README.md
```

## Fragment Pattern

Each interactive page uses `@st.fragment` to scope re-renders:
- **Controls** (sliders, inputs) live outside fragments — they trigger state updates
- **Metrics fragment** — redraws only the numeric readouts
- **Visualization fragment** — redraws only the Matplotlib/Plotly figure
- **Equations & explainers** — fully static, never re-render


