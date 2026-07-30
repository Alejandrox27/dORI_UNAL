import streamlit as st
import psycopg2
import pandas as pd

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
    
    # Consulta a PostgreSQL
    conn = obtener_conexion()
    query = "SELECT id_estudiante, nombre, apellidos, papa_acumulado, creditos_aprobados FROM estudiantes;"
    
    # Cargar datos en un DataFrame y mostrar la tabla visualmente
    df_estudiantes = pd.read_sql(query, conn)
    conn.close()
    
    # ¡Esta sola línea crea una tabla interactiva en la pantalla!
    st.dataframe(df_estudiantes)

with tab2:
    st.header("Nueva Postulación")
    # Formulario rápido para insertar datos
    with st.form("form_postulacion"):
        estudiante_id = st.text_input("Documento del Estudiante")
        convocatoria_id = st.number_input("ID Convocatoria", min_value=1)
        prioridad = st.selectbox("Prioridad de Opción", [1, 2, 3])
        
        # Botón de envío
        btn_guardar = st.form_submit_button("Registrar Postulación")
        
        if btn_guardar:
            # Aquí ejecutas el INSERT INTO postulaciones...
            st.success("¡Postulación registrada con éxito!")