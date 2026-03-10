import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import calendar
import io

st.set_page_config(page_title="Cleo Pro")
st.title("🧹 Generador de Factura (Imagen)")

# --- DATOS ---
IBAN = "ES44 0182 0143 5202 0163 6882 o Bizum 654 422 330"
LEY = "Exenta IVA Art. 20.Uno.22 Ley 37/1992. Directiva UE 2020/285."

CLIS = {
    "Lola": {"n": "Maria Dolores Albero Moya", "f": "21422031S", "d": "Calle Alcalde Ramon Orts Galan, 7 B52", "t": 14.0, "w": [2]},
    "Yordhana": {"n": "Maria de los Angeles Yordhana Gomez Sanchez", "f": "48361127Q", "d": "Calle Santiago, 45", "t": 14.0, "w": [3]},
    "Ania": {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3", "t": 13.0, "w": [0, 1]}
}

# --- MENU ---
C_S = st.selectbox("Cliente", list(CLIS.keys()))
MSS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
M_S = st.selectbox("Mes", MSS, index=2)

# --- CALCULO AUTOMATICO ---
M_I = MSS.index(M_S) + 1
C = CLIS[C_S]
CAL = calendar.Calendar()
DIAS = [f"{d:02d}/{M_I:02d}" for s in CAL.monthdays2calendar(2026, M_I) for d, ds in s if d != 0 and ds in C["w"]]

col1, col2 = st.columns(2)
with col1:
    HT = st.number_input("Horas", value=float(len(DIAS)*4))
with col2:
    NF = st.text_input("N. Factura", "2026-003")

if st.button("CREAR IMAGEN DE FACTURA"):
    # Crear lienzo (Blanco, tamaño A4 aprox)
    img = Image.new('RGB', (800, 1000), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Dibujar diseño
    draw.rectangle([0, 0, 800, 100], fill=(240, 240, 240)) # Franja arriba
    draw.text((50, 40), "FACTURA DE SERVICIOS", fill=(0,0,0))
    
    # Bloque Datos
    draw.text((50, 120), "EMISOR:\nSandra Ramirez Galvez\n78217908Z\nEl Campello, Alicante", fill=(0,0,0))
    draw.text((450, 120), f"CLIENTE:\n{C['n']}\nNIF: {C['f']}\n{C['d']}", fill=(0,0,0))
    
    # Datos Factura
    draw.text((50, 240), f"Factura N: {NF}      Fecha: 01/{M_I:02d}/2026", fill=(0,0,0))
    
    # Tabla
    y = 300
    draw.line([(50, y), (750, y)], fill=(0,0,0), width=2)
    draw.text((50, y+10), "CONCEPTO             FECHAS           H      PRECIO      TOTAL", fill=(0,0,0))
    draw.line([(50, y+40), (750, y+40)], fill=(0,0,0), width=1)
    
    y += 50
    h_dia = HT / len(DIAS) if DIAS else 0
    for f in DIAS:
        t_l = h
