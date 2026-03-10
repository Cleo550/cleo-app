import streamlit as st
from fpdf import FPDF
import calendar

st.title("🧹 Cleo Pro")

# --- DATOS ---
IBAN = "ES44 0182 0143 5202 0163 6882 o Bizum 654 422 330"
ms = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

clis = {
    "Lola": {"nom": "Maria Dolores Albero Moya", "nif": "21422031S", "dir": "Calle Alcalde Ramon Orts Galan, 7 B52", "pob": "03690 Sant Vicent", "tar": 14.0, "leg": True, "d": [2]},
    "Yordhana": {"nom": "Maria de los Angeles Yordhana Gomez Sanchez", "nif": "48361127Q", "dir": "Calle Santiago, 45", "pob": "03690 Sant Vicent", "tar": 14.0, "leg": True, "d": [3]},
    "Ania": {"nom": "Ania Rogala", "nif": "", "dir": "Calle Confrides, 3", "pob": "El Campello", "tar": 13.0, "leg": False, "d": [0, 1]}
}

c_s = st.selectbox("Cliente", list(clis.keys()))
m_s = st.selectbox("Mes", ms, index=2)

# Calcular fechas
m_idx = ms.index(m_s) + 1
cal = calendar.Calendar()
fechas = [f"{d:02d}/{m_idx:02d}" for s in cal.monthdays2calendar(2026, m_idx) for d, ds in s if d != 0 and ds in clis[c_s]["d"]]

h_sug = float(len(fechas) * 4)
nf = st.text_input("N. Factura", "2026-003") if clis[c_s]["leg"] else "BONO"
h_t = st.number_input("Horas Totales", value=h_sug)

if st.button("Generar PDF"):
    c = clis[c_s]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14
