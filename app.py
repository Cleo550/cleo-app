import streamlit as st
from PIL import Image, ImageDraw
import calendar
from datetime import datetime
import io

st.set_page_config(page_title="Cleo Pro", layout="centered")

# --- CONFIGURACIÓN DE CLIENTES ---
CLIS = {
    "Lola": {
        "n": "María Dolores Albero Moya", "f": "21422031S", 
        "d": "Calle Ramón Orts Galán, 7 B52", "p": "03690 San Vicente del Raspeig",
        "t": 14.0, "w": [2], "h_d": 4.0, "tipo": "Factura"
    },
    "Yordhana": {
        "n": "María de los Angeles Yordhana Gomez", "f": "48361127Q", 
        "d": "Calle Santiago, 45", "p": "03690 San Vicente del Raspeig",
        "t": 14.0, "w": [3], "h_d": 5.0, "tipo": "Factura"
    },
    "Ania": {
        "n": "Ania Rogala", "f": "---", 
        "d": "Calle Confrides, 3", "p": "03560 El Campello",
        "t": 13.0, "w": [0, 1], "h_d": 4.0, "tipo": "Bono"
    }
}

st.title("🧹 Gestión Cleo: Facturas y Bonos")

# --- INTERFAZ ---
c_nom = st.selectbox("Selecciona Cliente", list(CLIS.keys()))
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
m_nom = st.selectbox("Mes de servicio", meses, index=datetime.now().month-1)

c_dat = CLIS[c_nom]
m_idx = meses.index(m_nom) + 1
cal = calendar.Calendar()
dias_mes = [f"{d:02d}-{m_idx:02d}-2026" for s in cal.monthdays2calendar(2026, m_idx) if d!=0 for d, ds in s if d!=0 and ds
