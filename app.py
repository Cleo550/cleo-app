import streamlit as st
from fpdf import FPDF
from datetime import datetime
import calendar
import io

# --- DATOS FISCALES ---
NOMBRE_EMISOR = "Sandra Ramírez Gálvez"
NIF_EMISOR = "78217908Z"
DIR_EMISOR = "Urb. Alkabir Blq 5, pta i, El Campello"
POB_EMISOR = "03560 El Campello"

st.set_page_config(page_title="Cleo Pro", layout="centered")

# Configuración de clientes
clientes_fijo = {
    "Lola": {"nombre": "María Dolores Albero Moya", "nif": "21422031S", "dir": "Calle Alcalde Ramón Orts Galán, 7 Bungalow 52", "pob": "03690 Sant Vicent del Raspeig", "tarifa": 14.0, "legal": True, "dias_semana": [2]},
    "Yordhana": {"nombre": "María de los Ángeles Yordhana Gómez Sánchez", "nif": "48361127Q", "dir": "Calle Santiago, 45", "pob": "03690 Sant Vicent del Raspeig", "tarifa": 14.0, "legal": True, "dias_semana": [3]},
    "Ania": {"nombre": "Ania Rogala", "nif": "", "dir": "Calle Confrides, 3, C.P.03560", "pob": "El Campello", "tarifa": 13.0, "legal": False, "dias_semana": [0, 1]}
}

def contar_dias_mes(año, mes, dias_objetivo):
    cal = calendar.Calendar()
    semanas = cal.monthdays2calendar(año, mes)
    contador = 0
    for semana in semanas:
        for dia, dia_semana in semana:
            if dia != 0 and dia_semana in dias_objetivo:
                contador += 1
    return contador

def crear_documento(cli_key, n_fact, horas, mes_nombre, año):
    cli = clientes_fijo[cli_key]
    pdf = FPDF()
    pdf.add_page()
    
    try:
        pdf.image('logo.jpeg', 85, 10, 40)
    except:
        pass
    
    pdf.set_font('Arial', 'B', 14)
    pdf.set_y(45)
    pdf.cell(0, 10, 'SERVICIO DE LIMPIEZA', 0, 1, 'C')
    
    pdf.set_font('Arial', '', 10)
    pdf.set_xy(110, 15)
    meses_n = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_num = meses_n.index(mes_nombre) + 1
    fecha_doc = f"01/{mes_num:02d}/{año}"
    
    if cli["legal"]:
        pdf.cell(50, 8,
                
