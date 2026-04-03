import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import os
from dotenv import load_dotenv

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
load_dotenv()
# Prioridad: Secrets de Streamlit > archivo .env
api_key_env = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Emochi Builder Pro", page_icon="🤖", layout="wide")

# --- 3. ESTILOS VISUALES (CORRECCIÓN DE LECTURA) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; background-color: #ffaa00; color: white; 
        font-weight: bold; border-radius: 10px; border: none; height: 3em;
    }
    .biografia-container { 
        background-color: #ffffff; padding: 20px; border-radius: 10px;
        border-left: 5px solid #ffaa00; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        color: #1f1f1f; white-space: pre-wrap;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNCIÓN DE GENERACIÓN CON REGLAS ESTRICTAS ---
def generar_personaje(nombre, genero, arquetipo, key):
    genai.configure(api_key=key)
    # Modelo estable para evitar error 404
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Actúa como un escritor experto en psicología de personajes para la app Emochi.
    Crea una ficha para el personaje '{nombre}', de género '{genero}' y arquetipo '{arquetipo}'.
    
    REGLAS ESTRICTAS DE SALIDA (FORMATO TEXTO PLANO):
    1. Apariencia: Exactamente entre 50 y 90 caracteres (con espacios).
    2. Gustos: Exactamente entre 50 y 90 caracteres (con espacios).
    3. Disgustos: Exactamente entre 50 y 90 caracteres (con espacios).
    4. Descripción Profunda: Exactamente entre 1500 y 2500 caracteres (con espacios). Debe incluir Mentalidad y Rasgos.
    5. Prompt Visual: Sin límite, detallado, estilo 3D Octane Render, 8k.
    """
    
    response = model.generate_content(prompt)
    return response.text

def crear_pdf(datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"FICHA EMOCHI: {datos['nombre']}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    # Codificación segura para evitar errores de símbolos
    texto_limpio = datos['biografia'].encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, txt=texto_limpio)
    return pdf.output(dest='S')

# --- 5. INTERFAZ DE USUARIO ---
st.title("🤖 Emochi: Character Builder")

with st.sidebar:
    st.header("🔑 Configuración")
    # Se muestra "Clave cargada" si se detecta en el sistema
    api_key_input = st.text_input("Gemini API Key:", type="password", 
                                  value=api_key_env if api_key_env else "")
    
    if api_key_input:
        st.success("✅ Clave cargada")
    else:
        st.error("❌ Falta API Key")

col_input, col_display = st.columns(2)

with col_input:
    st.subheader("🛠 Parámetros")
    nombre = st.text_input("Nombre del Personaje:")
    genero = st.selectbox("Género:", ["Andrógino", "Masculino", "Femenino", "Fluido", "No binario"])
    arquetipo = st.text_area("Arquetipo / Esencia:", "Ancla")
    
    boton_generar = st.button("🚀 Generar / Actualizar")

with col_display:
    # --- LÓGICA DE GENERACIÓN ---
    if boton_generar:
        if not api_key_input:
            st.error("Por favor, introduce una API Key válida.")
        elif not nombre:
            st.warning("⚠️ El personaje necesita un nombre.")
        else:
            with st.spinner("Esculpiendo la psique del personaje..."):
                try:
                    resultado = generar_personaje(nombre, genero, arquetipo, api_key_input)
                    st.success(f"Entidad '{nombre}' manifestada.")
                    
                    # Mostrar resultado en pantalla
                    st.markdown(f'<div class="biografia-container">{resultado}</div>', unsafe_allow_html=True)
                    
                    # Generación de PDF
                    pdf_bytes = crear_pdf({"nombre": nombre, "biografia": resultado})
                    st.download_button(
                        label="📥 Descargar Ficha (PDF)",
                        data=pdf_bytes,
                        file_name=f"Emochi_{nombre}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Hubo un problema con la API: {e}")
    else:
        st.info("Define los parámetros y pulsa 'Generar' para visualizar la entidad.")
