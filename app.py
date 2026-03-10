import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import calendar
from datetime import datetime
import io

st.set_page_config(page_title="Cleo Pro", layout="centered")

# --- DATOS MAESTROS ---
IBAN = "ES44 0182 0143 5202 0163 6882 o Bizum 654 422 330"
DATOS_CLEO = "Sandra Ramirez Galvez - 78217908Z\nUrb. Alkabir Blq 5, pta i\n03560 El Campello (Alicante)"

CLIS = {
    "Lola": {"nom": "Maria Dolores Albero Moya", "nif": "21422031S", "dir": "Calle Alcalde Ramon Orts Galan, 7 B52", "tar": 14.0, "dias": [2], "leg": True},
    "Yordhana": {"nom": "Maria de los Angeles Yordhana Gomez Sanchez", "nif": "48361127Q", "dir": "Calle Santiago, 45", "tar": 14.0, "dias": [3], "leg": True},
    "Ania": {"nom": "Ania Rogala", "nif": "---", "dir": "Calle Confrides, 3", "tar": 13.0, "dias": [0, 1], "leg": False}
}

st.title("🧹 Generador de Recibos Cleo")

# --- SELECCIÓN ---
c_nom = st.selectbox("Cliente", list(CLIS.keys()))
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
m_nom = st.selectbox("Mes", meses, index=datetime.now().month-1)

# --- CÁLCULO AUTOMÁTICO ---
m_idx = meses.index(m_nom) + 1
c_data = CLIS[c_nom]
cal = calendar.Calendar()
# Detecta los días del mes según el cliente (0=Lun, 1=Mar, 2=Mie, etc.)
fechas_mes = [f"{d:02d}/{m_idx:02d}" for s in cal.monthdays2calendar(2026, m_idx) for d, ds in s if d != 0 and ds in c_data["dias"]]

st.info(f"Detectados {len(fechas_mes)} días de trabajo en {m_nom}")

# --- ENTRADAS DE USUARIO ---
col1, col2 = st.columns(2)
with col1:
    h_auto = float(len(fechas_mes) * 4)
    h_final = st.number_input("Horas Totales", value=h_auto)
with col2:
    if c_data["leg"]:
        n_fact = st.text_input("Número de Factura", value="2026-003")
    else:
        n_fact = "RECIBO-BONO"

if st.button("CREAR IMAGEN PARA WHATSAPP"):
    # Crear lienzo blanco
    img = Image.new('RGB', (800, 1000), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Textos principales
    d.text((50, 40), "FACTURA / RECIBO", fill=(0,0,0))
    d.text((50
