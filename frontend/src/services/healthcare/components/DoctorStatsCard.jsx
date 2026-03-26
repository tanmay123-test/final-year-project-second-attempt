import React from 'react';

const DoctorStatsCard = ({ icon, number, label, isTopCard = false }) => {
  return (
    <div 
      className={`doctor-stats-card ${isTopCard ? 'top-card' : 'bottom-card'}`}
      style={{
        background: 'white',
        borderRadius: '16px',
        padding: '20px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        border: '1px solid #f0f0f0',
        transition: 'transform 0.2s ease, box-shadow 0.2s ease'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.12)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
      }}
    >
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '12px',
        marginBottom: '8px'
      }}>
        <span style={{ 
          fontSize: '24px', 
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '48px',
          height: '48px',
          background: '#EDE9FE',
          borderRadius: '12px'
        }}>
          {icon}
        </span>
        <div>
          <div style={{ 
            fontSize: '28px', 
            fontWeight: '700', 
            color: '#1a1a2e',
            lineHeight: '1'
          }}>
            {number}
          </div>
          <div style={{ 
            fontSize: '14px', 
            color: '#6b7280',
            marginTop: '4px'
          }}>
            {label}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DoctorStatsCard;
