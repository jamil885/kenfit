# KenFit

Backend MVP de una app móvil de entrenamiento, nutrición y seguimiento.

**Frontend móvil: [empieza aquí](docs/mobile/EMPEZAR_AQUI.md).**

**Backend: [guía para Windows](docs/PRUEBAS_PC_WINDOWS.md).**

## Incluido

- FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, Argon2 y JWT.
- Registro, login, usuario actual y perfil con preferencias de disponibilidad.
- Catálogo extensible de disciplinas y ejercicios; contenido oficial y privado.
- Workouts y prescripciones por repeticiones, tiempo, distancia, carga e intensidad.
- Splits por ciclos y planes con semanas, días y fases.
- Duplicación de contenido con referencia al original; permisos por propietario.
- Historial de series con copias de la prescripción y seguimiento de peso.
- Generación de planes iniciales y sugerencias de progresión mediante reglas.
- Alimentos, comidas por gramos/porciones, estimación y metas de calorías/macros.
- Migración compatible con las revisiones anteriores y pruebas automatizadas.

## Arranque local

Python 3.12 recomendado. Configura `.env` usando `.env.example` y genera tu secreto JWT.
Desde la raíz: `docker compose up -d postgres`.
Desde `backend`:

```bash
python -m venv .venv
# Activa .venv según tu sistema operativo.
python -m pip install -r requirements-lock.txt
alembic upgrade head
python -m app.seed
uvicorn app.app.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs.

```bash
python -m pip install -r requirements-dev.txt
pytest -q
ruff check .
```

Las pruebas usan SQLite temporal por defecto. La guía explica cómo repetirlas en una base PostgreSQL separada `kenfit_test`.

## Documentación

- [Entrega y límites](docs/ENTREGA_BACKEND.md)
- [Contrato de API y ejemplos](docs/api/backend-mvp.md)
- [Pruebas en Windows](docs/PRUEBAS_PC_WINDOWS.md)
- [Arquitectura](docs/architecture/backend-mvp.md)

El frontend móvil inicial está implementado en `mobile/`, con demostración y vista web ligera incluida. Antes del despliegue público se debe validar en dispositivos reales y con PostgreSQL, y completar los pendientes de producción indicados en las entregas.
