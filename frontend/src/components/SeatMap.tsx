import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Grid, UserPlus, ShieldAlert, X, Bookmark } from 'lucide-react';

export const SeatMap: React.FC = () => {
  const {
    seats,
    employees,
    projects,
    selectedFloor,
    setSelectedFloor,
    selectedZone,
    setSelectedZone,
    allocateSeat,
    releaseSeat,
    reserveSeat,
    releaseReservation,
    userRole,
  } = useApp();

  const [selectedSeat, setSelectedSeat] = useState<any>(null);
  const [allocationEmployeeId, setAllocationEmployeeId] = useState<string>('');
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [actionMode, setActionMode] = useState<'allocate' | 'reserve'>('allocate');
  const [actionError, setActionError] = useState<string | null>(null);
  const [processing, setProcessing] = useState<boolean>(false);

  // Filter seats based on current floor and zone selection
  const filteredSeats = seats.filter(
    s => s.floor === selectedFloor && s.zone.toLowerCase() === selectedZone.toLowerCase()
  );

  // Group seats by Bay for organized rendering
  const bays = Array.from(new Set(filteredSeats.map(s => s.bay))).sort((a, b) => a - b);

  // Get active unseated employees for allocation dropdown
  const activeUnseatedEmployees = employees.filter(
    emp => emp.status === 'Active' && !seats.some(s => s.status === 'Occupied' && s.allocations?.some((a: any) => a.employee_id === emp.id && a.allocation_status === 'Active'))
  );

  const handleSeatClick = (seat: any) => {
    setSelectedSeat(seat);
    setAllocationEmployeeId('');
    setSelectedProjectId('');
    setActionMode('allocate');
    setActionError(null);
  };

  const handleAllocate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!allocationEmployeeId || !selectedSeat) return;
    setProcessing(true);
    setActionError(null);
    try {
      await allocateSeat(parseInt(allocationEmployeeId), selectedSeat.id);
      setSelectedSeat(null);
    } catch (err: any) {
      setActionError(err.message || 'Allocation failed');
    } finally {
      setProcessing(false);
    }
  };

  const handleReserve = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProjectId || !selectedSeat) return;
    setProcessing(true);
    setActionError(null);
    try {
      await reserveSeat(selectedSeat.id, parseInt(selectedProjectId));
      setSelectedSeat(null);
    } catch (err: any) {
      setActionError(err.message || 'Reservation failed');
    } finally {
      setProcessing(false);
    }
  };

  const handleReleaseReservation = async (seatId: number) => {
    setProcessing(true);
    setActionError(null);
    try {
      await releaseReservation(seatId);
      setSelectedSeat(null);
    } catch (err: any) {
      setActionError(err.message || 'Release reservation failed');
    } finally {
      setProcessing(false);
    }
  };

  const handleRelease = async (employeeId: number) => {
    setProcessing(true);
    setActionError(null);
    try {
      await releaseSeat(employeeId);
      setSelectedSeat(null);
    } catch (err: any) {
      setActionError(err.message || 'Release failed');
    } finally {
      setProcessing(false);
    }
  };

  const getSeatColorClass = (seat: any) => {
    switch (seat.status) {
      case 'Available':
        return 'bg-green-50 border border-green-200 text-green-700 hover:bg-green-100';
      case 'Occupied':
        return 'bg-blue-50 border border-blue-200 text-blue-700 hover:bg-blue-100';
      case 'Reserved':
        return 'bg-yellow-50 border border-yellow-200 text-yellow-700 hover:bg-yellow-100';
      default: // Maintenance
        return 'bg-slate-100 border border-slate-200 text-slate-400 hover:bg-slate-200';
    }
  };

  return (
    <div className="flex-grow p-8 bg-slate-50 flex flex-col lg:flex-row gap-8 overflow-y-auto">
      {/* Map Control Grid */}
      <div className="flex-1 bg-white border border-slate-200 rounded p-6 flex flex-col space-y-6">
        {/* Floor and Zone Selector */}
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4">
          {/* Floor tabs */}
          <div className="flex items-center gap-1">
            {[1, 2, 3, 4, 5].map(floor => (
              <button
                key={floor}
                onClick={() => setSelectedFloor(floor)}
                className={`px-3 py-1.5 rounded font-mono text-xs font-semibold border transition-colors ${
                  selectedFloor === floor
                    ? 'bg-slate-900 border-slate-900 text-white'
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                Floor {floor}
              </button>
            ))}
          </div>

          {/* Zone Selector */}
          <div className="flex items-center gap-1">
            {['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E', 'Zone F', 'Zone G', 'Zone H', 'Zone I', 'Zone J'].map(zone => (
              <button
                key={zone}
                onClick={() => setSelectedZone(zone)}
                className={`px-3 py-1.5 rounded text-xs font-semibold border transition-colors ${
                  selectedZone.toLowerCase() === zone.toLowerCase()
                    ? 'bg-slate-900 border-slate-900 text-white'
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                {zone}
              </button>
            ))}
          </div>
        </div>

        {/* Map Grid */}
        <div className="flex-1 border border-slate-100 rounded bg-slate-50 p-6 flex flex-col space-y-8 min-h-[400px]">
          {filteredSeats.length === 0 ? (
            <div className="flex-grow flex items-center justify-center">
              <span className="text-slate-400 font-mono text-xs">
                No seats generated on Floor {selectedFloor} {selectedZone}. Run seed scripts.
              </span>
            </div>
          ) : (
            bays.map(bay => {
              const baySeats = filteredSeats.filter(s => s.bay === bay);
              return (
                <div key={bay} className="space-y-3">
                  <h4 className="text-[10px] uppercase font-bold text-slate-400 tracking-wider font-mono">
                    Bay {bay}
                  </h4>
                  <div className="grid grid-cols-5 md:grid-cols-10 gap-3">
                    {baySeats.map(seat => {
                      return (
                        <button
                          key={seat.id}
                          onClick={() => handleSeatClick(seat)}
                          className={`aspect-square rounded text-[10px] font-bold font-mono transition-all flex flex-col items-center justify-center relative cursor-pointer ${getSeatColorClass(
                            seat
                          )}`}
                          title={`Seat: ${seat.seat_number} - Status: ${seat.status}`}
                        >
                          <span>{seat.seat_number}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Detail Sidebar / Modal replacement (Side Matte Box) */}
      {selectedSeat && (
        <div className="w-full lg:w-96 bg-white border border-slate-200 rounded p-6 flex flex-col shrink-0 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="font-bold text-slate-800 text-sm tracking-tight flex items-center gap-1.5">
              <Grid size={16} className="text-slate-500" />
              Seat Details ({selectedSeat.seat_number})
            </h3>
            <button
              onClick={() => setSelectedSeat(null)}
              className="text-slate-400 hover:text-slate-600 rounded p-1 hover:bg-slate-100"
            >
              <X size={16} />
            </button>
          </div>

          {/* Seat specifications */}
          <div className="grid grid-cols-2 gap-4 text-xs font-mono">
            <div className="p-3 bg-slate-50 border border-slate-100 rounded">
              <span className="text-slate-400 block text-[10px]">FLOOR</span>
              <span className="font-bold text-slate-800">{selectedSeat.floor}</span>
            </div>
            <div className="p-3 bg-slate-50 border border-slate-100 rounded">
              <span className="text-slate-400 block text-[10px]">ZONE</span>
              <span className="font-bold text-slate-800">{selectedSeat.zone}</span>
            </div>
            <div className="p-3 bg-slate-50 border border-slate-100 rounded">
              <span className="text-slate-400 block text-[10px]">BAY</span>
              <span className="font-bold text-slate-800">Bay {selectedSeat.bay}</span>
            </div>
            <div className="p-3 bg-slate-50 border border-slate-100 rounded">
              <span className="text-slate-400 block text-[10px]">STATUS</span>
              <span className="font-bold text-slate-800">{selectedSeat.status}</span>
            </div>
          </div>

          {/* Error notifications inside side box */}
          {actionError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded flex items-start gap-2 text-xs text-red-700">
              <ShieldAlert size={16} className="text-red-600 shrink-0 mt-0.5" />
              <span className="font-mono">{actionError}</span>
            </div>
          )}

          {/* Action Details depending on status */}
          {userRole === 'Employee' ? (
            <div className="p-4 border border-slate-200 rounded space-y-3 bg-slate-50 text-xs font-mono text-slate-500">
              Seat allocation and releasing options are locked. Switch to <strong>HR Admin</strong> role to edit workspace layout.
            </div>
          ) : selectedSeat.status === 'Available' ? (
            <div className="space-y-4">
              <div className="flex border-b border-slate-200">
                <button
                  type="button"
                  onClick={() => setActionMode('allocate')}
                  className={`flex-1 pb-2 text-center text-xs font-semibold ${
                    actionMode === 'allocate' ? 'border-b-2 border-slate-900 text-slate-900' : 'text-slate-400'
                  }`}
                >
                  Allocate Employee
                </button>
                <button
                  type="button"
                  onClick={() => setActionMode('reserve')}
                  className={`flex-1 pb-2 text-center text-xs font-semibold ${
                    actionMode === 'reserve' ? 'border-b-2 border-slate-900 text-slate-900' : 'text-slate-400'
                  }`}
                >
                  Reserve Seat
                </button>
              </div>

              {actionMode === 'allocate' ? (
                <form onSubmit={handleAllocate} className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-slate-700 block">Allocate to employee</label>
                    <select
                      value={allocationEmployeeId}
                      onChange={e => setAllocationEmployeeId(e.target.value)}
                      required
                      className="w-full border border-slate-200 bg-white rounded px-3 py-2 text-xs font-mono"
                    >
                      <option value="">-- Select Active Employee --</option>
                      {activeUnseatedEmployees.map(emp => (
                        <option key={emp.id} value={emp.id}>
                          {emp.name} ({emp.employee_code}) - {emp.project?.name || 'No Project'}
                        </option>
                      ))}
                    </select>
                  </div>
                  <button
                    type="submit"
                    disabled={processing || !allocationEmployeeId}
                    className="w-full bg-slate-900 border border-slate-950 text-white rounded py-2 text-xs font-semibold hover:bg-slate-800 transition-colors disabled:opacity-50 flex items-center justify-center gap-1.5"
                  >
                    <UserPlus size={14} />
                    Confirm Allocation
                  </button>
                </form>
              ) : (
                <form onSubmit={handleReserve} className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-slate-700 block">Reserve for project</label>
                    <select
                      value={selectedProjectId}
                      onChange={e => setSelectedProjectId(e.target.value)}
                      required
                      className="w-full border border-slate-200 bg-white rounded px-3 py-2 text-xs font-mono"
                    >
                      <option value="">-- Select Project --</option>
                      {projects.map(proj => (
                        <option key={proj.id} value={proj.id}>
                          {proj.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <button
                    type="submit"
                    disabled={processing || !selectedProjectId}
                    className="w-full bg-amber-600 border border-amber-700 text-white rounded py-2 text-xs font-semibold hover:bg-amber-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-1.5"
                  >
                    <Bookmark size={14} />
                    Confirm Reservation
                  </button>
                </form>
              )}
            </div>
          ) : (
            /* Seated / Reserved details */
            <div className="space-y-4">
              <div className="p-4 border border-slate-200 rounded space-y-3 bg-slate-50">
                {(() => {
                  if (selectedSeat.status === 'Reserved') {
                    return (
                      <div className="space-y-2 text-xs">
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                          Reservation Details
                        </span>
                        <div className="font-bold text-slate-800 text-sm">Seat Reserved</div>
                        <div className="font-medium text-amber-700 bg-amber-50 border border-amber-100 rounded px-2 py-0.5 inline-block mt-1">
                          Reserved
                        </div>
                        
                        {userRole === 'HR' && (
                          <div className="border-t border-slate-200 pt-3 mt-3">
                            <button
                              onClick={() => handleReleaseReservation(selectedSeat.id)}
                              disabled={processing}
                              className="w-full bg-red-50 border border-red-200 text-red-700 rounded py-2 text-xs font-semibold hover:bg-red-100 transition-colors disabled:opacity-50"
                            >
                              Release Reservation
                            </button>
                          </div>
                        )}
                      </div>
                    );
                  }

                  const alloc = selectedSeat.allocations?.find((a: any) => a.allocation_status === 'Active');
                  let occupant = alloc ? employees.find(e => e.id === alloc.employee_id) : null;
                  if (alloc && !occupant && alloc.employee) {
                    occupant = alloc.employee;
                  }
                  
                  if (!occupant) {
                    return (
                      <span className="text-xs text-slate-500 font-mono block">
                        Occupant details loading... (or not active)
                      </span>
                    );
                  }

                  return (
                    <div className="space-y-2 text-xs">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                        Current Occupant
                      </span>
                      <div className="font-bold text-slate-800 text-sm">{occupant.name}</div>
                      <div className="font-mono text-slate-500">{occupant.employee_code}</div>
                      <div className="font-mono text-slate-500">{occupant.email}</div>
                      <div className="font-medium text-blue-700 bg-blue-50 border border-blue-100 rounded px-2 py-0.5 inline-block mt-1">
                        {occupant.project?.name || 'No Project'}
                      </div>
                      
                      {userRole === 'HR' && (
                        <div className="border-t border-slate-200 pt-3 mt-3">
                          <button
                            onClick={() => handleRelease(occupant.id)}
                            disabled={processing}
                            className="w-full bg-red-50 border border-red-200 text-red-700 rounded py-2 text-xs font-semibold hover:bg-red-100 transition-colors disabled:opacity-50"
                          >
                            Release Seat Allocation
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })()}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
