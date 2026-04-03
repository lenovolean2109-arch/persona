import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import os
from dotenv import load_dotenv

# --- 1. CARGA DE CONFIGURACIÓN SEGURA ---
load_dotenv()  # Carga la clave desde el archivo .env (Local)
api_key_env = os.getenv("GEMINI_API_KEY")

# --- 2. CONFIGURACIÓN DE PÁGINA Y ESTILOS ---
st.set_page_config(page_title="Emochi Character Dashboard", page_icon="🤖", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stTextInput, .stTextArea { background-color: #161b22 !important; }
    .character-stat { font-size: 14px; font-weight: bold; color: #ffaa00; }
    </style>
    """, unsafe_allow_html=True)  # <-- CAMBIA 'index' POR 'html' AQUÍ

# --- 3. INICIALIZACIÓN DEL ESTADO (PERSISTENCIA) ---
if "personaje" not in st.session_state:
    st.session_state.personaje = {
        "nombre": "",
        "genero": "Andrógino",
        "arquetipo": "Ancla",
        "biografia": "",
        "listo": False
    }

# --- 4. FUNCIONES TÉCNICAS ---
def generar_personaje(nombre, genero, arquetipo, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Actúa como un psicólogo experto en narrativa para la app Emochi.
    Crea una ficha detallada para:
    - NOMBRE: {nombre}
    - GÉNERO: {genero}
    - ARQUETIPO: {arquetipo}

    REGLAS DE FORMATO:
    1. APARIENCIA: (50-90 caracteres).
    2. GUSTOS: (50-90 caracteres).
    3. DISGUSTOS: (50-90 caracteres).
    4. DESCRIPCIÓN PROFUNDA: (1500-2500 caracteres). Analiza su mentalidad basada en el arquetipo {arquetipo}.
    """
    response = model.generate_content(prompt)
    return response.text

def crear_pdf(datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"FICHA DE ENTIDAD: {datos['nombre']}", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(200, 10, txt=f"Arquetipo: {datos['arquetipo']} | Género: {datos['genero']}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=11)
    # Limpieza de caracteres para evitar errores de codificación Latin-1
    texto_limpio = datos['biografia'].encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, txt=texto_limpio)
    
    return pdf.output(dest='S')

# --- 5. INTERFAZ DE USUARIO ---
st.title("🤖 Emochi: Character Builder")

# Sidebar para la API Key (Prioriza .env, luego Secrets de Streamlit, luego manual)
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("API Key de Gemini:", 
                            type="password", 
                            value=api_key_env if api_key_env else "")
    st.caption("La clave se toma automáticamente del archivo .env si existe.")

col_input, col_display = st.columns(2)

with col_input:
    st.subheader("🛠 Parámetros")
    nombre = st.text_input("Nombre del Personaje:", value=st.session_state.personaje["nombre"])
    genero = st.selectbox("Género:", ["Masculino", "Femenino", "No binario", "Andrógino", "Fluido"], 
                          index=["Masculino", "Femenino", "No binario", "Andrógino", "Fluido"].index(st.session_state.personaje["genero"]))
    
    # APARTADO DE ARQUETIPO: El motor de actualización
    arquetipo = st.text_area("Arquetipo / Esencia:", 
                             value=st.session_state.personaje["arquetipo"], 
                             help="Cambia esto para actualizar la personalidad de la IA.")
    
    if st.button("🚀 Generar / Actualizar"):
        if not api_key:
            st.error("❌ Falta la API Key.")
        elif not nombre:
            st.warning("⚠️ El personaje necesita un nombre.")
        else:
            with st.spinner("La IA está esculpiendo la psique..."):
                try:
                    resultado = generar_personaje(nombre, genero, arquetipo, api_key)
                    # Actualizamos el estado global
                    st.session_state.personaje.update({
                        "nombre": nombre,
                        "genero": genero,
                        "arquetipo": arquetipo,
                        "biografia": resultado,
                        "listo": True
                    })
                    st.rerun() # Refresca para mostrar cambios
                except Exception as e:
                    st.error(f"Error: {e}")

with col_display:
    if st.session_state.personaje["listo"]:
        st.success(f"✅ Entidad '{st.session_state.personaje['nombre']}' Sincronizada")
        
        with st.container():
            st.markdown(f"### Análisis del Arquetipo: **{st.session_state.personaje['arquetipo']}**")
            st.info(st.session_state.personaje["biografia"])
            
            # Generación de PDF desde el estado actual
            pdf_bytes = crear_pdf(st.session_state.personaje)
            st.download_button(
                label="📥 Descargar Ficha PDF",
                data=pdf_bytes,
                file_name=f"Emochi_{st.session_state.personaje['nombre']}.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("Define los parámetros y pulsa 'Generar' para visualizar la entidad.")

# --- FOOTER ---
st.markdown("---")
st.caption("Emochi Dashboard v2.1 | Conexión Segura habilitada | 2026")