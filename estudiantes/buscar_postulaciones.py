import streamlit as st
import pandas as pd

def postulacion_estudiante(obtener_conexion=None):
    st.markdown("### Registro de Estudiante y Convocatorias Disponibles")
    st.caption("Selecciona tu Sede, Facultad y Programa académico para identificar las convocatorias a las que puedes postularte según tus méritos académicos.")

    if obtener_conexion is None:
        st.error("No se proporcionó una función de conexión a la base de datos.")
        return

    # 1. Cargar unidades organizacionales en cascada (Sede -> Facultad -> Programa)
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()

        # Cargar Sedes
        cursor.execute("SELECT id_unidad, nombre FROM unidades_organizacionales WHERE tipo = 'Sede' ORDER BY nombre;")
        sedes = cursor.fetchall()

    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return
    finally:
        if 'conn' in locals() and conn:
            conn.close()

    if not sedes:
        st.warning("No se encontraron Sedes registradas en la base de datos.")
        return

    st.subheader("1. Selección de Unidad Organizacional")
    col_sede, col_fac, col_prog = st.columns(3)

    with col_sede:
        sede_seleccionada = st.selectbox(
            "Sede / Ciudad *",
            options=sedes,
            format_func=lambda s: s[1],
            key="select_sede"
        )
        sede_id = sede_seleccionada[0] if sede_seleccionada else None

    # Cargar Facultades de la Sede seleccionada
    facultades = []
    if sede_id:
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_unidad, nombre FROM unidades_organizacionales WHERE tipo = 'Facultad' AND id_unidad_padre = %s ORDER BY nombre;",
                (sede_id,)
            )
            facultades = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            st.error(f"Error al cargar Facultades: {e}")

    with col_fac:
        if facultades:
            facultad_seleccionada = st.selectbox(
                "Facultad *",
                options=facultades,
                format_func=lambda f: f[1],
                key="select_facultad"
            )
            facultad_id = facultad_seleccionada[0] if facultad_seleccionada else None
        else:
            st.selectbox("Facultad *", options=["Sin facultades disponibles"], disabled=True)
            facultad_id = None

    # Cargar Programas de la Facultad seleccionada (directos o a través de un departamento)
    programas = []
    if facultad_id:
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.id_unidad, p.nombre, p.creditos_totales_programa 
                FROM unidades_organizacionales p 
                LEFT JOIN unidades_organizacionales d ON p.id_unidad_padre = d.id_unidad 
                WHERE p.tipo = 'Programa' AND (p.id_unidad_padre = %s OR d.id_unidad_padre = %s) 
                ORDER BY p.nombre;
                """,
                (facultad_id, facultad_id)
            )
            programas = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            st.error(f"Error al cargar Programas: {e}")

    with col_prog:
        if programas:
            programa_seleccionado = st.selectbox(
                "Programa Académico *",
                options=programas,
                format_func=lambda p: f"{p[1]} ({p[2]} cr. tot.)" if p[2] else p[1],
                key="select_programa"
            )
            programa_id = programa_seleccionado[0] if programa_seleccionado else None
            creditos_totales = programa_seleccionado[2] if programa_seleccionado else None
        else:
            st.selectbox("Programa Académico *", options=["Sin programas disponibles"], disabled=True)
            programa_id = None
            creditos_totales = None

    if programa_id:
        st.info(f" **Programa Seleccionado:** {programa_seleccionado[1]} | **ID Unidad:** `{programa_id}` | **Créditos Totales del Programa:** `{creditos_totales if creditos_totales else 'No especificado'}`")
    else:
        st.warning("Por favor selecciona una Sede, Facultad y Programa para continuar.")
        return

    st.markdown("---")
    st.subheader("2. Información del Estudiante")

    # Formulario para datos del estudiante
    with st.form("form_estudiante_postulacion"):
        col1, col2 = st.columns(2)

        with col1:
            estudiante_id = st.number_input(
                "Documento de Identidad (CC / TI) *",
                min_value=0,
                step=1,
                help="Ingresa tu número de documento sin puntos ni comas."
            )
            nombre_estudiante = st.text_input(
                "Nombre(s) *",
                placeholder="Ej. Juan Andrés"
            )
            apellidos_estudiante = st.text_input(
                "Apellidos *",
                placeholder="Ej. Pérez Gómez"
            )

        with col2:
            correo_institucional = st.text_input(
                "Correo Institucional *",
                placeholder="usuario@unal.edu.co"
            )
            papa_acumulado = st.number_input(
                "PAPA Acumulado *",
                min_value=0.0,
                max_value=5.0,
                step=0.01,
                format="%.2f",
                help="Promedio Académico Ponderado Acumulado (0.00 a 5.00)"
            )
            creditos_aprobados = st.number_input(
                "Créditos Aprobados *",
                min_value=0,
                step=1,
                help="Número total de créditos aprobados a la fecha"
            )

        st.caption("Nota: Los campos marcados con (*) son obligatorios.")
        btn_envio = st.form_submit_button("Guardar Datos y Buscar Convocatorias")

    # 3. Validación y Guardado en Base de Datos
    if btn_envio:
        # Validaciones de campos obligatorios
        errores = []
        if estudiante_id <= 0:
            errores.append("El Documento de Identidad debe ser un número mayor a 0.")
        if not nombre_estudiante.strip():
            errores.append("El campo Nombre(s) es obligatorio.")
        if not apellidos_estudiante.strip():
            errores.append("El campo Apellidos es obligatorio.")
        if not correo_institucional.strip():
            errores.append("El Correo Institucional es obligatorio.")
        elif "@" not in correo_institucional:
            errores.append("Ingresa un Correo Institucional válido (ej. usuario@unal.edu.co).")

        if errores:
            for error in errores:
                st.error(f" {error}")
            return

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()

            # Insertar o actualizar estudiante (UPSERT)
            query_upsert = """
                INSERT INTO estudiantes (
                    id_estudiante, id_unidad_organizacional, nombre, apellidos, 
                    correo_institucional, papa_acumulado, creditos_aprobados
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id_estudiante) DO UPDATE SET
                    id_unidad_organizacional = EXCLUDED.id_unidad_organizacional,
                    nombre = EXCLUDED.nombre,
                    apellidos = EXCLUDED.apellidos,
                    correo_institucional = EXCLUDED.correo_institucional,
                    papa_acumulado = EXCLUDED.papa_acumulado,
                    creditos_aprobados = EXCLUDED.creditos_aprobados;
            """
            cursor.execute(
                query_upsert,
                (
                    estudiante_id,
                    programa_id,
                    nombre_estudiante.strip(),
                    apellidos_estudiante.strip(),
                    correo_institucional.strip(),
                    papa_acumulado,
                    creditos_aprobados
                )
            )
            conn.commit()
            st.success("Datos del estudiante guardados y actualizados con éxito en la base de datos.")

            # Guardar información del estudiante en la sesión para el formulario de inscripción
            st.session_state["estudiante_activo"] = {
                "id_estudiante": estudiante_id,
                "nombre": f"{nombre_estudiante.strip()} {apellidos_estudiante.strip()}",
                "programa_id": programa_id,
                "papa": papa_acumulado,
                "creditos": creditos_aprobados
            }

            cursor.close()
            conn.close()

        except Exception as e:
            st.error(f"Error al procesar los datos del estudiante: {e}")
            return

    # 4. Si hay un estudiante activo en la sesión, buscar y mostrar sus convocatorias disponibles
    if "estudiante_activo" in st.session_state and st.session_state["estudiante_activo"]["id_estudiante"] > 0:
        est_info = st.session_state["estudiante_activo"]
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()

            query_convocatorias = """
                SELECT 
                    c.id_convocatoria AS "ID",
                    c.nombre_convocatoria AS "Convocatoria",
                    conv.codigo_convenio AS "Código Convenio",
                    us.nombre_oficial AS "Universidad Socia",
                    COALESCE(p.nombre_oficial, 'No especificado') AS "País",
                    c.periodo_academico AS "Periodo",
                    COALESCE(c.papa_minimo_requerido, 3.5) AS "PAPA Mínimo",
                    COALESCE(c.porcentaje_creditos_minimo, 40) AS "Porcentaje Créditos Mínimo",
                    c.fecha_cierre AS "Fecha Cierre"
                FROM convocatorias c
                JOIN convenios conv ON conv.id_convenio = c.id_convenio
                JOIN universidades_socias us ON us.id_universidad = conv.id_universidad
                LEFT JOIN paises p ON p.id_pais = us.pais
                JOIN unidades_organizacionales u ON u.id_unidad = %s
                WHERE 
                    %s >= GREATEST(COALESCE(c.papa_minimo_requerido, 3.5), 3.5)
                    AND ((%s::DECIMAL / NULLIF(u.creditos_totales_programa, 0)) * 100) >= COALESCE(c.porcentaje_creditos_minimo, 40)
                    AND (c.fecha_cierre IS NULL OR c.fecha_cierre >= CURRENT_DATE)
                    AND conv.estado_legal = 'Activo'
                    AND NOT EXISTS (
                        SELECT 1 FROM sanciones_disciplinarias sd
                        WHERE sd.id_estudiante = %s
                          AND (sd.fecha_fin IS NULL OR sd.fecha_fin >= CURRENT_DATE)
                    )
                ORDER BY c.fecha_cierre ASC;
            """
            cursor.execute(
                query_convocatorias,
                (est_info["programa_id"], est_info["papa"], est_info["creditos"], est_info["id_estudiante"])
            )
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()

            cursor.close()
            conn.close()

            st.markdown("---")
            st.markdown("### Convocatorias Habilitadas para Ti")
            if filas:
                df_convocatorias = pd.DataFrame(filas, columns=columnas)
                st.metric("Convocatorias disponibles", len(df_convocatorias))
                st.dataframe(df_convocatorias, use_container_width=True)

                st.markdown("---")
                st.subheader("Inscribirse a una Convocatoria")
                st.write("Selecciona una de las convocatorias habilitadas de la lista para registrar tu postulación:")

                # Crear mapa de opciones para el selectbox
                opciones_convocatorias = {
                    f"{row[0]} - {row[1]} ({row[3]})": row[0] for row in filas
                }

                with st.form("form_inscribirse_convocatoria"):
                    conv_seleccionada_label = st.selectbox(
                        "Selecciona la Convocatoria *",
                        options=list(opciones_convocatorias.keys())
                    )
                    prioridad_opcion = st.selectbox(
                        "Prioridad de Opción *",
                        options=[1, 2, 3],
                        help="1 = Primera opción, 2 = Segunda opción, 3 = Tercera opción"
                    )

                    btn_postular = st.form_submit_button(" Confirmar y Registrar Postulación")

                if btn_postular:
                    id_convocatoria_elegida = opciones_convocatorias[conv_seleccionada_label]
                    try:
                        conn = obtener_conexion()
                        cursor = conn.cursor()

                        # Registrar la postulación mediante el procedimiento almacenado sp_registrar_postulacion
                        cursor.execute(
                            "CALL sp_registrar_postulacion(%s, %s, %s);",
                            (est_info["id_estudiante"], id_convocatoria_elegida, prioridad_opcion)
                        )
                        conn.commit()
                        cursor.close()
                        conn.close()

                        st.success(
                            f"¡Postulación registrada con éxito! La postulación ha quedado registrada con estado 'Enviada' para el estudiante {est_info['id_estudiante']}."
                        )
                        st.info("Puedes verificar tus postulaciones activas en la pestaña **'Mis Postulaciones'**.")

                    except Exception as e:
                        error_msg = str(e)
                        if "llave duplicada" in error_msg.lower() or "duplicate key" in error_msg.lower():
                            try:
                                conn = obtener_conexion()
                                cursor = conn.cursor()
                                cursor.execute("SELECT setval(pg_get_serial_sequence('historico_estados_postulacion', 'id_historico'), COALESCE((SELECT MAX(id_historico) FROM historico_estados_postulacion), 1));")
                                cursor.execute("SELECT setval(pg_get_serial_sequence('postulaciones', 'id_postulacion'), COALESCE((SELECT MAX(id_postulacion) FROM postulaciones), 1));")
                                conn.commit()
                                
                                cursor.execute(
                                    "CALL sp_registrar_postulacion(%s, %s, %s);",
                                    (est_info["id_estudiante"], id_convocatoria_elegida, prioridad_opcion)
                                )
                                conn.commit()
                                cursor.close()
                                conn.close()

                                st.success(
                                    f"¡Postulación registrada con éxito! La postulación ha quedado registrada con estado 'Enviada' para el estudiante {est_info['id_estudiante']}."
                                )
                                st.info("Puedes verificar tus postulaciones activas en la pestaña **'Mis Postulaciones'**.")
                                return
                            except Exception as retry_err:
                                error_msg = str(retry_err)

                        if "ya esta postulado" in error_msg.lower():
                            st.warning("Ya estás postulado a esta convocatoria.")
                        elif "maximo permitido" in error_msg.lower():
                            st.warning("Has alcanzado el límite máximo permitido de postulaciones activas para este periodo.")
                        else:
                            st.error(f"No se pudo registrar la postulación: {error_msg}")

            else:
                st.warning("No se encontraron convocatorias activas que cumplan con tus requisitos académicos actuales (PAPA o % de créditos mínimos).")

        except Exception as e:
            st.error(f"Error al consultar convocatorias: {e}")


def mostrar_mis_postulaciones(obtener_conexion=None):
    st.markdown("### Mis Postulaciones")
    st.caption("Consulta el estado actual de tus postulaciones ingresando tu número de documento de identidad.")

    if obtener_conexion is None:
        st.error("No se proporcionó una función de conexión a la base de datos.")
        return

    with st.form("form_buscar_mis_postulaciones"):
        doc_estudiante = st.number_input(
            "Documento de Identidad (CC / TI) *",
            min_value=0,
            step=1,
            help="Ingresa el documento con el que te postulaste."
        )
        btn_consultar = st.form_submit_button(" Consultar Mis Postulaciones")

    if btn_consultar:
        if doc_estudiante <= 0:
            st.error("Por favor ingresa un número de documento válido.")
            return

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()

            # Consultar información del estudiante
            cursor.execute(
                "SELECT nombre, apellidos, correo_institucional FROM estudiantes WHERE id_estudiante = %s;",
                (doc_estudiante,)
            )
            est_data = cursor.fetchone()

            # Consultar las postulaciones del estudiante
            query_mis_postulaciones = """
                SELECT 
                    p.id_postulacion AS "ID Postulación",
                    c.nombre_convocatoria AS "Convocatoria",
                    us.nombre_oficial AS "Universidad Destino",
                    COALESCE(pais.nombre_oficial, 'No especificado') AS "País",
                    c.periodo_academico AS "Periodo",
                    p.prioridad_opcion AS "Prioridad",
                    p.fecha_postulacion AS "Fecha Postulación",
                    p.estado_actual AS "Estado Actual"
                FROM postulaciones p
                JOIN convocatorias c ON c.id_convocatoria = p.id_convocatoria
                JOIN convenios conv ON conv.id_convenio = c.id_convenio
                JOIN universidades_socias us ON us.id_universidad = conv.id_universidad
                LEFT JOIN paises pais ON pais.id_pais = us.pais
                WHERE p.id_estudiante = %s
                ORDER BY p.fecha_postulacion DESC;
            """
            cursor.execute(query_mis_postulaciones, (doc_estudiante,))
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()

            cursor.close()
            conn.close()

            if est_data:
                st.success(f"Estudiante: **{est_data[0]} {est_data[1]}** ({est_data[2]}) | Documento: `{doc_estudiante}`")
            
            if filas:
                df_post = pd.DataFrame(filas, columns=columnas)
                st.metric("Total de Postulaciones", len(df_post))
                st.dataframe(df_post, use_container_width=True)
            else:
                st.info(f"No se encontraron postulaciones registradas para el documento {doc_estudiante}.")

        except Exception as e:
            st.error(f"Error al consultar postulaciones: {e}")