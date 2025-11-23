import { createContext, useContext, useState, ReactNode } from 'react';
import type { Patient, Visit } from '../types';

interface AppContextType {
  currentPatient: Patient | null;
  setCurrentPatient: (patient: Patient | null) => void;
  currentVisit: Visit | null;
  setCurrentVisit: (visit: Visit | null) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  error: string | null;
  setError: (error: string | null) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [currentPatient, setCurrentPatient] = useState<Patient | null>(null);
  const [currentVisit, setCurrentVisit] = useState<Visit | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <AppContext.Provider
      value={{
        currentPatient,
        setCurrentPatient,
        currentVisit,
        setCurrentVisit,
        isLoading,
        setIsLoading,
        error,
        setError,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
}
