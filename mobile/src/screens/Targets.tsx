import { useEffect, useState } from "react";
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
  Notice,
  styles,
} from "../components/ui";
import { request, ApiError } from "../lib/api";
import { format, numeric, message } from "../lib/utils";
import type { RootStackParams, Macros, Estimate } from "../types";
export function TargetsScreen({
  navigation,
}: NativeStackScreenProps<RootStackParams, "Targets">) {
  const cache = useQueryClient();
  const [calories, setCalories] = useState(""),
    [protein, setProtein] = useState(""),
    [carbs, setCarbs] = useState(""),
    [fat, setFat] = useState(""),
    [sex, setSex] = useState(""),
    [activity, setActivity] = useState("1.2"),
    [adjustment, setAdjustment] = useState("0");
  const [busy, setBusy] = useState(false),
    [error, setError] = useState<string | null>(null),
    [estimate, setEstimate] = useState<Estimate | null>(null);
  const target = useQuery({
    queryKey: ["targets"],
    queryFn: async ({ signal }) => {
      try {
        return await request<Macros>("/nutrition/targets", { signal });
      } catch (e) {
        if (e instanceof ApiError && e.status === 404) return null;
        throw e;
      }
    },
  });
  const fill = (values: Macros) => {
    setCalories(String(values.calories));
    setProtein(String(values.protein_g));
    setCarbs(String(values.carbs_g));
    setFat(String(values.fat_g));
  };
  useEffect(() => {
    if (target.data) fill(target.data);
  }, [target.data]);
  const calculate = async () => {
    setBusy(true);
    setError(null);
    try {
      if (!sex)
        throw new Error("Selecciona el coeficiente que utilizará la ecuación.");
      const result = await request<Estimate>("/nutrition/estimate", {
        method: "POST",
        body: {
          equation_sex: sex,
          activity_factor: Number(activity),
          calorie_adjustment: numeric(adjustment, "Ajuste", -500, 500, true),
        },
      });
      setEstimate(result);
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  };
  const save = async () => {
    setBusy(true);
    setError(null);
    try {
      const values = {
        calories: numeric(calories, "Calorías", 500, 10000),
        protein_g: numeric(protein, "Proteína", 0, 1000),
        carbs_g: numeric(carbs, "Carbohidratos", 0, 2000),
        fat_g: numeric(fat, "Grasas", 0, 1000),
      };
      const energy = 4 * (values.protein_g + values.carbs_g) + 9 * values.fat_g;
      if (Math.abs(energy - values.calories) > values.calories * 0.1)
        throw new Error(
          "Las calorías y macros deben coincidir con una tolerancia del 10%. Ajusta los valores.",
        );
      await request("/nutrition/targets", { method: "PUT", body: values });
      await cache.invalidateQueries({ queryKey: ["targets"] });
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
        eyebrow="TUS METAS NUTRICIONALES"
        title="Un punto de referencia"
        subtitle="Puedes ingresar tus metas o revisar una estimación inicial."
      />
      <ErrorBox error={error} />
      {target.error && (
        <ErrorBox
          error={message(target.error)}
          retry={() => void target.refetch()}
        />
      )}
      <Card>
        <Text style={styles.cardTitle}>Estimar calorías y macros</Text>
        <Notice>
          Estimación general para adultos. No es una prescripción médica y no se
          guarda automáticamente. Revisa tus metas con un profesional si tienes
          necesidades específicas.
        </Notice>
        <Chips
          label="Coeficiente de la ecuación"
          value={sex}
          onChange={setSex}
          values={[
            { value: "male", label: "Masculino" },
            { value: "female", label: "Femenino" },
          ]}
        />
        <Chips
          label="Actividad diaria aproximada"
          value={activity}
          onChange={setActivity}
          values={[
            { value: "1.2", label: "Baja" },
            { value: "1.375", label: "Ligera" },
            { value: "1.55", label: "Moderada" },
            { value: "1.725", label: "Alta" },
            { value: "1.9", label: "Muy alta" },
          ]}
        />
        <Field
          label="Ajuste de calorías (−500 a +500)"
          value={adjustment}
          onChangeText={setAdjustment}
          keyboardType="numbers-and-punctuation"
        />
        <Button
          title="Revisar estimación"
          loading={busy}
          secondary
          onPress={() => void calculate()}
        />
        {estimate && (
          <>
            <Text style={styles.stat}>{format(estimate.calories)} kcal</Text>
            <Text style={styles.body}>
              {format(estimate.protein_g, 1)} g proteína ·{" "}
              {format(estimate.carbs_g, 1)} g carbos ·{" "}
              {format(estimate.fat_g, 1)} g grasas
            </Text>
            <Button
              title="Usar estos valores en el formulario"
              secondary
              disabled={busy}
              onPress={() => fill(estimate)}
            />
          </>
        )}
      </Card>
      <Card>
        <Text style={styles.cardTitle}>Tu meta diaria</Text>
        <Field
          label="Calorías (kcal)"
          value={calories}
          onChangeText={setCalories}
          keyboardType="decimal-pad"
        />
        <Field
          label="Proteína (g)"
          value={protein}
          onChangeText={setProtein}
          keyboardType="decimal-pad"
        />
        <Field
          label="Carbohidratos (g)"
          value={carbs}
          onChangeText={setCarbs}
          keyboardType="decimal-pad"
        />
        <Field
          label="Grasas (g)"
          value={fat}
          onChangeText={setFat}
          keyboardType="decimal-pad"
        />
        <Button
          title="Guardar metas"
          loading={busy}
          disabled={target.isPending}
          onPress={() => void save()}
        />
      </Card>
    </Screen>
  );
}
