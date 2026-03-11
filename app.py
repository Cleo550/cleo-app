import streamlit as st
from PIL import Image, ImageDraw
import calendar
from datetime import datetime
import io

st.set_page_config(page_title="Cleo Pro", layout="centered")

# --- DATOS CLIENTES ---
CLIS = {
    "Lola":     {"n": "Maria Dolores Albero Moya", "f": "21422031S", "d": "Calle Alcalde Ramon Orts Galan, 7 Bungalow 52", "p": "03690 Sant Vicent del Raspeig", "t": 14.0, "h": 4.0, "w": [2], "v": True},
    "Yordhana": {"n": "Maria de los Angeles Yordhana Gomez Sanchez", "f": "48361127Q", "d": "Calle Santiago, 45", "p": "03690 Sant Vicent del Raspeig", "t": 14.0, "h": 4.0, "w": [3], "v": True},
    "Ania":     {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3  C.P.03560", "p": "El Campello", "t": 13.0, "h": 5.0, "w": [0, 1], "v": False}
}

MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

st.title("Facturacion Cleo Pro")

# --- LEER PREFILL DESDE LANZADERA ---
prefill = st.session_state.get("factura_prefill", None)

# Cliente
clientes_lista = list(CLIS.keys())
idx_cliente = 0
if prefill:
    if prefill["cliente"] in clientes_lista:
        idx_cliente = clientes_lista.index(prefill["cliente"])

cn = st.selectbox("Selecciona Cliente", clientes_lista, index=idx_cliente)

# Mes
idx_mes = datetime.now().month - 1
if prefill and prefill.get("mes") in MESES:
    idx_mes = MESES.index(prefill["mes"])

mn = st.selectbox("Mes de servicio", MESES, index=idx_mes)

# Año
anio_val = prefill["anio"] if prefill else datetime.now().year
anio = st.number_input("Año", min_value=2024, max_value=2035, value=anio_val, step=1)

c = CLIS[cn]
mi = MESES.index(mn) + 1
cal = calendar.Calendar()
d_lista = [f"{d:02d}-{mi:02d}-{int(anio)}" for s in cal.monthdays2calendar(int(anio), mi)
           for d, ds in s if d != 0 and ds in c["w"]]

st.write("### Selecciona los dias trabajados")

# Si viene de lanzadera, marcar solo los dias que corresponden
dias_prefill = []
if prefill and prefill.get("cliente") == cn:
    dias_prefill = [f"{d:02d}-{mi:02d}-{int(anio)}" for d in prefill.get("dias", [])]

df = []
for f in d_lista:
    marcado = (f in dias_prefill) if dias_prefill else True
    if st.checkbox(f"Dia {f}", value=marcado, key=f"chk_{f}"):
        df.append(f)

ht = len(df) * c["h"]
nf = st.text_input("Factura Numero", f"{int(anio)}-00{mi}") if c["v"] else ""

# Limpiar prefill tras usarlo
if prefill and st.button("Limpiar seleccion previa"):
    del st.session_state["factura_prefill"]
    st.rerun()

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
    draw.text((850, 80), f"FECHA: 01/{mi:02d}/{int(anio)}", fill="black")

    y_inf = 400
    emisor = f"EMISOR\nSandra Ramirez Galvez\n78217908Z\nUrb. Alkabir Blq 5, pta i\n03560 El Campello"
    draw.text((70, y_inf), emisor, fill="black")

    cliente = f"CLIENTE\n{c['n']}\nNIF: {c['f']}\n{c['d']}\n{c['p']}"
    draw.text((650, y_inf), cliente, fill="black")

    y = 700
    draw.rectangle([70, y, 1130, y+40], fill=(240, 240, 240))
    draw.text((80, y+10), "DESCRIPCION", fill="black")
    draw.text((420, y+10), "FECHA", fill="black")
    draw.text((670, y+10), "HORAS", fill="black")
    draw.text((870, y+10), "PRECIO/H", fill="black")
    draw.text((1050, y+10), "TOTAL", fill="black")

    y += 60
    for f in df:
        sub = c["h"] * c["t"]
        draw.text((80, y), "Servicio limpieza", fill=(100,100,100))
        draw.text((420, y), f, fill="black")
        draw.text((680, y), f"{c['h']}", fill="black")
        draw.text((880, y), f"{c['t']} Eur", fill="black")
        draw.text((1050, y), f"{sub:.2f} Eur", fill="black")
        draw.line([(70, y+30), (1130, y+30)], fill=(230,230,230))
        y += 45

    y += 30
    tot_f = ht * c["t"]
    if c["v"]:
        draw.text((830, y), f"BASE TOTAL: {tot_f:.2f} Eur", fill="black")
        draw.text((830, y+30), "IVA (Exento): 0,00 Eur", fill="black")
        y += 60

    draw.line([(830, y), (1130, y)], fill="black", width=2)
    draw.text((830, y+10), f"TOTAL: {tot_f:.2f} Eur", fill="black")

    y_p = 1300
    if c["v"]:
        draw.text((70, y_p), "FORMA DE PAGO: Transferencia o Bizum", fill="black")
        draw.text((70, y_p+30), "IBAN: ES44 0182 0143 5202 0163 6882", fill="black")
        l1 = "Operacion exenta de IVA segun Art. 20.Uno.22 Ley 37/1992"
        l2 = "y acogida al Regimen de Franquicia de IVA (Directiva UE 2020/285)"
        draw.text((70, y_p+120), l1, fill=(100,100,100))
        draw.text((70, y_p+150), l2, fill=(100,100,100))
    else:
        draw.text((70, y_p), "FORMA DE PAGO: En Efectivo", fill="black")

    draw.text((70, y_p+70), "NOTA: Pago tipo Bono por adelantado.", fill=(80,80,80))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue())
    nombre_archivo = f"Factura_{cn}_{mn}_{int(anio)}.png" if c["v"] else f"Bono_{cn}_{mn}_{int(anio)}.png"
    st.download_button("Guardar Documento", buf.getvalue(), nombre_archivo)

    # Limpiar prefill tras generar
    if "factura_prefill" in st.session_state:
        del st.session_state["factura_prefill"]
