import streamlit as st
from PIL import Image, ImageDraw
import calendar
from datetime import datetime
import io

st.set_page_config(page_title="Cleo Pro", layout="centered")

# --- DATOS CLIENTES ---
# Actualizado: Yordhana 4h, Ania 5h. Sin tildes para evitar fallos.
CLIS = {
    "Lola": {"n": "Maria Dolores Albero Moya", "f": "21422031S", "d": "Calle Ramon Orts Galan, 7 B52", "p": "03690 San Vicente", "t": 14.0, "w": [2], "h": 4.0, "v": True},
    "Yordhana": {"n": "Maria de los Angeles Yordhana Gomez", "f": "48361127Q", "d": "Calle Santiago, 45", "p": "03690 San Vicente", "t": 14.0, "w": [3], "h": 4.0, "v": True},
    "Ania": {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3", "p": "03560 El Campello", "t": 13.0, "w": [0, 1], "h": 5.0, "v": False}
}

st.title("Gestion de Facturacion Cleo")

# --- INTERFAZ ---
cn = st.selectbox("Cliente", list(CLIS.keys()))
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
mn = st.selectbox("Mes de servicio", meses, index=datetime.now().month-1)

c = CLIS[cn]
mi = meses.index(mn) + 1
cal = calendar.Calendar()
# Genera los dias del mes para ese cliente
proximos_dias = [f"{d:02d}-{mi:02d}-2026" for s in cal.monthdays2calendar(2026, mi) for d, ds in s if d!=0 and ds in c["w"]]

st.write("### Selecciona los dias que VAS a trabajar")
df = []
for fecha in proximos_dias:
    if st.checkbox(f"Trabajare el {fecha}", value=True):
        df.append(fecha)

ht = len(df) * c["h"]
nf = st.text_input("Factura Numero", f"2026-00{mi}") if c["v"] else ""

if st.button("GENERAR DOCUMENTO FINAL"):
    img = Image.new('RGB', (1200, 1600), "white")
    draw = ImageDraw.Draw(img)
    
    # Intentar cargar logo
    try:
        lg = Image.open("logo.jpeg")
        lg.thumbnail((400, 200))
        img.paste(lg, (400, 50))
    except:
        draw.text((500, 100), "[Logo logo.jpeg no encontrado]", fill="black")

    # Cabecera Derecha
    tit = f"FACTURA N: {nf}" if c["v"] else "BONO MENSUAL"
    draw.text((850, 50), tit, fill="black")
    draw.text((850, 80), f"FECHA: 01/{mi:02d}/2026", fill="black")

    # Datos Emisor (CORREGIDA DIRECCION) y Cliente
    pos_y = 400
    e_txt = f"EMISOR\nSandra Ramirez Galvez\n78217908Z\nUrb. Alkabir Blq 5, pta i\n03560 El Campello"
    draw.text((70, pos_y), e_txt, fill="black")
    
    c_txt = f"CLIENTE\n{c['n']}\nNIF: {c['f']}\n{c['d']}\n{c['p']}"
    draw.text((650, pos_y), c_txt, fill="black")

    # Tabla con Columnas Fijas (Coordenadas X métricas)
    y = 700
    # Cabecera (Sombreado gris)
    draw.rectangle([70, y, 1130, y+40], fill=(240, 240, 240))
    draw.text((80, y+10), "DESCRIPCION", "black")
    draw.text((420, y+10), "FECHA", "black")
    draw.text((670, y+10), "HORAS", "black")
    draw.text((870, y+10), "PRECIO/H", "black")
    draw.text((1050, y+10), "TOTAL", "black")

    y += 60
    # Lineas de servicio
    for f in df:
        total_l = c["h"] * c["t"]
        draw.text((80, y), "Servicio limpieza", (100,100,100))
        draw.text((420, y), f, "black")
        draw.text((680, y), f"{c['h']}", "black")
        draw.text((880, y), f"{c['t']}€", "black")
        draw.text((1050, y), f"{total_l:.2f}€", "black")
        draw.line([(70, y+30), (1130, y+30)], fill=(230,230,230))
        y += 45

    # Totales
    y += 30
    draw.line([(830, y), (1130, y)], "black", 2)
    y += 10
    total_f = ht * c["t"]
    if c["v"]:
        draw.text((830, y), f"BASE TOTAL: {total_f:.2f}€", "black")
        draw.text((830, y+30), "IVA (Exento): 0,00€", "black")
        y += 60
    
    draw.text((830, y), f"TOTAL: {total_f:.2f}€", "black")

    # Pie de pagina dinámico
    y_p = 1300
    # Forma de Pago
    f_pago = f"PAGO: Transferencia o Bizum {c['t']} / 654 422 330" if c["v"] else "FORMA DE PAGO: En Efectivo"
    draw.text((70, y_p), f_pago, "black")
    
    y_p += 40
    # Cláusula legal exacta para facturas (Lola/Yordhana)
    if c["v"]:
        ley_1 = "Exenta IVA Art. 20.Uno.22 Ley 37/1992"
        ley_2 = "y acogida al Regimen de Franquicia de IVA (Directiva UE 2020/285)"
        draw.text((70, y_p), ley_1, (130,130,130))
        draw.text((70, y_p+30), ley_2, (130,130,130))
    
    draw.text((70, y_p+70), "NOTA: Pago tipo Bono que cubre el mes en curso.", (80,80,80))

    # Guardar
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue())
    st.download_button("Guardar Documento", buf.getvalue(), f"{cn}_{mn}.png")
