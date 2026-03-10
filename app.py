import streamlit as st
from PIL import Image, ImageDraw
import calendar
import io

st.set_page_config(page_title="Cleo Pro")
st.title("🧹 Factura en Imagen")

# --- DATOS ---
IBAN = "ES44 0182 0143 5202 0163 6882 o Bizum 654 422 330"
LEY = "Exenta IVA Art. 20.Uno.22 Ley 37/1992."

CLIS = {
    "Lola": {"n": "Maria Dolores Albero Moya", "f": "21422031S", "d": "Calle Alcalde Ramon Orts Galan, 7 B52", "t": 14.0, "w": [2]},
    "Yordhana": {"n": "Maria de los Angeles Yordhana Gomez Sanchez", "f": "48361127Q", "d": "Calle Santiago, 45", "t": 14.0, "w": [3]},
    "Ania": {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3", "t": 13.0, "w": [0, 1]}
}

# --- SELECCION ---
C_SEL = st.selectbox("Cliente", list(CLIS.keys()))
MSS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
M_SEL = st.selectbox("Mes", MSS, index=2)

# --- CALCULO ---
M_IDX = MSS.index(M_SEL) + 1
CLI = CLIS[C_SEL]
CAL = calendar.Calendar()
FECHAS = [f"{d:02d}/{M_IDX:02d}" for s in CAL.monthdays2calendar(2026, M_IDX) for d, ds in s if d != 0 and ds in CLI["w"]]

col1, col2 = st.columns(2)
with col1:
    H_TOT = st.number_input("Horas", value=float(len(FECHAS)*4))
with col2:
    N_FAC = st.text_input("N. Factura", "2026-003")

if st.button("CREAR IMAGEN"):
    # Creamos fondo blanco
    img = Image.new('RGB', (800, 1100), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Textos Cabecera
    draw.text((50, 40), "FACTURA / RECIBO", (0,0,0))
    draw.text((50, 100), "EMISOR: Sandra Ramirez", (0,0,0))
    draw.text((50, 120), "NIF: 78217908Z", (0,0,0))
    
    draw.text((450, 100), "CLIENTE: " + CLI['n'], (0,0,0))
    draw.text((450, 120), "NIF: " + CLI['f'], (0,0,0))
    
    # Tabla (Sin lineas largas para evitar errores)
    y = 250
    draw.text((50, y), "FECHA      DETALLE      HORAS      PRECIO      TOTAL", (0,0,0))
    y += 40
    
    h_dia = H_TOT / len(FECHAS) if FECHAS else 0
    for f in FECHAS:
        t_lin = h_dia * CLI['t']
        txt = f"{f}      Limpieza      {h_dia:.1f}      {CLI['t']}e      {t_lin:.2f}e"
        draw.text((50, y), txt, (0,0,0))
        y += 30
        
    # Total Final
    tot_eur = H_TOT * CLI['t']
    y += 50
    draw.text((450, y), "TOTAL NETO: " + str(round(tot_eur, 2)) + " Euros", (255, 0, 0))
    
    # Pago
    y += 100
    msg_pago = "PAGO: " + IBAN if C_SEL != "Ania" else "PAGO: Efectivo"
    draw.text((50, y), msg_pago, (0,0,0))
    draw.text((50, y+40), LEY, (100,100,100))

    # Guardar imagen
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    
    st.image(buf.getvalue())
    st.download_button("💾 DESCARGAR FOTO", buf.getvalue(), "factura.png", "image/png")
    
    # Enlace WhatsApp
    wa_txt = "Hola! Recibo de " + M_SEL + ". Total: " + str(tot_eur) + "e"
    wa_url = "https://wa.me/?text=" + wa_txt.replace(" ", "%20")
    st.markdown("[📲 Enviar por WhatsApp](" + wa_url + ")")
