import { useState } from "react";
import { Modal, Text, View, Pressable } from "react-native";
import { Ionicons } from "@expo/vector-icons";
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
  Meter,
  Empty,
  Row,
  styles,
} from "../components/ui";
import { request } from "../lib/api";
import {
  today,
  displayDate,
  validDate,
  format,
  mealLabels,
  message,
} from "../lib/utils";
import { colors as c } from "../theme";
import type { RootStackParams, DaySummary, Meal } from "../types";
export function NutritionScreen() {
  const nav = useNavigation<NativeStackNavigationProp<RootStackParams>>(),
    cache = useQueryClient();
  const [date, setDate] = useState(today()),
    [dateInput, setDateInput] = useState(today()),
    [error, setError] = useState<string | null>(null),
    [selected, setSelected] = useState<Meal | null>(null),
    [busy, setBusy] = useState(false);
  const summary = useQuery({
    queryKey: ["nutrition", date],
    queryFn: ({ signal }) =>
      request<DaySummary>("/nutrition/summary?recorded_on=" + date, { signal }),
  });
  const sum = summary.data;
  const changeDate = () => {
    setError(null);
    try {
      setDate(validDate(dateInput));
    } catch (e) {
      setError(message(e));
    }
  };
  const remove = async () => {
    if (!selected) return;
    setBusy(true);
    setError(null);
    try {
      await request(`/nutrition/meals/${selected.id}`, { method: "DELETE" });
      setSelected(null);
      await cache.invalidateQueries({ queryKey: ["nutrition"] });
    } catch (e) {
      setError(message(e));
      setSelected(null);
    } finally {
      setBusy(false);
    }
  };
  return (
    <Screen
      onRefresh={() => void summary.refetch()}
      refreshing={summary.isRefetching}
    >
      <Heading
        eyebrow="NUTRICIÓN"
        title="Dale energía a tu día"
        subtitle="Conoce lo que comes, sin perder de vista el equilibrio."
      />
      <View style={{ flexDirection: "row", gap: 10, alignItems: "center" }}>
        <View style={{ flex: 1 }}>
          <Field
            label="Fecha del registro"
            value={dateInput}
            onChangeText={setDateInput}
            placeholder="AAAA-MM-DD"
            maxLength={10}
          />
        </View>
        <Button title="Ver día" secondary onPress={changeDate} />
      </View>
      <ErrorBox error={error} />
      {summary.error && (
        <ErrorBox
          error={message(summary.error)}
          retry={() => void summary.refetch()}
        />
      )}
      {summary.isPending ? (
        <Loading />
      ) : (
        sum && (
          <>
            <Card>
              <Text style={styles.eyebrow}>
                {date === today() ? "HOY" : displayDate(date).toUpperCase()}
              </Text>
              <View
                style={{ flexDirection: "row", alignItems: "baseline", gap: 8 }}
              >
                <Text style={[styles.stat, { fontSize: 45 }]}>
                  {format(sum.consumed.calories)}
                </Text>
                <Text style={styles.body}>kcal registradas</Text>
              </View>
              <Meter
                value={sum.consumed.calories}
                target={sum.target?.calories ?? null}
              />
              <Text style={styles.caption}>
                {sum.target
                  ? `Meta: ${format(sum.target.calories)} kcal · ${sum.remaining!.calories < 0 ? "Exceso" : "Restantes"}: ${format(Math.abs(sum.remaining!.calories))} kcal`
                  : "Establece una meta para ver tu balance diario."}
              </Text>
              <Button
                title="Registrar comida"
                icon="add"
                onPress={() => nav.navigate("AddMeal", { date })}
              />
            </Card>
            <View style={styles.grid}>
              {[
                {
                  key: "protein_g" as const,
                  label: "Proteína",
                  color: c.accent,
                },
                { key: "carbs_g" as const, label: "Carbos", color: c.mint },
                { key: "fat_g" as const, label: "Grasas", color: c.orange },
              ].map((item) => (
                <Card key={item.key} style={{ flex: 1, padding: 13, gap: 12 }}>
                  <Text style={styles.caption}>{item.label}</Text>
                  <Text
                    style={{ color: c.text, fontSize: 21, fontWeight: "800" }}
                  >
                    {format(sum.consumed[item.key], 1)}
                    <Text style={{ fontSize: 12 }}> g</Text>
                  </Text>
                  <Meter
                    value={sum.consumed[item.key]}
                    target={sum.target?.[item.key] ?? null}
                    color={item.color}
                  />
                  <Text style={styles.caption}>
                    {sum.target
                      ? `/ ${format(sum.target[item.key])} g`
                      : "Sin meta"}
                  </Text>
                </Card>
              ))}
            </View>
            <Button
              title="Configurar calorías y macros"
              secondary
              onPress={() => nav.navigate("Targets")}
            />
            <Section title="Tus comidas" />
            {sum.entries.length ? (
              Object.entries(mealLabels).map(([key, label]) => {
                const entries = sum.entries.filter((x) => x.meal === key);
                return !entries.length ? null : (
                  <Card key={key}>
                    <Text style={styles.cardTitle}>{label}</Text>
                    {entries.map((meal) => (
                      <Row
                        key={meal.id}
                        title={meal.food_name}
                        subtitle={`${format(meal.grams, 1)} g · ${format(meal.calories)} kcal`}
                        right={
                          <Pressable
                            accessibilityRole="button"
                            accessibilityLabel={`Eliminar ${meal.food_name}`}
                            onPress={() => setSelected(meal)}
                            style={{ padding: 12 }}
                          >
                            <Ionicons
                              name="trash-outline"
                              color={c.muted}
                              size={19}
                            />
                          </Pressable>
                        }
                      />
                    ))}
                  </Card>
                );
              })
            ) : (
              <Empty
                title="Un registro a la vez"
                description="Añade tu primera comida de este día para ver tu balance."
              />
            )}
          </>
        )
      )}
      <Modal
        transparent
        visible={!!selected}
        animationType="fade"
        onRequestClose={() => !busy && setSelected(null)}
      >
        <View
          style={{
            flex: 1,
            backgroundColor: "#000A",
            justifyContent: "center",
            padding: 24,
          }}
        >
          <Card>
            <Text style={styles.cardTitle}>¿Eliminar esta comida?</Text>
            <Text style={styles.body}>
              {selected?.food_name}. Se quitará del resumen del día.
            </Text>
            <Button
              title="Eliminar registro"
              loading={busy}
              onPress={() => void remove()}
            />
            <Button
              title="Conservar registro"
              secondary
              disabled={busy}
              onPress={() => setSelected(null)}
            />
          </Card>
        </View>
      </Modal>
    </Screen>
  );
}
