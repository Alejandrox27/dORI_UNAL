import importlib
import pandas as pd
import psycopg2
import streamlit as st

import convocatorias.postulacion
# Forzar recarga del submódulo para desarrollos en Streamlit
importlib.reload(convocatorias.postulacion)

from convocatorias.postulacion import (
    mostrar_convenios,
    mostrar_convocatorias,
    mostrar_postulacion,
)

# 1. Configuración de título en la web
st.title("🎓 Sistema de Movilidad - ORI UNAL")


# 2. Función para conectar a la base de datos PostgreSQL
def obtener_conexion():
    return psycopg2.connect(
        host="localhost",
        port="5432",  # o 3306 según tu config de Postgres
        database="db_dori_unal",
        user="postgres",
        password="JDM_RaspBerryPi68",
    )


# 3. Crear pestañas visuales para la UI
tab1, tab2, tab3 = st.tabs(["🎓 Estudiantes", "📢 Convocatorias", "📊 Histórico"])

with tab1:
    st.header("Listado de Estudiantes Postulantes")

    # Consulta a PostgreSQL
    conn = obtener_conexion()
    query = "SELECT id_estudiante, nombre, apellidos, papa_acumulado, creditos_aprobados FROM estudiantes;"

    # Cargar datos en un DataFrame y mostrar la tabla visualmente
    df_estudiantes = pd.read_sql(query, conn)
    conn.close()

    # ¡Esta sola línea crea una tabla interactiva en la pantalla!
    st.dataframe(df_estudiantes)

with tab2:
    opcion = st.selectbox(
        "¿Qué deseas hacer?",
        ["Ver Convocatorias", "Ver Convenios", "Nueva Postulación"],
        key="menu_convocatorias",
    )

    if opcion == "Ver Convocatorias":
        mostrar_convocatorias(obtener_conexion)
    elif opcion == "Ver Convenios":
        mostrar_convenios(obtener_conexion)
    elif opcion == "Nueva Postulación":
        mostrar_postulacion(obtener_conexion)