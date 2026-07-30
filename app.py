import streamlit as st
import psycopg2
import pandas as pd
from convocatorias.postulacion import mostrar_postulacion
from estudiantes.buscar_postulaciones import postulacion_estudiante

# 1. Configuración de título en la web
st.title("🎓 Sistema de Movilidad - ORI UNAL")

# 2. Función para conectar a la base de datos PostgreSQL
def obtener_conexion():
    return psycopg2.connect(
        host="localhost",
        port="5432", # o 3306 según tu config de Postgres
        database="db_dori_unal",
        user="postgres",
        password="JDM_RaspBerryPi68"
    )

# 3. Crear pestañas visuales para la UI
tab1, tab2, tab3 = st.tabs(["🎓 Estudiantes", "📢 Convocatorias", "📊 Histórico"])

with tab1:
    st.header("Listado de Estudiantes Postulantes")
    
    postulacion_estudiante(obtener_conexion)

with tab2:
    mostrar_postulacion(obtener_conexion)