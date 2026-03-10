import streamlit as st
import calendar
from datetime import datetime

st.set_page_config(page_title="Cleo Pro")
st.title("🧹 Cleo: Facturación Automática")

# --- DATOS ---
IBAN = "ES44 0182 0143 5202 0163 6882 o Bizum 654 422 330"
MI_INFO = "Sandra Ramirez Galvez - 78217908Z\nUrb. Alkabir Blq 5, pta i, El Campello"

CLIS = {
    "Lola": {"n": "Maria Dolores Albero Moya", "f": "21422031S", "d": "Calle Alcalde Ramon Orts Galan, 7 B52", "t": 14.0, "w": [2], "l": True},
    "Yordhana": {"n": "Maria de los Angeles Yordhana Gomez Sanchez", "f": "48361127Q", "d": "Calle Santiago, 45", "t": 14.0, "w": [3], "l": True},
    "Ania": {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3", "t": 13.0, "w": [0, 1], "l": False}
}

# --- SELECCIÓN ---
c_nom = st.selectbox("Cliente", list(CLIS.keys()))
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
m_nom = st.selectbox("Mes", meses, index=datetime.now().month-1)

# --- CÁLCULO AUTO ---
m_idx = meses.index(m_nom) + 1
c = CLIS[c_nom]
cal = calendar.Calendar()
fechas = [f"{d:02d}/{m_idx:02d}" for s in cal.monthdays2calendar(2026, m_idx) for d, ds in s if d != 0 and ds in c["w"]]

st.success(f"Días detectados: {len(fechas)}")

col1, col2 = st.columns(2)
with col1:
    h_tot = st.number_input("Horas Totales", value=float(len(fechas)*4))
with col2:
    n_fac = st.text_input("N. Factura", "2026-003") if c["l"] else "BONO"

# --- VISTA PREVIA ---
total = h_tot * c["t"]
recibo_texto = f"""
FACTURA / RECIBO: {n_fac}
FECHA: 01/{m_idx:02d}/2026
--------------------------------------
EMISOR: {MI_INFO}
CLIENTE: {c['n']}
NIF: {c['f']}
--------------------------------------
CONCEPTO: Limpieza domicilio {m_nom}
DÍAS TRABAJADOS: {', '.join(fechas)}
HORAS TOTALES: {h_tot}h
PRECIO/HORA: {c['t']}€
--------------------------------------
TOTAL NETO: {total:.2f}€
--------------------------------------
PAGO: {IBAN if c_nom != 'Ania' else 'En Efectivo'}
Exenta IVA Art. 20.Uno.22 Ley 37/1992
"""

st.text_area("Vista previa para copiar", recibo_texto, height=400)

# --- BOTÓN WHATSAPP ---
t_wa = f"Hola! Te envío el recibo de {m_nom}. Total: {total:.2f}e. Detalle: {n_fac}"
url_wa = f"https://wa.me/?text={t_wa.replace(' ', '%20')}"

if st.button("Enviar por WhatsApp"):
    st.markdown(f'<a href="{url_wa}" target="_blank">📲 Abrir WhatsApp y enviar</a>', unsafe_allow_html=True)
    st.info("Copia el texto del cuadro de arriba y pégalo en el chat.")
