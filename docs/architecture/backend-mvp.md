# Arquitectura del backend MVP

`api/routes` declara entradas y respuestas tipadas. `schemas` valida campos y combinaciones. `services` aplica permisos, valida referencias y organiza transacciones. `repositories` concentra consultas reutilizables. `engine` contiene reglas de generación y progresión. `models` describe datos relacionales; Alembic conserva la evolución del esquema.

## Datos

- `users` → `fitness_profiles` y preferencias.
- `disciplines` → `exercises` → `exercise_muscles` → `muscle_groups`.
- `workouts` → `workout_exercises` → `exercises`.
- `splits` → `split_days` → `workouts`.
- `training_plans` → `plan_days` → `workouts`; el plan puede referenciar un split.
- `workout_logs` → `set_results`: prescripción y ejecución separadas.
- `weight_entries`: peso único por usuario y día.
- `foods` → `meal_entries`: nutrición calculada y conservada al registrar.
- `nutrition_targets`: una meta activa por usuario.

No se guardan workouts, splits ni planes como documentos JSON. El único JSON funcional añadido es la lista pequeña de equipos disponibles en el perfil.

## Seguridad y consistencia

Todas las operaciones de dominio requieren Bearer JWT. La identidad proviene del token; el cliente no asigna `owner_id`, `source` ni `user_id`. Consultas de contenido retornan datos propios o oficiales. Referencias a datos de otro usuario responden 404. Cambios sobre datos oficiales responden 403.

Las operaciones con varios registros se validan antes del commit. La generación de workouts, split y plan se confirma en una sola transacción; ante error se revierte. Reemplazar prescripciones vacía las filas anteriores antes de insertar nuevos órdenes para respetar las restricciones únicas.

Los datos ejecutados conservan nombres y métricas prescritas. Las comidas conservan sus calorías/macros por cantidad; editar el alimento no reescribe el pasado.

No hay endpoints administrativos públicos para publicar contenido SYSTEM. `python -m app.seed` instala el catálogo inicial como operación local del administrador.

## Compatibilidad

Se conserva `app.app.main:app` como punto de entrada y las rutas existentes. PUT del perfil sigue aceptando actualizaciones parciales por compatibilidad; PATCH es la ruta recomendada. PUT de workouts, splits y planes reemplaza toda la definición.

Nueva revisión: `82d6be1a904f`, padre `cc8be0ff1fcf`. Las preferencias nuevas tienen valores predeterminados para perfiles existentes. Los ejercicios antiguos quedan SYSTEM/platform porque el esquema anterior no registraba su dueño; para editarlos, duplicarlos.
