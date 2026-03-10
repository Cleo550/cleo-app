import streamlit as st
from fpdf import FPDF
import calendar

st.set_page_config(page_title="Cleo Pro")
st.title("🧹 Cleo Facturación")

# --- CONFIGURACION ---
IBAN = "ES44 0182 0143 5202 0163 6882 o Bizum 654 422 330"
LEY1 = "Operacion exenta de IVA segun Art. 20.Uno.22 Ley 37/1992"
LEY2 = "y acogida al Regimen de Franquicia de IVA (Directiva UE 2020/285)"

CLIS = {
    "Lola": {"n": "Maria Dolores Albero Moya", "f": "21422031S", "d": "Calle Alcalde Ramon Orts Galan, 7 B52", "t": 14.0, "l": True, "w": [2]},
    "Yordhana": {"n": "Maria de los Angeles Yordhana Gomez Sanchez", "f": "48361127Q", "d": "Calle Santiago, 45", "t": 14.0, "l": True, "w": [3]},
    "Ania": {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3", "t": 13.0, "l": False, "w": [0, 1]}
}

MSS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
C_S = st.selectbox("Elegir Cliente", list(CLIS.keys()))
M_S = st.selectbox("Elegir Mes", MSS, index=2)

# --- CALCULO FECHAS ---
M_I = MSS.index(M_S) + 1
C = CLIS[C_S]
CAL = calendar.Calendar()
DIAS = [f"{d:02d}/{M_I:02d}" for s in CAL.monthdays2calendar(2026, M_I) for d, ds in s if d != 0 and ds in C["w"]]

H_SUG = float(len(DIAS) * 4)
NF = st.text_input("N. Factura", "2026-003") if C["l"] else "BONO"
HT = st.number_input("Horas Totales", value=H_SUG)

if st.button("GENERAR PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "SERVICIO DE LIMPIEZA", 0, 1, "C")
    
    pdf.set_font("Arial", "", 9); pdf.ln(5)
    pdf.cell(95, 5, "EMISOR: Sandra Ramirez Galvez"); pdf.cell(95, 5, "CLIENTE: " + C["n"], 0, 1)
    pdf.cell(95, 5, "NIF: 78217908Z"); pdf.cell(95, 5, "NIF: " + C["f"], 0, 1)
    pdf.cell(95, 5, "Urb. Alkabir Blq 5, pta i"); pdf.cell(95, 5, "Dir: " + C["d"], 0, 1)
    
    pdf.ln(10); pdf.set_font("Arial", "B", 8)
    pdf.cell(60, 7, "CONCEPTO", 1); pdf.cell(25, 7, "FECHA", 1); pdf.cell(20, 7, "H", 1); pdf.cell(30, 7, "EUR/H", 1); pdf.cell(35, 7, "TOTAL", 1, 1)
    
    pdf.set_font("Arial", "", 8)
    HD = HT / len(DIAS) if DIAS else 0
    for f in DIAS:
        pdf.cell(60, 6, "Limpieza domicilio " + M_S, 1)
        pdf.cell(25, 6, f, 1, 0, "C")
        pdf.cell(20, 6, str(round(HD, 1)), 1, 0, "C")
        pdf.cell(30, 6, str(C["t"]) + " E", 1, 0, "C")
        pdf.cell(35, 6, str(round(HD * C["t"], 2)) + " E", 1, 1, "C")
    
    TOT = HT * C["t"]; pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(135, 10, "TOTAL NETO A PAGAR:", 0, 0, "R")
    pdf.cell(35, 10, str(round(TOT, 2)) + " E", 1, 1, "C")
    
    if C["l"]:
        pdf.ln(2); pdf.set_font("Arial", "I", 7)
        pdf.multi_cell(0, 4, LEY1 + " " + LEY2)
    
    pdf.ln(5); pdf.set_font("Arial", "B", 9)
    P = "FORMA DE PAGO: " + IBAN if C["l"] else "FORMA DE PAGO: En Efectivo"
    pdf.cell(0, 5, P, 0, 1)
    pdf.set_font("Arial", "I", 8); pdf.cell(0, 5, "NOTA: Pago tipo bono por adelantado.", 0, 1)
    
    RES = pdf.output(dest="S").encode("latin-1")
    st.download_button("📥 DESCARGAR FACTURA", RES, "factura_" + C_S + ".pdf")
