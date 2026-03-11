import streamlit as st
import calendar
from datetime import datetime

st.set_page_config(page_title="Gastos e Ingresos - Cleo Pro", layout="centered")

st.title("Gastos e Ingresos")
st.caption("Resumen mensual - Sistema de sobres")

# --- DATOS CLIENTES ---
CLIS = {
    "Ania":     {"t": 13.0, "h": 5.0, "w": [0, 1]},
    "Lola":     {"t": 14.0, "h": 4.0, "w": [2]},
    "Yordhana": {"t": 14.0, "h": 4.0, "w": [3]},
}

MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

def calcular_ingresos_mes(cliente_data, anio, mes_idx):
    cal = calendar.Calendar()
    dias = [d for s in cal.monthdays2calendar(anio, mes_idx)
            for d, ds in s if d != 0 and ds in cliente_data["w"]]
    return len(dias) * cliente_data["h"] * cliente_data["t"]

# --- SELECTOR MES Y ANIO ---
col_mes, col_anio = st.columns(2)
with col_mes:
    mes_nombre = st.selectbox("Mes", MESES, index=datetime.now().month - 1)
with col_anio:
    anio = st.number_input("Anio", min_value=2024, max_value=2035,
                           value=datetime.now().year, step=1)

mi = MESES.index(mes_nombre) + 1

st.divider()

# --- SECCION 1: INGRESOS ---
st.subheader("Ingresos del mes")

ingresos_reales = {}
for cliente, datos in CLIS.items():
    previsto = calcular_ingresos_mes(datos, anio, mi)
    c1, c2 = st.columns([2, 1])
    with c1:
        cal2 = calendar.Calendar()
        num_dias = len([d for s in cal2.monthdays2calendar(anio, mi)
                        for d, ds in s if d != 0 and ds in datos["w"]])
        st.write(f"{cliente} - {num_dias} dias - {datos['h']}h - {datos['t']} EUR/h")
    with c2:
        val = st.number_input(
            f"EUR {cliente}",
            min_value=0.0, max_value=5000.0,
            value=float(previsto),
            step=1.0,
            label_visibility="collapsed",
            key=f"ing_{cliente}_{mi}_{anio}"
        )
        ingresos_reales[cliente] = val

c1, c2 = st.columns([2, 1])
with c1:
    st.write("Otros ingresos")
with c2:
    otros_ingresos = st.number_input(
        "EUR otros",
        min_value=0.0, max_value=5000.0,
        value=0.0, step=1.0,
        label_visibility="collapsed",
        key=f"ing_otros_{mi}_{anio}"
    )

total_ingresos = sum(ingresos_reales.values()) + otros_ingresos
st.metric("Total ingresos", f"{total_ingresos:.2f} EUR")

st.divider()

# --- SECCION 2: TRADE REPUBLIC ---
st.subheader("Trade Republic")
st.caption("Aparta este dinero nada mas cobrar. No lo toques.")

SOBRES_ANUALES = {
    "Seguro Coche":     25.0,
    "Seguro Decesos":    6.0,
    "RC Limpieza":       8.0,
    "ITV":               6.0,
    "Imp. Circulacion": 11.0,
    "Amazon Prime":      5.0,
    "Plex":              5.0,
    "Regalos":          20.0,
}

SOBRES_MENSUALES = {
    "Cuota Autonomo": 88.72,
    "IRPF":           67.00,
    "Jubilacion":     50.00,
}

total_sobres = 0.0
sobres_vals = {}

st.markdown("**Pagos anuales** - Ahorra mensualmente para no sufrir el golpe")
cols = st.columns(4)
for i, (nombre, importe) in enumerate(SOBRES_ANUALES.items()):
    with cols[i % 4]:
        val = st.number_input(
            nombre,
            min_value=0.0, max_value=500.0,
            value=importe, step=0.5,
            key=f"san_{i}_{mi}_{anio}"
        )
        sobres_vals[nombre] = val
        total_sobres += val
        st.caption(f"{val:.2f} EUR/mes")

total_anuales = sum(sobres_vals[k] for k in SOBRES_ANUALES)
st.info(f"Total pagos anuales: {total_anuales:.2f} EUR/mes - Al anio: {total_anuales*12:.2f} EUR")

st.markdown("---")

st.markdown("**Pagos mensuales**")
cols2 = st.columns(3)
for i, (nombre, importe) in enumerate(SOBRES_MENSUALES.items()):
    with cols2[i]:
        val = st.number_input(
            nombre,
            min_value=0.0, max_value=1000.0,
            value=importe, step=0.5,
            key=f"smen_{i}_{mi}_{anio}"
        )
        sobres_vals[nombre] = val
        total_sobres += val
        st.caption(f"{val:.2f} EUR/mes")

total_mensuales = sum(sobres_vals[k] for k in SOBRES_MENSUALES)
st.info(f"Total pagos mensuales: {total_mensuales:.2f} EUR/mes")

st.markdown("---")
st.metric("Total Trade Republic", f"{total_sobres:.2f} EUR",
          delta=f"-{total_sobres:.2f} EUR de lo cobrado", delta_color="inverse")

st.divider()

# --- SECCION 3: GASTOS ---
st.subheader("Gastos del mes")

tab_bbva, tab_efectivo = st.tabs(["BBVA", "Gastos Efectivo"])

GASTOS_BBVA = {
    "Adeslas (seguro medico)": 30.27,
    "Movil Mama":              29.90,
    "Tinta HP":                 7.99,
    "Masmovil":                58.90,
}

with tab_bbva:
    total_fijos = 0.0
    for gasto, importe in GASTOS_BBVA.items():
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write(gasto)
        with c2:
            val = st.number_input(
                f"EUR {gasto}",
                min_value=0.0, max_value=2000.0,
                value=importe, step=0.5,
                label_visibility="collapsed",
                key=f"gf_{gasto}_{mi}_{anio}"
            )
            total_fijos += val
    st.metric("Total BBVA", f"{total_fijos:.2f} EUR")

GASTOS_EXTRA = {
    "Gasolina":     70.0,
    "Tabaco":       48.0,
    "Supermercado": 450.0,
    "Terapeuta":    30.0,
}

with tab_efectivo:
    total_extras = 0.0
    for gasto, importe in GASTOS_EXTRA.items():
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write(gasto)
        with c2:
            val = st.number_input(
                f"EUR extra {gasto}",
                min_value=0.0, max_value=2000.0,
                value=importe, step=1.0,
                label_visibility="collapsed",
                key=f"ge_{gasto}_{mi}_{anio}"
            )
            total_extras += val

    st.markdown("---")
    extra_nombre = st.text_input("Otro gasto (nombre)", placeholder="Ej: Farmacia",
                                  key=f"ge_nombre_{mi}_{anio}")
    extra_importe = st.number_input("Importe (EUR)", min_value=0.0, max_value=2000.0,
                                     value=0.0, step=1.0,
                                     key=f"ge_libre_{mi}_{anio}")
    if extra_nombre and extra_importe > 0:
        total_extras += extra_importe

    st.metric("Total Efectivo", f"{total_extras:.2f} EUR")

total_gastos = total_fijos + total_extras

st.divider()

# --- SECCION 4: RESUMEN FINAL ---
st.subheader("Resumen del mes")

neto_real = total_ingresos - total_gastos - total_sobres

col_a, col_b, col_c = st.columns(3)
col_a.metric("Ingresos", f"{total_ingresos:.2f} EUR")
col_b.metric("Total salidas", f"{total_gastos + total_sobres:.2f} EUR")
col_c.metric("Dinero libre", f"{neto_real:.2f} EUR")

with st.expander("Ver desglose completo"):
    st.markdown("**Ingresos por cliente:**")
    for cliente, val in ingresos_reales.items():
        st.write(f"- {cliente}: {val:.2f} EUR")
    if otros_ingresos > 0:
        st.write(f"- Otros: {otros_ingresos:.2f} EUR")
    st.write(f"**= Total ingresos: {total_ingresos:.2f} EUR**")

    st.markdown("---")
    st.markdown("**Trade Republic:**")
    st.write(f"- Pagos anuales: {total_anuales:.2f} EUR")
    st.write(f"- Pagos mensuales: {total_mensuales:.2f} EUR")
    st.write(f"**= Total Trade Republic: {total_sobres:.2f} EUR**")

    st.markdown("---")
    st.markdown("**BBVA:**")
    for gasto, importe in GASTOS_BBVA.items():
        st.write(f"- {gasto}: {importe:.2f} EUR")
    st.write(f"**= Total BBVA: {total_fijos:.2f} EUR**")

    st.markdown("---")
    st.write(f"**Gastos Efectivo:** {total_extras:.2f} EUR")

    st.markdown("---")
    st.write(f"**Ingresos:** {total_ingresos:.2f} EUR")
    st.write(f"**- Trade Republic:** -{total_sobres:.2f} EUR")
    st.write(f"**- BBVA:** -{total_fijos:.2f} EUR")
    st.write(f"**- Efectivo:** -{total_extras:.2f} EUR")
    st.write(f"**= Dinero libre: {neto_real:.2f} EUR**")
