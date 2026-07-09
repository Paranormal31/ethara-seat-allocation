import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { DashboardAPI, EmployeeAPI, ProjectAPI, SeatAPI, AIAPI } from '../services/api';

export interface ChatMessage {
  sender: 'user' | 'assistant';
  text: string;
  timestamp: Date;
}

export type UserRole = 'HR' | 'Employee';

interface AppContextType {
  dashboardData: any;
  employees: any[];
  projects: any[];
  seats: any[];
  selectedFloor: number;
  selectedZone: string;
  activeTab: string;
  aiMessages: ChatMessage[];
  loading: boolean;
  error: string | null;
  userRole: UserRole;
  setUserRole: (role: UserRole) => void;
  currentEmployee: any | null;
  setCurrentEmployee: (emp: any | null) => void;
  setSelectedFloor: (floor: number) => void;
  setSelectedZone: (zone: string) => void;
  setActiveTab: (tab: string) => void;
  refreshAllData: () => Promise<void>;
  allocateSeat: (employeeId: number, seatId: number) => Promise<void>;
  releaseSeat: (employeeId: number) => Promise<void>;
  reserveSeat: (seatId: number, projectId: number) => Promise<void>;
  releaseReservation: (seatId: number) => Promise<void>;
  getSeatSuggestions: (employeeId: number) => Promise<any[]>;
  sendAIQuery: (query: string) => Promise<void>;
  clearChat: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [employees, setEmployees] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);
  const [seats, setSeats] = useState<any[]>([]);
  const [selectedFloor, setSelectedFloorState] = useState<number>(1);
  const [selectedZone, setSelectedZoneState] = useState<string>('Zone A');
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [aiMessages, setAiMessages] = useState<ChatMessage[]>([
    {
      sender: 'assistant',
      text: "Hello! I am your local AI Seat Allocation Assistant. How can I help you manage the workspace today?",
      timestamp: new Date(),
    },
  ]);
  const [loading, setLoading] = useState<boolean>(true); // true until first fetch completes
  const [error, setError] = useState<string | null>(null);
  const [userRole, setUserRole] = useState<UserRole>('HR');
  const [currentEmployee, setCurrentEmployee] = useState<any | null>(null);

  // Automatically select Amit as the default employee when employees are loaded
  useEffect(() => {
    if (employees.length > 0 && !currentEmployee) {
      const amit = employees.find(e => e.name.toLowerCase() === 'amit');
      if (amit) {
        setCurrentEmployee(amit);
      }
    }
  }, [employees, currentEmployee]);

  const setSelectedFloor = (floor: number) => setSelectedFloorState(floor);
  const setSelectedZone = (zone: string) => setSelectedZoneState(zone);

  const refreshAllData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [dash, emps, projs, sts] = await Promise.all([
        DashboardAPI.summary(),
        EmployeeAPI.list(0, 10000), // load all seeded employees (up to 10,000)
        ProjectAPI.list(),
        SeatAPI.list(),
      ]);
      setDashboardData(dash);
      setEmployees(Array.isArray(emps) ? emps : []);
      setProjects(Array.isArray(projs) ? projs : []);
      setSeats(Array.isArray(sts) ? sts : []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load workspace data. Please make sure the backend server is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshAllData();
  }, [refreshAllData]);

  const allocateSeat = async (employeeId: number, seatId: number) => {
    setError(null);
    try {
      await SeatAPI.allocate(employeeId, seatId);
      await refreshAllData();
    } catch (err: any) {
      const errMsg = err.response?.data?.detail || 'Failed to allocate seat.';
      setError(errMsg);
      throw new Error(errMsg);
    }
  };

  const releaseSeat = async (employeeId: number) => {
    setError(null);
    try {
      await SeatAPI.release(employeeId);
      await refreshAllData();
    } catch (err: any) {
      const errMsg = err.response?.data?.detail || 'Failed to release seat.';
      setError(errMsg);
      throw new Error(errMsg);
    }
  };

  const reserveSeat = async (seatId: number, projectId: number) => {
    setError(null);
    try {
      await SeatAPI.reserve(seatId, projectId);
      await refreshAllData();
    } catch (err: any) {
      const errMsg = err.response?.data?.detail || 'Failed to reserve seat.';
      setError(errMsg);
      throw new Error(errMsg);
    }
  };

  const releaseReservation = async (seatId: number) => {
    setError(null);
    try {
      await SeatAPI.releaseReservation(seatId);
      await refreshAllData();
    } catch (err: any) {
      const errMsg = err.response?.data?.detail || 'Failed to release reservation.';
      setError(errMsg);
      throw new Error(errMsg);
    }
  };

  const getSeatSuggestions = async (employeeId: number) => {
    try {
      return await SeatAPI.suggest(employeeId, 5);
    } catch (err) {
      return [];
    }
  };

  const sendAIQuery = async (query: string) => {
    const userMsg: ChatMessage = {
      sender: 'user',
      text: query,
      timestamp: new Date(),
    };
    setAiMessages(prev => [...prev, userMsg]);

    try {
      const response = await AIAPI.query(query, userRole === 'Employee' ? currentEmployee?.id : null);
      const assistantMsg: ChatMessage = {
        sender: 'assistant',
        text: response.answer,
        timestamp: new Date(),
      };
      setAiMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      const errorMsg: ChatMessage = {
        sender: 'assistant',
        text: "I encountered an error querying the service. Please make sure the backend is active.",
        timestamp: new Date(),
      };
      setAiMessages(prev => [...prev, errorMsg]);
    }
  };

  const clearChat = () => {
    setAiMessages([
      {
        sender: 'assistant',
        text: "Hello! I am your local AI Seat Allocation Assistant. How can I help you manage the workspace today?",
        timestamp: new Date(),
      },
    ]);
  };

  return (
    <AppContext.Provider
      value={{
        dashboardData,
        employees,
        projects,
        seats,
        selectedFloor,
        selectedZone,
        activeTab,
        aiMessages,
        loading,
        error,
        setSelectedFloor,
        setSelectedZone,
        setActiveTab,
        refreshAllData,
        allocateSeat,
        releaseSeat,
        reserveSeat,
        releaseReservation,
        getSeatSuggestions,
        sendAIQuery,
        clearChat,
        userRole,
        setUserRole,
        currentEmployee,
        setCurrentEmployee,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
