import streamlit as st
import json
import re

# Configuración de pantalla y título del acceso directo
st.set_page_config(
    page_title="Ley Alcoholes",
    page_icon="📜",
    layout="wide"
)

# Estilo para tarjetas y resaltado (compatible con modo claro y oscuro)
st.markdown("""
    <style>
    .highlight {
        background-color: #ffe066;
        color: #000000;
        font-weight: bold;
        padding: 0px 4px;
        border-radius: 3px;
    }
    .card-ley {
        border-left: 5px solid #1F4E78;
        background-color: #ffffff;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 14px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.08);
    }
    .card-reg {
        border-left: 5px solid #2E7D32;
        background-color: #ffffff;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 14px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.08);
    }
    </style>
""", unsafe_allow_html=True)

# Cargar base de datos local
@st.cache_data
def cargar_datos():
    with open('normativa.json', 'r', encoding='utf-8') as f:
        return json.load(f)

try:
    datos = cargar_datos()
except FileNotFoundError:
    st.error("No se encontró el archivo 'normativa.json' en el repositorio.")
    st.stop()

st.title("📜 Buscador Legal de Alcoholes")
st.caption("Consulta interactiva de la Ley y Reglamento de Impuesto sobre Alcohol y Especies Alcohólicas")

# Campo de Búsqueda Principal
query = st.text_input("🔍 Buscar por palabra clave o número de artículo:", placeholder="Ej. alícuota, fianza, 12, destilación...")

# Selección por Botones / Pestañas
tab_todas, tab_ley, tab_reg = st.tabs(["📚 Todas las Normas", "🏛️ Solo Ley", "📋 Solo Reglamento"])

def resaltar_texto(texto, busqueda):
    if not busqueda:
        return texto
    patron = re.compile(re.escape(busqueda), re.IGNORECASE)
    return patron.sub(lambda m: f'<span class="highlight">{m.group(0)}</span>', texto)

def mostrar_resultados(filtro_norma):
    if not query.strip():
        st.info("Escribe un término en la barra superior para buscar entre los artículos.")
        return

    query_lower = query.strip().lower()
    resultados = []
    total_coincidencias = 0

    for item in datos:
        if filtro_norma != "TODAS" and item["norma"] != filtro_norma:
            continue

        contenido = item["contenido"]
        articulo = item["articulo"]
        titulo = item.get("titulo", "")

        # Coincidencia por contenido, artículo o título
        if (query_lower in contenido.lower() or 
            query_lower in articulo.lower() or 
            query_lower in titulo.lower()):
            
            matches = len(re.findall(re.escape(query_lower), contenido, re.IGNORECASE))
            total_coincidencias += max(matches, 1)
            resultados.append((item, matches))

    if resultados:
        st.markdown(f"**Coincidencias encontradas:** {len(resultados)} artículo(s).")
        st.divider()

        for item, matches in resultados:
            is_ley = (item["norma"] == "LEY")
            estilo_clase = "card-ley" if is_ley else "card-reg"
            etiqueta = "LEY" if is_ley else "REGLAMENTO"
            color_etiqueta = "#1F4E78" if is_ley else "#2E7D32"
            
            # Formato para números (1., 1.-, 1)), letras (a), b)) y parágrafos
            patron_subdivisiones = r'(\s)(\d+[\.\-\)]|[a-zA-Z]\)|Parágrafo\s+[A-ZÁÉÍÓÚa-zálíóú]+:)'
            contenido_formateado = re.sub(patron_subdivisiones, r'<br><br><b>\2</b>', item["contenido"])
            
            texto_resaltado = resaltar_texto(contenido_formateado, query)
            
            # Encabezado con color visible tanto en móvil como en laptop
            titulo_seccion = item.get('titulo', '')
            encabezado_html = f'<div style="color: {color_etiqueta}; font-size: 13px; font-weight: bold; margin-bottom: 4px;">[{etiqueta}] - {titulo_seccion}</div>'
            
            st.markdown(f"""
                <div class="{estilo_clase}">
                    {encabezado_html}
                    <h4 style="margin: 2px 0 8px 0; color: #111111;">{item['articulo']}</h4>
                    <div style="font-size: 15px; color: #222222; line-height: 1.6;">{texto_resaltado}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning(f"No se encontraron resultados para '{query}' en esta sección.")

# Renderizar contenido según la pestaña seleccionada
with tab_todas:
    mostrar_resultados("TODAS")

with tab_ley:
    mostrar_resultados("LEY")

with tab_reg:
    mostrar_resultados("REGLAMENTO")
