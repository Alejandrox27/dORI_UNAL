import datetime
import pandas as pd
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


def mostrar_convenios(obtener_conexion):
    """Muestra los convenios de la UNAL con filtros interactivos."""
    st.header("Convenios Vigentes de la UNAL")

    # ── Cargar datos completos (JOIN de 3 tablas) ──
    conn = obtener_conexion()
    query = """
        SELECT
            c.id_convenio,
            c.codigo_convenio   AS "Codigo",
            u.nombre_oficial    AS "Universidad Socia",
            p.nombre_oficial    AS "Pais",
            c.tipo_convenio     AS "Tipo",
            c.fecha_inicio      AS "Inicio Vigencia",
            c.fecha_vencimiento AS "Fin Vigencia",
            c.estado_legal      AS "Estado"
        FROM Convenios c
        JOIN Universidades_socias u ON u.id_universidad = c.id_universidad
        JOIN paises p               ON p.id_pais        = u.pais
        ORDER BY c.fecha_vencimiento DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        st.info("No se encontraron convenios registrados en la base de datos.")
        return

    # ── Filtros ──
    st.subheader("🔎 Filtros")
    col1, col2, col3 = st.columns(3)

    with col1:
        opciones_estado = ["Todos"] + sorted(df["Estado"].unique().tolist())
        filtro_estado = st.selectbox(
            "Estado del convenio", opciones_estado, key="flt_estado"
        )

    with col2:
        opciones_pais = ["Todos"] + sorted(df["Pais"].unique().tolist())
        filtro_pais = st.selectbox("País", opciones_pais, key="flt_pais")

    with col3:
        opciones_tipo = ["Todos"] + sorted(df["Tipo"].unique().tolist())
        filtro_tipo = st.selectbox(
            "Tipo de convenio", opciones_tipo, key="flt_tipo"
        )

    # Filtro adicional por universidad (depende del país seleccionado)
    if filtro_pais != "Todos":
        universidades_filtradas = sorted(
            df.loc[df["Pais"] == filtro_pais, "Universidad Socia"].unique().tolist()
        )
    else:
        universidades_filtradas = sorted(df["Universidad Socia"].unique().tolist())

    opciones_uni = ["Todas"] + universidades_filtradas
    filtro_uni = st.selectbox(
        "Universidad socia", opciones_uni, key="flt_uni"
    )

    # ── Aplicar filtros ──
    df_filtrado = df.copy()

    if filtro_estado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Estado"] == filtro_estado]

    if filtro_pais != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Pais"] == filtro_pais]

    if filtro_tipo != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Tipo"] == filtro_tipo]

    if filtro_uni != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Universidad Socia"] == filtro_uni]

    # ── Mostrar resultados ──
    st.divider()
    st.caption(f"Mostrando {len(df_filtrado)} de {len(df)} convenios")

    # Ocultar el id interno y renombrar columnas para visualización en pantalla
    df_visual = df_filtrado.drop(columns=["id_convenio"]).rename(
        columns={"Codigo": "Código", "Pais": "País"}
    )

    st.dataframe(
        df_visual,
        use_container_width=True,
        hide_index=True,
    )


def mostrar_convocatorias(obtener_conexion):
    """Muestra todas las convocatorias disponibles con filtros por país, universidad y periodo."""
    st.header("📢 Convocatorias de Movilidad")

    # ── Consulta SQL con JOIN a Convenios, Universidades_socias y paises ──
    conn = obtener_conexion()
    query = """
        SELECT
            conv.id_convocatoria            AS "ID Convocatoria",
            conv.nombre_convocatoria        AS "Nombre Convocatoria",
            u.nombre_oficial                AS "Universidad Socia",
            p.nombre_oficial                AS "Pais",
            conv.periodo_academico          AS "Periodo",
            c.codigo_convenio               AS "Codigo Convenio",
            c.tipo_convenio                 AS "Tipo Convenio",
            conv.fecha_apertura             AS "Apertura",
            conv.fecha_cierre               AS "Cierre",
            conv.papa_minimo_requerido      AS "PAPA Minimo",
            conv.porcentaje_creditos_minimo AS "Creditos Min %"
        FROM Convocatorias conv
        JOIN Convenios c            ON c.id_convenio    = conv.id_convenio
        JOIN Universidades_socias u ON u.id_universidad = c.id_universidad
        JOIN paises p               ON p.id_pais        = u.pais
        ORDER BY conv.fecha_apertura DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        st.info("No hay convocatorias registradas actualmente en el sistema.")
        return

    # ── Filtros interactivos ──
    st.subheader("🔎 Filtros de Convocatorias")
    col1, col2, col3 = st.columns(3)

    with col1:
        opciones_pais = ["Todos"] + sorted(df["Pais"].unique().tolist())
        filtro_pais = st.selectbox("País", opciones_pais, key="flt_conv_pais")

    with col2:
        opciones_periodo = ["Todos"] + sorted(df["Periodo"].unique().tolist())
        filtro_periodo = st.selectbox(
            "Periodo Académico", opciones_periodo, key="flt_conv_periodo"
        )

    with col3:
        filtro_vigencia = st.selectbox(
            "Estado de Convocatoria",
            ["Todas", "Vigentes / Abiertas"],
            key="flt_conv_vigencia",
        )

    # Filtro secundario de universidad dependiente del país seleccionado
    if filtro_pais != "Todos":
        universidades_disponibles = sorted(
            df.loc[df["Pais"] == filtro_pais, "Universidad Socia"].unique().tolist()
        )
    else:
        universidades_disponibles = sorted(
            df["Universidad Socia"].unique().tolist()
        )

    opciones_uni = ["Todas"] + universidades_disponibles
    filtro_uni = st.selectbox(
        "Universidad Socia", opciones_uni, key="flt_conv_uni"
    )

    # ── Aplicar filtros en pandas ──
    df_filtrado = df.copy()

    if filtro_pais != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Pais"] == filtro_pais]

    if filtro_periodo != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Periodo"] == filtro_periodo]

    if filtro_uni != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Universidad Socia"] == filtro_uni]

    if filtro_vigencia == "Vigentes / Abiertas":
        hoy = pd.to_datetime(datetime.date.today())
        # Convertir fecha_cierre a datetime para comparar
        cierres = pd.to_datetime(df_filtrado["Cierre"])
        df_filtrado = df_filtrado[(cierres.isna()) | (cierres >= hoy)]

    # ── Visualización de la tabla ──
    st.divider()
    st.caption(f"Mostrando {len(df_filtrado)} de {len(df)} convocatorias")

    # Renombrar columna para pantalla visual con tilde
    df_visual = df_filtrado.rename(
        columns={"Pais": "País", "Codigo Convenio": "Código Convenio"}
    )

    st.dataframe(
        df_visual,
        use_container_width=True,
        hide_index=True,
    )


def mostrar_reportes(obtener_conexion):
    """Muestra estadísticas y reportes analíticos basados en consultas agregadas."""
    st.header("📊 Reportes y Estadísticas del Sistema")

    sub_opcion = st.radio(
        "Selecciona el reporte a consultar:",
        [
            "📈 Cantidad de postulaciones por convocatoria",
            "🏛️ Universidades con más de 2 convenios activos",
            "🎯 Convocatorias con exigencia de PAPA superior al promedio de postulantes",
        ],
        key="sub_menu_reportes",
    )

    conn = obtener_conexion()

    if sub_opcion == "📈 Cantidad de postulaciones por convocatoria":
        st.subheader("📈 Total de Postulaciones por Convocatoria")
        query_4 = """
            SELECT
                c.id_convocatoria        AS "ID Convocatoria",
                c.nombre_convocatoria    AS "Convocatoria",
                COUNT(p.id_postulacion)  AS "Total Postulaciones"
            FROM Postulaciones p
            JOIN Convocatorias c ON p.id_convocatoria = c.id_convocatoria
            GROUP BY c.id_convocatoria, c.nombre_convocatoria
            ORDER BY COUNT(p.id_postulacion) DESC;
        """
        df4 = pd.read_sql(query_4, conn)

        if not df4.empty:
            st.dataframe(df4, use_container_width=True, hide_index=True)
            # Gráfico de barras interactivo
            st.bar_chart(df4.set_index("Convocatoria")["Total Postulaciones"])
        else:
            st.info("No hay datos de postulaciones por convocatoria.")

    elif sub_opcion == "🏛️ Universidades con más de 2 convenios activos":
        st.subheader("🏛️ Universidades Socias Destacadas (> 2 Convenios Activos)")
        query_6 = """
            SELECT
                us.id_universidad   AS "ID Universidad",
                us.nombre_oficial    AS "Universidad Socia",
                COUNT(c.id_convenio) AS "Total Convenios Activos"
            FROM Universidades_socias us
            JOIN Convenios c ON us.id_universidad = c.id_universidad
            WHERE c.estado_legal = 'Activo'
            GROUP BY us.id_universidad, us.nombre_oficial
            HAVING COUNT(c.id_convenio) > 2
            ORDER BY COUNT(c.id_convenio) DESC;
        """
        df6 = pd.read_sql(query_6, conn)

        if not df6.empty:
            st.dataframe(df6, use_container_width=True, hide_index=True)
        else:
            st.info("No hay universidades socias con más de 2 convenios activos.")

    elif sub_opcion == "🎯 Convocatorias con exigencia de PAPA superior al promedio de postulantes":
        st.subheader("🎯 Convocatorias con PAPA Exigido Alto (> Promedio de Postulantes)")
        query_10 = """
            SELECT
                c.id_convocatoria       AS "ID Convocatoria",
                c.nombre_convocatoria   AS "Convocatoria",
                c.papa_minimo_requerido AS "PAPA Mínimo Requerido",
                ROUND((
                    SELECT AVG(e.papa_acumulado)
                    FROM Postulaciones p
                    JOIN Estudiantes e ON e.id_estudiante = p.id_estudiante
                    WHERE p.id_convocatoria = c.id_convocatoria
                ), 2) AS "PAPA Promedio Postulantes"
            FROM Convocatorias c
            WHERE c.papa_minimo_requerido > (
                SELECT AVG(e.papa_acumulado)
                FROM Postulaciones p
                JOIN Estudiantes e ON e.id_estudiante = p.id_estudiante
                WHERE p.id_convocatoria = c.id_convocatoria
            )
            ORDER BY c.papa_minimo_requerido DESC;
        """
        df10 = pd.read_sql(query_10, conn)

        if not df10.empty:
            st.dataframe(df10, use_container_width=True, hide_index=True)
        else:
            st.info(
                "No hay convocatorias donde el PAPA requerido sea superior al promedio de sus postulantes."
            )

    conn.close()
