import streamlit as st
import urllib.parse
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Cleo App", page_icon="🧹")

# Estilo para botones grandes y claros
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 3em;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧹 Cleo Servicio de Limpieza")

# --- LÓGICA DE DÍA ---
dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
hoy_num = datetime.now().weekday()
dia_hoy = dias_semana[hoy_num]

# --- DATOS DE CLIENTES ---
# Configuramos quién tiene factura y quién no según tus notas
clientes = {
    "Ania": {"tarifa": 13.0, "factura": False},
    "Lola": {"tarifa": 14.0, "factura": True},
    "Yordhana": {"tarifa": 14.0, "factura": True}
}

# Sugerir cliente según el día
if hoy_num <= 1: sugerencia = "Ania"
elif hoy_num == 2: sugerencia = "Lola"
elif hoy_num == 3: sugerencia = "Yordhana"
else: sugerencia = "Ania"

# --- CALCULADORA ---
st.info(f"📅 Hoy es **{dia_hoy}**")

cliente_sel = st.selectbox("Selecciona cliente:", list(clientes.keys()), index=list(clientes.keys()).index(sugerencia))
horas = st.number_input("Horas trabajadas:", min_value=0.0, step=0.5, value=4.0)

if st.button("CALCULAR JORNADA"):
    tarifa = clientes[cliente_sel]["tarifa"]
    total = horas * tarifa
    
    st.divider()
    st.subheader(f"Total: {total:.2f} €")
    
    col1, col2 = st.columns(2)
    with col1:
        if clientes[cliente_sel]["factura"]:
            irpf = total * 0.20
            st.error(f"Hacienda (20%): {irpf:.2f} €")
            neto = total - irpf
        else:
            st.success("Neto (Sin factura)")
            neto = total
            
    with col2:
        # Apartamos una pequeña parte para la hucha de jubilación (proporcional)
        hucha_jubilacion = 2.27 
        st.warning(f"Hucha 2051: {hucha_jubilacion:.2f} €")
        
    st.divider()

    # --- BOTÓN DE WHATSAPP ---
    texto_msg = f"Hola {cliente_sel}, hoy han sido {horas} horas. El total es de {total:.2f}€. ¡Un saludo!"
    msg_url = urllib.parse.quote(texto_msg)
    
    st.markdown(f"""
        <a href="https://wa.me/?text={msg_url}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366; color:white; padding:15px; text-align:center; border-radius:10px; font-weight:bold; font-size:18px;">
                📲 Enviar por WhatsApp
            </div>
        </a>
        """, unsafe_allow_html=True)

st.divider()
st.caption("Cleo v1.0 | El Campello")
