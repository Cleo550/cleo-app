import streamlit as st
from fpdf import FPDF
import calendar

st.set_page_config(page_title="Cleo Pro")
st.title("🧹 Cleo Pro")

# --- TEXTOS SEGUROS (Cortos para evitar cortes) ---
M_NOM = "Sandra Ramirez Galvez"
M_NIF = "78217908Z"
M_DIR = "Urb. Alkabir Blq 5, pta i"
M_IBAN = "ES44 0182 0143 5202 0163 6882 o Bizum 654 422 330"
T_LEY = "Exenta IVA Art. 20.Uno.22 Ley 37/1992. Directiva UE 2020/285."

clis = {
    "Lola": {"nom": "Maria Dolores Albero Moya", "nif": "21422031S", "dir": "Calle Alcalde Ramon Orts Galan, 7 B52", "tar": 14.0, "leg": True, "d": [2]},
    "Yordhana": {"nom": "Maria de los Angeles Yordhana Gomez Sanchez", "nif": "48361127Q", "dir": "Calle Santiago, 45", "tar": 14.0, "leg": True, "d": [3]},
    "Ania": {"nom": "Ania Rogala", "nif": "---", "dir": "Calle Confrides, 3", "tar": 13.0, "leg": False, "d": [0, 1]}
}

meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
c_sel = st.selectbox("Cliente", list(clis.keys()))
m_sel = st.selectbox("Mes", meses, index=2)

# --- FECHAS ---
m_idx = meses.index(m_sel) + 1
c = clis[c_sel]
cal = calendar.Calendar()
dias = []
for sem in cal.monthdays2calendar(2026, m_idx):
    for d, ds in sem:
        if d != 0 and ds in c["d"]:
            dias.append(f"{d:02d}/{m_idx:02d}")

h_sug = float(len(dias) * 4)
nf = st.text_input("Num", "2026-003") if c["leg"] else "BONO"
h_t = st.number_input("Horas", value=h_sug)

if st.button("GENERAR"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "SERVICIO DE LIMPIEZA", 0, 1, "C")
    
    pdf.set_font("Arial", "", 9)
    pdf.ln(5)
    pdf.cell(95, 5, "EMISOR: " + M_NOM)
    pdf.cell(95, 5, "CLIENTE: " + c["nom"],
