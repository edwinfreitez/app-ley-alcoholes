import streamlit as st
import json
import re

# Configuración de página móvil/responsive
st.set_page_config(
    page_page_title="Buscador Legal de Alcoholes",
    page_icon="📜",
    layout="wide"
)

# Estilo personalizado para resaltado y tarjetas
st.markdown("""
    <style>
    .highlight {
        background-color: #ffe066;
        font-weight: bold;
        padding: 0px 4px;
        border-radius: 3px;
    }
    .card-ley {
        border-left: 5px solid #1F4E78;
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .card-reg {
        border-left: 5px solid #2E7D32;
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Cargar base de datos local JSON
@st.cache_data
def cargar_datos():
    # Carga el archivo JSON local
    with open('normativa.json', 'r', encoding='utf-8') as f:
        return json.load(f)

try:
    datos = cargar_datos()
except FileNotFoundError:
    st.error("No se encontró el archivo 'normativa.json'. Por favor agrégalo al repositorio.")
    st.stop()

# Encabezado
st.title("📜 Buscador Legal de Alcoholes")
st.caption("Ley y Reglamento de Impuesto sobre Alcohol y Especies Alcohólicas")

# Control de Filtros y Búsqueda
col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_input("🔍 Ingresa palabra clave:", placeholder="Ej. alícuota, registro, fianza, destilación...")

with col2:
    filtro_norma = st.selectbox("Norma:", ["Todas", "Ley", "Reglamento"])

# Función para resaltar coincidencias en HTML
def resaltar_texto(texto, busqueda):
    if not busqueda:
        return texto
    patron = re.compile(re.escape(busqueda), re.IGNORECASE)
    return patron.sub(lambda m: f'<span class="highlight">{m.group(0)}</span>', texto)

# Lógica del Buscador
if query.strip():
    query_lower = query.strip().lower()
    resultados = []
    total_coincidencias = 0

    for item in datos:
        # Filtro de norma
        if filtro_norma == "Ley" and item["norma"] != "LEY":
            continue
        if filtro_norma == "Reglamento" and item["norma"] != "REGLAMENTO":
            continue

        contenido = item["contenido"]
        articulo = item["articulo"]
        
        # Buscar en el contenido o en el número de artículo
        if query_lower in contenido.lower() or query_lower in articulo.lower():
            matches = len(re.findall(re.escape(query_lower), contenido, re.IGNORECASE))
            total_coincidencias += matches
            resultados.append((item, matches))

    # Métrica de resultados
    st.markdown(f"**Se encontraron {total_coincidencias} coincidencia(s) en {len(resultados)} artículo(s).**")
    st.divider()

    # Despliegue de tarjetas de resultados
    for item, matches in resultados:
        estilo_clase = "card-ley" if item["norma"] == "LEY" else "card-reg"
        etiqueta = "LEY" if item["norma"] == "LEY" else "REGLAMENTO"
        
        texto_resaltado = resaltar_texto(item["contenido"], query)
        
        st.markdown(f"""
            <div class="{estilo_clase}">
                <small><b>[{etiqueta}]</b> - {item['titulo']}</small><br>
                <h4 style="margin: 4px 0;">{item['articulo']}</h4>
                <p style="font-size: 14px; color: #333;">{texto_resaltado}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Expandible opcional para soporte con IA
        with st.expander(f"🤖 Interpretar {item['articulo']} con IA"):
            st.info("Para activar la interpretación en vivo, conecta tu API Key de Gemini/OpenAI en los Secrets de Streamlit.")
            st.write(f"**Texto de consulta:** {item['contenido']}")

else:
    st.info("Escribe una palabra en el campo superior para iniciar la búsqueda instantánea.")
