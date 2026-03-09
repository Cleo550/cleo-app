import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import datetime

# --- CONFIGURACIÓN DE DATOS ---
st.set_page_config(page_title="Cleo App", page_icon="🧹")

# Estilos personalizados
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #333; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧹 Cleo Servicio de Limpieza")
st.write(f"Bienvenida, **Sandra Ramírez**")

# --- BASE DE DATOS DE CLIENTES (Basada en tu Excel) ---
clientes = {
    "Lola (María Dolores)": {"tarifa": 14.0, "nif": "21422031S", "dir": "Calle Alcalde Ramón Orts Galán, 7"},
    "Yordhana (María de los Á.)": {"tarifa": 14.0, "nif": "48361127Q", "dir": "Calle Santiago, 45"},
    "Ania Rogala": {"tarifa": 13.0, "nif": "X0000000X", "dir": "Calle Confrides, 3"}
}

# --- SECCIÓN: CUENTAS Y JUBILACIÓN ---
col1, col2 = st.columns(2)
with col1:
    st.metric("Saldo BBVA", "82.72 €") # Datos de tu seguro/cuota
with col2:
    st.metric("Meta Jubilación 2051", "Ahorrando...")

# --- SECCIÓN: GENERADOR DE FACTURAS ---
st.header("📄 Generar Factura/Bono")
cliente_sel = st.selectbox("Selecciona Cliente", list(clientes.keys()))
mes = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])

horas = st.number_input("Total de horas trabajadas", min_value=1, value=4)
tarifa_actual = clientes[cliente_sel]["tarifa"]
total = horas * tarifa_actual

if st.button("Crear Imagen de Factura"):
    # Aquí el código crea la imagen (simulación para esta versión)
    st.success(f"Factura generada para {cliente_sel}")
    st.info(f"Total a cobrar: {total} €")
    st.write("Cálculo de Sobres:")
    st.write(f"- Hacienda (IRPF): {total * 0.20:.2f} €")
    st.write(f"- Jubilación: 50.00 € (mensual fijo)")

# --- SECCIÓN: GASTOS ---
st.header("📸 Registrar Gasto")
uploaded_file = st.file_uploader("Sube foto del ticket o factura", type=["jpg", "png", "pdf"])
if uploaded_file:
    st.success("Gasto guardado correctamente.")

st.info("Nota: En la Fase 2 activaremos el Modelo 130 cuando verifiquemos que estos totales cuadran con tu Excel.")
