import streamlit as st
import pandas as pd

def postulacion_estudiante(obtener_conexion=None):
    st.header("¿A qué convocatorias puedes postularte?")
    # Formulario para insertar datos del estuidante
    # y obtener convocatorias disponibles para dicho estudiante
    with st.form("form_estudiante_postulacion"):
        estudiante_id = st.number_input("Documento del Estudiante", step=1)
        unidad_organizacional_id = st.number_input("ID Unidad Organizacional", min_value=1)
        nombre_estudiante = st.text_input("Nombre del Estudiante")
        apellidos_estudiante = st.text_input("Apellidos del Estudiante")
        correo_instucional = st.text_input("Correo Institucional")
        papa_acumulado = st.number_input("PAPA Acumulado", min_value=0.0, max_value=5.0, step=0.01)
        creditos_aprobados = st.number_input("Créditos Aprobados", min_value=0)
        #prioridad = st.selectbox("Prioridad de Opción", [1, 2, 3])
        
        # Botón de envío
        btn_envio = st.form_submit_button("Registrar Postulación")
        
        if btn_envio:
            # sql
            conn = obtener_conexion()
            cursor = conn.cursor()
            query_insert = """INSERT INTO estudiantes (id_estudiante, id_unidad_organizacional, nombre, apellidos, correo_institucional, papa_acumulado, creditos_aprobados)
                              VALUES (%s, %s, %s, %s, %s, %s, %s)"""

            cursor.execute(query_insert, (estudiante_id, unidad_organizacional_id, nombre_estudiante, apellidos_estudiante, correo_instucional, papa_acumulado, creditos_aprobados))
            cursor.connection.commit()


            query = """SELECT
                        c.id_convocatoria,
                        c.nombre_convocatoria
                    FROM estudiantes e
                    JOIN unidades_organizacionales u 
                        ON u.id_unidad = e.id_unidad_organizacional
                    JOIN postulaciones p 
                        ON p.id_estudiante = e.id_estudiante
                    JOIN convocatorias c 
                        ON c.id_convocatoria = p.id_convocatoria
                    WHERE
                        e.id_estudiante = """ + str(estudiante_id) + """
                        AND 
                        e.papa_acumulado >= GREATEST(COALESCE(c.papa_minimo_requerido, 3.5), 3.5)
                        AND ((e.creditos_aprobados::DECIMAL / u.creditos_totales_programa) * 100) >= COALESCE(c.porcentaje_creditos_minimo, 40)
                        AND NOT EXISTS (
                            SELECT 1 
                            FROM sanciones_disciplinarias sd
                            WHERE sd.id_estudiante = e.id_estudiante
                            AND (sd.fecha_fin IS NULL OR sd.fecha_fin >= CURRENT_DATE)
                        );"""
                
            # Cargar datos en un DataFrame y mostrar la tabla visualmente
            cursor.execute(query, (estudiante_id,))
            cursor.close()
            df_estudiantes = pd.read_sql(query, conn)
            conn.close()
            st.success("¡Postulación registrada con éxito!")