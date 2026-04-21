import streamlit as st
from utils.usafa_styles import USAFA_CSS, render_sidebar
st.markdown(USAFA_CSS, unsafe_allow_html=True)
render_sidebar()
st.set_page_config(page_title="Glide - Virtual Lab", page_icon="🍂", layout="wide")

st.markdown("<h1 style='font-family:monospace;color:#ff6b2b;'>Glide Performance</h1>", unsafe_allow_html=True)
st.info("🚧  This lab is under construction. Check back soon.")
