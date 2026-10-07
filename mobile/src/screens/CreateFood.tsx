import { useState } from "react";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import { useQueryClient } from "@tanstack/react-query";
import {
  Screen,
  Heading,
  Field,
  Button,
  ErrorBox,
  Notice,
} from "../components/ui";
import { request } from "../lib/api";
import { numeric, optionalNumber, message } from "../lib/utils";
import type { RootStackParams } from "../types";
export function CreateFoodScreen({
  navigation,
}: NativeStackScreenProps<RootStackParams, "CreateFood">) {
  const cache = useQueryClient();
  const [name, setName] = useState(""),
    [calories, setCalories] = useState(""),
    [protein, setProtein] = useState(""),
    [carbs, setCarbs] = useState(""),
    [fat, setFat] = useState(""),
    [serving, setServing] = useState(""),
    [reference, setReference] = useState("");
  const [busy, setBusy] = useState(false),
    [error, setError] = useState<string | null>(null);
  const save = async () => {
    setBusy(true);
    setError(null);
    try {
      if (name.trim().length < 2)
        throw new Error("Ingresa un nombre para el alimento.");
      await request("/nutrition/foods", {
        method: "POST",
        body: {
          name: name.trim(),
          calories: numeric(calories, "Calorías", 0, 10000),
          protein_g: numeric(protein, "Proteína", 0, 1000),
          carbs_g: numeric(carbs, "Carbohidratos", 0, 2000),
          fat_g: numeric(fat, "Grasas", 0, 1000),
          serving_grams: optionalNumber(serving, "Porción", 0.1, 10000) ?? null,
          reference: reference.trim() || null,
        },
      });
      await cache.invalidateQueries({ queryKey: ["foods"] });
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
        eyebrow="TU CATÁLOGO"
        title="Un alimento propio"
        subtitle="Usa los valores de su etiqueta o una fuente verificada."
      />
      <Notice>
        Todos los valores nutricionales deben corresponder a 100 gramos de
        alimento, aunque la etiqueta muestre otra porción.
      </Notice>
      <ErrorBox error={error} />
      <Field
        label="Nombre del alimento"
        value={name}
        onChangeText={setName}
        maxLength={100}
      />
      <Field
        label="Calorías por 100 g"
        value={calories}
        onChangeText={setCalories}
        keyboardType="decimal-pad"
      />
      <Field
        label="Proteína por 100 g"
        value={protein}
        onChangeText={setProtein}
        keyboardType="decimal-pad"
      />
      <Field
        label="Carbohidratos por 100 g"
        value={carbs}
        onChangeText={setCarbs}
        keyboardType="decimal-pad"
      />
      <Field
        label="Grasas por 100 g"
        value={fat}
        onChangeText={setFat}
        keyboardType="decimal-pad"
      />
      <Field
        label="Peso de una porción (g), opcional"
        value={serving}
        onChangeText={setServing}
        keyboardType="decimal-pad"
      />
      <Field
        label="Fuente o referencia, opcional"
        value={reference}
        onChangeText={setReference}
        maxLength={255}
      />
      <Button
        title="Guardar alimento"
        loading={busy}
        onPress={() => void save()}
      />
    </Screen>
  );
}
