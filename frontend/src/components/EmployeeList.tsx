import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { UserPlus, Search, X, ShieldAlert } from 'lucide-react';
import { EmployeeAPI } from '../services/api';

export const EmployeeList: React.FC = () => {
  const { employees, projects, seats, refreshAllData, userRole } = useApp();
  const [showAddForm, setShowAddForm] = useState<boolean>(false);

  // Search & Filter State
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [filterProject, setFilterProject] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('');

  // Add Employee Form State
  const [name, setName] = useState<string>('');
  const [code, setCode] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [department, setDepartment] = useState<string>('');
  const [role, setRole] = useState<string>('');
  const [joiningDate, setJoiningDate] = useState<string>('');
  const [projectId, setProjectId] = useState<string>('');
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);

  const handleAddEmployee = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitError(null);

    const payload = {
      employee_code: code,
      name,
      email,
      department: department || null,
      role: role || null,
      joining_date: joiningDate,
      status: 'Active',
      project_id: projectId ? parseInt(projectId) : null,
    };

    try {
      await EmployeeAPI.create(payload);
      // Reset form
      setName('');
      setCode('');
      setEmail('');
      setDepartment('');
      setRole('');
      setJoiningDate('');
      setProjectId('');
      setShowAddForm(false);
      await refreshAllData();
    } catch (err: any) {
      setSubmitError(err.response?.data?.detail || 'Failed to register employee.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeactivate = async (id: number) => {
    if (!window.confirm('Are you sure you want to deactivate this employee? This will release their allocated seat.')) return;
    try {
      await EmployeeAPI.deactivate(id);
      await refreshAllData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to deactivate.');
    }
  };

  // Pagination state
  const [currentPage, setCurrentPage] = useState<number>(1);
  const itemsPerPage = 50;

  // Filter Logic
  const filteredEmployees = employees.filter(emp => {
    const matchesSearch =
      emp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      emp.employee_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      emp.email.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesProject = filterProject ? emp.project_id === parseInt(filterProject) : true;
    const matchesStatus = filterStatus ? emp.status === filterStatus : true;

    return matchesSearch && matchesProject && matchesStatus;
  });

  // Reset page when search or filters change
  React.useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, filterProject, filterStatus]);

  const totalPages = Math.ceil(filteredEmployees.length / itemsPerPage) || 1;
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedEmployees = filteredEmployees.slice(startIndex, startIndex + itemsPerPage);

  return (
    <div className="flex-grow p-8 bg-slate-50 flex flex-col lg:flex-row gap-8 overflow-y-auto">
      {/* Directory Grid */}
      <div className="flex-1 bg-white border border-slate-200 rounded p-6 flex flex-col space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <h3 className="font-bold text-slate-800 text-sm tracking-tight">
            Employee Directory ({filteredEmployees.length} registered)
          </h3>
          {userRole === 'HR' && (
            <button
              onClick={() => setShowAddForm(true)}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-slate-900 border border-slate-950 text-white rounded text-xs font-semibold hover:bg-slate-800 transition-colors"
            >
              <UserPlus size={14} />
              Add New Employee
            </button>
          )}
        </div>

        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-slate-50 p-4 border border-slate-200 rounded">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-2.5 text-slate-400" size={16} />
            <input
              type="text"
              placeholder="Search code, name, email..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 bg-white border border-slate-200 rounded text-xs font-mono"
            />
          </div>

          {/* Project Filter */}
          <select
            value={filterProject}
            onChange={e => setFilterProject(e.target.value)}
            className="w-full border border-slate-200 bg-white rounded px-3 py-1.5 text-xs font-mono"
          >
            <option value="">-- All Projects --</option>
            {projects.map(p => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            value={filterStatus}
            onChange={e => setFilterStatus(e.target.value)}
            className="w-full border border-slate-200 bg-white rounded px-3 py-1.5 text-xs font-mono"
          >
            <option value="">-- All Statuses --</option>
            <option value="Active">Active</option>
            <option value="Deactivated">Deactivated</option>
          </select>
        </div>

        {/* Directory Table */}
        <div className="flex-1 overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-200 text-slate-400 uppercase tracking-wider">
                <th className="py-2.5">Code</th>
                <th className="py-2.5">Name</th>
                <th className="py-2.5">Email</th>
                <th className="py-2.5">Project</th>
                <th className="py-2.5">Seat</th>
                <th className="py-2.5">Status</th>
                <th className="py-2.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {paginatedEmployees.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400">
                    No employees found matching filter settings.
                  </td>
                </tr>
              ) : (
                paginatedEmployees.map(emp => {
                  // Find active seat allocation for the display column
                  const seatAlloc = seats.find(s => s.status === 'Occupied' && s.allocations?.some((a: any) => a.employee_id === emp.id && a.allocation_status === 'Active'));
                  return (
                    <tr key={emp.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 font-bold">{emp.employee_code}</td>
                      <td className="py-3 font-medium">{emp.name}</td>
                      <td className="py-3 text-slate-500">{emp.email}</td>
                      <td className="py-3">
                        <span className="font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded text-[10px]">
                          {emp.project?.name || 'No Project'}
                        </span>
                      </td>
                      <td className="py-3 font-medium">
                        {seatAlloc ? (
                          <span className="text-blue-700 font-semibold">{seatAlloc.seat_number}</span>
                        ) : (
                          <span className="text-amber-600">Unallocated</span>
                        )}
                      </td>
                      <td className="py-3">
                        <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                          emp.status === 'Active' ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'
                        }`}>
                          {emp.status}
                        </span>
                      </td>
                      <td className="py-3 text-right">
                        {userRole === 'HR' && emp.status === 'Active' && (
                          <button
                            onClick={() => handleDeactivate(emp.id)}
                            className="text-red-600 hover:text-red-800 hover:underline"
                          >
                            Deactivate
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between border-t border-slate-100 pt-4">
            <span className="text-xs text-slate-400 font-mono">
              Showing {startIndex + 1}–{Math.min(startIndex + itemsPerPage, filteredEmployees.length)} of {filteredEmployees.length} records
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className="px-3 py-1.5 border border-slate-200 rounded text-xs font-semibold hover:bg-slate-50 disabled:opacity-40 transition-colors cursor-pointer"
              >
                Previous
              </button>
              <span className="text-xs text-slate-700 font-semibold font-mono">
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
                className="px-3 py-1.5 border border-slate-200 rounded text-xs font-semibold hover:bg-slate-50 disabled:opacity-40 transition-colors cursor-pointer"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Add Employee Form Sidebar */}
      {showAddForm && (
        <div className="w-full lg:w-96 bg-white border border-slate-200 rounded p-6 flex flex-col shrink-0 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="font-bold text-slate-800 text-sm tracking-tight flex items-center gap-1.5">
              <UserPlus size={16} className="text-slate-500" />
              Register New Employee
            </h3>
            <button
              onClick={() => setShowAddForm(false)}
              className="text-slate-400 hover:text-slate-600 rounded p-1 hover:bg-slate-100"
            >
              <X size={16} />
            </button>
          </div>

          {submitError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded flex items-start gap-2 text-xs text-red-700 font-mono">
              <ShieldAlert size={16} className="text-red-600 shrink-0 mt-0.5" />
              <span>{submitError}</span>
            </div>
          )}

          <form onSubmit={handleAddEmployee} className="space-y-4 text-xs font-mono">
            {/* Code */}
            <div className="space-y-1.5">
              <label className="font-bold text-slate-700">Employee Code</label>
              <input
                type="text"
                value={code}
                onChange={e => setCode(e.target.value)}
                required
                placeholder="e.g. EMP4923"
                className="w-full border border-slate-200 rounded px-3 py-2 bg-slate-50 focus:bg-white"
              />
            </div>

            {/* Name */}
            <div className="space-y-1.5">
              <label className="font-bold text-slate-700">Full Name</label>
              <input
                type="text"
                value={name}
                onChange={e => setName(e.target.value)}
                required
                placeholder="e.g. Amit Patel"
                className="w-full border border-slate-200 rounded px-3 py-2 bg-slate-50 focus:bg-white"
              />
            </div>

            {/* Email */}
            <div className="space-y-1.5">
              <label className="font-bold text-slate-700">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                placeholder="e.g. amit@ethara.ai"
                className="w-full border border-slate-200 rounded px-3 py-2 bg-slate-50 focus:bg-white"
              />
            </div>

            {/* Department */}
            <div className="space-y-1.5">
              <label className="font-bold text-slate-700">Department</label>
              <input
                type="text"
                value={department}
                onChange={e => setDepartment(e.target.value)}
                placeholder="e.g. Engineering"
                className="w-full border border-slate-200 rounded px-3 py-2 bg-slate-50 focus:bg-white"
              />
            </div>

            {/* Role */}
            <div className="space-y-1.5">
              <label className="font-bold text-slate-700">Role Title</label>
              <input
                type="text"
                value={role}
                onChange={e => setRole(e.target.value)}
                placeholder="e.g. Frontend Engineer"
                className="w-full border border-slate-200 rounded px-3 py-2 bg-slate-50 focus:bg-white"
              />
            </div>

            {/* Joining Date */}
            <div className="space-y-1.5">
              <label className="font-bold text-slate-700">Joining Date</label>
              <input
                type="date"
                value={joiningDate}
                onChange={e => setJoiningDate(e.target.value)}
                required
                className="w-full border border-slate-200 rounded px-3 py-2 bg-slate-50 focus:bg-white"
              />
            </div>

            {/* Project Mapping */}
            <div className="space-y-1.5">
              <label className="font-bold text-slate-700">Project Assignment</label>
              <select
                value={projectId}
                onChange={e => setProjectId(e.target.value)}
                className="w-full border border-slate-200 bg-slate-50 rounded px-3 py-2"
              >
                <option value="">-- No Project --</option>
                {projects.map(p => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-slate-900 border border-slate-950 text-white rounded py-2.5 font-bold hover:bg-slate-800 transition-colors disabled:opacity-50 mt-4"
            >
              Register Employee Record
            </button>
          </form>
        </div>
      )}
    </div>
  );
};
