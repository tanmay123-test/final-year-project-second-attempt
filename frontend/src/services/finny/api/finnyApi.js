import { moneyService } from '../../../shared/api';

// Finny-specific API wrapper
export const finnyApi = {
  // Dashboard data
  getDashboardData: () => moneyService.getDashboardData(),
  
  // Transactions
  getTransactions: (filters = {}) => moneyService.getTransactions(filters),
  addTransaction: (data) => moneyService.addTransaction(data),
  
  // Budgets
  getBudgets: () => moneyService.getBudgets(),
  setBudget: (data) => moneyService.setBudget(data),
  
  // Goals
  getGoals: () => moneyService.getGoals(),
  createGoal: (data) => moneyService.createGoal(data),
  
  // Analytics
  getMonthlyAnalytics: (months = 6) => moneyService.getMonthlyAnalytics(months),
  
  // Chat
  chatWithAI: (message) => moneyService.chatWithAI(message)
};
