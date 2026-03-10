import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import calendar
from datetime import datetime
import io

st.set_page_config(page_title="Cleo Pro", layout="centered")

# --- DATOS MAESTROS ---
IBAN = "ES44 0182 0143 5202 0163 6882 o Bizum 654 422 330"
DATOS_CLEO = "Sandra Ramirez Galvez - 78217908Z\nUrb. Alkabir Blq 5, pta i\n03560 El Campello (Alicante)"

CLIS = {
    "Lola": {"nom": "Maria Dolores Albero Moya", "nif": "21422031S", "dir": "Calle Alcalde Ramon Orts Galan, 7 B52", "tar": 14.0, "dias": [2]},
    "Yordhana": {"nom": "Maria de los Angeles Yordhana Gomez Sanchez", "nif": "48361127Q", "dir": "Calle Santiago, 45", "tar": 14.0, "dias": [3]},
    "Ania": {"nom": "Ania Rogala", "nif": "---", "dir": "Calle Confrides, 3", "tar": 13.0, "dias": [0, 1]}
}

st.title("🧹 Generador de Recibos Cleo")

# --- SELECCIÓN ---
c_nom = st.selectbox("Cliente", list(CLIS.keys()))
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
m_nom = st.selectbox("Mes", meses, index=datetime.now().month-1)

# --- CÁLCULO AUTOMÁTICO ---
m_idx = meses.index(m_nom) + 1
c_data = CLIS[c_nom]
cal = calendar.Calendar()
fechas_mes = [f"{d:02d}/{m_idx:02d}" for s in cal.monthdays2calendar(2026, m_idx) for d, ds in s if d != 0 and ds in c_data["dias"]]

st.info(f"Detectados {len(fechas_mes)} días de trabajo en {m_nom}")
h_auto = float(len(fechas_mes) * 4)
h_final = st.number_input("Horas Totales (puedes ajustar si un día no fuiste)", value=h_auto)

if st.button("CREAR IMAGEN PARA WHATSAPP"):
    # Crear lienzo blanco
    img = Image.new('RGB', (800, 1000), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        f_b = ImageFont.load_default()
        f_h = ImageFont.load_default()
    except: pass

    # Dibujar Cabecera
    d.text((50, 50), "RECIBO DE SERVICIO - " + m_nom.upper(), fill=(0,0,0))
    d.text((50, 100), "EMISOR:\n" + DATOS_CLEO, fill=(0,0,0))
    d.text((450, 100), "CLIENTE:\n" + c_data["nom"] + "\n" + c_data["dir"], fill=(0,0,0))
    
    # Tabla
    y = 250
    d.text((50, y), "FECHA          CONCEPTO               HORAS    PRECIO    TOTAL", fill=(0,0,0))
    d.line([(50, y+20), (750, y+20)], fill=(0,0,0))
    
    y += 40
    h_por_dia = h_final / len(fechas_mes) if fechas_mes else 0
    for fecha in fechas_mes:
        t_lin = h_por_dia * c_data["tar"]
        linea = f"{fecha}        Limpieza domicilio      {h_por_dia:.1f}      {c_data['tar']}e      {t_lin:.2f}e"
        d.text((50, y), linea, fill=(0,0,0))
        y += 30
    
    # Total
    total_final = h_final * c_data["tar"]
    d.line([(50, y+10), (750, y+10)], fill=(0,0,0))
    y += 30
    d.text((500, y), f"TOTAL A PAGAR: {total_final:.2f} Euros", fill=(255,0,0))
    
    y += 60
    pago_txt = f"PAGO: {IBAN}" if c_nom != "Ania" else "PAGO: En Efectivo"
    d.text((50, y), pago_txt, fill=(0,0,0))
    d.text((50, y+30), "NOTA: Pago tipo bono por adelantado.", fill=(100,100,100))

    # Guardar y Mostrar
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.image(byte_im, caption="Captura esta imagen o descárgala")
    st.download_button("💾 Guardar Foto en el Móvil", byte_im, "recibo.png", "image/png")
    
    # Botón WhatsApp
    texto_wa = f"Hola! Te envío el recibo de {m_nom}. Total: {total_final:.2f}e. Gracias!"
    wa_url = f"https://wa.me/?text={texto_wa.replace(' ', '%20')}"
    st.markdown(f'[📲 Enviar por WhatsApp]({wa_url})')
