import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Wallet, TrendingUp, TrendingDown, Clock, Shield, Search, IndianRupee, CreditCard, ArrowUpRight, ArrowDownLeft } from 'lucide-react';
import api from '../../../shared/api';
import '../styles/FreelancerDashboard.css';

const FreelanceWalletPage = () => {
  const navigate = useNavigate();
  const [wallet, setWallet] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWalletData();
  }, []);

  const fetchWalletData = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/freelance/wallet');
      setWallet(response.data.wallet);
    } catch (err) {
      console.error('Error fetching wallet data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return (
    <div className="loading-overlay">
      <div className="spinner"></div>
      <p>Loading your wallet...</p>
    </div>
  );

  return (
    <div className="project-detail-container">
      <button className="back-btn" onClick={() => navigate(-1)}>
        <ArrowLeft size={18} /> Back
      </button>

      <header className="detail-header" style={{ marginBottom: '2.5rem' }}>
        <div className="header-main">
          <h1 style={{ fontSize: '2.2rem', marginBottom: '0.5rem' }}>My Wallet</h1>
          <p style={{ color: '#6b7280' }}>Manage your earnings, project payments, and escrow</p>
        </div>
        <button className="action-btn-purple" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <CreditCard size={18} /> Withdraw Funds
        </button>
      </header>

      {wallet && (
        <>
          <div className="stats-grid" style={{ marginBottom: '3rem' }}>
            <div className="stat-card" style={{ borderBottom: '4px solid #10b981' }}>
              <div className="stat-icon" style={{ backgroundColor: '#f0fdf4', color: '#10b981' }}>
                <TrendingUp size={20} />
              </div>
              <div className="stat-info">
                <p>Total Earned</p>
                <h3 style={{ color: '#10b981' }}>₹{wallet.total_earned?.toLocaleString() || 0}</h3>
              </div>
            </div>
            <div className="stat-card" style={{ borderBottom: '4px solid #ef4444' }}>
              <div className="stat-icon" style={{ backgroundColor: '#fef2f2', color: '#ef4444' }}>
                <TrendingDown size={20} />
              </div>
              <div className="stat-info">
                <p>Total Spent</p>
                <h3 style={{ color: '#ef4444' }}>₹{wallet.total_spent?.toLocaleString() || 0}</h3>
              </div>
            </div>
            <div className="stat-card" style={{ borderBottom: '4px solid #f59e0b' }}>
              <div className="stat-icon" style={{ backgroundColor: '#fffbeb', color: '#f59e0b' }}>
                <Shield size={20} />
              </div>
              <div className="stat-info">
                <p>In Escrow</p>
                <h3 style={{ color: '#f59e0b' }}>₹{wallet.pending_payments?.toLocaleString() || 0}</h3>
              </div>
            </div>
            <div className="stat-card" style={{ borderBottom: '4px solid #9B59B6' }}>
              <div className="stat-icon" style={{ backgroundColor: '#f5f3ff', color: '#9B59B6' }}>
                <Wallet size={20} />
              </div>
              <div className="stat-info">
                <p>Available Balance</p>
                <h3>₹{(wallet.total_earned - wallet.total_spent)?.toLocaleString() || 0}</h3>
              </div>
            </div>
          </div>

          <section className="transactions-section">
            <h3 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <Clock size={22} color="#9B59B6" /> Recent Transactions
            </h3>
            
            <div className="info-card" style={{ padding: 0, overflow: 'hidden' }}>
              {wallet.recent_transactions?.length === 0 ? (
                <div className="empty-state-dashboard" style={{ border: 'none' }}>
                  <Search size={40} color="#cbd5e1" />
                  <p>No transactions found in your history.</p>
                </div>
              ) : (
                <div className="transactions-list">
                  {wallet.recent_transactions.map((tx, index) => {
                    const isEarned = tx.type === 'EARNING' || (tx.amount > 0 && tx.escrow_status === 'RELEASED');
                    return (
                      <div key={tx.id || index} className="transaction-item" style={{ 
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                        padding: '1.5rem', borderBottom: index === wallet.recent_transactions.length - 1 ? 'none' : '1px solid #f3f4f6'
                      }}>
                        <div style={{ display: 'flex', gap: '1.2rem', alignItems: 'center' }}>
                          <div style={{ 
                            width: '44px', height: '44px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                            backgroundColor: isEarned ? '#f0fdf4' : '#fef2f2',
                            color: isEarned ? '#10b981' : '#ef4444'
                          }}>
                            {isEarned ? <ArrowDownLeft size={20} /> : <ArrowUpRight size={20} />}
                          </div>
                          <div>
                            <h5 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.2rem' }}>{tx.project_title || 'Freelance Payment'}</h5>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
                              <span style={{ fontSize: '0.85rem', color: '#9ca3af' }}>{new Date(tx.created_at).toLocaleDateString()}</span>
                              <span className={`status-badge-unified ${tx.escrow_status?.toLowerCase() || 'completed'}`} style={{ fontSize: '0.65rem', padding: '0.1rem 0.5rem' }}>
                                {tx.escrow_status || 'COMPLETED'}
                              </span>
                            </div>
                          </div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div style={{ 
                            fontSize: '1.1rem', fontWeight: 800, 
                            color: isEarned ? '#10b981' : '#ef4444'
                          }}>
                            {isEarned ? '+' : '-'} ₹{Math.abs(tx.amount).toLocaleString()}
                          </div>
                          <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                            {tx.type || (isEarned ? 'Credit' : 'Debit')}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </section>
        </>
      )}
    </div>
  );
};

export default FreelanceWalletPage;
