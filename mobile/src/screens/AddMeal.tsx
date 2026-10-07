import { useState } from "react";
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
  Notice,
  Row,
  Empty,
  styles,
} from "../components/ui";
import { request, allPages } from "../lib/api";
import { format, mealLabels, numeric, message } from "../lib/utils";
import type { RootStackParams, Food } from "../types";
export function AddMealScreen({
  route,
  navigation,
}: NativeStackScreenProps<RootStackParams, "AddMeal">) {
  const cache = useQueryClient();
  const [search, setSearch] = useState(""),
    [selected, setSelected] = useState<Food | null>(null),
    [meal, setMeal] = useState("lunch"),
    [unit, setUnit] = useState("grams"),
    [amount, setAmount] = useState("100"),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<string | null>(null);
  const foods = useQuery({
    queryKey: ["foods"],
    queryFn: ({ signal }) => allPages<Food>("/nutrition/foods", signal),
  });
  const filtered = foods.data?.filter((f) =>
    f.name.toLowerCase().includes(search.toLowerCase()),
  );
  const quantity = Number(amount.replace(",", "."));
  const grams =
    unit === "grams" ? quantity : quantity * (selected?.serving_grams || 0);
  const save = async () => {
    setBusy(true);
    setError(null);
    try {
      if (!selected) throw new Error("Selecciona un alimento.");
      const value = numeric(
        amount,
        "Cantidad",
        0.01,
        unit === "grams" ? 10000 : 100,
      );
      await request("/nutrition/meals", {
        method: "POST",
        body: {
          food_id: selected.id,
          recorded_on: route.params.date,
          meal,
          ...(unit === "grams" ? { grams: value } : { servings: value }),
        },
      });
      await cache.invalidateQueries({ queryKey: ["nutrition"] });
      navigation.goBack();
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  };
  return (
    <Screen>
      <Heading
        eyebrow="REGISTRO DE COMIDA"
        title={selected ? "La cantidad cuenta" : "¿Qué vas a registrar?"}
        subtitle={`Registro del ${route.params.date}`}
      />
      <ErrorBox error={error} />
      {!selected ? (
        <>
          <Field
            label="Buscar alimento"
            value={search}
            onChangeText={setSearch}
            placeholder="Arroz, pollo, banana…"
          />
          {foods.isPending ? (
            <Loading />
          ) : foods.error ? (
            <ErrorBox
              error={message(foods.error)}
              retry={() => void foods.refetch()}
            />
          ) : filtered?.length ? (
            <Card>
              {filtered.map((food) => (
                <Row
                  key={food.id}
                  title={food.name}
                  subtitle={`${format(food.calories)} kcal / 100 g`}
                  onPress={() => {
                    setSelected(food);
                    setUnit("grams");
                    setAmount("100");
                  }}
                />
              ))}
            </Card>
          ) : (
            <Empty
              title="No encontramos ese alimento"
              description="Puedes registrar uno propio usando la información de su etiqueta."
            />
          )}
          <Button
            title="Crear alimento propio"
            secondary
            icon="add"
            onPress={() => navigation.navigate("CreateFood")}
          />
        </>
      ) : (
        <>
          <Card>
            <Text style={styles.cardTitle}>{selected.name}</Text>
            <Text style={styles.body}>
              {format(selected.calories)} kcal · {format(selected.protein_g, 1)}{" "}
              g proteína por 100 g
            </Text>
            {selected.reference
              ?.toLowerCase()
              .match(/demo|demostr|approximate/) && (
              <Notice>
                Dato de demostración. Verifica la etiqueta del alimento antes de
                usarlo como referencia real.
              </Notice>
            )}
            <Button
              title="Cambiar alimento"
              secondary
              disabled={busy}
              onPress={() => setSelected(null)}
            />
          </Card>
          <Chips
            label="Comida del día"
            value={meal}
            onChange={setMeal}
            values={Object.entries(mealLabels).map(([value, label]) => ({
              value,
              label,
            }))}
          />
          <Chips
            label="Forma de medir"
            value={unit}
            onChange={(v) => {
              setUnit(v);
              setAmount(v === "grams" ? "100" : "1");
            }}
            values={[
              { value: "grams", label: "Gramos" },
              ...(selected.serving_grams
                ? [
                    {
                      value: "servings",
                      label: `Porción (${selected.serving_grams} g)`,
                    },
                  ]
                : []),
            ]}
          />
          <Field
            label={unit === "grams" ? "Cantidad (g)" : "Número de porciones"}
            value={amount}
            onChangeText={setAmount}
            keyboardType="decimal-pad"
          />
          {Number.isFinite(grams) && grams > 0 && (
            <Card>
              <Text style={styles.eyebrow}>ESTA CANTIDAD APORTA</Text>
              <Text style={styles.stat}>
                {format((selected.calories * grams) / 100)} kcal
              </Text>
              <Text style={styles.body}>
                {format(grams, 1)} g de alimento ·{" "}
                {format((selected.protein_g * grams) / 100, 1)} g proteína ·{" "}
                {format((selected.carbs_g * grams) / 100, 1)} g carbos ·{" "}
                {format((selected.fat_g * grams) / 100, 1)} g grasas
              </Text>
            </Card>
          )}
          <Button
            title="Guardar comida"
            loading={busy}
            onPress={() => void save()}
          />
        </>
      )}
    </Screen>
  );
}
