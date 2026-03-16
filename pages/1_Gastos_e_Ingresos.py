import streamlit as st
import calendar
from datetime import datetime
import json
from supabase import create_client

st.set_page_config(page_title="Gastos e Ingresos - Cleo Pro", layout="centered")

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

# --- SUPABASE ---
@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = get_supabase()

@st.cache_data(ttl=30)
def cargar_todos_datos():
    """Carga TODOS los datos de Supabase de una sola vez."""
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

# Cargar TODOS los datos de Supabase de una sola vez (siempre recarga)
st.session_state["_todos_datos"] = cargar_todos_datos()
_datos = st.session_state["_todos_datos"]

def get_dato_local(datos, clave, defecto):
    return datos.get(clave, defecto)

def get_dato(clave, defecto):
    """Compatibilidad — usa el dict global si está disponible."""
    if "_todos_datos" in st.session_state:
        return st.session_state["_todos_datos"].get(clave, defecto)
    try:
        r = supabase.table("datos_app").select("valor").eq("clave", clave).execute()
        if r.data:
            return json.loads(r.data[0]["valor"])
        return defecto
    except:
        return defecto

def get_todos_sobres():
    datos = st.session_state.get("_todos_datos", {})
    return {k: float(v) for k, v in datos.items() if k.startswith("sobre_anual_")}

def get_valor_historico(prefijo, mi, anio, defecto):
    datos = st.session_state.get("_todos_datos", {})
    clave = f"{prefijo}_{mi}_{anio}"
    if clave in datos:
        return float(datos[clave]), clave
    m, a = mi, anio
    for _ in range(24):
        m -= 1
        if m == 0:
            m = 12
            a -= 1
        clave_ant = f"{prefijo}_{m}_{a}"
        if clave_ant in datos:
            return float(datos[clave_ant]), clave
    return defecto, clave

def get_sobre_anual(nombre, mi, anio, defecto, todos):
    """Busca el valor del sobre para este mes, si no hay busca el último mes anterior con dato."""
    clave = f"sobre_anual_{nombre.replace(' ','_')}_{mi}_{anio}"
    if clave in todos:
        return todos[clave], clave
    # Buscar hacia atrás hasta 24 meses en el dict ya cargado
    m, a = mi, anio
    for _ in range(24):
        m -= 1
        if m == 0:
            m = 12
            a -= 1
        clave_ant = f"sobre_anual_{nombre.replace(' ','_')}_{m}_{a}"
        if clave_ant in todos:
            return todos[clave_ant], clave
    return defecto, clave

def set_dato(clave, valor):
    try:
        supabase.table("datos_app").upsert({"clave": clave, "valor": json.dumps(valor)}).execute()
        # Actualizar cache local
        if "_todos_datos" in st.session_state:
            st.session_state["_todos_datos"][clave] = valor
        cargar_todos_datos.clear()
    except:
        pass

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

# --- SELECTOR MES Y AÑO ---
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

    # Cargar valor guardado en Supabase
    valor_guardado = int(get_dato(key_dias, num_dias_defecto))

    st.markdown(f"**{cliente}** · {datos['h']}h/dia · {datos['t']} EUR/h")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        num_dias = st.number_input(
            f"Dias trabajados {cliente}",
            min_value=0, max_value=31,
            value=valor_guardado, step=1,
            key=key_dias,
            label_visibility="collapsed"
        )
        st.caption(f"Dias segun calendario: {num_dias_defecto}")
        if num_dias != valor_guardado:
            set_dato(key_dias, num_dias)
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

# Otros ingresos
key_ing_extra = f"ingresos_extra_{mi}_{anio}"
if key_ing_extra not in st.session_state:
    st.session_state[key_ing_extra] = get_dato(key_ing_extra, [])

if st.session_state[key_ing_extra]:
    st.markdown("*Otros ingresos añadidos:*")
    for idx, (nombre_i, importe_i) in enumerate(st.session_state[key_ing_extra]):
        c1, c2, c3 = st.columns([2, 1, 0.5])
        with c1:
            st.write(nombre_i)
        with c2:
            st.write(f"{importe_i:.2f} EUR")
        with c3:
            if st.button("X", key=f"del_ing_{idx}_{mi}_{anio}"):
                st.session_state[key_ing_extra].pop(idx)
                set_dato(key_ing_extra, st.session_state[key_ing_extra])
                st.rerun()

c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    ing_nombre = st.text_input("Otros ingresos", placeholder="Otros ingresos",
                                key=f"ing_nombre_{mi}_{anio}", label_visibility="collapsed")
    st.caption("Otros ingresos")
with c2:
    ing_importe = st.number_input("Importe ingreso EUR", min_value=0.0, max_value=5000.0,
                                   value=0.0, step=1.0, key=f"ing_extra_importe_{mi}_{anio}",
                                   label_visibility="collapsed")
    st.caption("Importe EUR")
with c3:
    st.write("")
    if st.button("Añadir ingreso", key=f"btn_add_ing_{mi}_{anio}"):
        if ing_nombre and ing_importe > 0:
            st.session_state[key_ing_extra].append((ing_nombre, ing_importe))
            set_dato(key_ing_extra, st.session_state[key_ing_extra])
            st.rerun()

ingresos_extra_total = sum(v for _, v in st.session_state[key_ing_extra])
total_ingresos = sum(ingresos_reales.values()) + ingresos_extra_total
st.metric("Total ingresos", f"{total_ingresos:.2f} EUR")

st.divider()

# --- SECCION 2: TRADE REPUBLIC ---
col_m, col_a, col_r = st.columns([2, 1, 1])
with col_m:
    mes_nombre = st.selectbox("Mes", MESES, index=MESES.index(mes_nombre), key="mes__tr", label_visibility="collapsed")
with col_a:
    anio = st.number_input("Año", min_value=2024, max_value=2035, value=int(anio), step=1, key="anio__tr", label_visibility="collapsed")
with col_r:
    if st.button("🔄", key="refresh_tr_1", help="Refrescar"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
mi = MESES.index(mes_nombre) + 1

st.subheader("Trade Republic")
st.caption("Aparta este dinero nada mas cobrar. No lo toques.")


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
    "Mod. 130 (trimestral)": 67.00,
}

AHORRO_INVERSION = {
    "Jubilacion (acciones)": 50.00,
}

total_sobres = 0.0
sobres_vals = {}

st.markdown("**Pagos anuales** - Ahorra mensualmente para no sufrir el golpe")
todos_sobres = get_todos_sobres()
for i, (nombre, (mensual_def, anual_def)) in enumerate(SOBRES_ANUALES.items()):
    # Clave única por nombre + mes + año → busca hacia atrás si no hay dato
    anual_guardado, clave_anual = get_sobre_anual(nombre, mi, anio, anual_def, todos_sobres)

    # Mes de pago guardado en Supabase
    clave_mes_pago = f"sobre_mes_pago_{nombre.replace(' ','_')}"
    mes_pago_guardado = int(get_dato(clave_mes_pago, 1))

    with st.expander(f"**{nombre}**", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            val_anual = st.number_input(
                f"Al año (EUR)", min_value=0.0, max_value=2000.0,
                value=anual_guardado, step=0.5, key=f"anual_{i}_{mi}_{anio}",
            )
            if val_anual != anual_guardado:
                supabase.table("datos_app").upsert({
                    "clave": clave_anual,
                    "valor": str(val_anual)
                }).execute()
            with c2:
                val_mes = round(val_anual / 12, 2)
            st.markdown("**Al mes**")
            st.markdown(f"### {val_mes:.2f} €")
        with c3:
            meses_str = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
            clave_anio_pago = f"sobre_anio_pago_{nombre.replace(' ','_')}"
            anio_pago_guardado = int(get_dato(clave_anio_pago, int(anio)))
            cp1, cp2 = st.columns(2)
            with cp1:
                mes_pago = st.selectbox("Mes", list(range(1,13)),
                                         index=mes_pago_guardado-1,
                                         format_func=lambda x: meses_str[x-1],
                                         key=f"mes_pago_{i}_{mi}_{anio}")
            with cp2:
                anio_pago = st.number_input("Año", min_value=2024, max_value=2040,
                                             value=anio_pago_guardado,
                                             step=1, key=f"anio_pago_{i}_{mi}_{anio}")
            if mes_pago != mes_pago_guardado:
                supabase.table("datos_app").upsert({"clave": clave_mes_pago, "valor": str(mes_pago)}).execute()
            if anio_pago != anio_pago_guardado:
                supabase.table("datos_app").upsert({"clave": clave_anio_pago, "valor": str(anio_pago)}).execute()
        # Aviso mes anterior al pago
        mes_aviso = mes_pago - 1 if mes_pago > 1 else 12
        anio_aviso = anio_pago if mes_pago > 1 else anio_pago - 1
        if mi == mes_aviso and int(anio) == anio_aviso:
            st.warning(f"⚠️ El próximo mes toca pagar **{nombre}**: {val_anual:.2f} EUR ({meses_str[mes_pago-1]} {anio_pago})")
    sobres_vals[nombre] = val_mes
    total_sobres += val_mes

total_anuales = sum(sobres_vals[k] for k in SOBRES_ANUALES)

key_tr_extra = f"tr_extra_{mi}_{anio}"
if key_tr_extra not in st.session_state:
    st.session_state[key_tr_extra] = get_dato(key_tr_extra, [])

if st.session_state[key_tr_extra]:
    for idx, item in enumerate(st.session_state[key_tr_extra]):
        # Compatibilidad: formato antiguo (nombre, importe) o nuevo (nombre, mensualizado, periodo, total, mes_pago)
        if len(item) == 2:
            nombre_t, importe_t = item
            periodo_t, total_t, mes_pago_t = "Mensual", importe_t, None
        else:
            nombre_t, importe_t, periodo_t, total_t, mes_pago_t = item
        c1, c2, c3 = st.columns([3, 1.5, 0.5])
        with c1:
            st.write(f"**{nombre_t}** · {periodo_t} · {total_t:.2f} EUR")
        with c2:
            st.write(f"{importe_t:.2f} EUR/mes")
        with c3:
            if st.button("X", key=f"del_tr_{idx}_{mi}_{anio}"):
                st.session_state[key_tr_extra].pop(idx)
                set_dato(key_tr_extra, st.session_state[key_tr_extra])
                st.rerun()
        # Aviso el mes anterior al pago
        if mes_pago_t:
            mes_aviso = mes_pago_t - 1 if mes_pago_t > 1 else 12
            if mi == mes_aviso:
                meses_str = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
                st.warning(f"⚠️ El próximo mes toca pagar **{nombre_t}**: {total_t:.2f} EUR ({meses_str[mes_pago_t-1]})")
        total_sobres += importe_t

total_anuales = total_sobres
st.info(f"Total pagos anuales: {total_anuales:.2f} EUR/mes · Al año: {total_anuales*12:.2f} EUR")

if st.button("➕ Añadir nuevo sobre", key=f"btn_show_sobre_{mi}_{anio}"):
    st.session_state[f"show_nuevo_sobre_{mi}_{anio}"] = True

if st.session_state.get(f"show_nuevo_sobre_{mi}_{anio}", False):
    st.markdown("**Nuevo sobre:**")
    c1, c2 = st.columns(2)
    with c1:
        tr_nombre = st.text_input("Nombre del sobre", placeholder="Ej: Seguro hogar",
                                   key=f"tr_nombre_{mi}_{anio}")
    with c2:
        tr_periodo = st.selectbox("Periodicidad", ["Mensual", "Trimestral", "Semestral", "Anual"],
                                   key=f"tr_periodo_{mi}_{anio}")
    c3, c4 = st.columns(2)
    with c3:
        tr_importe_total = st.number_input("Importe total del periodo (EUR)",
                                            min_value=0.0, max_value=5000.0,
                                            value=0.0, step=0.5, key=f"tr_importe_{mi}_{anio}")
    with c4:
        tr_mes_pago = st.selectbox("Mes de pago", list(range(1, 13)),
                                    format_func=lambda x: ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"][x-1],
                                    key=f"tr_mes_pago_{mi}_{anio}")

    divisor = {"Mensual": 1, "Trimestral": 3, "Semestral": 6, "Anual": 12}[tr_periodo]
    tr_mensualizado = round(tr_importe_total / divisor, 2)
    if tr_importe_total > 0:
        st.caption(f"Apartando {tr_mensualizado:.2f} EUR/mes")

    c5, c6 = st.columns(2)
    with c5:
        if st.button("💾 Guardar sobre", key=f"btn_add_tr_{mi}_{anio}"):
            if tr_nombre and tr_importe_total > 0:
                nuevo = (tr_nombre, tr_mensualizado, tr_periodo, tr_importe_total, tr_mes_pago)
                st.session_state[key_tr_extra].append(nuevo)
                set_dato(key_tr_extra, st.session_state[key_tr_extra])
                st.session_state[f"show_nuevo_sobre_{mi}_{anio}"] = False
                st.rerun()
    with c6:
        if st.button("Cancelar", key=f"btn_cancel_sobre_{mi}_{anio}"):
            st.session_state[f"show_nuevo_sobre_{mi}_{anio}"] = False
            st.rerun()

st.markdown("---")
st.markdown("**Mod. 130 - Pago trimestral**")
st.caption("Se paga en Abril, Julio, Octubre y Enero. Aparta 1/3 cada mes.")

# Trimestre completo del mes actual
trimestre_actual = (mi - 1) // 3 + 1
meses_trimestre = {1: [1,2,3], 2: [4,5,6], 3: [7,8,9], 4: [10,11,12]}[trimestre_actual]
CLIS_130 = {"Lola": {"t": 14.0, "h": 4.0, "w": [2]}, "Yordhana": {"t": 14.0, "h": 4.0, "w": [3]}}

# Meses válidos: desde marzo 2026 (alta en SS)
MES_ALTA, ANIO_ALTA = 3, 2026
meses_validos = [m for m in meses_trimestre
                 if (int(anio) > ANIO_ALTA) or (int(anio) == ANIO_ALTA and m >= MES_ALTA)]
n_meses = len(meses_validos) if meses_validos else 1

# --- REAL: ingresos reales + facturas gastos del trimestre + autónomo ---
ingresos_real = 0.0
for cn, c in CLIS_130.items():
    for m in meses_validos:
        num = get_dato(f"dias_{cn}_{m}_{anio}", None)
        num_dias = int(num) if num is not None else len(calcular_dias_mes(c, int(anio), m))
        ingresos_real += num_dias * c["h"] * c["t"]

# Facturas gastos del trimestre desde Supabase
try:
    r = supabase.table("facturas_gastos").select("importe").eq(
        "trimestre", f"T{trimestre_actual}_{int(anio)}").execute()
    facturas_gastos_trim = sum(float(f["importe"]) for f in r.data) if r.data else 0.0
except:
    facturas_gastos_trim = 0.0

cuota_real = n_meses * 88.72
gastos_real = cuota_real + facturas_gastos_trim
beneficio_real = max(0.0, ingresos_real - gastos_real)
mod130_real = round(beneficio_real * 0.20, 2)
mod130_mensual = round(mod130_real / 3, 2)

st.markdown(f"**Real Q{trimestre_actual} {int(anio)}** · Ingresos: {ingresos_real:.2f}€ · Gastos: {gastos_real:.2f}€ · Beneficio: {beneficio_real:.2f}€")
st.caption(f"Autónomo {cuota_real:.2f}€ + Facturas gastos {facturas_gastos_trim:.2f}€ ({n_meses} mes/es)")
st.metric("💰 Mod. 130 a pagar", f"{mod130_real:.2f} €")
st.metric("📅 Aparta este mes (1/3)", f"{mod130_mensual:.2f} €")

meses_aviso_130 = [3, 6, 9, 12]
if mi in meses_aviso_130:
    st.warning(f"⚠️ El próximo mes toca pagar el Mod. 130: {mod130_real:.2f} EUR")

sobres_vals["Mod. 130"] = mod130_mensual
total_sobres += mod130_mensual
total_mensuales = mod130_mensual
st.caption(f"Total Mod. 130 mensualizado: {mod130_mensual:.2f} EUR/mes")


st.markdown("---")
st.markdown("**Ahorro inversión**")
st.caption("Dinero para invertir en acciones pensando en la jubilación.")
total_ahorro = 0.0
for i, (nombre, importe) in enumerate(AHORRO_INVERSION.items()):
    val_guardado_ahorro, clave_ahorro = get_valor_historico(f"ahorro_{nombre.replace(' ','_')}", mi, anio, importe)
    val = st.number_input(nombre, min_value=0.0, max_value=1000.0,
                          value=val_guardado_ahorro, step=0.5, key=f"ahorro_{i}_{mi}_{anio}")
    if val != val_guardado_ahorro:
        set_dato(clave_ahorro, val)
    total_ahorro += val
    st.caption(f"{val:.2f} EUR/mes")
total_sobres += total_ahorro
st.info(f"Total ahorro inversión: {total_ahorro:.2f} EUR/mes")

st.markdown("---")
st.write(f"**Total Trade Republic: {total_sobres:.2f} EUR**")

st.divider()

# --- SECCION 3: GASTOS ---
col_m, col_a, col_r = st.columns([2, 1, 1])
with col_m:
    mes_nombre = st.selectbox("Mes", MESES, index=MESES.index(mes_nombre), key="mes__gastos", label_visibility="collapsed")
with col_a:
    anio = st.number_input("Año", min_value=2024, max_value=2035, value=int(anio), step=1, key="anio__gastos", label_visibility="collapsed")
with col_r:
    if st.button("🔄", key="refresh_gastos", help="Refrescar"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
mi = MESES.index(mes_nombre) + 1

st.subheader("Gastos del mes")


tab_bbva, tab_efectivo = st.tabs(["BBVA", "Gastos Efectivo"])

GASTOS_BBVA = {
    "Cuota Autonomo":          88.72,
    "Adeslas (seguro medico)": 30.27,
    "Movil Mama":              29.90,
    "Tinta HP":                 7.99,
    "Masmovil":                58.90,
}

with tab_bbva:
    total_fijos = 0.0

    # Mod. 130 automático en meses de pago — calculado directamente
    ALTA_MES_130 = 3
    ALTA_ANIO_130 = 2026
    CLIS_FACTURA = {"Lola": {"t": 14.0, "h": 4.0, "w": [2]}, "Yordhana": {"t": 14.0, "h": 4.0, "w": [3]}}
    meses_pago_130 = [1, 4, 7, 10]
    if mi in meses_pago_130:
        t_anterior = {1: 4, 4: 1, 7: 2, 10: 3}[mi]
        anio_t = int(anio) - 1 if mi == 1 else int(anio)
        meses_trim_ant = {1: [1,2,3], 2: [4,5,6], 3: [7,8,9], 4: [10,11,12]}[t_anterior]
        # Filtrar por fecha de alta
        if anio_t == ALTA_ANIO_130:
            meses_trim_ant = [m for m in meses_trim_ant if m >= ALTA_MES_130]
        elif anio_t < ALTA_ANIO_130:
            meses_trim_ant = []

        if meses_trim_ant:
            # Calcular ingresos del trimestre
            ingresos_130 = 0.0
            for cn, c in CLIS_FACTURA.items():
                for m in meses_trim_ant:
                    num = get_dato_local(_datos, f"dias_{cn}_{m}_{anio_t}", None)
                    if num is None:
                        num_dias = len(calcular_dias_mes(c, anio_t, m))
                    else:
                        num_dias = int(num)
                    ingresos_130 += num_dias * c["h"] * c["t"]
                    lineas = get_dato_local(_datos, f"lineas_extra_{cn}_{m}_{anio_t}", [])
                    for _, precio in lineas:
                        ingresos_130 += precio

            # Calcular cuota autónomo del trimestre
            cuota_130 = len(meses_trim_ant) * 88.72

            # Gastos deducibles = cuota autónomo + facturas subidas del trimestre
            try:
                r = supabase.table("facturas_gastos").select("importe").eq(
                    "trimestre", f"T{t_anterior}_{anio_t}").execute()
                facturas_130 = sum(float(f["importe"]) for f in r.data) if r.data else 0.0
            except:
                facturas_130 = 0.0

            gastos_130 = cuota_130 + facturas_130
            beneficio_130 = ingresos_130 - gastos_130

            # Restar pagos anteriores del año
            pagos_ant = 0.0
            for t in range(1, t_anterior):
                if get_dato_local(_datos, f"mod130_pagado_t{t}_{anio_t}", False):
                    pagos_ant += float(get_dato_local(_datos, f"mod130_importe_t{t}_{anio_t}", 0.0))

            importe_130 = max(0.0, beneficio_130 * 0.20 - pagos_ant)
            ya_pagado = get_dato_local(_datos, f"mod130_pagado_t{t_anterior}_{anio_t}", False)

            nombre_130 = f"Mod. 130 T{t_anterior} ({anio_t})"
            c1, c2 = st.columns([2, 1])
            with c1:
                st.write(f"{'✅' if ya_pagado else '🔴'} {nombre_130}")
            with c2:
                st.number_input(f"EUR {nombre_130}", min_value=0.0, max_value=5000.0,
                                value=importe_130, step=0.5, label_visibility="collapsed",
                                key=f"mod130_bbva_{mi}_{anio}", disabled=True)
            total_fijos += importe_130
            if not ya_pagado and importe_130 > 0:
                st.warning(f"⚠️ Este mes toca pagar el Mod. 130: {importe_130:.2f} EUR — Ve a Modelo 130 para presentarlo")

    # Pagos anuales de Trade Republic que tocan este mes
    for nombre_sobre, (mensual_def, anual_def) in SOBRES_ANUALES.items():
        clave_mp = f"sobre_mes_pago_{nombre_sobre.replace(' ','_')}"
        mes_pago_sobre = int(get_dato_local(_datos, clave_mp, 1))
        if mi == mes_pago_sobre:
            # Leer importe anual guardado
            anual_guardado, _ = get_sobre_anual(nombre_sobre, mi, anio, anual_def, get_todos_sobres())
            nombre_bbva = f"TR - {nombre_sobre} (pago anual)"
            c1, c2 = st.columns([2, 1])
            with c1:
                st.write(f"💰 {nombre_bbva}")
            with c2:
                st.number_input(f"EUR {nombre_bbva}", min_value=0.0, max_value=5000.0,
                                value=float(anual_guardado), step=0.5,
                                label_visibility="collapsed",
                                key=f"sobre_bbva_{nombre_sobre}_{mi}_{anio}",
                                disabled=True)
            total_fijos += float(anual_guardado)
            st.info(f"💰 Este mes toca pagar **{nombre_sobre}**: {anual_guardado:.2f} EUR (ahorrado en Trade Republic)")

    for gasto, importe in GASTOS_BBVA.items():
        val_guardado_bbva, clave_bbva = get_valor_historico(f"bbva_{gasto.replace(' ','_')}", mi, anio, importe)
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write(gasto)
        with c2:
            val = st.number_input(f"EUR {gasto}", min_value=0.0, max_value=2000.0,
                                   value=val_guardado_bbva, step=0.5, label_visibility="collapsed",
                                   key=f"gf_{gasto}_{mi}_{anio}")
            if val != val_guardado_bbva:
                set_dato(clave_bbva, val)
            total_fijos += val

    key_bbva_extra = f"bbva_extra_{mi}_{anio}"
    if key_bbva_extra not in st.session_state:
        st.session_state[key_bbva_extra] = get_dato(key_bbva_extra, [])

    if st.session_state[key_bbva_extra]:
        st.markdown("*Gastos añadidos:*")
        for idx, (nombre_b, importe_b) in enumerate(st.session_state[key_bbva_extra]):
            c1, c2, c3 = st.columns([2, 1, 0.5])
            with c1:
                st.write(nombre_b)
            with c2:
                st.write(f"{importe_b:.2f} EUR")
            with c3:
                if st.button("X", key=f"del_bbva_{idx}_{mi}_{anio}"):
                    st.session_state[key_bbva_extra].pop(idx)
                    set_dato(key_bbva_extra, st.session_state[key_bbva_extra])
                    st.rerun()
            total_fijos += importe_b

    st.markdown("---")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        bbva_nombre = st.text_input("Nombre gasto BBVA", placeholder="Ej: Recibo luz",
                                     key=f"bbva_nombre_{mi}_{anio}", label_visibility="collapsed")
        st.caption("Nombre del gasto")
    with c2:
        bbva_importe = st.number_input("Importe BBVA EUR", min_value=0.0, max_value=2000.0,
                                        value=0.0, step=0.5, key=f"bbva_importe_{mi}_{anio}",
                                        label_visibility="collapsed")
        st.caption("Importe EUR")
    with c3:
        st.write("")
        if st.button("Añadir gasto BBVA", key=f"btn_add_bbva_{mi}_{anio}"):
            if bbva_nombre and bbva_importe > 0:
                st.session_state[key_bbva_extra].append((bbva_nombre, bbva_importe))
                set_dato(key_bbva_extra, st.session_state[key_bbva_extra])
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
        val_guardado_ef, clave_ef = get_valor_historico(f"efectivo_{gasto.replace(' ','_')}", mi, anio, importe)
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write(gasto)
        with c2:
            val = st.number_input(f"EUR extra {gasto}", min_value=0.0, max_value=2000.0,
                                   value=val_guardado_ef, step=1.0, label_visibility="collapsed",
                                   key=f"ge_{gasto}_{mi}_{anio}")
            if val != val_guardado_ef:
                set_dato(clave_ef, val)
            total_extras += val

    key_ge_extra = f"gastos_extra_{mi}_{anio}"
    if key_ge_extra not in st.session_state:
        st.session_state[key_ge_extra] = get_dato(key_ge_extra, [])

    if st.session_state[key_ge_extra]:
        st.markdown("*Gastos añadidos:*")
        for idx, (nombre_g, importe_g) in enumerate(st.session_state[key_ge_extra]):
            c1, c2, c3 = st.columns([2, 1, 0.5])
            with c1:
                st.write(nombre_g)
            with c2:
                st.write(f"{importe_g:.2f} EUR")
            with c3:
                if st.button("X", key=f"del_extra_{idx}_{mi}_{anio}"):
                    st.session_state[key_ge_extra].pop(idx)
                    set_dato(key_ge_extra, st.session_state[key_ge_extra])
                    st.rerun()
            total_extras += importe_g

    st.markdown("---")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        extra_nombre = st.text_input("Nombre del gasto", placeholder="Ej: Farmacia",
                                      key=f"ge_nombre_{mi}_{anio}", label_visibility="collapsed")
        st.caption("Nombre del gasto")
    with c2:
        extra_importe = st.number_input("Importe EUR", min_value=0.0, max_value=2000.0,
                                         value=0.0, step=1.0, key=f"ge_libre_{mi}_{anio}",
                                         label_visibility="collapsed")
        st.caption("Importe EUR")
    with c3:
        st.write("")
        if st.button("Añadir", key=f"btn_add_{mi}_{anio}"):
            if extra_nombre and extra_importe > 0:
                st.session_state[key_ge_extra].append((extra_nombre, extra_importe))
                set_dato(key_ge_extra, st.session_state[key_ge_extra])
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
    for nombre_i, importe_i in st.session_state[key_ing_extra]:
        st.write(f"- {nombre_i}: {importe_i:.2f} EUR")
    st.write(f"**= Total ingresos: {total_ingresos:.2f} EUR**")
    st.markdown("---")
    st.markdown("**Trade Republic:**")
    st.write(f"- Pagos anuales: {total_anuales:.2f} EUR/mes")
    st.write(f"- Mod. 130 (mensualizado): {total_mensuales:.2f} EUR")
    st.write(f"- Ahorro inversion: {total_ahorro:.2f} EUR")
    for nombre_t, importe_t in st.session_state[key_tr_extra]:
        st.write(f"- {nombre_t}: {importe_t:.2f} EUR")
    st.write(f"**= Total Trade Republic: {total_sobres:.2f} EUR**")
    st.markdown("---")
    st.markdown("**BBVA:**")
    # Pagos anuales de Trade Republic que tocan este mes
    for nombre_sobre, (mensual_def, anual_def) in SOBRES_ANUALES.items():
        clave_mp = f"sobre_mes_pago_{nombre_sobre.replace(' ','_')}"
        mes_pago_sobre = int(get_dato_local(_datos, clave_mp, 1))
        if mi == mes_pago_sobre:
            # Leer importe anual guardado
            anual_guardado, _ = get_sobre_anual(nombre_sobre, mi, anio, anual_def, get_todos_sobres())
            nombre_bbva = f"TR - {nombre_sobre} (pago anual)"
            c1, c2 = st.columns([2, 1])
            with c1:
                st.write(f"💰 {nombre_bbva}")
            with c2:
                st.number_input(f"EUR {nombre_bbva}", min_value=0.0, max_value=5000.0,
                                value=float(anual_guardado), step=0.5,
                                label_visibility="collapsed",
                                key=f"sobre_bbva_{nombre_sobre}_{mi}_{anio}",
                                disabled=True)
            total_fijos += float(anual_guardado)
            st.info(f"💰 Este mes toca pagar **{nombre_sobre}**: {anual_guardado:.2f} EUR (ahorrado en Trade Republic)")

    for gasto, importe in GASTOS_BBVA.items():
        st.write(f"- {gasto}: {importe:.2f} EUR")
    for nombre_b, importe_b in st.session_state[key_bbva_extra]:
        st.write(f"- {nombre_b}: {importe_b:.2f} EUR")
    st.write(f"**= Total BBVA: {total_fijos:.2f} EUR**")
    st.markdown("---")
    st.markdown("**Gastos Efectivo:**")
    for gasto, importe in GASTOS_EXTRA_DEF.items():
        st.write(f"- {gasto}: {importe:.2f} EUR")
    for nombre_g, importe_g in st.session_state[key_ge_extra]:
        st.write(f"- {nombre_g}: {importe_g:.2f} EUR")
    st.write(f"**= Total Efectivo: {total_extras:.2f} EUR**")
    st.markdown("---")
    st.write(f"**Ingresos:** {total_ingresos:.2f} EUR")
    st.write(f"**- Trade Republic:** -{total_sobres:.2f} EUR")
    st.write(f"**- BBVA:** -{total_fijos:.2f} EUR")
    st.write(f"**- Efectivo:** -{total_extras:.2f} EUR")
    st.write(f"**= Dinero libre: {neto_real:.2f} EUR**")
