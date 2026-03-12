import streamlit as st
from PIL import Image

st.set_page_config(page_title="Cleo Pro", layout="centered")

try:
    logo = Image.open("logo.jpeg")
    st.image(logo, use_container_width=True)
except:
    st.title("Cleo Pro")
