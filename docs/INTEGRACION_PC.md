# Integración del trabajo local de la PC con el MVP

La PC estaba en `fea8b9182489`; el MVP remoto estaba en `82d6be1a904f`. No se deben mezclar esas migraciones con un merge ni ejecutar `alembic upgrade head` directamente sobre la base local antigua.

Esta entrega conserva el historial local como segundo padre del commit de integración y adapta su módulo `/training-sessions` al modelo compartido del MVP. Los CRUD de ejercicios, workouts, splits y planes utilizan ahora los contratos del MVP que consume el frontend. No se mantienen dos implementaciones ORM para las mismas tablas. Las rutas y cuerpos de los antiguos CRUD no son todos compatibles: `order` pasa a `position`/`day`, `load_kg` a `weight_kg` y `duration_weeks` a `weeks`. La API de sesiones conserva sus rutas y estados `IN_PROGRESS`, `COMPLETED`, `CANCELLED`; los resultados por serie siguen en `/history` y no se inventan a partir de sesiones antiguas.

## Antes de ejecutar

1. Detener Uvicorn y cualquier otro proceso que escriba en la base.
2. Conservar la rama `respaldo/pc-antes-integracion` y los archivos `.env` locales.
3. Crear un respaldo de PostgreSQL desde la raíz del repositorio, en PowerShell:

```powershell
docker compose exec postgres pg_dump -U kenfit -d kenfit -Fc -f /tmp/kenfit-antes-integracion.dump
docker compose cp postgres:/tmp/kenfit-antes-integracion.dump .\kenfit-antes-integracion.dump
```

Comprobar que ambos comandos terminaron correctamente y el archivo existe y tiene contenido. El archivo es privado y está ignorado por Git.

## Configuración

Usar el entorno virtual del backend e instalar `requirements-lock.txt`. En `backend/.env`, configurar `DATABASE_URL` hacia la base **kenfit original**, puerto 5433, y `JWT_SECRET_KEY` con una clave aleatoria persistente. No compartir esos valores. Las variables `$env:DATABASE_URL` y `$env:JWT_SECRET_KEY` de una terminal tienen prioridad sobre `.env`: revisar la conexión, especialmente si se había seleccionado `kenfit_beta`.

## Primero: simulación

Desde `backend`, con el entorno virtual activo:

```powershell
python -m app.migrate_pc
```

El comando exige exactamente la revisión `fea8b9182489` y las tablas esperadas. Ejecuta toda la conversión dentro de una transacción de PostgreSQL y al finalizar **revierte**: muestra recuentos pero no cambia el esquema.

Si falla, no ejecutar `--apply`. Revisar el error. Por ejemplo, nombres locales de más de 100 caracteres o prescripciones incompatibles necesitan revisión explícita; no se truncan silenciosamente.

## Aplicar después de una simulación correcta

```powershell
python -m app.migrate_pc --apply
python -m alembic current
python -m app.seed
python -m uvicorn app.app.main:app --reload
```

La revisión final es `9c4a10b2d7ef`. Los IDs, emails, hashes de contraseña, propietarios, ejercicios, relaciones musculares, workouts, cargas, splits, planes y sesiones se copian. Se recalibran las secuencias de IDs para permitir nuevas altas.

Todas las tablas originales, incluida `alembic_version`, quedan en un esquema `kenfit_pc_<fecha>` dentro de la misma base. El esquema no se elimina automáticamente. Un error durante la conversión revierte tanto la creación del esquema como el movimiento y la copia de tablas. El respaldo externo sigue siendo necesario.

## Datos que requieren revisión

- El perfil recibe los valores iniciales del MVP: 3 días, 45 minutos, peso corporal y disciplina strength. Editar el perfil tras entrar.
- Los workouts sin disciplina local reciben `strength`; revisar los de cardio/deportes.
- Los planes sin duración reciben 4 semanas y los de objetivo vacío `general_fitness`; el valor original permanece en el archivo de esquema.
- El calendario se deriva de splits de 7 días. Ciclos más largos conservan sus días, pero requieren editar su calendario; no se convierten a semanas artificialmente.
- Los estados y notas de sesiones antiguas se conservan. No se generan resultados de series ni métricas completadas en `/history` sin evidencia de ejecución.
- El frontend no tiene todavía interfaz para el ciclo independiente de `/training-sessions`; se puede comprobar en `/docs`. El registro detallado móvil sigue usando `/history`.

## Verificación después de aplicar

Entrar con una cuenta existente; consultar ejercicios, workouts, splits, planes y `/training-sessions`; revisar cargas y notas. Crear un registro nuevo para verificar IDs. Completar de nuevo el perfil y validar un entrenamiento, comida y peso desde el frontend.

Para instalaciones nuevas o bases que ya están en `82d6be1a904f`, usar `alembic upgrade head` normalmente: la nueva migración añade la tabla de sesiones sin modificar las migraciones previas.

No usar `alembic downgrade` como restauración de la conversión entre arquitecturas. Si se necesita volver atrás, restaurar el dump en una base separada, verificarlo y arrancar la rama de respaldo contra esa base.
