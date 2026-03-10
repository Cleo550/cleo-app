import streamlit as st
import urllib.parse
from datetime import datetime
import calendar

st.set_page_config(page_title="Cleo Pro", page_icon="🧹")

st.title("🧹 Gestión Cleo Servicio de Limpieza")

# --- CONFIGURACIÓN DE DATOS ---
clientes_base = {
    "Ania": {"tarifa": 13.0, "factura": False, "dias_semana": [0, 1]},
    "Lola": {"tarifa": 14.0, "factura": True, "dias_semana": [2]},
    "Yordhana": {"tarifa": 14.0, "factura": True, "dias_semana": [3]}
}

meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

def contar_dias_mes(año, mes, dias_objetivo):
    cal = calendar.Calendar()
    semanas = cal.monthdays2calendar(año, mes)
    contador = 0
    for semana in semanas:
        for dia, dia_semana in semana:
            if dia != 0 and dia_semana in dias_objetivo:
                contador += 1
    return contador

# --- PESTAÑAS ---
tab1, tab2 = st.tabs(["💰 Cobros de este Mes", "📅 Previsión y Anual"])

with tab1:
    hoy = datetime.now()
    mes_actual_nombre = meses_nombres[hoy.month - 1]
    st.header(f"Facturación: {mes_actual_nombre}")
    
    for nombre, datos in clientes_base.items():
        with st.expander(f"👤 {nombre}", expanded=True):
            d_auto = contar_dias_mes(hoy.year, hoy.month, datos["dias_semana"])
            c1, c2 = st.columns(2)
            with c1:
                n_dias = st.number_input(f"Días ({nombre})", value=d_auto, key=f"now_{nombre}")
                h_dia = st.number_input(f"Horas/día ({nombre})", value=4.0, step=0.5, key=f"hnow_{nombre}")
            
            total = n_dias * h_dia * datos["tarifa"]
            with c2:
                st.metric("Total", f"{total:.2f} €")
                if datos["factura"]:
                    st.caption(f"IRPF: {total*0.20:.2f} €")
            
            # Botón WhatsApp
            msg = urllib.parse.quote(f"Hola {nombre}, resumen de {mes_actual_nombre}: {n_dias} días de {h_dia}h. Total: {total:.2f}€. ¡Gracias!")
            st.markdown(f'<a href="https://wa.me/?text={msg}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:8px; text-align:center; border-radius:5px;">📲 Enviar WhatsApp</div></a>', unsafe_allow_html=True)

with tab2:
    st.header("Planificador")
    
    # Elegir mes
    mes_sel = st.selectbox("Elige un mes para consultar:", meses_nombres, index=datetime.now().month - 1)
    num_mes_sel = meses_nombres.index(mes_sel) + 1
    
    st.subheader(f"Estimación para {mes_sel}")
    total_estimado_mes = 0
    for nombre, datos in clientes_base.items():
        d_mes = contar_dias_mes(datetime.now().year, num_mes_sel, datos["dias_semana"])
        subtotal = d_mes * 4.0 * datos["tarifa"] # 4h por defecto
        total_estimado_mes += subtotal
        st.write(f"**{nombre}:** {d_mes} días → {subtotal:.2f} €")
    
    st.info(f"**Total estimado en {mes_sel}: {total_estimado_mes:.2f} €**")
    
    st.divider()
    
    # Previsión Anual
    st.subheader(f"📊 Resumen Anual {datetime.now().year}")
    total_anual = 0
    for m in range(1, 13):
        for nombre, datos in clientes_base.items():
            d_m = contar_dias_mes(datetime.now().year, m, datos["dias_semana"])
            total_anual += (d_m * 4.0 * datos["tarifa"])
    
    st.success(f"### Previsión Anual Total: {total_anual:.2f} €")
    st.caption("Nota: El cálculo anual asume 4 horas por día trabajado.")

st.divider()
st.caption("Cleo v3.0 | Gestión Profesional")
