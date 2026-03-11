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

def calcular_dias_mes(cliente_data, anio, mes_idx):
    cal = calendar.Calendar()
    return [d for s in cal.monthdays2calendar(anio, mes_idx)
            for d, ds in s if d != 0 and ds in cliente_data["w"]]

# --- SELECTOR MES Y ANIO ---
col_mes, col_anio = st.columns(2)
with col_mes:
    mes_nombre = st.selectbox("Mes", MESES, index=datetime.now().month - 1)
with col_anio:
    anio = st.number_input("Año", min_value=2024, max_value=2035,
                           value=datetime.now().year, step=1)

mi = MESES.index(mes_nombre) + 1

st.divider()

# --- SECCION 1: INGRESOS ---
st.subheader("Ingresos del mes")

ingresos_reales = {}
dias_trabajados = {}

for cliente, datos in CLIS.items():
    dias_cal = calcular_dias_mes(datos, anio, mi)
    num_dias_defecto = len(dias_cal)
    key_dias = f"dias_{cliente}_{mi}_{anio}"
    if key_dias not in st.session_state:
        st.session_state[key_dias] = num_dias_defecto
    st.markdown(f"**{cliente}** · {datos['h']}h/dia · {datos['t']} EUR/h")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        num_dias = st.number_input(
            f"Dias trabajados {cliente}",
            min_value=0, max_value=31,
            value=st.session_state[key_dias], step=1,
            key=key_dias,
            label_visibility="collapsed"
        )
        st.caption(f"Dias segun calendario: {num_dias_defecto}")
    with c2:
        st.write("")
        st.write(f"{num_dias} dias")
    with c3:
        total_cliente = num_dias * datos["h"] * datos["t"]
        st.write("")
        st.write(f"**{total_cliente:.2f} EUR**")
    dias_trabajados[cliente] = num_dias
    ingresos_reales[cliente] = total_cliente

st.markdown("---")

if f"ingresos_extra_{mi}_{anio}" not in st.session_state:
    st.session_state[f"ingresos_extra_{mi}_{anio}"] = []

if st.session_state[f"ingresos_extra_{mi}_{anio}"]:
    st.markdown("*Otros ingresos añadidos:*")
    for idx, (nombre_i, importe_i) in enumerate(st.session_state[f"ingresos_extra_{mi}_{anio}"]):
        c1, c2, c3 = st.columns([2, 1, 0.5])
        with c1:
            st.write(nombre_i)
        with c2:
            st.write(f"{importe_i:.2f} EUR")
        with c3:
            if st.button("X", key=f"del_ing_{idx}_{mi}_{anio}"):
                st.session_state[f"ingresos_extra_{mi}_{anio}"].pop(idx)
                st.rerun()

c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    ing_nombre = st.text_input("Otros ingresos",
                                placeholder="Otros ingresos",
                                key=f"ing_nombre_{mi}_{anio}",
                                label_visibility="collapsed")
    st.caption("Otros ingresos")
with c2:
    ing_importe = st.number_input("Importe ingreso EUR",
                                   min_value=0.0, max_value=5000.0,
                                   value=0.0, step=1.0,
                                   key=f"ing_extra_importe_{mi}_{anio}",
                                   label_visibility="collapsed")
    st.caption("Importe EUR")
with c3:
    st.write("")
    if st.button("Añadir ingreso", key=f"btn_add_ing_{mi}_{anio}"):
        if ing_nombre and ing_importe > 0:
            st.session_state[f"ingresos_extra_{mi}_{anio}"].append((ing_nombre, ing_importe))
            st.rerun()

ingresos_extra_total = sum(v for _, v in st.session_state[f"ingresos_extra_{mi}_{anio}"])
total_ingresos = sum(ingresos_reales.values()) + ingresos_extra_total
st.metric("Total ingresos", f"{total_ingresos:.2f} EUR")

st.divider()

# --- SECCION 2: TRADE REPUBLIC ---
st.subheader("Trade Republic")
st.caption("Aparta este dinero nada mas cobrar. No lo toques.")

# nombre: (mensual_defecto, anual_defecto)
SOBRES_ANUALES = {
    "Seguro Coche":     (25.0,  300.0),
    "Seguro Decesos":   (6.0,   65.0),
    "RC Limpieza":      (8.0,   82.72),
    "ITV":              (6.0,   70.0),
    "Imp. Circulacion": (11.0,  129.0),
    "Amazon Prime":     (5.0,   49.9),
    "Plex":             (5.0,   60.0),
    "Regalos":          (20.0,  240.0),
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
for i, (nombre, (mensual, anual)) in enumerate(SOBRES_ANUALES.items()):
    with cols[i % 4]:
        val_anual = st.number_input(
            f"Anual {nombre}",
            min_value=0.0, max_value=2000.0,
            value=anual, step=0.5,
            key=f"anual_{i}_{mi}_{anio}",
            label_visibility="collapsed"
        )
        st.caption(f"Al año: {val_anual:.2f} EUR")
        val_mes_calc = round(val_anual / 12, 2)
        val_mes = st.number_input(
            f"Mensual {nombre}",
            min_value=0.0, max_value=500.0,
            value=val_mes_calc, step=0.5,
            key=f"san_{i}_{mi}_{anio}",
            label_visibility="collapsed"
        )
        st.caption(f"{nombre}: {val_mes:.2f} EUR/mes")
        sobres_vals[nombre] = val_mes
        total_sobres += val_mes

total_anuales = sum(sobres_vals[k] for k in SOBRES_ANUALES)
st.info(f"Total pagos anuales: {total_anuales:.2f} EUR/mes · Al año: {total_anuales*12:.2f} EUR")

if f"tr_extra_{mi}_{anio}" not in st.session_state:
    st.session_state[f"tr_extra_{mi}_{anio}"] = []

if st.session_state[f"tr_extra_{mi}_{anio}"]:
    for idx, (nombre_t, importe_t) in enumerate(st.session_state[f"tr_extra_{mi}_{anio}"]):
        c1, c2, c3 = st.columns([2, 1, 0.5])
        with c1:
            st.write(nombre_t)
        with c2:
            st.write(f"{importe_t:.2f} EUR")
        with c3:
            if st.button("X", key=f"del_tr_{idx}_{mi}_{anio}"):
                st.session_state[f"tr_extra_{mi}_{anio}"].pop(idx)
                st.rerun()
        total_sobres += importe_t

c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    tr_nombre = st.text_input("Nombre sobre TR",
                               placeholder="Ej: Nuevo ahorro",
                               key=f"tr_nombre_{mi}_{anio}",
                               label_visibility="collapsed")
    st.caption("Nombre del sobre")
with c2:
    tr_importe = st.number_input("Importe TR EUR",
                                  min_value=0.0, max_value=1000.0,
                                  value=0.0, step=0.5,
                                  key=f"tr_importe_{mi}_{anio}",
                                  label_visibility="collapsed")
    st.caption("Importe EUR/mes")
with c3:
    st.write("")
    if st.button("Añadir sobre", key=f"btn_add_tr_{mi}_{anio}"):
        if tr_nombre and tr_importe > 0:
            st.session_state[f"tr_extra_{mi}_{anio}"].append((tr_nombre, tr_importe))
            st.rerun()

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
st.write(f"**Total Trade Republic: {total_sobres:.2f} EUR**")

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

    if f"bbva_extra_{mi}_{anio}" not in st.session_state:
        st.session_state[f"bbva_extra_{mi}_{anio}"] = []

    if st.session_state[f"bbva_extra_{mi}_{anio}"]:
        st.markdown("*Gastos añadidos:*")
        for idx, (nombre_b, importe_b) in enumerate(st.session_state[f"bbva_extra_{mi}_{anio}"]):
            c1, c2, c3 = st.columns([2, 1, 0.5])
            with c1:
                st.write(nombre_b)
            with c2:
                st.write(f"{importe_b:.2f} EUR")
            with c3:
                if st.button("X", key=f"del_bbva_{idx}_{mi}_{anio}"):
                    st.session_state[f"bbva_extra_{mi}_{anio}"].pop(idx)
                    st.rerun()
            total_fijos += importe_b

    st.markdown("---")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        bbva_nombre = st.text_input("Nombre gasto BBVA",
                                     placeholder="Ej: Recibo luz",
                                     key=f"bbva_nombre_{mi}_{anio}",
                                     label_visibility="collapsed")
        st.caption("Nombre del gasto")
    with c2:
        bbva_importe = st.number_input("Importe BBVA EUR",
                                        min_value=0.0, max_value=2000.0,
                                        value=0.0, step=0.5,
                                        key=f"bbva_importe_{mi}_{anio}",
                                        label_visibility="collapsed")
        st.caption("Importe EUR")
    with c3:
        st.write("")
        if st.button("Añadir gasto BBVA", key=f"btn_add_bbva_{mi}_{anio}"):
            if bbva_nombre and bbva_importe > 0:
                st.session_state[f"bbva_extra_{mi}_{anio}"].append((bbva_nombre, bbva_importe))
                st.rerun()

    st.metric("Total BBVA", f"{total_fijos:.2f} EUR")

GASTOS_EXTRA_DEF = {
    "Gasolina":     70.0,
    "Tabaco":       48.0,
    "Supermercado": 450.0,
    "Terapeuta":    30.0,
}

with tab_efectivo:
    total_extras = 0.0
    for gasto, importe in GASTOS_EXTRA_DEF.items():
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

    if f"gastos_extra_{mi}_{anio}" not in st.session_state:
        st.session_state[f"gastos_extra_{mi}_{anio}"] = []

    if st.session_state[f"gastos_extra_{mi}_{anio}"]:
        st.markdown("*Gastos añadidos:*")
        for idx, (nombre_g, importe_g) in enumerate(st.session_state[f"gastos_extra_{mi}_{anio}"]):
            c1, c2, c3 = st.columns([2, 1, 0.5])
            with c1:
                st.write(nombre_g)
            with c2:
                st.write(f"{importe_g:.2f} EUR")
            with c3:
                if st.button("X", key=f"del_extra_{idx}_{mi}_{anio}"):
                    st.session_state[f"gastos_extra_{mi}_{anio}"].pop(idx)
                    st.rerun()
            total_extras += importe_g

    st.markdown("---")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        extra_nombre = st.text_input("Nombre del gasto",
                                      placeholder="Ej: Farmacia",
                                      key=f"ge_nombre_{mi}_{anio}",
                                      label_visibility="collapsed")
        st.caption("Nombre del gasto")
    with c2:
        extra_importe = st.number_input("Importe EUR",
                                         min_value=0.0, max_value=2000.0,
                                         value=0.0, step=1.0,
                                         key=f"ge_libre_{mi}_{anio}",
                                         label_visibility="collapsed")
        st.caption("Importe EUR")
    with c3:
        st.write("")
        if st.button("Añadir", key=f"btn_add_{mi}_{anio}"):
            if extra_nombre and extra_importe > 0:
                st.session_state[f"gastos_extra_{mi}_{anio}"].append((extra_nombre, extra_importe))
                st.rerun()

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
        st.write(f"- {cliente} ({dias_trabajados[cliente]} dias): {val:.2f} EUR")

    for nombre_i, importe_i in st.session_state[f"ingresos_extra_{mi}_{anio}"]:
        st.write(f"- {nombre_i}: {importe_i:.2f} EUR")
    st.write(f"**= Total ingresos: {total_ingresos:.2f} EUR**")

    st.markdown("---")
    st.markdown("**Trade Republic:**")
    st.write(f"- Pagos anuales: {total_anuales:.2f} EUR/mes")
    st.write(f"- Pagos mensuales: {total_mensuales:.2f} EUR")
    for nombre_t, importe_t in st.session_state[f"tr_extra_{mi}_{anio}"]:
        st.write(f"- {nombre_t}: {importe_t:.2f} EUR")
    st.write(f"**= Total Trade Republic: {total_sobres:.2f} EUR**")

    st.markdown("---")
    st.markdown("**BBVA:**")
    for gasto, importe in GASTOS_BBVA.items():
        st.write(f"- {gasto}: {importe:.2f} EUR")
    for nombre_b, importe_b in st.session_state[f"bbva_extra_{mi}_{anio}"]:
        st.write(f"- {nombre_b}: {importe_b:.2f} EUR")
    st.write(f"**= Total BBVA: {total_fijos:.2f} EUR**")

    st.markdown("---")
    st.write(f"**Gastos Efectivo:** {total_extras:.2f} EUR")

    st.markdown("---")
    st.write(f"**Ingresos:** {total_ingresos:.2f} EUR")
    st.write(f"**- Trade Republic:** -{total_sobres:.2f} EUR")
    st.write(f"**- BBVA:** -{total_fijos:.2f} EUR")
    st.write(f"**- Efectivo:** -{total_extras:.2f} EUR")
    st.write(f"**= Dinero libre: {neto_real:.2f} EUR**")

st.divider()

# --- SECCION 5: LANZADERA DE FACTURAS ---
st.subheader("Generar facturas")
st.caption("Revisa los dias trabajados arriba y pulsa el boton del cliente para generar su factura.")

for cliente, datos in CLIS.items():
    num_dias = dias_trabajados[cliente]
    total_c = ingresos_reales[cliente]
    dias_lista = calcular_dias_mes(datos, anio, mi)
    if num_dias != len(dias_lista):
        dias_lista = dias_lista[:num_dias]

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.write(f"**{cliente}** · {num_dias} dias · {total_c:.2f} EUR")
    with c3:
        if st.button(f"Factura {cliente}", key=f"btn_fac_{cliente}_{mi}_{anio}"):
            st.session_state["factura_prefill"] = {
                "cliente": cliente,
                "mes": mes_nombre,
                "anio": int(anio),
                "dias": dias_lista,
                "num_dias": num_dias,
            }
            st.switch_page("pages/0_Facturacion.py")
