import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

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

export const freelanceService = {
  // Projects
  getProjects: (filters = {}) => api.get('/api/freelance/projects', { params: filters }),
  getProjectById: (id) => api.get(`/api/freelance/projects/${id}`),
  createProject: (data) => api.post('/api/freelance/projects', data),
  updateProject: (id, data) => api.put(`/api/freelance/projects/${id}`, data),
  deleteProject: (id) => api.delete(`/api/freelance/projects/${id}`),
  
  // Proposals
  getProposals: (projectId) => api.get(`/api/freelance/projects/${projectId}/proposals`),
  createProposal: (projectId, data) => api.post(`/api/freelance/projects/${projectId}/proposals`, data),
  updateProposal: (proposalId, data) => api.put(`/api/freelance/proposals/${proposalId}`, data),
  acceptProposal: (proposalId) => api.post(`/api/freelance/proposals/${proposalId}/accept`),
  rejectProposal: (proposalId) => api.post(`/api/freelance/proposals/${proposalId}/reject`),
  
  // Contracts
  getContracts: (userId) => api.get(`/api/freelance/contracts?user_id=${userId}`),
  getContractById: (id) => api.get(`/api/freelance/contracts/${id}`),
  createContract: (data) => api.post('/api/freelance/contracts', data),
  updateContract: (id, data) => api.put(`/api/freelance/contracts/${id}`, data),
  
  // Milestones
  getMilestones: (contractId) => api.get(`/api/freelance/contracts/${contractId}/milestones`),
  createMilestone: (contractId, data) => api.post(`/api/freelance/contracts/${contractId}/milestones`, data),
  updateMilestone: (milestoneId, data) => api.put(`/api/freelance/milestones/${milestoneId}`, data),
  approveMilestone: (milestoneId) => api.post(`/api/freelance/milestones/${milestoneId}/approve`),
  
  // Payments
  getPayments: (userId) => api.get(`/api/freelance/payments?user_id=${userId}`),
  createPayment: (data) => api.post('/api/freelance/payments', data),
  releasePayment: (paymentId) => api.post(`/api/freelance/payments/${paymentId}/release`),
  
  // Reviews
  getReviews: (userId) => api.get(`/api/freelance/reviews?user_id=${userId}`),
  createReview: (data) => api.post('/api/freelance/reviews', data),
  
  // Freelancers
  getFreelancers: (filters = {}) => api.get('/api/freelance/freelancers', { params: filters }),
  getFreelancerById: (id) => api.get(`/api/freelance/freelancers/${id}`),
  getFreelancerPortfolio: (id) => api.get(`/api/freelance/freelancers/${id}/portfolio`),
  
  // Messages
  getMessages: (contractId) => api.get(`/api/freelance/contracts/${contractId}/messages`),
  sendMessage: (contractId, data) => api.post(`/api/freelance/contracts/${contractId}/messages`, data),
  
  // Notifications
  getNotifications: (userId) => api.get(`/api/freelance/notifications?user_id=${userId}`),
  markNotificationRead: (notificationId) => api.put(`/api/freelance/notifications/${notificationId}/read`),
  
  // Skills
  getSkills: () => api.get('/api/freelance/skills'),
  addSkill: (freelancerId, skillId) => api.post(`/api/freelance/freelancers/${freelancerId}/skills`, { skill_id: skillId }),
  removeSkill: (freelancerId, skillId) => api.delete(`/api/freelance/freelancers/${freelancerId}/skills/${skillId}`),
  
  // Disputes
  createDispute: (data) => api.post('/api/freelance/disputes', data),
  getDisputes: (userId) => api.get(`/api/freelance/disputes?user_id=${userId}`),
};

export default api;
