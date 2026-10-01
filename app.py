import streamlit as st
import json
import re

# Configuración de pantalla y título del acceso directo
st.set_page_config(
    page_title="Ley Alcoholes",
    page_icon="📜",
    layout="wide"
)

# Estilo para tarjetas, resaltado y encabezado DUSA ajustado
st.markdown("""
    <style>
    /* Reducir el espacio superior general de la página Streamlit */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
    }

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
    
    /* Estilos del encabezado con espacio compacto arriba y mayor interlineado interno */
    .header-container {
        display: flex;
        align-items: center;
        gap: 15px;
        background-color: #f8f9fa;
        padding: 10px 16px;
        border-radius: 8px;
        margin-top: 0px;
        margin-bottom: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .header-container img {
        border-radius: 4px;
        object-fit: contain;
    }
    .titulo-mini {
        font-size: 16px;
        font-weight: bold;
        color: #1a252f;
        margin: 0 0 4px 0; /* Separación hacia el subtítulo */
        text-transform: uppercase;
        line-height: 1.2;
    }
    .subtitulo-mini {
        font-size: 14px;
        font-weight: bold;
        color: #2c3e50;
        margin: 0 0 3px 0; /* Separación hacia el autor */
        line-height: 1.2;
    }
    .autor-text {
        font-size: 12px;
        color: #2980b9;
        margin: 0;
        line-height: 1.2;
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

# ENCABEZADO
URL_LOGO = "https://media.licdn.com/dms/image/v2/C4E0BAQGROeCPt2-5rQ/company-logo_200_200/company-logo_200_200/0/1630651014568/destileras_unidas_s_a_logo?e=2147483647&v=beta&t=4KCIm7iySF8w6uXTN9ISvF6zPFRGhe8L3MTN2oGJh34"

st.markdown(f"""
    <div class="header-container">
        <img src="{URL_LOGO}" width="50">
        <div>
            <p class="titulo-mini">Buscador Ley de Alcoholes</p>
            <p class="subtitulo-mini">Destilerías Unidas, S.A.</p>
            <p class="autor-text">© Edwin Freitez</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
