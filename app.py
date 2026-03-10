import streamlit as st
from fpdf import FPDF
from datetime import datetime
import calendar
import io

# --- DATOS FISCALES ---
NOMBRE_EMISOR = "Sandra Ramirez Galvez"
NIF_EMISOR = "78217908Z"
DIR_EMISOR = "Urb. Alkabir Blq 5, pta i, El Campello"
POB_EMISOR = "03560 El Campello"

st.set_page_config(page_title="Cleo Pro", layout="centered")

clientes = {
    "Lola": {"nombre": "Maria Dolores Albero Moya", "nif": "21422031S", "dir": "Calle Alcalde Ramon Orts Galan, 7 B52", "pob": "03690 Sant Vicent", "tarifa": 14.0, "legal": True, "dias": [2]},
    "Yordhana": {"nombre": "Maria de los Angeles Yordhana Gomez Sanchez", "nif": "48361127Q", "dir": "Calle Santiago, 45", "pob": "03690 Sant Vicent", "tarifa": 14.0, "legal": True, "dias": [3]},
    "Ania": {"nombre": "Ania Rogala", "nif": "", "dir": "Calle Confrides, 3", "pob": "El Campello", "tarifa": 13.0, "legal": False, "dias": [0, 1]}
}

def contar_dias(año, mes, dias_obj):
    cal = calendar.Calendar()
    return sum(1 for semana in cal.monthdays2calendar(año, mes) for dia, d_sem in semana if dia != 0 and d_sem in dias_obj)

def generar_pdf(cli_k, n_f, h, m_n, año):
    c = clientes[cli_k]
    pdf = FPDF()
    pdf.add_page()
    try: pdf.image('logo.jpeg', 85, 10, 40)
    except: pass
    pdf.set_font('Arial', 'B', 14)
    pdf.set_y(45)
    pdf.cell(0, 10, 'SERVICIO DE LIMPIEZA', 0, 1, 'C')
    pdf.set_font('Arial', '', 10)
    pdf.set_xy(110, 15)
    m_i = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Jun
