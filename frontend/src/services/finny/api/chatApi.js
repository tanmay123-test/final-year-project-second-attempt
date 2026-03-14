import { moneyService } from '../../../shared/api';
import { chatParser } from './chatParser';

// Chat API service
export const chatApi = {
  // Parse and save transactions from chat input
  processChatInput: async (input) => {
    try {
      // Parse the natural language input
      const parsedTransactions = chatParser.parseInput(input);
      
      if (parsedTransactions.length === 0) {
        return {
          success: false,
          message: 'No valid transactions found. Try: "food 200 transport 150"'
        };
      }
      
      // Format for API
      const transactionsToSave = chatParser.formatForAPI(parsedTransactions);
      
      // Save each transaction
      const results = [];
      for (const transaction of transactionsToSave) {
        try {
          const result = await moneyService.addTransaction(transaction);
          results.push({
            success: true,
            merchant: transaction.merchant,
            category: transaction.category,
            amount: transaction.amount
          });
        } catch (error) {
          results.push({
            success: false,
            merchant: transaction.merchant,
            error: error.response?.data?.error || error.message
          });
        }
      }
      
      return {
        success: true,
        message: `Successfully added ${results.filter(r => r.success).length} transaction(s)`,
        results: results
      };
    } catch (error) {
      console.error('Failed to process chat input:', error);
      return {
        success: false,
        message: 'Failed to process your input. Please try again.',
        error: error.response?.data?.error || error.message
      };
    }
  },

  // Get today's summary
  getTodaySummary: async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const response = await moneyService.getTransactions({
        start_date: today,
        end_date: today
      });
      
      const transactions = response.data.transactions || [];
      const categories = {};
      let total = 0;
      
      transactions.forEach(tx => {
        const category = tx.category || 'Other';
        const amount = Math.abs(tx.amount || 0);
        
        categories[category] = (categories[category] || 0) + amount;
        total += amount;
      });
      
      return {
        success: true,
        data: {
          total,
          categories,
          date: today,
          transactionCount: transactions.length
        }
      };
    } catch (error) {
      console.error('Failed to get today summary:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message,
        data: {
          total: 0,
          categories: {},
          date: new Date().toISOString().split('T')[0],
          transactionCount: 0
        }
      };
    }
  }
};
