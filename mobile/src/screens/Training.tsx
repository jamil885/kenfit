import { useState } from "react";
import { Text } from "react-native";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import {
  Screen,
  Heading,
  Card,
  Button,
  ErrorBox,
  Loading,
  Section,
  Row,
  Empty,
  Notice,
  styles,
} from "../components/ui";
import { allPages, request } from "../lib/api";
import { useSession } from "../state/Session";
import { disciplineLabels, message } from "../lib/utils";
import type { RootStackParams, Plan, Workout, Split } from "../types";
export function TrainingScreen() {
  const nav = useNavigation<NativeStackNavigationProp<RootStackParams>>(),
    cache = useQueryClient();
  const { profile } = useSession();
  const plans = useQuery({
    queryKey: ["plans"],
    queryFn: ({ signal }) => allPages<Plan>("/training-plans", signal),
  });
  const workouts = useQuery({
    queryKey: ["workouts"],
    queryFn: ({ signal }) => allPages<Workout>("/workouts", signal),
  });
  const splits = useQuery({
    queryKey: ["splits"],
    queryFn: ({ signal }) => allPages<Split>("/splits", signal),
  });
  const [busy, setBusy] = useState(false),
    [error, setError] = useState<string | null>(null);
  const generate = async () => {
    setBusy(true);
    setError(null);
    try {
      const plan = await request<Plan>("/recommendations/training-plan", {
        method: "POST",
        body: { weeks: 4 },
      });
      await cache.invalidateQueries({ queryKey: ["plans"] });
      await cache.invalidateQueries({ queryKey: ["workouts"] });
      await cache.invalidateQueries({ queryKey: ["splits"] });
      nav.navigate("Plan", { planId: plan.id });
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  };
  return (
    <Screen
      onRefresh={() => {
        void plans.refetch();
        void workouts.refetch();
        void splits.refetch();
      }}
      refreshing={
        plans.isRefetching || workouts.isRefetching || splits.isRefetching
      }
    >
      <Heading
        eyebrow="ENTRENAMIENTO"
        title="Muévete con intención"
        subtitle="Tu estructura, tus sesiones y espacio para crear algo propio."
      />
      <Card>
        <Text style={styles.eyebrow}>TU PUNTO DE PARTIDA</Text>
        <Text style={styles.cardTitle}>Un plan para empezar</Text>
        <Text style={styles.body}>
          {disciplineLabels[profile?.preferred_discipline || ""] ||
            profile?.preferred_discipline}{" "}
          · {profile?.days_per_week} días por semana ·{" "}
          {profile?.session_minutes} minutos disponibles
        </Text>
        <Notice>
          Generaremos una plantilla de 4 semanas. Revísala antes de entrenar; no
          reemplaza una evaluación profesional.
        </Notice>
        <ErrorBox error={error} />
        <Button
          title="Generar mi plan inicial"
          loading={busy}
          onPress={() => void generate()}
        />
      </Card>
      <Section title="Planes de entrenamiento" />
      {plans.isPending ? (
        <Loading />
      ) : plans.error ? (
        <ErrorBox
          error={message(plans.error)}
          retry={() => void plans.refetch()}
        />
      ) : plans.data.length ? (
        <Card>
          {[...plans.data]
            .sort((a, b) => b.id - a.id)
            .map((p) => (
              <Row
                key={p.id}
                title={p.name}
                subtitle={`${p.weeks} semanas · ${p.source === "SYSTEM" ? "KenFit" : "Tu contenido"}`}
                onPress={() => nav.navigate("Plan", { planId: p.id })}
              />
            ))}
        </Card>
      ) : (
        <Empty
          title="Empieza con una estructura"
          description="Genera tu primer plan y úsalo como guía."
        />
      )}
      <Section
        title="Tus sesiones"
        action="Crear"
        onAction={() => nav.navigate("CreateWorkout")}
      />
      {workouts.isPending ? (
        <Loading />
      ) : workouts.error ? (
        <ErrorBox
          error={message(workouts.error)}
          retry={() => void workouts.refetch()}
        />
      ) : workouts.data.length ? (
        <Card>
          {workouts.data.map((w) => (
            <Row
              key={w.id}
              title={w.name}
              subtitle={`${disciplineLabels[w.discipline] || w.discipline} · ${w.exercises.length} ejercicios`}
              onPress={() => nav.navigate("Workout", { workoutId: w.id })}
            />
          ))}
        </Card>
      ) : (
        <Empty
          title="Sesiones a tu manera"
          description="Crea tu primera sesión con ejercicios del catálogo."
        />
      )}
      <Section title="Distribución de sesiones" />
      {splits.error ? (
        <ErrorBox
          error={message(splits.error)}
          retry={() => void splits.refetch()}
        />
      ) : (
        splits.data?.map((split) => (
          <Card key={split.id}>
            <Text style={styles.cardTitle}>{split.name}</Text>
            <Text style={styles.caption}>Ciclo de {split.cycle_days} días</Text>
            {split.days.map((day) => (
              <Row
                key={day.day}
                title={`Día ${day.day} · ${day.label || (day.workout_id ? "Entrenamiento" : "Descanso")}`}
                subtitle={
                  day.workout_id
                    ? workouts.data?.find((w) => w.id === day.workout_id)?.name
                    : undefined
                }
                onPress={
                  day.workout_id
                    ? () =>
                        nav.navigate("Workout", { workoutId: day.workout_id! })
                    : undefined
                }
              />
            ))}
          </Card>
        ))
      )}
    </Screen>
  );
}
