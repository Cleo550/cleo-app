import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

# --- DATOS FISCALES ---
NOMBRE_LEGAL = "Sandra Ramírez Gálvez"
DIRECCION = "Urb. Alkabir Bloque 5, El Campello"

st.set_page_config(page_title="Cleo App", page_icon="🧹")

def crear_imagen_factura(cliente, num, horas, tarifa, es_legal, mes):
    # Crear un lienzo blanco (tamaño recibo)
    img = Image.new('RGB', (600, 800), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Colores y fuentes (simuladas con trazos básicos)
    color_texto = (0, 0, 0)
    color_azul = (0, 51, 102)
    
    # Encabezado
    d.text((40, 40), "CLEO SERVICIO DE LIMPIEZA", fill=color_azul)
    d.text((40, 70), f"{NOMBRE_LEGAL}", fill=color_texto)
    d.text((40, 90), f"{DIRECCION}", fill=color_texto)
    
    # Título Recibo
    titulo = f"FACTURA: {num}" if es_legal else f"BONO DE SERVICIO: {mes.upper()}"
    d.rectangle([40, 140, 560, 180], outline=color_azul, width=2)
    d.text((200, 150), titulo, fill=color_azul)
    
    # Cuerpo
    d.text((40, 220), f"FECHA: {datetime.now().strftime('%d/%m/%Y')}", fill=color_texto)
    d.text((40, 250), f"CLIENTE: {cliente}", fill=color_texto)
    
    # Tabla de conceptos
    d.line([(40, 300), (560, 300)], fill=color_texto, width=2)
    d.text((50, 320), "CONCEPTO", fill=color_texto)
    d.text((400, 320), "TOTAL", fill=color_texto)
    d.line([(40, 350), (560, 350)], fill=color_texto, width=1)
    
    total_bruto = horas * tarifa
    d.text((50, 370), f"Servicio Limpieza {mes} ({horas}h x {tarifa}€)", fill=color_texto)
    d.text((420, 370), f"{total_bruto:.2f} €", fill=color_texto)
    
    if es_legal:
        irpf = total_bruto * 0.20
        total_final = total_bruto - irpf
        d.text((300, 450), "Retención IRPF (20%):", fill=color_texto)
        d.text((480, 450), f"-{irpf:.2f} €", fill=color_texto)
        d.line([(300, 480), (560, 480)], fill=color_texto, width=2)
        d.text((300, 500), "TOTAL A COBRAR:", fill=color_azul)
        d.text((480, 500), f"{total_final:.2f} €", fill=color_azul)
    else:
        d.line([(300, 430), (560, 430)], fill=color_texto, width=2)
        d.text((300, 450), "TOTAL NETO:", fill=color_azul)
        d.text((480, 450), f"{total_bruto:.2f} €", fill=color_azul)

    # Convertir a formato que Streamlit pueda mostrar
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

st.title("🧹 Generador de Facturas (Imagen)")

# --- INTERFAZ ---
cliente = st.selectbox("¿Para quién es la factura?", ["Ania", "Lola", "Yordhana"])
es_factura = cliente != "Ania"

col1, col2 = st.columns(2)
with col1:
    num_f = st.text_input("Número de factura", value="2026-003") if es_factura else "BONO"
    horas_m = st.number_input("Horas totales del mes", value=16.0)
with col2:
    mes_f = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=datetime.now().month-1)
    tarifa_f = 14.0 if es_factura else 13.0

if st.button("🖼️ GENERAR IMAGEN"):
    imagen_final = crear_imagen_factura(cliente, num_f, horas_m, tarifa_f, es_factura, mes_f)
    
    # Mostrar la imagen en la app para ver cómo queda
    st.image(imagen_final, caption="Previsualización de la factura")
    
    # Botón para descargar la imagen al móvil
    st.download_button(
        label="📥 Guardar imagen en el móvil",
        data=imagen_final,
        file_name=f"Factura_{cliente}_{mes_f}.png",
        mime="image/png"
    )
    st.success("¡Imagen creada! Guárdala y envíala por WhatsApp.")
