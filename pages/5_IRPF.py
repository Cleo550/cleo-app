import streamlit as st
import json
import calendar
from datetime import datetime
from supabase import create_client

st.set_page_config(page_title="IRPF - Cleo Pro", layout="centered")

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
def cargar_datos():
    try:
        r = supabase.table("datos_app").select("clave,valor").execute()
        result = {}
        for row in r.data:
            try:
                result[row["clave"]] = json.loads(row["valor"])
            except:
                result[row["clave"]] = row["valor"]
        return result
    except:
        return {}

def get_dato(clave, defecto):
    datos = st.session_state.get("_irpf_datos", {})
    return datos.get(clave, defecto)

def set_dato(clave, valor):
    try:
        supabase.table("datos_app").upsert({"clave": clave, "valor": json.dumps(valor)}).execute()
        cargar_datos.clear()
        if "_irpf_datos" in st.session_state:
            st.session_state["_irpf_datos"][clave] = valor
    except:
        pass

def calcular_dias_mes(cliente_data, anio, mes_idx):
    cal = calendar.Calendar()
    return [d for s in cal.monthdays2calendar(anio, mes_idx)
            for d, ds in s if d != 0 and ds in cliente_data["w"]]

CLIS = {
    "Lola":     {"t": 14.0, "h": 4.0, "w": [2]},
    "Yordhana": {"t": 14.0, "h": 4.0, "w": [3]},
}
MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

# Cargar datos
st.session_state["_irpf_datos"] = cargar_datos()

# =====================
# TÍTULO
# =====================
st.markdown("<h1 style='color:#2ABFBF'>Declaración de la Renta (IRPF)</h1>", unsafe_allow_html=True)
st.caption("Ejercicio fiscal anual. Todos los datos se guardan para la presentación.")

# Selector de año
anio = st.number_input("Año fiscal", min_value=2026, max_value=2040,
                        value=datetime.now().year, step=1)

st.markdown("---")

# =====================
# 1. ACTIVIDAD ECONÓMICA
# =====================
st.markdown("<h2 style='color:#2ABFBF'>1. Actividad económica</h2>", unsafe_allow_html=True)
st.caption("Ingresos como autónoma menos gastos deducibles.")

# Ingresos anuales automáticos
ingresos_anuales = 0.0
with st.expander("📊 Ver desglose de ingresos por cliente", expanded=False):
    for cn, c in CLIS.items():
        total_cliente = 0.0
        for m in range(1, 13):
            num = get_dato(f"dias_{cn}_{m}_{anio}", None)
            if num is None:
                num_dias = len(calcular_dias_mes(c, int(anio), m))
            else:
                num_dias = int(num)
            total_cliente += num_dias * c["h"] * c["t"]
        st.write(f"- **{cn}**: {total_cliente:.2f} EUR")
        ingresos_anuales += total_cliente

st.metric("Total ingresos clientes", f"{ingresos_anuales:.2f} €")

# Gastos deducibles anuales automáticos
st.markdown("<h3 style='color:#FF69B4'>Gastos deducibles</h3>", unsafe_allow_html=True)

# Cuota autónomo anual
cuota_anual = sum(float(get_dato(f"bbva_Cuota_Autonomo_{m}_{anio}", 88.72)) for m in range(1, 13))
# Adeslas anual
adeslas_anual = sum(float(get_dato(f"bbva_Adeslas_{m}_{anio}", 30.27)) for m in range(1, 13))
# Facturas gastos anuales desde Supabase
try:
    r = supabase.table("facturas_gastos").select("importe").execute()
    facturas_anuales = sum(float(f["importe"]) for f in r.data) if r.data else 0.0
except:
    facturas_anuales = 0.0

with st.expander("📊 Ver desglose de gastos deducibles", expanded=False):
    st.write(f"- Cuota autónomo: {cuota_anual:.2f} EUR")
    st.write(f"- Adeslas (seguro médico): {adeslas_anual:.2f} EUR")
    st.write(f"- Facturas gastos subidas: {facturas_anuales:.2f} EUR")

total_gastos_ded = cuota_anual + adeslas_anual + facturas_anuales
st.metric("Total gastos deducibles", f"{total_gastos_ded:.2f} €")

# Mod. 130 pagado
mod130_pagado = 0.0
for t in range(1, 5):
    if get_dato(f"mod130_pagado_t{t}_{anio}", False):
        mod130_pagado += float(get_dato(f"mod130_importe_t{t}_{anio}", 0.0))
st.metric("Mod. 130 ya pagado (se resta)", f"{mod130_pagado:.2f} €")

rendimiento_actividad = ingresos_anuales - total_gastos_ded
st.metric("📌 Rendimiento neto actividad", f"{rendimiento_actividad:.2f} €")

st.markdown("---")

# =====================
# 2. AYUDAS Y SUBVENCIONES
# =====================
st.markdown("<h2 style='color:#2ABFBF'>2. Ayudas y subvenciones</h2>", unsafe_allow_html=True)
st.caption("Ayudas ingresadas en cuenta — se suman a los ingresos de actividad.")

key_ayudas = f"irpf_ayudas_{anio}"
if key_ayudas not in st.session_state:
    st.session_state[key_ayudas] = get_dato(key_ayudas, [])

if st.session_state[key_ayudas]:
    for idx, (nombre_a, importe_a) in enumerate(st.session_state[key_ayudas]):
        c1, c2, c3 = st.columns([3, 1, 0.5])
        with c1:
            st.write(nombre_a)
        with c2:
            st.write(f"{importe_a:.2f} EUR")
        with c3:
            if st.button("🗑️", key=f"del_ayuda_{idx}_{anio}"):
                st.session_state[key_ayudas].pop(idx)
                set_dato(key_ayudas, st.session_state[key_ayudas])
                st.rerun()

c1, c2, c3 = st.columns([3, 1, 1])
with c1:
    ayuda_nombre = st.text_input("Nombre", placeholder="Ej: Subvención autónomos IVACE",
                                  key=f"ayuda_nom_{anio}", label_visibility="collapsed")
    st.caption("Nombre de la ayuda")
with c2:
    ayuda_importe = st.number_input("Importe", min_value=0.0, max_value=20000.0,
                                     value=0.0, step=1.0, key=f"ayuda_imp_{anio}",
                                     label_visibility="collapsed")
    st.caption("Importe EUR")
with c3:
    st.write("")
    if st.button("Añadir", key=f"btn_ayuda_{anio}"):
        if ayuda_nombre and ayuda_importe > 0:
            st.session_state[key_ayudas].append((ayuda_nombre, ayuda_importe))
            set_dato(key_ayudas, st.session_state[key_ayudas])
            st.rerun()

total_ayudas = sum(v for _, v in st.session_state[key_ayudas])
st.metric("Total ayudas", f"{total_ayudas:.2f} €")

st.markdown("---")

# =====================
# 3. GANANCIAS PATRIMONIALES
# =====================
st.markdown("<h2 style='color:#2ABFBF'>3. Ganancias patrimoniales</h2>", unsafe_allow_html=True)
st.caption("Apuestas, venta de acciones, etc.")

key_ganancias = f"irpf_ganancias_{anio}"
if key_ganancias not in st.session_state:
    st.session_state[key_ganancias] = get_dato(key_ganancias, [])

if st.session_state[key_ganancias]:
    for idx, (nombre_g, importe_g) in enumerate(st.session_state[key_ganancias]):
        c1, c2, c3 = st.columns([3, 1, 0.5])
        with c1:
            st.write(nombre_g)
        with c2:
            color = "green" if importe_g >= 0 else "red"
            st.markdown(f"<span style='color:{color}'>{importe_g:+.2f} EUR</span>", unsafe_allow_html=True)
        with c3:
            if st.button("🗑️", key=f"del_gan_{idx}_{anio}"):
                st.session_state[key_ganancias].pop(idx)
                set_dato(key_ganancias, st.session_state[key_ganancias])
                st.rerun()

c1, c2, c3 = st.columns([3, 1, 1])
with c1:
    gan_nombre = st.text_input("Nombre", placeholder="Ej: Apuestas deportivas, Venta acciones",
                                key=f"gan_nom_{anio}", label_visibility="collapsed")
    st.caption("Concepto")
with c2:
    gan_importe = st.number_input("Importe", min_value=-50000.0, max_value=50000.0,
                                   value=0.0, step=1.0, key=f"gan_imp_{anio}",
                                   label_visibility="collapsed")
    st.caption("Importe (negativo = pérdida)")
with c3:
    st.write("")
    if st.button("Añadir", key=f"btn_gan_{anio}"):
        if gan_nombre and gan_importe != 0:
            st.session_state[key_ganancias].append((gan_nombre, gan_importe))
            set_dato(key_ganancias, st.session_state[key_ganancias])
            st.rerun()

total_ganancias = sum(v for _, v in st.session_state[key_ganancias])
color_g = "green" if total_ganancias >= 0 else "red"
st.markdown(f"**Total ganancias patrimoniales:** <span style='color:{color_g}'>{total_ganancias:+.2f} €</span>", unsafe_allow_html=True)

st.markdown("---")

# =====================
# 4. CAPITAL MOBILIARIO
# =====================
st.markdown("<h2 style='color:#2ABFBF'>4. Capital mobiliario</h2>", unsafe_allow_html=True)
st.caption("Dividendos e intereses de Trade Republic u otras inversiones.")

key_capital = f"irpf_capital_{anio}"
if key_capital not in st.session_state:
    st.session_state[key_capital] = get_dato(key_capital, [])

if st.session_state[key_capital]:
    for idx, (nombre_c, importe_c, retencion_c) in enumerate(st.session_state[key_capital]):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 0.5])
        with c1:
            st.write(nombre_c)
        with c2:
            st.write(f"{importe_c:.2f} EUR")
        with c3:
            st.caption(f"Ret: {retencion_c:.2f}€")
        with c4:
            if st.button("🗑️", key=f"del_cap_{idx}_{anio}"):
                st.session_state[key_capital].pop(idx)
                set_dato(key_capital, st.session_state[key_capital])
                st.rerun()

c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
with c1:
    cap_nombre = st.text_input("Nombre", placeholder="Ej: Dividendos TR",
                                key=f"cap_nom_{anio}", label_visibility="collapsed")
    st.caption("Concepto")
with c2:
    cap_importe = st.number_input("Importe", min_value=0.0, max_value=50000.0,
                                   value=0.0, step=0.5, key=f"cap_imp_{anio}",
                                   label_visibility="collapsed")
    st.caption("Importe EUR")
with c3:
    cap_ret = st.number_input("Retención", min_value=0.0, max_value=10000.0,
                               value=0.0, step=0.5, key=f"cap_ret_{anio}",
                               label_visibility="collapsed")
    st.caption("Retención EUR")
with c4:
    st.write("")
    if st.button("Añadir", key=f"btn_cap_{anio}"):
        if cap_nombre and cap_importe > 0:
            st.session_state[key_capital].append((cap_nombre, cap_importe, cap_ret))
            set_dato(key_capital, st.session_state[key_capital])
            st.rerun()

total_capital = sum(v for _, v, _ in st.session_state[key_capital])
total_ret_capital = sum(r for _, _, r in st.session_state[key_capital])
st.metric("Total capital mobiliario", f"{total_capital:.2f} €")
if total_ret_capital > 0:
    st.caption(f"Retenciones ya aplicadas: {total_ret_capital:.2f} €")

st.markdown("---")

# =====================
# 5. DEDUCCIONES PERSONALES
# =====================
st.markdown("<h2 style='color:#2ABFBF'>5. Deducciones personales</h2>", unsafe_allow_html=True)
st.caption("Se guardan automáticamente para años siguientes.")

key_ded = f"irpf_deducciones"
ded = get_dato(key_ded, {})

col1, col2 = st.columns(2)
with col1:
    hijos = st.number_input("Número de hijos menores de 25 años", min_value=0, max_value=10,
                             value=int(ded.get("hijos", 0)), step=1, key="ded_hijos")
    hipoteca = st.number_input("Deducción hipoteca (si comprada antes 2013) EUR",
                                min_value=0.0, max_value=10000.0,
                                value=float(ded.get("hipoteca", 0.0)), step=1.0, key="ded_hipoteca")
with col2:
    discapacidad = st.selectbox("Discapacidad", ["Ninguna", "33%-65%", "Más del 65%"],
                                 index=["Ninguna", "33%-65%", "Más del 65%"].index(ded.get("discapacidad", "Ninguna")),
                                 key="ded_discapacidad")
    donativos = st.number_input("Donativos a ONGs EUR", min_value=0.0, max_value=5000.0,
                                 value=float(ded.get("donativos", 0.0)), step=1.0, key="ded_donativos")

nuevas_ded = {"hijos": hijos, "hipoteca": hipoteca, "discapacidad": discapacidad, "donativos": donativos}
if nuevas_ded != ded:
    set_dato(key_ded, nuevas_ded)

# Calcular deducciones
ded_total = hipoteca + donativos * 0.80
if hijos == 1:
    ded_total += 2400
elif hijos == 2:
    ded_total += 2400 + 2700
elif hijos >= 3:
    ded_total += 2400 + 2700 + 4000
if discapacidad == "33%-65%":
    ded_total += 3000
elif discapacidad == "Más del 65%":
    ded_total += 9000

st.metric("Total deducciones estimadas", f"{ded_total:.2f} €")

st.markdown("---")

# =====================
# 6. RESUMEN IRPF
# =====================
st.markdown("<h2 style='color:#2ABFBF'>6. Resumen IRPF</h2>", unsafe_allow_html=True)

base_general = rendimiento_actividad + total_ayudas
base_ahorro = total_ganancias + total_capital
base_imponible = base_general + base_ahorro - ded_total

# Cálculo orientativo del IRPF (tramos 2024)
def calcular_irpf(base):
    if base <= 0:
        return 0.0
    tramos = [(12450, 0.19), (7750, 0.24), (15000, 0.30), (24800, 0.37), (float('inf'), 0.45)]
    impuesto = 0.0
    resto = base
    for limite, tipo in tramos:
        if resto <= 0:
            break
        tramo = min(resto, limite)
        impuesto += tramo * tipo
        resto -= tramo
    return round(impuesto, 2)

irpf_bruto = calcular_irpf(base_imponible)
a_pagar = max(0.0, irpf_bruto - mod130_pagado - total_ret_capital)
a_devolver = max(0.0, mod130_pagado + total_ret_capital - irpf_bruto)

col1, col2, col3 = st.columns(3)
col1.metric("Base imponible", f"{base_imponible:.2f} €")
col2.metric("IRPF estimado", f"{irpf_bruto:.2f} €")
col3.metric("Mod.130 + Ret. ya pagados", f"{mod130_pagado + total_ret_capital:.2f} €")

if a_pagar > 0:
    st.markdown(f"<h3 style='color:red'>🔴 A INGRESAR: {a_pagar:.2f} €</h3>", unsafe_allow_html=True)
else:
    st.markdown(f"<h3 style='color:green'>🟢 A DEVOLVER: {a_devolver:.2f} €</h3>", unsafe_allow_html=True)

st.caption("⚠️ Cálculo orientativo. El resultado final puede variar según el borrador de la AEAT.")

with st.expander("📋 Casillas principales", expanded=False):
    st.code(f"""
Casilla 0180 - Rendimiento actividad económica:  {rendimiento_actividad:.2f} EUR
Casilla 0200 - Ayudas y subvenciones:            {total_ayudas:.2f} EUR
Casilla 0300 - Ganancias patrimoniales:          {total_ganancias:.2f} EUR
Casilla 0029 - Rendimientos capital mobiliario:  {total_capital:.2f} EUR
Casilla 0595 - Retenciones capital mobiliario:   {total_ret_capital:.2f} EUR
Casilla 0588 - Pagos fraccionados (Mod.130):     {mod130_pagado:.2f} EUR
Casilla 0500 - Base imponible general:           {base_general:.2f} EUR
Casilla 0510 - Base imponible ahorro:            {base_ahorro:.2f} EUR
Casilla 0545 - Cuota íntegra estimada:           {irpf_bruto:.2f} EUR
RESULTADO:                                       {"A INGRESAR " + str(a_pagar) if a_pagar > 0 else "A DEVOLVER " + str(a_devolver)} EUR
""")

st.markdown("---")

# =====================
# 7. GUÍA PASO A PASO
# =====================
st.markdown("<h2 style='color:#2ABFBF'>7. Cómo presentar la declaración</h2>", unsafe_allow_html=True)

with st.expander("📖 Ver guía completa", expanded=False):
    st.markdown("""
<h3 style='color:#FF69B4'>Cuándo presentarla</h3>

La campaña de la renta abre normalmente en **abril** y cierra a finales de **junio**.
Si el resultado es **a ingresar** y quieres domiciliar el pago, el plazo cierra antes (consulta la fecha exacta cada año en la web de la AEAT).

<h3 style='color:#FF69B4'>Paso 1 — Obtén el borrador</h3>

1. Entra en **agenciatributaria.gob.es**
2. Accede con **Cl@ve PIN**, certificado digital o número de referencia
3. Pincha en **"Renta 202X · Servicio de tramitación del borrador"**
4. Verás el borrador con los datos que la AEAT ya tiene de ti

<h3 style='color:#FF69B4'>Paso 2 — Revisa y completa</h3>

La AEAT no tendrá tus gastos deducibles como autónoma — **tienes que añadirlos tú**.
Usa los datos de esta página para rellenar las casillas que faltan.

<h3 style='color:#FF69B4'>Paso 3 — Añade los datos que faltan</h3>

- Gastos deducibles de actividad (cuota autónomo, Adeslas, facturas)
- Ayudas y subvenciones recibidas
- Ganancias de Trade Republic (usa el certificado fiscal)
- Deducciones personales

<h3 style='color:#FF69B4'>Paso 4 — Confirma y presenta</h3>

- Si el resultado te parece correcto, pulsa **"Confirmar borrador"**
- Si hay que pagar, puedes domiciliar o pagar con tarjeta
- Guarda el **justificante de presentación** en la página de Documentos

<h3 style='color:#FF69B4'>Documentos que necesitas tener a mano</h3>

- Facturas emitidas a Lola y Yordhana
- Facturas de gastos deducibles
- Certificado fiscal de Trade Republic
- Justificantes de los 4 pagos del Mod. 130
- Cualquier certificado de ayuda o subvención recibida
""", unsafe_allow_html=True)
