import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import {
  Screen,
  Heading,
  Field,
  Button,
  Chips,
  ErrorBox,
} from "../components/ui";
import { request } from "../lib/api";
import { disciplineLabels, message } from "../lib/utils";
import type { RootStackParams } from "../types";
export function CreateExerciseScreen({
  navigation,
}: NativeStackScreenProps<RootStackParams, "CreateExercise">) {
  const cache = useQueryClient();
  const [name, setName] = useState(""),
    [discipline, setDiscipline] = useState("strength"),
    [equipment, setEquipment] = useState("bodyweight"),
    [instructions, setInstructions] = useState(""),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<string | null>(null);
  const save = async () => {
    setBusy(true);
    setError(null);
    try {
      if (name.trim().length < 2)
        throw new Error("Ingresa el nombre del ejercicio.");
      await request("/exercises", {
        method: "POST",
        body: {
          name: name.trim(),
          discipline,
          exercise_type: "movement",
          equipment: equipment.trim() || null,
          instructions: instructions.trim() || null,
        },
      });
      await cache.invalidateQueries({ queryKey: ["exercises"] });
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
        title="Un ejercicio propio"
        subtitle="Tu ejercicio será privado y podrás reutilizarlo en tus sesiones."
      />
      <ErrorBox error={error} />
      <Field
        label="Nombre del ejercicio"
        value={name}
        onChangeText={setName}
        maxLength={100}
      />
      <Chips
        label="Disciplina"
        value={discipline}
        onChange={setDiscipline}
        values={Object.entries(disciplineLabels).map(([value, label]) => ({
          value,
          label,
        }))}
      />
      <Field
        label="Equipo (código o descripción)"
        value={equipment}
        onChangeText={setEquipment}
        maxLength={100}
      />
      <Field
        label="Indicaciones, opcional"
        value={instructions}
        onChangeText={setInstructions}
        multiline
        maxLength={4000}
      />
      <Button
        title="Guardar ejercicio"
        loading={busy}
        onPress={() => void save()}
      />
    </Screen>
  );
}
