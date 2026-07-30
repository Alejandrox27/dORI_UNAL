-- =========================================================
-- Consulta 1: Estudiantes con PAPA alto
-- =========================================================
SELECT * 
FROM estudiantes
WHERE papa_acumulado >= 4.0
ORDER BY papa_acumulado DESC;


-- =========================================================
-- Consulta 2: Programa curricular de los estudiantes
-- =========================================================
SELECT e.id_estudiante, uo.nombre, uo.tipo, uo.creditos_totales_programa
FROM estudiantes e
JOIN unidades_organizacionales uo ON e.id_unidad_organizacional = uo.id_unidad;


-- =========================================================
-- Consulta 3: Documentos asociados a cada postulación
-- =========================================================
SELECT p.id_postulacion, p.fecha_postulacion, p.estado_actual, rd.nombre_documento, dp.url_archivo_pdf, dp.fecha_subida
FROM postulaciones p
JOIN documentos_postulaciones dp ON p.id_postulacion = dp.id_postulacion
JOIN requisitos_documentales rd ON dp.id_requisito = rd.id_requisito;


-- =========================================================
-- Consulta 4: Cantidad de postulaciones por convocatoria
-- =========================================================
SELECT c.id_convocatoria, c.nombre_convocatoria, COUNT(p.id_postulacion) AS total_postulaciones
FROM postulaciones p
JOIN convocatorias c ON p.id_convocatoria = c.id_convocatoria
GROUP BY c.id_convocatoria, c.nombre_convocatoria
ORDER BY COUNT(p.id_postulacion);


-- =========================================================
-- Consulta 5: Promedio de PAPA por programa académico
-- =========================================================
SELECT unio.id_unidad, unio.tipo, unio.nombre, AVG(est.papa_acumulado) AS promedio_papa
FROM estudiantes est
JOIN unidades_organizacionales unio ON est.id_unidad_organizacional = unio.id_unidad
GROUP BY unio.id_unidad, unio.nombre;


-- =========================================================
-- Consulta 6: Universidades con más de dos convenios activos
-- =========================================================
SELECT us.id_universidad, us.nombre_oficial, COUNT(c.id_convenio) AS total_convenios  
FROM universidades_socias us
JOIN convenios c ON us.id_universidad = c.id_universidad
WHERE c.estado_legal = 'Activo'
GROUP BY us.id_universidad, us.nombre_oficial
HAVING(COUNT(c.id_convenio) > 2);


-- =========================================================
-- Consulta 7: Convenios por país
-- =========================================================
SELECT p.nombre_oficial, COUNT(us.id_universidad) AS total_universidades_socias, COUNT(c.id_convenio) AS total_convenios 
FROM paises p
JOIN universidades_socias us ON p.id_pais = us.pais
JOIN convenios c ON us.id_universidad = c.id_universidad
GROUP BY p.id_pais;


-- =========================================================
-- Consulta 8: Estudiantes con PAPA superior al promedio de su programa
-- =========================================================
SELECT e.id_estudiante, e.nombre, e.apellidos, e.papa_acumulado, uo.nombre AS programa
FROM estudiantes e
JOIN unidades_organizacionales uo ON e.id_unidad_organizacional = uo.id_unidad
WHERE e.papa_acumulado > (
    SELECT AVG(e2.papa_acumulado)
    FROM estudiantes e2
    WHERE e2.id_unidad_organizacional = e.id_unidad_organizacional
);


-- =========================================================
-- Consulta 9: Estudiantes sin postulaciones
-- =========================================================
SELECT *
FROM estudiantes e
WHERE NOT EXISTS (
    SELECT 1
    FROM postulaciones p
    WHERE p.id_estudiante = e.id_estudiante
);


-- =========================================================
-- Consulta 10: Convocatorias con requisito de PAPA superior al promedio de sus postulantes
-- =========================================================
WITH promedio_postulantes AS (
    SELECT
        p.id_convocatoria,
        AVG(e.papa_acumulado) AS papa_promedio
    FROM postulaciones p
    JOIN estudiantes e ON e.id_estudiante = p.id_estudiante
    GROUP BY p.id_convocatoria
)
SELECT
    c.id_convocatoria,
    c.nombre_convocatoria,
    c.papa_minimo_requerido,
    pp.papa_promedio AS papa_promedio_postulantes
FROM convocatorias c
JOIN promedio_postulantes pp ON pp.id_convocatoria = c.id_convocatoria
WHERE c.papa_minimo_requerido > pp.papa_promedio;


-- =========================================================
-- Consulta 11: Estudiantes que cumplen los requisitos de una convocatoria
-- =========================================================
SELECT 
    e.apellidos, 
    e.nombre, 
    c.id_convocatoria
FROM estudiantes e
JOIN unidades_organizacionales u 
    ON u.id_unidad = e.id_unidad_organizacional
JOIN postulaciones p 
    ON p.id_estudiante = e.id_estudiante
JOIN convocatorias c 
    ON c.id_convocatoria = p.id_convocatoria
WHERE 
    e.papa_acumulado >= GREATEST(COALESCE(c.papa_minimo_requerido, 3.5), 3.5)
    AND ((e.creditos_aprobados::DECIMAL / u.creditos_totales_programa) * 100) >= COALESCE(c.porcentaje_creditos_minimo, 40)
    AND NOT EXISTS (
        SELECT 1 
        FROM sanciones_disciplinarias sd
        WHERE sd.id_estudiante = e.id_estudiante
          AND (sd.fecha_fin IS NULL OR sd.fecha_fin >= CURRENT_DATE)
    );


-- =========================================================
-- Consulta 12 (optimizada): Universidad con mayor número de
-- convenios activos por país
-- =========================================================
WITH conteo_por_universidad AS (
    SELECT
        us.id_universidad,
        us.nombre_oficial,
        p.id_pais,
        p.nombre_oficial AS pais,
        COUNT(c.id_convenio) AS cantidad_convenios
    FROM universidades_socias us
    JOIN paises p ON us.pais = p.id_pais
    JOIN convenios c ON us.id_universidad = c.id_universidad
    WHERE c.estado_legal = 'Activo'
    GROUP BY us.id_universidad, us.nombre_oficial, p.id_pais, p.nombre_oficial
),
rankeado AS (
    SELECT
        *,
        RANK() OVER (PARTITION BY id_pais ORDER BY cantidad_convenios DESC) AS posicion
    FROM conteo_por_universidad
)
SELECT
    nombre_oficial AS universidad,
    pais,
    cantidad_convenios
FROM rankeado
WHERE posicion = 1
ORDER BY pais;


-- =========================================================
-- Consulta 13: Estudiantes que cumplen todos los requisitos documentales
-- =========================================================
SELECT
    e.id_estudiante,
    e.nombre,
    e.apellidos
FROM estudiantes e
WHERE NOT EXISTS
(
    SELECT 1
    FROM requisitos_documentales r
    WHERE NOT EXISTS
    (
        SELECT 1
        FROM postulaciones p
        JOIN documentos_postulaciones d
            ON p.id_postulacion = d.id_postulacion
        WHERE p.id_estudiante = e.id_estudiante
          AND d.id_requisito = r.id_requisito
    )
);


-- =========================================================
-- Consulta 14: Postulaciones de estudiantes sin sanciones disciplinarias vigentes
-- =========================================================
SELECT
    e.id_estudiante,
    e.nombre AS estudiante,
    c.nombre_convocatoria,
    us.nombre_oficial AS universidad_destino,
    p.fecha_postulacion
FROM estudiantes e
JOIN postulaciones p
    ON e.id_estudiante = p.id_estudiante
JOIN convocatorias c
    ON p.id_convocatoria = c.id_convocatoria
JOIN convenios co
    ON c.id_convenio = co.id_convenio
JOIN universidades_socias us
    ON co.id_universidad = us.id_universidad
WHERE NOT EXISTS (
        SELECT 1
        FROM sanciones_disciplinarias s
        WHERE s.id_estudiante = e.id_estudiante
          AND CURRENT_DATE BETWEEN s.fecha_inicio
                               AND COALESCE(s.fecha_fin, CURRENT_DATE)
);


-- =========================================================
-- Consulta 15: Estudiantes enviados por universidad socia
-- =========================================================
SELECT
    us.id_universidad,
    us.nombre_oficial,
    COUNT(DISTINCT e.id_estudiante) AS estudiantes_enviados
FROM universidades_socias us
JOIN convenios co
    ON us.id_universidad = co.id_universidad
JOIN convocatorias c
    ON co.id_convenio = c.id_convenio
JOIN postulaciones p
    ON c.id_convocatoria = p.id_convocatoria
JOIN estudiantes e
    ON p.id_estudiante = e.id_estudiante
WHERE EXISTS
(
    SELECT 1
    FROM historico_estados_postulacion h
    WHERE h.id_postulacion = p.id_postulacion
      AND h.estado_registrado = 'Aceptada por Socio'
)
GROUP BY us.id_universidad, us.nombre_oficial;

