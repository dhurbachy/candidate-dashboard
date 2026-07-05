import React, { createContext, useState, useContext, useEffect, useCallback, type ReactNode, useRef } from 'react';
import { OpenAPI } from "../services/candidates-services/core/OpenAPI";
import { AuthenticationGatewaySuiteService } from "../services/candidates-services/services/AuthenticationGatewaySuiteService";

interface AuthContextType {
  accessToken: string | null;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Guard reference to ensure bootstrap runs exactly once across mounts
  const hasBootstrapped = useRef(false);

  // Sync OpenAPI client config safely when accessToken state changes
  useEffect(() => {
    OpenAPI.TOKEN = accessToken ?? "";
  }, [accessToken]);

  const login = useCallback((token: string) => {
    setAccessToken(token);
  }, []);

  const logout = useCallback(() => {
  AuthenticationGatewaySuiteService.logoutApiAuthLogoutPost()
    .catch((err) => {
      console.error("Failed to clear backend cookie session:", err);
    })
    .finally(() => {
      setAccessToken(null);
      OpenAPI.TOKEN = "";
      window.location.href = "/login";
    });
}, []);

  // Run token initialization once on application mount
  useEffect(() => {
    // If React Strict Mode mounts this twice, abort the duplicate call
    if (hasBootstrapped.current) return;
    hasBootstrapped.current = true;

    const bootstrap = async () => {
      try {
        const data = await AuthenticationGatewaySuiteService.refreshApiAuthRefreshPost();
        
        // Sync both configurations immediately
        OpenAPI.TOKEN = data.access_token;
        setAccessToken(data.access_token);
      } catch {
        setAccessToken(null);
      } finally {
        setIsLoading(false);
      }
    };
    
    bootstrap();
  }, []);

  return (
    <AuthContext.Provider value={{ accessToken, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
