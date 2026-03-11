import streamlit as st
import calendar
from datetime import datetime

st.set_page_config(page_title="Gastos e Ingresos - Cleo Pro", layout="centered")

st.title("💰 Gastos e Ingresos")
st.caption("Resumen mensual · Sistema de sobres")

# ─── DATOS CLIENTES ───────────────────────────────────────────────────────────
CLIS = {
    "Ania":     {"t": 13.0, "h": 5.0, "w": [0, 1]},  # lunes=0, martes=1
    "Lola":     {"t": 14.0, "h": 4.0, "w": [2]},      # miércoles=2
    "Yordhana": {"t": 14.0, "h": 4.0, "w": [3]},      # jueves=3
}

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

# ─── SELECTOR MES Y AÑO ───────────────────────────────────────────────────────
col_mes, col_anio = st.columns(2)
with col_mes:
    mes_nombre = st.selectbox("📅 Mes", MESES, index=datetime.now().month - 1)
with col_anio:
    anio = st.number_input("📆 Año", min_value=2024, max_value=2035,
                           value=datetime.now().year, step=1)

mi = MESES.index(mes_nombre) + 1  # 1-12

st.divider()

# ─── SECCIÓN 1: INGRESOS ──────────────────────────────────────────────────────
st.subheader("📈 Ingresos del mes")

ingresos_reales = {}
cal = calendar.Calendar()

for cliente, datos in CLIS.items():
    with st.expander(f"👤 {cliente} · {datos['h']}h · {datos['t']}€/h", expanded=True):

        # Selector de días de la semana para este cliente este mes
        dias_seleccionados = st.multiselect(
            "Días de trabajo este mes",
            options=list(range(7)),
            default=datos["w"],
            format_func=lambda x: DIAS_SEMANA[x],
            key=f"diasem_{cliente}_{mi}_{anio}"
        )

        if not dias_seleccionados:
            st.info("Sin días seleccionados — ingreso 0 €")
            ingresos_reales[cliente] = 0.0
            continue

        # Generar lista de días del mes que coinciden con los días seleccionados
        todos_los_dias = [
            f"{d:02d}/{mi:02d}/{anio}"
            for s in cal.monthdays2calendar(anio, mi)
            for d, ds in s
            if d != 0 and ds in dias_seleccionados
        ]

        # Checkboxes para marcar/desmarcar días concretos
        st.caption("Marca los días que hayas trabajado:")
        cols_dias = st.columns(4)
        dias_trabajados = []
        for i, dia in enumerate(todos_los_dias):
            with cols_dias[i % 4]:
                if st.checkbox(dia, value=True, key=f"dia_{cliente}_{dia}_{anio}"):
                    dias_trabajados.append(dia)

        total_cliente = len(dias_trabajados) * datos["h"] * datos["t"]
        st.metric(
            f"Total {cliente}",
            f"{total_cliente:.2f} €",
            delta=f"{len(dias_trabajados)} días × {datos['h']}h × {datos['t']}€/h"
        )
        ingresos_reales[cliente] = total_cliente

# Otros ingresos
c1, c2 = st.columns([2, 1])
with c1:
    st.write("Otros ingresos")
with c2:
    otros_ingresos = st.number_input(
        "€ otros",
        min_value=0.0, max_value=5000.0,
        value=0.0, step=1.0,
        label_visibility="collapsed",
        key=f"ing_otros_{mi}_{anio}"
    )

total_ingresos = sum(ingresos_reales.values()) + otros_ingresos
st.metric("💵 Total ingresos", f"{total_ingresos:.2f} €")

st.divider()

# ─── SECCIÓN 2: SOBRES ────────────────────────────────────────────────────────
st.subheader("🗂️ Sistema de Sobres")
st.caption("Aparta este dinero nada más cobrar. No lo toques.")

SOBRES_FIJOS = {
    "🏛️ Cuota Autónomo": 88.72,
    "📋 IRPF": 67.00,
    "🏦 Jubilación": 50.00,
}

total_sobres = 0.0
cols_sob = st.columns(len(SOBRES_FIJOS))
sobres_vals = {}
for i, (nombre, importe) in enumerate(SOBRES_FIJOS.items()):
    with cols_sob[i]:
        val = st.number_input(
            nombre,
            min_value=0.0, max_value=1000.0,
            value=importe, step=0.5,
            key=f"sobre_{i}_{mi}_{anio}"
        )
        sobres_vals[nombre] = val
        total_sobres += val
        st.caption(f"📌 {val:.2f} €")

st.metric("🗂️ Total sobres a apartar", f"{total_sobres:.2f} €",
          delta=f"-{total_sobres:.2f} € de lo cobrado", delta_color="inverse")

st.divider()

# ─── SECCIÓN 3: GASTOS ────────────────────────────────────────────────────────
st.subheader("💸 Gastos del mes")

tab_fijos, tab_extras = st.tabs(["Gastos fijos", "Gastos extra (efectivo)"])

GASTOS_FIJOS = {
    "Adeslas (seguro médico)": 30.27,
    "Móvil Mamá (Digi)": 29.90,
    "Tinta HP": 7.99,
    "Digi (propio)": 3.00,
    "Másmovil": 58.90,
}

with tab_fijos:
    total_fijos = 0.0
    for gasto, importe in GASTOS_FIJOS.items():
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write(gasto)
        with c2:
            val = st.number_input(
                f"€ {gasto}",
                min_value=0.0, max_value=2000.0,
                value=importe, step=0.5,
                label_visibility="collapsed",
                key=f"gf_{gasto}_{mi}_{anio}"
            )
            total_fijos += val
    st.metric("Total gastos fijos", f"{total_fijos:.2f} €")

GASTOS_EXTRA = {
    "Gasolina": 70.0,
    "Tabaco": 48.0,
    "Supermercado": 450.0,
    "Terapeuta": 30.0,
}

with tab_extras:
    total_extras = 0.0
    for gasto, importe in GASTOS_EXTRA.items():
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write(gasto)
        with c2:
            val = st.number_input(
                f"€ extra {gasto}",
                min_value=0.0, max_value=2000.0,
                value=importe, step=1.0,
                label_visibility="collapsed",
                key=f"ge_{gasto}_{mi}_{anio}"
            )
            total_extras += val

    st.markdown("---")
    extra_nombre = st.text_input("Otro gasto (nombre)", placeholder="Ej: Farmacia",
                                  key=f"ge_nombre_{mi}_{anio}")
    extra_importe = st.number_input("Importe (€)", min_value=0.0, max_value=2000.0,
                                     value=0.0, step=1.0,
                                     key=f"ge_libre_{mi}_{anio}")
    if extra_nombre and extra_importe > 0:
        total_extras += extra_importe

    st.metric("Total gastos extra", f"{total_extras:.2f} €")

total_gastos = total_fijos + total_extras

st.divider()

# ─── SECCIÓN 4: RESUMEN FINAL ─────────────────────────────────────────────────
st.subheader("📊 Resumen del mes")

neto_real = total_ingresos - total_gastos - total_sobres

col_a, col_b, col_c = st.columns(3)
col_a.metric("📥 Ingresos", f"{total_ingresos:.2f} €")
col_b.metric("📤 Total salidas", f"{total_gastos + total_sobres:.2f} €")
col_c.metric("💚 Dinero libre", f"{neto_real:.2f} €")

with st.expander("🔍 Ver desglose completo"):
    st.markdown("**Ingresos por cliente:**")
    for cliente, val in ingresos_reales.items():
        st.write(f"- {cliente}: {val:.2f} €")
    if otros_ingresos > 0:
        st.write(f"- Otros: {otros_ingresos:.2f} €")
    st.write(f"**= Total ingresos: {total_ingresos:.2f} €**")

    st.markdown("---")
    st.markdown("**Sobres apartados:**")
    for nombre, val in sobres_vals.items():
        st.write(f"- {nombre}: {val:.2f} €")
    st.write(f"**= Total sobres: {total_sobres:.2f} €**")

    st.markdown("---")
    st.markdown("**Gastos fijos:**")
    for gasto, importe in GASTOS_FIJOS.items():
        st.write(f"- {gasto}: {importe:.2f} €")
    st.write(f"**= Total fijos: {total_fijos:.2f} €**")

    st.markdown("---")
    st.write(f"**Gastos extra:** {total_extras:.2f} €")

    st.markdown("---")
    st.write(f"**Ingresos:** {total_ingresos:.2f} €")
    st.write(f"**- Sobres:** -{total_sobres:.2f} €")
    st.write(f"**- Gastos fijos:** -{total_fijos:.2f} €")
    st.write(f"**- Gastos extra:** -{total_extras:.2f} €")
    st.write(f"**= 💚 Dinero libre: {neto_real:.2f} €**")
