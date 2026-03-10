import streamlit as st
from fpdf import FPDF
from datetime import datetime
import calendar
import io

# --- DATOS FISCALES (Sandra Ramírez Gálvez) ---
NOMBRE_EMISOR = "Sandra Ramírez Gálvez"
NIF_EMISOR = "78217908Z"
DIR_EMISOR = "Urb. Alkabir Blq 5, pta i, El Campello"
POB_EMISOR = "03560 El Campello"

st.set_page_config(page_title="Cleo Pro", layout="centered")

# --- DATOS CLIENTES ---
clientes_fijo = {
    "Lola": {"nombre": "María Dolores Albero Moya", "nif": "21422031S", "dir": "Calle Alcalde Ramón Orts Galán, 7 Bungalow 52", "pob": "03690 Sant Vicent del Raspeig", "tarifa": 14.0, "legal": True},
    "Yordhana": {"nombre": "María de los Ángeles Yordhana Gómez Sánchez", "nif": "48361127Q", "dir": "Calle Santiago, 45", "pob": "03690 Sant Vicent del Raspeig", "tarifa": 14.0, "legal": True},
    "Ania": {"nombre": "Ania Rogala", "nif": "", "dir": "Calle Confrides, 3, C.P.03560", "pob": "El Campello", "tarifa": 13.0, "legal": False}
}

# --- FUNCIÓN PARA CREAR EL DOCUMENTO ---
def crear_documento(cli_key, n_fact, horas, mes_nombre):
    cli = clientes_fijo[cli_key]
    pdf = FPDF()
    pdf.add_page()
    
    # Intentar poner tu logo.jpeg
    try: pdf.image('logo.jpeg', 85, 10, 40)
    except: pass
    
    pdf.set_font('Arial', 'B', 14)
    pdf.set_y(45)
    pdf.cell(0, 10, 'SERVICIO DE LIMPIEZA', 0, 1, 'C')
    
    # Recuadro Fecha/Número
    pdf.set_font('Arial', '', 10)
    pdf.set_xy(110, 15)
    if cli["legal"]:
        pdf.cell(50, 8, f'FACTURA Nº: {n_fact}', 1, 0, 'C')
        pdf.cell(40, 8, f'FECHA: 01/{datetime.now().strftime("%m/%Y")}', 1, 1, 'C')
    else:
        pdf.cell(90, 8, f'FECHA: 01/{datetime.now().strftime("%m/%Y")}', 1, 1, 'C')

    # Bloque Emisor y Cliente
    pdf.set_y(65)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(95, 5, 'EMISOR', 0, 0)
    pdf.cell(95, 5, 'CLIENTE', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(95, 5, f'Nombre: {NOMBRE_EMISOR}', 0, 0)
    pdf.cell(95, 5, f'Nombre: {cli["nombre"]}', 0, 1)
    pdf.cell(95, 5, f'NIF: {NIF_EMISOR}', 0, 0)
    pdf.cell(95, 5, f'NIF: {cli["nif"]}', 0, 1)
    pdf.cell(95, 5, f'Dirección: {DIR_EMISOR}', 0, 0)
    pdf.cell(95, 5, f'Dirección: {cli["dir"]}', 0, 1)
    pdf.cell(95, 5, f'Población: {POB_EMISOR}', 0, 0)
    pdf.cell(95, 5, f'Población: {cli["pob"]}', 0, 1)

    # Tabla de servicios
    pdf.ln(15)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(80, 8, 'DESCRIPCIÓN', 1, 0, 'C')
    pdf.cell(30, 8, 'HORAS', 1, 0, 'C')
    pdf.cell(40, 8, 'PRECIO/H', 1, 0, 'C')
    pdf.cell(40, 8, 'TOTAL', 1, 1, 'C')
    
    total_bruto = horas * cli["tarifa"]
    pdf.set_font('Arial', '', 10)
    pdf.cell(80, 8, f'Servicio limpieza {mes_nombre}', 1)
    pdf.cell(30, 8, str(horas), 1, 0, 'C')
    pdf.cell(40, 8, f'{cli["tarifa"]:.2f} €', 1, 0, 'C')
    pdf.cell(40, 8, f'{total_bruto:.2f} €', 1, 1, 'C')

    # Totales e IRPF
    pdf.ln(5)
    if cli["legal"]:
        irpf = total_bruto * 0.20
        pdf.cell(150, 8, 'Retención IRPF (20%)', 0, 0, 'R')
        pdf.cell(40, 8, f'-{irpf:.2f} €', 1, 1, 'C')
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(150, 10, 'TOTAL A PERCIBIR', 0, 0, 'R')
        pdf.cell(40, 10, f'{total_bruto - irpf:.2f} €', 1, 1, 'C')
        pdf.set_font('Arial', 'I', 8)
        pdf.ln(5)
        pdf.multi_cell(0, 4, 'Operación exenta de IVA según el Art. 20.Uno.22º de la Ley 37/1992.')
    else:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(150, 10, 'TOTAL NETO', 0, 0, 'R')
        pdf.cell(40, 10, f'{total_bruto:.2f} €', 1, 1,

