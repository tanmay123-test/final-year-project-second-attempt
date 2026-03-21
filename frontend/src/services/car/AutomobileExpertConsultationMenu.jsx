import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  FileText, 
  TrendingUp, 
  Award, 
  AlertTriangle, 
  BarChart3,
  ChevronRight
} from 'lucide-react';
import AutomobileExpertBottomNav from '../../components/AutomobileExpertBottomNav';

const AutomobileExpertConsultationMenu = () => {
  const navigate = useNavigate();

  const menuItems = [
    {
      id: 1,
      title: '📋 View Consultation History',
      description: 'View your completed consultation history',
      icon: FileText,
      path: '/worker/car/automobile-expert/consultation-history',
      color: '#2563eb'
    },
    {
      id: 2,
      title: '📈 View Performance Analytics',
      description: 'Track your performance metrics and trends',
      icon: TrendingUp,
      path: '/worker/car/automobile-expert/performance-analytics',
      color: '#16a34a'
    },
    {
      id: 3,
      title: '🏆 View Reputation & Badges',
      description: 'View your reputation, badges, and achievements',
      icon: Award,
      path: '/worker/car/automobile-expert/reputation',
      color: '#f59e0b'
    },
    {
      id: 4,
      title: '🚨 Report User',
      description: 'Report inappropriate or problematic user behavior',
      icon: AlertTriangle,
      path: '/worker/car/automobile-expert/report-user',
      color: '#dc2626'
    },
    {
      id: 5,
      title: '📊 View Queue Status',
      description: 'View real-time consultation queue information',
      icon: BarChart3,
      path: '/worker/car/automobile-expert/queue-status',
      color: '#8b5cf6'
    }
  ];

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f9fafb',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      paddingBottom: '80px'
    }}>
      {/* Header */}
      <div style={{
        backgroundColor: '#8b5cf6',
        color: 'white',
        padding: '16px 20px',
        boxShadow: '0 2px 4px rgba(139, 92, 246, 0.1)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={() => navigate('/worker/car/automobile-expert/homepage')}
            style={{
              background: 'none',
              border: 'none',
              color: 'white',
              cursor: 'pointer',
              padding: '4px',
              fontSize: '16px'
            }}
          >
            ← Back
          </button>
          <div>
            <h1 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>
              📊 Consultation History & Performance
            </h1>
            <p style={{ margin: 0, fontSize: '14px', opacity: 0.9 }}>
              Choose an option to view detailed information
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
        <div style={{ display: 'grid', gap: '16px' }}>
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => navigate(item.path)}
                style={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '12px',
                  padding: '20px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  transition: 'all 0.2s ease',
                  width: '100%',
                  textAlign: 'left'
                }}
                onMouseOver={(e) => {
                  e.target.style.backgroundColor = '#f8fafc';
                  e.target.style.borderColor = item.color;
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
                }}
                onMouseOut={(e) => {
                  e.target.style.backgroundColor = 'white';
                  e.target.style.borderColor = '#e5e7eb';
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = 'none';
                }}
              >
                <div style={{
                  width: '50px',
                  height: '50px',
                  borderRadius: '10px',
                  backgroundColor: item.color + '20',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  <Icon size={24} style={{ color: item.color }} />
                </div>
                
                <div style={{ flex: 1 }}>
                  <h3 style={{ 
                    margin: '0 0 4px 0', 
                    fontSize: '16px', 
                    fontWeight: '600', 
                    color: '#111827' 
                  }}>
                    {item.title}
                  </h3>
                  <p style={{ 
                    margin: 0, 
                    fontSize: '14px', 
                    color: '#6b7280' 
                  }}>
                    {item.description}
                  </p>
                </div>
                
                <ChevronRight size={20} style={{ color: '#9ca3af', flexShrink: 0 }} />
              </button>
            );
          })}
        </div>

        {/* Info Section */}
        <div style={{
          backgroundColor: '#f3e8ff',
          border: '1px solid #d8b4fe',
          borderRadius: '12px',
          padding: '20px',
          marginTop: '24px'
        }}>
          <h3 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: '600', color: '#7c3aed' }}>
            💡 About This Section
          </h3>
          <p style={{ margin: 0, fontSize: '14px', color: '#6d28d9', lineHeight: '1.6' }}>
            This section provides comprehensive insights into your consultation history, performance metrics, 
            reputation, and queue status. Track your progress, view earnings, manage reports, and monitor 
            real-time demand patterns.
          </p>
        </div>
      </div>

      <AutomobileExpertBottomNav />
    </div>
  );
};

export default AutomobileExpertConsultationMenu;
