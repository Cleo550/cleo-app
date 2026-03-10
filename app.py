import streamlit as st
from PIL import Image, ImageDraw
import calendar
from datetime import datetime
import io

st.set_page_config(page_title="Cleo Pro", layout="centered")

# --- DATOS MAESTROS (Sin acentos para evitar errores de simbolos) ---
IBAN_CLEO = "ES16 0073 0100 5605 9883 8303 Transferencia / 654 422 330 Bizum"
INFO_EMISOR = "Nombre: Sandra Ramirez Galvez\nNIF: 78217908Z\nDireccion: Urb. Alkabir Blq 5, pta i\nPoblacion: 03560 El Campello"

CLIS = {
    "Lola": {"n": "Maria Dolores Albero Moya", "f": "21422031S", "d": "Calle Alcalde Ramon Orts Galan, 7 Bungalow 52", "p": "03690 Sant Vicent del Raspeig", "t": 14.0, "w": [2], "h": 4.0},
    "Yordhana": {"n": "Maria de los Angeles Yordhana Gomez Sanchez", "f": "48361127Q", "d": "Calle Santiago, 45", "p": "Alicante", "t": 14.0, "w": [3], "h": 4.0},
    "Ania": {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3", "p": "Alicante", "t": 13.0, "w": [0, 1], "h": 5.0}
}

st.title("✨ Facturacion Cleo")

# --- INTERFAZ ---
C_S = st.selectbox("Seleccionar Cliente", list(CLIS.keys()))
MSS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
M_S = st.selectbox("Mes de la Factura", MSS, index=datetime.now().month-1)

M_I = MSS.index(M_S) + 1
C = CLIS[C_S]
CAL = calendar.Calendar()
DIAS = [f"{d:02d}-{M_I:02d}-26" for s in CAL.monthdays2calendar(2026, M_I) for d, ds in s if d!=0 and ds in C["w"]]

col1, col2 = st.columns(2)
with col1:
    h_tot = st.number_input("Total Horas", value=float(len(DIAS)*C["h"]))
    nf = st.text_input("Factura Numero", "2026-002")
with col2:
    st.write("📅 **Dias detectados:**")
    st.write(", ".join(DIAS))

if st.button("🎨 GENERAR FACTURA EXACTA"):
    img = Image.new('RGB', (1200, 1600), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # 1. CABECERA (Lineas y Numero)
    d.line([(600, 50), (1150, 50)], fill=(0,0,0), width=2)
    d.text((800, 20), f"FACTURA N: {nf}", fill=(0,0,0))
    d.line([(600, 75), (1150, 75)], fill=(0,0,0), width=1)
    d.text((850, 55), f"FECHA: 01/{M_I:02d}/2026", fill=(0,0,0))

    # 2. LOGO "CLEO" (Estilo dibujo para que sea elegante)
    d.text((550, 150), "Cleo", fill=(0,0,0))
    d.text((430, 280), "SERVICIO DE LIMPIEZA", fill=(50,50,50))
    d.line([(50, 320), (1150, 320)], fill=(200, 200, 200), width=1)

    # 3. BLOQUES EMISOR / CLIENTE
    y_info = 450
    d.text((50, y_info), "EMISOR", fill=(0,0,0))
    d.text((50, y_info+30), INFO_EMISOR, fill=(50,50,50))
    
    d.text((600, y_info), "CLIENTE", fill=(0,0,0))
    cli_txt = f"Nombre: {C['n']}\nNIF: {C['f']}\nDireccion: {C['d']}\nPoblacion: {C['p']}"
    d.text((600, y_info+30), cli_txt, fill=(50,50,50))

    # 4. TABLA
    y_tab = 750
    d.text((100, y_tab), "DESCRIPCION", fill=(0,0,0))
    d.text((400, y_tab), "FECHA", fill=(0,0,0))
    d.text((600, y_tab), "HORAS", fill=(0,0,0))
    d.text((800, y_tab), "PRECIO/H", fill=(0,0,0))
    d.text((1000, y_tab), "TOTAL", fill=(0,0,0))
    d.line([(100, y_tab+30), (1100, y_tab+30)], fill=(0,0,0), width=1)

    y = y_tab + 50
    for fecha in DIAS:
        subt = C["h"] * C['t']
        d.text((100, y), "Servicio limpieza", fill=(80,80,80))
        d.text((400, y), fecha, fill=(0,0,0))
        d.text((600, y), f"{C['h']:.0f}", fill=(0,0,0))
        d.text((800, y), f"{C['t']:.2f} EUR", fill=(0,0,0))
        d.text((1000, y), f"{subt:.2f} EUR", fill=(0,0,0))
        y += 40

    # 5. RESUMEN FINAL
    y += 50
    base_t = h_tot * C['t']
    d.text((800, y), "BASE TOTAL", fill=(0,0,0))
    d.text((1000, y), f"{base_t:.2f} EUR", fill=(0,0,0))
    d.text((800, y+30), "IVA (Exento)", fill=(0,0,0))
    d.text((1000, y+30), "0,00 EUR", fill=(0,0,0))
    d.line([(800, y+65), (1100, y+65)], fill=(0,0,0), width=2)
    d.text((800, y+75), "TOTAL", fill=(0,0,0))
    d.text((1000, y+75), f"{base_t:.2f} EUR", fill=(0,0,0))

    # 6. PIE
    y_pie = y + 150
    leyenda = "Operacion exenta de IVA segun el Art. 20.Uno.22 de la Ley 37/1992.\nRegimen de Franquicia de IVA para pequeños autonomos (Directiva UE 2020/285)"
    d.text((400, y_pie), leyenda, fill=(100,100,100))
    
    y_pie += 100
    d.text((100, y_pie), f"FORMA DE PAGO: {IBAN_CLEO}", fill=(0,0,0))
    
    y_pie += 120
    nota = "NOTA:\nEl pago es 'tipo Bono' que cubre el mes en curso, a pagar el primer dia\nde trabajo del mes, (por adelantado)"
    d.text((200, y_pie), nota, fill=(50,50,50))

    b = io.BytesIO()
    img.save(b, format="PNG")
    st.image(b.getvalue())
    st.download_button("📥 DESCARGAR FACTURA", b.getvalue(), "factura.png")
