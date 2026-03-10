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
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "SERVICIO DE LIMPIEZA", 0, 1, "C")
    
    pdf.set_font("Arial", "", 9)
    pdf.ln(5)
    pdf.cell(95, 5, "EMISOR: Sandra Ramirez Galvez", 0, 0)
    pdf.cell(95, 5, f"CLIENTE: {c['nom']}", 0, 1)
    pdf.cell(95, 5, "NIF: 78217908Z", 0, 0)
    pdf.cell(95, 5, f"NIF: {c['nif']}", 0, 1)
    pdf.cell(95, 5, "Urb. Alkabir Blq 5, pta i, El Campello", 0, 0)
    pdf.cell(95, 5, f"Dir: {c['dir']}", 0, 1)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 8)
    pdf.cell(60, 7, "CONCEPTO", 1); pdf.cell(30, 7, "FECHA", 1); pdf.cell(25, 7, "HORAS", 1); pdf.cell(35, 7, "PRECIO", 1); pdf.cell(35, 7, "TOTAL", 1, 1)
    
    pdf.set_font("Arial", "", 8)
    h_d = h_t / len(fechas) if fechas else 0
    for f in fechas:
        pdf.cell(60, 6, f"Limpieza {m_s}", 1)
        pdf.cell(30, 6, f, 1)
        pdf.cell(25, 6, f"{h_d:.1f}", 1)
        pdf.cell(35, 6, f"{c['tar']:.2f} E", 1)
        pdf.cell(35, 6, f"{h_d*c['tar']:.2f} E", 1, 1)
    
    tot = h_t * c["tar"]
    pdf.ln(5)
    if c["leg"]:
        irpf = tot * 0.20
        pdf.cell(150, 7, "BASE TOTAL:", 0, 0, "R"); pdf.cell(35, 7, f"{tot:.2f} E", 1, 1)
        pdf.cell(150, 7, "IVA (Exento):", 0, 0, "R"); pdf.cell(35, 7, "0.00 E", 1, 1)
        pdf.cell(150, 7, "TOTAL (IRPF 20%):", 0, 0, "R"); pdf.cell(35, 7, f"{tot-irpf:.2f} E", 1, 1)
        pdf.ln(2)
        pdf.set_font("Arial", "I", 7)
        pdf.multi_cell(0, 4, "Exenta IVA Art. 20.Uno.22 Ley 37/1992. Directiva UE 2020/285.")
    else:
        pdf.cell(150, 10, "TOTAL NETO:", 0, 0, "R"); pdf.cell(35, 10, f"{tot:.2f} E", 1, 1)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 9)
    pago = f"PAGO: {IBAN}" if c["leg"] else "PAGO: En Efectivo"
    pdf.cell(0, 5, pago, 0, 1)
    
    out = pdf.output(dest='S').encode('latin-1')
    st.download_button("📥 Descargar Factura", out, "factura.pdf")
