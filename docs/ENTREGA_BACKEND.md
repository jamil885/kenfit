# Entrega del backend KenFit — 5 de octubre de 2026

## Alcance implementado

La especificación adjunta de entrenamiento guía la separación de ejercicio, sesión, split, plan y ejecución. Se conserva el proyecto original y sus migraciones.

| Módulo | Comportamiento entregado |
|---|---|
| Auth | Registro, login JWT, `/auth/me`, Argon2, bloqueo de usuarios inactivos, tokens con vencimiento obligatorio |
| Perfil | Creación, lectura, PUT compatible y PATCH; preferencias de días, equipo, tiempo y disciplina |
| Ejercicios | CRUD con borrado lógico, ownership, duplicación, grupos musculares y catálogo relacional de disciplinas |
| Workouts | CRUD de sesiones, prescripciones ordenadas, repeticiones/tiempo/distancia y duplicación |
| Splits | Ciclos de 1–28 días, sesiones y descanso explícito |
| Planes | 1–52 semanas, sesiones por día, fases etiquetadas y split opcional |
| Historial | Series realmente ejecutadas y snapshots de nombre y métricas prescritas |
| Progresión | Sugerencias orientativas de carga; no modifica rutinas automáticamente |
| Generación | Plantillas iniciales de fuerza, running y movilidad según disponibilidad y nivel |
| Nutrición | Alimentos oficiales/de usuario, comidas por gramos o porciones, metas editables y resumen diario |
| Estimación | Mifflin–St Jeor, factor de actividad y ajuste explícitos; no guarda metas sin acción del usuario |
| Progreso | Peso por fecha, actualización del mismo día y resumen de entrenamientos |

## Decisiones compatibles con el MVP

- `Workout` es una sesión reutilizable. La rutina recurrente se representa mediante `Split`, y el programa de semanas mediante `TrainingPlan`; no se añadió una entidad `Routine` redundante.
- Las disciplinas tienen catálogo propio. Los códigos libres se registran al crear/editar un ejercicio, sin modificar el esquema.
- El contenido oficial es global y de solo lectura; el del usuario es privado. No hay publicación ni permisos de compartición en esta versión.
- `parent_id` conserva el origen de una copia. No hay historial completo de versiones de cada edición.
- Se archivan ejercicios y plantillas para preservar referencias existentes. Los registros de ejecución y comidas pueden eliminarse por su propietario.
- Las fases del plan son etiquetas en las entradas de calendario. No hay periodización avanzada ni entidades separadas para bloques.
- El perfil existente conserva `gender`, `goal` y `fitness_level` como strings para evitar romper clientes previos. Los ejemplos recomiendan códigos estables.
- El generador de fuerza usa una plantilla de peso corporal de 1–3 días. Las sesiones y planes manuales pueden representar otras disciplinas y frecuencias.
- La disponibilidad y el nivel ajustan volumen/duración; el objetivo de ganancia muscular ajusta repeticiones. El equipo no selecciona automáticamente un programa avanzado de gimnasio: el generador básico permanece centrado en peso corporal.

## Verificación realizada

- 34 pruebas pasaron usando SQLite temporal con migraciones reales y claves foráneas habilitadas en la API.
- Pruebas de autenticación, aislamiento entre usuarios, protección del catálogo oficial, referencias privadas, validación, snapshots, nutrición, onboarding, generación y progreso.
- Migración desde la revisión anterior con usuarios, perfiles, ejercicios y grupos musculares existentes; datos conservados.
- Downgrade del esquema nuevo probado en la base SQLite de prueba.
- `alembic check` sin diferencias pendientes; SQL de migraciones generado para el dialecto PostgreSQL.
- `ruff check` y comprobación de dependencias sin errores.
- Una advertencia de deprecación del cliente de pruebas de Starlette/httpx, sin errores de ejecución.

**No se ejecutó una instancia real de PostgreSQL ni Docker aquí.** La guía permite repetir la suite en `kenfit_test` y validar las migraciones sobre un respaldo restaurado de tu base en la PC principal.

## Límites antes del lanzamiento público

El backend MVP está implementado para revisión e integración; no se presenta como una aplicación ya validada para producción.

1. Validar PostgreSQL, migraciones y compatibilidad del cliente móvil en la PC principal.
2. Revisar y ampliar el contenido deportivo con un profesional. La generación actual es una plantilla inicial, no un entrenador clínico ni una adaptación completa multi-atleta.
3. Los seis alimentos del seed son **datos aproximados de demostración**, claramente marcados en `reference`. Sustituirlos por etiquetas verificadas o un catálogo autorizado y trazable antes de publicarlos como base nutricional definitiva.
4. Ajustar preferencias y reglas nutricionales con revisión profesional. La distribución inicial de macros es configurable mediante las metas; se excluye nutrición clínica y no se genera un menú automático.
5. Preparar HTTPS, límites de solicitudes y protección contra intentos de login, despliegue, backups, observabilidad y gestión de secretos.
6. Para una experiencia móvil comercial, completar recuperación de contraseña, verificación de email, refresh/logout de sesiones y gestión/eliminación de cuenta. Esta entrega conserva el alcance de registro/login mediante access tokens; expiran a los 30 minutos por defecto.
7. IA, pagos, notificaciones, catálogo multimedia, compartir contenido y adaptación avanzada quedan para etapas posteriores.

## Referencias de implementación

- Especificación del Sistema de Entrenamientos facilitada por el usuario.
- SQLAlchemy: https://docs.sqlalchemy.org/en/20/orm/relationship_api.html
- Alembic: https://alembic.sqlalchemy.org/en/latest/batch.html
- Ecuación Mifflin–St Jeor, estudio original: https://pubmed.ncbi.nlm.nih.gov/2305711/

Los límites de la calculadora y la distribución inicial de macros son decisiones de producto del MVP, no recomendaciones clínicas derivadas automáticamente del estudio.
