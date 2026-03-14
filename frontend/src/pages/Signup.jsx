import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/api';
import { User, AtSign, Mail, Lock, Eye, EyeOff, KeyRound } from 'lucide-react';

const Signup = () => {
  const [step, setStep] = useState(1); // 1: Signup, 2: Verify OTP
  const [formData, setFormData] = useState({
    name: '',
    username: '',
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      await authService.signup(formData);
      navigate('/verify-email', { state: { email: formData.email } });
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to sign up');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      await authService.verifyOtp({ email: formData.email, otp });
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.error || 'Invalid OTP');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container-wrapper">
      <div className="auth-container">
        <div className="auth-header">
        <h2 className="auth-title">{step === 1 ? 'Join ExpertEase' : 'Verify Email'}</h2>
        <p className="auth-subtitle">
          {step === 1 
            ? 'Create your account to get started' 
            : `We've sent a code to ${formData.email}`}
        </p>
      </div>

      {error && <div className="error-message">{error}</div>}
      
      {step === 1 ? (
        <form onSubmit={handleSignup}>
          <div className="input-group">
            <label>Full Name</label>
            <div className="input-wrapper">
              <User className="input-icon" size={20} />
              <input 
                name="name" 
                value={formData.name} 
                onChange={handleChange} 
                required 
                placeholder="John Doe" 
              />
            </div>
          </div>

          <div className="input-group">
            <label>Username</label>
            <div className="input-wrapper">
              <AtSign className="input-icon" size={20} />
              <input 
                name="username" 
                value={formData.username} 
                onChange={handleChange} 
                required 
                placeholder="johndoe123" 
              />
            </div>
          </div>

          <div className="input-group">
            <label>Email</label>
            <div className="input-wrapper">
              <Mail className="input-icon" size={20} />
              <input 
                type="email" 
                name="email" 
                value={formData.email} 
                onChange={handleChange} 
                required 
                placeholder="john@example.com" 
              />
            </div>
          </div>

          <div className="input-group">
            <label>Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" size={20} />
              <input 
                type={showPassword ? "text" : "password"} 
                name="password" 
                value={formData.password} 
                onChange={handleChange} 
                required 
                placeholder="••••••••" 
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? 'Creating Account...' : 'Sign Up'}
          </button>
        </form>
      ) : (
        <form onSubmit={handleVerify}>
          <div className="input-group">
            <label>One-Time Password</label>
            <div className="input-wrapper">
              <KeyRound className="input-icon" size={20} />
              <input 
                value={otp} 
                onChange={(e) => setOtp(e.target.value)} 
                required 
                placeholder="Enter 6-digit code" 
                maxLength={6}
              />
            </div>
          </div>
          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? 'Verifying...' : 'Verify & Login'}
          </button>
        </form>
      )}
      
      <div className="auth-footer">
        {step === 1 && (
          <>
            Already have an account? <Link to="/login">Login</Link>
          </>
        )}
        <div style={{ marginTop: '1rem' }}>
          <Link to="/" style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 'normal' }}>
            ← Back to Home
          </Link>
        </div>
      </div>
      </div>
    </div>
  );
};

export default Signup;
