import React, { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { AtSign, Lock, Eye, EyeOff, Plus, ArrowLeft, Shield, Smartphone, Monitor } from 'lucide-react';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/services';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    // Simple client-side logging
    console.info(`[Auth] Login attempt started for user: ${username} at ${new Date().toISOString()}`);

    try {
      await login(username, password);
      console.info(`[Auth] Login successful for user: ${username}`);
      navigate(from, { replace: true });
    } catch (err) {
      console.error(`[Auth] Login failed for user: ${username}`, err);
      setError(err.response?.data?.error || 'Failed to login. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="webapp-auth-container">
      <style>{`
        .webapp-auth-container {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 1rem;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          position: relative;
          overflow: hidden;
        }

        .webapp-auth-container::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
          pointer-events: none;
        }

        .auth-card {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(20px);
          border-radius: 20px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
          width: 100%;
          max-width: 480px;
          padding: 2.5rem;
          position: relative;
          z-index: 1;
          border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .auth-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .auth-icon-wrapper {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 80px;
          height: 80px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 20px;
          margin-bottom: 1.5rem;
          box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
          position: relative;
          overflow: hidden;
        }

        .auth-icon-wrapper::before {
          content: '';
          position: absolute;
          top: -50%;
          left: -50%;
          width: 200%;
          height: 200%;
          background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
          transform: rotate(45deg);
          animation: shimmer 3s infinite;
        }

        @keyframes shimmer {
          0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
          100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }

        .auth-icon {
          color: white;
          position: relative;
          z-index: 1;
        }

        .auth-title {
          font-size: 2rem;
          font-weight: 700;
          color: #2d3748;
          margin: 0 0 0.5rem 0;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .auth-subtitle {
          color: #718096;
          font-size: 1.1rem;
          margin: 0;
          font-weight: 400;
        }

        .error-message {
          background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
          color: white;
          padding: 1rem;
          border-radius: 12px;
          margin-bottom: 1.5rem;
          font-size: 0.95rem;
          border: 1px solid rgba(255, 255, 255, 0.2);
          box-shadow: 0 4px 15px rgba(255, 107, 107, 0.2);
          animation: slideDown 0.3s ease-out;
        }

        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .input-group {
          margin-bottom: 1.5rem;
        }

        .input-group label {
          display: block;
          margin-bottom: 0.5rem;
          color: #4a5568;
          font-weight: 600;
          font-size: 0.95rem;
        }

        .input-wrapper {
          position: relative;
          display: flex;
          align-items: center;
        }

        .input-wrapper input {
          flex: 1;
          padding: 1rem 1rem 1rem 3rem;
          border: 2px solid #e2e8f0;
          border-radius: 12px;
          font-size: 1rem;
          transition: all 0.3s ease;
          background: rgba(255, 255, 255, 0.8);
          backdrop-filter: blur(10px);
        }

        .input-wrapper input:focus {
          outline: none;
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
          background: rgba(255, 255, 255, 0.95);
        }

        .input-wrapper input::placeholder {
          color: #a0aec0;
        }

        .input-icon {
          position: absolute;
          left: 1rem;
          color: #a0aec0;
          pointer-events: none;
          z-index: 1;
        }

        .password-toggle {
          position: absolute;
          right: 1rem;
          background: none;
          border: none;
          color: #a0aec0;
          cursor: pointer;
          padding: 0.5rem;
          border-radius: 8px;
          transition: all 0.2s ease;
          z-index: 1;
        }

        .password-toggle:hover {
          background: rgba(102, 126, 234, 0.1);
          color: #667eea;
        }

        .forgot-password {
          display: inline-block;
          color: #667eea;
          text-decoration: none;
          font-size: 0.9rem;
          font-weight: 500;
          margin-bottom: 1.5rem;
          transition: color 0.2s ease;
        }

        .forgot-password:hover {
          color: #5a67d8;
          text-decoration: underline;
        }

        .btn-primary {
          width: 100%;
          padding: 1rem 2rem;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          border-radius: 12px;
          font-size: 1.1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
          position: relative;
          overflow: hidden;
        }

        .btn-primary::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
          transition: left 0.5s ease;
        }

        .btn-primary:hover::before {
          left: 100%;
        }

        .btn-primary:hover {
          transform: translateY(-2px);
          box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        }

        .btn-primary:active {
          transform: translateY(0);
        }

        .btn-primary:disabled {
          opacity: 0.7;
          cursor: not-allowed;
          transform: none;
        }

        .auth-footer {
          text-align: center;
          margin-top: 2rem;
          padding-top: 2rem;
          border-top: 1px solid #e2e8f0;
          color: #718096;
        }

        .auth-footer a {
          color: #667eea;
          text-decoration: none;
          font-weight: 600;
          transition: color 0.2s ease;
        }

        .auth-footer a:hover {
          color: #5a67d8;
          text-decoration: underline;
        }

        .back-to-home {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          color: #a0aec0;
          text-decoration: none;
          font-size: 0.9rem;
          margin-top: 1rem;
          transition: color 0.2s ease;
        }

        .back-to-home:hover {
          color: #667eea;
        }

        .features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 1rem;
          margin: 2rem 0;
        }

        .feature-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 1rem;
          background: rgba(102, 126, 234, 0.05);
          border-radius: 12px;
          border: 1px solid rgba(102, 126, 234, 0.1);
        }

        .feature-icon {
          width: 40px;
          height: 40px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          flex-shrink: 0;
        }

        .feature-text {
          font-size: 0.9rem;
          color: #4a5568;
          font-weight: 500;
        }

        /* Responsive Design */
        @media (max-width: 640px) {
          .webapp-auth-container {
            padding: 0.5rem;
          }

          .auth-card {
            padding: 2rem 1.5rem;
            margin: 0.5rem;
            border-radius: 16px;
          }

          .auth-title {
            font-size: 1.75rem;
          }

          .auth-subtitle {
            font-size: 1rem;
          }

          .auth-icon-wrapper {
            width: 70px;
            height: 70px;
          }

          .input-wrapper input {
            padding: 0.875rem 0.875rem 0.875rem 2.5rem;
            font-size: 0.95rem;
          }

          .input-icon {
            left: 0.875rem;
          }

          .password-toggle {
            right: 0.875rem;
          }

          .btn-primary {
            padding: 0.875rem 1.5rem;
            font-size: 1rem;
          }

          .features-grid {
            grid-template-columns: 1fr;
            gap: 0.75rem;
          }

          .feature-item {
            padding: 0.75rem;
          }
        }

        @media (max-width: 480px) {
          .auth-card {
            padding: 1.5rem 1rem;
            border-radius: 12px;
          }

          .auth-title {
            font-size: 1.5rem;
          }

          .auth-icon-wrapper {
            width: 60px;
            height: 60px;
          }

          .input-wrapper input {
            padding: 0.75rem 0.75rem 0.75rem 2.25rem;
            font-size: 0.9rem;
          }

          .input-icon {
            left: 0.75rem;
          }

          .password-toggle {
            right: 0.75rem;
            padding: 0.375rem;
          }

          .btn-primary {
            padding: 0.75rem 1rem;
            font-size: 0.95rem;
          }
        }

        @media (min-width: 768px) {
          .auth-card {
            max-width: 520px;
            padding: 3rem;
          }

          .features-grid {
            grid-template-columns: repeat(3, 1fr);
          }
        }

        @media (min-width: 1024px) {
          .webapp-auth-container {
            padding: 2rem;
          }

          .auth-card {
            max-width: 560px;
            padding: 3.5rem;
          }
        }

        /* Loading spinner */
        .btn-primary.loading::after {
          content: '';
          position: absolute;
          width: 20px;
          height: 20px;
          top: 50%;
          left: 50%;
          margin-left: -10px;
          margin-top: -10px;
          border: 2px solid transparent;
          border-top: 2px solid white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>

      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-icon-wrapper">
            <Plus className="auth-icon" size={32} strokeWidth={3} />
          </div>
          <h1 className="auth-title">Welcome Back</h1>
          <p className="auth-subtitle">Login to continue to ExpertEase</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="username">Username or Email</label>
            <div className="input-wrapper">
              <AtSign className="input-icon" size={20} />
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="Enter your username or email"
                autoComplete="username"
              />
            </div>
          </div>

          <div className="input-group">
            <label htmlFor="password">Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" size={20} />
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
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

          <Link to="#" className="forgot-password">Forgot Password?</Link>

          <button 
            type="submit" 
            className={`btn-primary ${isLoading ? 'loading' : ''}`} 
            disabled={isLoading}
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="features-grid">
          <div className="feature-item">
            <div className="feature-icon">
              <Shield size={20} />
            </div>
            <span className="feature-text">Secure Login</span>
          </div>
          <div className="feature-item">
            <div className="feature-icon">
              <Smartphone size={20} />
            </div>
            <span className="feature-text">Mobile Friendly</span>
          </div>
          <div className="feature-item">
            <div className="feature-icon">
              <Monitor size={20} />
            </div>
            <span className="feature-text">Web App Ready</span>
          </div>
        </div>

        <div className="auth-footer">
          Don't have an account? <Link to="/signup">Sign Up</Link>
          <div>
            <Link to="/" className="back-to-home">
              <ArrowLeft size={16} />
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
