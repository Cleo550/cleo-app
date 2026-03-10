import streamlit as st
from PIL import Image, ImageDraw
import calendar
from datetime import datetime
import io

st.set_page_config(page_title="Cleo Pro", layout="centered")

# --- DATOS CLIENTES ---
CLIS = {
    "Lola": {"n": "Maria Dolores Albero Moya", "f": "21422031S", "d": "Calle Ramon Orts Galan, 7 B52", "p": "03690 San Vicente del Raspeig", "t": 14.0, "h": 4.0, "w": [2], "v": True},
    "Yordhana": {"n": "Maria de los Angeles Yordhana Gomez", "f": "48361127Q", "d": "Calle Santiago, 45", "p": "03690 San Vicente del Raspeig", "t": 14.0, "h": 4.0, "w": [3], "v": True},
    "Ania": {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3", "p": "03560 El Campello", "t": 13.0, "h": 5.0, "w": [0, 1], "v": False}
}

st.title("Gestion de Facturacion Cleo")

cn = st.selectbox("Selecciona Cliente", list(CLIS.keys()))
meses = ["Enero", "
