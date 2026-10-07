export const today = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};
export const dayLabels = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];
export const goalLabels: Record<string, string> = {
  general_fitness: "Bienestar general",
  muscle_gain: "Ganar músculo",
  fat_loss: "Perder grasa",
  strength: "Ganar fuerza",
  endurance: "Resistencia",
};
export const disciplineLabels: Record<string, string> = {
  strength: "Fuerza",
  running: "Running",
  mobility: "Movilidad",
  hybrid: "Híbrido",
};
export const mealLabels: Record<string, string> = {
  breakfast: "Desayuno",
  lunch: "Almuerzo",
  dinner: "Cena",
  snack: "Snack",
};
export const displayDate = (s: string) =>
  new Date(s + "T12:00:00").toLocaleDateString("es-PA", {
    day: "numeric",
    month: "short",
  });
export const format = (n: number | null | undefined, digits = 0) =>
  n == null
    ? "—"
    : n.toLocaleString("es-PA", { maximumFractionDigits: digits });
export const numeric = (
  s: string,
  label: string,
  min: number,
  max: number,
  integer = false,
) => {
  const value = Number(s.replace(",", "."));
  if (
    !s.trim() ||
    !Number.isFinite(value) ||
    value < min ||
    value > max ||
    (integer && !Number.isInteger(value))
  )
    throw new Error(
      `${label}: ingresa ${integer ? "un número entero" : "un valor"} entre ${min} y ${max}.`,
    );
  return value;
};
export const optionalNumber = (
  s: string,
  label: string,
  min: number,
  max: number,
  integer = false,
) => (s.trim() ? numeric(s, label, min, max, integer) : undefined);
export const validDate = (s: string, birth = false) => {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(s))
    throw new Error("Usa una fecha con formato AAAA-MM-DD.");
  const d = new Date(s + "T12:00:00");
  if (
    Number.isNaN(d.getTime()) ||
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}` !==
      s
  )
    throw new Error("La fecha no es válida.");
  if (s > today() || (birth && s === today()))
    throw new Error("La fecha debe estar en el pasado.");
  return s;
};
export const message = (error: unknown) =>
  error instanceof Error
    ? error.message
    : "Ocurrió un error. Inténtalo de nuevo.";
