import streamlit as st
import json
from supabase import create_client
from datetime import datetime

st.set_page_config(page_title="Modelo 130 - Cleo Pro", layout="centered")

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

@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = get_supabase()

def get_dato(clave, defecto):
    try:
        r = supabase.table("datos_app").select("valor").eq("clave", clave).execute()
        if r.data:
            return json.loads(r.data[0]["valor"])
        return defecto
    except:
        return defecto

def set_dato(clave, valor):
    try:
        supabase.table("datos_app").upsert({
            "clave": clave,
            "valor": json.dumps(valor)
        }).execute()
    except:
        pass

MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

TRIMESTRES = {
    "T1 - Enero a Marzo":       [1, 2, 3],
    "T2 - Abril a Junio":       [4, 5, 6],
    "T3 - Julio a Septiembre":  [7, 8, 9],
    "T4 - Octubre a Diciembre": [10, 11, 12],
}

CLIENTES_FACTURA = ["Lola", "Yordhana"]  # Solo los que tienen factura legal

st.title("Modelo 130")
st.caption("Pago fraccionado IRPF - Estimación Directa Simplificada")

col1, col2 = st.columns(2)
with col1:
    trimestre = st.selectbox("Trimestre", list(TRIMESTRES.keys()))
with col2:
    anio = st.number_input("Año", min_value=2024, max_value=2035,
                            value=datetime.now().year, step=1)

meses_trim = TRIMESTRES[trimestre]
t_num = list(TRIMESTRES.keys()).index(trimestre) + 1

st.markdown("---")

# --- INGRESOS ---
st.subheader("📥 Ingresos con factura")
st.caption("Solo Lola y Yordhana (tienen factura legal). Ania no cuenta.")

total_ingresos = 0.0
ingresos_detalle = {}

for cn in CLIENTES_FACTURA:
    ingresos_cliente = 0.0
    for mi in meses_trim:
        # Días trabajados guardados
        key_dias = f"dias_{cn}_{mi}_{anio}"
        num_dias = int(get_dato(key_dias, 0))
        tarifa = 14.0
        horas = 4.0
        ingreso_mes = num_dias * horas * tarifa

        # Líneas extra
        key_lineas = f"lineas_extra_{cn}_{mi}_{anio}"
        lineas_extra = get_dato(key_lineas, [])
        for conc, precio in lineas_extra:
            ingreso_mes += precio

        ingresos_cliente += ingreso_mes
    ingresos_detalle[cn] = ingresos_cliente
    total_ingresos += ingresos_cliente
    st.write(f"- **{cn}**: {ingresos_cliente:.2f} EUR")

st.metric("Total ingresos", f"{total_ingresos:.2f} EUR")

st.markdown("---")

# --- GASTOS DEDUCIBLES ---
st.subheader("📤 Gastos deducibles")

total_gastos_ded = 0.0

# 1. Cuota autónomo (BBVA)
cuota_autonomo = 0.0
for mi in meses_trim:
    val, _ = (get_dato(f"bbva_Cuota_Autonomo_{mi}_{anio}", None),  None)
    # Buscar con lógica histórica hacia atrás
    found = False
    m, a = mi, int(anio)
    for _ in range(24):
        v = get_dato(f"bbva_Cuota_Autónomo_{m}_{a}", None)
        if v is None:
            v = get_dato(f"bbva_Cuota_Autonomo_{m}_{a}", None)
        if v is not None:
            cuota_autonomo += float(v)
            found = True
            break
        m -= 1
        if m == 0:
            m = 12
            a -= 1
    if not found:
        cuota_autonomo += 88.72  # valor por defecto

st.write(f"- **Cuota Autónomo** ({len(meses_trim)} meses): {cuota_autonomo:.2f} EUR")
total_gastos_ded += cuota_autonomo

# 2. RC Limpieza (Trade Republic - pago anual mensualizado)
rc_trimestre = 0.0
for mi in meses_trim:
    rc_mes = 0.0
    m, a = mi, int(anio)
    for _ in range(24):
        v = get_dato(f"sobre_anual_RC_Limpieza_{m}_{a}", None)
        if v is not None:
            rc_mes = float(v) / 12
            break
        m -= 1
        if m == 0:
            m = 12
            a -= 1
    if rc_mes == 0:
        rc_mes = 82.72 / 12
    rc_trimestre += rc_mes

st.write(f"- **RC Limpieza** (mensualizado): {rc_trimestre:.2f} EUR")
total_gastos_ded += rc_trimestre

# 3. Facturas de gastos del trimestre (página Facturas Gastos)
st.write(f"**Facturas de gastos registradas (T{t_num} {int(anio)}):**")
facturas_trim = 0.0
try:
    r = supabase.table("facturas_gastos").select("nombre,importe").eq(
        "trimestre", f"T{t_num}-{int(anio)}").execute()
    if r.data:
        for fac in r.data:
            st.write(f"  · {fac['nombre']}: {float(fac['importe']):.2f} EUR")
            facturas_trim += float(fac['importe'])
    else:
        st.caption("No hay facturas registradas para este trimestre")
except:
    st.caption("No se pudieron cargar las facturas")

st.write(f"- **Total facturas gastos**: {facturas_trim:.2f} EUR")
total_gastos_ded += facturas_trim

st.metric("Total gastos deducibles", f"{total_gastos_ded:.2f} EUR")

st.markdown("---")

# --- CÁLCULO MOD. 130 ---
st.subheader("🧮 Cálculo Modelo 130")

beneficio = total_ingresos - total_gastos_ded
retencion = max(0.0, beneficio * 0.20)

# Pagos anteriores del año
pagos_anteriores = float(get_dato(f"mod130_pagado_{int(anio)}", 0.0))

a_ingresar = max(0.0, retencion - pagos_anteriores)

col1, col2, col3 = st.columns(3)
col1.metric("Ingresos", f"{total_ingresos:.2f} €")
col2.metric("Gastos deducibles", f"{total_gastos_ded:.2f} €")
col3.metric("Beneficio", f"{beneficio:.2f} €")

st.markdown("---")
col4, col5, col6 = st.columns(3)
col4.metric("20% beneficio", f"{retencion:.2f} €")
col5.metric("Pagos anteriores año", f"{pagos_anteriores:.2f} €")
col6.metric("🔴 A INGRESAR", f"{a_ingresar:.2f} €", delta=None)

# Guardar como valor por defecto en Mod.130 de Gastos e Ingresos
importe_mensual = round(a_ingresar / 3, 2)
for mi in meses_trim:
    clave_130 = f"mod130_Mod._130_(trimestral)_{mi}_{anio}"
    set_dato(clave_130, a_ingresar)
st.success(f"✅ Actualizado en Gastos e Ingresos: {a_ingresar:.2f} EUR para T{t_num} ({importe_mensual:.2f} EUR/mes)")

# Marcar como pagado
st.markdown("---")
st.subheader("✅ Marcar como pagado")
pagado_key = f"mod130_pagado_t{t_num}_{int(anio)}"
ya_pagado = get_dato(pagado_key, False)
if ya_pagado:
    st.success(f"Este trimestre ya está marcado como pagado: {a_ingresar:.2f} EUR")
    if st.button("↩️ Desmarcar como pagado"):
        set_dato(pagado_key, False)
        nuevo_total = pagos_anteriores - a_ingresar
        set_dato(f"mod130_pagado_{int(anio)}", max(0, nuevo_total))
        st.rerun()
else:
    if st.button(f"💳 Marcar T{t_num} como pagado ({a_ingresar:.2f} EUR)", type="primary"):
        set_dato(pagado_key, True)
        nuevo_total = pagos_anteriores + a_ingresar
        set_dato(f"mod130_pagado_{int(anio)}", nuevo_total)
        st.rerun()

st.markdown("---")

# --- RESUMEN PARA COPIAR ---
st.subheader("📋 Resumen para presentar en Hacienda")
st.caption("Copia estos datos en la web de la AEAT")

resumen = f"""
MODELO 130 - {trimestre} {int(anio)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Casilla 01 - Ingresos:              {total_ingresos:.2f} EUR
Casilla 02 - Gastos deducibles:     {total_gastos_ded:.2f} EUR
Casilla 03 - Rendimiento neto:      {beneficio:.2f} EUR
Casilla 04 - 20% de casilla 03:     {retencion:.2f} EUR
Casilla 05 - Pagos anteriores:      {pagos_anteriores:.2f} EUR
Casilla 06 - RESULTADO:             {a_ingresar:.2f} EUR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
st.code(resumen, language=None)

st.markdown("---")

# --- GUÍA PASO A PASO ---
st.subheader("📖 Cómo presentar el Modelo 130 paso a paso")

with st.expander("Ver guía completa", expanded=False):
    st.markdown("""
**PASO 1 - Entra en la web de Hacienda**
- Ve a: **sede.agenciatributaria.gob.es**
- Haz clic en **"Trámites destacados"** → **"Modelo 130"**
- O busca directamente **"Modelo 130"** en el buscador de la sede

**PASO 2 - Identifícate**
- Usa tu **Cl@ve PIN**, certificado digital o DNI electrónico
- Si no tienes Cl@ve, puedes darte de alta en la app Cl@ve

**PASO 3 - Rellena el formulario**
- Selecciona el **año** y el **trimestre** que corresponde
- **Casilla 01** → Pon los **Ingresos**: `{ingresos:.2f} EUR`
- **Casilla 02** → Pon los **Gastos deducibles**: `{gastos:.2f} EUR`
- **Casilla 03** → Se calcula sola (01 - 02 = Rendimiento neto)
- **Casilla 04** → Se calcula sola (20% de 03)
- **Casilla 05** → Pagos de trimestres anteriores este año: `{anteriores:.2f} EUR`
- **Casilla 06** → Resultado final a ingresar: `{resultado:.2f} EUR`

**PASO 4 - Revisa y presenta**
- Comprueba que el resultado es `{resultado:.2f} EUR`
- Haz clic en **"Firmar y enviar"**
- Si el resultado es positivo, te pedirá los datos bancarios para el pago
- Si es 0 o negativo, se presenta igualmente pero sin pagar

**PASO 5 - Guarda el justificante**
- Descarga el **PDF del justificante** de presentación
- Guárdalo en la página de **Facturas Gastos** de esta app

**⏰ Fechas límite de presentación:**
- T1 (Enero-Marzo) → hasta el **20 de Abril**
- T2 (Abril-Junio) → hasta el **20 de Julio**
- T3 (Julio-Septiembre) → hasta el **20 de Octubre**
- T4 (Octubre-Diciembre) → hasta el **30 de Enero** del año siguiente
    """.format(
        ingresos=total_ingresos,
        gastos=total_gastos_ded,
        anteriores=pagos_anteriores,
        resultado=a_ingresar
    ))
