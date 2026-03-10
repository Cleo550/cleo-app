import streamlit as st

st.set_page_config(page_title="Gastos e Ingresos - Cleo", layout="centered")

st.title("📊 Control de Gastos e Ingresos")

# --- RESUMEN RAPIDO ---
st.subheader("Estado de mis 'Sobres'")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Cuota Autonomo", "88,72 €", help="Tarifa Plana + MEI")
with col2:
    st.metric("Sobre Hacienda", "66,00 €/mes", delta="- IRPF")
with col3:
    st.metric("Sobre Jubilacion", "50,00 €", delta="2051")

st.divider()

# --- FORMULARIO DE GASTOS ---
st.subheader("Anotar nuevo Gasto")
with st.expander("Haz clic para añadir un gasto (Material, Seguro, etc.)"):
    fecha_g = st.date_input("Fecha del gasto")
    tipo_g = st.selectbox("Concepto", ["Material Limpieza", "Seguro RC", "Otros"])
    monto_g = st.number_input("Importe (€)", min_value=0.0, step=0.1)
    if st.button("Guardar Gasto"):
        st.success(f"Gasto de {monto_g}€ guardado (Simulado)")

# --- CALCULO DE MARGEN ---
st.divider()
st.subheader("Calculadora de Margen Neto")
ingresos_est = st.number_input("Ingresos totales del mes (€)", value=1000.0)
gastos_fijos = 88.72 + 66.0 + 50.0 + 6.90 # Cuota + IRPF + Jubi + Seguro aprox
margen = ingresos_est - gastos_fijos

if margen > 150:
    st.balloons()
    st.success(f"Tu margen libre este mes es de: {margen:.2f} €")
else:
    st.warning(f"Margen libre: {margen:.2f} €. Estas cerca del limite de 120€.")
