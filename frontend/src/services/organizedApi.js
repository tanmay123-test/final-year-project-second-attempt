/**
 * Organized API Service
 * Uses new organized database endpoints
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// User Authentication API
export const userAuthAPI = {
  register: (userData) => api.post('/api/register', userData),
  login: (credentials) => api.post('/api/login', credentials),
  getProfile: () => api.get('/api/user/profile'),
  updateProfile: (data) => api.put('/api/user/profile', data),
};

// Worker Authentication API
export const workerAuthAPI = {
  register: (workerData) => api.post('/api/worker/register', workerData),
  login: (credentials) => api.post('/api/worker/login', credentials),
  getProfile: () => api.get('/api/worker/profile'),
};

// Service Workers API
export const serviceWorkersAPI = {
  getWorkersByService: (serviceType) => api.get(`/api/workers/${serviceType}`),
  getHealthcareWorkers: (workerType) => api.get('/api/workers/healthcare', { 
    params: { worker_type: workerType } 
  }),
  getCarServiceWorkers: (workerType) => api.get('/api/workers/car_service', { 
    params: { worker_type: workerType } 
  }),
  getHousekeepingWorkers: () => api.get('/api/workers/housekeeping'),
  getFreelanceWorkers: () => api.get('/api/workers/freelance'),
  getMoneyManagementWorkers: () => api.get('/api/workers/money_management'),
};

// Service Statistics API
export const statisticsAPI = {
  getServiceStatistics: (serviceType) => api.get(`/api/statistics/${serviceType}`),
};

// Health Check API
export const healthAPI = {
  checkHealth: () => api.get('/api/health'),
};

// Service-specific booking API (using organized database)
export const bookingAPI = {
  createBooking: (serviceType, bookingData) => api.post(`/api/bookings/${serviceType}`, bookingData),
  getBookings: (serviceType, params = {}) => api.get(`/api/bookings/${serviceType}`, { params }),
  updateBooking: (serviceType, bookingId, data) => api.put(`/api/bookings/${serviceType}/${bookingId}`, data),
  cancelBooking: (serviceType, bookingId) => api.delete(`/api/bookings/${serviceType}/${bookingId}`),
};

// Car Service Specific API
export const carServiceAPI = {
  getMechanics: (filters = {}) => api.get('/api/workers/car_service', { 
    params: { worker_type: 'mechanic', ...filters } 
  }),
  getFuelDeliveryAgents: (filters = {}) => api.get('/api/workers/car_service', { 
    params: { worker_type: 'fuel_delivery', ...filters } 
  }),
  getTowTruckOperators: (filters = {}) => api.get('/api/workers/car_service', { 
    params: { worker_type: 'tow_truck', ...filters } 
  }),
  createCarServiceBooking: (bookingData) => api.post('/api/bookings/car_service', bookingData),
  getCarServiceBookings: (params = {}) => api.get('/api/bookings/car_service', { params }),
};

// Healthcare Service Specific API
export const healthcareAPI = {
  getDoctors: (filters = {}) => api.get('/api/workers/healthcare', { 
    params: { worker_type: 'doctor', ...filters } 
  }),
  getSpecializations: () => api.get('/api/healthcare/specializations'),
  createAppointment: (appointmentData) => api.post('/api/bookings/healthcare', appointmentData),
  getAppointments: (params = {}) => api.get('/api/bookings/healthcare', { params }),
};

// Housekeeping Service Specific API
export const housekeepingAPI = {
  getCleaners: (filters = {}) => api.get('/api/workers/housekeeping', { params: filters }),
  createCleaningBooking: (bookingData) => api.post('/api/bookings/housekeeping', bookingData),
  getCleaningBookings: (params = {}) => api.get('/api/bookings/housekeeping', { params }),
};

// Freelance Service Specific API
export const freelanceAPI = {
  getFreelancers: (filters = {}) => api.get('/api/workers/freelance', { params: filters }),
  createProject: (projectData) => api.post('/api/projects/freelance', projectData),
  getProjects: (params = {}) => api.get('/api/projects/freelance', { params }),
  submitProposal: (projectId, proposalData) => api.post(`/api/proposals/freelance/${projectId}`, proposalData),
};

// Money Management Service Specific API
export const moneyManagementAPI = {
  getAdvisors: (filters = {}) => api.get('/api/workers/money_management', { params: filters }),
  createTransaction: (transactionData) => api.post('/api/transactions/money_management', transactionData),
  getTransactions: (params = {}) => api.get('/api/transactions/money_management', { params }),
  getBudget: () => api.get('/api/budgets/money_management'),
  updateBudget: (budgetData) => api.put('/api/budgets/money_management', budgetData),
};

// Utility functions
export const apiUtils = {
  // Get current user from localStorage
  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
  
  // Get current worker from localStorage
  getCurrentWorker: () => {
    const workerStr = localStorage.getItem('worker');
    return workerStr ? JSON.parse(workerStr) : null;
  },
  
  // Set authentication data
  setAuthData: (token, user = null, worker = null) => {
    localStorage.setItem('token', token);
    if (user) {
      localStorage.setItem('user', JSON.stringify(user));
    }
    if (worker) {
      localStorage.setItem('worker', JSON.stringify(worker));
    }
  },
  
  // Clear authentication data
  clearAuthData: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('worker');
  },
  
  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },
  
  // Get user type
  getUserType: () => {
    if (localStorage.getItem('user')) return 'user';
    if (localStorage.getItem('worker')) return 'worker';
    return null;
  }
};

export default api;
