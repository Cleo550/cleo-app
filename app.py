import streamlit as st
from PIL import Image, ImageDraw
import calendar
from datetime import datetime
import io

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Cleo Pro", layout="centered")

# --- DATOS FIJOS ---
IBAN_C = "ES16 0073 0100 5605 9883 8303 / Bizum 654 422 330"
INFO_E = "Sandra Ramírez Gálvez - 78217908Z\nUrb. Alkabir Blq 5, pta i\n03560 El Campello (Alicante)"

CLIS = {
    "Lola": {"n": "María Dolores Albero Moya", "f": "21422031S", "d": "Calle Ramón Orts Galán, 7 B52", "t": 14.0, "w": [2], "h_d": 4.0},
    "Yordhana": {"n": "María de los Angeles Yordhana Gomez", "f": "48361127Q", "d": "Calle Santiago, 45", "t": 14.0, "w": [3], "h_d": 5.0},
    "Ania": {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3", "t": 13.0, "w": [0, 1], "h_d": 4.0}
}

st.title("✨ Facturación por Adelantado")

# --- MENÚ ---
c_nom = st.selectbox("Cliente", list(CLIS.keys()))
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
m_nom = st.selectbox("Mes de servicio", meses, index=datetime.now().month-1)

c_dat = CLIS[c_nom]
m_idx = meses.index(m_nom) + 1
cal = calendar.Calendar()
# Calcula los días del mes para ese cliente
proximos_dias = [f"{d:02d}-{m_idx:02d}-26" for s in cal.monthdays2calendar(2026, m_idx) for d, ds in s if d!=0 and ds in c_dat["w"]]

# --- SELECCIÓN DE DÍAS ---
st.write("### 📅 ¿Qué días VAS a trabajar?")
dias_finales = []
for fecha in proximos_dias:
    if st.checkbox(f"Voy a trabajar el {fecha}", value=True):
        dias_finales.append(fecha)

h_tot = len(dias_finales) * c_dat["h_d"]
nf = st.text_input("Factura Nº", "2026-002")

# --- GENERAR IMAGEN ---
if st.button("🎨 GENERAR FACTURA AHORA"):
    # Creamos el lienzo (Blanco)
    img = Image.new('RGB', (1200, 1600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 1. Cabecera
    draw.line([(600, 50), (1150, 50)], fill=(0,0,0), width=2)
    draw.text((800, 20), f"FACTURA Nº: {nf}", fill=(0,0,0))
    draw.text((850, 55), f"FECHA: 01/{m_idx:02d}/2026", fill=(0,0,0))

    # 2. Logo Estilo Cleo
    draw.text((520, 150), "Cleo", fill=(0,0,0))
    draw.text((250, 280), "S E R V I C I O   D E   L I M P I E Z A", fill=(50,50,50))
    draw.line([(50, 320), (1150, 320)], fill=(200, 200, 200), width=1)

    # 3. Datos Emisor / Cliente
    pos_y = 400
    draw.text((50, pos_y), "EMISOR", fill=(0,0,0))
    draw.text((50, pos_y+30), INFO_E, fill=(50,50,50))
    
    draw.text((650, pos_y), "CLIENTE", fill=(0,0,0))
    draw.text((650, pos_y+30), f"{c_dat['n']}\nNIF: {c_dat['f']}\n{c_dat['d']}", fill=(50,50,50))

    # 4. Tabla
    y_t = 700
    draw.text((100, y_t), "DESCRIPCIÓN", fill=(0,0,0))
    draw.text((400, y_t), "FECHA", fill=(0,0,0))
    draw.text((620, y_t), "HORAS", fill=(0,0,0))
    draw.text((800, y_t), "PRECIO", fill=(0,0,0))
    draw.text((1000, y_t), "TOTAL", fill=(0,0,0))
    draw.line([(100, y_t+30), (1100, y_t+30)], fill=(0,0,0), width=1)

    y_l = y_t + 50
    for f in dias_finales:
        sub = c_dat["h_d"] * c_dat["t"]
        draw.text((100, y_l), "Servicio limpieza", fill=(80,80,80))
        draw.text((400, y_l), f, fill=(0,0,0))
        draw.text((620, y_l
