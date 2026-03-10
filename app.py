import streamlit as st
from PIL import Image, ImageDraw
import calendar
from datetime import datetime
import io

st.set_page_config(page_title="Cleo Pro", layout="centered")

# --- DATOS ---
IBAN_C = "ES16 0073 0100 5605 9883 8303 / Bizum 654 422 330"
INFO_E = "Sandra Ramírez Gálvez - 78217908Z\nUrb. Alkabir Blq 5, pta i\n03560 El Campello (Alicante)"

CLIS = {
    "Lola": {"n": "María Dolores Albero Moya", "f": "21422031S", "d": "Calle Ramón Orts Galán, 7 B52", "t": 14.0, "w": [2], "h_d": 4.0},
    "Yordhana": {"n": "María de los Angeles Yordhana Gomez", "f": "48361127Q", "d": "Calle Santiago, 45", "t": 14.0, "w": [3], "h_d": 5.0},
    "Ania": {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3", "t": 13.0, "w": [0, 1], "h_d": 4.0}
}

st.title("✨ Facturación Cleo")

# --- SELECCIÓN ---
c_nom = st.selectbox("Cliente", list(CLIS.keys()))
mss = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
m_nom = st.selectbox("Mes de servicio", mss, index=datetime.now().month-1)

c_dat = CLIS[c_nom]
m_idx = mss.index(m_nom) + 1
cal = calendar.Calendar()
dias_mes = [f"{d:02d}-{m_idx:02d}-2026" for s in cal.monthdays2calendar(2026, m_idx) for d, ds in s if d!=0 and ds in c_dat["w"]]

st.write("### 📅 ¿Qué días VAS a trabajar?")
dias_finales = []
for fecha in dias_mes:
    if st.checkbox(f"Trabajaré el {fecha}", value=True):
        dias_finales.append(fecha)

h_tot = len(dias_finales) * c_dat["h_d"]
nf = st.text_input("Factura Nº", "2026-003")

# --- GENERAR FACTURA ---
if st.button("🎨 GENERAR FACTURA AHORA"):
    img = Image.new('RGB', (1200, 1600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 1. Cabecera
    draw.line([(600, 50), (1150, 50)], fill=(0,0,0), width=2)
    draw.text((800, 20), f"FACTURA Nº: {nf}", fill=(0,0,0))
    draw.text((850, 55), f"FECHA: 01/{m_idx:02d}/2026", fill=(0,0,0))

    # 2. Logo
    draw.text((520, 150), "Cleo", fill=(0,0,0))
    draw.text((250, 280), "S E R V I C I O   D E   L I M P I E Z A", fill=(50,50,50))
    draw.line([(50, 320), (1150, 320)], fill=(200, 200, 200), width=1)

    # 3. Datos
    y_p = 400
    draw.text((50, y_p), "EMISOR", fill=(0,0,0))
    draw.text((50, y_p+30), INFO_E, fill=(50,50,50))
    draw.text((650, y_p), "CLIENTE", fill=(0,0,0))
    draw.text((650, y_p+30), f"{c_dat['n']}\nNIF: {c_dat['f']}\n{c_dat['d']}", fill=(50,50,50))

    # 4. Tabla
    y_t = 700
    draw.text((100, y_t), "DESCRIPCIÓN      FECHA      HORAS    PRECIO    TOTAL", fill=(0,0,0))
    draw.line([(100, y_t+30), (1100, y_t+30)], fill=(0,0,0), width=1)

    y_l = y_t + 50
    for f in dias_finales:
        sub = c_dat["h_d"] * c_dat["t"]
        draw.text((100, y_l), "Servicio limpieza", fill=(80,80,80))
        draw.text((400, y_l), f, fill=(0,0,0))
        draw.text((620, y_l), f"{c_dat['h_d']}", fill=(0,0,0))
        draw.text((800, y_l), f"{c_dat['t']}e", fill=(0,0,0))
        draw.text((1000, y_l), f"{sub:.2f}e", fill=(0,0,0))
        y_l += 40

    # 5. Totales
    y_l += 40
    total = h_tot * c_dat["t"]
    draw.text((800, y_l), f"BASE TOTAL: {total:.2f}e", fill=(0,0,0))
    draw.text((800, y_l+30), "IVA (Exento): 0,00e", fill=(0,0,0))
    draw.line([(800, y_l+65), (1100, y_l+65)], fill=(0,0,0), width=2)
    draw.text((800, y_l+75), f"TOTAL: {total:.2f}e", fill=(0,0,0))

    # 6. Pie
    y_f = 1150
    draw.text((100, y_f), f"PAGO: {IBAN_C}", fill=(0,0,0))
    nota = "NOTA: Pago tipo Bono por adelantado."
    draw.text((100, y_f+60), nota, fill=(80,80,80))
    ley = "Exenta IVA Art. 20.Uno.22 Ley 37/1992"
    draw.text((400, y_f+180), ley, fill=(130,130,130))

    # Botón Descarga
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue())
    st.download_button("📥 DESCARGAR FACTURA", buf.getvalue(), f"Factura_{c_nom}_{m_nom}.png")
