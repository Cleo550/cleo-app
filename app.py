import streamlit as st
from PIL import Image, ImageDraw
import calendar
from datetime import datetime
import io

st.set_page_config(page_title="Cleo Pro", layout="centered")

# --- DATOS CLIENTES ---
CLIS = {
    "Lola": {"n": "María Dolores Albero Moya", "f": "21422031S", "d": "Calle Ramón Orts Galán, 7 B52", "p": "03690 San Vicente del Raspeig", "t": 14.0, "w": [2], "h": 4.0, "v": True},
    "Yordhana": {"n": "María de los Angeles Yordhana Gomez", "f": "48361127Q", "d": "Calle Santiago, 45", "p": "03690 San Vicente del Raspeig", "t": 14.0, "w": [3], "h": 5.0, "v": True},
    "Ania": {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3", "p": "03560 El Campello", "t": 13.0, "w": [0, 1], "h": 4.0, "v": False}
}

st.title("🧹 Gestión Cleo")

# --- INTERFAZ ---
cn = st.selectbox("Cliente", list(CLIS.keys()))
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
mn = st.selectbox("Mes", meses, index=datetime.now().month-1)

c = CLIS[cn]
mi = meses.index(mn) + 1
cal = calendar.Calendar()
d_lista = [f"{d:02d}-{mi:02d}-2026" for s in cal.monthdays2calendar(2026, mi) for d, ds in s if d != 0 and ds in c["w"]]

st.write("### 📅 ¿Qué días VAS a trabajar?")
df = [f for f in d_lista if st.checkbox(f"Trabajaré el {f}", value=True)]

ht = len(df) * c["h"]
nf = st.text_input("Factura Nº", f"2026-00{mi}") if c["v"] else ""

# --- GENERAR IMAGEN ---
if st.button("🚀 GENERAR DOCUMENTO"):
    img = Image.new('RGB', (1200, 1600), "white")
    draw = ImageDraw.Draw(img)
    
    try:
        lg = Image.open("logo.jpeg")
        lg.thumbnail((400, 200))
        img.paste(lg, (400, 50))
    except:
        draw.text((500, 100), "[Logo logo.jpeg no encontrado]", fill="red")

    # Cabecera
    tit = f"FACTURA Nº: {nf}" if c["v"] else "BONO MENSUAL"
    draw.text((850, 50), tit, fill="black")
    draw.text((850, 80), f"FECHA: 01/{mi:02d}/2026", fill="black")

    # Bloques Info
    draw.text((70, 400), "EMISOR\nSandra Ramírez Gálvez\n78217908Z\nUrb. Alkabir Blq 5, pta i\n03560 El Campello", fill="black")
    draw.text((650, 400), f"CLIENTE\n{c['n']}\nNIF: {c['f']}\n{c['d']}\n{c['p']}", fill="black")

    # Tabla (Columnas alineadas)
    y = 700
    draw.rectangle([70, y, 1130, y+40], fill=(240, 240, 240))
    draw.text((80, y+10), "DESCRIPCIÓN", "black")
    draw.text((420, y+10), "FECHA", "black")
    draw.text((670, y+10), "HORAS", "black")
    draw.text((870, y+10), "PRECIO/H", "black")
    draw.text((1050, y+10), "TOTAL", "black")

    y += 60
    for f in df:
        total_linea = c["h"] * c["t"]
        draw.text((80, y), "Servicio limpieza", (100,100,100))
        draw.text((420, y), f, "black")
        draw.text((680, y), f"{c['h']}", "black")
        draw.text((880, y), f"{c['t']}€", "black")
        draw.text((1050, y), f"{total_linea:.2f}€", "black")
        draw.line([(70, y+30), (1130, y+30)], fill=(230,230,230))
        y += 45

    # Totales
    y += 30
    tf = ht * c["t"]
    draw.text((830, y), f"BASE TOTAL: {tf:.2f}€", "black")
    if c["v"]:
        draw.text((830, y+30), "IVA (Exento): 0,00€", "black")
        y += 30
    draw.line([(830, y+40), (1130, y+40)], "black", 2)
    draw.text((830, y+50), f"TOTAL: {tf:.2f}€", "black")

    # Pie
    y_p = 1300
    pago = f"FORMA DE PAGO: Transferencia/Bizum\nIBAN: ES16 0073 0100 5605 9883 8303" if c["v"] else "FORMA DE PAGO: En Efectivo"
    draw.text((70, y_p), pago, "black")
    draw.text((70, y_p+70), "NOTA: Pago tipo Bono por adelantado.", (80,80,80))
    if c["v"]:
        ley = "Exenta IVA Art. 20.Uno.22 Ley 37/1992.\nDirectiva UE 2020/285"
        draw.text((70, y_p+120), ley, (130,130,130))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue())
    st.download_button("📥 GUARDAR DOCUMENTO", buf.getvalue(), f"{cn}.png")
