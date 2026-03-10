import streamlit as st
import urllib.parse
from datetime import datetime
import calendar

st.set_page_config(page_title="Cleo Gestión Mensual", page_icon="🧹")

st.title("🧹 Cleo: Gestión Mensual")

# --- CONFIGURACIÓN BASE (Tus datos) ---
clientes_base = {
    "Ania": {"tarifa": 13.0, "factura": False, "dias_semana": [0, 1]}, # 0=Lunes, 1=Martes
    "Lola": {"tarifa": 14.0, "factura": True, "dias_semana": [2]},    # 2=Miércoles
    "Yordhana": {"tarifa": 14.0, "factura": True, "dias_semana": [3]} # 3=Jueves
}

# --- LÓGICA DEL MES ACTUAL ---
hoy = datetime.now()
mes_nombre = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"][hoy.month - 1]
st.subheader(f"📅 Previsión para {mes_nombre} {hoy.year}")

def contar_dias_mes(año, mes, dias_objetivo):
    cal = calendar.Calendar()
    semanas = cal.monthdays2calendar(año, mes)
    contador = 0
    for semana in semanas:
        for dia, dia_semana in semana:
            if dia != 0 and dia_semana in dias_objetivo:
                contador += 1
    return contador

# --- INTERFAZ POR CLIENTE ---
for nombre, datos in clientes_base.items():
    with st.expander(f"👤 Factura {nombre}", expanded=True):
        # Calculamos días automáticos
        dias_auto = contar_dias_mes(hoy.year, hoy.month, datos["dias_semana"])
        
        col1, col2 = st.columns(2)
        with col1:
            n_dias = st.number_input(f"Días de trabajo ({nombre})", value=dias_auto, key=f"dias_{nombre}")
            horas_dia = st.number_input(f"Horas por día ({nombre})", value=4.0, step=0.5, key=f"horas_{nombre}")
        
        total_mensual = n_dias * horas_dia * datos["tarifa"]
        
        with col2:
            st.metric("Total Mes", f"{total_mensual:.2f} €")
            if datos["factura"]:
                irpf = total_mensual * 0.20
                st.caption(f"Separar IRPF: {irpf:.2f} €")
                st.caption(f"Neto real: {total_mensual - irpf:.2f} €")
            else:
                st.caption("Cobro Neto (Sin factura)")

        # Botón WhatsApp Mensual
        texto_wa = f"Hola {nombre}, este es el resumen de {mes_nombre}: {n_dias} días de {horas_dia}h. Total: {total_mensual:.2f}€. ¡Gracias!"
        msg_url = urllib.parse.quote(texto_wa)
        st.markdown(f"""<a href="https://wa.me/?text={msg_url}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366; color:white; padding:8px; text-align:center; border-radius:5px; font-size:14px;">
                📲 Enviar factura {mes_nombre}
            </div></a>""", unsafe_allow_html=True)

st.divider()
st.caption("Cleo v2.0 - Cobro por adelantado")
