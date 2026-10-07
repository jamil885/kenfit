import { useState } from "react";
import { Text } from "react-native";
import { useQuery } from "@tanstack/react-query";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import {
  Screen,
  Heading,
  Card,
  Button,
  ErrorBox,
  Loading,
  Notice,
  Row,
  styles,
} from "../components/ui";
import { request } from "../lib/api";
import { format, displayDate, message } from "../lib/utils";
import type { RootStackParams, WorkoutLog } from "../types";
type Suggestion = {
  position: number;
  action: string;
  suggested_weight_kg: number | null;
  notice: string;
};
export function LogDetailScreen({
  route,
}: NativeStackScreenProps<RootStackParams, "LogDetail">) {
  const log = useQuery({
    queryKey: ["log", route.params.logId],
    queryFn: ({ signal }) =>
      request<WorkoutLog>("/workout-logs/" + route.params.logId, { signal }),
  });
  const [suggestions, setSuggestions] = useState<Suggestion[] | null>(null),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<string | null>(null);
  const review = async () => {
    setBusy(true);
    setError(null);
    try {
      const response = await request<{ suggestions: Suggestion[] }>(
        "/recommendations/progression",
        { method: "POST", body: { log_id: route.params.logId } },
      );
      setSuggestions(response.suggestions);
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  };
  return (
    <Screen>
      <Heading
        eyebrow="TU HISTORIAL"
        title={log.data?.workout_name || "Registro de sesión"}
        subtitle={
          log.data
            ? `${displayDate(log.data.performed_on)} · ${log.data.status === "completed" ? "Completada" : log.data.status === "partial" ? "Parcial" : "Omitida"}`
            : undefined
        }
      />
      {log.isPending ? (
        <Loading />
      ) : log.error ? (
        <ErrorBox error={message(log.error)} retry={() => void log.refetch()} />
      ) : (
        <>
          {log.data.duration_seconds && (
            <Notice>
              Duración registrada: {format(log.data.duration_seconds / 60, 1)}{" "}
              minutos.
            </Notice>
          )}
          {log.data.results.map((result) => (
            <Card key={`${result.position}-${result.set_number}`}>
              <Text style={styles.cardTitle}>{result.exercise_name}</Text>
              <Text style={styles.caption}>SERIE {result.set_number}</Text>
              <Text style={styles.body}>
                Realizado:{" "}
                {[
                  result.reps == null ? null : `${result.reps} reps`,
                  result.weight_kg == null
                    ? null
                    : `${format(result.weight_kg, 1)} kg`,
                  result.duration_seconds == null
                    ? null
                    : `${result.duration_seconds} s`,
                  result.distance_meters == null
                    ? null
                    : `${format(result.distance_meters)} m`,
                ]
                  .filter(Boolean)
                  .join(" · ")}
              </Text>
              <Text style={styles.caption}>
                Prescrito:{" "}
                {[
                  result.prescribed_reps == null
                    ? null
                    : `${result.prescribed_reps} reps`,
                  result.prescribed_weight_kg == null
                    ? null
                    : `${format(result.prescribed_weight_kg, 1)} kg`,
                  result.prescribed_duration_seconds == null
                    ? null
                    : `${result.prescribed_duration_seconds} s`,
                  result.prescribed_distance_meters == null
                    ? null
                    : `${result.prescribed_distance_meters} m`,
                ]
                  .filter(Boolean)
                  .join(" · ") || "Ver sesión original"}
              </Text>
              {result.rpe != null && (
                <Text style={styles.caption}>
                  Esfuerzo percibido: {result.rpe} / 10
                </Text>
              )}
            </Card>
          ))}
          {log.data.results.length > 0 && (
            <>
              <ErrorBox error={error} />
              <Button
                title="Revisar sugerencias de progresión"
                loading={busy}
                secondary
                onPress={() => void review()}
              />
              {suggestions && (
                <Card>
                  <Text style={styles.cardTitle}>Para tu próxima sesión</Text>
                  <Notice>
                    Son sugerencias basadas en reglas. No cambian tu rutina
                    automáticamente. Revisa técnica y recuperación antes de
                    aumentar la carga.
                  </Notice>
                  {suggestions.map((s) => (
                    <Row
                      key={s.position}
                      title={`Ejercicio ${s.position} · ${s.action === "review_increase" ? "Revisar aumento" : "Repetir y revisar"}`}
                      subtitle={
                        s.suggested_weight_kg == null
                          ? "Mantén el foco en ejecución y constancia."
                          : `Carga orientativa: ${format(s.suggested_weight_kg, 2)} kg`
                      }
                    />
                  ))}
                </Card>
              )}
            </>
          )}
        </>
      )}
    </Screen>
  );
}
