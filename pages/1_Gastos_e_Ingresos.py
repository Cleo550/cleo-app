import streamlit as st
import calendar
from datetime import datetime

st.set_page_config(page_title="Gastos e Ingresos - Cleo Pro", layout="centered")

st.title("💰 Gastos e Ingresos")
st.caption("Resumen mensual · Sistema de sobres")

# ─── DATOS CLIENTES (igual que app.py) ────────────────────────────────────────
CLIS = {
    "Ania":     {"t": 13.0, "h": 5.0, "w": [0, 1]},   # lunes, martes
    "Lola":     {"t": 14.0, "h": 4.0, "w": [2]},       # miércoles
    "Yordhana": {"t": 14.0, "h": 4.0, "w": [3]},       # jueves
}

MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

SOBRES_DEF = {
    "🏛️ Cuota Autónomo": 88.72,
    "📋 IRPF": 67.00,
    "🏦 Jubilación": 50.00,
}

GASTOS_FIJOS_DEF = {
    "Adeslas": 30.27,
    "Móvil Mamá": 29.90,
    "Tinta HP": 7.99,
    "Digi": 3.00,
    "Másmovil": 58.90,
}

GASTOS_EXTRA_DEF = {
    "Gasolina": 70.0,
    "Tabaco": 48.0,
    "Supermercado": 450.0,
    "Terapeuta": 30.0,
}

# ─── FUNCIÓN: ingresos reales según calendario ────────────────────────────────
def dias_trabajados(year, month, weekdays):
    cal = calendar.Calendar()
    return sum(1 for d, ds in cal.itermonthdays2(year, month) if d != 0 and ds in weekdays)

def ingreso_previsto(year, month, cliente):
    c = CLIS[cliente]
    dias = dias_trabajados(year, month, c["w"])
    return dias * c["h"] * c["t"]

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
for cliente in CLIS:
    previsto = ingreso_previsto(int(anio), mi, cliente)
    dias = dias_trabajados(int(anio), mi, CLIS[cliente]["w"])
    c1, c2 = st.columns([2, 1])
    with c1:
        st.write(f"{cliente}")
        st.caption(f"{dias} días × {CLIS[cliente]['h']}h × {CLIS[cliente]['t']}€/h")
    with c2:
        val = st.number_input(
            f"€ {cliente}",
            min_value=0.0, max_value=5000.0,
            value=float(previsto),
            step=1.0,
            label_visibility="collapsed",
            key=f"ing_{cliente}"
        )
        ingresos_reales[cliente] = val

c1, c2 = st.columns([2, 1])
with c1:
    st.write("Otros ingresos")
with c2:
    otros_ingresos = st.number_input(
        "€ otros", min_value=0.0, max_value=5000.0,
        value=0.0, step=1.0,
        label_visibility="collapsed", key="ing_otros"
    )

total_ingresos = sum(ingresos_reales.values()) + otros_ingresos
st.metric("💵 Total ingresos", f"{total_ingresos:.2f} €")

st.divider()

# ─── SECCIÓN 2: SOBRES ────────────────────────────────────────────────────────
st.subheader("🗂️ Sistema de Sobres")
st.caption("Aparta este dinero nada más cobrar.")

total_sobres = 0.0
sobres_vals = {}
cols = st.columns(len(SOBRES_DEF))
for i, (nombre, importe) in enumerate(SOBRES_DEF.items()):
    with cols[i]:
        val = st.number_input(
            nombre, min_value=0.0, max_value=1000.0,
            value=importe, step=0.5, key=f"sobre_{i}"
        )
        sobres_vals[nombre] = val
        total_sobres += val
        st.caption(f"📌 {val:.2f} €")

st.metric("🗂️ Total sobres", f"{total_sobres:.2f} €",
          delta=f"-{total_sobres:.2f} € de lo cobrado", delta_color="inverse")

st.divider()

# ─── SECCIÓN 3: GASTOS ────────────────────────────────────────────────────────
st.subheader("💸 Gastos del mes")

tab_fijos, tab_extras = st.tabs(["Gastos fijos", "Gastos extra (efectivo)"])

with tab_fijos:
    total_fijos = 0.0
    gastos_fijos_vals = {}
    for gasto, importe in GASTOS_FIJOS_DEF.items():
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write(gasto)
        with c2:
            val = st.number_input(
                f"€ {gasto}", min_value=0.0, max_value=2000.0,
                value=importe, step=0.5,
                label_visibility="collapsed", key=f"gf_{gasto}"
            )
            gastos_fijos_vals[gasto] = val
            total_fijos += val
    st.metric("Total gastos fijos", f"{total_fijos:.2f} €")

with tab_extras:
    total_extras = 0.0
    for gasto, importe in GASTOS_EXTRA_DEF.items():
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write(gasto)
        with c2:
            val = st.number_input(
                f"€ {gasto}", min_value=0.0, max_value=2000.0,
                value=importe, step=1.0,
                label_visibility="collapsed", key=f"ge_{gasto}"
            )
            total_extras += val

    st.markdown("---")
    extra_nombre = st.text_input("Otro gasto (nombre)", placeholder="Ej: Farmacia")
    extra_importe = st.number_input("Importe (€)", min_value=0.0, max_value=2000.0,
                                    value=0.0, step=1.0, key="ge_libre")
    if extra_nombre:
        total_extras += extra_importe

    st.metric("Total gastos extra", f"{total_extras:.2f} €")

total_gastos = total_fijos + total_extras

st.divider()

# ─── SECCIÓN 4: RESUMEN ───────────────────────────────────────────────────────
st.subheader("📊 Resumen del mes")

neto_real = total_ingresos - total_gastos - total_sobres

col_a, col_b, col_c = st.columns(3)
col_a.metric("📥 Ingresos", f"{total_ingresos:.2f} €")
col_b.metric("📤 Total salidas", f"{total_gastos + total_sobres:.2f} €")
col_c.metric("💚 Dinero libre", f"{neto_real:.2f} €")

if neto_real >= 0:
    st.success(f"✅ Este mes tienes {neto_real:.2f} € libres.")
else:
    st.error(f"❌ Este mes gastas {abs(neto_real):.2f} € más de lo que ingresas.")

with st.expander("🔍 Ver desglose completo"):
    st.markdown("**Ingresos por cliente:**")
    for cliente, val in ingresos_reales.items():
        dias = dias_trabajados(int(anio), mi, CLIS[cliente]["w"])
        st.write(f"- {cliente} ({dias} días): {val:.2f} €")
    if otros_ingresos > 0:
        st.write(f"- Otros: {otros_ingresos:.2f} €")
    st.write(f"**= Total ingresos: {total_ingresos:.2f} €**")

    st.markdown("---")
    st.markdown("**Sobres:**")
    for nombre, val in sobres_vals.items():
        st.write(f"- {nombre}: {val:.2f} €")
    st.write(f"**= Total sobres: {total_sobres:.2f} €**")

    st.markdown("---")
    st.markdown("**Gastos fijos:**")
    for gasto, val in gastos_fijos_vals.items():
        st.write(f"- {gasto}: {val:.2f} €")
    st.write(f"**= Total fijos: {total_fijos:.2f} €**")

    st.markdown("---")
    st.write(f"**Gastos extra:** {total_extras:.2f} €")
    st.markdown("---")
    st.write(f"**{total_ingresos:.2f} − {total_sobres:.2f} − {total_fijos:.2f} − {total_extras:.2f} = {neto_real:.2f} €**")
