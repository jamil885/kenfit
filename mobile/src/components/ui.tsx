import React from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
  RefreshControl,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import type { TextInputProps, StyleProp, ViewStyle } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { colors as c } from "../theme";
import { useSession } from "../state/Session";
export function Screen({
  children,
  refreshing = false,
  onRefresh,
}: {
  children: React.ReactNode;
  refreshing?: boolean;
  onRefresh?: () => void;
}) {
  const { demo } = useSession();
  return (
    <SafeAreaView
      style={{ flex: 1, backgroundColor: c.bg }}
      edges={["left", "right"]}
    >
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <ScrollView
          contentContainerStyle={styles.page}
          keyboardShouldPersistTaps="handled"
          refreshControl={
            onRefresh ? (
              <RefreshControl
                refreshing={refreshing}
                onRefresh={onRefresh}
                tintColor={c.accent}
              />
            ) : undefined
          }
        >
          {demo && (
            <View style={styles.demo}>
              <Ionicons name="flask-outline" size={14} color={c.accent} />
              <Text style={styles.demoText}>
                DEMOSTRACIÓN · datos de ejemplo
              </Text>
            </View>
          )}
          {children}
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
export function Heading({
  eyebrow,
  title,
  subtitle,
}: {
  eyebrow?: string;
  title: string;
  subtitle?: string;
}) {
  return (
    <View style={{ gap: 8, marginBottom: 24 }}>
      {eyebrow && <Text style={styles.eyebrow}>{eyebrow}</Text>}
      <Text style={styles.title}>{title}</Text>
      {subtitle && <Text style={styles.body}>{subtitle}</Text>}
    </View>
  );
}
export function Card({
  children,
  style,
}: {
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
}) {
  return <View style={[styles.card, style]}>{children}</View>;
}
export function Button({
  title,
  onPress,
  loading = false,
  disabled = false,
  secondary = false,
  icon,
}: {
  title: string;
  onPress: () => void;
  loading?: boolean;
  disabled?: boolean;
  secondary?: boolean;
  icon?: React.ComponentProps<typeof Ionicons>["name"];
}) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={title}
      disabled={loading || disabled}
      onPress={onPress}
      style={({ pressed }) => [
        styles.button,
        secondary && styles.secondary,
        (loading || disabled) && { opacity: 0.45 },
        pressed && { opacity: 0.75 },
      ]}
    >
      {loading ? (
        <ActivityIndicator color={secondary ? c.accent : c.accentDark} />
      ) : (
        <>
          {icon && (
            <Ionicons
              name={icon}
              size={18}
              color={secondary ? c.text : c.accentDark}
            />
          )}
          <Text style={[styles.buttonText, secondary && { color: c.text }]}>
            {title}
          </Text>
        </>
      )}
    </Pressable>
  );
}
export function Field({ label, ...props }: TextInputProps & { label: string }) {
  return (
    <View style={{ gap: 8, marginBottom: 16 }}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        accessibilityLabel={label}
        placeholderTextColor={c.muted}
        selectionColor={c.accent}
        {...props}
        style={[
          styles.input,
          props.multiline && { minHeight: 90, textAlignVertical: "top" },
          props.style,
        ]}
      />
    </View>
  );
}
export function Chips<T extends string>({
  label,
  values,
  value,
  onChange,
}: {
  label: string;
  values: { value: T; label: string }[];
  value: T;
  onChange: (v: T) => void;
}) {
  return (
    <View style={{ gap: 10, marginBottom: 18 }}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.wrap}>
        {values.map((item) => (
          <Pressable
            key={item.value}
            accessibilityRole="button"
            accessibilityState={{ selected: value === item.value }}
            onPress={() => onChange(item.value)}
            style={[styles.chip, value === item.value && styles.selectedChip]}
          >
            <Text
              style={{
                color: value === item.value ? c.accent : c.muted,
                fontWeight: "600",
              }}
            >
              {item.label}
            </Text>
          </Pressable>
        ))}
      </View>
    </View>
  );
}
export function ErrorBox({
  error,
  retry,
}: {
  error: string | null | undefined;
  retry?: () => void;
}) {
  if (!error) return null;
  return (
    <View accessibilityRole="alert" style={styles.error}>
      <Text style={{ color: c.danger, lineHeight: 21 }}>{error}</Text>
      {retry && (
        <Pressable accessibilityRole="button" onPress={retry}>
          <Text style={{ color: c.accent, fontWeight: "700", marginTop: 12 }}>
            Reintentar
          </Text>
        </Pressable>
      )}
    </View>
  );
}
export function Notice({ children }: { children: React.ReactNode }) {
  return (
    <View style={styles.notice}>
      <Text style={[styles.body, { fontSize: 13 }]}>{children}</Text>
    </View>
  );
}
export function Loading() {
  return (
    <View style={{ padding: 40 }}>
      <ActivityIndicator color={c.accent} />
      <Text style={[styles.body, { textAlign: "center", marginTop: 10 }]}>
        Cargando tus datos…
      </Text>
    </View>
  );
}
export function Empty({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <Card>
      <Ionicons name="leaf-outline" color={c.accent} size={26} />
      <Text style={styles.cardTitle}>{title}</Text>
      <Text style={styles.body}>{description}</Text>
      {action}
    </Card>
  );
}
export function Section({
  title,
  action,
  onAction,
}: {
  title: string;
  action?: string;
  onAction?: () => void;
}) {
  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {action && (
        <Pressable accessibilityRole="button" onPress={onAction}>
          <Text style={{ color: c.accent, fontWeight: "600" }}>{action}</Text>
        </Pressable>
      )}
    </View>
  );
}
export function Row({
  title,
  subtitle,
  right,
  onPress,
}: {
  title: string;
  subtitle?: string;
  right?: React.ReactNode;
  onPress?: () => void;
}) {
  return (
    <Pressable
      accessibilityRole={onPress ? "button" : undefined}
      onPress={onPress}
      style={styles.row}
    >
      <View style={{ flex: 1, gap: 5 }}>
        <Text style={styles.rowTitle}>{title}</Text>
        {subtitle && <Text style={styles.caption}>{subtitle}</Text>}
      </View>
      {right ??
        (onPress ? (
          <Ionicons name="chevron-forward" size={19} color={c.muted} />
        ) : null)}
    </Pressable>
  );
}
export function Meter({
  value,
  target,
  color = c.accent,
}: {
  value: number;
  target: number | null;
  color?: string;
}) {
  const ratio =
    target && target > 0 ? Math.min(1, Math.max(0, value / target)) : 0;
  return (
    <View style={styles.track}>
      <View
        style={{
          backgroundColor: color,
          height: 6,
          borderRadius: 4,
          width: `${ratio * 100}%`,
        }}
      />
    </View>
  );
}
export const styles = StyleSheet.create({
  page: {
    padding: 22,
    paddingTop: 24,
    paddingBottom: 40,
    gap: 16,
    width: "100%",
    maxWidth: 720,
    alignSelf: "center",
  },
  demo: {
    padding: 10,
    borderRadius: 10,
    backgroundColor: "#21321C",
    flexDirection: "row",
    gap: 8,
    alignItems: "center",
  },
  demoText: {
    fontSize: 11,
    color: c.accent,
    fontWeight: "700",
    letterSpacing: 0.5,
  },
  eyebrow: {
    color: c.accent,
    fontSize: 11,
    fontWeight: "800",
    letterSpacing: 2,
  },
  title: {
    color: c.text,
    fontSize: 34,
    lineHeight: 40,
    fontWeight: "800",
    letterSpacing: -1.2,
  },
  body: { color: c.muted, fontSize: 15, lineHeight: 23 },
  caption: { color: c.muted, fontSize: 12, lineHeight: 18 },
  label: { color: c.text, fontSize: 13, fontWeight: "600" },
  card: {
    backgroundColor: c.surface,
    borderColor: c.border,
    borderWidth: 1,
    borderRadius: 22,
    padding: 20,
    gap: 14,
  },
  cardTitle: {
    color: c.text,
    fontSize: 20,
    fontWeight: "700",
    letterSpacing: -0.4,
  },
  button: {
    minHeight: 52,
    backgroundColor: c.accent,
    borderRadius: 14,
    paddingHorizontal: 18,
    paddingVertical: 14,
    alignItems: "center",
    justifyContent: "center",
    flexDirection: "row",
    gap: 10,
  },
  secondary: {
    backgroundColor: c.raised,
    borderColor: c.border,
    borderWidth: 1,
  },
  buttonText: { color: c.accentDark, fontSize: 14, fontWeight: "800" },
  input: {
    backgroundColor: c.surface,
    borderWidth: 1,
    borderColor: c.border,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 14,
    color: c.text,
    fontSize: 16,
    minHeight: 50,
  },
  wrap: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 12,
    borderWidth: 1,
    borderColor: c.border,
    borderRadius: 12,
    backgroundColor: c.surface,
  },
  selectedChip: { borderColor: c.accent, backgroundColor: "#25351D" },
  error: {
    backgroundColor: "#36201F",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  notice: {
    padding: 14,
    borderWidth: 1,
    borderColor: c.border,
    borderRadius: 12,
  },
  section: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginTop: 8,
    marginBottom: 2,
  },
  sectionTitle: { color: c.text, fontSize: 18, fontWeight: "700" },
  row: {
    paddingVertical: 14,
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    borderBottomWidth: 1,
    borderBottomColor: c.border,
  },
  rowTitle: { color: c.text, fontSize: 15, fontWeight: "600" },
  track: {
    height: 6,
    borderRadius: 4,
    backgroundColor: c.border,
    overflow: "hidden",
  },
  stat: { color: c.text, fontSize: 30, fontWeight: "800", letterSpacing: -1 },
  grid: { flexDirection: "row", gap: 12 },
});
