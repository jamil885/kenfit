# API KenFit MVP

Contrato completo y validaciones: `/docs` y `/openapi.json`. IDs de ejemplos son ilustrativos: usa los que devuelva tu servidor.

Todas las rutas siguientes, salvo registro/login y health, requieren `Authorization: Bearer <token>`.

## Rutas

| Recurso | Operaciones |
|---|---|
| `/auth/register`, `/auth/login` | POST |
| `/auth/me` | GET |
| `/fitness-profile` | POST, GET, PATCH; PUT parcial compatible |
| `/exercises` | GET paginado, POST |
| `/exercises/{id}` | GET, PATCH, DELETE lógico |
| `/exercises/{id}/duplicate` | POST |
| `/exercises/disciplines`, `/exercises/muscle-groups` | GET |
| `/workouts`, `/splits`, `/training-plans` | GET paginado, POST |
| `/{recurso}/{id}` | GET, PUT completo, DELETE lógico |
| `/{recurso}/{id}/duplicate` | POST |
| `/workout-logs` | POST, GET paginado |
| `/workout-logs/{id}` | GET, DELETE |
| `/recommendations/training-plan` | POST |
| `/recommendations/progression` | POST |
| `/progress/weight` | GET paginado, PUT por fecha |
| `/progress/weight/{id}` | DELETE |
| `/progress/summary` | GET |
| `/nutrition/foods` | GET paginado, POST |
| `/nutrition/foods/{id}` | GET, PUT de alimento propio |
| `/nutrition/estimate` | POST, vista previa sin guardar |
| `/nutrition/targets` | GET, PUT |
| `/nutrition/meals` | POST |
| `/nutrition/meals/{id}` | DELETE |
| `/nutrition/summary?recorded_on=2026-10-05` | GET |

Paginación: `offset=0&limit=50`; máximo 100. Catálogos/plantillas admiten `search`. Las listas solo incluyen contenido activo y visible. El catálogo de disciplinas es global; no revela el contenido privado de los usuarios.

## Flujo inicial

### POST /auth/register

```json
{"name":"Kenji","email":"kenji@example.com","password":"UnaClaveSegura123!"}
```

### POST /auth/login

```json
{"email":"kenji@example.com","password":"UnaClaveSegura123!"}
```

### POST /fitness-profile

```json
{
  "birth_date":"2000-01-01",
  "gender":"male",
  "height_cm":175,
  "weight_kg":75,
  "fitness_level":"beginner",
  "goal":"general_fitness",
  "days_per_week":3,
  "session_minutes":45,
  "available_equipment":["bodyweight"],
  "preferred_discipline":"strength"
}
```

Códigos sugeridos: niveles `beginner`, `intermediate`, `advanced`; objetivos `general_fitness`, `muscle_gain`, `fat_loss`, `strength`, `endurance`. El esquema mantiene strings libres por compatibilidad. El generador admite `strength`, `running`, `mobility`; otras disciplinas se construyen con los endpoints de contenido.

### POST /recommendations/training-plan

```json
{"weeks":4}
```

Usa preferencias del perfil. Para sobrescribirlas en esta generación:

```json
{"weeks":4,"days_per_week":3,"discipline":"strength","equipment":["bodyweight"]}
```

Devuelve plan con `schedule`; consulta sus workouts usando los IDs del calendario. Los días son 1–7 dentro de cada semana, no fechas absolutas. No hay activación o calendario con fechas en esta versión.

### POST /workouts

```json
{
  "name":"Sesión híbrida",
  "discipline":"hybrid",
  "exercises":[
    {"exercise_id":1,"position":1,"sets":3,"reps":8,"weight_kg":20,"rest_seconds":90},
    {"exercise_id":5,"position":2,"duration_seconds":900,"distance_meters":2000,"intensity":"easy"}
  ]
}
```

La duplicación es superficial: un plan duplicado conserva referencias a sus workouts y split. Para modificar una sesión oficial, duplica también esa sesión y actualiza la referencia del plan propio.

Cada ejercicio requiere repeticiones, duración o distancia. Posiciones únicas. `sets` es opcional para actividades que se registran como un bloque.

### POST /workout-logs

```json
{
  "workout_id":1,
  "performed_on":"2026-10-05",
  "status":"partial",
  "duration_seconds":1200,
  "results":[
    {"position":1,"set_number":1,"reps":8,"weight_kg":20,"rpe":7},
    {"position":1,"set_number":2,"reps":7,"weight_kg":20,"rpe":8}
  ]
}
```

Resultados por posición y número de serie, sin duplicados. `completed` y `partial` requieren resultados; `skipped` requiere la lista vacía. Fechas futuras se rechazan. La declaración de `completed` la hace el usuario, pero una sugerencia de aumento exige que estén registradas todas las series prescritas de ese ejercicio, con repeticiones cumplidas y RPE <=8.

### POST /recommendations/progression

```json
{"log_id":1}
```

Devuelve una sugerencia; nunca altera la prescripción ni el historial. No es una regla avanzada para running o movilidad.

## Nutrición

Todos los valores del alimento se expresan **por 100 gramos**. `serving_grams` define el peso de una porción. El usuario puede registrar alimentos usando los valores de su etiqueta.

### POST /nutrition/foods

```json
{"name":"Mi yogur","calories":60,"protein_g":4,"carbs_g":5,"fat_g":2.7,"serving_grams":125,"reference":"Etiqueta del producto"}
```

### POST /nutrition/estimate

```json
{"equation_sex":"male","activity_factor":1.2,"calorie_adjustment":0}
```

`equation_sex` selecciona el coeficiente de la ecuación; no se infiere del campo libre `gender`. Factor entre 1.2 y 1.9, ajuste explícito entre -500 y +500 kcal. Uso limitado por el MVP a adultos 18–80 y resultados 1200–5000 kcal. No hay reducción automática por `goal`. El resultado propone una distribución inicial de 25% proteína, 45% carbohidratos y 30% grasas, editable al guardar.

La ecuación estima gasto en reposo; el factor de actividad es una hipótesis indicada por el usuario. La estimación no se guarda hasta llamar PUT `/nutrition/targets` con los cuatro valores numéricos. No se debe usar como prescripción clínica.

### PUT /nutrition/targets

```json
{"calories":2000,"protein_g":125,"carbs_g":225,"fat_g":66.7}
```

Las calorías de la meta deben concordar con 4 kcal/g de proteína, 4 kcal/g de carbohidratos y 9 kcal/g de grasa con tolerancia de 10%. Las comidas usan las calorías declaradas del alimento, sin forzarlas a esa ecuación aproximada.

### POST /nutrition/meals

```json
{"food_id":1,"recorded_on":"2026-10-05","meal":"lunch","grams":150}
```

Alternativa: `servings: 1.5` en lugar de `grams`. No se admiten ambas. Si el alimento no define porción, usa gramos. Valores de `meal`: `breakfast`, `lunch`, `dinner`, `snack`.

El resumen diario incluye consumido, meta, saldo y comidas. Si no existe meta, `target` y `remaining` son null. El saldo puede ser negativo cuando se supera una meta.

Para corregir una comida, elimina el registro y crea uno nuevo. No hay editor de comidas compuestas ni menús automáticos.

## Peso

PUT `/progress/weight`:

```json
{"recorded_on":"2026-10-05","weight_kg":75}
```

Un registro por usuario y fecha; repetir el día actualiza ese dato. No modifica automáticamente el peso del perfil ni recalcula las metas. El resumen de peso compara el primer y último registro por fecha.

## Errores

- 401: autenticación inválida, ausente, expirada o usuario inactivo.
- 403: intento de editar/eliminar contenido de plataforma.
- 404: recurso inexistente o privado de otro usuario.
- 409: registro duplicado, referencias de base incompatibles o prerrequisito pendiente.
- 422: validación de campos, fechas o estructura.
- 503: `/health/database` cuando no se puede conectar a la base.
