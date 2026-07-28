import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { authApi } from "../lib/endpoints";
import { api, getRefreshToken, setAccessToken, setRefreshToken } from "../lib/api";
import type { User } from "../types";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, fullName: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // On app load, we only have a refresh token (access token lives in memory
    // and is lost on refresh) - use it to silently re-authenticate.
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      setIsLoading(false);
      return;
    }

    (async () => {
      try {
        const { data } = await api.post("/auth/refresh", { refresh_token: refreshToken });
        setAccessToken(data.access_token);
        const meResponse = await authApi.me();
        setUser(meResponse.data);
      } catch {
        setRefreshToken(null);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  async function login(email: string, password: string) {
    const { data } = await authApi.login(email, password);
    setAccessToken(data.access_token);
    setRefreshToken(data.refresh_token);
    setUser(data.user);
  }

  async function register(email: string, fullName: string, password: string) {
    const { data } = await authApi.register(email, fullName, password);
    setAccessToken(data.access_token);
    setRefreshToken(data.refresh_token);
    setUser(data.user);
  }

  function logout() {
    setAccessToken(null);
    setRefreshToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
