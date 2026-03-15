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

@st.cache_data(ttl=60)
def cargar_todos_datos():
    try:
        r = supabase.table("datos_app").select("clave,valor").execute()
        return {row["clave"]: row["valor"] for row in r.data}
    except:
        return {}

@st.cache_data(ttl=60)
def cargar_facturas_trim(trimestre_key):
    try:
        r = supabase.table("facturas_gastos").select("nombre,importe").eq("trimestre", trimestre_key).execute()
        return r.data or []
    except:
        return []

def get_dato_local(datos, clave, defecto):
    if clave in datos:
        try:
            return json.loads(datos[clave])
        except:
            return datos[clave]
    return defecto

def set_dato(clave, valor):
    try:
        supabase.table("datos_app").upsert({
            "clave": clave,
            "valor": json.dumps(valor)
        }).execute()
        cargar_todos_datos.clear()
    except:
        pass

def buscar_historico(datos, prefijo, mi, anio, defecto):
    m, a = mi, int(anio)
    for _ in range(24):
        v = get_dato_local(datos, f"{prefijo}_{m}_{a}", None)
        if v is not None:
            return float(v)
        m -= 1
        if m == 0:
            m = 12
            a -= 1
    return defecto

CLIS = {
    "Lola":     {"t": 14.0, "h": 4.0},
    "Yordhana": {"t": 14.0, "h": 4.0},
}

MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

TRIMESTRES = {
    "T1 - Enero a Marzo":       [1, 2, 3],
    "T2 - Abril a Junio":       [4, 5, 6],
    "T3 - Julio a Septiembre":  [7, 8, 9],
    "T4 - Octubre a Diciembre": [10, 11, 12],
}

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
trimestre_key = f"T{t_num}-{int(anio)}"

# Cargar todos los datos de una vez
datos = cargar_todos_datos()
facturas = cargar_facturas_trim(trimestre_key)

st.markdown("---")

# --- INGRESOS ---
st.subheader("📥 Ingresos con factura")
st.caption("Solo Lola y Yordhana (tienen factura legal). Ania cobra en efectivo y no cuenta.")

total_ingresos = 0.0

for cn, c in CLIS.items():
    ingreso_cliente = 0.0
    for mi in meses_trim:
        # Leer lista de días trabajados
        dias = get_dato_local(datos, f"dias_mod_{cn}_{mi}_{anio}", None)
        if dias is None:
            # Si no hay modificación guardada, usar número de días base
            num = get_dato_local(datos, f"dias_{cn}_{mi}_{anio}", 0)
            ingreso_mes = int(num) * c["h"] * c["t"]
        else:
            ingreso_mes = len(dias) * c["h"] * c["t"]
        # Líneas extra
        lineas = get_dato_local(datos, f"lineas_extra_{cn}_{mi}_{anio}", [])
        for _, precio in lineas:
            ingreso_mes += precio
        ingreso_cliente += ingreso_mes
    total_ingresos += ingreso_cliente
    st.write(f"- **{cn}**: {ingreso_cliente:.2f} EUR")

st.metric("Total ingresos", f"{total_ingresos:.2f} EUR")

st.markdown("---")

# --- GASTOS DEDUCIBLES ---
st.subheader("📤 Gastos deducibles")

total_gastos_ded = 0.0

# 1. Cuota autónomo
cuota_autonomo = 0.0
for mi in meses_trim:
    v = buscar_historico(datos, "bbva_Cuota_Autónomo", mi, anio,
        buscar_historico(datos, "bbva_Cuota_Autonomo", mi, anio, 88.72))
    cuota_autonomo += v
st.write(f"- **Cuota Autónomo** ({len(meses_trim)} meses): {cuota_autonomo:.2f} EUR — *100% deducible*")
total_gastos_ded += cuota_autonomo

# 2. Adeslas — deducible hasta 500€/año
adeslas_trim = 0.0
for mi in meses_trim:
    v = buscar_historico(datos, "bbva_Adeslas", mi, anio, 30.27)
    adeslas_trim += v

# Calcular total Adeslas del año para avisar si supera 500€
adeslas_anio = 0.0
for mi in range(1, 13):
    v = buscar_historico(datos, "bbva_Adeslas", mi, anio, 30.27)
    adeslas_anio += v

adeslas_deducible = min(adeslas_trim, max(0, 500.0 - (adeslas_anio - adeslas_trim)))
st.write(f"- **Adeslas** (este trimestre): {adeslas_trim:.2f} EUR → deducible: {adeslas_deducible:.2f} EUR — *hasta 500€/año*")
if adeslas_anio > 500:
    st.warning(f"⚠️ Adeslas acumulado en {int(anio)}: {adeslas_anio:.2f} EUR — **superas el límite de 500€/año**. Solo puedes deducir 500€ en total.")
elif adeslas_anio > 400:
    st.warning(f"⚠️ Adeslas acumulado en {int(anio)}: {adeslas_anio:.2f} EUR — te quedan {500-adeslas_anio:.2f} EUR para llegar al límite de 500€.")
total_gastos_ded += adeslas_deducible

# 3. Facturas subidas del trimestre
st.write(f"**Facturas de gastos subidas (T{t_num} {int(anio)}):**")
facturas_trim_total = 0.0
if facturas:
    for fac in facturas:
        st.write(f"  · {fac['nombre']}: {float(fac['importe']):.2f} EUR — *100% deducible*")
        facturas_trim_total += float(fac['importe'])
else:
    st.caption("No hay facturas registradas para este trimestre")
total_gastos_ded += facturas_trim_total

st.metric("Total gastos deducibles", f"{total_gastos_ded:.2f} EUR")

st.markdown("---")

# --- CÁLCULO ---
st.subheader("🧮 Cálculo Modelo 130")

beneficio = total_ingresos - total_gastos_ded
retencion = max(0.0, beneficio * 0.20)
pagos_anteriores = float(get_dato_local(datos, f"mod130_pagado_{int(anio)}", 0.0))
a_ingresar = max(0.0, retencion - pagos_anteriores)

col1, col2, col3 = st.columns(3)
col1.metric("Ingresos", f"{total_ingresos:.2f} €")
col2.metric("Gastos deducibles", f"{total_gastos_ded:.2f} €")
col3.metric("Beneficio neto", f"{beneficio:.2f} €")

st.markdown("")
col4, col5, col6 = st.columns(3)
col4.metric("20% beneficio", f"{retencion:.2f} €")
col5.metric("Pagos anteriores año", f"{pagos_anteriores:.2f} €")
col6.metric("🔴 A INGRESAR", f"{a_ingresar:.2f} €")

# Actualizar Mod.130 en Gastos e Ingresos
for mi in meses_trim:
    set_dato(f"mod130_Mod._130_(trimestral)_{mi}_{anio}", a_ingresar)
st.success(f"✅ Gastos e Ingresos actualizado: {a_ingresar:.2f} EUR para T{t_num}")

# Marcar como pagado
st.markdown("---")
st.subheader("✅ Marcar como pagado")
pagado_key = f"mod130_pagado_t{t_num}_{int(anio)}"
ya_pagado = get_dato_local(datos, pagado_key, False)
if ya_pagado:
    st.success(f"T{t_num} ya pagado: {a_ingresar:.2f} EUR")
    if st.button("↩️ Desmarcar como pagado"):
        set_dato(pagado_key, False)
        set_dato(f"mod130_pagado_{int(anio)}", max(0, pagos_anteriores - a_ingresar))
        st.rerun()
else:
    if st.button(f"💳 Marcar T{t_num} como pagado ({a_ingresar:.2f} EUR)", type="primary"):
        set_dato(pagado_key, True)
        set_dato(f"mod130_pagado_{int(anio)}", pagos_anteriores + a_ingresar)
        st.rerun()

st.markdown("---")

# --- RESUMEN PARA COPIAR ---
st.subheader("📋 Resumen para presentar en Hacienda")
st.caption("Copia estos datos en la web de la AEAT")

resumen = f"""MODELO 130 - {trimestre} {int(anio)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Casilla 01 - Ingresos:              {total_ingresos:.2f} EUR
Casilla 02 - Gastos deducibles:     {total_gastos_ded:.2f} EUR
Casilla 03 - Rendimiento neto:      {beneficio:.2f} EUR
Casilla 04 - 20% de casilla 03:     {retencion:.2f} EUR
Casilla 05 - Pagos anteriores año:  {pagos_anteriores:.2f} EUR
Casilla 06 - RESULTADO A INGRESAR:  {a_ingresar:.2f} EUR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
st.code(resumen, language=None)

st.markdown("---")

# --- GUÍA PASO A PASO ---
st.subheader("📖 Cómo presentar el Modelo 130")
with st.expander("Ver guía completa", expanded=False):
    st.markdown(f"""
**PASO 1 — Entra en la web de Hacienda**
- Ve a: **sede.agenciatributaria.gob.es**
- Haz clic en **Todos los trámites → Impuestos → IRPF → Modelo 130**
- O busca **"Modelo 130"** en el buscador

**PASO 2 — Identifícate**
- Usa tu **Cl@ve PIN**, certificado digital o DNI electrónico

**PASO 3 — Rellena el formulario**
- Selecciona **Año: {int(anio)}** y **Trimestre: {t_num}T**
- **Casilla 01** (Ingresos): `{total_ingresos:.2f}`
- **Casilla 02** (Gastos): `{total_gastos_ded:.2f}`
- **Casilla 03** se calcula sola: `{beneficio:.2f}`
- **Casilla 04** se calcula sola: `{retencion:.2f}`
- **Casilla 05** (Pagos anteriores este año): `{pagos_anteriores:.2f}`
- **Casilla 06** (Resultado): `{a_ingresar:.2f}`

**PASO 4 — Revisa y presenta**
- Comprueba que el resultado es **{a_ingresar:.2f} EUR**
- Haz clic en **"Firmar y enviar"**
- Si es positivo, te pedirá datos bancarios para el cargo

**PASO 5 — Guarda el justificante**
- Descarga el **PDF del justificante**
- Súbelo en la página **Facturas Gastos** de esta app para tenerlo guardado

**⏰ Fechas límite:**
- T1 (Enero-Marzo) → hasta el **20 de Abril**
- T2 (Abril-Junio) → hasta el **20 de Julio**
- T3 (Julio-Septiembre) → hasta el **20 de Octubre**
- T4 (Octubre-Diciembre) → hasta el **30 de Enero** del año siguiente
""")
