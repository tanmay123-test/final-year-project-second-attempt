import { moneyService } from '../../../shared/api';

// Transactions API service
export const transactionsApi = {
  // Get all transactions with optional filters
  getTransactions: async (filters = {}) => {
    try {
      const response = await moneyService.getTransactions(filters);
      return {
        success: true,
        data: response.data.transactions || []
      };
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to fetch transactions',
        data: []
      };
    }
  },

  // Get transactions by category
  getTransactionsByCategory: async (category) => {
    return transactionsApi.getTransactions({ category });
  },

  // Search transactions by merchant name
  searchTransactions: async (searchTerm) => {
    try {
      const response = await moneyService.getTransactions();
      const allTransactions = response.data.transactions || [];
      
      const filteredTransactions = allTransactions.filter(transaction =>
        transaction.merchant?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      
      return {
        success: true,
        data: filteredTransactions
      };
    } catch (error) {
      console.error('Failed to search transactions:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to search transactions',
        data: []
      };
    }
  },

  // Add new transaction
  addTransaction: async (transactionData) => {
    try {
      const response = await moneyService.addTransaction(transactionData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Failed to add transaction:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to add transaction'
      };
    }
  }
};
