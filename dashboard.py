import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import os
from dotenv import load_dotenv

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
load_dotenv()
# Prioridad: 1. Secrets de Streamlit, 2. Archivo .env
if "OPENAI_API_KEY" in st.secrets:
    api_key_env = st.secrets["OPENAI_API_KEY"]
else:
    api_key_env = os.getenv("OPENAI_API_KEY")

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Emochi Builder Pro", page_icon="🤖", layout="wide")

# --- 3. ESTILOS VISUALES ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; background-color: #00A67E; color: white; 
        font-weight: bold; border-radius: 10px; border: none; height: 3em;
    }
    .stButton>button:hover { background-color: #008f6c; }
    .biografia-container { 
        background-color: #ffffff; padding: 20px; border-radius: 10px;
        border-left: 5px solid #00A67E; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        color: #1f1f1f;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNCIÓN DE IA (AHORA CON CHATGPT) ---
def generar_personaje(nombre, genero, arquetipo, key):
    client = OpenAI(api_key=key)
    
    prompt = f"Actúa como psicólogo narrativo. Crea una ficha detallada para: {nombre}, género {genero}, arquetipo {arquetipo}."
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", # O usa "gpt-4" si tienes acceso
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices.message.content

def crear_pdf(datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"FICHA EMOCHI: {datos['nombre']}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    texto_limpio = datos['biografia'].encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, txt=texto_limpio)
    return pdf.output(dest='S')

# --- 5. INTERFAZ ---
st.title("🤖 Emochi: Character Builder (ChatGPT Version)")

with st.sidebar:
    st.header("🔑 Configuración")
    api_key_input = st.text_input("OpenAI API Key:", type="password", value=api_key_env if api_key_env else "")
    if api_key_input:
        st.success("✅ Clave detectada")
    else:
        st.error("❌ Falta API Key")

col_in, col_out = st.columns(2)

with col_in:
    st.subheader("🛠️ Parámetros")
    nombre = st.text_input("Nombre del Personaje:")
    genero = st.selectbox("Género:", ["Andrógino", "Masculino", "Femenino", "Fluido", "No binario"])
    arquetipo = st.text_area("Arquetipo / Esencia:", "Ancla")
    boton = st.button("🚀 Generar Entidad")

with col_out:
    if boton:
        if not api_key_input:
            st.error("Error: Revisa la API Key en la barra lateral.")
        elif not nombre:
            st.warning("El personaje necesita un nombre.")
        else:
            with st.spinner("Consultando con la mente de ChatGPT..."):
                try:
                    biografia = generar_personaje(nombre, genero, arquetipo, api_key_input)
                    st.success(f"Entidad '{nombre}' manifestada.")
                    st.markdown(f'<div class="biografia-container">{biografia}</div>', unsafe_allow_html=True)
                    
                    pdf_bytes = crear_pdf({"nombre": nombre, "biografia": biografia})
                    st.download_button(label="📥 Descargar PDF", data=pdf_bytes, file_name=f"Emochi_{nombre}.pdf", mime="application/pdf")
                except Exception as e:
                    st.error(f"Error técnico con OpenAI: {e}")
    else:
        st.info("Configura los parámetros y pulsa 'Generar'.")
