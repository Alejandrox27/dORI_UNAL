import importlib
import pandas as pd
import psycopg2
import streamlit as st

# 1. Configuración de la página en Streamlit (debe ser la primera llamada de Streamlit)
st.set_page_config(
    page_title="Sistema de Movilidad - ORI UNAL",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

import convocatorias.postulacion
import estudiantes.buscar_postulaciones

# Forzar recarga de submódulos para desarrollos en Streamlit
importlib.reload(convocatorias.postulacion)
importlib.reload(estudiantes.buscar_postulaciones)

from convocatorias.postulacion import (
    mostrar_convenios,
    mostrar_convocatorias,
    mostrar_reportes,
)
from estudiantes.buscar_postulaciones import postulacion_estudiante

# 2. Inyección de CSS personalizado para armonizar con el Escudo de la UNAL
st.markdown(
    """
    <style>
    /* Estilos globales y paleta UNAL */
    :root {
        --unal-green: #046A38;
        --unal-green-dark: #004D25;
        --unal-green-light: #EBF3EE;
        --unal-accent: #80B035;
    }
    
    /* Personalización del Header */
    .unal-header {
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 15px 20px;
        background-color: #ffffff;
        border-radius: 12px;
        border-left: 6px solid var(--unal-green);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 25px;
    }
    
    .unal-header h1 {
        color: var(--unal-green);
        margin: 0;
        font-size: 2.1rem;
        font-weight: 700;
    }
    
    .unal-header p {
        color: #555;
        margin: 2px 0 0 0;
        font-size: 1.0rem;
    }
    
    /* Tarjeta de integrantes y materia */
    .team-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 4px solid var(--unal-green);
        border-radius: 10px;
        padding: 20px;
        margin-top: 30px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    .team-title {
        color: var(--unal-green);
        font-weight: bold;
        font-size: 1.15rem;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .team-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 10px;
        margin-top: 10px;
    }
    
    .team-member {
        background-color: var(--unal-green-light);
        padding: 10px 14px;
        border-radius: 8px;
        font-size: 0.92rem;
        color: #1E293B;
        border-left: 3px solid var(--unal-green);
    }
    
    .team-member strong {
        color: var(--unal-green-dark);
    }
    
    /* Botones y pestañas */
    .stButton>button {
        background-color: var(--unal-green) !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        font-weight: 600 !important;
    }
    
    .stButton>button:hover {
        background-color: var(--unal-green-dark) !important;
    }
    
    /* Ajustes generales */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--unal-green-light) !important;
        color: var(--unal-green) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. Encabezado principal con el Escudo de la UNAL
col_logo, col_title = st.columns([1, 5], vertical_alignment="center")

with col_logo:
    st.image("images/00f00EscudoUN2016.jpg", use_container_width=True)

with col_title:
    st.markdown(
        """
        <div style="padding-left: 10px;">
            <h1 style="color: #046A38; margin: 0; font-size: 2.2rem;"> Sistema de Movilidad - ORI UNAL</h1>
            <p style="color: #4A5568; margin: 4px 0 0 0; font-size: 1.05rem; font-weight: 500;">
                Universidad Nacional de Colombia — Dirección de Relaciones Exteriores (DORI)
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# 4. Configuración de la Barra Lateral (Sidebar)
with st.sidebar:
    st.image("images/00f00EscudoUN2016.jpg", width=160)
    st.title("ORI UNAL")
    st.caption("Sistema de Gestión de Convocatorias y Movilidad Académica")
    
    st.divider()
    st.markdown("### Asignatura")
    st.markdown("**Bases de Datos**")
    
    st.divider()
    st.markdown("### Integrantes")
    st.markdown("""
    -  **Didier Alejandro Mejia Merchan**  
      `1025323509`
    -  **Samuel Emanuel Daniel Alvarez Torres**  
      `1027522564`
    -  **Alejandro Santos Nivia**  
      `1028486932`
    -  **Jean Carlo Triana Guzmán**  
      `1025140412`
    -  **Santiago Cedeño Sabogal**  
      `1031807186`
    """)


# 5. Función para conectar a la base de datos PostgreSQL
def obtener_conexion():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="db_dori_unal",
        user="postgres",
        password="JDM_RaspBerryPi68",
    )


# 6. Pestañas visuales para la UI
tab1, tab2, tab3 = st.tabs([" Estudiantes", " Convocatorias", " Histórico"])

with tab1:
    st.header("Listado de Estudiantes Postulantes")
    
    postulacion_estudiante(obtener_conexion)

with tab2:
    opcion = st.selectbox(
        "Lista de opciones:",
        [
            "Ver Convocatorias",
            "Ver Convenios",
            "Reportes y Estadísticas",
        ],
        key="menu_convocatorias",
    )

    if opcion == "Ver Convocatorias":
        mostrar_convocatorias(obtener_conexion)
    elif opcion == "Ver Convenios":
        mostrar_convenios(obtener_conexion)
    elif opcion == "Reportes y Estadísticas":
        mostrar_reportes(obtener_conexion)

with tab3:
    st.header("Histórico de Movilidad")
    st.info("Sección de registros históricos de convocatorias y postulaciones.")

# 7. Pie de página (Footer) con los créditos del proyecto
st.markdown(
    """
    <div class="team-card">
        <div class="team-title">
            Proyecto Final de Bases de Datos — Universidad Nacional de Colombia
        </div>
        <p style="margin: 0 0 10px 0; color: #4A5568; font-size: 0.95rem;">
            <strong>Materia:</strong> Bases de Datos | <strong>Sección:</strong> DORI UNAL
        </p>
        <div class="team-grid">
            <div class="team-member"><strong>Didier Alejandro Mejia Merchan</strong><br><small>CC: 1025323509</small></div>
            <div class="team-member"><strong>Samuel Emanuel Daniel Alvarez Torres</strong><br><small>CC: 1027522564</small></div>
            <div class="team-member"><strong>Alejandro Santos Nivia</strong><br><small>CC: 1028486932</small></div>
            <div class="team-member"><strong>Jean Carlo Triana Guzmán</strong><br><small>CC: 1025140412</small></div>
            <div class="team-member"><strong>Santiago Cedeño Sabogal</strong><br><small>CC: 1031807186</small></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
