import { useState } from "react";
import { Text, View } from "react-native";
import {
  Screen,
  Heading,
  Field,
  Chips,
  Button,
  ErrorBox,
  Notice,
  styles,
} from "../components/ui";
import { colors as c } from "../theme";
import { useSession } from "../state/Session";
import {
  goalLabels,
  disciplineLabels,
  numeric,
  validDate,
  message,
} from "../lib/utils";
export function ProfileScreen() {
  const { user, profile, saveProfile, signOut } = useSession();
  const [step, setStep] = useState(profile ? 2 : 0),
    [birth, setBirth] = useState(profile?.birth_date || ""),
    [gender, setGender] = useState(profile?.gender || "");
  const [height, setHeight] = useState(
      profile ? String(profile.height_cm) : "",
    ),
    [weight, setWeight] = useState(profile ? String(profile.weight_kg) : "");
  const [level, setLevel] = useState(profile?.fitness_level || "beginner"),
    [goal, setGoal] = useState(profile?.goal || "general_fitness");
  const [days, setDays] = useState(String(profile?.days_per_week || 3)),
    [minutes, setMinutes] = useState(String(profile?.session_minutes || 45)),
    [discipline, setDiscipline] = useState(
      profile?.preferred_discipline || "strength",
    );
  const [equipment, setEquipment] = useState(
    profile?.available_equipment || ["bodyweight"],
  );
  const [busy, setBusy] = useState(false),
    [error, setError] = useState<string | null>(null),
    [success, setSuccess] = useState(false);
  const basic = () => {
    validDate(birth, true);
    if (!gender) throw new Error("Selecciona una opción de género.");
    numeric(height, "Estatura", 50, 250);
    numeric(weight, "Peso", 20, 500);
  };
  const next = () => {
    setError(null);
    try {
      if (step === 0) basic();
      setStep(step + 1);
    } catch (e) {
      setError(message(e));
    }
  };
  const save = async () => {
    setError(null);
    setSuccess(false);
    setBusy(true);
    try {
      basic();
      await saveProfile({
        birth_date: birth,
        gender,
        height_cm: numeric(height, "Estatura", 50, 250),
        weight_kg: numeric(weight, "Peso", 20, 500),
        fitness_level: level,
        goal,
        days_per_week: numeric(days, "Días", 1, 6, true),
        session_minutes: numeric(minutes, "Tiempo", 10, 180, true),
        available_equipment: equipment,
        preferred_discipline: discipline,
      });
      setSuccess(true);
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  };
  const stepTitles = [
    "Conozcamos tu punto de partida",
    "¿Qué quieres construir?",
    "Haz espacio en tu semana",
  ];
  return (
    <Screen>
      <Heading
        eyebrow={profile ? "TU PERFIL" : `PASO ${step + 1} DE 3`}
        title={profile ? "Hecho para ti" : stepTitles[step]!}
        subtitle={
          profile
            ? `${user?.name} · ${user?.email}`
            : "Estos datos nos ayudan a preparar tu experiencia."
        }
      />
      <View style={styles.grid}>
        {[0, 1, 2].map((i) => (
          <View
            key={i}
            style={{
              height: 4,
              flex: 1,
              backgroundColor: i <= step ? c.accent : c.border,
              borderRadius: 2,
            }}
          />
        ))}
      </View>
      <ErrorBox error={error} />
      {success && <Notice>Tu perfil fue actualizado.</Notice>}
      {step === 0 && (
        <View>
          <Field
            label="Fecha de nacimiento (AAAA-MM-DD)"
            value={birth}
            onChangeText={setBirth}
            placeholder="2000-01-01"
            maxLength={10}
          />
          <Chips
            label="Género"
            value={gender}
            onChange={setGender}
            values={[
              { value: "male", label: "Masculino" },
              { value: "female", label: "Femenino" },
              { value: "other", label: "Otro / prefiero no decir" },
            ]}
          />
          <Field
            label="Estatura (cm)"
            value={height}
            onChangeText={setHeight}
            keyboardType="decimal-pad"
          />
          <Field
            label="Peso actual (kg)"
            value={weight}
            onChangeText={setWeight}
            keyboardType="decimal-pad"
          />
        </View>
      )}
      {step === 1 && (
        <View>
          <Chips
            label="Tu objetivo"
            value={goal}
            onChange={setGoal}
            values={Object.entries(goalLabels).map(([value, label]) => ({
              value,
              label,
            }))}
          />
          <Chips
            label="Tu experiencia"
            value={level}
            onChange={setLevel}
            values={[
              { value: "beginner", label: "Estoy empezando" },
              { value: "intermediate", label: "Ya entreno" },
              { value: "advanced", label: "Avanzado" },
            ]}
          />
          <Notice>
            El generador ofrece un punto de partida con reglas básicas. Podrás
            registrar tus propias sesiones y ajustar el plan.
          </Notice>
        </View>
      )}
      {step === 2 && (
        <View>
          <Chips
            label="Disciplina principal"
            value={discipline}
            onChange={setDiscipline}
            values={Object.entries(disciplineLabels)
              .filter(([v]) => v !== "hybrid")
              .map(([value, label]) => ({ value, label }))}
          />
          <Chips
            label="Días por semana"
            value={days}
            onChange={setDays}
            values={["1", "2", "3", "4", "5", "6"].map((value) => ({
              value,
              label: value,
            }))}
          />
          <Field
            label="Minutos disponibles por sesión"
            value={minutes}
            onChangeText={setMinutes}
            keyboardType="number-pad"
          />
          <Text style={[styles.label, { marginBottom: 12 }]}>
            Equipo disponible (puedes elegir varios)
          </Text>
          <View style={[styles.wrap, { marginBottom: 18 }]}>
            {[
              { value: "bodyweight", label: "Peso corporal" },
              { value: "dumbbells", label: "Mancuernas" },
              { value: "barbell", label: "Barra" },
              { value: "bands", label: "Bandas" },
            ].map((item) => (
              <Button
                key={item.value}
                title={
                  (equipment.includes(item.value) ? "✓ " : "") + item.label
                }
                secondary={!equipment.includes(item.value)}
                onPress={() =>
                  setEquipment(
                    equipment.includes(item.value)
                      ? equipment.filter((x) => x !== item.value)
                      : [...equipment, item.value],
                  )
                }
              />
            ))}
          </View>
          {discipline === "strength" && Number(days) > 3 && (
            <Notice>
              La plantilla inicial Full Body admite hasta 3 días. Puedes
              conservar esta disponibilidad y crear sesiones propias para
              frecuencias mayores.
            </Notice>
          )}
        </View>
      )}
      {step < 2 ? (
        <Button title="Continuar" onPress={next} />
      ) : (
        <Button
          title={profile ? "Guardar cambios" : "Crear mi perfil"}
          loading={busy}
          onPress={() => void save()}
        />
      )}
      {step > 0 && (
        <Button
          title="Volver al paso anterior"
          secondary
          disabled={busy}
          onPress={() => {
            setStep(step - 1);
            setError(null);
          }}
        />
      )}
      <Button
        title="Cerrar sesión"
        secondary
        disabled={busy}
        onPress={() => void signOut()}
      />
    </Screen>
  );
}
