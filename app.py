import streamlit as st
from fpdf import FPDF
from datetime import datetime
import calendar
import io

# --- DATOS FISCALES ---
NOM_E = "Sandra Ramirez Galvez"
NIF_E = "78217908Z"
DIR_E = "Urb. Alkabir Blq 5, pta i, El Campello"
POB_E = "03560 El Campello"

st.set_page_config(page_title="Cleo Pro", layout="centered")

# 0=Lunes, 1=Martes, 2=Miérc, 3=Juev
CLIS = {
    "Lola": {"nom": "Maria Dolores Albero Moya", "nif": "21422031S", "dir": "Calle Alcalde Ramon Orts Galan, 7 B52", "pob": "03690 Sant Vicent", "tari": 14.0, "leg": True, "d": [2]},
    "Yordhana": {"nom": "Maria de los Angeles Yordhana Gomez Sanchez", "nif": "48361127Q", "dir": "Calle Santiago, 45", "pob": "03690 Sant Vicent", "tari": 14.0, "leg": True, "d": [3]},
    "Ania": {"nom": "Ania Rogala", "nif": "", "dir": "Calle Confrides, 3", "pob": "El Campello", "tari": 13.0, "leg": False, "d": [0, 1]}
}

def contar(a, m, d_o):
    c = calendar.Calendar()
    return sum(1 for sem in c.monthdays2calendar(a, m) for d, ds in sem if d != 0 and ds in d_o)

def PDF_GEN(ck, nf, h, mn, a):
    c = CLIS[ck]
    pdf = FPDF()
    pdf.add_page()
    try: pdf.image('logo.jpeg', 85, 10, 40)
    except: pass
    pdf.set_font('Arial', 'B', 14); pdf.set_y(45); pdf.cell(0, 10, 'SERVICIO DE LIMPIEZA', 0, 1, 'C')
    pdf.set_font('Arial', '', 10); pdf.set_xy(110, 15)
    ms = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mi = ms.index(mn) + 1; fd = f"01/{mi:02d}/{a}"
    if c["leg"]:
        pdf.cell(50, 8, f'FACTURA N: {nf}', 1, 0, 'C'); pdf.cell(40, 8, f'FECHA: {fd}', 1, 1, 'C')
    else:
        pdf.cell(90, 8, f'FECHA: {fd}', 1, 1, 'C')
    pdf.set_y(65); pdf.set_font('Arial', 'B', 9)
    pdf.cell(95, 5, 'EMISOR', 0, 0); pdf.cell(95, 5, 'CLIENTE', 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.cell(95, 5, f'Nombre: {NOM_E}', 0, 0); pdf.cell(95, 5, f'Nombre: {c["nom"]}', 0, 1)
    pdf.cell(95, 5, f'NIF: {NIF_E}', 0, 0); pdf.cell(95, 5, f'NIF: {c["nif"]}', 0, 1)
    pdf.cell(95, 5, f'Dir: {DIR_E}', 0, 0); pdf.cell(95, 5, f'Dir: {c["dir"]}', 0, 1)
    pdf.cell(95, 5, f'Pob: {POB_E}', 0, 0); pdf.cell(95, 5, f'Pob: {c["pob"]}', 0, 1)
    pdf.ln(10); pdf.set_font('Arial', 'B', 10)
    pdf.cell(80, 8, 'DESCRIPCION', 1, 0, 'C'); pdf.cell(25, 8, 'HORAS', 1, 0, 'C'); pdf.cell(40, 8, 'PRECIO/H', 1, 0, 'C'); pdf.cell(45, 8, 'TOTAL', 1, 1, 'C')
    tb = h * c["tari"]; pdf.set_font('Arial', '', 10)
    pdf.cell(80, 8, f'Limpieza {mn}', 1); pdf.cell(25, 8, f"{h:.1f}", 1, 0, 'C'); pdf.cell(40, 8, f'{c["tari"]:.2f} E', 1, 0, 'C'); pdf.cell(45, 8, f'{tb:.2f} E', 1, 1, 'C')
    pdf.ln(5)
    if c["leg"]:
        ret = tb * 0.20; pdf.cell(145, 8, 'Retencion IRPF (20%)', 0, 0, 'R'); pdf.cell(45, 8, f'-{ret:.2f} E', 1, 1, 'C')
        pdf.set_font('Arial', 'B', 11); pdf.cell(145, 10, 'TOTAL A PERCIBIR', 0, 0, 'R'); pdf.cell(45, 10, f'{tb-ret:.2f} E', 1, 1, 'C')
    else:
        pdf.set_font('Arial', 'B', 11); pdf.cell(145, 10, 'TOTAL NETO', 0, 0, 'R'); pdf.cell(45, 10, f'{tb:.2f} E', 1, 1, 'C')
    pdf.ln(10); pdf.set_font('Arial', 'I', 8); pdf.multi_cell(0, 5, 'NOTA: Pago tipo Bono por adelantado.')
    return pdf.output(dest='S').
