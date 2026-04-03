import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import os
from dotenv import load_dotenv

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
load_dotenv()

# Intentamos obtener la clave desde Secrets (nube) o .env (local)
if "GEMINI_API_KEY" in st.secrets:
    api_key_env = st.secrets["GEMINI_API_KEY"]
else:
    api_key_env = os.getenv("GEMINI_API_KEY")

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Emochi Builder Pro", page_icon="🤖", layout="wide")

# --- 3. ESTILOS (CORREGIDOS) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; background-color: #ffaa00; color: white; 
        font-weight: bold; border-radius: 10px; border: none; height: 3em;
    }
    .stButton>button:hover { background-color: #e69900; }
    .biografia-container { 
        background-color: #ffffff; padding: 20px; border-radius: 10px;
        border-left: 5px solid #ffaa00; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNCIONES (ACTUALIZADAS PARA EVITAR ERROR 404) ---
def generar_personaje(nombre, genero, arquetipo, key):
    genai.configure(api_key=key)
    # Usamos el nombre de modelo más estándar y estable
    model = genai.GenerativeModel('gemini-1.5-flash-latest') 
    
    prompt = f"Actúa como psicólogo narrativo. Crea una ficha detallada para: {nombre}, género {genero}, arquetipo {arquetipo}. Describe su mentalidad en profundidad."
    
    response = model.generate_content(prompt)
    return response.text

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
st.title("🤖 Emochi: Character Builder")

with st.sidebar:
    st.header("🔑 Configuración")
    api_key_input = st.text_input("Gemini API Key:", type="password", 
                                  value=api_key_env if api_key_env else "")
    if api_key_input:
        st.success("✅ Clave lista")
    else:
        st.error("❌ Falta API Key")

col_in, col_out = st.columns(2)

with col_in:
    st.subheader("🛠 Parámetros")
    nombre = st.text_input("Nombre del Personaje:")
    genero = st.selectbox("Género:", ["Andrógino", "Masculino", "Femenino", "Fluido", "No binario"])
    arquetipo = st.text_area("Arquetipo / Esencia:", "Ancla")
    
    boton = st.button("🚀 Generar Entidad")

with col_out:
    if boton:
        if not api_key_input:
            st.error("Error: Introduce una clave válida.")
        elif not nombre:
            st.warning("El personaje necesita un nombre.")
        else:
            with st.spinner("Conectando con la consciencia artificial..."):
                try:
                    biografia = generar_personaje(nombre, genero, arquetipo, api_key_input)
                    st.success(f"Entidad '{nombre}' manifestada.")
                    st.markdown(f'<div class="biografia-container">{biografia}</div>', unsafe_allow_html=True)
                    
                    pdf_bytes = crear_pdf({"nombre": nombre, "biografia": biografia})
                    st.download_button(label="📥 Descargar PDF", data=pdf_bytes, 
                                       file_name=f"Emochi_{nombre}.pdf", mime="application/pdf")
                except Exception as e:
                    # Si el error 404 persiste, intentamos con el nombre corto del modelo
                    st.error(f"Error de conexión: {e}")
    else:
        st.info("Configura los parámetros y pulsa 'Generar'.")
