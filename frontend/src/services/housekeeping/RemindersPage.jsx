import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Bell, Calendar, CheckCircle2, AlertCircle, Clock } from 'lucide-react';
import api from '../../shared/api';
import { useAuth } from '../../context/AuthContext';
import './RemindersPage.css';

const RemindersPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [reminders, setReminders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReminders = async () => {
      // Use user.id or user.user_id as fallback
      const userId = user?.id || user?.user_id;
      
      if (!userId) {
        setLoading(false);
        return;
      }

      try {
        const response = await api.get(`/api/ai/recommendations?user_id=${userId}`);
        setReminders(response.data);
      } catch (error) {
        console.error('Failed to fetch reminders:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchReminders();
  }, [user]);

  const getUrgencyIcon = (urgency) => {
    switch (urgency) {
      case 'HIGH': return <AlertCircle size={20} color="#EF4444" />;
      case 'MEDIUM': return <Clock size={20} color="#F59E0B" />;
      default: return <CheckCircle2 size={20} color="#10B981" />;
    }
  };

  return (
    <div className="reminders-page">
      {/* Header */}
      <header className="reminders-header">
        <div className="header-left">
          <button className="icon-btn-circle" onClick={() => navigate(-1)}>
            <ArrowLeft size={20} color="white" />
          </button>
        </div>
        
        <div className="header-center">
          <h1>Hygiene Reminders</h1>
          <p>Stay on top of your home care</p>
        </div>

        <div className="header-right">
          <div className="icon-btn-circle active">
            <Bell size={20} color="white" />
          </div>
        </div>
      </header>

      {/* Body */}
      <main className="reminders-body">
        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Analyzing your home hygiene...</p>
          </div>
        ) : reminders.length === 0 ? (
          <div className="empty-reminders">
            <CheckCircle2 size={60} color="#8E44AD" opacity={0.2} />
            <h3>All Caught Up!</h3>
            <p>Your home hygiene scores are looking great.</p>
          </div>
        ) : (
          <div className="reminders-list">
            <div className="reminders-section-title">
              <h2>Smart Suggestions</h2>
              <span>Based on your history</span>
            </div>

            {reminders.map((item, idx) => (
              <div key={idx} className={`reminder-card ${item.urgency.toLowerCase()}`}>
                <div className="reminder-icon">
                  {getUrgencyIcon(item.urgency)}
                </div>
                
                <div className="reminder-content">
                  <div className="reminder-header">
                    <h3>{item.service}</h3>
                    <span className="urgency-tag">{item.urgency}</span>
                  </div>
                  
                  <p className="reminder-msg">{item.message}</p>
                  
                  <div className="reminder-footer">
                    <div className="hygiene-score-mini">
                      <span className="label">Hygiene Score</span>
                      <div className="score-bar-bg">
                        <div 
                          className="score-bar-fill" 
                          style={{ 
                            width: `${item.score * 10}%`,
                            backgroundColor: item.score < 3 ? '#EF4444' : item.score < 7 ? '#F59E0B' : '#10B981'
                          }}
                        ></div>
                      </div>
                      <span className="score-val">{item.score}/10</span>
                    </div>
                    
                    <button 
                      className="book-shortcut-btn"
                      onClick={() => navigate('/housekeeping/booking/create', { state: { service: item.service } })}
                    >
                      Book Now
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default RemindersPage;
