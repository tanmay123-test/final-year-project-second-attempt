import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10s timeout
});

// Event bus for non-component error handling
export const apiEvents = new EventTarget();

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = 'An unexpected error occurred';
    if (error.response) {
      // Server responded with error
      message = error.response.data.error || error.response.data.msg || message;
      if (error.response.status === 401) {
        // Unauthorized - dispatch logout event if needed
        apiEvents.dispatchEvent(new Event('auth:unauthorized'));
      }
    } else if (error.request) {
      // Network error
      message = 'Network error. Please check your connection.';
    } else {
      message = error.message;
    }
    
    // Dispatch error event for global toast
    const event = new CustomEvent('api:error', { detail: { message } });
    apiEvents.dispatchEvent(event);

    return Promise.reject(error);
  }
);

export const authService = {
  signup: (userData) => api.post('/signup', userData),
  verifyOtp: (data) => api.post('/verify-otp', data),
  resendOtp: (data) => api.post('/resend-otp', data),
  login: (credentials) => api.post('/login', credentials),
  getUserInfo: () => api.get('/user/info'),
};

export const workerService = {
  // Auth
  register: (data) => api.post('/worker/signup', data), // Generic
  registerHealthcare: (data) => api.post('/worker/healthcare/signup', data),
  login: (credentials) => api.post('/worker/login', credentials),
  verifyToken: () => api.get('/api/provider/auth/me'),
  
  // Dashboard & Management
  getRequests: (workerId) => api.get(`/worker/${workerId}/requests`),
  getAppointments: (workerId) => api.get(`/worker/${workerId}/appointments`),
  getHistory: (workerId) => api.get(`/worker/${workerId}/history`),
  getDashboardStats: (workerId) => api.get(`/worker/${workerId}/dashboard/stats`),
  
  // Status & Availability
  getStatus: (workerId) => api.get(`/worker/${workerId}/status`),
  updateStatus: (workerId, status) => api.post(`/worker/${workerId}/status`, { status }),
  getAvailability: (workerId, date) => api.get(`/worker/${workerId}/availability?date=${date}`),
  addAvailability: (workerId, date, timeSlot) => api.post(`/worker/${workerId}/availability`, { date, time_slot: timeSlot }),
  removeAvailability: (workerId, date, timeSlot) => api.delete(`/worker/${workerId}/availability`, { data: { date, time_slot: timeSlot } }),
  
  // Responses
  respondToRequest: (data) => api.post('/worker/respond', data),
};

export const doctorService = {
  getAllDoctors: () => api.get('/healthcare/doctors'),
  getSpecializations: () => api.get('/healthcare/specializations'),
  getDoctorsBySpecialization: (spec) => api.get(`/healthcare/doctors/${spec}`),
  searchDoctors: (query) => api.get(`/healthcare/search?q=${query}`),
  getDoctorById: (id) => api.get(`/worker/${id}`),
  getAvailability: (id, date) => api.get(`/worker/${id}/availability?date=${date}`),
};

export const appointmentService = {
  bookClinic: (data) => api.post('/appointment/book', data),
  bookVideo: (data) => api.post('/appointment/video-request', data),
  getUserAppointments: () => api.get('/user/appointments'),
};

export const videoService = {
  startVideo: (appointmentId, otp) => api.post('/appointment/video/start', { appointment_id: appointmentId, otp }),
  getVideoLink: (appointmentId) => api.get(`/appointment/${appointmentId}/video-link`),
  endVideo: (appointmentId) => api.post('/appointment/video/end', { appointment_id: appointmentId }),
  // Duplicate start endpoint in backend, mapping both just in case
  startVideoCall: (data) => api.post('/video/start', data),
};

export const aiService = {
  analyzeSymptoms: (data) => api.post('/healthcare/ai-care', data),
};

export const commonService = {
  getServices: () => api.get('/services'),
};

export const housekeepingService = {
  getServices: (workerId) => api.get('/api/housekeeping/services', { params: { worker_id: workerId } }),
  getTopCleaners: () => api.get('/api/housekeeping/services'), 
  getRecommendedWorkers: (serviceType) => api.get(`/api/housekeeping/recommendations/workers`, { params: { service_type: serviceType, _t: new Date().getTime() } }),
  getSlots: (serviceType, date, workerId) => api.get('/api/housekeeping/slots', { params: { service_type: serviceType, date, worker_id: workerId, _t: new Date().getTime() } }),
  checkAvailability: (data) => api.post('/api/housekeeping/check-availability', data),
  confirmBooking: (data) => api.post('/api/housekeeping/confirm-booking', data),
  getUserBookings: () => api.get('/api/housekeeping/my-bookings', { params: { _t: new Date().getTime() } }),
  
  // Worker
  getWorkerStatus: () => api.get('/api/housekeeping/worker/status'),
  setWorkerStatus: (isOnline) => api.post('/api/housekeeping/worker/status', { is_online: isOnline }),
  updateBookingStatus: (data) => api.post('/api/housekeeping/worker/update-status', data),
  getWorkerBalance: () => api.get('/api/housekeeping/worker/balance'),
  getWorkerServices: () => api.get('/api/housekeeping/worker/services'),
  saveWorkerServices: (services) => api.post('/api/housekeeping/worker/services', { services }),
  cancelBooking: (bookingId) => api.post('/api/housekeeping/cancel-booking', { booking_id: bookingId }),
};

export const moneyService = {
  getDashboardData: () => api.get('/api/money/dashboard'),
  addTransaction: (data) => api.post('/api/money/transactions', data),
  getTransactions: (filters = {}) => api.get('/api/money/transactions', { params: filters }),
  setBudget: (data) => api.post('/api/money/budget', data),
  getBudgets: () => api.get('/api/money/budget'),
  createGoal: (data) => api.post('/api/money/goals', data),
  getGoals: () => api.get('/api/money/goals'),
  getMonthlyAnalytics: (months = 6) => api.get('/api/money/analytics/monthly', { params: { months } }),
  chatWithAI: (message) => api.post('/api/money/chat', { message }),
};

export default api;
