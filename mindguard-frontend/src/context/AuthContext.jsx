import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { auth } from "../services/api";

const AuthContext = createContext(null);

function readStoredUser() {
  try {
    const saved = localStorage.getItem("user");
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    function handleUnauthorized() {
      if (!cancelled) setUser(null);
    }

    window.addEventListener("mindguard:unauthorized", handleUnauthorized);

    const token = localStorage.getItem("token");

    if (!token) {
      setLoading(false);
      return () => {
        cancelled = true;
        window.removeEventListener("mindguard:unauthorized", handleUnauthorized);
      };
    }

    // Trust the server, not a stale localStorage entry. This also picks up
    // profile changes made on another device.
    auth.me()
      .then((profile) => {
        if (cancelled) return;
        setUser(profile);
        localStorage.setItem("user", JSON.stringify(profile));
      })
      .catch((err) => {
        if (cancelled) return;
        if (err.status === 401) {
          localStorage.removeItem("token");
          localStorage.removeItem("user");
          setUser(null);
        } else {
          // Offline: keep the cached identity rather than logging the user
          // out because of a temporary network failure.
          setUser(readStoredUser());
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
      window.removeEventListener("mindguard:unauthorized", handleUnauthorized);
    };
  }, []);

  const login = useCallback((token, userData) => {
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(userData));
    setUser(userData);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  }, []);

  const refreshUser = useCallback((userData) => {
    if (!userData) return;
    localStorage.setItem("user", JSON.stringify(userData));
    setUser(userData);
  }, []);

  const isAuthenticated = useCallback(() => !!user, [user]);

  return (
    <AuthContext.Provider
      value={{ user, login, logout, refreshUser, loading, isAuthenticated }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
