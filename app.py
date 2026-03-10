import streamlit as st
from PIL import Image, ImageDraw
import calendar
from datetime import datetime
import io

st.set_page_config(page_title="Cleo Pro", layout="centered")

# --- DATOS CLIENTES ---
CLIS = {
    "Lola": {"n": "Maria Dolores Albero Moya", "f": "21422031S", "d": "Calle Ramon Orts Galan, 7 B52", "p": "03690 San Vicente del Raspeig", "t": 14.0, "h": 4.0, "w": [2], "v": True},
    "Yordhana": {"n": "Maria de los Angeles Yordhana Gomez", "f": "48361127Q", "d": "Calle Santiago, 45", "p": "03690 San Vicente del Raspeig", "t": 14.0, "h": 4.0, "w": [3], "v": True},
    "Ania": {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3", "p": "03560 El Campello", "t": 13.0, "h": 5.0, "w": [0, 1], "v": False}
}

st.title("Gestion de Facturacion Cleo")

cn = st.selectbox("Selecciona Cliente", list(CLIS.keys()))
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
mn = st.selectbox("Mes de servicio", meses, index=datetime.now().month-1)

c = CLIS[cn]
mi = meses.index(mn) + 1
cal = calendar.Calendar()
d_lista = [f"{d:02d}-{mi:02d}-2026" for s in cal.monthdays2calendar(2026, mi) for d, ds in s if d!=0 and ds in c["w"]]

st.write("### Selecciona los dias trabajados")
# LINEA REPARADA:
df = [f for f in d_lista if st.checkbox(f"Dia {f}", value=True)]

ht = len(df) * c["h"]
nf = st.text_input("Factura Numero", f"2026-00{mi}") if c["v"] else ""

if st.button("GENERAR DOCUMENTO FINAL"):
    img = Image.new('RGB', (1200, 1600), "white")
    draw = ImageDraw.Draw(img)
    
    try:
        lg = Image.open("logo.jpeg")
        lg.thumbnail((400, 200))
        img.paste(lg, (400, 50))
    except:
        draw.text((500, 100), "[Logo logo.jpeg]", fill="black")

    tit = f"FACTURA N: {nf}" if c["v"] else "BONO MENSUAL"
    draw.text((850, 50), tit, fill="
