'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { login as apiLogin, register as apiRegister, getCurrentUser, setAuthToken } from '@/lib/api';

interface User {
  id: number;
  email: string;
  username: string;
  display_name?: string;
  avatar_url?: string;
  bio?: string;
  preferred_language: string;
  preferred_format: string;
  is_active: boolean;
  is_verified: boolean;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, displayName?: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('auth_token');
    if (token) {
      setAuthToken(token);
      refreshUser();
    } else {
      setIsLoading(false);
    }
  }, []);

  const refreshUser = async () => {
    try {
      const response = await getCurrentUser();
      setUser(response.data);
    } catch {
      // Token invalid or expired
      localStorage.removeItem('auth_token');
      setAuthToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await apiLogin({ email, password });
    const { access_token, user: userData } = response.data;

    localStorage.setItem('auth_token', access_token);
    setAuthToken(access_token);
    setUser(userData);
  };

  const register = async (email: string, username: string, password: string, displayName?: string) => {
    const response = await apiRegister({ email, username, password, display_name: displayName });
    const { access_token, user: userData } = response.data;

    localStorage.setItem('auth_token', access_token);
    setAuthToken(access_token);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setAuthToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
