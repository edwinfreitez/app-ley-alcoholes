import streamlit as st
import json
import re

# Configuración de pantalla y título del acceso directo
st.set_page_config(
    page_title="Ley Alcoholes",
    page_icon="📜",
    layout="wide"
)

# Estilo para tarjetas, resaltado y encabezado corporativo
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
    
    /* Contenedor del encabezado al estilo DUSA */
    .header-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 18px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .header-logo {
        width: 75px;
        height: auto;
        background-color: #ffffff;
        padding: 6px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .header-title {
        font-size: 17px;
        font-weight: bold;
        color: #2c3e50;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0;
    }
    .header-subtitle {
        font-size: 15px;
        font-weight: bold;
        color: #1a252f;
        margin: 2px 0 0 0;
    }
    .header-author {
        font-size: 13px;
        color: #2980b9;
        margin: 2px 0 0 0;
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

# --- ENCABEZADO ESTILO DUSA ---
# Logo DUSA oficial en SVG vectorizado
logo_dusa_svg = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 100" width="100%">
  <circle cx="40" cy="50" r="28" fill="#a6192e"/>
  <ellipse cx="40" cy="50" rx="20" ry="10" fill="none" stroke="#ffffff" stroke-width="3" transform="rotate(-30 40 50)"/>
  <ellipse cx="40" cy="50" rx="20" ry="10" fill="none" stroke="#ffffff" stroke-width="3" transform="rotate(30 40 50)"/>
  <text x="80" y="62" font-family="Arial, sans-serif" font-weight="900" font-size="34" fill="#a6192e" letter-spacing="1">DUSA</text>
</svg>
"""

st.markdown(f"""
    <div class="header-box">
        <div class="header-logo">
            {logo_dusa_svg}
        </div>
        <div>
            <div class="header-title">BUSCADOR LEY DE ALCOHOLES</div>
            <div class="header-subtitle">Destilerías Unidas, S.A.</div>
            <div class="header-author">© Edwin Freitez</div>
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
