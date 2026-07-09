import React from 'react';
import { RefreshCw, CheckCircle2 } from 'lucide-react';
import { useApp } from '../context/AppContext';

export const Header: React.FC = () => {
  const { activeTab, refreshAllData, loading, userRole, setUserRole, currentEmployee } = useApp();

  const getPageTitle = () => {
    switch (activeTab) {
      case 'dashboard':
        return 'Workspace Analytics Dashboard';
      case 'seats':
        return 'Interactive Seat Allocation Map';
      case 'employees':
        return 'Employee Directory Registry';
      default:
        return 'Ethara Management System';
    }
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 shrink-0">
      {/* Title */}
      <h2 className="font-bold text-slate-800 text-lg tracking-tight">
        {getPageTitle()}
      </h2>

      {/* Utilities */}
      <div className="flex items-center gap-4">
        {/* Refresh button */}
        <button
          onClick={refreshAllData}
          disabled={loading}
          className="p-2 hover:bg-slate-100 rounded text-slate-500 hover:text-slate-800 transition-colors disabled:opacity-50"
          title="Refresh Data"
        >
          <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
        </button>

        {/* Database Status indicator */}
        <div className="flex items-center gap-1.5 px-3 py-1 bg-green-50 border border-green-200 rounded-full text-xs text-green-700 font-mono">
          <CheckCircle2 size={12} className="text-green-600" />
          db connected
        </div>

        {/* User profile info / role switcher */}
        <div className="flex items-center gap-3 border-l border-slate-200 pl-4">
          <div className="flex flex-col items-end shrink-0">
            <span className="text-[10px] text-slate-400 font-medium font-mono uppercase">Role Context</span>
            <span className="text-xs font-semibold text-slate-700">
              {userRole === 'HR' ? 'Administrator' : (currentEmployee?.name || 'Employee')}
            </span>
          </div>
          <select
            value={userRole}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setUserRole(e.target.value as any)}
            className="px-2 py-1.5 bg-slate-50 border border-slate-200 rounded text-xs font-semibold font-mono text-slate-700 focus:bg-white focus:outline-none cursor-pointer"
          >
            <option value="HR">💼 HR Admin</option>
            <option value="Employee">👤 Demo Employee</option>
          </select>
        </div>
      </div>
    </header>
  );
};
