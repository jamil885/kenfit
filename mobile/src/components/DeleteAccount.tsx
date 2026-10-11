import { useState } from "react";
import { Modal } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Screen, Heading, Field, Button, ErrorBox, Notice } from "./ui";
import { useSession } from "../state/Session";
import { request } from "../lib/api";
import { message } from "../lib/utils";
import { colors } from "../theme";

export function DeleteAccount() {
  const { demo, signOut } = useSession();
  const [open, setOpen] = useState(false);
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  if (demo) return null;
  const close = () => {
    if (!busy) {
      setOpen(false);
      setPassword("");
      setConfirmation("");
      setError(null);
    }
  };
  async function remove() {
    setBusy(true);
    setError(null);
    try {
      if (confirmation !== "ELIMINAR")
        throw new Error("Escribe ELIMINAR para confirmar.");
      await request("/auth/me", { method: "DELETE", body: { password } });
      setPassword("");
      setOpen(false);
      await signOut();
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <Button
        title="Eliminar mi cuenta"
        secondary
        onPress={() => setOpen(true)}
      />
      <Modal visible={open} animationType="slide" onRequestClose={close}>
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
          <Screen>
            <Heading
              title="Eliminar cuenta"
              subtitle="Esta acción no se puede deshacer desde la aplicación."
            />
            <Notice>
              Se eliminarán tu perfil, registros de entrenamiento, comidas, peso
              y contenido privado. Se cerrará el acceso a tu cuenta. Los
              catálogos oficiales permanecen.
            </Notice>
            <Field
              label="Contraseña actual"
              value={password}
              onChangeText={setPassword}
              secureTextEntry
              autoCapitalize="none"
              autoComplete="current-password"
              maxLength={128}
            />
            <Field
              label="Escribe ELIMINAR"
              value={confirmation}
              onChangeText={setConfirmation}
              autoCorrect={false}
              maxLength={8}
            />
            <ErrorBox error={error} />
            <Button
              title="Eliminar definitivamente"
              loading={busy}
              disabled={confirmation !== "ELIMINAR" || password.length < 8}
              onPress={() => void remove()}
            />
            <Button
              title="Cancelar"
              secondary
              disabled={busy}
              onPress={close}
            />
          </Screen>
        </SafeAreaView>
      </Modal>
    </>
  );
}
