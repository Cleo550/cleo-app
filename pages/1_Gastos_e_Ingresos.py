import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Gastos e Ingresos - Cleo Pro", layout="centered")

st.title("💰 Gastos e Ingresos")
st.caption("Resumen mensual · Sistema de sobres · Progreso hacia tu meta")

# ─── DATOS BASE ───────────────────────────────────────────────────────────────
MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

# Ingresos previstos por cliente (del Excel, hoja Cuentas)
INGRESOS_PREVISTOS = {
    "Ania":     [480,520,650,520,520,650,520,585,585,520,585,585],
    "Lola":     [192,168,168,280,224,224,280,224,280,224,224,280],
    "Yordhana": [240,224,224,280,224,224,280,224,224,280,224,280],
}

# Sobres fijos mensuales
SOBRES_FIJOS = {
    "🏛️ Cuota Autónomo": 88.72,
    "📋 IRPF": 67.00,
    "🏦 Jubilación (Trade Republic)": 50.00,
}

# Gastos mensuales fijos (del Excel)
GASTOS_FIJOS_MENSUALES = {
    "Adeslas (seguro médico)": 30.27,
    "Móvil Mamá (Digi)": 29.90,
    "Tinta HP": 7.99,
    "Digi (propio)": 3.00,
    "Másmovil": 58.90,
}

META = 1000.0

# ─── SELECTOR MES ─────────────────────────────────────────────────────────────
mes_nombre = st.selectbox("📅 Mes", MESES, index=datetime.now().month - 1)
mi = MESES.index(mes_nombre)  # índice 0-11

st.divider()

# ─── SECCIÓN 1: INGRESOS ──────────────────────────────────────────────────────
st.subheader("📈 Ingresos del mes")

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("**Cliente**")
with col2:
    st.markdown("**Importe (€)**")

ingresos_reales = {}
for cliente, previstos in INGRESOS_PREVISTOS.items():
    c1, c2 = st.columns([2, 1])
    with c1:
        st.write(cliente)
    with c2:
        val = st.number_input(
            f"€ {cliente}",
            min_value=0.0, max_value=5000.0,
            value=float(previstos[mi]),
            step=1.0,
            label_visibility="collapsed",
            key=f"ing_{cliente}"
        )
        ingresos_reales[cliente] = val

# Ingreso extra (apuestas/otros)
c1, c2 = st.columns([2, 1])
with c1:
    st.write("Otros ingresos")
with c2:
    otros_ingresos = st.number_input(
        "€ otros",
        min_value=0.0, max_value=5000.0,
        value=0.0, step=1.0,
        label_visibility="collapsed",
        key="ing_otros"
    )

total_ingresos = sum(ingresos_reales.values()) + otros_ingresos

st.metric("💵 Total ingresos", f"{total_ingresos:.2f} €")

st.divider()

# ─── SECCIÓN 2: SOBRES ────────────────────────────────────────────────────────
st.subheader("🗂️ Sistema de Sobres")
st.caption("Aparta este dinero nada más cobrar. No lo toques.")

total_sobres = 0.0
cols = st.columns(len(SOBRES_FIJOS))
for i, (nombre, importe) in enumerate(SOBRES_FIJOS.items()):
    with cols[i]:
        val = st.number_input(
            nombre,
            min_value=0.0, max_value=1000.0,
            value=importe, step=0.5,
            key=f"sobre_{i}"
        )
        SOBRES_FIJOS[nombre] = val
        total_sobres += val
        st.caption(f"📌 {val:.2f} €/mes")

st.metric("🗂️ Total sobres a apartar", f"{total_sobres:.2f} €",
          delta=f"-{total_sobres:.2f} € de lo cobrado", delta_color="inverse")

st.divider()

# ─── SECCIÓN 3: GASTOS ────────────────────────────────────────────────────────
st.subheader("💸 Gastos del mes")

tab_fijos, tab_extras = st.tabs(["Gastos fijos", "Gastos extra (efectivo)"])

with tab_fijos:
    total_fijos = 0.0
    for gasto, importe in GASTOS_FIJOS_MENSUALES.items():
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write(gasto)
        with c2:
            val = st.number_input(
                f"€ {gasto}",
                min_value=0.0, max_value=2000.0,
                value=importe, step=0.5,
                label_visibility="collapsed",
                key=f"gf_{gasto}"
            )
            GASTOS_FIJOS_MENSUALES[gasto] = val
            total_fijos += val
    st.metric("Total gastos fijos", f"{total_fijos:.2f} €")

with tab_extras:
    st.caption("Gasolina, tabaco, supermercado, terapeuta, etc.")
    gastos_extra_def = {
        "Gasolina": 70.0,
        "Tabaco": 48.0,
        "Supermercado": 450.0,
        "Terapeuta": 30.0,
    }
    total_extras = 0.0
    for gasto, importe in gastos_extra_def.items():
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write(gasto)
        with c2:
            val = st.number_input(
                f"€ extra {gasto}",
                min_value=0.0, max_value=2000.0,
                value=importe, step=1.0,
                label_visibility="collapsed",
                key=f"ge_{gasto}"
            )
            total_extras += val

    # Gasto extra libre
    st.markdown("---")
    extra_nombre = st.text_input("Otro gasto (nombre)", placeholder="Ej: Farmacia")
    extra_importe = st.number_input("Importe (€)", min_value=0.0, max_value=2000.0,
                                     value=0.0, step=1.0, key="ge_libre")
    if extra_nombre:
        total_extras += extra_importe

    st.metric("Total gastos extra", f"{total_extras:.2f} €")

total_gastos = total_fijos + total_extras

st.divider()

# ─── SECCIÓN 4: RESUMEN FINAL ─────────────────────────────────────────────────
st.subheader("📊 Resumen del mes")

neto_antes_sobres = total_ingresos - total_gastos
neto_real = neto_antes_sobres - total_sobres
diferencia_meta = neto_real - META

# Métricas principales
col_a, col_b, col_c = st.columns(3)
col_a.metric("📥 Ingresos", f"{total_ingresos:.2f} €")
col_b.metric("📤 Gastos totales", f"{total_gastos + total_sobres:.2f} €")
col_c.metric(
    "💚 Dinero libre",
    f"{neto_real:.2f} €",
    delta=f"{diferencia_meta:+.2f} € vs meta 1.000€",
    delta_color="normal"
)

# Barra de progreso hacia meta
st.markdown(f"**Progreso hacia tu meta de {META:.0f} €**")
progreso = min(max(neto_real / META, 0), 1.0)
st.progress(progreso)

if neto_real >= META:
    st.success(f"🎉 ¡Meta alcanzada! Te sobran {neto_real - META:.2f} € este mes.")
elif neto_real >= META * 0.8:
    st.warning(f"⚠️ Casi, casi... Te faltan {META - neto_real:.2f} € para llegar a 1.000 €.")
else:
    st.error(f"❌ Este mes no llegas a la meta. Faltan {META - neto_real:.2f} €.")

# Desglose detallado
with st.expander("🔍 Ver desglose completo"):
    st.markdown("**Ingresos por cliente:**")
    for cliente, val in ingresos_reales.items():
        st.write(f"- {cliente}: {val:.2f} €")
    if otros_ingresos > 0:
        st.write(f"- Otros: {otros_ingresos:.2f} €")
    st.write(f"**= Total ingresos: {total_ingresos:.2f} €**")

    st.markdown("---")
    st.markdown("**Sobres a apartar:**")
    for nombre, val in SOBRES_FIJOS.items():
        st.write(f"- {nombre}: {val:.2f} €")
    st.write(f"**= Total sobres: {total_sobres:.2f} €**")

    st.markdown("---")
    st.markdown("**Gastos fijos:**")
    for gasto, val in GASTOS_FIJOS_MENSUALES.items():
        st.write(f"- {gasto}: {val:.2f} €")
    st.write(f"**= Total fijos: {total_fijos:.2f} €**")

    st.markdown("---")
    st.markdown("**Gastos extra (efectivo):**")
    st.write(f"Total extras: {total_extras:.2f} €")

    st.markdown("---")
    st.write(f"**Ingresos:** {total_ingresos:.2f} €")
    st.write(f"**- Sobres:** -{total_sobres:.2f} €")
    st.write(f"**- Gastos fijos:** -{total_fijos:.2f} €")
    st.write(f"**- Gastos extra:** -{total_extras:.2f} €")
    st.write(f"**= Dinero libre: {neto_real:.2f} €**")
