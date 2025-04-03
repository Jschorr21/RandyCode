import React, { createContext, useContext, useEffect, useState } from 'react';
import { jwtDecode } from 'jwt-decode';
import { useToast } from "@/hooks/use-toast";

interface AuthContextType {
  user: { email: string } | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

interface JWTPayload {
  username: string;
  exp: number;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<{ email: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    const token = localStorage.getItem("access");
  
    if (token) {
      try {
        const decoded = jwtDecode<JWTPayload>(token);
        if (decoded.exp * 1000 > Date.now()) {
          setUser({ email: decoded.username });
        } else {
          localStorage.removeItem("access");
          setUser(null); // ✅
        }
      } catch {
        localStorage.removeItem("access");
        setUser(null); // ✅
      }
    } else {
      setUser(null); // ✅ force null when no token found
    }
  
    setLoading(false);
  }, []);
  

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch(`http://${window.location.hostname}:8000/api/token/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: email, password }),
      });

      const data = await response.json();

      if (!response.ok) throw new Error(data.detail || 'Login failed');

      localStorage.setItem('access', data.access);
      localStorage.setItem('refresh', data.refresh);

      const decoded = jwtDecode<JWTPayload>(data.access);
      setUser({ email: decoded.email });

      toast({
        title: 'Login successful',
      });
    } catch (error: any) {
      toast({
        title: 'Login error',
        description: error.message,
        variant: 'destructive',
      });
    }
  };

  const logout = () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    setUser(null);
    toast({
      title: 'Logged out',
    });
  };

  const value = { user, loading, login, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
