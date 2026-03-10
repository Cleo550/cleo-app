import streamlit as st
from fpdf import FPDF
import calendar

st.set_page_config(page_title="Cleo Pro")
st.title("🧹 Cleo Pro")

# --- VARIABLES CORTAS PARA EVITAR CORTES ---
MI_NOM = "Sandra Ramirez Galvez"
MI_NIF = "78217908Z"
MI_DIR = "Urb. Alkabir Blq 5, pta i"
MI_POB = "03560 El Campello"
MI_PAGO = "ES44 0182 0143 5202 0163 6882 o Bizum 654 422 330"
LEY_1 = "Exenta IVA Art. 20.Uno.22 Ley 37/1992."
LEY_2 = "Directiva UE 2020/285."

clis = {
    "Lola": {"nom": "Maria Dolores Albero Moya", "nif": "21422031S", "dir": "Calle Alcalde Ramon Orts Galan, 7 B52", "tar": 14.0, "leg": True, "d": [2]},
    "Yordhana": {"nom": "Maria de los Angeles Yordhana Gomez Sanchez", "nif": "48361127Q", "dir": "Calle Santiago, 45", "tar": 14.0, "leg": True, "d": [3]},
    "Ania": {"nom": "Ania Rogala", "nif": "---", "dir": "Calle Confrides, 3", "tar": 13.0, "leg": False, "d": [0, 1]}
}

meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
c_sel = st.selectbox("Cliente", list(clis.keys()))
m_sel = st.selectbox("Mes", meses, index=2)

# --- CÁLCULO DE FECHAS ---
m_idx = meses.index(m_sel) + 1
c = clis[c_sel]
cal = calendar.Calendar()
dias_trabajo = []
for sem in cal.monthdays2calendar(2026, m_idx):
    for d, ds in sem:
        if d != 0 and ds in c["d"]:
            dias_trabajo.append(f"{d:02d}/{m_idx:02d}")

h_sug = float(len(dias_trabajo) * 4)
n_fact = st.text_input("N. Fact
