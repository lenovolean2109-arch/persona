import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import os
from dotenv import load_dotenv

# --- 1. CARGA DE CONFIGURACIÓN SEGURA ---
load_dotenv()  # Carga la clave desde el archivo .env (Local)
api_key_env = os.getenv("GEMINI_API_KEY")

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Emochi Character Dashboard", page_icon="🤖", layout="wide")

# --- 3. ESTILOS PERSONALIZADOS (LIMPIOS Y VISIBLES) ---
st.markdown("""
    <style>
    /* Fondo general y fuentes */
    .main { background-color: #f8f9fa; color: #1f1f1f; }
    
    /* Botón Generar Profesional */
    .stButton>button { 
        width: 100%; 
        background-color: #ffaa00; 
        color: white; 
        font-weight: bold; 
        border-radius: 10px; 
        border: none;
        height: 3.5em;
        transition: 0.3s;
    }
    .stButton>button:hover { 
        background-color: #e69900; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Caja de estadísticas lateral */
    .stat-box { 
        background-color: white; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 6px solid #ffaa00;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. PERSISTENCIA DE DATOS (SESSION STATE) ---
if "personaje" not in st.session_state:
    st.session_state.personaje = {
        "nombre": "",
        "genero": "Andrógino",
        "arquetipo": "Ancla",
        "biografia": "",
        "listo": False
    }

# --- 5. FUNCIONES TÉCNICAS ---
def generar_personaje(nombre, genero, arquetipo, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Actúa como un psicólogo experto en narrativa. Crea una ficha para:
    - NOMBRE: {nombre}
    - GÉNERO: {genero}
    - ARQUETIPO: {arquetipo}

    REGLAS:
    1. Apariencia: (50-90 caracteres).
    2. Gustos/Disgustos: (Breve).
    3. Descripción Profunda: (1500-2500 caracteres) analizando su mentalidad.
    """
    response = model.generate_content(prompt)
    return response.text

def crear_pdf(datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"FICHA DE ENTIDAD: {datos['nombre']}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=11)
    # Limpieza para evitar errores en PDF con caracteres especiales
    texto_pdf = datos['biografia'].encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, txt=texto_pdf)
    
    return pdf.output(dest='S')

# --- 6. INTERFAZ DE USUARIO ---
st.title("🤖 Emochi: Character Builder")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("API Key de Gemini:", 
                            type="password", 
                            value=api_key_env if api_key_env else "")
    st.caption("Nota: La clave se carga del archivo .env o de los Secrets de Streamlit.")

# Layout Principal (Corregido)
col_input, col_display = st.columns(2)

with col_input:
    st.subheader("🛠 Parámetros")
    nombre_in = st.text_input("Nombre del Personaje:", value=st.session_state.personaje["nombre"])
    genero_in = st.selectbox("Género:", ["Masculino", "Femenino", "No binario", "Andrógino", "Fluido"])
    arquetipo_in = st.text_area("Arquetipo / Esencia:", value=st.session_state.personaje["arquetipo"])
    
    if st.button("🚀 Generar / Actualizar"):
        if not api_key:
            st.error("Por favor, introduce una API Key válida.")
        elif not nombre_in:
            st.warning("El personaje necesita un nombre.")
        else:
            with st.spinner("La IA está esculpiendo la entidad..."):
                try:
                    resultado = generar_personaje(nombre_in, genero_in, arquetipo_in, api_key)
                    st.session_state.personaje.update({
                        "nombre": nombre_in,
                        "genero": genero_in,
                        "arquetipo": arquetipo_in,
                        "biografia": resultado,
                        "listo": True
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"Error de API: {e}")

with col_display:
    if st.session_state.personaje["listo"]:
        st.success(f"✅ Entidad '{st.session_state.personaje['nombre']}' Sincronizada")
        
        st.markdown(f"**Arquetipo:** {st.session_state.personaje['arquetipo']}")
        st.info(st.session_state.personaje["biografia"])
        
        # Botón de Descarga
        pdf_bytes = crear_pdf(st.session_state.personaje)
        st.download_button(
            label="📥 Descargar Ficha PDF",
            data=pdf_bytes,
            file_name=f"Emochi_{st.session_state.personaje['nombre']}.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Define los parámetros y pulsa 'Generar' para visualizar la entidad.")

# --- 7. FOOTER ---
st.markdown("---")
st.caption("Emochi Dashboard v2.2 | Limpieza de Interfaz Completada | 2026")