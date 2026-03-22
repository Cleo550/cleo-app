import streamlit as st
import json
from datetime import datetime, date, timedelta
import calendar
import math
import sqlite3 as sq3
import tempfile
import os
from supabase import create_client
from calculadora import mostrar_calculadora

st.set_page_config(page_title="Libro de Cuentas - Cleo Pro", layout="centered")

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
mostrar_calculadora()

@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = get_supabase()

# ─────────────────────────────────────────────
# ESTRUCTURA DE CUENTAS
# ─────────────────────────────────────────────
CUENTAS_CONFIG = {
    "Efectivo": {
        "emoji": "💵",
        "subcuentas": ["Cash", "Sueldo limpieza", "Supermercados", "Tabaco", "Terapeuta", "Gasolina"]
    },
    "BBVA": {
        "emoji": "🏦",
        "subcuentas": ["En la Cuenta", "Mi Hucha", "Sueldo Limpieza", "Autónomo",
                       "Adeslas", "Tinta HP", "MásMovil", "Móvil Mama",
                       "Ingresos Laura", "Financiación compras"]
    },
    "Ahorros": {
        "emoji": "🐷",
        "subcuentas": ["Trade Republic", "Intereses 2%", "Hacienda",
                       "Imp. Circulación", "Amazon Prime", "Seguro RC",
                       "Seguro Coche", "Seguro Decesos", "ITV", "Plex",
                       "Regalos", "Jubilación"]
    },
    "OpenBanc": {
        "emoji": "🏛️",
        "subcuentas": ["En la cuenta"]
    },
    "OpenBanc Laura & Cleo": {
        "emoji": "🏛️",
        "subcuentas": ["Openbanc Laura & Cleo", "Ingresos Laura nuestra cuenta"]
    },
}

TODAS_CUENTAS = list(CUENTAS_CONFIG.keys())

CATEGORIAS_GASTO = [
    "Compras casa", "Salud", "Autónomo", "Tele/Móvil/Internet",
    "Transporte/Vehículo", "Tabaco", "Regalos", "Gastos Cleo",
    "Restaurante/Bar", "Ocio", "Ropa", "Farmacia", "Veterinario",
    "Seguros", "Hogar", "Otros"
]
CATEGORIAS_INGRESO = [
    "Sueldo Limpieza", "Ania", "Lola", "Yordhana",
    "Apuestas", "Intereses Trade Republic", "Regalo", "Otros"
]

MESES_ES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

COLORES_CHART = ["#FF6B6B","#FF9F43","#FECA57","#48DBB4","#54A0FF",
                 "#5F27CD","#FF69B4","#2ABFBF","#A29BFE","#FD79A8",
                 "#00B894","#E17055","#74B9FF","#FDCB6E","#6C5CE7"]

# ─────────────────────────────────────────────
# TRANSACCIONES REPETIDAS
# ─────────────────────────────────────────────
REPETIDAS = [
    {"nombre": "Lola",             "tipo": "ingreso", "importe": 168.0,  "cuenta": "Efectivo", "subcuenta": "Sueldo limpieza",  "categoria": "Sueldo Limpieza",     "dia": 1,  "periodo": "mensual"},
    {"nombre": "Yordhana",         "tipo": "ingreso", "importe": 224.0,  "cuenta": "Efectivo", "subcuenta": "Sueldo limpieza",  "categoria": "Sueldo Limpieza",     "dia": 2,  "periodo": "mensual"},
    {"nombre": "Ania",             "tipo": "ingreso", "importe": 650.0,  "cuenta": "Efectivo", "subcuenta": "Sueldo limpieza",  "categoria": "Sueldo Limpieza",     "dia": 6,  "periodo": "mensual"},
    {"nombre": "Adeslas",          "tipo": "gasto",   "importe": 30.27,  "cuenta": "BBVA",     "subcuenta": "Adeslas",          "categoria": "Salud",               "dia": 2,  "periodo": "mensual"},
    {"nombre": "MásMovil",         "tipo": "gasto",   "importe": 58.90,  "cuenta": "BBVA",     "subcuenta": "MásMovil",         "categoria": "Tele/Móvil/Internet", "dia": 2,  "periodo": "mensual"},
    {"nombre": "Móvil Mama",       "tipo": "gasto",   "importe": 29.90,  "cuenta": "BBVA",     "subcuenta": "Móvil Mama",       "categoria": "Regalos",             "dia": 16, "periodo": "mensual"},
    {"nombre": "Tinta HP",         "tipo": "gasto",   "importe": 7.99,   "cuenta": "BBVA",     "subcuenta": "Tinta HP",         "categoria": "Autónomo",            "dia": 24, "periodo": "mensual"},
    {"nombre": "Digi",             "tipo": "gasto",   "importe": 3.00,   "cuenta": "OpenBanc", "subcuenta": "En la cuenta",     "categoria": "Tele/Móvil/Internet", "dia": 26, "periodo": "mensual"},
    {"nombre": "Jubilación",       "tipo": "transf",  "importe": 50.00,  "cuenta": "Ahorros",  "subcuenta": "Jubilación",       "categoria": "Traspasos",           "dia": 2,  "periodo": "mensual"},
    {"nombre": "Amazon Prime",     "tipo": "gasto",   "importe": 49.90,  "cuenta": "Ahorros",  "subcuenta": "Amazon Prime",     "categoria": "Ocio",                "dia": 13, "periodo": "anual",    "mes": 5},
    {"nombre": "Imp. Circulación", "tipo": "gasto",   "importe": 129.0,  "cuenta": "Ahorros",  "subcuenta": "Imp. Circulación", "categoria": "Transporte/Vehículo", "dia": 1,  "periodo": "anual",    "mes": 5},
    {"nombre": "Seguro Coche",     "tipo": "gasto",   "importe": 149.30, "cuenta": "Ahorros",  "subcuenta": "Seguro Coche",     "categoria": "Seguros",             "dia": 1,  "periodo": "semestral","mes": 7},
    {"nombre": "Plex",             "tipo": "gasto",   "importe": 60.00,  "cuenta": "Ahorros",  "subcuenta": "Plex",             "categoria": "Tele/Móvil/Internet", "dia": 1,  "periodo": "anual",    "mes": 11},
    {"nombre": "Seguro Decesos",   "tipo": "gasto",   "importe": 66.47,  "cuenta": "Ahorros",  "subcuenta": "Seguro Decesos",   "categoria": "Seguros",             "dia": 12, "periodo": "anual",    "mes": 1},
    {"nombre": "Seguro RC",        "tipo": "gasto",   "importe": 82.72,  "cuenta": "Ahorros",  "subcuenta": "Seguro RC",        "categoria": "Autónomo",            "dia": 1,  "periodo": "anual",    "mes": 3},
]

# ─────────────────────────────────────────────
# SUPABASE
# ─────────────────────────────────────────────
@st.cache_data(ttl=15)
def cargar_transacciones():
    try:
        r = supabase.table("libro_cuentas").select("*").order("fecha", desc=True).order("id", desc=True).execute()
        return r.data or []
    except:
        return []

def guardar_tx(fecha, tipo, cuenta, subcuenta, categoria, descripcion, importe, auto=False):
    try:
        supabase.table("libro_cuentas").insert({
            "fecha": str(fecha),
            "tipo": tipo,
            "cuenta": cuenta,
            "subcuenta": subcuenta,
            "categoria": categoria,
            "descripcion": descripcion,
            "importe": float(importe),
            "auto": auto
        }).execute()
        cargar_transacciones.clear()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def borrar_tx(id_tx):
    try:
        supabase.table("libro_cuentas").delete().eq("id", id_tx).execute()
        cargar_transacciones.clear()
    except:
        pass

def get_importe_repetida(nombre):
    """Lee el importe guardado para una repetida. Si no hay, devuelve None."""
    try:
        clave = f"rep_importe_{nombre.replace(' ','_')}"
        r = supabase.table("datos_app").select("valor").eq("clave", clave).execute()
        if r.data:
            import json as _json
            return float(_json.loads(r.data[0]["valor"]))
    except:
        pass
    return None

def set_importe_repetida(nombre, importe):
    """Guarda el importe personalizado de una repetida en datos_app."""
    try:
        import json as _json
        clave = f"rep_importe_{nombre.replace(' ','_')}"
        supabase.table("datos_app").upsert(
            {"clave": clave, "valor": _json.dumps(float(importe))}
        ).execute()
    except:
        pass

def get_dia_mes_repetida(nombre, dia_def, mes_def):
    """Lee el día y mes guardados para una repetida."""
    try:
        import json as _json
        clave = f"rep_diames_{nombre.replace(' ','_')}"
        r = supabase.table("datos_app").select("valor").eq("clave", clave).execute()
        if r.data:
            v = _json.loads(r.data[0]["valor"])
            return int(v["dia"]), int(v["mes"])
    except:
        pass
    return dia_def, mes_def

def set_dia_mes_repetida(nombre, dia, mes):
    """Guarda el día y mes personalizados de una repetida."""
    try:
        import json as _json
        clave = f"rep_diames_{nombre.replace(' ','_')}"
        supabase.table("datos_app").upsert(
            {"clave": clave, "valor": _json.dumps({"dia": dia, "mes": mes})}
        ).execute()
    except:
        pass

# ─────────────────────────────────────────────
# APLICAR REPETIDAS AUTOMÁTICAMENTE
# ─────────────────────────────────────────────
def aplicar_repetidas():
    hoy = date.today()
    mes_actual = hoy.month
    anio_actual = hoy.year
    prefijo = f"{anio_actual}-{mes_actual:02d}"

    txs = cargar_transacciones()
    nombres_auto_mes = {t["descripcion"] for t in txs
                        if t["fecha"].startswith(prefijo) and t.get("auto")}

    for r in REPETIDAS:
        if r["periodo"] == "mensual":
            toca = True
        elif r["periodo"] == "anual":
            toca = (mes_actual == r.get("mes", 1))
        elif r["periodo"] == "semestral":
            mes_base = r.get("mes", 1)
            mes2 = mes_base + 6 if mes_base <= 6 else mes_base - 6
            toca = mes_actual in [mes_base, mes2]
        else:
            toca = False

        if toca and r["nombre"] not in nombres_auto_mes:
            # Usar día guardado si existe
            dia_real, _ = get_dia_mes_repetida(r["nombre"], r["dia"], r.get("mes", 1))
            ultimo_dia = calendar.monthrange(anio_actual, mes_actual)[1]
            dia_real = min(dia_real, ultimo_dia)
            # Usar importe personalizado si existe, si no el por defecto
            importe_real = get_importe_repetida(r["nombre"])
            if importe_real is None:
                importe_real = r["importe"]
            guardar_tx(
                fecha=date(anio_actual, mes_actual, dia_real),
                tipo=r["tipo"],
                cuenta=r["cuenta"],
                subcuenta=r["subcuenta"],
                categoria=r["categoria"],
                descripcion=r["nombre"],
                importe=importe_real,
                auto=True
            )

if "repetidas_ok" not in st.session_state:
    aplicar_repetidas()
    st.session_state["repetidas_ok"] = True

# ─────────────────────────────────────────────
# SALDOS
# ─────────────────────────────────────────────
def calcular_saldos(txs):
    saldos = {c: {sc: 0.0 for sc in cfg["subcuentas"]}
              for c, cfg in CUENTAS_CONFIG.items()}
    for t in txs:
        c = t.get("cuenta", "")
        sc = t.get("subcuenta", "")
        imp = float(t.get("importe", 0))
        tipo = t.get("tipo", "")
        if c in saldos:
            if sc not in saldos[c]:
                saldos[c][sc] = 0.0
            if tipo == "ingreso":
                saldos[c][sc] += imp
            elif tipo == "gasto":
                saldos[c][sc] -= imp
    return saldos

# ─────────────────────────────────────────────
# GRÁFICO TARTA SVG
# ─────────────────────────────────────────────
def pie_chart_svg(cats_ord, total):
    if not cats_ord or total == 0:
        return ""
    cx, cy, r = 150, 130, 95
    paths = []
    angulo = -math.pi / 2
    for i, (cat, val) in enumerate(cats_ord):
        prop = val / total
        angulo_fin = angulo + 2 * math.pi * prop
        x1 = cx + r * math.cos(angulo)
        y1 = cy + r * math.sin(angulo)
        x2 = cx + r * math.cos(angulo_fin)
        y2 = cy + r * math.sin(angulo_fin)
        large = 1 if prop > 0.5 else 0
        color = COLORES_CHART[i % len(COLORES_CHART)]
        paths.append(
            f'<path d="M {cx},{cy} L {x1:.1f},{y1:.1f} A {r},{r} 0 {large},1 {x2:.1f},{y2:.1f} Z" '
            f'fill="{color}" stroke="white" stroke-width="2"/>'
        )
        # Etiqueta % solo si segmento es visible
        if prop > 0.07:
            ang_mid = angulo + math.pi * prop
            lx = cx + (r * 0.62) * math.cos(ang_mid)
            ly = cy + (r * 0.62) * math.sin(ang_mid)
            # Nombre de categoría fuera del círculo
            nx = cx + (r * 1.25) * math.cos(ang_mid)
            ny = cy + (r * 1.25) * math.sin(ang_mid)
            anchor = "start" if nx > cx else "end"
            paths.append(
                f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle" '
                f'font-size="10" fill="white" font-weight="bold">{prop*100:.0f}%</text>'
            )
            # Nombre abreviado fuera
            nombre_corto = cat[:12] + "..." if len(cat) > 12 else cat
            paths.append(
                f'<text x="{nx:.0f}" y="{ny:.0f}" text-anchor="{anchor}" '
                f'font-size="9" fill="#555">{nombre_corto}</text>'
            )
        angulo = angulo_fin

    return f'<svg viewBox="0 0 300 260" xmlns="http://www.w3.org/2000/svg">{"".join(paths)}</svg>'

# ═══════════════════════════════════════════
# UI PRINCIPAL
# ═══════════════════════════════════════════
st.markdown("<h1 style='color:#2ABFBF'>Libro de Cuentas</h1>", unsafe_allow_html=True)

# Navegación igual que Money Manager
col_nav = st.columns(4)
vistas = ["🏦 Cuentas", "📋 Trans.", "📊 Estad.", "🔁 Repetidas"]
if "vista_lc" not in st.session_state:
    st.session_state["vista_lc"] = "🏦 Cuentas"

for i, v in enumerate(vistas):
    with col_nav[i]:
        tipo_btn = "primary" if st.session_state["vista_lc"] == v else "secondary"
        if st.button(v, use_container_width=True, type=tipo_btn, key=f"nav_{v}"):
            st.session_state["vista_lc"] = v
            st.rerun()

st.markdown("---")
vista = st.session_state["vista_lc"]
txs_all = cargar_transacciones()

# ═══════════════════════════════════════════
# 🏦 CUENTAS
# ═══════════════════════════════════════════
if vista == "🏦 Cuentas":
    saldos = calcular_saldos(txs_all)

    todos_saldos = [v for c in saldos.values() for v in c.values()]
    capital = sum(v for v in todos_saldos if v > 0)
    a_deber = abs(sum(v for v in todos_saldos if v < 0))
    balance = sum(todos_saldos)

    st.markdown(f"""
    <div style='display:flex;justify-content:space-around;padding:14px 0 10px 0;
                border-bottom:1px solid #eee;margin-bottom:12px'>
        <div style='text-align:center'>
            <div style='font-size:11px;color:#aaa;margin-bottom:2px'>Capital</div>
            <div style='font-size:20px;font-weight:bold;color:#2ABFBF'>{capital:,.2f}</div>
        </div>
        <div style='text-align:center'>
            <div style='font-size:11px;color:#aaa;margin-bottom:2px'>A deber</div>
            <div style='font-size:20px;font-weight:bold;color:#FF4444'>{a_deber:,.2f}</div>
        </div>
        <div style='text-align:center'>
            <div style='font-size:11px;color:#aaa;margin-bottom:2px'>Balance</div>
            <div style='font-size:20px;font-weight:bold;color:#333'>{balance:,.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for cuenta, cfg in CUENTAS_CONFIG.items():
        total_c = sum(saldos[cuenta].values())
        color_c = "#2ABFBF" if total_c >= 0 else "#FF4444"

        st.markdown(f"""
        <div style='background:#f5f5f5;padding:10px 16px;margin-top:18px;
                    display:flex;justify-content:space-between;border-radius:4px'>
            <b style='color:#555'>{cfg['emoji']} {cuenta}</b>
            <b style='color:{color_c}'>€ {total_c:,.2f}</b>
        </div>
        """, unsafe_allow_html=True)

        for sc in cfg["subcuentas"]:
            saldo_sc = saldos[cuenta].get(sc, 0.0)
            color_sc = "#2ABFBF" if saldo_sc > 0 else ("#FF4444" if saldo_sc < 0 else "#bbb")
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;
                        padding:9px 16px;border-bottom:1px solid #f2f2f2'>
                <span style='color:#333;font-size:15px'>{sc}</span>
                <span style='color:{color_sc};font-size:15px'>€ {saldo_sc:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Actualizar", use_container_width=True):
        cargar_transacciones.clear()
        st.rerun()

# ═══════════════════════════════════════════
# 📋 TRANSACCIONES (DIARIO)
# ═══════════════════════════════════════════
elif vista == "📋 Trans.":

    if "lc_mes" not in st.session_state:
        st.session_state["lc_mes"] = datetime.now().month
    if "lc_anio" not in st.session_state:
        st.session_state["lc_anio"] = datetime.now().year

    col_prev, col_label, col_next = st.columns([1, 3, 1])
    with col_prev:
        if st.button("◀", use_container_width=True, key="prev_t"):
            if st.session_state["lc_mes"] == 1:
                st.session_state["lc_mes"] = 12
                st.session_state["lc_anio"] -= 1
            else:
                st.session_state["lc_mes"] -= 1
            st.rerun()
    with col_label:
        st.markdown(
            f"<h3 style='text-align:center;margin:4px 0;color:#333'>"
            f"{MESES_ES[st.session_state['lc_mes']-1][:3].lower()} "
            f"{st.session_state['lc_anio']}</h3>",
            unsafe_allow_html=True)
    with col_next:
        if st.button("▶", use_container_width=True, key="next_t"):
            if st.session_state["lc_mes"] == 12:
                st.session_state["lc_mes"] = 1
                st.session_state["lc_anio"] += 1
            else:
                st.session_state["lc_mes"] += 1
            st.rerun()

    mes_v = st.session_state["lc_mes"]
    anio_v = st.session_state["lc_anio"]
    prefijo_v = f"{anio_v}-{mes_v:02d}"
    txs_mes = [t for t in txs_all if t["fecha"].startswith(prefijo_v)]

    ing_mes = sum(float(t["importe"]) for t in txs_mes if t["tipo"] == "ingreso")
    gas_mes = sum(float(t["importe"]) for t in txs_mes if t["tipo"] == "gasto")

    st.markdown(f"""
    <div style='display:flex;justify-content:space-around;padding:8px 0 12px 0'>
        <span style='color:#aaa;font-size:14px'>Ingresos
            <b style='color:#2ABFBF;margin-left:6px'>€ {ing_mes:,.2f}</b>
        </span>
        <span style='color:#aaa;font-size:14px'>Gastos
            <b style='color:#FF69B4;margin-left:6px'>€ {gas_mes:,.2f}</b>
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Formulario nueva transacción (al principio) ──
    with st.expander("➕ Nueva transacción", expanded=True):
        tipo_nueva = st.radio("", ["💸 Gasto", "💰 Ingreso", "↔️ Transferencia"],
                               horizontal=True, key="tipo_nueva_tx")
        es_g_n = tipo_nueva == "💸 Gasto"
        es_tr_n = tipo_nueva == "↔️ Transferencia"
        tipo_db = "gasto" if es_g_n else ("transf" if es_tr_n else "ingreso")

        hoy = date.today()
        col_dia, col_mes, col_anio, col_imp = st.columns([1, 2, 1.2, 1.5])
        with col_dia:
            dia_n = st.selectbox("Día", list(range(1, 32)),
                                  index=hoy.day - 1, key="dia_n",
                                  label_visibility="collapsed")
            st.caption("Día")
        with col_mes:
            mes_n = st.selectbox("Mes", MESES_ES,
                                  index=hoy.month - 1, key="mes_n",
                                  label_visibility="collapsed")
            st.caption("Mes")
        with col_anio:
            anio_n = st.number_input("Año", min_value=2020, max_value=2060,
                                      value=hoy.year, step=1, key="anio_n",
                                      label_visibility="collapsed")
            st.caption("Año")
        with col_imp:
            importe_n = st.number_input("Importe €", min_value=0.01, max_value=99999.0,
                                         value=0.01, step=0.01, key="importe_n",
                                         label_visibility="collapsed")
            st.caption("Importe €")
        try:
            mes_num_n = MESES_ES.index(mes_n) + 1
            import calendar as _cal
            ultimo_dia_n = _cal.monthrange(int(anio_n), mes_num_n)[1]
            fecha_n = date(int(anio_n), mes_num_n, min(dia_n, ultimo_dia_n))
        except:
            fecha_n = hoy

        col3, col4 = st.columns(2)
        with col3:
            cuenta_n = st.selectbox("Cuenta", TODAS_CUENTAS, key="cuenta_n")
        with col4:
            sc_opts = CUENTAS_CONFIG[cuenta_n]["subcuentas"]
            subcuenta_n = st.selectbox("Subcuenta", sc_opts, key="sc_n")

        cats_n = CATEGORIAS_GASTO if es_g_n else CATEGORIAS_INGRESO
        col5, col6 = st.columns(2)
        with col5:
            cat_n = st.selectbox("Categoría", cats_n, key="cat_n")
        with col6:
            desc_n = st.text_input("Descripción", placeholder="Mercadona, farmacia...",
                                    key="desc_n", label_visibility="collapsed")
            st.caption("Descripción")

        if st.button("💾 Guardar", type="primary", use_container_width=True, key="btn_guardar"):
            if guardar_tx(fecha_n, tipo_db, cuenta_n, subcuenta_n, cat_n, desc_n, importe_n):
                st.success("✅ Guardado")
                st.rerun()

    st.markdown("---")

    # Agrupar por día
    por_dia = {}
    for t in txs_mes:
        d = t["fecha"]
        por_dia.setdefault(d, []).append(t)

    if not txs_mes:
        st.info("No hay transacciones este mes.")
    else:
        for dia in sorted(por_dia.keys(), reverse=True):
            txs_dia = por_dia[dia]
            try:
                d_obj = datetime.strptime(dia, "%Y-%m-%d")
                dia_num = d_obj.strftime("%d")
                dia_sem = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"][d_obj.weekday()]
            except:
                dia_num = dia; dia_sem = ""

            ing_d = sum(float(t["importe"]) for t in txs_dia if t["tipo"] == "ingreso")
            gas_d = sum(float(t["importe"]) for t in txs_dia if t["tipo"] == "gasto")

            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;align-items:center;
                        padding:5px 2px 4px 2px;margin-top:14px;border-bottom:2px solid #eee'>
                <div>
                    <span style='font-size:22px;font-weight:bold;color:#222'>{dia_num}</span>
                    <span style='font-size:11px;color:#aaa;margin-left:4px'>{dia_sem} {mes_v:02d}.{str(anio_v)[2:]}</span>
                </div>
                <div>
                    <span style='color:#2ABFBF;font-size:12px;margin-right:10px'>€ {ing_d:.2f}</span>
                    <span style='color:#FF69B4;font-size:12px'>€ {gas_d:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            for t in txs_dia:
                es_g = t["tipo"] == "gasto"
                es_tr = t["tipo"] == "transf"
                color_imp = "#FF69B4" if es_g else ("#888" if es_tr else "#2ABFBF")
                signo = "" if es_g or es_tr else "+"
                desc = t.get("descripcion") or t.get("categoria") or "—"
                cat = t.get("categoria") or ""
                subct = t.get("subcuenta") or t.get("cuenta") or ""

                c1, c2, c3 = st.columns([5, 2, 0.4])
                with c1:
                    st.markdown(
                        f"<div style='padding:5px 0 3px 0'>"
                        f"<div style='font-weight:600;font-size:14px;color:#222'>{desc}</div>"
                        f"<div style='color:#aaa;font-size:11px'>{cat} · {subct}</div>"
                        f"</div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(
                        f"<div style='text-align:right;padding:5px 0'>"
                        f"<span style='color:{color_imp};font-weight:bold;font-size:15px'>"
                        f"{signo}{float(t['importe']):.2f} €</span></div>",
                        unsafe_allow_html=True)
                with c3:
                    if st.button("✕", key=f"del_{t['id']}"):
                        borrar_tx(t["id"])
                        st.rerun()

# ═══════════════════════════════════════════
# 📊 ESTADÍSTICAS
# ═══════════════════════════════════════════
elif vista == "📊 Estad.":

    if "lc_mes_e" not in st.session_state:
        st.session_state["lc_mes_e"] = datetime.now().month
    if "lc_anio_e" not in st.session_state:
        st.session_state["lc_anio_e"] = datetime.now().year

    col_prev, col_label, col_next, col_modo = st.columns([1, 2, 1, 2])
    with col_prev:
        if st.button("◀", key="prev_e", use_container_width=True):
            if st.session_state["lc_mes_e"] == 1:
                st.session_state["lc_mes_e"] = 12; st.session_state["lc_anio_e"] -= 1
            else:
                st.session_state["lc_mes_e"] -= 1
            st.rerun()
    with col_label:
        st.markdown(
            f"<h3 style='text-align:center;margin:4px 0;color:#333'>"
            f"{MESES_ES[st.session_state['lc_mes_e']-1][:3].lower()} "
            f"{st.session_state['lc_anio_e']}</h3>", unsafe_allow_html=True)
    with col_next:
        if st.button("▶", key="next_e", use_container_width=True):
            if st.session_state["lc_mes_e"] == 12:
                st.session_state["lc_mes_e"] = 1; st.session_state["lc_anio_e"] += 1
            else:
                st.session_state["lc_mes_e"] += 1
            st.rerun()
    with col_modo:
        modo_e = st.selectbox("", ["Mensual", "Anual"], key="modo_e",
                               label_visibility="collapsed")

    mes_e = st.session_state["lc_mes_e"]
    anio_e = st.session_state["lc_anio_e"]
    txs_e = [t for t in txs_all if t["fecha"].startswith(
        f"{anio_e}-{mes_e:02d}" if modo_e == "Mensual" else str(anio_e))]

    ing_e = sum(float(t["importe"]) for t in txs_e if t["tipo"] == "ingreso")
    gas_e = sum(float(t["importe"]) for t in txs_e if t["tipo"] == "gasto")

    tab_ing, tab_gas = st.tabs([
        f"Ingresos  € {ing_e:,.2f}",
        f"Gastos  € {gas_e:,.2f}"
    ])

    for tab, tipo_tab, total_tab in [(tab_ing, "ingreso", ing_e), (tab_gas, "gasto", gas_e)]:
        with tab:
            if total_tab == 0:
                st.info("Sin datos para este período.")
                continue

            cats_d = {}
            for t in txs_e:
                if t["tipo"] == tipo_tab:
                    cat = t.get("categoria") or "Sin categoría"
                    cats_d[cat] = cats_d.get(cat, 0) + float(t["importe"])
            cats_ord = sorted(cats_d.items(), key=lambda x: -x[1])

            # SVG tarta
            svg = pie_chart_svg(cats_ord, total_tab)
            if svg:
                st.markdown(svg, unsafe_allow_html=True)

            # Lista con colores y %
            for i, (cat, val) in enumerate(cats_ord):
                pct = val / total_tab * 100
                color = COLORES_CHART[i % len(COLORES_CHART)]
                st.markdown(f"""
                <div style='display:flex;align-items:center;padding:10px 4px;
                            border-bottom:1px solid #f5f5f5'>
                    <div style='background:{color};color:white;font-weight:bold;
                                border-radius:6px;padding:3px 8px;min-width:46px;
                                text-align:center;font-size:13px;margin-right:14px'>
                        {pct:.0f}%
                    </div>
                    <span style='flex:1;font-size:15px;color:#333'>{cat}</span>
                    <span style='font-weight:bold;font-size:15px;color:#333'>€ {val:,.2f}</span>
                </div>
                """, unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 🔁 TRANSACCIONES REPETIDAS
# ═══════════════════════════════════════════
elif vista == "🔁 Repetidas":
    st.markdown("<h3 style='color:#FF69B4'>Transacciones repetidas</h3>", unsafe_allow_html=True)
    st.caption("Se insertan automáticamente cada mes. Cambia el importe y se guarda para siempre.")

    # ── Calendario de referencia ──
    if "rep_cal_mes" not in st.session_state:
        st.session_state["rep_cal_mes"] = datetime.now().month
    if "rep_cal_anio" not in st.session_state:
        st.session_state["rep_cal_anio"] = datetime.now().year

    col_cp, col_cl, col_cn = st.columns([1, 3, 1])
    with col_cp:
        if st.button("◀", key="cal_prev", use_container_width=True):
            if st.session_state["rep_cal_mes"] == 1:
                st.session_state["rep_cal_mes"] = 12
                st.session_state["rep_cal_anio"] -= 1
            else:
                st.session_state["rep_cal_mes"] -= 1
            st.rerun()
    with col_cl:
        st.markdown(
            f"<div style='text-align:center;font-weight:bold;font-size:15px;padding:6px 0'>"
            f"{MESES_ES[st.session_state['rep_cal_mes']-1]} {st.session_state['rep_cal_anio']}"
            f"</div>", unsafe_allow_html=True)
    with col_cn:
        if st.button("▶", key="cal_next", use_container_width=True):
            if st.session_state["rep_cal_mes"] == 12:
                st.session_state["rep_cal_mes"] = 1
                st.session_state["rep_cal_anio"] += 1
            else:
                st.session_state["rep_cal_mes"] += 1
            st.rerun()

    # Generar calendario SVG en español
    cal_mes = st.session_state["rep_cal_mes"]
    cal_anio = st.session_state["rep_cal_anio"]
    dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    primer_dia = date(cal_anio, cal_mes, 1).weekday()  # 0=lun
    total_dias = calendar.monthrange(cal_anio, cal_mes)[1]
    hoy_cal = date.today()

    cell_w, cell_h = 42, 36
    cols_cal = 7
    header_h = 28
    filas = math.ceil((primer_dia + total_dias) / 7)
    svg_w = cell_w * cols_cal
    svg_h = header_h + filas * cell_h + 8

    svg_parts = [f'<svg viewBox="0 0 {svg_w} {svg_h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:360px;display:block;margin:0 auto">']

    # Fondo
    svg_parts.append(f'<rect width="{svg_w}" height="{svg_h}" fill="#fafafa" rx="8"/>')

    # Cabecera días semana
    for i, d in enumerate(dias_semana):
        x = i * cell_w + cell_w // 2
        color_hdr = "#FF69B4" if i >= 5 else "#999"
        svg_parts.append(f'<text x="{x}" y="{header_h - 6}" text-anchor="middle" font-size="11" fill="{color_hdr}" font-weight="bold">{d}</text>')

    # Días del mes
    dia_actual = 1
    for fila in range(filas):
        for col in range(cols_cal):
            pos = fila * cols_cal + col
            if pos < primer_dia or dia_actual > total_dias:
                col += 1
                continue
            cx = col * cell_w + cell_w // 2
            cy = header_h + fila * cell_h + cell_h // 2
            es_hoy = (dia_actual == hoy_cal.day and cal_mes == hoy_cal.month and cal_anio == hoy_cal.year)
            es_finde = col >= 5
            # Círculo para hoy
            if es_hoy:
                svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="14" fill="#2ABFBF"/>')
                color_txt = "white"
            else:
                color_txt = "#FF69B4" if es_finde else "#333"
            svg_parts.append(f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" font-size="13" fill="{color_txt}" font-weight="{"bold" if es_hoy else "normal"}">{dia_actual}</text>')
            dia_actual += 1

    svg_parts.append('</svg>')
    st.markdown("".join(svg_parts), unsafe_allow_html=True)
    st.markdown("---")

    for grupo, tipo_grupo, color_grupo in [
        ("Ingresos", "ingreso", "#2ABFBF"),
        ("Gastos", "gasto", "#FF69B4"),
        ("Transferencias", "transf", "#888")
    ]:
        items = [r for r in REPETIDAS if r["tipo"] == tipo_grupo]
        if not items:
            continue
        st.markdown(f"<div style='font-weight:bold;color:{color_grupo};padding:12px 0 6px 0;font-size:15px'>{grupo}</div>",
                    unsafe_allow_html=True)

        for r in items:
            if r["periodo"] == "mensual":
                periodo_txt = "Cada mes"
            elif r["periodo"] == "anual":
                periodo_txt = f"Cada año · {MESES_ES[r.get('mes',1)-1]}"
            elif r["periodo"] == "semestral":
                periodo_txt = "Cada 6 meses"
            else:
                periodo_txt = r["periodo"]

            # Leer importe guardado (personalizado) o usar el por defecto
            importe_guardado = get_importe_repetida(r["nombre"])
            importe_actual = importe_guardado if importe_guardado is not None else r["importe"]

            # Leer día y mes guardados
            dia_guardado, mes_guardado = get_dia_mes_repetida(
                r["nombre"], r["dia"], r.get("mes", 1)
            )

            c1, c2, c3, c4 = st.columns([2.5, 0.8, 1.5, 1.5])
            with c1:
                st.markdown(
                    f"<div style='padding:8px 0 2px 0'>"
                    f"<div style='font-weight:600;font-size:14px'>{r['nombre']}</div>"
                    f"<div style='color:#aaa;font-size:11px'>{periodo_txt} · {r['cuenta']}</div>"
                    f"</div>", unsafe_allow_html=True)
            with c2:
                nuevo_dia = st.number_input(
                    "Día", min_value=1, max_value=31,
                    value=int(dia_guardado), step=1,
                    key=f"rep_dia_{r['nombre']}",
                    label_visibility="collapsed"
                )
                st.caption("Día")
            with c3:
                nuevo_mes = st.selectbox(
                    "Mes", MESES_ES,
                    index=int(mes_guardado) - 1,
                    key=f"rep_mes_{r['nombre']}",
                    label_visibility="collapsed"
                ) if r["periodo"] != "mensual" else st.markdown(
                    "<span style='color:#aaa;font-size:12px'>Todos</span>",
                    unsafe_allow_html=True) or MESES_ES[int(mes_guardado) - 1]
                st.caption("Mes")
            with c4:
                nuevo_importe = st.number_input(
                    "Importe",
                    min_value=0.01, max_value=99999.0,
                    value=float(importe_actual),
                    step=0.01,
                    key=f"rep_imp_{r['nombre']}",
                    label_visibility="collapsed"
                )
                st.caption("Importe €")

            # Guardar si cambia algo
            mes_num_nuevo = MESES_ES.index(nuevo_mes) + 1 if isinstance(nuevo_mes, str) else int(mes_guardado)
            cambio_diames = (nuevo_dia != dia_guardado or mes_num_nuevo != mes_guardado)
            cambio_importe = abs(nuevo_importe - importe_actual) > 0.001
            if cambio_diames:
                set_dia_mes_repetida(r["nombre"], nuevo_dia, mes_num_nuevo)
                st.rerun()
            if cambio_importe:
                set_importe_repetida(r["nombre"], nuevo_importe)
                st.rerun()

            st.markdown("<hr style='margin:4px 0;border-color:#f2f2f2'>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Reaplicar este mes", use_container_width=True):
        st.session_state.pop("repetidas_ok", None)
        cargar_transacciones.clear()
        aplicar_repetidas()
        cargar_transacciones.clear()
        st.success("✅ Listo")
        st.rerun()

    st.markdown("---")
    st.markdown("<h3 style='color:#FF69B4'>📥 Importar historial Money Manager</h3>",
                unsafe_allow_html=True)
    st.caption(f"Transacciones actuales en el libro: **{len(txs_all)}**")

    archivo_mm = st.file_uploader("Subir archivo .db de Money Manager",
                                   type=None, key="mm_up")
    if archivo_mm:
        tmp = tempfile.mktemp(suffix=".db")
        with open(tmp, "wb") as f:
            f.write(archivo_mm.read())
        conn2 = sq3.connect(tmp)
        cur2 = conn2.cursor()
        cur2.execute("""SELECT WDATE, DO_TYPE, CAST(ZMONEY AS REAL), ZCONTENT
                        FROM INOUTCOME WHERE IS_DEL=0 AND DO_TYPE IN ('0','1')
                        ORDER BY WDATE ASC""")
        rows2 = cur2.fetchall()
        conn2.close()
        os.unlink(tmp)
        st.success(f"✅ {len(rows2)} transacciones encontradas")

        desde_imp = st.date_input("Importar desde", value=date(2022, 1, 1), key="desde_imp")
        if st.button("🚀 Importar todo", type="primary", key="btn_importar"):
            lote = [{"fecha": r[0], "tipo": "ingreso" if r[1]=="0" else "gasto",
                     "cuenta": "", "subcuenta": "", "categoria": "",
                     "descripcion": r[3] or "", "importe": float(r[2]), "auto": False}
                    for r in rows2 if r[0] >= str(desde_imp)]
            prog = st.progress(0)
            for i in range(0, len(lote), 100):
                supabase.table("libro_cuentas").insert(lote[i:i+100]).execute()
                prog.progress(min((i+100)/max(len(lote),1), 1.0))
            cargar_transacciones.clear()
            st.success(f"✅ {len(lote)} transacciones importadas")
            st.rerun()
