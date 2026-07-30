# Sistema de Movilidad Académica - ORI UNAL

Sistema web de gestión de convocatorias, convenios y movilidad académica desarrollado para la Dirección de Relaciones Exteriores (DORI) de la Universidad Nacional de Colombia.

Este proyecto fue desarrollado como entrega final para la asignatura de **Bases de Datos**.

---

## Integrantes del Proyecto

- **Didier Alejandro Mejía Merchán** (CC: 1025323509)
- **Samuel Emanuel Daniel Álvarez Torres** (CC: 1027522564)
- **Alejandro Santos Nivia** (CC: 1028486932)
- **Jean Carlo Triana Guzmán** (CC: 1025140412)
- **Santiago Cedeño Sabogal** (CC: 1031807186)

---

## Requisitos del Sistema

- **Python**: 3.9 o superior
- **PostgreSQL**: 14 o superior
- **Dependencias de Python**:
  - `streamlit`
  - `psycopg2-binary`
  - `pandas`

---

## Instalación y Configuración

### 1. Clonar o descargar el repositorio
Navega a la carpeta principal del proyecto:

```bash
cd dori_unal_project
```

### 2. Crear y activar un entorno virtual (opcional)

En Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

En Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar las dependencias de Python

```bash
pip install -r requirements.txt
```

### 4. Configurar la Base de Datos PostgreSQL

1. Crea la base de datos en PostgreSQL:
```sql
CREATE DATABASE db_dori_unal;
```

2. Restaura el backup de la base de datos usando el archivo `database/DORI_UNAL_DB.sql`:
```bash
psql -U postgres -d db_dori_unal -f database/DORI_UNAL_DB.sql
```

3. Crea el archivo de credenciales `.streamlit/secrets.toml` en la raíz del proyecto con el siguiente contenido:

```toml
[database]
password = "TU_CONTRASEÑA_POSTGRESQL"
```

Este archivo ya está incluido en `.gitignore` y **no sera subido a GitHub**. La aplicacion lee la contraseña automaticamente desde este archivo usando `st.secrets`.

---

## Ejecución de la Aplicación

Para iniciar el servidor de desarrollo de Streamlit, ejecuta:

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador predeterminado en `http://localhost:8501`.

---

## Estructura del Proyecto

- `app.py`: Archivo principal de la aplicación en Streamlit, maneja el diseño general y las pestañas principales.
- `convocatorias/`: Módulo encargado de la visualización de convenios, convocatorias y reportes estadísticos.
- `estudiantes/`: Módulo con el formulario de registro de estudiantes y consulta dinámica de convocatorias habilitadas según criterios académicos.
- `database/DORI_UNAL_DB.sql`: Volcado (backup) completo de la base de datos PostgreSQL con tablas, enumeraciones, disparadores, funciones y datos de prueba.
- `database/CONSULTAS_OPTIMIZADAS_POSTGRESQL.sql`: Archivo con las consultas SQL optimizadas utilizadas en los reportes y estadísticas del sistema.
- `.streamlit/secrets.toml`: Archivo local con la contraseña de la base de datos. **No se sube a GitHub** (excluido por `.gitignore`).
- `.gitignore`: Excluye de Git los archivos sensibles y de cache como `secrets.toml` y `__pycache__/`.
- `requirements.txt`: Lista de librerías de Python requeridas para ejecutar el sistema.

