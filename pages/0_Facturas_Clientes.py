import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import calendar
from datetime import datetime
import io
import json
from supabase import create_client

st.set_page_config(page_title="Facturas Clientes - Cleo Pro", layout="centered")

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

def get_dato(clave, defecto):
    try:
        r = supabase.table("datos_app").select("valor").eq("clave", clave).execute()
        if r.data:
            return json.loads(r.data[0]["valor"])
        return defecto
    except:
        return defecto

# --- DATOS ---
CLIS = {
    "Lola":     {"n": "Maria Dolores Albero Moya", "f": "21422031S", "d": "Calle Alcalde Ramon Orts Galan, 7 Bungalow 52", "p": "03690 Sant Vicent del Raspeig", "t": 14.0, "h": 4.0, "w": [2], "v": True},
    "Yordhana": {"n": "Maria de los Angeles Yordhana Gomez Sanchez", "f": "48361127Q", "d": "Calle Santiago, 45", "p": "03690 Sant Vicent del Raspeig", "t": 14.0, "h": 4.0, "w": [3], "v": True},
    "Ania":     {"n": "Ania Rogala", "f": "---", "d": "Calle Confrides, 3  C.P.03560", "p": "El Campello", "t": 13.0, "h": 5.0, "w": [0, 1], "v": False}
}

MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

def calcular_dias(cliente_data, anio, mes_idx):
    cal = calendar.Calendar()
    return [f"{d:02d}/{mes_idx:02d}/{int(anio)}"
            for s in cal.monthdays2calendar(int(anio), mes_idx)
            for d, ds in s if d != 0 and ds in cliente_data["w"]]

def generar_imagen(cn, c, mi, anio, dias, num_factura, lineas_extra=None):
    if lineas_extra is None:
        lineas_extra = []

    # Canvas grande para que las letras se vean bien en móvil
    W, H = 800, 1400
    S = 2  # factor de escala respecto al diseño original

    img = Image.new('RGB', (W, H), "white")
    draw = ImageDraw.Draw(img)

    try:
        font_title  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_bold   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_normal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_small  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
        font_tiny   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    except:
        font_title = font_bold = font_normal = font_small = font_tiny = ImageFont.load_default()

    # Logo
    try:
        lg = Image.open("logo.jpeg")
        lg.thumbnail((600, 300))
        img.paste(lg, ((W - lg.width) // 2, 20))
        y_after_logo = 20 + lg.height + 15
    except:
        draw.text((W//2 - 40, 20), "CLEO PRO", font=font_title, fill="black")
        y_after_logo = 60

    # Cabecera
    if c["v"]:
        texto_cab = f"Nº Factura: {num_factura}" if num_factura else "Nº Factura: "
        draw.text((W - 280, y_after_logo), texto_cab, font=font_bold, fill="black")
    else:
        draw.text((W - 280, y_after_logo), "BONO MENSUAL", font=font_bold, fill="black")
    draw.text((W - 280, y_after_logo + 28), f"Fecha: 01/{mi:02d}/{int(anio)}", font=font_normal, fill="black")

    # Emisor y Cliente
    y_info = y_after_logo + 60
    draw.text((10, y_info), "EMISOR", font=font_bold, fill="black")
    for i, linea in enumerate(["Sandra Ramirez Galvez", "NIF: 78217908Z", "Urb. Alkabir Blq 5, pta i", "03560 El Campello"]):
        draw.text((10, y_info + 26 + i*22), linea, font=font_normal, fill=(60,60,60))

    draw.text((W//2 + 10, y_info), "CLIENTE", font=font_bold, fill="black")
    for i, linea in enumerate([c["n"], f"NIF: {c['f']}", c["d"], c["p"]]):
        draw.text((W//2 + 10, y_info + 26 + i*22), linea, font=font_normal, fill=(60,60,60))

    # Tabla
    y_tab = y_info + 160
    draw.rectangle([10, y_tab, W-10, y_tab+44], fill=(220,220,220))
    cols = [10, 200, 370, 500, 650]
    headers = ["DESCRIPCION", "FECHA", "HORAS", "PRECIO/H", "TOTAL"]
    for col, header in zip(cols, headers):
        draw.text((col+3, y_tab+12), header, font=font_bold, fill="black")

    y = y_tab + 55
    tot_f = 0.0
    for fecha in dias:
        sub = c["h"] * c["t"]
        tot_f += sub
        draw.text((cols[0]+3, y), "Servicio limpieza", font=font_normal, fill=(80,80,80))
        draw.text((cols[1]+3, y), fecha, font=font_normal, fill="black")
        draw.text((cols[2]+3, y), f"{c['h']}h", font=font_normal, fill="black")
        draw.text((cols[3]+3, y), f"{c['t']} EUR", font=font_normal, fill="black")
        draw.text((cols[4]+3, y), f"{sub:.2f} EUR", font=font_normal, fill="black")
        draw.line([(10, y+22), (W-10, y+22)], fill=(210,210,210))
        y += 28

    # Lineas extra
    for conc, precio in lineas_extra:
        draw.text((cols[0]+3, y), conc, font=font_normal, fill=(80,80,80))
        draw.text((cols[4]+3, y), f"{precio:+.2f} EUR", font=font_normal, fill=(180,0,0) if precio < 0 else (0,130,0))
        draw.line([(10, y+22), (W-10, y+22)], fill=(210,210,210))
        y += 28
        tot_f += precio

    # Totales
    y += 10
    if c["v"]:
        draw.text((cols[3], y), "BASE TOTAL:", font=font_bold, fill="black")
        draw.text((cols[4], y), f"{tot_f:.2f} EUR", font=font_normal, fill="black")
        draw.text((cols[3], y+26), "IVA (Exento):", font=font_bold, fill="black")
        draw.text((cols[4], y+26), "0,00 EUR", font=font_normal, fill="black")
        y += 55
    draw.line([(cols[3], y), (W-10, y)], fill="black", width=1)
    draw.text((cols[3], y+5), "TOTAL:", font=font_bold, fill="black")
    draw.text((cols[4], y+5), f"{tot_f:.2f} EUR", font=font_bold, fill=(0,100,0))

    # Pie
    y_pie = H - 160
    if c["v"]:
        draw.text((10, y_pie), "FORMA DE PAGO: Transferencia bancaria o Bizum", font=font_normal, fill="black")
        draw.text((10, y_pie+20), "IBAN: ES44 0182 0143 5202 0163 6882", font=font_normal, fill="black")
        draw.text((10, y_pie+40), "Bizum: 654 422 330", font=font_normal, fill="black")
        draw.text((10, y_pie+65), "Operacion exenta de IVA segun Art. 20.Uno.22 Ley 37/1992", font=font_tiny, fill=(130,130,130))
        draw.text((10, y_pie+80), "y acogida al Regimen de Franquicia de IVA (Directiva UE 2020/285)", font=font_tiny, fill=(130,130,130))
    if not c["v"]:
        draw.text((10, y_pie), "FORMA DE PAGO: En efectivo", font=font_normal, fill="black")
    draw.text((10, y_pie+110), "NOTA: Pago tipo Bono por adelantado.", font=font_small, fill=(100,100,100))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- UI ---
st.title("Facturas Clientes")

col1, col2 = st.columns(2)
with col1:
    mn = st.selectbox("Mes", MESES, index=datetime.now().month - 1)
with col2:
    anio = st.number_input("Año", min_value=2024, max_value=2035, value=datetime.now().year, step=1)

mi = MESES.index(mn) + 1
st.markdown("---")

col_l, col_y, col_a = st.columns(3)
if "cliente_sel" not in st.session_state:
    st.session_state["cliente_sel"] = "Lola"

with col_l:
    if st.button("Lola", use_container_width=True,
                 type="primary" if st.session_state["cliente_sel"] == "Lola" else "secondary"):
        st.session_state["cliente_sel"] = "Lola"
        st.rerun()
with col_y:
    if st.button("Yordhana", use_container_width=True,
                 type="primary" if st.session_state["cliente_sel"] == "Yordhana" else "secondary"):
        st.session_state["cliente_sel"] = "Yordhana"
        st.rerun()
with col_a:
    if st.button("Ania", use_container_width=True,
                 type="primary" if st.session_state["cliente_sel"] == "Ania" else "secondary"):
        st.session_state["cliente_sel"] = "Ania"
        st.rerun()

cn = st.session_state["cliente_sel"]
c = CLIS[cn]

dias_cal = calcular_dias(c, anio, mi)
key_dias_supabase = f"dias_{cn}_{mi}_{anio}"
num_dias_guardado = int(get_dato(key_dias_supabase, len(dias_cal)))
dias_defecto = dias_cal[:num_dias_guardado] if num_dias_guardado <= len(dias_cal) else dias_cal

key_dias_mod = f"dias_mod_{cn}_{mi}_{anio}"
if key_dias_mod not in st.session_state:
    st.session_state[key_dias_mod] = dias_defecto.copy()

dias_actuales = st.session_state[key_dias_mod]

key_nf = f"nf_{cn}_{mi}_{anio}"
if key_nf not in st.session_state:
    # Cargar desde Supabase
    st.session_state[key_nf] = get_dato(key_nf, "")
num_factura = st.session_state[key_nf]

key_lineas = f"lineas_extra_{cn}_{mi}_{anio}"
if key_lineas not in st.session_state:
    st.session_state[key_lineas] = []

img_bytes = generar_imagen(cn, c, mi, anio, dias_actuales, num_factura, st.session_state[key_lineas])
st.image(img_bytes, use_container_width=True)

st.markdown("---")

col_nf, col_env, col_mod = st.columns(3)

with col_nf:
    nuevo_nf = st.text_input("Número de factura", value=num_factura,
                              placeholder="Ej: 2025-003",
                              key=f"input_nf_{cn}_{mi}_{anio}",
                              label_visibility="collapsed")
    st.caption("Número factura")
    if nuevo_nf != num_factura:
        st.session_state[key_nf] = nuevo_nf
        supabase.table("datos_app").upsert({"clave": key_nf, "valor": json.dumps(nuevo_nf)}).execute()
        st.rerun()

with col_env:
    nombre_archivo = f"Factura_{cn}_{mn}_{int(anio)}.png" if c["v"] else f"Bono_{cn}_{mn}_{int(anio)}.png"
    st.download_button("📥 Guardar imagen", img_bytes, nombre_archivo, use_container_width=True)
    st.caption("Guarda en el dispositivo")

with col_mod:
    if st.button("✏️ Modificar factura", use_container_width=True):
        st.session_state[f"modo_edicion_{cn}_{mi}_{anio}"] = True

key_edicion = f"modo_edicion_{cn}_{mi}_{anio}"
if st.session_state.get(key_edicion, False):
    st.markdown("---")
    st.subheader("Modificar factura")

    st.markdown("**Días trabajados:**")
    nuevos_dias = []
    for d in dias_actuales:
        if st.checkbox(d, value=True, key=f"edit_chk_{d}_{cn}_{mi}_{anio}"):
            nuevos_dias.append(d)

    dia_extra = st.text_input("Añadir día extra (dd/mm/aaaa)", placeholder="Ej: 15/03/2025",
                               key=f"dia_extra_{cn}_{mi}_{anio}")
    if st.button("Añadir día", key=f"btn_dia_extra_{cn}_{mi}_{anio}"):
        if dia_extra and dia_extra not in nuevos_dias:
            nuevos_dias.append(dia_extra)

    st.markdown("**Líneas extra (devoluciones u otros conceptos):**")
    for idx, (conc, precio) in enumerate(st.session_state[key_lineas]):
        c1, c2, c3 = st.columns([3, 1, 0.5])
        with c1:
            st.write(conc)
        with c2:
            st.write(f"{precio:+.2f} EUR")
        with c3:
            if st.button("X", key=f"del_linea_{idx}_{cn}_{mi}_{anio}"):
                st.session_state[key_lineas].pop(idx)
                st.rerun()

    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        nuevo_conc = st.text_input("Concepto", placeholder="Ej: Devolucion 2h dia 05/02",
                                    key=f"nuevo_conc_{cn}_{mi}_{anio}", label_visibility="collapsed")
        st.caption("Concepto")
    with c2:
        nuevo_precio = st.number_input("Precio", min_value=-500.0, max_value=500.0,
                                        value=0.0, step=0.5,
                                        key=f"nuevo_precio_{cn}_{mi}_{anio}", label_visibility="collapsed")
        st.caption("Importe (negativo = devolucion)")
    with c3:
        st.write("")
        if st.button("Añadir línea", key=f"btn_linea_{cn}_{mi}_{anio}"):
            if nuevo_conc and nuevo_precio != 0:
                st.session_state[key_lineas].append((nuevo_conc, nuevo_precio))
                st.rerun()

    col_g, col_c2 = st.columns(2)
    with col_g:
        if st.button("💾 Guardar cambios", use_container_width=True, type="primary"):
            st.session_state[key_dias_mod] = nuevos_dias
            st.session_state[key_edicion] = False
            st.rerun()
    with col_c2:
        if st.button("Cancelar", use_container_width=True):
            st.session_state[key_edicion] = False
            st.rerun()
