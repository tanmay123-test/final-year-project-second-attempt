import api from '../shared/api';

// user_id is now read from JWT token on the backend — no need to send it manually
const goalApi = {
  getGoals: () =>
    api.get('/api/goal/list'),

  createGoal: (data) =>
    api.post('/api/goal/create', data),

  addSavings: (data) =>
    api.post('/api/goal/add-savings', data),

  getProgress: (goalId) =>
    api.get(`/api/goal/progress?goal_id=${goalId}`),

  simulate: (data) =>
    api.post('/api/goal/simulate', data),

  getProjection: (goalId, months = 24) =>
    api.get(`/api/goal/projection?goal_id=${goalId}&months=${months}`),

  transferLeftover: (data) =>
    api.post('/api/goal/transfer-leftover', data),

  getAcceleration: () =>
    api.get('/api/goal/acceleration'),

  getNotifications: () =>
    api.get('/api/goal/notifications'),
};

export default goalApi;
