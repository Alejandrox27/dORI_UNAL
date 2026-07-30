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
