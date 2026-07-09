import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './components/Dashboard';
import { SeatMap } from './components/SeatMap';
import { EmployeeList } from './components/EmployeeList';
import { SeatAllocation } from './components/SeatAllocation';
import { ChatSidebar } from './components/ChatSidebar';
import { ShieldAlert } from 'lucide-react';

const WorkspaceLayout: React.FC = () => {
  const { activeTab, error, refreshAllData } = useApp();

  const renderActiveScreen = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'seats':
        return <SeatMap />;
      case 'employees':
        return <EmployeeList />;
      case 'allocation':
        return <SeatAllocation />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-100 font-sans text-xs">
      {/* Left Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        {/* Demo Mode Notice Banner */}
        <div className="bg-slate-900 border-b border-slate-950 px-8 py-2.5 flex items-center justify-between text-[11px] text-slate-300 shrink-0 font-mono">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse shrink-0" />
            <span><strong>Demo Mode:</strong> Try switching between <strong>HR Admin</strong> and <strong>Employee</strong> profiles in the top-right header to view user restrictions and test natural language queries (e.g. <em>"where sits Amit"</em>).</span>
          </div>
        </div>

        {/* Global Error Banner */}
        {error && (
          <div className="bg-red-50 border-b border-red-200 px-8 py-3 flex items-center justify-between text-xs text-red-800 shrink-0 font-mono">
            <div className="flex items-center gap-2">
              <ShieldAlert size={16} className="text-red-600" />
              <span>{error}</span>
            </div>
            <button
              onClick={() => refreshAllData()}
              className="text-[10px] uppercase font-bold text-red-700 hover:underline"
            >
              Retry Connection
            </button>
          </div>
        )}

        {/* Dynamic Screen panel */}
        {renderActiveScreen()}
      </div>

      {/* Right AI Sidebar */}
      <ChatSidebar />
    </div>
  );
};

function App() {
  return (
    <AppProvider>
      <WorkspaceLayout />
    </AppProvider>
  );
}

export default App;
