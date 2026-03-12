import streamlit as st
from supabase import create_client
from datetime import datetime
import uuid

st.set_page_config(page_title="Facturas Gastos - Cleo Pro", layout="centered")

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

TRIMESTRES = {
    "T1 · Enero - Marzo":        "T1",
    "T2 · Abril - Junio":        "T2",
    "T3 · Julio - Septiembre":   "T3",
    "T4 · Octubre - Diciembre":  "T4",
}

st.title("Facturas Gastos")

# Selector trimestre y año
col1, col2 = st.columns(2)
with col1:
    trimestre_nombre = st.selectbox("Trimestre", list(TRIMESTRES.keys()))
with col2:
    anio = st.number_input("Año", min_value=2024, max_value=2035,
                            value=datetime.now().year, step=1)

trimestre = TRIMESTRES[trimestre_nombre]
clave_trim = f"{trimestre}_{int(anio)}"

st.markdown("---")

# --- SUBIR FACTURA ---
st.subheader("Añadir factura")

col_a, col_b = st.columns(2)
with col_a:
    archivo = st.file_uploader("Subir archivo o foto", type=["pdf","png","jpg","jpeg"],
                                key=f"uploader_{clave_trim}")
with col_b:
    concepto = st.text_input("Concepto", placeholder="Ej: Gasolina febrero",
                              key=f"concepto_{clave_trim}")
    importe = st.number_input("Importe EUR", min_value=0.0, max_value=10000.0,
                               value=0.0, step=0.5, key=f"importe_{clave_trim}")

if st.button("💾 Guardar factura", type="primary", use_container_width=True):
    if archivo and concepto and importe > 0:
        try:
            ext = archivo.name.split(".")[-1]
            nombre_archivo = f"{clave_trim}_{uuid.uuid4().hex[:8]}.{ext}"
            supabase.storage.from_("facturas-gastos").upload(nombre_archivo, archivo.read(),
                {"content-type": archivo.type})
            url = supabase.storage.from_("facturas-gastos").get_public_url(nombre_archivo)
            supabase.table("facturas_gastos").insert({
                "trimestre": clave_trim,
                "nombre": concepto,
                "importe": importe,
                "archivo_url": url
            }).execute()
            st.success("✅ Factura guardada correctamente")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")
    else:
        st.warning("⚠️ Rellena el concepto, el importe y adjunta un archivo.")

st.markdown("---")

# --- LISTADO DE FACTURAS ---
st.subheader(f"Facturas guardadas · {trimestre_nombre} · {int(anio)}")

with st.spinner("Cargando facturas..."):
    try:
        r = supabase.table("facturas_gastos").select("*").eq("trimestre", clave_trim).order("creado_en").execute()
        facturas = r.data
    except:
        facturas = []

if not facturas:
    st.info("No hay facturas registradas para este trimestre todavía.")
else:
    total = 0.0
    for f in facturas:
        with st.container():
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.write(f"**{f['nombre']}**")
            with c2:
                st.write(f"{float(f['importe']):.2f} EUR")
            with c3:
                if st.button("🗑️", key=f"del_{f['id']}"):
                    supabase.table("facturas_gastos").delete().eq("id", f["id"]).execute()
                    st.rerun()
            if f.get("archivo_url"):
                url = f["archivo_url"]
                ext = url.split(".")[-1].lower()
                if ext in ["jpg","jpeg","png"]:
                    st.image(url, use_container_width=True)
                else:
                    st.markdown(f"📄 [Ver archivo]({url})")
                st.download_button("⬇️ Descargar", url, file_name=f"{f['nombre']}.{ext}",
                                   key=f"dl_{f['id']}")
            st.markdown("---")
            total += float(f["importe"])

    st.metric(f"Total {trimestre_nombre}", f"{total:.2f} EUR")
