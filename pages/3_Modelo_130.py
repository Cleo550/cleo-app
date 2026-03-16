import streamlit as st
import calendar as cal_module
import json
from supabase import create_client
from datetime import datetime

st.set_page_config(page_title="Modelo 130 - Cleo Pro", layout="centered")

def check_password():
    if st.session_state.get("autenticada"):
        return True
    st.title("Cleo Servicio de Limpieza")
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

ALTA_MES = 3
ALTA_ANIO = 2026

meses_trim_base = TRIMESTRES[trimestre]
t_num = list(TRIMESTRES.keys()).index(trimestre) + 1
trimestre_key = f"T{t_num}_{int(anio)}"

# Filtrar meses anteriores al alta
if int(anio) == ALTA_ANIO:
    meses_trim = [m for m in meses_trim_base if m >= ALTA_MES]
elif int(anio) < ALTA_ANIO:
    meses_trim = []
else:
    meses_trim = meses_trim_base

if not meses_trim:
    st.warning("No hay actividad en este trimestre (antes del alta como autónoma el 2 de marzo de 2026).")
    st.stop()

# Cargar todos los datos de una vez
datos = cargar_todos_datos()
facturas = cargar_facturas_trim(trimestre_key)

st.markdown("---")

# Meses acumulados desde inicio del año (o desde el alta) hasta fin del trimestre
# Solo los meses del trimestre actual (filtrados por fecha de alta)
meses_acumulados = meses_trim

# --- INGRESOS ---
st.subheader("📥 Ingresos con factura")
st.caption("Solo Lola y Yordhana (tienen factura legal). Ania cobra en efectivo y no cuenta.")
st.caption(f"Meses: {', '.join([MESES[m-1] for m in meses_trim])}")

total_ingresos = 0.0

def dias_calendario(weekdays, mi, anio):
    c = cal_module.Calendar()
    return len([d for d, ds in c.itermonthdays2(int(anio), mi) if d != 0 and ds in weekdays])

CLIS_DIAS = {"Lola": [2], "Yordhana": [3]}

hoy = datetime.now()

for cn, c in CLIS.items():
    ingreso_cliente = 0.0
    for mi in meses_acumulados:
        # Si el mes ya ha pasado o es el actual, usar dato de Supabase
        # Si es futuro, calcular del calendario
        es_pasado = (int(anio) < hoy.year) or (int(anio) == hoy.year and mi <= hoy.month)
        if es_pasado:
            num = get_dato_local(datos, f"dias_{cn}_{mi}_{anio}", None)
            if num is None:
                # No hay dato guardado para este mes pasado → calcular del calendario
                num_dias = dias_calendario(CLIS_DIAS[cn], mi, anio)
            else:
                num_dias = int(num)
        else:
            # Mes futuro → calcular del calendario
            num_dias = dias_calendario(CLIS_DIAS[cn], mi, anio)
        ingreso_mes = num_dias * c["h"] * c["t"]
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
# Alta de autónoma: 2 de marzo de 2026
FECHA_ALTA_MES = 3
FECHA_ALTA_ANIO = 2026

cuota_autonomo = 0.0
meses_con_cuota = []
for mi in meses_acumulados:
    # Solo contar meses desde el alta
    if int(anio) > FECHA_ALTA_ANIO or (int(anio) == FECHA_ALTA_ANIO and mi >= FECHA_ALTA_MES):
        v = buscar_historico(datos, "bbva_Cuota_Autónomo", mi, anio,
            buscar_historico(datos, "bbva_Cuota_Autonomo", mi, anio, 88.72))
        cuota_autonomo += v
        meses_con_cuota.append(MESES[mi-1])

if meses_con_cuota:
    st.write(f"- **Cuota Autónomo** ({', '.join(meses_con_cuota)}): {cuota_autonomo:.2f} EUR — *100% deducible*")
else:
    st.write(f"- **Cuota Autónomo**: 0.00 EUR (antes del alta)")
total_gastos_ded += cuota_autonomo

# 2. Facturas subidas del trimestre
st.write(f"**Facturas de gastos subidas (T{t_num} {int(anio)}):**")
facturas_trim_total = 0.0
adeslas_trim = 0.0
# Solo las facturas del trimestre actual
if facturas:
    for fac in facturas:
        importe = float(fac["importe"])
        nombre = fac["nombre"]
        if "adeslas" in nombre.lower() or "seguro salud" in nombre.lower():
            adeslas_trim += importe
        facturas_trim_total += importe
        st.write(f"  · {nombre}: {importe:.2f} EUR — *100% deducible*")
else:
    st.caption("No hay facturas registradas para este trimestre")

# Aviso Adeslas si supera 500€/año
if adeslas_trim > 0:
    # Sumar Adeslas de otros trimestres del año
    adeslas_otros = 0.0
    for t in range(1, 5):
        if t != t_num:
            facs_t = cargar_facturas_trim(f"T{t}_{int(anio)}")
            for fac in facs_t:
                if "adeslas" in fac["nombre"].lower() or "seguro salud" in fac["nombre"].lower():
                    adeslas_otros += float(fac["importe"])
    adeslas_anio = adeslas_trim + adeslas_otros
    if adeslas_anio > 500:
        st.warning(f"⚠️ Adeslas acumulado en {int(anio)}: {adeslas_anio:.2f} EUR — **superas el límite de 500€/año**. Solo puedes deducir 500€ en total.")
    elif adeslas_anio > 400:
        st.warning(f"⚠️ Adeslas acumulado en {int(anio)}: {adeslas_anio:.2f} EUR — te quedan {500-adeslas_anio:.2f} EUR para llegar al límite.")

total_gastos_ded += facturas_trim_total

st.metric("Total gastos deducibles", f"{total_gastos_ded:.2f} EUR")

st.markdown("---")

# --- CÁLCULO ---
st.subheader("🧮 Cálculo Modelo 130")

beneficio = total_ingresos - total_gastos_ded
retencion = max(0.0, beneficio * 0.20)
# Sumar lo pagado en trimestres anteriores de este año
pagos_anteriores = 0.0
for t in range(1, t_num):
    pagado_t = get_dato_local(datos, f"mod130_pagado_t{t}_{int(anio)}", False)
    if pagado_t:
        # Recuperar el importe pagado en ese trimestre
        importe_t = float(get_dato_local(datos, f"mod130_importe_t{t}_{int(anio)}", 0.0))
        pagos_anteriores += importe_t

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
        set_dato(f"mod130_importe_t{t_num}_{int(anio)}", 0.0)
        st.rerun()
else:
    if st.button(f"💳 Marcar T{t_num} como pagado ({a_ingresar:.2f} EUR)", type="primary"):
        set_dato(pagado_key, True)
        set_dato(f"mod130_importe_t{t_num}_{int(anio)}", a_ingresar)
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
