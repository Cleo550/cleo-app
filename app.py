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
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
mn = st.selectbox("Mes de servicio", meses, index=datetime.now().month-1)

c = CLIS[cn]
mi = meses.index(mn) + 1
cal = calendar.Calendar()
# REPARADO ERROR LINEA 27 (Dividido en dos para evitar cortes)
d_lista = [f"{d:02d}-{mi:02d}-2026" for s in cal.monthdays2calendar(2026, mi) 
           for d, ds in s if d!=0 and ds in c["w"]]

st.write("### Selecciona los dias trabajados")
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
    draw.text((850, 50), tit, fill="black")
    draw.text((850, 80), f"FECHA: 01/{mi:02d}/2026", fill="black")

    y_inf = 400
    emisor = "EMISOR\nSandra Ramirez Galvez\n78217908Z\nUrb. Alkabir Blq 5, pta i\n03560 El Campello"
    draw.text((70, y_inf), emisor, fill="black")
    
    cliente = f"CLIENTE\n{c['n']}\nNIF: {c['f']}\n{c['d']}\n{c['p']}"
    draw.text((650, y_inf), cliente, fill="black")

    y = 700
    draw.rectangle([70, y, 1130, y+40], fill=(240, 240, 240))
    draw.text((80, y+10), "DESCRIPCION", "black")
    draw.text((420, y+10), "FECHA", "black")
    draw.text((670, y+10), "HORAS", "black")
    draw.text((870, y+10), "PRECIO/H", "black")
    draw.text((1050, y+10), "TOTAL", "black")

    y += 60
    for f in df:
        sub = c["h"] * c["t"]
        draw.text((80, y), "Servicio limpieza", (100,100,100))
        draw.text((420, y), f, "black")
        draw.text((680, y), f"{c['h']}", "black")
        draw.text((880, y), f"{c['t']} Eur", "black")
        draw.text((1050, y), f"{sub:.2f} Eur", "black")
        draw.line([(70, y+30), (1130, y+30)], fill=(230,230,230))
        y += 45

    y += 30
    tot_f = ht * c["t"]
    if c["v"]:
        draw.text((830, y), f"BASE TOTAL: {tot_f:.2f} Eur", "black")
        draw.text((830, y+30), "IVA (Exento): 0,00 Eur", "black")
        y += 60
    
    draw.line([(830, y), (1130, y)], "black", 2)
    draw.text((830, y+10), f"TOTAL: {tot_f:.2f} Eur", "black")

    y_p = 1300
    if c["v"]:
        draw.text((70, y_p), "FORMA DE PAGO: Transferencia o Bizum", "black")
        draw.text((70, y_p+30), "IBAN: ES44 0182 0143 5202 0163 6882", "black")
        l1 = "Operacion exenta de IVA segun Art. 20.Uno.22 Ley 37/1992"
        l2 = "y acogida al Regimen de Franquicia de IVA (Directiva UE 2020/285)"
        draw.text((70, y_p+120), l1, (100,100,100))
        draw.text((70, y_p+150), l2, (100,100,100))
    else:
        draw.text((70, y_p), "FORMA DE PAGO: En Efectivo", "black")
    
    draw.text((70, y_p+70), "NOTA: Pago tipo Bono por adelantado.", (80,80,80))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue())
    st.download_button("Guardar Documento", buf.getvalue(), f"{cn}_{mn}.png")
