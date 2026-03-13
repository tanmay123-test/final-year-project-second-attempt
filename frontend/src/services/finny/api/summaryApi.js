import { moneyService } from '../../../shared/api';

// Summary API service
export const summaryApi = {
  // Get summary analytics for current month
  getMonthlySummary: async (month = null) => {
    try {
      // Use the existing dashboard endpoint which has the summary data
      const response = await moneyService.getDashboardData();
      const backendData = response.data;
      
      // Transform backend data to match expected format
      const categories = backendData.categories || [];
      const totalSpent = backendData.total_spending || 0;
      
      // Calculate days in current month
      const currentDate = new Date();
      const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
      const dailyAverage = daysInMonth > 0 ? Math.round(totalSpent / daysInMonth) : 0;
      
      return {
        success: true,
        data: {
          categories: categories,
          totalSpent: totalSpent,
          dailyAverage: dailyAverage,
          month: backendData.month || currentDate.toISOString().slice(0, 7),
          daysInPeriod: daysInMonth
        }
      };
    } catch (error) {
      console.error('Failed to fetch summary:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to fetch summary',
        data: {
          categories: [],
          totalSpent: 0,
          dailyAverage: 0,
          month: new Date().toISOString().slice(0, 7),
          daysInPeriod: 30
        }
      };
    }
  },

  // Get summary for custom date range
  getDateRangeSummary: async (startDate, endDate) => {
    try {
      const response = await moneyService.getTransactions({
        start_date: startDate,
        end_date: endDate
      });
      
      const transactions = response.data.transactions || [];
      const totalSpent = transactions.reduce((sum, tx) => sum + (tx.amount || 0), 0);
      
      // Calculate days in period
      const start = new Date(startDate);
      const end = new Date(endDate);
      const daysInPeriod = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;
      
      // Group by category
      const categoryTotals = {};
      transactions.forEach(tx => {
        const category = tx.category || 'Other';
        categoryTotals[category] = (categoryTotals[category] || 0) + (tx.amount || 0);
      });
      
      const categories = Object.keys(categoryTotals).map(name => ({
        name,
        amount: categoryTotals[name]
      }));
      
      const dailyAverage = daysInPeriod > 0 ? Math.round(totalSpent / daysInPeriod) : 0;
      
      return {
        success: true,
        data: {
          categories,
          totalSpent,
          dailyAverage,
          startDate,
          endDate,
          daysInPeriod
        }
      };
    } catch (error) {
      console.error('Failed to fetch date range summary:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to fetch summary',
        data: null
      };
    }
  }
};
