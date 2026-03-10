import streamlit as st

st.set_page_config(page_title="Cleo App", page_icon="🧹")

st.title("🧹 Cleo Servicio de Limpieza")
st.write(f"Bienvenida, **Cleo**")

# --- BASE DE DATOS DE CLIENTES ---
clientes = {
    "Lola (María Dolores)": {"tarifa": 14.0},
    "Yordhana": {"tarifa": 14.0},
    "Ania": {"tarifa": 13.0}
}

# --- CALCULADORA ---
st.header("📄 Generador de Facturas")
cliente_sel = st.selectbox("Selecciona Cliente", list(clientes.keys()))
horas = st.number_input("Total de horas", min_value=1.0, step=0.5)

if st.button("Calcular Factura"):
    tarifa = clientes[cliente_sel]["tarifa"]
    total = horas * tarifa
    st.success(f"Total a cobrar: {total} €")
    st.info(f"Reserva IRPF (20%): {total * 0.20:.2f} €")
