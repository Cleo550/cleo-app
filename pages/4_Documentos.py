import streamlit as st
import json
import uuid
from supabase import create_client

st.set_page_config(page_title="Documentos - Cleo Pro", layout="centered")

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

# --- SUPABASE ---
@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_SERVICE_KEY"])

supabase = get_supabase()

BUCKET = "documentos"
TIPOS = ["pdf", "png", "jpg", "jpeg", "docx", "xlsx"]

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
        supabase.table("datos_app").upsert({"clave": clave, "valor": json.dumps(valor)}).execute()
    except:
        pass

def subir_archivo(archivo, carpeta):
    try:
        ext = archivo.name.split(".")[-1].lower()
        nombre_unico = f"{carpeta}/{uuid.uuid4()}.{ext}"
        supabase.storage.from_(BUCKET).upload(
            nombre_unico,
            archivo.read(),
            {"content-type": archivo.type}
        )
        url = supabase.storage.from_(BUCKET).get_public_url(nombre_unico)
        return url, nombre_unico
    except Exception as e:
        st.error(f"Error al subir: {e}")
        return None, None

def eliminar_archivo(path, clave_lista, idx):
    try:
        supabase.storage.from_(BUCKET).remove([path])
    except:
        pass
    lista = get_dato(clave_lista, [])
    lista.pop(idx)
    set_dato(clave_lista, lista)
    st.rerun()

def mostrar_documentos(clave_lista, carpeta):
    """Muestra los documentos guardados y el formulario para subir nuevos."""
    lista = get_dato(clave_lista, [])

    # Subir nuevo documento
    with st.expander("➕ Añadir documento", expanded=False):
        archivo = st.file_uploader("Subir archivo o foto", type=["pdf","png","jpg","jpeg","docx","xlsx"], key=f"up_{clave_lista}")
        nombre = st.text_input("Nombre", placeholder="Ej: Contrato 2026", key=f"nom_{clave_lista}")
        desc = st.text_input("Descripción (opcional)", placeholder="Ej: Firmado en marzo", key=f"desc_{clave_lista}")
        if st.button("💾 Guardar documento", key=f"btn_{clave_lista}"):
            if archivo and nombre:
                with st.spinner("Subiendo..."):
                    url, path = subir_archivo(archivo, carpeta)
                if url:
                    lista.append({"nombre": nombre, "desc": desc, "url": url, "path": path, "tipo": archivo.name.split(".")[-1].lower()})
                    set_dato(clave_lista, lista)
                    st.success("✅ Guardado")
                    st.rerun()
            else:
                st.warning("Falta el archivo o el nombre")

    # Listar documentos
    if not lista:
        st.caption("No hay documentos aún.")
    for idx, doc in enumerate(lista):
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f"**{doc['nombre']}**")
            if doc.get("desc"):
                st.caption(doc["desc"])
            st.markdown(f"[📄 Ver archivo]({doc['url']})")
        with c2:
            st.markdown(f"<a href='{doc['url']}' download target='_blank'><button style='background:#2ABFBF;color:white;border:none;border-radius:4px;padding:6px 10px;cursor:pointer;width:100%'>⬇️</button></a>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{clave_lista}_{idx}"):
                eliminar_archivo(doc.get("path", ""), clave_lista, idx)
        st.markdown("---")

# =====================
# TÍTULO PRINCIPAL
# =====================
st.markdown("<h1 style='color:#2ABFBF'>Documentos</h1>", unsafe_allow_html=True)

tab_clientes, tab_gastos = st.tabs(["👥 Documentos Clientes", "📁 Documentos Gastos"])

# =====================
# DOCUMENTOS CLIENTES
# =====================
with tab_clientes:
    st.markdown("<h2 style='color:#2ABFBF'>Documentos Clientes</h2>", unsafe_allow_html=True)

    # Cargar lista de clientes
    clientes_fijos = ["Lola", "Yordhana", "Ania"]
    clientes_extra = get_dato("doc_clientes_extra", [])
    todos_clientes = clientes_fijos + clientes_extra

    # Selector de cliente
    col_btns = st.columns(len(todos_clientes) + 1)
    if "doc_cliente_sel" not in st.session_state:
        st.session_state["doc_cliente_sel"] = todos_clientes[0]

    for i, cl in enumerate(todos_clientes):
        with col_btns[i]:
            tipo = "primary" if st.session_state["doc_cliente_sel"] == cl else "secondary"
            if st.button(cl, key=f"btn_cl_{cl}", use_container_width=True, type=tipo):
                st.session_state["doc_cliente_sel"] = cl
                st.rerun()

    # Botón añadir cliente
    with col_btns[-1]:
        if st.button("➕", key="btn_nuevo_cliente", use_container_width=True):
            st.session_state["show_nuevo_cliente"] = True

    if st.session_state.get("show_nuevo_cliente", False):
        nuevo_cl = st.text_input("Nombre del nuevo cliente", key="input_nuevo_cliente")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Añadir", key="btn_add_cliente"):
                if nuevo_cl and nuevo_cl not in todos_clientes:
                    clientes_extra.append(nuevo_cl)
                    set_dato("doc_clientes_extra", clientes_extra)
                    st.session_state["doc_cliente_sel"] = nuevo_cl
                    st.session_state["show_nuevo_cliente"] = False
                    st.rerun()
        with c2:
            if st.button("Cancelar", key="btn_cancel_cliente"):
                st.session_state["show_nuevo_cliente"] = False
                st.rerun()

    st.markdown("---")
    cliente_sel = st.session_state["doc_cliente_sel"]
    st.markdown(f"<h3 style='color:#FF69B4'>{cliente_sel}</h3>", unsafe_allow_html=True)
    mostrar_documentos(f"docs_cliente_{cliente_sel}", f"clientes/{cliente_sel}")

# =====================
# DOCUMENTOS GASTOS
# =====================
with tab_gastos:
    st.markdown("<h2 style='color:#2ABFBF'>Documentos Gastos</h2>", unsafe_allow_html=True)

    secciones = get_dato("doc_gastos_secciones", [])

    if "doc_seccion_sel" not in st.session_state and secciones:
        st.session_state["doc_seccion_sel"] = secciones[0]

    # Botones de secciones
    if secciones:
        cols = st.columns(len(secciones) + 1)
        for i, sec in enumerate(secciones):
            with cols[i]:
                tipo = "primary" if st.session_state.get("doc_seccion_sel") == sec else "secondary"
                if st.button(sec, key=f"btn_sec_{sec}", use_container_width=True, type=tipo):
                    st.session_state["doc_seccion_sel"] = sec
                    st.rerun()
        with cols[-1]:
            if st.button("➕", key="btn_nueva_seccion", use_container_width=True):
                st.session_state["show_nueva_seccion"] = True
    else:
        if st.button("➕ Añadir sección", key="btn_nueva_seccion"):
            st.session_state["show_nueva_seccion"] = True

    if st.session_state.get("show_nueva_seccion", False):
        nueva_sec = st.text_input("Nombre de la sección", placeholder="Ej: Seguros, Contratos...", key="input_nueva_seccion")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Añadir", key="btn_add_seccion"):
                if nueva_sec and nueva_sec not in secciones:
                    secciones.append(nueva_sec)
                    set_dato("doc_gastos_secciones", secciones)
                    st.session_state["doc_seccion_sel"] = nueva_sec
                    st.session_state["show_nueva_seccion"] = False
                    st.rerun()
        with c2:
            if st.button("Cancelar", key="btn_cancel_seccion"):
                st.session_state["show_nueva_seccion"] = False
                st.rerun()

    st.markdown("---")
    if secciones and st.session_state.get("doc_seccion_sel"):
        sec_sel = st.session_state["doc_seccion_sel"]
        st.markdown(f"<h3 style='color:#FF69B4'>{sec_sel}</h3>", unsafe_allow_html=True)
        mostrar_documentos(f"docs_gastos_{sec_sel}", f"gastos/{sec_sel}")
    elif not secciones:
        st.caption("No hay secciones aún. Pulsa ➕ para empezar.")
