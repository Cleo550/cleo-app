import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import calendar
from datetime import datetime
import io

st.set_page_config(page_title="Cleo Pro", layout="centered")

# --- DATOS MAESTROS ---
IBAN_CLEO = "ES16 0073 0100 5605 9883 8303 Transferencia / 654 422 330 Bizum"
INFO_EMISOR = "Nombre: Sandra Ramírez Gálvez\nNIF: 78217908Z\nDirección: Urb. Alkabir Blq 5, pta i\nPoblación: 03560 El Campello"

CLIS = {
    "Lola": {"n": "María Dolores Albero Moya", "f": "21422031S", "d": "Calle Alcalde Ramón Orts Galán, 7 Bungalow 52", "p": "03690 Sant Vicent del Raspeig", "t": 14.0, "w": [2]},
    "Yordhana": {"n": "María de los Angeles Yordhana Gomez Sanchez", "f": "48361127Q", "d": "Calle Santiago, 45", "p": "Alicante", "t": 14.0, "w": [3]},
    "Ania": {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3", "p": "Alicante", "t": 13.0, "w": [0, 1]}
}

st.title("✨ Generador de Factura Premium")

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
    h_tot = st.number_input("Total Horas", value=float(len(DIAS)*4))
    nf = st.text_input("Factura Nº", "2026-002")
with col2:
    st.write("📅 **Días detectados:**")
    st.write(", ".join(DIAS))

if st.button("🎨 GENERAR FACTURA EXACTA"):
    # Crear lienzo blanco alta calidad
    img = Image.new('RGB', (1200, 1600), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # 1. CABECERA (Líneas y Número)
    d.line([(600, 50), (1150, 50)], fill=(0,0,0), width=2)
    d.text((800, 20), f"FACTURA Nº: {nf}", fill=(0,0,0))
    d.line([(600, 75), (1150, 75)], fill=(0,0,0), width=1)
    d.text((850, 55), f"FECHA: 01/{M_I:02d}/2026", fill=(0,0,0))

    # 2. LOGO CENTRAL (Simulado como el de la foto)
    # Aquí dibujo un texto elegante ya que no tengo el archivo .jpg del logo
    d.text((450, 150), "Cleo", fill=(0,0,0))
    d.text((150, 280), "S E R V I C I O   D E   L I M P I E Z A", fill=(50,50,50))
    d.line([(50, 320), (1150, 320)], fill=(200, 200, 200), width=1)

    # 3. BLOQUES EMISOR / CLIENTE
    y_info = 450
    d.text((50, y_info), "EMISOR", fill=(0,0,0))
    d.text((50, y_info+30), INFO_EMISOR, fill=(50,50,50))
    
    d.text((600, y_info), "CLIENTE", fill=(0,0,0))
    cli_txt = f"Nombre: {C['n']}\nNIF: {C['f']}\nDirección: {C['d']}\nPoblación: {C['p']}"
    d.text((600, y_info+30), cli_txt, fill=(50,50,50))

    # 4. TABLA DE DESCRIPCIÓN (Igual a la imagen)
    y_tab = 750
    d.text((100, y_tab), "DESCRIPCIÓN", fill=(0,0,0))
    d.text((400, y_tab), "FECHA", fill=(0,0,0))
    d.text((600, y_tab), "HORAS", fill=(0,0,0))
    d.text((800, y_tab), "PRECIO/H", fill=(0,0,0))
    d.text((1000, y_tab), "TOTAL", fill=(0,0,0))
    d.line([(100, y_tab+30), (1100, y_tab+30)], fill=(0,0,0), width=1)

    y = y_tab + 50
    h_d = h_tot / len(DIAS) if DIAS else 0
    for fecha in DIAS:
        subt = h_d * C['t']
        d.text((100, y), "Servicio limpieza", fill=(80,80,80))
        d.text((400, y), fecha, fill=(0,0,0))
        d.text((600, y), f"{h_d:.0f}", fill=(0,0,0))
        d.text((800, y), f"{C['t']:.2f} €", fill=(0,0,0))
        d.text((1000, y), f"{subt:.2f} €", fill=(0,0,0))
        y += 40

    # 5. RESUMEN FINAL
    y += 50
    base_t = h_tot * C['t']
    d.text((800, y), "BASE TOTAL", fill=(0,0,0))
    d.text((1000, y), f"{base_t:.2f} €", fill=(0,0,0))
    d.text((800, y+30), "IVA (Exento)", fill=(0,0,0))
    d.text((1000, y+30), "0,00 €", fill=(0,0,0))
    d.line([(800, y+65), (1100, y+65)], fill=(0,0,0), width=2)
    d.text((800, y+75), "TOTAL", fill=(0,0,0))
    d.text((1000, y+75), f"{base_t:.2f} €", fill=(0,0,0))

    # 6. LEYENDA Y PAGO
    y_pie = y + 150
    leyenda = "Operación exenta de IVA según el Art. 20.Uno.22º de la Ley 37/1992.\nRégimen de Franquicia de IVA para pequeños autónomos (Directiva UE 2020/285)"
    d.text((450, y_pie), leyenda, fill=(100,100,100))
    
    y_pie += 100
    d.text((100, y_pie), f"FORMA DE PAGO: {IBAN_CLEO}", fill=(0,0,0))
    
    y_pie += 120
    nota = "NOTA:\nEl pago es 'tipo Bono' que cubre el mes en curso, a pagar el primer día\nde trabajo del mes, (por adelantado)"
    d.text((200, y_pie), nota, fill=(50,50,50))

    # Guardar y mostrar
    b = io.BytesIO()
    img.save(b, format="PNG")
    st.image(b.getvalue(), caption="Factura Generada con éxito")
    st.download_button("📥 DESCARGAR FACTURA (IMAGEN)", b.getvalue(), f"Factura_{C_S}_{M_S}.png")
