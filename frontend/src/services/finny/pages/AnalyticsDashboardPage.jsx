import React, { useState, useEffect } from 'react';
import { ArrowLeft, BarChart3, Target, TrendingUp, Activity, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { analyticsApi } from '../api/analyticsApi';
import { moneyService } from '../../../shared/api';
import BudgetPage from './BudgetPage';
import Prediction from '../components/Prediction';
import FinancialHealth from '../components/FinancialHealth';
import WeeklyChart from '../components/WeeklyChart';
import '../styles/AnalyticsPage.css';

// Month abbreviation helper
const MONTH_ABBR = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

const getMonthAbbr = (yyyyMM) => {
  const parts = yyyyMM.split('-');
  const monthIndex = parseInt(parts[1], 10) - 1;
  return MONTH_ABBR[monthIndex] || yyyyMM;
};

// Custom SVG Line Chart
const CustomLineChart = ({ data }) => {
  if (!data || data.length === 0) return null;

  const maxValue = Math.max(...data.map(d => d.amount), 1);
  // Round up to nearest 6000 for clean Y axis
  const yMax = Math.ceil(maxValue / 6000) * 6000 || 24000;
  const yTicks = [0, yMax / 4, yMax / 2, (yMax * 3) / 4, yMax];

  const chartWidth = 400;
  const chartHeight = 200;
  const padding = { top: 20, right: 20, left: 50, bottom: 40 };

  const getX = (i) => {
    const w = chartWidth - padding.left - padding.right;
    return padding.left + (i * w) / Math.max(data.length - 1, 1);
  };

  const getY = (val) => {
    const h = chartHeight - padding.top - padding.bottom;
    return chartHeight - padding.bottom - (val / yMax) * h;
  };

  const linePath = data
    .map((pt, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(pt.amount)}`)
    .join(' ');

  return (
    <div style={{ width: '100%', height: '240px' }}>
      <svg width="100%" height="100%" viewBox={`0 0 ${chartWidth} ${chartHeight}`} preserveAspectRatio="none">
        {/* Grid lines */}
        {yTicks.map((val) => (
          <line
            key={val}
            x1={padding.left} x2={chartWidth - padding.right}
            y1={getY(val)} y2={getY(val)}
            stroke="#E5E7EB" strokeDasharray="4 4"
          />
        ))}

        {/* Axes */}
        <line x1={padding.left} x2={chartWidth - padding.right} y1={chartHeight - padding.bottom} y2={chartHeight - padding.bottom} stroke="#E5E7EB" />
        <line x1={padding.left} x2={padding.left} y1={padding.top} y2={chartHeight - padding.bottom} stroke="#E5E7EB" />

        {/* Y labels */}
        {yTicks.map((val) => (
          <text key={val} x={padding.left - 6} y={getY(val) + 4} textAnchor="end" fill="#9CA3AF" fontSize="10">
            {val >= 1000 ? `${val / 1000}k` : val}
          </text>
        ))}

        {/* X labels */}
        {data.map((pt, i) => (
          <text key={i} x={getX(i)} y={chartHeight - padding.bottom + 16} textAnchor="middle" fill="#9CA3AF" fontSize="10">
            {pt.month}
          </text>
        ))}

        {/* Line */}
        <path d={linePath} fill="none" stroke="#1a3a5c" strokeWidth="2.5" strokeLinejoin="round" />

        {/* Dots */}
        {data.map((pt, i) => (
          <circle key={i} cx={getX(i)} cy={getY(pt.amount)} r="5" fill="#F4B400" stroke="#fff" strokeWidth="2" />
        ))}
      </svg>
    </div>
  );
};

// Weekly inline view (no separate file needed)
const WeeklyView = ({ weeklySpending }) => (
  <div className="analytics-card">
    <WeeklyChart weeklySpending={weeklySpending} />
  </div>
);

const AnalyticsDashboardPage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [monthlyTrend, setMonthlyTrend] = useState([]);
  const [weeklySpending, setWeeklySpending] = useState({});

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Fetch monthly analytics from backend
      const [monthlyRes, txRes] = await Promise.allSettled([
        analyticsApi.getMonthlyAnalytics(6),
        moneyService.getTransactions()
      ]);

      // --- Monthly analytics ---
      if (monthlyRes.status === 'fulfilled' && monthlyRes.value.success) {
        const summary = monthlyRes.value.data.monthly_summary || [];

        // Build trend chart data (oldest → newest)
        const trend = [...summary]
          .sort((a, b) => a.month.localeCompare(b.month))
          .map(row => ({ month: getMonthAbbr(row.month), amount: row.expenses || 0 }));
        setMonthlyTrend(trend);

        // Derive stats
        const sorted = [...summary].sort((a, b) => b.month.localeCompare(a.month));
        const thisMonthData = sorted[0] || {};
        const lastMonthData = sorted[1] || {};

        const thisMonth = thisMonthData.expenses || 0;
        const lastMonth = lastMonthData.expenses || 0;
        const txCount = thisMonthData.transaction_count || 0;
        const lastTxCount = lastMonthData.transaction_count || 0;

        // Avg daily: days elapsed in current month
        const now = new Date();
        const daysElapsed = now.getDate();
        const avgDaily = daysElapsed > 0 ? Math.round(thisMonth / daysElapsed) : 0;

        const monthChange = lastMonth > 0 ? Math.round(((thisMonth - lastMonth) / lastMonth) * 100) : 0;
        const txChange = txCount - lastTxCount;

        setStats({ thisMonth, lastMonth, avgDaily, transactions: txCount, monthChange, txChange });
      } else {
        // Fallback
        setStats({ thisMonth: 0, lastMonth: 0, avgDaily: 0, transactions: 0, monthChange: 0, txChange: 0 });
      }

      // --- Weekly spending from transactions ---
      if (txRes.status === 'fulfilled') {
        const transactions = txRes.value.data.transactions || [];
        const weekly = { Mon: 0, Tue: 0, Wed: 0, Thu: 0, Fri: 0, Sat: 0, Sun: 0 };
        const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        const sevenDaysAgo = new Date();
        sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

        transactions.forEach(tx => {
          if (!tx.date || tx.type !== 'expense') return;
          const d = new Date(tx.date);
          if (d >= sevenDaysAgo) {
            const dayKey = dayNames[d.getDay()];
            weekly[dayKey] = (weekly[dayKey] || 0) + Math.abs(tx.amount);
          }
        });
        setWeeklySpending(weekly);
      }
    } catch (err) {
      console.error('Analytics load error:', err);
      setStats({ thisMonth: 0, lastMonth: 0, avgDaily: 0, transactions: 0, monthChange: 0, txChange: 0 });
    } finally {
      setLoading(false);
    }
  };

  const handleTabClick = (tab) => {
    setActiveTab(tab);
    if (tab === 'budget') navigate('/finny/budget');
  };

  const formatAmount = (val) => `₹${(val || 0).toLocaleString('en-IN')}`;

  if (loading) {
    return (
      <div className="analytics-page">
        <div className="adp-header">
          <button className="back-button" onClick={() => navigate('/finny')}><ArrowLeft size={20} /></button>
          <div className="header-text">
            <h1 className="header-title">Analytics Mode</h1>
            <p className="header-subtitle">Deep financial insights</p>
          </div>
        </div>
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-page">
      {/* Header */}
      <div className="adp-header">
        <button className="back-button" onClick={() => navigate('/finny')}><ArrowLeft size={20} /></button>
        <div className="header-text">
          <h1 className="header-title">Analytics Mode</h1>
          <p className="header-subtitle">Deep financial insights</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="adp-tabs-bar">
        <div className="tabs-container">
          {[
            { id: 'dashboard', label: 'Dashboard', Icon: BarChart3 },
            { id: 'budget',    label: 'Budget',    Icon: Target },
            { id: 'weekly',    label: 'Weekly',    Icon: TrendingUp },
            { id: 'predict',   label: 'Predict',   Icon: Activity },
            { id: 'health',    label: 'Health',    Icon: User },
          ].map(({ id, label, Icon }) => (
            <button
              key={id}
              className={`tab ${activeTab === id ? 'active' : ''}`}
              onClick={() => handleTabClick(id)}
            >
              <Icon size={15} />
              <span>{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="main-section">
        {activeTab === 'dashboard' && (
          <>
            {/* Stats Grid */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-label">This Month</div>
                <div className="stat-value">{formatAmount(stats?.thisMonth)}</div>
                {stats?.monthChange !== 0 && (
                  <div className={`stat-change ${stats?.monthChange < 0 ? 'positive' : 'negative'}`}>
                    {stats?.monthChange < 0 ? '' : '+'}{stats?.monthChange}%
                  </div>
                )}
              </div>
              <div className="stat-card">
                <div className="stat-label">Last Month</div>
                <div className="stat-value">{formatAmount(stats?.lastMonth)}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Avg Daily</div>
                <div className="stat-value">{formatAmount(stats?.avgDaily)}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Transactions</div>
                <div className="stat-value">{stats?.transactions || 0}</div>
                {stats?.txChange !== 0 && (
                  <div className={`stat-change ${stats?.txChange < 0 ? 'positive' : 'negative'}`}>
                    {stats?.txChange < 0 ? '' : '+'}{stats?.txChange}
                  </div>
                )}
              </div>
            </div>

            {/* Monthly Trend Chart */}
            <div className="charts-grid">
              <div className="analytics-card monthly-trend-card">
              <div className="chart-header">
                <h3>Monthly Trend</h3>
              </div>
              {monthlyTrend.length > 0 ? (
                <CustomLineChart data={monthlyTrend} />
              ) : (
                <div className="empty-chart-message" style={{ padding: '40px', textAlign: 'center', color: '#9CA3AF' }}>
                  No transaction data yet. Add transactions to see your trend.
                </div>
              )}
            </div>
            </div>
          </>
        )}

        {activeTab === 'weekly' && <WeeklyView weeklySpending={weeklySpending} />}
        {activeTab === 'predict' && <Prediction />}
        {activeTab === 'health' && <FinancialHealth />}
      </div>

    </div>
  );
};

export default AnalyticsDashboardPage;
