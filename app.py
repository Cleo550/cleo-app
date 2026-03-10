    import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import calendar
from datetime import datetime
import io

st.set_page_config(page_title="Cleo Pro")

# --- DATOS MAESTROS ---
M_BAN = "ES44 0182 0143 5202 0163 6882 o Bizum 654 422 330"
M_LEY = "Exenta IVA Art. 20.Uno.22 Ley 37/1992. Directiva UE 2020/285."
DATOS_M = "Sandra Ramirez Galvez\n78217908Z\nUrb. Alkabir Blq 5, pta i\n03560 El Campello (Alicante)"

CLIS = {
    "Lola": {"n": "Maria Dolores Albero Moya", "f": "21422031S", "d": "Calle Alcalde Ramon Orts Galan, 7 B52", "t": 14.0, "w": [2], "l": True},
    "Yordhana": {"n": "Maria de los Angeles Yordhana Gomez Sanchez", "f": "48361127Q", "d": "Calle Santiago, 45", "t": 14.0, "w": [3], "l": True},
    "Ania": {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3", "t": 13.0, "w": [0, 1], "l": False}
}

st.markdown("# 🧹 Generador de Facturas")

# --- MENU ---
C_S = st.selectbox("Cliente", list(CLIS.keys()))
MSS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
M_S = st.selectbox("Mes", MSS, index=2)

M_I = MSS.index(M_S) + 1
C = CLIS[C_S]
CAL = calendar.Calendar()
DIAS = [f"{d:02d}/{M_I:02d}" for s in CAL.monthdays2calendar(2026, M_I) for d, ds in s if d!=0 and ds in C["w"]]

col1, col2 = st.columns(2)
with col1:
    h_tot = st.number_input("Horas Totales", value=float(len(DIAS)*4))
with col2:
    nf = st.text_input("N. Factura", "2026-003") if C["l"] else "BONO"

# --- GENERAR IMAGEN ---
if st.button("CREAR IMAGEN DE FACTURA"):
    # Creamos un lienzo limpio y grande
    img = Image.new('RGB', (1000, 1200), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # 1. CABECERA ESTILO PROFESIONAL
    d.rectangle([0, 0, 1000, 150], fill=(245, 245, 245))
    d.text((50, 45), "🧹", fill=(0,0,0)) # Logo
    d.text((100, 50), "FACTURA DE SERVICIOS", fill=(50, 50, 50))
    d.text((700, 50), f"Nº: {nf}\nFecha: 01/{M_I:02d}/2026", fill=(50, 50, 50))

    # 2. BLOQUES DE DATOS (Izquierda Emisor, Derecha Cliente)
    d.text((50, 200), "DE (EMISOR):", fill=(150, 150, 150))
    d.text((50, 230), DATOS_M, fill=(0, 0, 0))
    
    d.text((550, 200), "PARA (CLIENTE):", fill=(150, 150, 150))
    d.text((550, 230), f"{C['n']}\nNIF: {C['f']}\n{C['d']}", fill=(0, 0, 0))

    # 3. TABLA DE SERVICIOS
    y = 450
    # Fondo gris para la cabecera de la tabla
    d.rectangle([50, y, 950, y+40], fill=(230, 230, 230))
    d.text((60, y+10), "DETALLE DEL SERVICIO", fill=(0,0,0))
    d.text((450, y+10), "FECHA", fill=(0,0,0))
    d.text((600, y+10), "HORAS", fill=(0,0,0))
    d.text((750, y+10), "PRECIO", fill=(0,0,0))
    d.text((880, y+10), "TOTAL", fill=(0,0,0))
    
    y += 60
    h_d = h_tot / len(DIAS) if DIAS else 0
    for f in DIAS:
        t_l = h_d * C['t']
        d.text((60, y), f"Limpieza domicilio {M_S}", fill=(80,80,80))
        d.text((450, y), f, fill=(0,0,0))
        d.text((600, y), f"{h_d:.1f}", fill=(0,0,0))
        d.text((750, y), f"{C['t']}€", fill=(0,0,0))
        d.text((880, y), f"{t_l:.2f}€", fill=(0,0,0))
        d.line([(50, y+25), (950, y+25)], fill=(240, 240, 240))
        y += 40

    # 4. TOTAL FINAL
    y += 30
    d.rectangle([650, y, 950, y+60], fill=(255, 240, 240))
    total_f = h_tot * C['t']
    d.text((670, y+20), "TOTAL A PAGAR:", fill=(200, 0, 0))
    d.text((850, y+20), f"{total_f:.2f} €", fill=(200, 0, 0))

    # 5. PIE DE PÁGINA
    y_p = 1000
    d.line([(50, y_p), (950, y_p)], fill=(200, 200, 200))
    d.text((50, y_p+20), M_LEY, fill=(130, 130, 130))
    p_txt = f"PAGO: {M_BAN}" if C_S != "Ania" else "PAGO: En Efectivo"
    d.text((50, y_p+50), p_txt, fill=(0,0,0))
    d.text((50, y_p+80), "Nota: Servicio bajo modalidad de bono.", fill=(150, 150, 150))

    # MOSTRAR Y DESCARGAR
    b = io.BytesIO()
    img.save(b, format="PNG")
    st.image(b.getvalue())
    st.download_button("💾 Guardar Factura en el Móvil", b.getvalue(), "factura.png")
