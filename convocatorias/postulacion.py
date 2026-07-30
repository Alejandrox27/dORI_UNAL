import streamlit as st

def mostrar_postulacion(obtener_conexion=None):
    st.header("Nueva Postulación")
    # Formulario rápido para insertar datos
    with st.form("form_postulacion"):
        estudiante_id = st.text_input("Documento del Estudiante")
        convocatoria_id = st.number_input("ID Convocatoria", min_value=1)
        prioridad = st.selectbox("Prioridad de Opción", [1, 2, 3])
        
        # Botón de envío
        btn_guardar = st.form_submit_button("Registrar Postulación")
        
        if btn_guardar:
            # sql
            st.success("¡Postulación registrada con éxito!")
