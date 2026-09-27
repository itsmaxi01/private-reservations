# Nuestro espacio

Aplicación web privada para dos usuarios con reservaciones, WatchList compartida
y mensajes. FastAPI sirve tanto la API como el frontend HTML/CSS/JavaScript.

## Funcionalidad incluida

- Autenticación externa con Supabase Auth y aprovisionamiento limitado a dos correos.
- Roles `ADMIN` y `MEMBER`.
- Reservaciones `DATE` y `WATCH` con reglas de fecha, horario y cupo semanal.
- WatchList compartida, estado manual y archivado seguro.
- Mensajes compartidos y fijados.
- Migraciones Alembic, pruebas y contenedor de despliegue.

## Desarrollo local

Requiere Python 3.11+ y PostgreSQL.

```bash
python -m venv .venv
pip install -e ".[dev]"
```

Copiar `.env.example` a `.env` y completar todos sus valores. Después:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

La aplicación queda disponible en `http://localhost:8000` y la documentación de
la API en `http://localhost:8000/docs`.

## Configurar Supabase

1. Crear un proyecto de Supabase.
2. En Authentication, desactivar **Allow new users to sign up**.
3. Invitar los dos correos desde Authentication > Users.
4. Configurar la URL local y la URL de producción entre las Redirect URLs.
5. Configurar SMTP para entregar Magic Links/OTP a los dos correos.
6. Copiar Project URL y Publishable Key a las variables correspondientes.
7. Copiar la conexión PostgreSQL del pooler en modo sesión a `DATABASE_URL`.
8. Asignar los correos exactos a `ADMIN_EMAIL` y `MEMBER_EMAIL`.

El backend valida localmente los JWT mediante el JWKS público. `created_by` y
`added_by` siempre proceden de la identidad autenticada.

## Despliegue en Render

El archivo `render.yaml` y el `Dockerfile` preparan un único Web Service gratuito
que sirve frontend y API.

1. Publicar el repositorio en GitHub.
2. En Render, crear un Blueprint desde el repositorio.
3. Completar las variables marcadas como `sync: false`.
4. Usar la URL resultante como Site URL/Redirect URL en Supabase.

Al arrancar, `scripts/start.sh` ejecuta `alembic upgrade head` antes de iniciar
Uvicorn. `/api/health` comprueba también la conexión a PostgreSQL.

El servicio gratuito de Render entra en reposo después de inactividad, por lo
que la primera carga puede tardar. La información persiste en Supabase, no en el
sistema de archivos efímero del contenedor.

## Pruebas

```bash
pytest -q
```

Las pruebas unitarias usan SQLite como sustituto rápido. Antes de considerar un
despliegue definitivo debe ejecutarse también una prueba de integración contra
un proyecto PostgreSQL/Supabase real, especialmente para el advisory lock que
protege el límite semanal.

## Estructura

```text
app/
├── models/          # entidades SQLAlchemy y enums
├── schemas/         # contratos Pydantic
├── repositories/    # consultas y persistencia
├── services/        # reglas de negocio
├── routers/         # API HTTP
├── auth.py          # validación JWT y aprovisionamiento
├── config.py        # variables de entorno
├── database.py      # engine y sesiones
└── main.py          # FastAPI y frontend estático
frontend/            # HTML, CSS y JavaScript vanilla
migrations/          # migraciones Alembic
tests/               # pruebas estructurales, de servicios y API
```
