import React, { createContext, useState, useContext, useEffect, type ReactNode } from 'react';
import { OpenAPI } from "../services/candidates-services/core/OpenAPI";

interface AuthContextType {
  accessToken: string | null;
  login: (token: string) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  // Access token is now strictly in-memory (state)
  const [accessToken, setAccessToken] = useState<string | null>(null);

  // Sync OpenAPI client whenever the token state changes
  useEffect(() => {
    OpenAPI.TOKEN = async () => accessToken ?? "";
  }, [accessToken]);

  const login = (token: string) => {
    setAccessToken(token);
  };

  const logout = () => {
    setAccessToken(null);
  };

  return (
    <AuthContext.Provider value={{ accessToken, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};