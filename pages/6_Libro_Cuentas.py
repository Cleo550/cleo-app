import streamlit as st
import json
import sqlite3
import io
from datetime import datetime, date
from supabase import create_client

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

# --- SUPABASE ---
@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = get_supabase()

# --- CONSTANTES ---
CUENTAS = ["BBVA", "Efectivo", "OpenBanc", "Trade Republic"]

CATEGORIAS_GASTO = [
    "Supermercado", "Gasolina", "Farmacia", "Tabaco", "Restaurante/Bar",
    "Ropa", "Salud", "Terapeuta", "Transporte", "Amazon",
    "Suscripciones", "Móvil/Internet", "Autónomo", "Seguros",
    "Hogar", "Ocio", "Regalos", "Veterinario", "Otros"
]

CATEGORIAS_INGRESO = [
    "Sueldo Limpieza", "Ania", "Lola", "Yordhana",
    "Apuestas", "Trade Republic", "Regalo", "Otros"
]

# --- SUPABASE: tabla libro_cuentas ---
# Estructura: id (auto), fecha TEXT, tipo TEXT (gasto/ingreso), cuenta TEXT,
#             categoria TEXT, descripcion TEXT, importe REAL, creado_en TIMESTAMP

@st.cache_data(ttl=30)
def cargar_transacciones():
    try:
        r = supabase.table("libro_cuentas").select("*").order("fecha", desc=True).order("id", desc=True).execute()
        return r.data or []
    except Exception as e:
        return []

def guardar_transaccion(fecha, tipo, cuenta, categoria, descripcion, importe):
    try:
        supabase.table("libro_cuentas").insert({
            "fecha": str(fecha),
            "tipo": tipo,
            "cuenta": cuenta,
            "categoria": categoria,
            "descripcion": descripcion,
            "importe": float(importe)
        }).execute()
        cargar_transacciones.clear()
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

def eliminar_transaccion(id_tx):
    try:
        supabase.table("libro_cuentas").delete().eq("id", id_tx).execute()
        cargar_transacciones.clear()
        return True
    except:
        return False

# --- IMPORTACIÓN DESDE SQLITE ---
def importar_desde_sqlite(archivo_bytes):
    """Importa transacciones desde el backup SQLite de Money Manager."""
    # Guardar temporalmente
    tmp_path = "/tmp/mm_import.db"
    with open(tmp_path, "wb") as f:
        f.write(archivo_bytes)

    conn = sqlite3.connect(tmp_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT WDATE, DO_TYPE, CAST(ZMONEY AS REAL), ZCONTENT
        FROM INOUTCOME
        WHERE IS_DEL=0 AND DO_TYPE IN ('0','1')
        ORDER BY WDATE ASC, AID ASC
    """)
    rows = cur.fetchall()
    conn.close()

    return rows  # [(fecha_str, tipo, importe, descripcion), ...]


# ============================
# UI PRINCIPAL
# ============================
st.markdown("<h1 style='color:#2ABFBF'>Libro de Cuentas</h1>", unsafe_allow_html=True)

tab_nuevo, tab_historial, tab_resumen, tab_importar = st.tabs([
    "➕ Nueva entrada", "📋 Historial", "📊 Resumen", "📥 Importar"
])

# ============================
# TAB 1: NUEVA ENTRADA
# ============================
with tab_nuevo:
    st.markdown("<h3 style='color:#FF69B4'>Añadir transacción</h3>", unsafe_allow_html=True)

    # Tipo de transacción
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        tipo_sel = st.radio("Tipo", ["💸 Gasto", "💰 Ingreso"], horizontal=True, key="tipo_tx")
    es_gasto = tipo_sel == "💸 Gasto"

    col1, col2 = st.columns(2)
    with col1:
        fecha_tx = st.date_input("Fecha", value=date.today(), key="fecha_nueva")
    with col2:
        cuenta_tx = st.selectbox("Cuenta", CUENTAS, key="cuenta_nueva")

    col3, col4 = st.columns(2)
    with col3:
        cats = CATEGORIAS_GASTO if es_gasto else CATEGORIAS_INGRESO
        categoria_tx = st.selectbox("Categoría", cats, key="cat_nueva")
    with col4:
        importe_tx = st.number_input("Importe EUR", min_value=0.01, max_value=99999.0,
                                      value=0.01, step=0.01, key="importe_nueva")

    descripcion_tx = st.text_input("Descripción (opcional)", placeholder="Ej: Mercadona, gasolinera...",
                                    key="desc_nueva")

    if st.button("💾 Guardar", type="primary", use_container_width=True):
        tipo_guardado = "gasto" if es_gasto else "ingreso"
        if guardar_transaccion(fecha_tx, tipo_guardado, cuenta_tx, categoria_tx, descripcion_tx, importe_tx):
            st.success("✅ Guardado")
            st.rerun()

# ============================
# TAB 2: HISTORIAL
# ============================
with tab_historial:
    st.markdown("<h3 style='color:#FF69B4'>Historial de transacciones</h3>", unsafe_allow_html=True)

    # Filtros
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        filtro_tipo = st.selectbox("Tipo", ["Todos", "Gastos", "Ingresos"], key="f_tipo")
    with col_f2:
        filtro_cuenta = st.selectbox("Cuenta", ["Todas"] + CUENTAS, key="f_cuenta")
    with col_f3:
        meses_opts = ["Todos"] + [f"{m:02d}/{a}" for a in range(2022, datetime.now().year+1)
                     for m in range(1, 13) if not (a == datetime.now().year and m > datetime.now().month)]
        filtro_mes = st.selectbox("Mes", list(reversed(meses_opts[:25])), key="f_mes")
    with col_f4:
        filtro_buscar = st.text_input("Buscar", placeholder="descripción...", key="f_buscar",
                                       label_visibility="collapsed")
        st.caption("Buscar texto")

    if st.button("🔄 Refrescar", key="btn_refresh_hist"):
        cargar_transacciones.clear()
        st.rerun()

    txs = cargar_transacciones()

    # Aplicar filtros
    if filtro_tipo == "Gastos":
        txs = [t for t in txs if t["tipo"] == "gasto"]
    elif filtro_tipo == "Ingresos":
        txs = [t for t in txs if t["tipo"] == "ingreso"]

    if filtro_cuenta != "Todas":
        txs = [t for t in txs if t.get("cuenta") == filtro_cuenta]

    if filtro_mes != "Todos":
        mes_num, anio_num = filtro_mes.split("/")
        txs = [t for t in txs if t["fecha"].startswith(f"{anio_num}-{mes_num}")]

    if filtro_buscar:
        buscar_lower = filtro_buscar.lower()
        txs = [t for t in txs if buscar_lower in (t.get("descripcion") or "").lower()
               or buscar_lower in (t.get("categoria") or "").lower()]

    st.caption(f"{len(txs)} transacciones")

    if not txs:
        st.info("No hay transacciones con estos filtros.")
    else:
        # Agrupar por fecha
        fecha_actual = None
        for tx in txs:
            # Separador por fecha
            try:
                f = datetime.strptime(tx["fecha"], "%Y-%m-%d")
                fecha_fmt = f.strftime("%d %b %Y")
            except:
                fecha_fmt = tx["fecha"]

            if fecha_fmt != fecha_actual:
                st.markdown(f"<p style='color:#999;font-size:12px;margin:8px 0 2px 0'>{fecha_fmt}</p>",
                            unsafe_allow_html=True)
                fecha_actual = fecha_fmt

            es_g = tx["tipo"] == "gasto"
            color = "#FF69B4" if es_g else "#2ABFBF"
            signo = "−" if es_g else "+"
            emoji_cuenta = {"BBVA": "🏦", "Efectivo": "💵", "OpenBanc": "🏛️", "Trade Republic": "📈"}.get(tx.get("cuenta", ""), "💳")

            c1, c2, c3 = st.columns([4, 2, 0.5])
            with c1:
                desc = tx.get("descripcion") or tx.get("categoria") or "—"
                cat = tx.get("categoria") or ""
                st.markdown(
                    f"<span style='font-weight:600'>{desc}</span> "
                    f"<span style='color:#999;font-size:12px'>{cat} · {emoji_cuenta} {tx.get('cuenta','')}</span>",
                    unsafe_allow_html=True
                )
            with c2:
                st.markdown(
                    f"<span style='color:{color};font-weight:bold;font-size:16px'>"
                    f"{signo} {float(tx['importe']):.2f} €</span>",
                    unsafe_allow_html=True
                )
            with c3:
                if st.button("🗑️", key=f"del_tx_{tx['id']}"):
                    if eliminar_transaccion(tx["id"]):
                        st.rerun()

        # Totales filtrados
        st.markdown("---")
        total_g = sum(float(t["importe"]) for t in txs if t["tipo"] == "gasto")
        total_i = sum(float(t["importe"]) for t in txs if t["tipo"] == "ingreso")
        c1, c2, c3 = st.columns(3)
        c1.metric("Ingresos", f"{total_i:.2f} €")
        c2.metric("Gastos", f"{total_g:.2f} €")
        color_b = "green" if (total_i - total_g) >= 0 else "red"
        c3.markdown(f"<p style='font-size:13px;color:grey'>Balance</p>"
                    f"<p style='font-size:1.4rem;font-weight:bold;color:{color_b}'>"
                    f"{total_i - total_g:+.2f} €</p>", unsafe_allow_html=True)

# ============================
# TAB 3: RESUMEN
# ============================
with tab_resumen:
    st.markdown("<h3 style='color:#FF69B4'>Resumen mensual</h3>", unsafe_allow_html=True)

    col_rm, col_ra = st.columns(2)
    with col_rm:
        mes_res = st.selectbox("Mes", list(range(1, 13)),
                                index=datetime.now().month - 1,
                                format_func=lambda x: ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                                                        "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"][x-1],
                                key="mes_resumen")
    with col_ra:
        anio_res = st.number_input("Año", min_value=2022, max_value=2060,
                                    value=datetime.now().year, step=1, key="anio_resumen")

    if st.button("🔄 Refrescar resumen", key="btn_refresh_res"):
        cargar_transacciones.clear()
        st.rerun()

    txs_all = cargar_transacciones()
    prefijo = f"{int(anio_res)}-{int(mes_res):02d}"
    txs_mes = [t for t in txs_all if t["fecha"].startswith(prefijo)]

    if not txs_mes:
        st.info("No hay datos para este mes.")
    else:
        total_ing = sum(float(t["importe"]) for t in txs_mes if t["tipo"] == "ingreso")
        total_gas = sum(float(t["importe"]) for t in txs_mes if t["tipo"] == "gasto")
        balance = total_ing - total_gas

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Ingresos", f"{total_ing:.2f} €")
        col2.metric("💸 Gastos", f"{total_gas:.2f} €")
        color_b = "green" if balance >= 0 else "red"
        col3.markdown(f"<p style='font-size:13px;color:grey'>Balance</p>"
                      f"<p style='font-size:1.4rem;font-weight:bold;color:{color_b}'>"
                      f"{balance:+.2f} €</p>", unsafe_allow_html=True)

        st.markdown("---")

        # Gastos por categoría
        st.markdown("<b style='color:#FF69B4'>Gastos por categoría:</b>", unsafe_allow_html=True)
        cats_gas = {}
        for t in txs_mes:
            if t["tipo"] == "gasto":
                cat = t.get("categoria") or "Sin categoría"
                cats_gas[cat] = cats_gas.get(cat, 0) + float(t["importe"])

        for cat, total in sorted(cats_gas.items(), key=lambda x: -x[1]):
            pct = (total / total_gas * 100) if total_gas > 0 else 0
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.write(cat)
                st.progress(min(pct / 100, 1.0))
            with c2:
                st.write(f"{total:.2f} €")
            with c3:
                st.caption(f"{pct:.0f}%")

        st.markdown("---")

        # Gastos por cuenta
        st.markdown("<b style='color:#FF69B4'>Por cuenta:</b>", unsafe_allow_html=True)
        cuentas_totales = {}
        for t in txs_mes:
            cuenta = t.get("cuenta") or "Sin cuenta"
            if cuenta not in cuentas_totales:
                cuentas_totales[cuenta] = {"gasto": 0, "ingreso": 0}
            cuentas_totales[cuenta][t["tipo"]] += float(t["importe"])

        for cuenta, vals in cuentas_totales.items():
            emoji = {"BBVA": "🏦", "Efectivo": "💵", "OpenBanc": "🏛️", "Trade Republic": "📈"}.get(cuenta, "💳")
            c1, c2, c3 = st.columns(3)
            c1.write(f"{emoji} {cuenta}")
            c2.write(f"↑ {vals['ingreso']:.2f} €")
            c3.write(f"↓ {vals['gasto']:.2f} €")

        # Histórico últimos 12 meses
        st.markdown("---")
        st.markdown("<b style='color:#FF69B4'>Últimos 12 meses:</b>", unsafe_allow_html=True)

        resumen_meses = {}
        for t in txs_all:
            mes_key = t["fecha"][:7]  # YYYY-MM
            if mes_key not in resumen_meses:
                resumen_meses[mes_key] = {"gasto": 0, "ingreso": 0}
            resumen_meses[mes_key][t["tipo"]] += float(t["importe"])

        # Últimos 12 meses con datos
        meses_ordenados = sorted(resumen_meses.keys(), reverse=True)[:12]
        for mk in meses_ordenados:
            try:
                anio_m, mes_m = mk.split("-")
                nombre_mes = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"][int(mes_m)-1]
                label = f"{nombre_mes} {anio_m}"
            except:
                label = mk
            vals = resumen_meses[mk]
            bal = vals["ingreso"] - vals["gasto"]
            color_bal = "green" if bal >= 0 else "red"
            c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1.5])
            c1.write(label)
            c2.caption(f"↑ {vals['ingreso']:.0f}€")
            c3.caption(f"↓ {vals['gasto']:.0f}€")
            c4.markdown(f"<span style='color:{color_bal};font-weight:bold'>{bal:+.0f}€</span>",
                        unsafe_allow_html=True)

# ============================
# TAB 4: IMPORTAR
# ============================
with tab_importar:
    st.markdown("<h3 style='color:#FF69B4'>Importar desde Money Manager</h3>", unsafe_allow_html=True)
    st.caption("Sube el archivo de backup de Money Manager (el mismo que ya me pasaste).")

    # Contar cuántas ya hay importadas
    txs_actuales = cargar_transacciones()
    st.info(f"Actualmente hay **{len(txs_actuales)}** transacciones en el libro.")

    archivo_mm = st.file_uploader("Subir backup de Money Manager",
                                   type=None,
                                   key="uploader_mm",
                                   help="El archivo .db que exporta Money Manager")

    if archivo_mm:
        try:
            rows = importar_desde_sqlite(archivo_mm.read())
            st.success(f"✅ Archivo leído: {len(rows)} transacciones encontradas")

            # Preview
            with st.expander("Ver primeras 10 transacciones"):
                for r in rows[:10]:
                    tipo_txt = "INGRESO" if r[1] == "0" else "GASTO"
                    st.write(f"{r[0]} | {tipo_txt} | {r[2]:.2f} € | {r[3] or '—'}")

            col_imp1, col_imp2 = st.columns(2)
            with col_imp1:
                cuenta_import = st.selectbox("Asignar cuenta a todas",
                                              ["Sin cuenta"] + CUENTAS,
                                              key="cuenta_import",
                                              help="Como no se guardó la cuenta en Money Manager, elige una o déjalo en 'Sin cuenta'")
            with col_imp2:
                desde_fecha = st.date_input("Importar solo desde",
                                             value=date(2022, 1, 1),
                                             key="desde_import")

            rows_filtradas = [r for r in rows if r[0] >= str(desde_fecha)]
            st.write(f"A importar: **{len(rows_filtradas)}** transacciones desde {desde_fecha}")

            if st.button("🚀 Importar todo", type="primary", use_container_width=True):
                cuenta_val = cuenta_import if cuenta_import != "Sin cuenta" else ""
                lote = []
                for r in rows_filtradas:
                    tipo_db = "ingreso" if r[1] == "0" else "gasto"
                    lote.append({
                        "fecha": r[0],
                        "tipo": tipo_db,
                        "cuenta": cuenta_val,
                        "categoria": "",
                        "descripcion": r[3] or "",
                        "importe": float(r[2])
                    })

                # Insertar en lotes de 100
                progress = st.progress(0)
                total_lotes = (len(lote) // 100) + 1
                insertados = 0
                errores = 0

                for i in range(0, len(lote), 100):
                    chunk = lote[i:i+100]
                    try:
                        supabase.table("libro_cuentas").insert(chunk).execute()
                        insertados += len(chunk)
                    except Exception as e:
                        errores += len(chunk)
                    progress.progress(min((i + 100) / len(lote), 1.0))

                cargar_transacciones.clear()
                if errores == 0:
                    st.success(f"✅ Importadas {insertados} transacciones correctamente")
                else:
                    st.warning(f"✅ {insertados} importadas, ⚠️ {errores} con error")
                st.rerun()

        except Exception as e:
            st.error(f"Error leyendo el archivo: {e}")
            st.caption("Asegúrate de que es el archivo .db de Money Manager (no un Excel)")

    st.markdown("---")
    st.markdown("<h3 style='color:#FF69B4'>⚠️ Borrar todo el historial</h3>", unsafe_allow_html=True)
    st.caption("Usa esto solo si quieres volver a importar desde cero.")
    if st.button("🗑️ Borrar TODAS las transacciones", type="secondary"):
        st.session_state["confirm_delete_all"] = True

    if st.session_state.get("confirm_delete_all", False):
        st.warning("¿Segura? Esto borra todas las transacciones del libro.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Sí, borrar todo", type="primary"):
                try:
                    # Borrar todas las filas
                    supabase.table("libro_cuentas").delete().neq("id", 0).execute()
                    cargar_transacciones.clear()
                    st.session_state["confirm_delete_all"] = False
                    st.success("Borrado")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        with c2:
            if st.button("Cancelar"):
                st.session_state["confirm_delete_all"] = False
                st.rerun()
