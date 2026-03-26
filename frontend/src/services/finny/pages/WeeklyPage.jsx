import React, { useState, useEffect } from 'react';
import { Zap } from 'lucide-react';
import { analyticsApi } from '../api/analyticsApi';
import WeeklyBarChart from '../components/WeeklyBarChart';
import '../styles/AnalyticsPage.css';

const WeeklyPage = () => {
  const [loading, setLoading] = useState(true);
  const [weeklyData, setWeeklyData] = useState(null);

  // Default weekly data matching the design
  const defaultWeeklyData = [
    { day: 'Mon', amount: 450 },
    { day: 'Tue', amount: 320 },
    { day: 'Wed', amount: 680 },
    { day: 'Thu', amount: 200 },
    { day: 'Fri', amount: 540 },
    { day: 'Sat', amount: 880 }, // Peak day
    { day: 'Sun', amount: 330 }
  ];

  useEffect(() => {
    const loadWeeklyData = async () => {
      setLoading(true);
      try {
        // In a real app, fetch from analyticsApi
        const response = await analyticsApi.getAnalytics();
        if (response.success && response.data.weekly_spending) {
          // Process weekly data from API response
          const processedData = processWeeklyData(response.data.weekly_spending);
          setWeeklyData(processedData);
        } else {
          // Fall back to default data
          setWeeklyData(defaultWeeklyData);
        }
      } catch (error) {
        console.error('Failed to load weekly data:', error);
        // Fall back to default data
        setWeeklyData(defaultWeeklyData);
      } finally {
        setLoading(false);
      }
    };

    loadWeeklyData();
  }, []);

  // Process weekly data from API response
  const processWeeklyData = (apiData) => {
    // Convert API data format to our chart format
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    return days.map(day => ({
      day,
      amount: apiData[day] || 0
    }));
  };

  // Calculate summary statistics
  const calculateStats = (data) => {
    if (!data || data.length === 0) return { total: 0, peakDay: null, peakAmount: 0, spikePercent: 0 };
    
    const total = data.reduce((sum, item) => sum + item.amount, 0);
    const peakItem = data.reduce((max, item) => item.amount > max.amount ? item : max, data[0]);
    const average = total / data.length;
    const spikePercent = average > 0 ? Math.round(((peakItem.amount - average) / average) * 100) : 0;
    
    return {
      total,
      peakDay: peakItem.day,
      peakAmount: peakItem.amount,
      spikePercent
    };
  };

  const formatCurrency = (amount) => {
    return `₹${amount.toLocaleString()}`;
  };

  if (loading) {
    return (
      <div className="weekly-page">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading weekly data...</p>
        </div>
      </div>
    );
  }

  const stats = calculateStats(weeklyData);

  return (
    <div className="weekly-page">
      {/* Bar Chart Card */}
      <div className="chart-card">
        <h3 className="chart-title">This Week's Spending</h3>
        <WeeklyBarChart data={weeklyData || defaultWeeklyData} />
      </div>

      {/* Summary Cards Row */}
      <div className="summary-row">
        {/* Week Total Card */}
        <div className="summary-card">
          <div className="summary-label">Week Total</div>
          <div className="summary-value">{formatCurrency(stats.total)}</div>
        </div>

        {/* Peak Day Card */}
        <div className="summary-card">
          <div className="summary-label peak">Peak Day</div>
          <div className="summary-value peak">{stats.peakDay}</div>
        </div>
      </div>

      {/* Spending Spike Alert */}
      {stats.spikePercent > 50 && (
        <div className="alert-card">
          <div className="alert-header">
            <Zap className="alert-icon" size={18} />
            <span>Spending Spike Detected</span>
          </div>
          <div className="alert-body">
            {stats.peakDay} spending was {stats.spikePercent}% higher than your daily average. 
            Consider setting weekend spending alerts.
          </div>
        </div>
      )}
    </div>
  );
};

export default WeeklyPage;
