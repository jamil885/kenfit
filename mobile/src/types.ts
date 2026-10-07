export type User = {
  id: number;
  name: string;
  email: string;
  is_active: boolean;
};
export type ProfileInput = {
  birth_date: string;
  gender: string;
  height_cm: number;
  weight_kg: number;
  fitness_level: string;
  goal: string;
  days_per_week: number;
  session_minutes: number;
  available_equipment: string[];
  preferred_discipline: string;
};
export type Profile = ProfileInput & { id: number; user_id: number };
export type Content = {
  id: number;
  name: string;
  description: string | null;
  owner_id: number | null;
  source: string;
  visibility: string;
  parent_id: number | null;
  is_active: boolean;
  created_at: string;
};
export type Exercise = Content & {
  discipline: string;
  exercise_type: string;
  equipment: string | null;
  difficulty: string | null;
  instructions: string | null;
  modality: string | null;
  muscle_groups: { muscle_group_id: number; role: string }[];
};
export type Prescription = {
  exercise_id: number;
  position: number;
  sets?: number | null;
  reps?: number | null;
  duration_seconds?: number | null;
  distance_meters?: number | null;
  weight_kg?: number | null;
  rest_seconds?: number | null;
  intensity?: string | null;
  tempo?: string | null;
  notes?: string | null;
  progression?: string | null;
};
export type Workout = Content & {
  discipline: string;
  exercises: Prescription[];
};
export type Plan = Content & {
  weeks: number;
  goal: string;
  split_id: number | null;
  schedule: {
    week: number;
    day: number;
    workout_id: number;
    phase: string | null;
  }[];
};
export type Split = Content & {
  cycle_days: number;
  days: { day: number; workout_id: number | null; label: string | null }[];
};
export type SetInput = {
  position: number;
  set_number: number;
  reps?: number;
  weight_kg?: number;
  duration_seconds?: number;
  distance_meters?: number;
  rpe?: number;
};
export type LogInput = {
  workout_id: number;
  performed_on: string;
  status: "completed" | "partial" | "skipped";
  duration_seconds?: number;
  notes?: string;
  results: SetInput[];
};
export type WorkoutLog = Omit<LogInput, "results"> & {
  id: number;
  workout_name: string;
  results: (SetInput & {
    exercise_id: number;
    exercise_name: string;
    prescribed_sets: number | null;
    prescribed_reps: number | null;
    prescribed_weight_kg: number | null;
    prescribed_duration_seconds: number | null;
    prescribed_distance_meters: number | null;
  })[];
};
export type Macros = {
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
};
export type Food = Macros & {
  id: number;
  name: string;
  source: string;
  owner_id: number | null;
  serving_grams: number | null;
  reference: string | null;
};
export type Meal = Macros & {
  id: number;
  food_id: number;
  food_name: string;
  recorded_on: string;
  meal: string;
  grams: number;
};
export type DaySummary = {
  recorded_on: string;
  consumed: Macros;
  target: Macros | null;
  remaining: Macros | null;
  entries: Meal[];
};
export type Weight = { id: number; recorded_on: string; weight_kg: number };
export type Progress = {
  workouts_completed: number;
  workouts_partial: number;
  workouts_skipped: number;
  total_duration_seconds: number;
  latest_weight_kg: number | null;
  weight_change_kg: number | null;
};
export type Estimate = Macros & {
  resting_energy_estimate: number;
  method: string;
  notice: string;
};
export type RootStackParams = {
  Main: undefined;
  Workout: { workoutId: number };
  Plan: { planId: number };
  AddMeal: { date: string };
  Targets: undefined;
  CreateFood: undefined;
  LogDetail: { logId: number };
  CreateWorkout: { workoutId?: number } | undefined;
  CreateExercise: undefined;
};
export type TabParams = {
  Home: undefined;
  Training: undefined;
  Nutrition: undefined;
  Progress: undefined;
  Profile: undefined;
};
