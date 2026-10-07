import { useState } from "react";
import { View, Text, Pressable } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import {
  Screen,
  Heading,
  Field,
  Button,
  ErrorBox,
  styles,
  Notice,
} from "../components/ui";
import { colors as c } from "../theme";
import { useSession } from "../state/Session";
import { message } from "../lib/utils";
export function AuthScreen() {
  const session = useSession();
  const [register, setRegister] = useState(false),
    [name, setName] = useState(""),
    [email, setEmail] = useState(""),
    [password, setPassword] = useState(""),
    [visible, setVisible] = useState(false);
  const [busy, setBusy] = useState(false),
    [error, setError] = useState<string | null>(null);
  const run = async (demo = false) => {
    setBusy(true);
    setError(null);
    try {
      if (demo) {
        await session.enterDemo();
        return;
      }
      if (register && name.trim().length < 2)
        throw new Error("Ingresa tu nombre (al menos 2 caracteres).");
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim()))
        throw new Error("Ingresa un correo válido.");
      if (password.length < 8 || password.length > 128)
        throw new Error("La contraseña debe tener entre 8 y 128 caracteres.");
      if (register) await session.register(name, email, password);
      else await session.signIn(email, password);
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  };
  return (
    <SafeAreaView
      style={{ flex: 1, backgroundColor: c.bg }}
      edges={["top", "bottom"]}
    >
      <Screen>
        <View
          style={{
            flexDirection: "row",
            alignItems: "center",
            gap: 10,
            marginBottom: 30,
          }}
        >
          <View
            style={{ backgroundColor: c.accent, padding: 10, borderRadius: 14 }}
          >
            <Ionicons name="leaf" size={24} color={c.accentDark} />
          </View>
          <Text
            style={{
              color: c.text,
              fontSize: 25,
              fontWeight: "800",
              letterSpacing: -1,
            }}
          >
            kenfit<Text style={{ color: c.accent }}>.</Text>
          </Text>
        </View>
        <Heading
          eyebrow="UN PASO A LA VEZ"
          title={"Tu progreso.\nA tu ritmo."}
          subtitle="Entrena con intención, conoce tu nutrición y construye hábitos que se queden contigo."
        />
        <View style={{ flexDirection: "row", gap: 10, marginBottom: 20 }}>
          {["Entrena", "Nutre", "Evoluciona"].map((text, i) => (
            <View
              key={text}
              style={{
                flex: 1,
                paddingVertical: 13,
                borderTopWidth: 2,
                borderColor: i === 0 ? c.accent : c.border,
              }}
            >
              <Text style={styles.caption}>{text}</Text>
            </View>
          ))}
        </View>
        <Text style={styles.cardTitle}>
          {register ? "Crea tu cuenta" : "Qué bueno verte"}
        </Text>
        {session.notice && <Notice>{session.notice}</Notice>}
        <ErrorBox error={error} />
        <View>
          {register && (
            <Field
              label="Nombre"
              value={name}
              onChangeText={setName}
              maxLength={100}
              autoComplete="name"
            />
          )}
          <Field
            label="Correo electrónico"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
            autoComplete="email"
            maxLength={255}
          />
          <Field
            label="Contraseña"
            value={password}
            onChangeText={setPassword}
            secureTextEntry={!visible}
            autoCapitalize="none"
            autoComplete={register ? "new-password" : "current-password"}
            maxLength={128}
          />
          <Pressable
            accessibilityRole="button"
            onPress={() => setVisible(!visible)}
          >
            <Text
              style={[styles.caption, { color: c.accent, marginBottom: 20 }]}
            >
              {visible ? "Ocultar contraseña" : "Mostrar contraseña"}
            </Text>
          </Pressable>
          <Button
            title={register ? "Crear cuenta" : "Iniciar sesión"}
            loading={busy}
            onPress={() => void run()}
          />
        </View>
        <Pressable
          accessibilityRole="button"
          disabled={busy}
          onPress={() => {
            setRegister(!register);
            setError(null);
          }}
          style={{ paddingVertical: 10 }}
        >
          <Text style={{ color: c.muted, textAlign: "center" }}>
            {register ? "¿Ya tienes cuenta? " : "¿Primera vez aquí? "}
            <Text style={{ color: c.accent, fontWeight: "700" }}>
              {register ? "Inicia sesión" : "Regístrate"}
            </Text>
          </Text>
        </Pressable>
        <Button
          title="Explorar demostración"
          secondary
          icon="flask-outline"
          disabled={busy}
          onPress={() => void run(true)}
        />
        <Text style={[styles.caption, { textAlign: "center" }]}>
          La demostración usa datos de ejemplo. No crea una cuenta ni envía
          información al servidor.
        </Text>
      </Screen>
    </SafeAreaView>
  );
}
