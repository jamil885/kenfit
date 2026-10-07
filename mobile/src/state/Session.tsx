import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  useCallback,
} from "react";
import { useQueryClient } from "@tanstack/react-query";
import type { User, Profile, ProfileInput } from "../types";
import { ApiError, request, configureApi, resetDemoData } from "../lib/api";
import { readToken, saveToken, removeToken } from "../lib/storage";
import { message } from "../lib/utils";
type Session = {
  user: User | null;
  profile: Profile | null;
  demo: boolean;
  booting: boolean;
  bootstrapError: string | null;
  notice: string | null;
  signIn: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  enterDemo: () => Promise<void>;
  signOut: () => Promise<void>;
  retry: () => void;
  saveProfile: (input: ProfileInput) => Promise<void>;
};
const Context = createContext<Session | null>(null);
export function SessionProvider({ children }: { children: React.ReactNode }) {
  const cache = useQueryClient();
  const [user, setUser] = useState<User | null>(null),
    [profile, setProfile] = useState<Profile | null>(null),
    [demo, setDemo] = useState(false);
  const [booting, setBooting] = useState(true),
    [bootstrapError, setBootstrapError] = useState<string | null>(null),
    [notice, setNotice] = useState<string | null>(null);
  const epoch = useRef(0);
  const signOut = useCallback(async () => {
    epoch.current++;
    void cache.cancelQueries();
    cache.clear();
    configureApi(null, false);
    setUser(null);
    setProfile(null);
    setDemo(false);
    setBootstrapError(null);
    setBooting(false);
    try {
      await removeToken();
    } catch {
      setNotice(
        "Se cerró la sesión, pero no se pudo limpiar el almacenamiento. Inténtalo de nuevo.",
      );
    }
  }, [cache]);
  const expired = useCallback(() => {
    void signOut();
    setNotice("Tu sesión venció. Vuelve a iniciar sesión.");
  }, [signOut]);
  const load = useCallback(
    async (token: string, demoMode: boolean) => {
      const version = ++epoch.current;
      configureApi(token, demoMode, expired);
      const current = await request<User>("/auth/me");
      let fitness: Profile | null = null;
      try {
        fitness = await request<Profile>("/fitness-profile");
      } catch (error) {
        if (!(error instanceof ApiError && error.status === 404)) throw error;
      }
      if (version !== epoch.current) return;
      setUser(current);
      setProfile(fitness);
      setDemo(demoMode);
      setNotice(null);
      cache.clear();
    },
    [cache, expired],
  );
  const restore = useCallback(async () => {
    setBooting(true);
    setBootstrapError(null);
    try {
      const token = await readToken();
      if (token) await load(token, false);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        await signOut();
      } else setBootstrapError(message(error));
    } finally {
      setBooting(false);
    }
  }, [load, signOut]);
  useEffect(() => {
    void restore();
    return () => {
      epoch.current++;
      configureApi(null, false);
    };
  }, [restore]);
  const signIn = async (email: string, password: string) => {
    configureApi(null, false);
    const response = await request<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: { email: email.trim().toLowerCase(), password },
    });
    await saveToken(response.access_token);
    try {
      await load(response.access_token, false);
    } catch (error) {
      configureApi(null, false);
      await removeToken();
      throw error;
    }
  };
  const register = async (name: string, email: string, password: string) => {
    await request<User>("/auth/register", {
      method: "POST",
      body: { name: name.trim(), email: email.trim().toLowerCase(), password },
    });
    // Account creation is committed even if a later login request fails.
    try {
      await signIn(email, password);
    } catch {
      throw new Error("Tu cuenta fue creada. Inicia sesión para continuar.");
    }
  };
  const enterDemo = async () => {
    resetDemoData();
    await removeToken();
    await load("demo", true);
  };
  const saveProfile = async (input: ProfileInput) => {
    const version = epoch.current;
    const updated = await request<Profile>("/fitness-profile", {
      method: profile ? "PATCH" : "POST",
      body: input,
    });
    if (version === epoch.current) {
      setProfile(updated);
      await cache.invalidateQueries();
    }
  };
  return (
    <Context.Provider
      value={{
        user,
        profile,
        demo,
        booting,
        bootstrapError,
        notice,
        signIn,
        register,
        enterDemo,
        signOut,
        retry: () => {
          void restore();
        },
        saveProfile,
      }}
    >
      {children}
    </Context.Provider>
  );
}
export function useSession() {
  const value = useContext(Context);
  if (!value) throw new Error("Missing session provider");
  return value;
}
