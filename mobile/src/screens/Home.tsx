import { Text, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import {
  Screen,
  Heading,
  Card,
  Button,
  ErrorBox,
  Loading,
  Section,
  Meter,
  styles,
} from "../components/ui";
import { useSession } from "../state/Session";
import { request, allPages } from "../lib/api";
import { today, format, goalLabels, message } from "../lib/utils";
import type { RootStackParams, Plan, DaySummary, Progress } from "../types";
import { colors as c } from "../theme";
export function HomeScreen() {
  const { user, profile } = useSession();
  const nav = useNavigation<NativeStackNavigationProp<RootStackParams>>();
  const date = today();
  const plans = useQuery({
    queryKey: ["plans"],
    queryFn: ({ signal }) => allPages<Plan>("/training-plans", signal),
  });
  const nutrition = useQuery({
    queryKey: ["nutrition", date],
    queryFn: ({ signal }) =>
      request<DaySummary>("/nutrition/summary?recorded_on=" + date, { signal }),
  });
  const progress = useQuery({
    queryKey: ["progress"],
    queryFn: ({ signal }) => request<Progress>("/progress/summary", { signal }),
  });
  const own = plans.data
    ?.filter((p) => p.owner_id === user?.id)
    .sort((a, b) => b.id - a.id)[0];
  const plan = own || plans.data?.[0];
  const sum = nutrition.data;
  const refresh = () => {
    void plans.refetch();
    void nutrition.refetch();
    void progress.refetch();
  };
  return (
    <Screen
      refreshing={
        plans.isRefetching || nutrition.isRefetching || progress.isRefetching
      }
      onRefresh={refresh}
    >
      <Heading
        eyebrow="TU ESPACIO PARA CRECER"
        title={`Hola, ${user?.name.split(" ")[0] || "atleta"} ✦`}
        subtitle={
          goalLabels[profile?.goal || ""] ||
          "Un buen día para dar el siguiente paso."
        }
      />
      <LinearGradient
        colors={["#C6F477", "#89CC91"]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={{ padding: 24, borderRadius: 24, gap: 14, overflow: "hidden" }}
      >
        <Ionicons
          name="fitness-outline"
          size={110}
          color="#6EAF74"
          style={{ position: "absolute", right: -12, top: 8, opacity: 0.35 }}
        />
        <Text
          style={{
            color: c.accentDark,
            fontSize: 11,
            fontWeight: "800",
            letterSpacing: 1.5,
          }}
        >
          CADA SESIÓN CUENTA
        </Text>
        <Text
          style={{
            color: c.accentDark,
            fontSize: 27,
            fontWeight: "800",
            maxWidth: 240,
            lineHeight: 32,
          }}
        >
          {"Pequeños pasos.\nMás constancia."}
        </Text>
        <Text style={{ color: "#294B27", fontSize: 14, maxWidth: 260 }}>
          Tu plan es una guía. Tú marcas el ritmo.
        </Text>
        <Text
          style={{
            color: c.accentDark,
            fontSize: 12,
            fontWeight: "800",
            marginTop: 8,
          }}
        >
          ENTRENA · NUTRE · EVOLUCIONA
        </Text>
      </LinearGradient>
      <Section title="Tu plan" />
      {plans.isPending ? (
        <Loading />
      ) : plans.error ? (
        <ErrorBox
          error={message(plans.error)}
          retry={() => void plans.refetch()}
        />
      ) : plan ? (
        <Card>
          <Text style={styles.eyebrow}>
            {own ? "TU PLAN MÁS RECIENTE" : "PLANTILLA KENFIT"}
          </Text>
          <Text style={styles.cardTitle}>{plan.name}</Text>
          <Text style={styles.body}>
            {plan.weeks} semanas · {profile?.days_per_week} días disponibles por
            semana
          </Text>
          <Button
            title="Ver mi plan"
            icon="arrow-forward"
            onPress={() => nav.navigate("Plan", { planId: plan.id })}
          />
        </Card>
      ) : (
        <Card>
          <Text style={styles.cardTitle}>Tu primer plan te espera</Text>
          <Text style={styles.body}>
            Ve a Entrenamiento para crear una plantilla inicial según tu perfil.
          </Text>
        </Card>
      )}
      <Section
        title="Nutrición de hoy"
        action="Ver metas"
        onAction={() => nav.navigate("Targets")}
      />
      {nutrition.error ? (
        <ErrorBox
          error={message(nutrition.error)}
          retry={() => void nutrition.refetch()}
        />
      ) : nutrition.isPending ? (
        <Loading />
      ) : (
        <Card>
          <View
            style={{ flexDirection: "row", alignItems: "baseline", gap: 8 }}
          >
            <Text style={styles.stat}>{format(sum?.consumed.calories)}</Text>
            <Text style={styles.body}>
              / {sum?.target ? format(sum.target.calories) : "sin meta"} kcal
            </Text>
          </View>
          <Meter
            value={sum?.consumed.calories || 0}
            target={sum?.target?.calories || null}
          />
          <View
            style={{ flexDirection: "row", justifyContent: "space-between" }}
          >
            {[
              ["Proteína", sum?.consumed.protein_g],
              ["Carbos", sum?.consumed.carbs_g],
              ["Grasas", sum?.consumed.fat_g],
            ].map(([label, value]) => (
              <View key={String(label)}>
                <Text style={styles.caption}>{label}</Text>
                <Text
                  style={{
                    color: c.text,
                    fontSize: 17,
                    fontWeight: "700",
                    marginTop: 6,
                  }}
                >
                  {format(value as number, 1)} g
                </Text>
              </View>
            ))}
          </View>
          <Button
            title="Registrar comida"
            secondary
            icon="add"
            onPress={() => nav.navigate("AddMeal", { date })}
          />
        </Card>
      )}
      <Section title="Lo que vas construyendo" />
      {progress.error ? (
        <ErrorBox
          error={message(progress.error)}
          retry={() => void progress.refetch()}
        />
      ) : (
        <View style={styles.grid}>
          <Card style={{ flex: 1 }}>
            <Ionicons
              name="checkmark-circle-outline"
              color={c.accent}
              size={23}
            />
            <Text style={styles.stat}>
              {format(progress.data?.workouts_completed)}
            </Text>
            <Text style={styles.caption}>Sesiones completadas</Text>
          </Card>
          <Card style={{ flex: 1 }}>
            <Ionicons name="trending-up-outline" color={c.mint} size={23} />
            <Text style={styles.stat}>
              {format(progress.data?.latest_weight_kg, 1)}
            </Text>
            <Text style={styles.caption}>Último peso · kg</Text>
          </Card>
        </View>
      )}
    </Screen>
  );
}
