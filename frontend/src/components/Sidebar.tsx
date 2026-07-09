import React from 'react';
import { LayoutDashboard, Grid, Users, UserCheck } from 'lucide-react';
import { useApp } from '../context/AppContext';

export const Sidebar: React.FC = () => {
  const { activeTab, setActiveTab } = useApp();

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'seats', label: 'Seat Map Grid', icon: Grid },
    { id: 'allocation', label: 'Seat Allocation', icon: UserCheck },
    { id: 'employees', label: 'Employee Registry', icon: Users },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 text-slate-300 flex flex-col h-screen shrink-0">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center font-bold text-white tracking-wider">
            E
          </div>
          <span className="font-bold text-white text-lg tracking-tight">Ethara</span>
          <span className="text-xs text-slate-500 font-mono mt-1">v1.0</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 py-6 px-4 space-y-1 overflow-y-auto">
        {menuItems.map(item => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-medium transition-all ${
                isActive
                  ? 'bg-blue-600 text-white font-semibold'
                  : 'hover:bg-slate-800 hover:text-white'
              }`}
            >
              <Icon size={18} className={isActive ? 'text-white' : 'text-slate-400'} />
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800 text-xs text-slate-500 font-mono text-center">
        Matte Grid Layout System
      </div>
    </aside>
  );
};
