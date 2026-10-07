import React from "react";
import { Text } from "react-native";
import { NavigationContainer, DarkTheme } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";
import { Ionicons } from "@expo/vector-icons";
import { SessionProvider, useSession } from "./src/state/Session";
import { ApiError } from "./src/lib/api";
import { colors as c } from "./src/theme";
import { Button, Loading, ErrorBox, styles } from "./src/components/ui";
import type { RootStackParams, TabParams } from "./src/types";
import { AuthScreen } from "./src/screens/Auth";
import { ProfileScreen } from "./src/screens/Profile";
import { HomeScreen } from "./src/screens/Home";
import { TrainingScreen } from "./src/screens/Training";
import { NutritionScreen } from "./src/screens/Nutrition";
import { ProgressScreen } from "./src/screens/Progress";
import { WorkoutScreen } from "./src/screens/Workout";
import { PlanScreen } from "./src/screens/Plan";
import { AddMealScreen } from "./src/screens/AddMeal";
import { TargetsScreen } from "./src/screens/Targets";
import { CreateFoodScreen } from "./src/screens/CreateFood";
import { LogDetailScreen } from "./src/screens/LogDetail";
import { CreateWorkoutScreen } from "./src/screens/CreateWorkout";
import { CreateExerciseScreen } from "./src/screens/CreateExercise";
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000,
      retry: (count, error) =>
        !(
          error instanceof ApiError &&
          error.status >= 400 &&
          error.status < 500
        ) && count < 1,
    },
  },
});
const Stack = createNativeStackNavigator<RootStackParams>(),
  Tabs = createBottomTabNavigator<TabParams>();
const theme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    primary: c.accent,
    background: c.bg,
    card: c.bg,
    text: c.text,
    border: c.border,
    notification: c.accent,
  },
};
const icons: Record<
  keyof TabParams,
  React.ComponentProps<typeof Ionicons>["name"]
> = {
  Home: "grid-outline",
  Training: "barbell-outline",
  Nutrition: "restaurant-outline",
  Progress: "trending-up-outline",
  Profile: "person-outline",
};
function MainTabs() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: c.bg }} edges={["top"]}>
      <Tabs.Navigator
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarHideOnKeyboard: true,
          tabBarActiveTintColor: c.accent,
          tabBarInactiveTintColor: c.muted,
          tabBarStyle: { backgroundColor: c.bg, borderTopColor: c.border },
          tabBarLabelStyle: { fontSize: 10, fontWeight: "600" },
          tabBarIcon: ({ color, size }) => (
            <Ionicons name={icons[route.name]} size={size} color={color} />
          ),
        })}
      >
        <Tabs.Screen
          name="Home"
          component={HomeScreen}
          options={{ title: "Inicio" }}
        />
        <Tabs.Screen
          name="Training"
          component={TrainingScreen}
          options={{ title: "Entreno" }}
        />
        <Tabs.Screen
          name="Nutrition"
          component={NutritionScreen}
          options={{ title: "Nutrición" }}
        />
        <Tabs.Screen
          name="Progress"
          component={ProgressScreen}
          options={{ title: "Progreso" }}
        />
        <Tabs.Screen
          name="Profile"
          component={ProfileScreen}
          options={{ title: "Perfil" }}
        />
      </Tabs.Navigator>
    </SafeAreaView>
  );
}
function Navigation() {
  const session = useSession();
  if (session.booting)
    return (
      <SafeAreaView
        style={{ flex: 1, backgroundColor: c.bg, justifyContent: "center" }}
      >
        <Text style={[styles.title, { textAlign: "center" }]}>kenfit.</Text>
        <Loading />
      </SafeAreaView>
    );
  if (session.bootstrapError)
    return (
      <SafeAreaView
        style={{
          flex: 1,
          backgroundColor: c.bg,
          justifyContent: "center",
          padding: 24,
          gap: 16,
        }}
      >
        <Text style={styles.cardTitle}>Volvamos a conectar</Text>
        <ErrorBox error={session.bootstrapError} />
        <Button title="Reintentar conexión" onPress={session.retry} />
        <Button
          title="Volver al inicio de sesión"
          secondary
          onPress={() => void session.signOut()}
        />
      </SafeAreaView>
    );
  if (!session.user) return <AuthScreen />;
  if (!session.profile)
    return (
      <SafeAreaView
        style={{ flex: 1, backgroundColor: c.bg }}
        edges={["top", "bottom"]}
      >
        <ProfileScreen />
      </SafeAreaView>
    );
  return (
    <NavigationContainer theme={theme}>
      <Stack.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: c.bg },
          headerTintColor: c.text,
          headerShadowVisible: false,
          headerTitleStyle: { fontSize: 16 },
          contentStyle: { backgroundColor: c.bg },
        }}
      >
        <Stack.Screen
          name="Main"
          component={MainTabs}
          options={{ title: "KenFit", headerShown: false }}
        />
        <Stack.Screen
          name="Workout"
          component={WorkoutScreen}
          options={{ title: "Tu sesión" }}
        />
        <Stack.Screen
          name="Plan"
          component={PlanScreen}
          options={{ title: "Plan de entrenamiento" }}
        />
        <Stack.Screen
          name="AddMeal"
          component={AddMealScreen}
          options={{ title: "Registrar comida" }}
        />
        <Stack.Screen
          name="Targets"
          component={TargetsScreen}
          options={{ title: "Calorías y macros" }}
        />
        <Stack.Screen
          name="CreateFood"
          component={CreateFoodScreen}
          options={{ title: "Alimento propio" }}
        />
        <Stack.Screen
          name="LogDetail"
          component={LogDetailScreen}
          options={{ title: "Registro de sesión" }}
        />
        <Stack.Screen
          name="CreateWorkout"
          component={CreateWorkoutScreen}
          options={{ title: "Crear sesión" }}
        />
        <Stack.Screen
          name="CreateExercise"
          component={CreateExerciseScreen}
          options={{ title: "Crear ejercicio" }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
export default function App() {
  return (
    <SafeAreaProvider>
      <QueryClientProvider client={queryClient}>
        <SessionProvider>
          <StatusBar style="light" />
          <Navigation />
        </SessionProvider>
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}
