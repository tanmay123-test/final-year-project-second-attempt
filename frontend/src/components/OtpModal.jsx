import React, { useState } from 'react';
import { X, Check } from 'lucide-react';

const OtpModal = ({ isOpen, onClose, onSubmit, bookingId }) => {
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleChange = (element, index) => {
    // Only allow numbers
    if (!/^\d*$/.test(element.value)) return;

    const newOtp = [...otp];
    newOtp[index] = element.value;
    setOtp(newOtp);

    // Focus next input
    if (element.nextSibling && element.value) {
      element.nextSibling.focus();
    }
  };

  const handleKeyDown = (e, index) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      const newOtp = [...otp];
      newOtp[index - 1] = '';
      setOtp(newOtp);
      e.target.previousSibling.focus();
    }
  };

  const handleSubmit = async () => {
    const otpValue = otp.join('');
    if (otpValue.length !== 6) {
      setError('Please enter a complete 6-digit OTP');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await onSubmit(bookingId, otpValue);
      // Reset and close is handled by parent on success, or we do it here
    } catch (err) {
      setError(err.message || 'Verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        padding: '24px',
        width: '90%',
        maxWidth: '360px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.15)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold', color: '#1F2937' }}>Verify Job Completion</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#6B7280' }}>
            <X size={20} />
          </button>
        </div>

        <p style={{ fontSize: '14px', color: '#4B5563', marginBottom: '24px', textAlign: 'center' }}>
          Please ask the customer for the 6-digit OTP sent to their device to verify job completion.
        </p>

        <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', marginBottom: '24px' }}>
          {otp.map((digit, index) => (
            <input
              key={index}
              type="text"
              maxLength="1"
              value={digit}
              onChange={(e) => handleChange(e.target, index)}
              onKeyDown={(e) => handleKeyDown(e, index)}
              style={{
                width: '40px',
                height: '48px',
                fontSize: '20px',
                textAlign: 'center',
                border: '1px solid #D1D5DB',
                borderRadius: '8px',
                outline: 'none',
                backgroundColor: '#F9FAFB'
              }}
              onFocus={(e) => e.target.style.borderColor = '#8E44AD'}
              onBlur={(e) => e.target.style.borderColor = '#D1D5DB'}
            />
          ))}
        </div>

        {error && (
          <div style={{ color: '#EF4444', fontSize: '13px', textAlign: 'center', marginBottom: '16px' }}>
            {error}
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading}
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: '#8E44AD',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontWeight: '600',
            cursor: loading ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            opacity: loading ? 0.7 : 1
          }}
        >
          {loading ? 'Verifying...' : (
            <>
              <Check size={18} />
              Verify & Complete
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default OtpModal;
