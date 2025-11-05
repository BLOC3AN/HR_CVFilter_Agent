import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '../services/apiClient';

interface SessionContextType {
  sessionId: string | null;
  createSession: () => Promise<void>;
  clearSession: () => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Load session from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem('hr_cv_session_id');
    if (stored) {
      setSessionId(stored);
    } else {
      // Create new session if none exists
      createSession();
    }
  }, []);

  const createSession = async () => {
    try {
      const response = await apiClient.createSession();
      if (response.success && response.session_id) {
        setSessionId(response.session_id);
        localStorage.setItem('hr_cv_session_id', response.session_id);
      }
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const clearSession = () => {
    setSessionId(null);
    localStorage.removeItem('hr_cv_session_id');
    createSession();
  };

  return (
    <SessionContext.Provider value={{ sessionId, createSession, clearSession }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
}

