import streamlit as st
from PIL import Image
from calculadora import mostrar_calculadora

st.set_page_config(page_title="Cleo Pro", layout="centered")

def check_password():
    if st.session_state.get("autenticada"):
        return True
    st.title("Cleo Pro")
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
