import { useState, useEffect, useRef } from "react";
import { Text } from "react-native";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import {
  Screen,
  Heading,
  Card,
  Button,
  Field,
  Chips,
  ErrorBox,
  Loading,
  Row,
  styles,
} from "../components/ui";
import { request, allPages } from "../lib/api";
import {
  numeric,
  optionalNumber,
  disciplineLabels,
  message,
} from "../lib/utils";
import type {
  RootStackParams,
  Exercise,
  Workout,
  Prescription,
} from "../types";
type Item = {
  key: number;
  exercise: Exercise;
  mode: string;
  sets: string;
  reps: string;
  seconds: string;
  meters: string;
  weight: string;
  rest: string;
  prescription?: Prescription;
};
export function CreateWorkoutScreen({
  route,
  navigation,
}: NativeStackScreenProps<RootStackParams, "CreateWorkout">) {
  const cache = useQueryClient();
  const [name, setName] = useState(""),
    [discipline, setDiscipline] = useState("strength"),
    [search, setSearch] = useState(""),
    [items, setItems] = useState<Item[]>([]),
    [key, setKey] = useState(0),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<string | null>(null);
  const editingId = route.params?.workoutId;
  const initialized = useRef(false);
  const existing = useQuery({
    queryKey: ["workout-edit", editingId],
    enabled: !!editingId,
    queryFn: ({ signal }) =>
      request<Workout>("/workouts/" + editingId, { signal }),
  });
  const exercises = useQuery({
    queryKey: ["exercises"],
    queryFn: ({ signal }) => allPages<Exercise>("/exercises", signal),
  });
  useEffect(() => {
    if (!existing.data || !exercises.data || initialized.current) return;
    initialized.current = true;
    setName(existing.data.name);
    setDiscipline(existing.data.discipline);
    setItems(
      existing.data.exercises.map((p, i) => ({
        key: i,
        exercise:
          exercises.data.find((e) => e.id === p.exercise_id) ||
          ({
            id: p.exercise_id,
            name: "Ejercicio archivado #" + p.exercise_id,
          } as Exercise),
        mode:
          p.duration_seconds && p.distance_meters
            ? "mixed"
            : p.reps
              ? "reps"
              : p.duration_seconds
                ? "time"
                : "distance",
        sets: String(p.sets || 1),
        reps: String(p.reps || 8),
        seconds: String(p.duration_seconds || 60),
        meters: String(p.distance_meters || 1000),
        weight: p.weight_kg == null ? "" : String(p.weight_kg),
        rest: p.rest_seconds == null ? "" : String(p.rest_seconds),
        prescription: p,
      })),
    );
    setKey(existing.data.exercises.length);
  }, [existing.data, exercises.data]);
  const update = (id: number, field: keyof Item, value: string) =>
    setItems((current) =>
      current.map((x) => (x.key === id ? { ...x, [field]: value } : x)),
    );
  const add = (exercise: Exercise) => {
    setItems([
      ...items,
      {
        key,
        exercise,
        mode: exercise.discipline === "running" ? "time" : "reps",
        sets: "2",
        reps: "8",
        seconds: "60",
        meters: "1000",
        weight: "",
        rest: "90",
      },
    ]);
    setKey(key + 1);
  };
  const save = async () => {
    setBusy(true);
    setError(null);
    try {
      if (name.trim().length < 2)
        throw new Error("Ingresa el nombre de tu sesión.");
      if (!items.length) throw new Error("Añade al menos un ejercicio.");
      const entries: Prescription[] = items.map((x, i) => ({
        ...x.prescription,
        reps: undefined,
        duration_seconds: undefined,
        distance_meters: undefined,
        exercise_id: x.exercise.id,
        position: i + 1,
        sets: numeric(x.sets, "Series", 1, 100, true),
        ...(x.mode === "reps"
          ? { reps: numeric(x.reps, "Repeticiones", 1, 10000, true) }
          : x.mode === "time"
            ? { duration_seconds: numeric(x.seconds, "Tiempo", 1, 86400, true) }
            : x.mode === "mixed"
              ? {
                  duration_seconds: numeric(
                    x.seconds,
                    "Tiempo",
                    1,
                    86400,
                    true,
                  ),
                  distance_meters: numeric(x.meters, "Distancia", 1, 1000000),
                }
              : {
                  distance_meters: numeric(x.meters, "Distancia", 1, 1000000),
                }),
        weight_kg: optionalNumber(x.weight, "Carga", 0, 2000),
        rest_seconds: optionalNumber(x.rest, "Descanso", 0, 7200, true),
      }));
      const workout = await request<Workout>(
        editingId ? "/workouts/" + editingId : "/workouts",
        {
          method: editingId ? "PUT" : "POST",
          body: { name: name.trim(), discipline, exercises: entries },
        },
      );
      await cache.invalidateQueries({ queryKey: ["workouts"] });
      await cache.invalidateQueries({ queryKey: ["workout", editingId] });
      navigation.replace("Workout", { workoutId: workout.id });
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  };
  if (
    editingId &&
    (!initialized.current || existing.error || exercises.error)
  ) {
    return (
      <Screen>
        <Heading eyebrow="A TU MANERA" title="Edita tu sesión" />
        {existing.error ? (
          <ErrorBox
            error={message(existing.error)}
            retry={() => void existing.refetch()}
          />
        ) : exercises.error ? (
          <ErrorBox
            error={message(exercises.error)}
            retry={() => void exercises.refetch()}
          />
        ) : (
          <Loading />
        )}
      </Screen>
    );
  }
  return (
    <Screen>
      <Heading
        eyebrow="A TU MANERA"
        title={editingId ? "Edita tu sesión" : "Crea una sesión"}
        subtitle="Combina ejercicios del catálogo y define cómo los realizarás."
      />
      <ErrorBox error={error} />
      {editingId && existing.isPending && <Loading />}
      {existing.error && (
        <ErrorBox
          error={message(existing.error)}
          retry={() => void existing.refetch()}
        />
      )}
      <Field
        label="Nombre de la sesión"
        value={name}
        onChangeText={setName}
        maxLength={100}
      />
      <Chips
        label="Disciplina"
        value={discipline}
        onChange={setDiscipline}
        values={Object.entries(disciplineLabels).map(([value, label]) => ({
          value,
          label,
        }))}
      />
      {items.map((item, index) => (
        <Card key={item.key}>
          <Text style={styles.cardTitle}>
            {index + 1}. {item.exercise.name}
          </Text>
          <Chips
            label="Tipo de prescripción"
            value={item.mode}
            onChange={(v) => update(item.key, "mode", v)}
            values={[
              { value: "reps", label: "Reps" },
              { value: "time", label: "Tiempo" },
              { value: "distance", label: "Distancia" },
              { value: "mixed", label: "Tiempo + distancia" },
            ]}
          />
          <Field
            label={`Series · ${index + 1}`}
            value={item.sets}
            onChangeText={(v) => update(item.key, "sets", v)}
            keyboardType="number-pad"
          />
          {item.mode === "reps" ? (
            <Field
              label={`Repeticiones · ${index + 1}`}
              value={item.reps}
              onChangeText={(v) => update(item.key, "reps", v)}
              keyboardType="number-pad"
            />
          ) : item.mode === "time" || item.mode === "mixed" ? (
            <Field
              label={`Duración en segundos · ${index + 1}`}
              value={item.seconds}
              onChangeText={(v) => update(item.key, "seconds", v)}
              keyboardType="number-pad"
            />
          ) : (
            <Field
              label={`Distancia en metros · ${index + 1}`}
              value={item.meters}
              onChangeText={(v) => update(item.key, "meters", v)}
              keyboardType="decimal-pad"
            />
          )}
          {item.mode === "mixed" && (
            <Field
              label={`Distancia en metros · ${index + 1}`}
              value={item.meters}
              onChangeText={(v) => update(item.key, "meters", v)}
              keyboardType="decimal-pad"
            />
          )}
          <Field
            label={`Carga kg, opcional · ${index + 1}`}
            value={item.weight}
            onChangeText={(v) => update(item.key, "weight", v)}
            keyboardType="decimal-pad"
          />
          <Field
            label={`Descanso en segundos · ${index + 1}`}
            value={item.rest}
            onChangeText={(v) => update(item.key, "rest", v)}
            keyboardType="number-pad"
          />
          <Button
            title={`Quitar ${item.exercise.name}`}
            secondary
            onPress={() => setItems(items.filter((x) => x.key !== item.key))}
          />
        </Card>
      ))}
      {items.length > 0 && (
        <Button
          title={
            editingId ? "Guardar cambios de sesión" : "Guardar sesión propia"
          }
          loading={busy}
          onPress={() => void save()}
        />
      )}
      <Field
        label="Buscar ejercicio para añadir"
        value={search}
        onChangeText={setSearch}
        maxLength={100}
      />
      {exercises.isPending ? (
        <Loading />
      ) : exercises.error ? (
        <ErrorBox
          error={message(exercises.error)}
          retry={() => void exercises.refetch()}
        />
      ) : (
        <Card>
          {exercises.data
            .filter((x) => x.name.toLowerCase().includes(search.toLowerCase()))
            .map((e) => (
              <Row
                key={e.id}
                title={e.name}
                subtitle={disciplineLabels[e.discipline] || e.discipline}
                onPress={() => add(e)}
              />
            ))}
        </Card>
      )}
      <Button
        title="Crear ejercicio propio"
        secondary
        onPress={() => navigation.navigate("CreateExercise")}
      />
    </Screen>
  );
}
