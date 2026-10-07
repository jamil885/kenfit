import { demoRequest, resetDemo } from "./demo";
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}
const configured = process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, "");
export const apiUrl = configured || "http://127.0.0.1:8000";
let token: string | null = null;
let demo = false;
let unauthorized: (() => void) | null = null;
export function configureApi(
  nextToken: string | null,
  nextDemo: boolean,
  onExpired?: () => void,
) {
  token = nextToken;
  demo = nextDemo;
  unauthorized = onExpired || null;
}
export const resetDemoData = resetDemo;
export function errorDetail(value: unknown): string {
  if (typeof value === "string") {
    const translations: Record<string, string> = {
      "Invalid email or password": "Correo o contraseña incorrectos.",
      "Email already registered": "Ese correo ya está registrado.",
      "Create a fitness profile first": "Completa tu perfil primero.",
      "Content not found": "El contenido ya no está disponible.",
      "Food not found": "El alimento ya no está disponible.",
    };
    return translations[value] || value;
  }
  if (Array.isArray(value))
    return value
      .map(
        (item) =>
          `${item.loc?.slice(1).join(" · ") || "Campo"}: ${item.msg || "valor inválido"}`,
      )
      .join("\n");
  return "No se pudo completar la operación.";
}
export async function request<T>(
  path: string,
  options: { method?: string; body?: unknown; signal?: AbortSignal } = {},
): Promise<T> {
  if (demo)
    return demoRequest(
      path,
      options.method || "GET",
      options.body,
    ) as Promise<T>;
  const controller = new AbortController();
  const abort = () => controller.abort();
  if (options.signal?.aborted) abort();
  options.signal?.addEventListener("abort", abort);
  const timeout = setTimeout(abort, 15000);
  const sentToken = token;
  try {
    const response = await fetch(apiUrl + path, {
      method: options.method || "GET",
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(sentToken ? { Authorization: "Bearer " + sentToken } : {}),
      },
      ...(options.body === undefined
        ? {}
        : { body: JSON.stringify(options.body) }),
    });
    const body =
      response.status === 204
        ? undefined
        : await response.json().catch(() => undefined);
    if (!response.ok) {
      if (response.status === 401 && sentToken && token === sentToken)
        unauthorized?.();
      throw new ApiError(
        response.status === 401 && sentToken
          ? "Tu sesión venció. Vuelve a iniciar sesión."
          : errorDetail(body?.detail),
        response.status,
      );
    }
    return body as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (controller.signal.aborted)
      throw new ApiError(
        "La conexión tardó demasiado o fue cancelada. Inténtalo de nuevo.",
        0,
      );
    throw new ApiError(
      "No se pudo conectar con KenFit. Revisa tu conexión y la dirección del servidor.",
      0,
    );
  } finally {
    clearTimeout(timeout);
    options.signal?.removeEventListener("abort", abort);
  }
}
export async function allPages<T>(
  path: string,
  signal?: AbortSignal,
): Promise<T[]> {
  const values: T[] = [];
  for (let offset = 0; ; offset += 100) {
    const page = await request<T[]>(
      `${path}${path.includes("?") ? "&" : "?"}limit=100&offset=${offset}`,
      { signal },
    );
    values.push(...page);
    if (page.length < 100) return values;
  }
}
