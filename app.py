import streamlit as st
from PIL import Image, ImageDraw
import calendar
import io

st.set_page_config(page_title="Cleo Pro")
st.title("🧹 Generador de Factura (Imagen)")

# --- DATOS ---
MI_IBAN = "ES44 0182 0143 5202 0163 6882 o Bizum 654 422 330"
MI_LEY = "Exenta IVA Art. 20.Uno.22 Ley 37/1992. Directiva UE 2020/285."

CLIS = {
    "Lola": {"n": "Maria Dolores Albero Moya", "f": "21422031S", "d": "Calle Alcalde Ramon Orts Galan, 7 B52", "t": 14.0, "w": [2]},
    "Yordhana": {"n": "Maria de los Angeles Yordhana Gomez Sanchez", "f": "48361127Q", "d": "Calle Santiago, 45", "t": 14.0, "w": [3]},
    "Ania": {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3", "t": 13.0, "w": [0, 1]}
}

# --- SELECCIÓN ---
C_SEL = st.selectbox("Cliente", list(CLIS.keys()))
MSS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
M_SEL = st.selectbox("Mes", MSS, index=2)

# --- CÁLCULO AUTO ---
M_IDX = MSS.index(M_SEL) + 1
CLI = CLIS[C_SEL]
CAL = calendar.Calendar()
FECHAS = [f"{d:02d}/{M_IDX:02d}" for s in CAL.monthdays2calendar(2026, M_IDX) for d, ds in s if d != 0 and ds in CLI["w"]]

col1, col2 = st.columns(2)
with col1:
    H_TOT = st.number_input("Horas", value=float(len(FECHAS)*4))
with col2:
    N_FAC = st.text_input("N. Factura", "2026-003")

if st.button("CREAR IMAGEN DE FACTURA"):
    # Crear imagen blanca
    img = Image.new('RGB', (800, 1100), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Diseño de la factura (Cabecera gris)
    draw.rectangle([0, 0, 800, 80], fill=(230, 230, 230))
    draw.text((50, 30), "FACTURA / RECIBO DE SERVICIOS", fill=(0,0,0))
    
    # Datos Emisor y Cliente
    draw.text((50, 110), f"EMISOR:\nSandra Ramirez Galvez\n78217908Z\nEl Campello, Alicante", fill=(0,0,0))
    draw.text((450, 110), f"CLIENTE:\n{CLI['n']}\nNIF: {CLI['f']}\n{CLI['d']}", fill=(0,0,0))
    
    draw.text((50, 220), f"Factura N: {N_FAC}      Fecha Emision: 01/{M_IDX:02d}/2026", fill=(0,0,0))
    
    # Tabla de servicios
    y = 280
    draw.line([(50, y), (750, y)], fill
