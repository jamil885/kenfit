import { useEffect, useState } from "react";
import { Text, View, Pressable } from "react-native";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Ionicons } from "@expo/vector-icons";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import {
  Screen,
  Heading,
  Card,
  Button,
  Field,
  Loading,
  ErrorBox,
  Notice,
  styles,
} from "../components/ui";
import { request, allPages } from "../lib/api";
import { colors as c } from "../theme";
import { today, optionalNumber, message } from "../lib/utils";
import type {
  RootStackParams,
  Workout,
  Exercise,
  SetInput,
  WorkoutLog,
} from "../types";
type Draft = {
  position: number;
  set_number: number;
  done: boolean;
  reps: string;
  weight: string;
  duration: string;
  distance: string;
  rpe: string;
};
export function WorkoutScreen({
  route,
  navigation,
}: NativeStackScreenProps<RootStackParams, "Workout">) {
  const cache = useQueryClient();
  const workout = useQuery({
    queryKey: ["workout", route.params.workoutId],
    queryFn: ({ signal }) =>
      request<Workout>("/workouts/" + route.params.workoutId, { signal }),
  });
  const exercises = useQuery({
    queryKey: ["exercises"],
    queryFn: ({ signal }) => allPages<Exercise>("/exercises", signal),
  });
  const [rows, setRows] = useState<Draft[]>([]),
    [start, setStart] = useState<number | null>(null),
    [clock, setClock] = useState(Date.now()),
    [restUntil, setRestUntil] = useState<number | null>(null);
  const [busy, setBusy] = useState(false),
    [error, setError] = useState<string | null>(null),
    [saved, setSaved] = useState<WorkoutLog | null>(null);
  useEffect(() => {
    if (workout.data)
      setRows(
        workout.data.exercises.flatMap((x) =>
          Array.from({ length: x.sets || 1 }, (_, i) => ({
            position: x.position,
            set_number: i + 1,
            done: false,
            reps: x.reps == null ? "" : String(x.reps),
            weight: x.weight_kg == null ? "" : String(x.weight_kg),
            duration:
              x.duration_seconds == null ? "" : String(x.duration_seconds),
            distance:
              x.distance_meters == null ? "" : String(x.distance_meters),
            rpe: "",
          })),
        ),
      );
  }, [workout.data]);
  useEffect(() => {
    if (!start && !restUntil) return;
    const timer = setInterval(() => setClock(Date.now()), 1000);
    return () => clearInterval(timer);
  }, [start, restUntil]);
  const update = (index: number, field: keyof Draft, value: string | boolean) =>
    setRows((current) =>
      current.map((row, i) => (i === index ? { ...row, [field]: value } : row)),
    );
  const save = async (status: "completed" | "partial" | "skipped") => {
    setError(null);
    setBusy(true);
    try {
      const results: SetInput[] =
        status === "skipped"
          ? []
          : rows
              .filter((x) => x.done)
              .map((x) => {
                const result = {
                  position: x.position,
                  set_number: x.set_number,
                  reps: optionalNumber(x.reps, "Repeticiones", 0, 10000, true),
                  weight_kg: optionalNumber(x.weight, "Carga", 0, 2000),
                  duration_seconds: optionalNumber(
                    x.duration,
                    "Duración",
                    0,
                    86400,
                    true,
                  ),
                  distance_meters: optionalNumber(
                    x.distance,
                    "Distancia",
                    0,
                    1000000,
                  ),
                  rpe: optionalNumber(x.rpe, "RPE", 1, 10),
                };
                if (
                  result.reps === undefined &&
                  result.duration_seconds === undefined &&
                  result.distance_meters === undefined
                )
                  throw new Error(
                    "Indica repeticiones, tiempo o distancia para cada serie realizada.",
                  );
                return result;
              });
      if (status !== "skipped" && !results.length)
        throw new Error("Marca al menos una serie como realizada.");
      if (status === "completed" && results.length !== rows.length)
        throw new Error(
          "Para completar la sesión, marca todas las series. Si terminaste antes, guarda una sesión parcial.",
        );
      const log = await request<WorkoutLog>("/workout-logs", {
        method: "POST",
        body: {
          workout_id: route.params.workoutId,
          performed_on: today(),
          status,
          results,
          ...(start
            ? {
                duration_seconds: Math.max(
                  1,
                  Math.floor((Date.now() - start) / 1000),
                ),
              }
            : {}),
        },
      });
      setSaved(log);
      setStart(null);
      setRestUntil(null);
      await cache.invalidateQueries({ queryKey: ["logs"] });
      await cache.invalidateQueries({ queryKey: ["progress"] });
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  };
  const duplicate = async () => {
    setBusy(true);
    setError(null);
    try {
      const copy = await request<Workout>(
        `/workouts/${route.params.workoutId}/duplicate`,
        { method: "POST" },
      );
      await cache.invalidateQueries({ queryKey: ["workouts"] });
      navigation.replace("Workout", { workoutId: copy.id });
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  };
  const elapsed = start ? Math.max(0, Math.floor((clock - start) / 1000)) : 0;
  return (
    <Screen>
      <Heading
        eyebrow="SESIÓN DE ENTRENAMIENTO"
        title={workout.data?.name || "Tu sesión"}
        subtitle={
          workout.data
            ? `${workout.data.exercises.length} ejercicios · ${workout.data.source === "SYSTEM" ? "Plantilla KenFit" : "Tu contenido"}`
            : undefined
        }
      />
      <ErrorBox error={error} />
      {saved ? (
        <Card>
          <Ionicons name="checkmark-circle" size={44} color={c.accent} />
          <Text style={styles.cardTitle}>Sesión registrada</Text>
          <Text style={styles.body}>
            Se guardó en tu historial como{" "}
            {saved.status === "completed"
              ? "completada"
              : saved.status === "partial"
                ? "parcial"
                : "omitida"}
            .
          </Text>
          <Button
            title="Ver mi registro"
            onPress={() => navigation.replace("LogDetail", { logId: saved.id })}
          />
          <Button
            title="Volver"
            secondary
            onPress={() => navigation.goBack()}
          />
        </Card>
      ) : workout.isPending ? (
        <Loading />
      ) : workout.error ? (
        <ErrorBox
          error={message(workout.error)}
          retry={() => void workout.refetch()}
        />
      ) : (
        <>
          {exercises.error && (
            <ErrorBox
              error={message(exercises.error)}
              retry={() => void exercises.refetch()}
            />
          )}
          <Notice>
            Ajusta los resultados reales y marca cada serie realizada. Los
            valores iniciales son la prescripción, no un registro de lo que
            hiciste.
          </Notice>
          <Card>
            <View
              style={{
                flexDirection: "row",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <View>
                <Text style={styles.caption}>TIEMPO DE SESIÓN</Text>
                <Text style={styles.stat}>
                  {String(Math.floor(elapsed / 60)).padStart(2, "0")}:
                  {String(elapsed % 60).padStart(2, "0")}
                </Text>
              </View>
              <Ionicons name="timer-outline" size={32} color={c.mint} />
            </View>
            {!start && (
              <Button
                title="Iniciar cronómetro"
                secondary
                onPress={() => {
                  setClock(Date.now());
                  setStart(Date.now());
                }}
              />
            )}
            {restUntil !== null && (
              <Text style={{ color: c.accent }}>
                Descanso: {Math.max(0, Math.ceil((restUntil - clock) / 1000))} s
              </Text>
            )}
          </Card>
          {workout.data.exercises.map((item) => {
            const exercise = exercises.data?.find(
              (x) => x.id === item.exercise_id,
            );
            return (
              <Card key={item.position}>
                <Text style={styles.eyebrow}>EJERCICIO {item.position}</Text>
                <Text style={styles.cardTitle}>
                  {exercise?.name || `Ejercicio #${item.exercise_id}`}
                </Text>
                <Text style={styles.body}>
                  {item.sets || 1} {item.sets ? "series" : "bloque"}
                  {item.reps ? ` × ${item.reps} repeticiones` : ""}
                  {item.duration_seconds ? ` · ${item.duration_seconds} s` : ""}
                  {item.distance_meters ? ` · ${item.distance_meters} m` : ""}
                </Text>
                {exercise?.instructions && (
                  <Text style={styles.caption}>{exercise.instructions}</Text>
                )}
                {rows.map((row, index) =>
                  row.position !== item.position ? null : (
                    <View
                      key={row.set_number}
                      style={{
                        borderTopWidth: 1,
                        borderColor: c.border,
                        paddingTop: 16,
                        gap: 10,
                      }}
                    >
                      <Pressable
                        accessibilityRole="checkbox"
                        accessibilityState={{ checked: row.done }}
                        accessibilityLabel={`Serie ${row.set_number} de ${exercise?.name || "ejercicio " + item.position} realizada`}
                        onPress={() => update(index, "done", !row.done)}
                        style={{
                          flexDirection: "row",
                          alignItems: "center",
                          gap: 10,
                          paddingVertical: 6,
                        }}
                      >
                        <Ionicons
                          name={row.done ? "checkbox" : "square-outline"}
                          color={row.done ? c.accent : c.muted}
                          size={24}
                        />
                        <Text style={styles.label}>
                          Serie {row.set_number} ·{" "}
                          {row.done ? "realizada" : "pendiente"}
                        </Text>
                      </Pressable>
                      <View style={styles.grid}>
                        {item.reps != null && (
                          <View style={{ flex: 1 }}>
                            <Field
                              label={`Reps · ejercicio ${item.position}, serie ${row.set_number}`}
                              value={row.reps}
                              onChangeText={(v) => update(index, "reps", v)}
                              keyboardType="number-pad"
                            />
                          </View>
                        )}
                        <View style={{ flex: 1 }}>
                          <Field
                            label={`Carga kg · ejercicio ${item.position}, serie ${row.set_number}`}
                            value={row.weight}
                            onChangeText={(v) => update(index, "weight", v)}
                            keyboardType="decimal-pad"
                            placeholder="Opcional"
                          />
                        </View>
                      </View>
                      {item.duration_seconds != null && (
                        <Field
                          label={`Tiempo s · ejercicio ${item.position}, serie ${row.set_number}`}
                          value={row.duration}
                          onChangeText={(v) => update(index, "duration", v)}
                          keyboardType="number-pad"
                        />
                      )}
                      {item.distance_meters != null && (
                        <Field
                          label={`Distancia m · ejercicio ${item.position}, serie ${row.set_number}`}
                          value={row.distance}
                          onChangeText={(v) => update(index, "distance", v)}
                          keyboardType="decimal-pad"
                        />
                      )}
                      <Field
                        label={`Esfuerzo RPE 1–10 · ejercicio ${item.position}, serie ${row.set_number}`}
                        value={row.rpe}
                        onChangeText={(v) => update(index, "rpe", v)}
                        keyboardType="decimal-pad"
                        placeholder="Opcional"
                      />
                    </View>
                  ),
                )}
                {!!item.rest_seconds && (
                  <Button
                    title={`Descansar ${item.rest_seconds} s`}
                    secondary
                    onPress={() => {
                      setClock(Date.now());
                      setRestUntil(Date.now() + item.rest_seconds! * 1000);
                    }}
                  />
                )}
              </Card>
            );
          })}
          <Button
            title="Completar y guardar sesión"
            loading={busy}
            onPress={() => void save("completed")}
          />
          <Button
            title="Guardar sesión parcial"
            secondary
            disabled={busy}
            onPress={() => void save("partial")}
          />
          <Button
            title="Registrar sesión omitida"
            secondary
            disabled={busy}
            onPress={() => void save("skipped")}
          />
          {workout.data.source === "USER" && (
            <Button
              title="Editar mi sesión"
              secondary
              disabled={busy || rows.some((row) => row.done)}
              onPress={() =>
                navigation.navigate("CreateWorkout", {
                  workoutId: workout.data.id,
                })
              }
            />
          )}
          {workout.data.source === "SYSTEM" && (
            <Button
              title="Guardar una copia propia"
              secondary
              disabled={busy}
              onPress={() => void duplicate()}
            />
          )}
        </>
      )}
    </Screen>
  );
}
