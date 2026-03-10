import streamlit as st
from fpdf import FPDF
import calendar

st.set_page_config(page_title="Cleo Pro")
st.title("🧹 Cleo Pro")

# --- DATOS FIJOS ---
M_NOM = "Sandra Ramirez Galvez"
M_NIF = "78217908Z"
M_DIR = "Urb. Alkabir Blq 5, pta i"
M_BAN = "ES44 0182 0143 5202 0163 6882 o Bizum 654 422 330"
M_LEY = "Operacion exenta de IVA segun Art. 20.Uno.22 Ley 37/1992"
M_LEY2 = "y acogida al Regimen de Franquicia de IVA (Directiva UE 2020/285)"

CLIS = {
    "Lola": {"n": "Maria Dolores Albero Moya", "f": "21422031S", "d": "Calle Alcalde Ramon Orts Galan, 7 B52", "t": 14.0, "l": True, "w": [2]},
    "Yordhana": {"n": "Maria de los Angeles Yordhana Gomez Sanchez", "f": "48361127Q", "d": "Calle Santiago, 45", "t": 14.0, "l": True, "w": [3]},
    "Ania": {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3", "t": 13.0, "l": False, "w": [0, 1]}
}

MSS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
C_S = st.selectbox("Cli", list(CLIS.keys()))
M_S = st.selectbox("Mes", MSS, index=2)

# --- FECHAS ---
M_I = MSS.index(M_S) + 1
C = CLIS[C_S]
CAL = calendar.Calendar()
DIAS = [f"{d:02d}/{M_I:02d}" for s in CAL.monthdays2calendar(2026, M_I) for d, ds in s if d != 0 and ds in C["w"]]

H_SUG = float(len(DIAS) * 4)
NF = st.text_input("Fact", "2026-003") if C["l"] else "BONO"
HT = st.number_input("Horas", value=H_SUG)

if st.button("GENERAR"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "SERVICIO DE LIMPIEZA", 0, 1, "C")
    
    pdf.set_font("Arial", "", 9)
    pdf.ln(5)
    # Datos Emisor
    pdf.cell(95, 5, "EMISOR:")
    pdf.cell(95, 5, "CLIENTE:", 0, 1)
    pdf.cell(95, 5, M_NOM)
    pdf.cell(95, 5, C["n"], 0, 1)
    pdf.cell(95, 5, "NIF: " + M_NIF)
    pdf.cell(95, 5, "NIF: " + C["f"], 0, 1)
    pdf.cell(95, 5, M_DIR)
    pdf.cell(95, 5, "Dir: " + C["d"], 0, 1)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 8)
    # Cabecera Tabla
    pdf.cell(60, 7, "CONCEPTO", 1)
    pdf.cell(25, 7, "FECHA", 1)
    pdf.cell(20, 7, "H", 1)
    pdf.cell(35, 7, "EUR/H", 1)
    pdf.cell(35, 7, "TOTAL", 1, 1)
    
    pdf.set_font("Arial", "", 8)
    HD = HT / len(DIAS) if DIAS else 0
    for f in DIAS:
        pdf.cell(60, 6, "Limpieza " + M_S, 1)
        pdf.cell(25, 6, f, 1)
        pdf.cell(20, 6, str(round(HD, 1)), 1)
        pdf.cell(35, 6, str(C["t"]) + " E", 1)
        pdf.cell(35, 6, str(round(HD * C["t"], 2)) + " E", 1, 1)
    
    TOT = HT * C["t"]
    pdf.ln(5)
    if C["l"]:
        RET = TOT * 0.20
        pdf.set_font("Arial", "B", 9)
        pdf.cell(140, 7, "BASE:", 0, 0, "R")
        pdf.cell(35, 7, str(round(TOT, 2)) + " E", 1, 1)
        pdf.cell(140, 7, "IVA (Exento):", 0, 0, "R")
        pdf.cell(35, 7, "0,00 E", 1, 1)
        pdf.cell(140, 7, "NETO (IRPF 20%):", 0, 0, "R")
        pdf.cell(35, 7, str(round(TOT - RET, 2)) + " E", 1, 1)
        pdf.ln(3)
        pdf.set_font("Arial", "I", 7)
        pdf.multi_cell(0, 4, M_LEY + " " + M_LEY2)
    else:
        pdf.set_font("Arial", "B", 10)
        pdf.cell(140, 10, "TOTAL NETO:", 0, 0, "R")
