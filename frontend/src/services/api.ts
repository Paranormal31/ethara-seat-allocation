import axios from 'axios';

// In production (Vercel), VITE_API_URL is set to the Render backend URL.
// In local dev, it's empty so Vite proxy handles /api → localhost:8000.
const BASE_URL = import.meta.env.VITE_API_URL ?? '';

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const ProjectAPI = {
  list: () => client.get('/api/projects/').then(r => r.data),
  get: (id: number) => client.get(`/api/projects/${id}`).then(r => r.data),
  employees: (id: number) => client.get(`/api/projects/${id}/employees`).then(r => r.data),
  create: (data: { name: string; description?: string; manager_name?: string; status?: string }) =>
    client.post('/api/projects/', data).then(r => r.data),
};

export const EmployeeAPI = {
  list: (skip = 0, limit = 100) =>
    client.get('/api/employees/', { params: { skip, limit } }).then(r => r.data),
  get: (id: number) => client.get(`/api/employees/${id}`).then(r => r.data),
  create: (data: any) => client.post('/api/employees/', data).then(r => r.data),
  update: (id: number, data: any) => client.put(`/api/employees/${id}`, data).then(r => r.data),
  deactivate: (id: number) => client.delete(`/api/employees/${id}`).then(r => r.data),
};

export const SeatAPI = {
  list: () => client.get('/api/seats/').then(r => r.data),
  available: () => client.get('/api/seats/available').then(r => r.data),
  allocate: (employeeId: number, seatId: number) =>
    client.post('/api/seats/allocate', { employee_id: employeeId, seat_id: seatId }).then(r => r.data),
  release: (employeeId: number) =>
    client.post('/api/seats/release', { employee_id: employeeId }).then(r => r.data),
  suggest: (employeeId: number, limit = 5) =>
    client.get(`/api/seats/suggest/${employeeId}`, { params: { limit } }).then(r => r.data),
  reserve: (seatId: number, projectId: number) =>
    client.post('/api/seats/reserve', { seat_id: seatId, project_id: projectId }).then(r => r.data),
  releaseReservation: (seatId: number) =>
    client.post('/api/seats/release-reservation', { seat_id: seatId }).then(r => r.data),
};

export const DashboardAPI = {
  summary: () => client.get('/api/dashboard/summary').then(r => r.data),
};

export const AIAPI = {
  query: (queryText: string, employeeId?: number | null) =>
    client.post('/api/ai/query', { query: queryText, employee_id: employeeId }).then(r => r.data),
};
