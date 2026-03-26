import React from 'react';

const AppointmentCard = ({ appointment, onStatusChange }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'upcoming':
        return { bg: '#7C3AED', text: 'white' };
      case 'in_progress':
        return { bg: '#10B981', text: 'white' };
      case 'completed':
        return { bg: '#6B7280', text: 'white' };
      default:
        return { bg: '#7C3AED', text: 'white' };
    }
  };

  const getTypeIcon = (type) => {
    return type === 'video' ? '📹' : '🏥';
  };

  const getInitials = (name) => {
    return name ? name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) : 'P';
  };

  const statusColors = getStatusColor(appointment.status);

  return (
    <div 
      className="appointment-card"
      style={{
        background: 'white',
        borderRadius: '12px',
        padding: '16px',
        marginBottom: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
        border: '1px solid #f0f0f0',
        transition: 'transform 0.2s ease, box-shadow 0.2s ease'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-1px)';
        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.10)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)';
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Avatar */}
        <div style={{
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #7C3AED, #9333EA)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontWeight: '600',
          fontSize: '16px',
          flexShrink: 0
        }}>
          {getInitials(appointment.patient_name)}
        </div>

        {/* Patient Info */}
        <div style={{ flex: 1 }}>
          <div style={{
            fontSize: '16px',
            fontWeight: '600',
            color: '#1a1a2e',
            marginBottom: '4px'
          }}>
            {appointment.patient_name}
          </div>
          
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '4px'
          }}>
            <span style={{ fontSize: '14px', color: '#6b7280' }}>
              {getTypeIcon(appointment.type)} {appointment.type === 'video' ? 'Video Call' : 'In-Person'}
            </span>
          </div>
          
          {appointment.reason && (
            <div style={{
              fontSize: '13px',
              color: '#9ca3af',
              fontStyle: 'italic'
            }}>
              {appointment.reason}
            </div>
          )}
        </div>

        {/* Time and Status */}
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'flex-end',
          gap: '8px'
        }}>
          <div style={{
            fontSize: '16px',
            fontWeight: '600',
            color: '#1a1a2e'
          }}>
            {appointment.time}
          </div>
          
          <div style={{
            padding: '4px 12px',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: '500',
            background: statusColors.bg,
            color: statusColors.text,
            textTransform: 'capitalize'
          }}>
            {appointment.status.replace('_', ' ')}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AppointmentCard;
