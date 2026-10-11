import { useState } from "react";
import { View } from "react-native";
import { Button, Field, Notice, ErrorBox } from "./ui";
import { request } from "../lib/api";
import { message } from "../lib/utils";

export function Recovery() {
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [sent, setSent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  async function run(reset: boolean) {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      if (reset) {
        if (password.length < 8 || password.length > 128)
          throw new Error("La contraseña debe tener entre 8 y 128 caracteres.");
        if (password !== confirm)
          throw new Error("Las contraseñas no coinciden.");
        if (token.trim().length < 32)
          throw new Error("Pega el código completo que recibiste por correo.");
        await request("/auth/reset-password", {
          method: "POST",
          body: { token: token.trim(), password },
        });
        setToken("");
        setPassword("");
        setConfirm("");
        setSent(false);
        setNotice(
          "Contraseña actualizada. Inicia sesión con tu nueva contraseña; se cerraron las sesiones anteriores.",
        );
      } else {
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim()))
          throw new Error("Ingresa un correo válido.");
        await request("/auth/forgot-password", {
          method: "POST",
          body: { email: email.trim().toLowerCase() },
        });
        setSent(true);
        setNotice(
          "Si existe una cuenta con ese correo, recibirás instrucciones. Revisa también spam. El código vence en 15 minutos.",
        );
      }
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  }
  if (!open)
    return (
      <Button
        title="Olvidé mi contraseña"
        secondary
        onPress={() => setOpen(true)}
      />
    );
  return (
    <View>
      <Notice>
        Recupera el acceso con el código que recibirás por correo.
      </Notice>
      <ErrorBox error={error} />
      {notice && <Notice>{notice}</Notice>}
      {!sent ? (
        <>
          <Field
            label="Correo de recuperación"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
            maxLength={255}
          />
          <Button
            title="Solicitar código"
            loading={busy}
            onPress={() => void run(false)}
          />
          <Button
            title="Ya tengo un código"
            secondary
            disabled={busy}
            onPress={() => {
              setSent(true);
              setError(null);
              setNotice(null);
            }}
          />
        </>
      ) : (
        <>
          <Field
            label="Código de recuperación"
            value={token}
            onChangeText={setToken}
            autoCapitalize="none"
            autoCorrect={false}
            maxLength={128}
          />
          <Field
            label="Nueva contraseña"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
            autoCapitalize="none"
            autoComplete="new-password"
            maxLength={128}
          />
          <Field
            label="Repite la nueva contraseña"
            value={confirm}
            onChangeText={setConfirm}
            secureTextEntry
            autoCapitalize="none"
            maxLength={128}
          />
          <Button
            title="Actualizar contraseña"
            loading={busy}
            onPress={() => void run(true)}
          />
          <Button
            title="Solicitar otro código"
            secondary
            disabled={busy}
            onPress={() => {
              setSent(false);
              setToken("");
              setError(null);
              setNotice(null);
            }}
          />
        </>
      )}
      <Button
        title="Volver al acceso"
        secondary
        disabled={busy}
        onPress={() => {
          setOpen(false);
          setPassword("");
          setConfirm("");
          setToken("");
          setSent(false);
          setError(null);
          setNotice(null);
        }}
      />
    </View>
  );
}
