import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { UserCheck, Search, HelpCircle, Compass, CheckCircle } from 'lucide-react';

export const SeatAllocation: React.FC = () => {
  const {
    employees,
    seats,
    getSeatSuggestions,
    allocateSeat,
    userRole,
  } = useApp();

  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedEmployee, setSelectedEmployee] = useState<any>(null);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState<boolean>(false);
  const [allocating, setAllocating] = useState<boolean>(false);
  const [allocationError, setAllocationError] = useState<string | null>(null);
  const [allocationSuccess, setAllocationSuccess] = useState<boolean>(false);

  // Get active unallocated employees
  const unallocatedEmployees = employees.filter(
    emp => emp.status === 'Active' && !seats.some(s => s.status === 'Occupied' && s.allocations?.some((a: any) => a.employee_id === emp.id && a.allocation_status === 'Active'))
  );

  // Filtered list based on search term
  const filteredEmployees = unallocatedEmployees.filter(
    emp =>
      emp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      emp.employee_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (emp.project?.name && emp.project.name.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleEmployeeClick = async (emp: any) => {
    setSelectedEmployee(emp);
    setSuggestions([]);
    setLoadingSuggestions(true);
    setAllocationError(null);
    setAllocationSuccess(false);
    try {
      const sugs = await getSeatSuggestions(emp.id);
      setSuggestions(sugs);
    } catch (err) {
      console.error('Failed to get seat suggestions', err);
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const handleAllocate = async (seatId: number) => {
    if (!selectedEmployee) return;
    setAllocating(true);
    setAllocationError(null);
    setAllocationSuccess(false);
    try {
      await allocateSeat(selectedEmployee.id, seatId);
      setAllocationSuccess(true);
      setSelectedEmployee(null);
      setSuggestions([]);
    } catch (err: any) {
      setAllocationError(err.message || 'Failed to allocate seat.');
    } finally {
      setAllocating(false);
    }
  };

  return (
    <div className="flex-grow p-8 bg-slate-50 flex flex-col lg:flex-row gap-8 overflow-y-auto">
      {/* Left Pane - Unallocated List */}
      <div className="w-full lg:w-96 bg-white border border-slate-200 rounded p-6 flex flex-col space-y-4 shrink-0">
        <div className="border-b border-slate-100 pb-3 flex items-center gap-2">
          <UserCheck size={18} className="text-slate-500" />
          <h3 className="font-bold text-slate-800 text-sm tracking-tight">
            Pending Seat Allocations ({unallocatedEmployees.length})
          </h3>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-2.5 text-slate-400" size={16} />
          <input
            type="text"
            placeholder="Search name, code, project..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded text-xs font-mono"
          />
        </div>

        {/* List container */}
        <div className="flex-grow overflow-y-auto space-y-2 max-h-[500px] pr-1">
          {filteredEmployees.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-xs font-mono">
              No unallocated employees found.
            </div>
          ) : (
            filteredEmployees.map(emp => (
              <button
                key={emp.id}
                onClick={() => handleEmployeeClick(emp)}
                className={`w-full text-left p-3 rounded border transition-all flex flex-col gap-1 cursor-pointer ${
                  selectedEmployee?.id === emp.id
                    ? 'border-blue-600 bg-blue-50/50'
                    : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-800 text-xs">{emp.name}</span>
                  <span className="text-[10px] font-mono text-slate-400">{emp.employee_code}</span>
                </div>
                <div className="flex items-center justify-between mt-1">
                  <span className="text-[10px] text-slate-500 font-mono">{emp.department || 'No Dept'}</span>
                  <span className="font-semibold text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded text-[9px]">
                    {emp.project?.name || 'No Project'}
                  </span>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Right Pane - Recommendations & Actions */}
      <div className="flex-1 bg-white border border-slate-200 rounded p-6 flex flex-col min-w-0">
        {selectedEmployee ? (
          <div className="flex flex-col h-full space-y-6">
            {/* Header info */}
            <div className="border-b border-slate-100 pb-4">
              <span className="text-[10px] font-bold text-slate-400 font-mono uppercase tracking-wider block">
                Selected Employee
              </span>
              <h3 className="font-bold text-slate-800 text-lg tracking-tight mt-1">
                {selectedEmployee.name}
              </h3>
              <div className="flex flex-wrap gap-2 items-center mt-2 text-xs font-mono text-slate-500">
                <span>Code: <strong>{selectedEmployee.employee_code}</strong></span>
                <span className="text-slate-300">|</span>
                <span>Department: <strong>{selectedEmployee.department || 'N/A'}</strong></span>
                <span className="text-slate-300">|</span>
                <span>Project Assignment: <strong className="text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-100">{selectedEmployee.project?.name || 'None'}</strong></span>
              </div>
            </div>

            {/* Error handling */}
            {allocationError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded text-xs text-red-700 font-mono">
                {allocationError}
              </div>
            )}

            {/* Suggestions Box */}
            <div className="flex-grow flex flex-col space-y-4">
              <div className="flex items-center gap-1.5 text-slate-800 font-bold text-xs">
                <Compass size={16} className="text-slate-500" />
                <span>AI-Recommended Seats (Project-Proximity Optimized)</span>
              </div>

              {loadingSuggestions ? (
                <div className="flex-grow flex items-center justify-center py-12 text-slate-400 text-xs font-mono">
                  Analyzing team occupancy grids...
                </div>
              ) : suggestions.length === 0 ? (
                <div className="p-6 bg-slate-50 border border-slate-100 rounded text-center text-slate-400 text-xs font-mono">
                  {selectedEmployee.project_id 
                    ? "No proximity recommendations found. Switch to the Seat Map Grid to manually allocate."
                    : "Employee must have an assigned project before proximity recommendations can be calculated."
                  }
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {suggestions.map(seat => (
                    <div key={seat.id} className="p-4 border border-slate-200 rounded bg-slate-50 flex flex-col justify-between gap-4">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-800 text-sm font-mono">{seat.seat_number}</span>
                          <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-100 rounded text-[9px] font-bold">
                            Available
                          </span>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-500">
                          <div>Floor: <strong className="text-slate-700">{seat.floor}</strong></div>
                          <div>Zone: <strong className="text-slate-700">{seat.zone}</strong></div>
                          <div>Bay: <strong className="text-slate-700">Bay {seat.bay}</strong></div>
                        </div>
                      </div>

                      {userRole === 'HR' ? (
                        <button
                          onClick={() => handleAllocate(seat.id)}
                          disabled={allocating}
                          className="w-full bg-slate-900 border border-slate-950 text-white rounded py-2 text-xs font-bold hover:bg-slate-800 transition-colors disabled:opacity-50 cursor-pointer"
                        >
                          {allocating ? 'Allocating...' : 'Allocate Seat'}
                        </button>
                      ) : (
                        <div className="text-[10px] font-mono text-slate-400 text-center italic border-t border-slate-200 pt-2">
                          Switch to HR Admin to allocate
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="flex-grow flex flex-col items-center justify-center text-slate-400 p-8 space-y-4">
            {allocationSuccess && (
              <div className="p-4 bg-green-50 border border-green-200 text-green-800 rounded flex items-center gap-2 text-xs font-mono mb-4 max-w-md">
                <CheckCircle size={16} className="text-green-600 shrink-0" />
                <span>Seat allocation confirmed and saved successfully!</span>
              </div>
            )}
            <HelpCircle size={48} className="text-slate-300" />
            <div className="text-center space-y-1">
              <h4 className="font-bold text-slate-700 text-sm">Select an Employee</h4>
              <p className="text-xs max-w-sm">
                Click on any unallocated employee in the list to calculate proximity-based seat recommendations.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
