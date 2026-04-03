import streamlit as st
from google import genai
from fpdf import FPDF
import os
from dotenv import load_dotenv

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
load_dotenv()
# Prioridad: Secrets de Streamlit > variable de entorno .env
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Emochi Builder Pro", page_icon="🤖", layout="wide")

# --- 3. ESTILOS VISUALES ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; background-color: #ffaa00; color: white; 
        font-weight: bold; border-radius: 10px; border: none; height: 3em;
    }
    .biografia-container { 
        background-color: #ffffff; padding: 25px; border-radius: 10px;
        border-left: 5px solid #ffaa00; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        color: #1f1f1f; white-space: pre-wrap;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LÓGICA DE IA (NUEVO SDK) ---
def generar_personaje(nombre, genero, arquetipo, key):
    # Inicialización del cliente con el nuevo SDK de Google
    client = genai.Client(api_key=key)
    
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
    
    # Uso de gemini-1.5-flash para máxima estabilidad y evitar errores 404
    response = client.models.generate_content(
        model="gemini-1.5-flash", 
        contents=prompt
    )
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

# --- 5. INTERFAZ DE USUARIO ---
st.title("🤖 Emochi: Character Builder")

with st.sidebar:
    st.header("🔑 Configuración")
    api_key_input = st.text_input("Gemini API Key:", type="password", value=api_key if api_key else "")
    
    if api_key_input:
        st.success("✅ Clave cargada")
    else:
        st.error("❌ Falta API Key")

col_in, col_out = st.columns()

with col_in:
    st.subheader("🛠 Parámetros")
    nombre = st.text_input("Nombre del Personaje:")
    genero = st.selectbox("Género:", ["Andrógino", "Masculino", "Femenino", "Fluido", "No binario"])
    arquetipo = st.text_area("Arquetipo / Esencia:", "Ancla")
    
    boton_generar = st.button("🚀 Generar Entidad")

with col_out:
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
                    st.success(f"¡Entidad '{nombre}' manifestada!")
                    
                    st.markdown(f'<div class="biografia-container">{resultado}</div>', unsafe_allow_html=True)
                    
                    pdf_bytes = crear_pdf({"nombre": nombre, "biografia": resultado})
                    st.download_button("📥 Descargar PDF", pdf_bytes, f"Emochi_{nombre}.pdf", "application/pdf")
                except Exception as e:
                    # Captura de errores de cuota y conexión
                    st.error(f"Error técnico detectado: {e}")
    else:
        st.info("Configura los parámetros y pulsa 'Generar'.")
