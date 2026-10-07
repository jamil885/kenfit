import { useState } from "react";
import { Text } from "react-native";
import { useQuery } from "@tanstack/react-query";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import {
  Screen,
  Heading,
  Card,
  Chips,
  Row,
  Loading,
  ErrorBox,
  Notice,
  styles,
} from "../components/ui";
import { request, allPages } from "../lib/api";
import { dayLabels, goalLabels, message } from "../lib/utils";
import type { RootStackParams, Plan, Workout } from "../types";
export function PlanScreen({
  route,
  navigation,
}: NativeStackScreenProps<RootStackParams, "Plan">) {
  const plan = useQuery({
    queryKey: ["plan", route.params.planId],
    queryFn: ({ signal }) =>
      request<Plan>("/training-plans/" + route.params.planId, { signal }),
  });
  const workouts = useQuery({
    queryKey: ["workouts"],
    queryFn: ({ signal }) => allPages<Workout>("/workouts", signal),
  });
  const [week, setWeek] = useState("1");
  return (
    <Screen>
      <Heading
        eyebrow="TU ESTRUCTURA"
        title={plan.data?.name || "Plan de entrenamiento"}
        subtitle={
          plan.data
            ? `${plan.data.weeks} semanas · ${goalLabels[plan.data.goal] || plan.data.goal}`
            : undefined
        }
      />
      {plan.isPending ? (
        <Loading />
      ) : plan.error ? (
        <ErrorBox
          error={message(plan.error)}
          retry={() => void plan.refetch()}
        />
      ) : (
        <>
          <Chips
            label="Semana del plan"
            value={week}
            onChange={setWeek}
            values={Array.from({ length: plan.data.weeks }, (_, i) => ({
              value: String(i + 1),
              label: String(i + 1),
            }))}
          />
          <Notice>
            Los días organizan cada semana del plan. Aún no están vinculados a
            una fecha de inicio.
          </Notice>
          {workouts.error && (
            <ErrorBox
              error={message(workouts.error)}
              retry={() => void workouts.refetch()}
            />
          )}
          {Array.from({ length: 7 }, (_, i) => i + 1).map((day) => {
            const entry = plan.data.schedule.find(
              (x) => x.week === Number(week) && x.day === day,
            );
            const workout = workouts.data?.find(
              (w) => w.id === entry?.workout_id,
            );
            return (
              <Card key={day}>
                <Text style={styles.eyebrow}>
                  {dayLabels[day - 1]} · DÍA {day}
                </Text>
                {entry ? (
                  <Row
                    title={workout?.name || "Sesión del plan"}
                    subtitle={entry.phase ? `Fase: ${entry.phase}` : undefined}
                    onPress={() =>
                      navigation.navigate("Workout", {
                        workoutId: entry.workout_id,
                      })
                    }
                  />
                ) : (
                  <Text style={styles.body}>
                    Descanso · dale espacio a la recuperación.
                  </Text>
                )}
              </Card>
            );
          })}
        </>
      )}
    </Screen>
  );
}
