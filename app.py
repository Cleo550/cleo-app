import streamlit as st
from PIL import Image
from calculadora import mostrar_calculadora

st.set_page_config(page_title="Cleo Pro", layout="centered")

# Ocultar barra "Gestionar la aplicación" en todas las páginas
st.markdown("""
<style>
[data-testid="stToolbar"] { display: none !important; }
[data-testid="manage-app-button"] { display: none !important; }
.stAppDeployButton { display: none !important; }
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

def check_password():
    if st.session_state.get("autenticada"):
        return True
    st.title("Cleo Servicio de Limpieza")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if pwd == st.secrets["password"]:
            st.session_state["autenticada"] = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    st.stop()

check_password()
mostrar_calculadora()

try:
    logo = Image.open("logo.jpeg")
    st.image(logo, use_container_width=True)
except:
    st.title("Cleo Pro")
