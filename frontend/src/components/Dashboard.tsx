import React from 'react';
import { useApp } from '../context/AppContext';
import { Users, Grid, CheckSquare, Clock, BarChart3, Bookmark, UserCheck } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { dashboardData, loading, setActiveTab } = useApp();

  if (loading && !dashboardData) {
    return (
      <div className="flex-grow flex items-center justify-center bg-slate-50">
        <span className="text-slate-500 font-mono">Loading dashboard analytics...</span>
      </div>
    );
  }

  // Get data or fallback to defaults
  const stats = dashboardData?.summary || {
    total_employees: 0,
    total_seats: 5500,
    occupied_seats: 0,
    available_seats: 0,
    reserved_seats: 0,
    maintenance_seats: 0,
    pending_allocations_count: 0,
  };

  const projectWise = dashboardData?.project_wise_allocations || [];
  const floorWise = dashboardData?.floor_wise_occupancy || [];

  const occupancyRate = stats.total_seats > 0
    ? round((stats.occupied_seats / stats.total_seats) * 100, 1)
    : 0.0;

  function round(val: number, precision: number) {
    const multiplier = Math.pow(10, precision || 0);
    return Math.round(val * multiplier) / multiplier;
  }

  const cards = [
    {
      title: 'Total Employees',
      value: stats.total_employees.toLocaleString(),
      desc: 'Registered in database registry',
      icon: Users,
      color: 'border-blue-100 text-blue-800 bg-white',
      action: undefined,
    },
    {
      title: 'Total Seats',
      value: stats.total_seats.toLocaleString(),
      desc: 'Configured workstation units',
      icon: Grid,
      color: 'border-slate-300 text-slate-800 bg-white',
      action: undefined,
    },
    {
      title: 'Occupied Seats',
      value: stats.occupied_seats.toLocaleString(),
      desc: `${occupancyRate}% utilization rate`,
      icon: UserCheck,
      color: 'border-purple-200 text-purple-800 bg-white',
      action: undefined,
    },
    {
      title: 'Available Seats',
      value: stats.available_seats.toLocaleString(),
      desc: 'Free and ready for allocation',
      icon: CheckSquare,
      color: 'border-green-200 text-green-800 bg-white',
      action: undefined,
    },
    {
      title: 'Reserved Seats',
      value: stats.reserved_seats.toLocaleString(),
      desc: 'Allocated for special needs',
      icon: Bookmark,
      color: 'border-indigo-200 text-indigo-800 bg-white',
      action: undefined,
    },
    {
      title: 'New Joiners Pending Allocation',
      value: stats.pending_allocations_count.toLocaleString(),
      desc: 'New joiners waiting for assignments',
      icon: Clock,
      color: 'border-amber-200 text-amber-800 bg-white hover:border-amber-400 cursor-pointer transition-colors',
      action: () => setActiveTab('allocation'),
    },
  ];

  return (
    <div className="flex-grow p-8 overflow-y-auto bg-slate-50 space-y-8">
      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div
              key={idx}
              onClick={card.action}
              className={`p-6 rounded border ${card.color} flex items-start justify-between`}
            >
              <div className="space-y-2">
                <span className="text-xs text-slate-500 font-medium tracking-tight block">
                  {card.title}
                </span>
                <span className="text-3xl font-extrabold tracking-tight block">
                  {card.value}
                </span>
                <span className="text-xs text-slate-400 block">{card.desc}</span>
              </div>
              <div className="p-2.5 bg-slate-100 rounded text-slate-600">
                <Icon size={20} />
              </div>
            </div>
          );
        })}
      </div>

      {/* Tables Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Floor Utilization */}
        <div className="bg-white border border-slate-200 rounded p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <BarChart3 className="text-slate-500" size={18} />
            <h3 className="font-bold text-slate-800 text-sm tracking-tight">
              Floor Utilization breakdown
            </h3>
          </div>
          {floorWise.length === 0 ? (
            <p className="text-xs text-slate-400 font-mono py-4">No floor data available.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-400 uppercase tracking-wider">
                    <th className="py-2.5">Floor</th>
                    <th className="py-2.5 text-center">Occupied</th>
                    <th className="py-2.5 text-center">Total Seats</th>
                    <th className="py-2.5 text-right">Occupancy Rate</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {floorWise.map((floor: any, idx: number) => (
                    <tr key={idx} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 font-semibold text-slate-800">Floor {floor.floor}</td>
                      <td className="py-3 text-center">{floor.occupied}</td>
                      <td className="py-3 text-center">{floor.total}</td>
                      <td className="py-3 text-right font-bold text-blue-600">
                        {floor.occupancy_rate}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Project Utilization */}
        <div className="bg-white border border-slate-200 rounded p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <Users className="text-slate-500" size={18} />
            <h3 className="font-bold text-slate-800 text-sm tracking-tight">
              Project Seat allocations
            </h3>
          </div>
          {projectWise.length === 0 ? (
            <p className="text-xs text-slate-400 font-mono py-4">No active projects found.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-400 uppercase tracking-wider">
                    <th className="py-2.5">Project Name</th>
                    <th className="py-2.5 text-right">Seated Members</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {projectWise.map((proj: any, idx: number) => (
                    <tr key={idx} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 font-semibold text-slate-800">{proj.project_name}</td>
                      <td className="py-3 text-right font-bold text-slate-900">{proj.count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
