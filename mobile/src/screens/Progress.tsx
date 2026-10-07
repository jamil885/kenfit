import { useState } from "react";
import { Text, View } from "react-native";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import {
  Screen,
  Heading,
  Card,
  Button,
  Field,
  ErrorBox,
  Loading,
  Section,
  Row,
  Empty,
  Notice,
  styles,
} from "../components/ui";
import { request, allPages } from "../lib/api";
import { today, format, displayDate, numeric, message } from "../lib/utils";
import { colors as c } from "../theme";
import type { RootStackParams, Progress, Weight, WorkoutLog } from "../types";
export function ProgressScreen() {
  const nav = useNavigation<NativeStackNavigationProp<RootStackParams>>(),
    cache = useQueryClient();
  const summary = useQuery({
    queryKey: ["progress"],
    queryFn: ({ signal }) => request<Progress>("/progress/summary", { signal }),
  });
  const weights = useQuery({
    queryKey: ["weights"],
    queryFn: ({ signal }) => allPages<Weight>("/progress/weight", signal),
  });
  const logs = useQuery({
    queryKey: ["logs"],
    queryFn: ({ signal }) => allPages<WorkoutLog>("/workout-logs", signal),
  });
  const [weight, setWeight] = useState(""),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<string | null>(null),
    [success, setSuccess] = useState(false);
  const save = async () => {
    setBusy(true);
    setError(null);
    setSuccess(false);
    try {
      await request("/progress/weight", {
        method: "PUT",
        body: {
          recorded_on: today(),
          weight_kg: numeric(weight, "Peso", 0.1, 500),
        },
      });
      await cache.invalidateQueries({ queryKey: ["weights"] });
      await cache.invalidateQueries({ queryKey: ["progress"] });
      setWeight("");
      setSuccess(true);
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  };
  const ordered = [...(weights.data || [])].sort((a, b) =>
    a.recorded_on.localeCompare(b.recorded_on),
  );
  const chart = ordered.slice(-12);
  const min = Math.min(...chart.map((x) => x.weight_kg)),
    max = Math.max(...chart.map((x) => x.weight_kg));
  return (
    <Screen
      onRefresh={() => {
        void summary.refetch();
        void weights.refetch();
        void logs.refetch();
      }}
      refreshing={
        summary.isRefetching || weights.isRefetching || logs.isRefetching
      }
    >
      <Heading
        eyebrow="PROGRESO"
        title="Mira cuánto has avanzado"
        subtitle="La constancia también se ve en los pequeños registros."
      />
      {summary.error ? (
        <ErrorBox
          error={message(summary.error)}
          retry={() => void summary.refetch()}
        />
      ) : summary.isPending ? (
        <Loading />
      ) : (
        <View style={styles.grid}>
          <Card style={{ flex: 1 }}>
            <Text style={styles.stat}>
              {format(summary.data.workouts_completed)}
            </Text>
            <Text style={styles.caption}>Sesiones completadas</Text>
          </Card>
          <Card style={{ flex: 1 }}>
            <Text style={styles.stat}>
              {format(summary.data.latest_weight_kg, 1)}
            </Text>
            <Text style={styles.caption}>Último peso · kg</Text>
          </Card>
        </View>
      )}
      <Card>
        <Text style={styles.cardTitle}>Tu peso, con perspectiva</Text>
        {weights.error ? (
          <ErrorBox
            error={message(weights.error)}
            retry={() => void weights.refetch()}
          />
        ) : weights.isPending ? (
          <Loading />
        ) : chart.length ? (
          <>
            <View
              accessibilityLabel="Historial de peso, variación entre registros"
              style={{
                height: 135,
                flexDirection: "row",
                alignItems: "flex-end",
                gap: 6,
                paddingTop: 18,
              }}
            >
              {chart.map((w) => (
                <View
                  key={w.id}
                  style={{ flex: 1, alignItems: "center", gap: 7 }}
                >
                  <Text style={{ color: c.muted, fontSize: 9 }}>
                    {format(w.weight_kg, 1)}
                  </Text>
                  <View
                    style={{
                      height:
                        35 +
                        (max > min
                          ? ((w.weight_kg - min) / (max - min)) * 55
                          : 30),
                      width: "100%",
                      maxWidth: 36,
                      backgroundColor: c.mint,
                      borderRadius: 6,
                    }}
                  />
                  <Text style={{ color: c.muted, fontSize: 8 }}>
                    {w.recorded_on.slice(5)}
                  </Text>
                </View>
              ))}
            </View>
            <Text style={styles.caption}>
              Escala relativa entre registros; las barras no parten de cero. El
              peso es solo una parte de tu progreso.
            </Text>
            <Text style={styles.body}>
              Cambio desde el primer registro:{" "}
              {summary.data?.weight_change_kg == null
                ? "—"
                : `${summary.data.weight_change_kg > 0 ? "+" : ""}${format(summary.data.weight_change_kg, 1)} kg`}
            </Text>
          </>
        ) : (
          <Text style={styles.body}>
            Registra tu peso para empezar a ver su evolución.
          </Text>
        )}
      </Card>
      <Card>
        <Text style={styles.cardTitle}>Registrar el peso de hoy</Text>
        <Text style={styles.caption}>
          Si ya registraste hoy, este valor lo actualizará.
        </Text>
        <ErrorBox error={error} />
        {success && (
          <Notice>
            Peso registrado. Las metas nutricionales y el perfil no se cambian
            automáticamente.
          </Notice>
        )}
        <Field
          label="Peso de hoy (kg)"
          value={weight}
          onChangeText={setWeight}
          keyboardType="decimal-pad"
        />
        <Button
          title="Guardar peso"
          loading={busy}
          onPress={() => void save()}
        />
      </Card>
      <Section title="Historial de entrenamientos" />
      {logs.isPending ? (
        <Loading />
      ) : logs.error ? (
        <ErrorBox
          error={message(logs.error)}
          retry={() => void logs.refetch()}
        />
      ) : logs.data.length ? (
        <Card>
          {logs.data.map((log) => (
            <Row
              key={log.id}
              title={log.workout_name}
              subtitle={`${displayDate(log.performed_on)} · ${log.status === "completed" ? "Completada" : log.status === "partial" ? "Parcial" : "Omitida"}`}
              onPress={() => nav.navigate("LogDetail", { logId: log.id })}
            />
          ))}
        </Card>
      ) : (
        <Empty
          title="Cada sesión deja una huella"
          description="Tus entrenamientos registrados aparecerán aquí."
        />
      )}
    </Screen>
  );
}
