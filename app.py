import streamlit as st
from PIL import Image, ImageDraw
import calendar
from datetime import datetime
import io

st.set_page_config(page_title="Cleo Pro", layout="centered")

# --- DATOS MAESTROS ---
IBAN_C = "ES16 0073 0100 5605 9883 8303 / Bizum 654 422 330"
INFO_E = "Sandra Ramírez Gálvez - 78217908Z\nUrb. Alkabir Blq 5, pta i\n03560 El Campello (Alicante)"

CLIS = {
    "Lola": {"n": "María Dolores Albero Moya", "f": "21422031S", "d": "Calle Ramón Orts Galán, 7 B52", "t": 14.0, "w": [2], "h_d": 4.0},
    "Yordhana": {"n": "María de los Angeles Yordhana Gomez", "f": "48361127Q", "d": "Calle Santiago, 45", "t": 14.0, "w": [3], "h_d": 5.0},
    "Ania": {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3", "t": 13.0, "w": [0, 1], "h_d": 4.0}
}

st.title("✨ Facturación por Adelantado")

# --- MENÚ DE SELECCIÓN ---
c_nom = st.selectbox("Cliente", list(CLIS.keys()))
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
m_nom = st.selectbox("Mes de servicio", meses, index=datetime.now().month-1)

c_dat = CLIS
