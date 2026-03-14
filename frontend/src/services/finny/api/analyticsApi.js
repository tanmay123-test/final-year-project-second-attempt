import { moneyService } from '../../../shared/api';

// Analytics API service
export const analyticsApi = {
  // Get comprehensive analytics data
  getAnalytics: async () => {
    try {
      const response = await moneyService.getTransactions();
      const transactions = response.data.transactions || [];
      
      // Calculate weekly spending
      const weeklySpending = calculateWeeklySpending(transactions);
      
      // Calculate financial health score
      const healthScore = calculateFinancialHealthScore(transactions);
      const healthStatus = getHealthStatus(healthScore);
      const healthDescription = getHealthDescription(healthScore);
      
      // Calculate spending prediction
      const prediction = calculateSpendingPrediction(transactions);
      
      return {
        success: true,
        data: {
          weekly_spending: weeklySpending,
          financial_health_score: healthScore,
          health_status: healthStatus,
          health_description: healthDescription,
          prediction: prediction
        }
      };
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to fetch analytics',
        data: {
          weekly_spending: {},
          financial_health_score: 0,
          health_status: 'Poor',
          health_description: 'Unable to calculate financial health',
          prediction: { monthly_estimate: 0 }
        }
      };
    }
  }
};

// Helper functions
const calculateWeeklySpending = (transactions) => {
  const weeklySpending = {
    'Mon': 0,
    'Tue': 0,
    'Wed': 0,
    'Thu': 0,
    'Fri': 0,
    'Sat': 0,
    'Sun': 0
  };

  transactions.forEach(transaction => {
    if (transaction.date && transaction.amount) {
      const date = new Date(transaction.date);
      const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
      const amount = Math.abs(transaction.amount);
      
      if (weeklySpending.hasOwnProperty(dayName)) {
        weeklySpending[dayName] += amount;
      }
    }
  });

  return weeklySpending;
};

const calculateFinancialHealthScore = (transactions) => {
  if (!transactions || transactions.length === 0) return 0;
  
  // Calculate spending stability (consistency)
  const monthlyTotals = {};
  transactions.forEach(tx => {
    if (tx.date && tx.amount) {
      const month = tx.date.substring(0, 7); // YYYY-MM
      monthlyTotals[month] = (monthlyTotals[month] || 0) + Math.abs(tx.amount);
    }
  });
  
  const monthlyAmounts = Object.values(monthlyTotals);
  if (monthlyAmounts.length === 0) return 0;
  
  const average = monthlyAmounts.reduce((sum, amount) => sum + amount, 0) / monthlyAmounts.length;
  const variance = average > 0 ? monthlyAmounts.reduce((sum, amount) => sum + Math.pow(amount - average, 2), 0) / monthlyAmounts.length : 0;
  const stability = Math.max(0, 100 - (variance / (average * average)) * 100);
  
  // Calculate category distribution
  const categoryTotals = {};
  transactions.forEach(tx => {
    const category = tx.category || 'Other';
    categoryTotals[category] = (categoryTotals[category] || 0) + Math.abs(tx.amount);
  });
  
  const totalSpending = Object.values(categoryTotals).reduce((sum, amount) => sum + amount, 0);
  const categoryCount = Object.keys(categoryTotals).length;
  const idealDistribution = categoryCount > 0 ? totalSpending / categoryCount : 0;
  const categoryAmounts = Object.values(categoryTotals);
  const distributionScore = categoryAmounts.length > 0 ? 
    categoryAmounts.reduce((score, amount) => {
      const deviation = Math.abs(amount - idealDistribution);
      return score + Math.max(0, 100 - (deviation / idealDistribution) * 50);
    }, 0) / categoryCount : 0;
  
  // Calculate savings ratio (assuming income is 30% more than spending)
  const savingsRatio = totalSpending > 0 ? Math.min(50, (totalSpending * 0.3) / (totalSpending * 1.3)) : 0;
  
  // Calculate daily average consistency
  const dailySpending = {};
  transactions.forEach(tx => {
    if (tx.date && tx.amount) {
      const day = tx.date.substring(0, 10);
      dailySpending[day] = (dailySpending[day] || 0) + Math.abs(tx.amount);
    }
  });
  
  const dailyAmounts = Object.values(dailySpending);
  const dailyAverage = dailyAmounts.length > 0 ? 
    dailyAmounts.reduce((sum, amount) => sum + amount, 0) / dailyAmounts.length : 0;
  const dailyConsistency = dailyAverage > 0 ? 
    dailyAmounts.filter(amount => Math.abs(amount - dailyAverage) / dailyAverage <= 0.2).length / dailyAmounts.length : 0;
  
  // Final health score calculation
  const healthScore = Math.round(
    (stability * 0.3) +
    (distributionScore * 0.3) +
    (savingsRatio * 0.2) +
    (dailyConsistency * 100 * 0.2)
  );
  
  return Math.min(100, Math.max(0, healthScore));
};

const getHealthStatus = (score) => {
  if (score >= 80) return 'Excellent';
  if (score >= 60) return 'Good';
  if (score >= 40) return 'Fair';
  return 'Poor';
};

const getHealthDescription = (score) => {
  if (score >= 80) return 'Your spending is well-balanced. Keep up the great work!';
  if (score >= 60) return 'Your spending is reasonably balanced. Consider reducing dining out expenses.';
  if (score >= 40) return 'Your spending needs improvement. Focus on budgeting.';
  return 'Your spending requires immediate attention. Consider creating a strict budget.';
};

const calculateSpendingPrediction = (transactions) => {
  if (!transactions || transactions.length === 0) return { monthly_estimate: 0 };
  
  // Calculate average daily spending from last 30 days
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
  
  const recentTransactions = transactions.filter(tx => {
    if (tx.date) {
      const transactionDate = new Date(tx.date);
      return transactionDate >= thirtyDaysAgo;
    }
    return false;
  });
  
  if (recentTransactions.length === 0) return { monthly_estimate: 0 };
  
  const dailyTotal = recentTransactions.reduce((sum, tx) => sum + Math.abs(tx.amount), 0);
  const daysWithData = recentTransactions.reduce((days, tx) => {
    const day = tx.date;
    return days.has(day) ? days : days.add(day);
  }, new Set()).size;
  
  const averageDailySpending = daysWithData > 0 ? dailyTotal / daysWithData : 0;
  const monthlyEstimate = Math.round(averageDailySpending * 30);
  
  return { monthly_estimate: monthlyEstimate };
};
