# AeroFundamentals Lab

Interactive aerodynamics simulation suite built with Streamlit as an extension and modernization of Dr. Steven Brandt's Virtual Lab files.
This was created by Maj Matthew Thompson with reference to Introduction to Aeronautics - A Design Perspective, the Virtual Labs' and various 
LLMs to assist in coding/debuging. 

v0.1.2

## Setup

```bash
pip install -r requirements.txt
```
Line 35 of Airfoils.py in the Airfoils lib requires updating due to scipy modernization:
from scipy.differentiate import derivative

## Run locally

```bash
streamlit run app.py
```

## Project Structure

```
labs/
├── app.py                       # Home page / main menu
├── pages/
├── requirements.txt
└── README.md
```

## Fragment Pattern

Each interactive page uses `@st.fragment` to scope re-renders:
- **Controls** (sliders, inputs) live outside fragments — they trigger state updates
- **Metrics fragment** — redraws only the numeric readouts
- **Visualization fragment** — redraws only the Matplotlib/Plotly figure
- **Equations & explainers** — fully static, never re-render


