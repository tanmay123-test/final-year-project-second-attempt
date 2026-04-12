import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor to add auth token
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

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = 'An unexpected error occurred';
    if (error.response) {
      message = error.response.data.error || error.response.data.msg || message;
      if (error.response.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    } else if (error.request) {
      message = 'Network error. Please check your connection.';
    } else {
      message = error.message;
    }
    return Promise.reject(error);
  }
);

export const loanApi = {
  // 1. Analyze Single Loan
  analyzeLoan: async (loanData) => {
    try {
      console.log('Making loan analysis request to:', '/api/loan/analyze', loanData);
      const response = await api.post('/api/loan/analyze', loanData);
      console.log('Loan analysis response:', response);
      return { success: true, data: response.data.data };
    } catch (error) {
      console.error('Loan analysis API error:', error);
      
      // Handle different error types
      if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
        return { 
          success: false, 
          error: 'Backend server is not running. Please start the server and try again.'
        };
      }
      
      if (error.response?.status === 404) {
        return { 
          success: false, 
          error: 'Loan analysis endpoint not found. Please check backend configuration.'
        };
      }
      
      if (error.response?.status === 500) {
        return { 
          success: false, 
          error: 'Server error occurred. Please try again later.'
        };
      }
      
      return { 
        success: false, 
        error: error.response?.data?.error || error.message || 'Failed to analyze loan'
      };
    }
  },

  // 2. Compare Two Loans
  compareLoans: async (loanComparison) => {
    try {
      const response = await api.post('/api/loan/compare', loanComparison);
      return { success: true, data: response.data.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || error.message || 'Failed to compare loans'
      };
    }
  },

  // 3. Loan Impact Simulation
  simulateImpact: async (impactData) => {
    try {
      const response = await api.post('/api/loan/impact', impactData);
      return { success: true, data: response.data.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || error.message || 'Failed to simulate loan impact'
      };
    }
  },

  // 4. Early Repayment Simulation
  simulateEarlyRepayment: async (repaymentData) => {
    try {
      const response = await api.post('/api/loan/repayment-simulation', repaymentData);
      return { success: true, data: response.data.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || error.message || 'Failed to simulate early repayment'
      };
    }
  },

  // 5. Generate Repayment Schedule
  generateSchedule: async (scheduleData) => {
    try {
      const response = await api.post('/api/loan/schedule', scheduleData);
      return { success: true, data: response.data.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || error.message || 'Failed to generate repayment schedule'
      };
    }
  },

  // 6. Loan Risk Assessment — uses analyze endpoint (risk data is included in analyze response)
  assessRisk: async (riskData) => {
    try {
      const response = await api.post('/api/loan/analyze', riskData);
      return { success: true, data: response.data.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || error.message || 'Failed to assess loan risk'
      };
    }
  },

  // 7. Get Loan Analysis History
  getHistory: async () => {
    const userId = localStorage.getItem('user_id');
    try {
      const response = await api.get(`/api/loan/history/${userId}`);
      return { success: true, data: response.data.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || error.message || 'Failed to fetch loan history'
      };
    }
  }
};
