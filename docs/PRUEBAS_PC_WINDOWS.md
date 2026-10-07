# Pruebas de KenFit en tu PC principal

## 1. Integrar el código

Guarda una copia de tu repositorio antes de integrar esta entrega. El ZIP conserva el proyecto y sustituye el backend, documentación, `.env.example` y Compose. No incluye tu `.env` ni modifica GitHub automáticamente.

Para conservar tu historial Git, copia el contenido de `kenfit-main` sobre tu clon existente, sin reemplazar `.git` ni tus archivos `.env`. Revisa `git status` y `git diff` antes del commit.

No borres el volumen de PostgreSQL. No ejecutes `docker compose down -v`.

## 2. Variables de entorno

Desde la raíz del repositorio, en PowerShell:

```powershell
Copy-Item .env.example .env
py -3.12 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Si ya tienes `.env`, edítalo; no lo sobrescribas. Guarda el valor generado en `JWT_SECRET_KEY`.

Variables mínimas:

```dotenv
POSTGRES_DB=kenfit
POSTGRES_USER=kenfit
POSTGRES_PASSWORD=tu_password_actual
DATABASE_URL=postgresql+psycopg://kenfit:tu_password_actual@localhost:5433/kenfit
JWT_SECRET_KEY=tu_secreto_aleatorio_de_al_menos_32_caracteres
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=[]
```

Conserva la contraseña real de tu volumen existente. Cambiar `POSTGRES_PASSWORD` no cambia la contraseña de una base ya inicializada. Si usas caracteres reservados en el password de la URL, codifícalos como URL; la variable `POSTGRES_PASSWORD` conserva el valor original.

El backend lee `.env` en la raíz y también `backend/.env`; el de `backend` tiene prioridad. Si tienes ambos, alinea las variables. Se corrigieron los nombres `JWT_SECRET` y `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` del ejemplo anterior: los nombres esperados son los de arriba. El puerto local es **5433**.

## 3. Arrancar PostgreSQL y respaldar la base existente

Desde la raíz:

```powershell
docker compose up -d postgres
docker compose ps
docker exec kenfit-postgres pg_dump -U kenfit -d kenfit -Fc -f /tmp/kenfit-before-mvp.dump
docker cp kenfit-postgres:/tmp/kenfit-before-mvp.dump .\kenfit-before-mvp.dump
```

El respaldo contiene datos personales: guárdalo fuera de Git. Antes de migrar una base importante, verifica que el respaldo pueda restaurarse en una base separada. Cambia usuario/base en los comandos si tu configuración usa otros nombres.

## 4. Preparar Python y aplicar migraciones

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
alembic current
alembic upgrade head
alembic current
alembic check
python -m app.seed
```

La revisión final es `82d6be1a904f`; se conserva la cadena anterior. Los ejercicios antiguos, sin propietario identificable, se convierten en contenido de plataforma de solo lectura. Puedes duplicarlos para obtener una copia editable propia. No se inventa un dueño para esos datos.

Si PowerShell bloquea la activación, usa directamente `.\.venv\Scripts\python.exe` para ejecutar Python y `.\.venv\Scriptslembic.exe` para Alembic; no hace falta cambiar la política global de tu PC.

## 5. Ejecutar la API

```powershell
uvicorn app.app.main:app --reload
```

Abre http://127.0.0.1:8000/docs. Primero verifica `/health` y `/health/database`.

Registra un usuario con `/auth/register`, entra con `/auth/login` y pega el `access_token` en **Authorize**. Swagger HTTPBearer recibe el token sin anteponer `Bearer` manualmente.

Usa los ejemplos de `docs/api/backend-mvp.md` para crear el perfil, generar un plan, registrar una sesión y una comida. Confirma que otro usuario no puede acceder a los datos privados del primero.

## 6. Pruebas automatizadas rápidas

En otra terminal, desde `backend`, activa `.venv`:

```powershell
python -m pip install -r requirements-dev.txt
pytest -q
ruff check .
```

Por defecto crean una base SQLite temporal y no usan la base `kenfit`.

## 7. Repetir la suite sobre PostgreSQL

Esta fase es la validación pendiente de la entrega. Crea una base exclusiva para pruebas:

```powershell
docker exec kenfit-postgres createdb -U kenfit kenfit_test
$env:KENFIT_TEST_DATABASE_URL="postgresql+psycopg://kenfit:tu_password_actual@localhost:5433/kenfit_test"
pytest -q
Remove-Item Env:KENFIT_TEST_DATABASE_URL
```

Si `kenfit_test` ya existe y solo contiene datos de pruebas, reutilízala. La suite **borra y recrea sus tablas en cada prueba**. Rechaza cualquier base PostgreSQL cuyo nombre no sea exactamente `kenfit_test`. Nunca apuntes esta variable a datos que quieras conservar.

El caso de migración con datos anteriores se verifica además en una base SQLite aislada; para validar la actualización real de tu esquema PostgreSQL, aplica el paso 4 sobre una copia restaurada del respaldo y revisa los registros anteriores.

## 8. Antes del commit

```powershell
git status
git diff --stat
```

Confirma que no aparezcan `.env`, `.venv`, respaldos ni bases de datos. Si las pruebas pasan y la API funciona, el commit puede describirse como:

`feat: complete training and basic nutrition backend MVP`
