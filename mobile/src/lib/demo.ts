import type {
  Profile,
  Workout,
  Plan,
  Exercise,
  Food,
  Meal,
  Weight,
  WorkoutLog,
  Macros,
  LogInput,
  SetInput,
} from "../types";
import { today } from "./utils";
export const demoUser = {
  id: 1,
  name: "Kenji",
  email: "demo@kenfit.app",
  is_active: true,
};
const meta = (id: number, name: string) => ({
  id,
  name,
  description: null,
  owner_id: null,
  source: "SYSTEM",
  visibility: "platform",
  parent_id: null,
  is_active: true,
  created_at: "2026-10-01T12:00:00Z",
});
let profile: Profile;
let exercises: Exercise[];
let workouts: Workout[];
let plans: Plan[];
let foods: Food[];
let meals: Meal[];
let weights: Weight[];
let logs: WorkoutLog[];
let target: Macros;
let counter = 50;
export function resetDemo() {
  counter = 50;
  profile = {
    id: 1,
    user_id: 1,
    birth_date: "2000-01-01",
    gender: "male",
    height_cm: 175,
    weight_kg: 75,
    fitness_level: "beginner",
    goal: "general_fitness",
    days_per_week: 3,
    session_minutes: 45,
    available_equipment: ["bodyweight"],
    preferred_discipline: "strength",
  };
  exercises = [
    "Sentadilla corporal",
    "Flexión inclinada",
    "Puente de glúteos",
    "Bird dog",
  ].map((name, i) => ({
    ...meta(i + 1, name),
    discipline: "strength",
    exercise_type: "movement",
    equipment: "bodyweight",
    difficulty: "beginner",
    modality: null,
    instructions:
      "Realiza el movimiento de forma controlada y dentro de un rango cómodo.",
    muscle_groups: [],
  }));
  workouts = [
    {
      ...meta(1, "Full Body · Base"),
      discipline: "strength",
      exercises: exercises.map((e, i) => ({
        exercise_id: e.id,
        position: i + 1,
        sets: 2,
        reps: 8,
        rest_seconds: 90,
      })),
    },
  ];
  plans = [
    {
      ...meta(1, "Tu punto de partida"),
      owner_id: 1,
      source: "USER",
      visibility: "private",
      weeks: 4,
      goal: "general_fitness",
      split_id: null,
      schedule: Array.from({ length: 4 }, (_, i) =>
        [1, 3, 5].map((day) => ({
          week: i + 1,
          day,
          workout_id: 1,
          phase: "base",
        })),
      ).flat(),
    },
  ];
  foods = [
    {
      id: 1,
      name: "Arroz blanco, cocido",
      calories: 130,
      protein_g: 2.7,
      carbs_g: 28.2,
      fat_g: 0.3,
      serving_grams: 150,
      owner_id: null,
      source: "SYSTEM",
      reference: "Dato aproximado de demostración",
    },
    {
      id: 2,
      name: "Pechuga de pollo, cocida",
      calories: 165,
      protein_g: 31,
      carbs_g: 0,
      fat_g: 3.6,
      serving_grams: 100,
      owner_id: null,
      source: "SYSTEM",
      reference: "Dato aproximado de demostración",
    },
    {
      id: 3,
      name: "Banana",
      calories: 89,
      protein_g: 1.1,
      carbs_g: 22.8,
      fat_g: 0.3,
      serving_grams: 100,
      owner_id: null,
      source: "SYSTEM",
      reference: "Dato aproximado de demostración",
    },
  ];
  target = { calories: 2000, protein_g: 125, carbs_g: 225, fat_g: 66.7 };
  meals = [
    {
      id: 1,
      food_id: 1,
      food_name: foods[0]!.name,
      recorded_on: today(),
      meal: "lunch",
      grams: 150,
      calories: 195,
      protein_g: 4.05,
      carbs_g: 42.3,
      fat_g: 0.45,
    },
    {
      id: 2,
      food_id: 2,
      food_name: foods[1]!.name,
      recorded_on: today(),
      meal: "lunch",
      grams: 100,
      calories: 165,
      protein_g: 31,
      carbs_g: 0,
      fat_g: 3.6,
    },
  ];
  weights = [
    { id: 1, recorded_on: "2026-09-20", weight_kg: 76.2 },
    { id: 2, recorded_on: today(), weight_kg: 75 },
  ];
  logs = [];
}
resetDemo();
export async function demoRequest(
  rawPath: string,
  method: string,
  rawBody?: unknown,
): Promise<unknown> {
  await new Promise((resolve) => setTimeout(resolve, 120));
  const url = new URL(rawPath, "https://demo.kenfit.local");
  const path = url.pathname;
  const body = (rawBody || {}) as Record<string, any>;
  const id = Number(path.split("/")[2]);
  const page = (items: unknown[]) =>
    items.slice(
      Number(url.searchParams.get("offset") || 0),
      Number(url.searchParams.get("offset") || 0) +
        Number(url.searchParams.get("limit") || 100),
    );
  const find = <T extends { id: number }>(items: T[], key: number) => {
    const item = items.find((x) => x.id === key);
    if (!item) throw new Error("Contenido de demostración no encontrado.");
    return item;
  };
  if (path === "/auth/me") return demoUser;
  if (path === "/fitness-profile") {
    if (method === "POST" || method === "PATCH" || method === "PUT")
      profile = { ...profile, ...body };
    return profile;
  }
  if (path === "/exercises" && method === "GET")
    return page(exercises.filter((x) => x.is_active));
  if (path === "/exercises" && method === "POST") {
    const e = {
      ...meta(++counter, body.name),
      discipline: body.discipline,
      exercise_type: body.exercise_type,
      equipment: body.equipment ?? null,
      difficulty: null,
      instructions: body.instructions ?? null,
      modality: null,
      owner_id: 1,
      source: "USER",
      visibility: "private",
      muscle_groups: [],
    } as Exercise;
    exercises.push(e);
    return e;
  }
  if (path === "/workouts" && method === "GET")
    return page(workouts.filter((x) => x.is_active));
  if (path === "/workouts" && method === "POST") {
    const w = {
      ...meta(++counter, body.name),
      ...body,
      owner_id: 1,
      source: "USER",
      visibility: "private",
    } as Workout;
    workouts.push(w);
    return w;
  }
  if (path.startsWith("/workouts/")) {
    const w = find(workouts, id);
    if (method === "PUT") {
      if (w.source === "SYSTEM")
        throw new Error("Duplica la sesión oficial antes de editarla.");
      Object.assign(w, body);
      return w;
    }
    if (path.endsWith("/duplicate")) {
      const copy = {
        ...w,
        id: ++counter,
        name: w.name + " · Mi copia",
        owner_id: 1,
        source: "USER",
        visibility: "private",
        parent_id: w.id,
        exercises: w.exercises.map((x) => ({ ...x })),
      };
      workouts.push(copy);
      return copy;
    }
    return w;
  }
  if (path === "/training-plans") return page(plans);
  if (path.startsWith("/training-plans/")) return find(plans, id);
  if (path === "/splits") return [];
  if (path === "/recommendations/training-plan") {
    const weeks = Number(body.weeks || 4),
      days = Number(body.days_per_week || profile.days_per_week);
    if (profile.preferred_discipline === "strength" && days > 3)
      throw new Error(
        "La plantilla inicial de fuerza admite hasta 3 días por semana.",
      );
    if (profile.preferred_discipline !== "strength")
      throw new Error(
        "La demostración incluye la plantilla de fuerza. Las otras disciplinas se generan al conectar el backend.",
      );
    const pattern = [[], [1], [1, 4], [1, 3, 5]][days]!;
    const p = {
      ...meta(++counter, "Plan inicial · Mi versión"),
      source: "USER",
      owner_id: 1,
      visibility: "private",
      weeks,
      goal: profile.goal,
      split_id: null,
      schedule: Array.from({ length: weeks }, (_, i) =>
        Array.from({ length: days }, (_, d) => ({
          week: i + 1,
          day: pattern[d]!,
          workout_id: 1,
          phase: "base",
        })),
      ).flat(),
    };
    plans.push(p);
    return p;
  }
  if (path === "/workout-logs" && method === "POST") {
    const input = body as LogInput;
    const w = find(workouts, input.workout_id);
    const results = input.results.map((result: SetInput) => {
      const item = w.exercises.find((x) => x.position === result.position)!;
      return {
        ...result,
        exercise_id: item.exercise_id,
        exercise_name: find(exercises, item.exercise_id).name,
        prescribed_sets: item.sets ?? null,
        prescribed_reps: item.reps ?? null,
        prescribed_weight_kg: item.weight_kg ?? null,
        prescribed_duration_seconds: item.duration_seconds ?? null,
        prescribed_distance_meters: item.distance_meters ?? null,
      };
    });
    const log = { ...input, id: ++counter, workout_name: w.name, results };
    logs.unshift(log);
    return log;
  }
  if (path === "/workout-logs") return page(logs);
  if (path.startsWith("/workout-logs/")) return find(logs, id);
  if (path === "/recommendations/progression")
    return {
      log_id: body.log_id,
      suggestions: [
        {
          position: 1,
          action: "repeat_and_review",
          suggested_weight_kg: null,
          notice: "Repite y revisa la técnica; esta es una demostración.",
        },
      ],
    };
  if (path === "/progress/weight") {
    if (method === "PUT") {
      const existing = weights.find((w) => w.recorded_on === body.recorded_on);
      if (existing) existing.weight_kg = body.weight_kg;
      else
        weights.push({
          id: ++counter,
          recorded_on: body.recorded_on,
          weight_kg: body.weight_kg,
        });
      return weights.find((w) => w.recorded_on === body.recorded_on);
    }
    return page(
      [...weights].sort((a, b) => b.recorded_on.localeCompare(a.recorded_on)),
    );
  }
  if (path === "/progress/summary") {
    const sorted = [...weights].sort((a, b) =>
      a.recorded_on.localeCompare(b.recorded_on),
    );
    return {
      workouts_completed: logs.filter((x) => x.status === "completed").length,
      workouts_partial: logs.filter((x) => x.status === "partial").length,
      workouts_skipped: logs.filter((x) => x.status === "skipped").length,
      total_duration_seconds: logs.reduce(
        (sum, x) => sum + (x.duration_seconds || 0),
        0,
      ),
      latest_weight_kg: sorted.at(-1)?.weight_kg ?? null,
      weight_change_kg:
        sorted.length > 1
          ? sorted.at(-1)!.weight_kg - sorted[0]!.weight_kg
          : null,
    };
  }
  if (path === "/nutrition/foods") {
    if (method === "POST") {
      const food = {
        ...body,
        id: ++counter,
        source: "USER",
        owner_id: 1,
      } as Food;
      foods.push(food);
      return food;
    }
    const search = url.searchParams.get("search")?.toLowerCase() || "";
    return page(foods.filter((f) => f.name.toLowerCase().includes(search)));
  }
  if (path === "/nutrition/targets") {
    if (method === "PUT") target = body as Macros;
    return target;
  }
  if (path === "/nutrition/estimate")
    return {
      ...target,
      resting_energy_estimate: 1650,
      method: "Vista de demostración",
      notice:
        "Valores de ejemplo. No se ha calculado una recomendación para tu cuerpo.",
    };
  if (path === "/nutrition/meals" && method === "POST") {
    const food = find(foods, body.food_id);
    const grams = body.grams ?? body.servings * (food.serving_grams ?? 100);
    const meal = {
      id: ++counter,
      food_id: food.id,
      food_name: food.name,
      recorded_on: body.recorded_on,
      meal: body.meal,
      grams,
      calories: (food.calories * grams) / 100,
      protein_g: (food.protein_g * grams) / 100,
      carbs_g: (food.carbs_g * grams) / 100,
      fat_g: (food.fat_g * grams) / 100,
    };
    meals.push(meal);
    return meal;
  }
  if (path.startsWith("/nutrition/meals/") && method === "DELETE") {
    const mealId = Number(path.split("/")[3]);
    meals = meals.filter((x) => x.id !== mealId);
    return undefined;
  }
  if (path === "/nutrition/summary") {
    const day = url.searchParams.get("recorded_on") || today();
    const entries = meals.filter((x) => x.recorded_on === day);
    const consumed = { calories: 0, protein_g: 0, carbs_g: 0, fat_g: 0 };
    for (const e of entries)
      for (const k of Object.keys(consumed) as (keyof Macros)[])
        consumed[k] += e[k];
    const remaining = { ...consumed };
    for (const k of Object.keys(remaining) as (keyof Macros)[])
      remaining[k] = target[k] - consumed[k];
    return { recorded_on: day, entries, consumed, target, remaining };
  }
  throw new Error(
    `Esta función todavía no está disponible en la demostración: ${path}`,
  );
}
