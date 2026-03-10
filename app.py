import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import calendar
from datetime import datetime
import io

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Cleo Pro")

# --- DATOS FIJOS (Para evitar cortes al copiar) ---
M_BAN = "ES44 0182 0143 5202 0163 6882 o Bizum 654 422 330"
M_LEY = "Exenta IVA Art. 20.Uno.22 Ley 37/1992. Directiva UE 2020/285."

CLIS = {
    "Lola": {"n": "Maria Dolores Albero Moya", "f": "21422031S", "d": "Calle Alcalde Ramon Orts Galan, 7 B52", "t": 14.0, "w": [2]},
    "Yordhana": {"n": "Maria de los Angeles Yordhana Gomez Sanchez", "f": "48361127Q", "d": "Calle Santiago, 45", "t": 14.0, "w": [3]},
    "Ania": {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3", "t": 13.0, "w": [0, 1]}
}

st.title("🧹 Generador de Factura (Imagen)")

# --- MENÚ ---
C_S = st.selectbox("Cliente", list(CLIS.keys()))
MSS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
M_S = st.selectbox("Mes", MSS, index=2)

# --- CALCULO AUTOMATICO ---
M_I = MSS.index(M_S) + 1
C = CLIS[C_S]
CAL = calendar.Calendar()
# Sugiere las fechas de trabajo (ej. los 4 miércoles de marzo para Lola)
DIAS = [f"{d:02d}/{M_I:02d}" for s in CAL.monthdays2calendar(2026, M_I) for d, ds in s if d != 0 and ds in C["w"]]

col1, col2 = st.columns(2)
with col1:
    h_tot = st.number_input("Horas Totales", value=float(len(DIAS)*4))
with col2:
    nf = st.text_input("N. Factura", "2026-003")

# --- DIBUJAR IMAGEN ---
if st.button("CREAR IMAGEN DE FACTURA"):
    # Crear lienzo (Blanco, tamaño A4 aprox)
    img = Image.new('RGB', (800, 1000), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Textos fijos
    # LOGO: Añadimos la escoba como texto o imagen
    draw.text((50, 40), "🧹 FACTURA DE SERVICIOS", fill=(0,0,0))
    
    # Bloque Datos
    draw.text((50, 100), "EMISOR:\nSandra Ramirez Galvez\n78217908Z\nEl Campello, Alicante", fill=(0,0,0))
    draw.text((450, 100), f"CLIENTE:\n{C['n']}\nNIF: {C['f']}\n{C['d']}", fill=(0,0,0))
    
    # Datos Factura
    draw.text((50, 220), f"Factura N: {nf}      Fecha: 01/{M_I:02d}/2026", fill=(0,0,0))
    
    # Tabla con columnas alineadas
    y_tab = 300
    draw.line([(50, y_tab), (750, y_tab)], fill=(0,0,0), width=2)
    
    # Coordenadas fijas para alinear columnas
    # CONCEPTO (50), FECHAS (250), HORAS (400), PRECIO (500), TOTAL (650)
    draw.text((50, y_tab+10), "CONCEPTO", fill=(0,0,0))
    draw.text((250, y_tab+10), "FECHAS", fill=(0,0,0))
    draw.text((400, y_tab+10), "H", fill=(0,0,0))
    draw.text((500, y_tab+10), "PRECIO", fill=(0,0,0))
    draw.text((650, y_tab+10), "TOTAL", fill=(0,0,0))
    draw.line([(50, y_tab+40), (750, y_tab+40)], fill=(0,0,0), width=1)
    
    y = y_tab + 50
    hd = h_tot / len(DIAS) if DIAS else 0
    p = C['t']
    for f in DIAS:
        tl = hd * p
        # Texto de la línea de servicio
        draw.text((50, y), f"Limpieza domicilio", fill=(0,0,0))
        draw.text((250, y), f, fill=(0,0,0))
        draw.text((400, y), f"{hd:.1f}", fill=(0,0,0))
        draw.text((500, y), f"{p}e", fill=(0,0,0))
        draw.text((650, y), f"{tl:.2f}e", fill=(0,0,0))
        y += 30
        
    # Totales
    total = h_tot * p
    draw.line([(450, y+20), (750, y+20)], fill=(0,0,0), width=2)
    draw.text((450, y+40), f"TOTAL NETO: {total:.2f} Euros", fill=(200, 0, 0))
    
    # Pie de pagina
    y_pie = 850
    draw.text((50, y_pie), M_LEY, fill=(100,100,100))
    pago = f"FORMA DE PAGO: {M_BAN}" if C_S != "Ania" else "FORMA DE PAGO: En Efectivo"
    draw.text((50, y_pie+40), pago, fill=(0,0,0))
    draw.text((50, y_pie+70), "NOTA: Pago tipo bono por adelantado.", fill=(100,100,100))

    # Guardar y Mostrar
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), caption="Factura generada")
    st.download_button("📥 Guardar Foto en el Móvil", buf.getvalue(), "factura.png", "image/png")
