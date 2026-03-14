import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/api';
import { Mail, ArrowLeft, RotateCcw, CheckCircle, Loader2 } from 'lucide-react';

const VerifyEmail = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [email, setEmail] = useState(location.state?.email || '');
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [timer, setTimer] = useState(60);
  const [canResend, setCanResend] = useState(false);
  
  const inputRefs = useRef([]);

  useEffect(() => {
    if (!email) {
      navigate('/signup');
    }
    // Auto-focus first input
    if (inputRefs.current[0]) {
      inputRefs.current[0].focus();
    }
  }, [email, navigate]);

  useEffect(() => {
    let interval;
    if (timer > 0) {
      interval = setInterval(() => {
        setTimer((prev) => prev - 1);
      }, 1000);
    } else {
      setCanResend(true);
    }
    return () => clearInterval(interval);
  }, [timer]);

  const handleChange = (index, value) => {
    if (isNaN(value)) return;

    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Auto-tab to next input
    if (value !== '' && index < 5) {
      inputRefs.current[index + 1].focus();
    }
  };

  const handleKeyDown = (index, e) => {
    // Handle Backspace
    if (e.key === 'Backspace') {
      if (index > 0 && otp[index] === '') {
        inputRefs.current[index - 1].focus();
      }
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const data = e.clipboardData.getData('text').slice(0, 6).split('');
    const newOtp = [...otp];
    data.forEach((digit, index) => {
      if (index < 6 && !isNaN(digit)) {
        newOtp[index] = digit;
      }
    });
    setOtp(newOtp);
    // Focus the next empty input or the last one
    const nextEmptyIndex = newOtp.findIndex(val => val === '');
    const focusIndex = nextEmptyIndex === -1 ? 5 : nextEmptyIndex;
    inputRefs.current[focusIndex].focus();
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    const otpValue = otp.join('');
    if (otpValue.length !== 6) {
      setError('Please enter the complete 6-digit code');
      return;
    }

    setError('');
    setIsLoading(true);
    try {
      await authService.verifyOtp({ email, otp: otpValue });
      setSuccess('Email verified successfully!');
      setTimeout(() => navigate('/login'), 1500);
    } catch (err) {
      setError(err.response?.data?.error || 'Invalid OTP code. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    if (!canResend) return;
    
    setIsLoading(true);
    setError('');
    setSuccess('');
    try {
      // Assuming there's a resend endpoint or reusing signup to trigger OTP
      // For now, we'll simulate a resend call or use a specific endpoint if available
      // Ideally: await authService.resendOtp({ email });
      // Since we don't have explicit resend in api.js, we might need to add it or reuse signup logic carefully
      // Let's assume we can call a resend method. I'll need to check api.js or add it.
      // Checking previous api.js content... only signup, verifyOtp, login.
      // I should add resendOtp to api.js.
      await authService.resendOtp({ email });
      setTimer(60);
      setCanResend(false);
      setSuccess('New code sent!');
    } catch (err) {
      setError('Failed to resend code. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container-wrapper">
      <div className="auth-container otp-container">
        <div className="auth-header">
          <button onClick={() => navigate('/signup')} className="back-button-floating">
            <ArrowLeft size={20} />
          </button>
          <div className="auth-icon icon-purple">
            <Mail size={32} strokeWidth={2} color="white" />
          </div>
          <h2 className="auth-title">Verify Email</h2>
          <p className="auth-subtitle">
            We've sent a 6-digit code to <br />
            <span className="email-highlight">{email}</span>
          </p>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <form onSubmit={handleVerify} className="auth-form">
          <div className="otp-input-group">
            {otp.map((digit, index) => (
              <input
                key={index}
                ref={(el) => (inputRefs.current[index] = el)}
                type="text"
                maxLength={1}
                value={digit}
                onChange={(e) => handleChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                onPaste={handlePaste}
                className={`otp-input ${digit ? 'filled' : ''}`}
                inputMode="numeric"
                autoComplete="one-time-code"
              />
            ))}
          </div>

          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? (
              <><Loader2 className="animate-spin" size={20} /> Verifying...</>
            ) : (
              'Verify'
            )}
          </button>
        </form>

        <div className="auth-footer">
          <div className="resend-container">
            {canResend ? (
              <button onClick={handleResend} className="resend-button active" disabled={isLoading}>
                <RotateCcw size={16} /> Resend Code
              </button>
            ) : (
              <span className="resend-timer">
                Resend code in {timer}s
              </span>
            )}
          </div>
          <p className="change-email">
            Wrong email? <Link to="/signup">Change email address</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default VerifyEmail;
