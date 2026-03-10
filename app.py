import streamlit as st
from fpdf import FPDF
from datetime import datetime
import calendar

st.set_page_config(page_title="Cleo Pro")

# --- DATOS FIJOS ---
IBAN = "ES44 0182 0143 5202 0163 6882 o Bizum 654 422 330"
LEY = "Operacion exenta de IVA segun Art. 20.Uno.22 Ley 37/1992"
LEY2 = "y acogida al Regimen de Franquicia de IVA (Directiva UE 2020/285)"

CLIS = {
    "Lola": {"nom": "Maria Dolores Albero Moya", "nif": "21422031S", "dir": "Calle Alcalde Ramon Orts Galan, 7 B52", "pob": "03690 Sant Vicent", "tari": 14.0, "leg": True, "d": [2]},
    "Yordhana": {"nom": "Maria de los Angeles Yordhana Gomez Sanchez", "nif": "48361127Q", "dir": "Calle Santiago, 45", "pob": "03690 Sant Vicent", "tari": 14.0, "leg": True, "d": [3]},
    "Ania": {"nom": "Ania Rogala", "nif": "", "dir": "Calle Confrides, 3", "pob": "El Campello", "tari": 13.0, "leg": False, "d": [0, 1]}
}

def obtener_fechas(a, m, d_o):
    c = calendar.Calendar()
    return [f"{d:02d}/{m:02d}" for s in c.monthdays2calendar(a, m) for d, ds in s if d != 0 and ds in d_o]

def PDF_GEN(ck, nf, h_total, mn, a):
    c, pdf = CLIS[ck], FPDF()
    pdf.add_page()
    try: pdf.image('logo.jpeg', 85, 10, 40)
    except: pass
    
    pdf.set_font('Arial', 'B', 14); pdf.set_y(45)
    pdf.cell(0, 10, 'SERVICIO DE LIMPIEZA', 0, 1, 'C')
    
    pdf.set_font('Arial', '', 10); pdf.set_xy(110, 15)
    ms = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    m_i = ms.index(mn)+1; fd = f"01/{m_i:02d}/{a}"
    
    if c["leg"]:
        pdf.cell(50, 8, f'FACTURA N: {nf}', 1, 0, 'C')
        pdf.cell(40, 8, f'FECHA: {fd}', 1, 1, 'C')
    else:
        pdf.cell(90, 8, f'FECHA: {fd
