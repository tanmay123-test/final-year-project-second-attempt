import React from 'react';
import { DollarSign, TrendingUp, Calendar } from 'lucide-react';
import ProviderBottomNav from '../../../components/ProviderBottomNav';

const ProviderEarnings = () => {
  const earnings = {
    today: 1200,
    week: 4500,
    month: 18200,
    history: [
      { id: 1, date: 'Today', amount: 1200, jobs: 1 },
      { id: 2, date: 'Yesterday', amount: 800, jobs: 2 },
      { id: 3, date: 'Feb 12', amount: 1500, jobs: 3 },
    ]
  };

  return (
    <div style={{ backgroundColor: '#F9FAFB', minHeight: '100vh', paddingBottom: '80px' }}>
      <div style={{ backgroundColor: '#8E44AD', padding: '20px', margin: '-20px -20px 20px -20px', borderBottomLeftRadius: '24px', borderBottomRightRadius: '24px', color: 'white' }}>
        <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>Earnings</h1>
        <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <span style={{ fontSize: '14px', opacity: 0.9 }}>Total Balance</span>
            <div style={{ fontSize: '32px', fontWeight: 'bold' }}>₹{earnings.month}</div>
          </div>
          <div style={{ backgroundColor: 'rgba(255,255,255,0.2)', padding: '8px 12px', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <TrendingUp size={16} />
            <span style={{ fontSize: '12px', fontWeight: 'bold' }}>+12%</span>
          </div>
        </div>
      </div>

      <div style={{ padding: '0 20px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
          <div style={{ backgroundColor: 'white', padding: '16px', borderRadius: '16px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
            <div style={{ color: '#6B7280', fontSize: '12px', marginBottom: '8px' }}>Today</div>
            <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#1F2937' }}>₹{earnings.today}</div>
          </div>
          <div style={{ backgroundColor: 'white', padding: '16px', borderRadius: '16px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
            <div style={{ color: '#6B7280', fontSize: '12px', marginBottom: '8px' }}>This Week</div>
            <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#1F2937' }}>₹{earnings.week}</div>
          </div>
        </div>

        <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#1F2937', marginBottom: '16px' }}>Transaction History</h3>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {earnings.history.map(item => (
            <div key={item.id} style={{ backgroundColor: 'white', padding: '16px', borderRadius: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid #F3F4F6' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ width: '40px', height: '40px', backgroundColor: '#F3E5F5', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#8E44AD' }}>
                  <DollarSign size={20} />
                </div>
                <div>
                  <div style={{ fontWeight: '600', color: '#1F2937' }}>Payout</div>
                  <div style={{ fontSize: '12px', color: '#6B7280' }}>{item.date} • {item.jobs} jobs</div>
                </div>
              </div>
              <span style={{ fontWeight: 'bold', color: '#8E44AD' }}>+₹{item.amount}</span>
            </div>
          ))}
        </div>
      </div>

      <ProviderBottomNav />
    </div>
  );
};

export default ProviderEarnings;
