import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Wrench, Mail, Phone, MapPin, Calendar, Award, FileText, User, Lock, Eye, EyeOff, AlertCircle, CheckCircle, Camera, Upload, ArrowLeft } from 'lucide-react';

const MechanicAuth = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const isLogin = location.pathname.includes('login');
  
  const [formData, setFormData] = useState({
    password: '',
    email: '',
    fullName: '',
    phone: '',
    age: '',
    city: '',
    address: '',
    experience: '',
    skills: '',
    aadhaarFile: null,
    licenseFile: null,
    certificateFile: null,
    profilePhotoFile: null
  });

  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showApprovalStatus, setShowApprovalStatus] = useState(false);
  const [signupData, setSignupData] = useState(null);
  const [showSecurityDeclaration, setShowSecurityDeclaration] = useState(false);
  const [securityAccepted, setSecurityAccepted] = useState('');
  const [securityInputValue, setSecurityInputValue] = useState('');

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleFileChange = (e) => {
    const { name, files } = e.target;
    setFormData({
      ...formData,
      [name]: files[0]
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Form submitted, isLogin:', isLogin);
    console.log('FormData:', formData);
    
    setLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/api/auth/car/mechanic/login' : '/api/auth/car/mechanic/signup';
      
      if (isLogin) {
        const payload = { email: formData.email, password: formData.password };
        
        const response = await fetch(`http://127.0.0.1:5000${endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload)
        });

        const data = await response.json();
        console.log('Login response status:', response.status);
        console.log('Login response data:', data);

        if (response.ok) {
          // Store token and user data
          localStorage.setItem('workerToken', data.token);
          localStorage.setItem('workerData', JSON.stringify(data.mechanic));
          
          // Show success message like CLI
          alert(`✅ Login successful! Welcome back, ${data.mechanic?.name || 'Mechanic'}!`);
          
          // Navigate to dashboard
          navigate('/worker/car/homepage');
        } else {
          console.log('Login failed - status:', response.status);
          console.log('Login failed - data:', data);
          // Check if it's an approval pending error
          if (data.requires_approval) {
            // Show approval pending message and freeze login
            setError('⏳ Your account is pending admin approval. Please wait for approval before logging in.');
            // Disable form inputs
            const inputs = document.querySelectorAll('input');
            inputs.forEach(input => input.disabled = true);
            // Disable submit button
            const submitBtn = document.querySelector('.submit-button');
            if (submitBtn) submitBtn.disabled = true;
          } else {
            console.error('Login error:', data);
            setError(data.error || 'Login failed');
          }
        }
      } else {
        // For signup, show security declaration first
        console.log('Setting showSecurityDeclaration to true for signup');
        setShowSecurityDeclaration(true);
      }
    } catch (err) {
      console.error('Form submission error:', err);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle security input change
  const handleSecurityInputChange = (e) => {
    const value = e.target.value.toUpperCase();
    setSecurityInputValue(value);
    setSecurityAccepted(value === 'YES');
  };

  // Handle actual form submission after security declaration
  const handleSecuritySubmit = async () => {
    console.log('Security submit clicked, securityAccepted:', securityAccepted);
    if (!securityAccepted) {
      setError('You must accept the security declaration to continue');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const endpoint = '/api/auth/car/mechanic/signup';
      const formDataToSend = new FormData();
      formDataToSend.append('full_name', formData.fullName);
      formDataToSend.append('email', formData.email);
      formDataToSend.append('phone', formData.phone);
      formDataToSend.append('password', formData.password);
      formDataToSend.append('age', formData.age);
      formDataToSend.append('city', formData.city);
      formDataToSend.append('address', formData.address);
      formDataToSend.append('experience', formData.experience);
      formDataToSend.append('skills', formData.skills);
      
      if (formData.aadhaarFile) {
        formDataToSend.append('aadhaar_file', formData.aadhaarFile);
      }
      if (formData.licenseFile) {
        formDataToSend.append('license_file', formData.licenseFile);
      }
      if (formData.certificateFile) {
        formDataToSend.append('certificate_file', formData.certificateFile);
      }
      if (formData.profilePhotoFile) {
        formDataToSend.append('profile_photo_file', formData.profilePhotoFile);
      }

      console.log('Sending FormData to:', endpoint);
      console.log('FormData contents:');
      for (let [key, value] of formDataToSend.entries()) {
        console.log(key, value);
      }

      const response = await fetch(`http://127.0.0.1:5000${endpoint}`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
        },
        body: formDataToSend
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      const data = await response.json();

      if (response.ok) {
        // Store signup data and show approval status
        setSignupData(data);
        setShowSecurityDeclaration(false);
        setShowApprovalStatus(true);
      } else {
        console.error('Signup error:', data);
        setError(data.error || 'Signup failed');
      }
    } catch (err) {
      console.error('Form submission error:', err);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    navigate(isLogin ? '/worker/car/mechanic/signup' : '/worker/car/mechanic/login');
  };

  return (
    <div className="mechanic-auth">
      {/* Back Button */}
      <button 
        type="button" 
        className="back-button"
        onClick={() => navigate('/worker/car/services')}
        style={{ position: 'absolute', top: '2rem', left: '2rem', zIndex: 10, background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: '50%', width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', cursor: 'pointer', backdropFilter: 'blur(10px)' }}
      >
        <ArrowLeft size={20} />
      </button>

      <div className="auth-container">

        {/* Form */}
        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="error-message">{error}</div>}

          {/* Common Fields */}
          <div className="form-group">
            <label htmlFor="email">
              <Mail size={18} />
              Email
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              placeholder="your@email.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              <Lock size={18} />
              Password
            </label>
            <div className="password-input">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                placeholder="Enter your password"
              />
              <button
                type="button"
                className="toggle-password"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          {/* Signup Only Fields */}
          {!isLogin && (
            <>
              <div className="form-group">
                <label htmlFor="fullName">Full Name</label>
                <input
                  type="text"
                  id="fullName"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleInputChange}
                  required
                  placeholder="John Doe"
                />
              </div>

              <div className="form-group">
                <label htmlFor="phone">
                  <Phone size={18} />
                  Phone Number
                </label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  required
                  placeholder="+1234567890"
                />
              </div>

              <div className="form-group">
                <label htmlFor="age">Age</label>
                <input
                  type="number"
                  id="age"
                  name="age"
                  value={formData.age}
                  onChange={handleInputChange}
                  required
                  placeholder="25"
                  min="18"
                  max="65"
                />
              </div>

              <div className="form-group">
                <label htmlFor="city">City</label>
                <input
                  type="text"
                  id="city"
                  name="city"
                  value={formData.city}
                  onChange={handleInputChange}
                  required
                  placeholder="Mumbai"
                />
              </div>

              <div className="form-group">
                <label htmlFor="address">Address</label>
                <input
                  type="text"
                  id="address"
                  name="address"
                  value={formData.address}
                  onChange={handleInputChange}
                  required
                  placeholder="Kannamwar Nagar, Vikhroli East, Mumbai - 400083"
                />
              </div>

              <div className="form-group">
                <label htmlFor="experience">Experience (years)</label>
                <input
                  type="number"
                  id="experience"
                  name="experience"
                  value={formData.experience}
                  onChange={handleInputChange}
                  required
                  placeholder="4"
                  min="1"
                />
              </div>

              <div className="form-group">
                <label htmlFor="skills">Skills (comma separated)</label>
                <input
                  type="text"
                  id="skills"
                  name="skills"
                  value={formData.skills}
                  onChange={handleInputChange}
                  required
                  placeholder="good mechanic, build expert"
                />
              </div>

              {/* Document Uploads */}
              <div className="form-group">
                <label>
                  <FileText size={18} />
                  Aadhaar Card
                </label>
                <input
                  type="file"
                  name="aadhaarFile"
                  onChange={handleFileChange}
                  accept="image/*,.pdf"
                  required
                />
                {formData.aadhaarFile && (
                  <div className="file-preview">
                    Selected: {formData.aadhaarFile.name}
                  </div>
                )}
              </div>

              <div className="form-group">
                <label>
                  <FileText size={18} />
                  License Certificate
                </label>
                <input
                  type="file"
                  name="licenseFile"
                  onChange={handleFileChange}
                  accept="image/*,.pdf"
                  required
                />
                {formData.licenseFile && (
                  <div className="file-preview">
                    Selected: {formData.licenseFile.name}
                  </div>
                )}
              </div>

              <div className="form-group">
                <label>
                  <FileText size={18} />
                  Work Certificate
                </label>
                <input
                  type="file"
                  name="certificateFile"
                  onChange={handleFileChange}
                  accept="image/*,.pdf"
                  required
                />
                {formData.certificateFile && (
                  <div className="file-preview">
                    Selected: {formData.certificateFile.name}
                  </div>
                )}
              </div>

              <div className="form-group">
                <label>
                  <Camera size={18} />
                  Profile Photo
                </label>
                <input
                  type="file"
                  name="profilePhotoFile"
                  onChange={handleFileChange}
                  accept="image/*"
                  required
                />
                {formData.profilePhotoFile && (
                  <div className="file-preview">
                    Selected: {formData.profilePhotoFile.name}
                  </div>
                )}
              </div>

              </>
          )}

          {/* Security Declaration - Only for Signup */}
          {!isLogin && showSecurityDeclaration && (
            console.log('Rendering security declaration - isLogin:', isLogin, 'showSecurityDeclaration:', showSecurityDeclaration) || (
            <div className="security-declaration">
              <h4>🔒 SECURITY DECLARATION</h4>
              <p>I confirm all documents are valid and I agree to platform policies</p>
              <p>(Type YES in any case: yes, YES, Yes)</p>
              <div className="security-input">
                <input
                  type="text"
                  value={securityInputValue}
                  onChange={handleSecurityInputChange}
                  placeholder="Type YES to continue"
                  style={{ textTransform: 'uppercase' }}
                />
              </div>

              <button 
                type="button"
                className="submit-button security-submit"
                onClick={handleSecuritySubmit}
                disabled={loading || !securityAccepted}
              >
                {loading ? 'Processing...' : 'Submit Application'}
              </button>
            </div>
            )
          )}

          {/* Submit Button - Only show if not showing security declaration */}
          {!showSecurityDeclaration && (
            <button 
              type="submit" 
              className="submit-button" 
              disabled={loading}
            >
              {loading ? 'Processing...' : (isLogin ? 'Login' : 'Sign Up')}
            </button>
          )}
        </form>

        {/* Approval Status Modal */}
        {showApprovalStatus && signupData && (
          <div className="approval-overlay">
            <div className="approval-modal">
              <div className="approval-header">
                <div className="approval-icon">✅</div>
                <h2>Worker Signup Successful!</h2>
              </div>
              
              <div className="approval-content">
                <div className="approval-details">
                  <h3>APPROVAL STATUS</h3>
                  <div className="status-item">
                    <span className="status-label">Worker ID:</span>
                    <span className="status-value">#{signupData.worker_id || signupData.mechanic_id || '1'}</span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Status:</span>
                    <span className="status-value pending">PENDING ADMIN APPROVAL</span>
                  </div>
                </div>
                
                <div className="approval-info">
                  <h4>📋 Your account has been submitted for admin review</h4>
                  <p>Expected approval time: 2-24 hours</p>
                  <p>You will receive a notification once approved</p>
                  <p>After approval, you can login and access your dashboard</p>
                  <p>For urgent inquiries, contact support</p>
                </div>
                
                <div className="approval-actions">
                  <button 
                    className="approval-button primary"
                    onClick={() => {
                      setShowApprovalStatus(false);
                      navigate('/worker/car/mechanic/login');
                    }}
                  >
                    Go to Login
                  </button>
                  <button 
                    className="approval-button secondary"
                    onClick={() => setShowApprovalStatus(false)}
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Toggle Mode */}
        <div className="auth-toggle">
          <p>
            {isLogin ? "Don't have an account?" : "Already have an account?"}
            <button type="button" onClick={toggleMode} className="toggle-link">
              {isLogin ? 'Sign Up' : 'Login'}
            </button>
          </p>
        </div>

        {/* Back button has been moved to top right */}
      </div>

      <style>{`
        .mechanic-auth {
          min-height: 100vh;
          background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 1rem;
          position: relative;
        }

        .auth-container {
          background: rgba(59, 130, 246, 0.1);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(59, 130, 246, 0.3);
          border-radius: 24px;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
          padding: 2rem;
          max-width: 600px;
          width: 90%;
          position: relative;
        }

        .auth-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .auth-header h1 {
          color: white;
          font-size: 2rem;
          font-weight: bold;
          margin-bottom: 0.5rem;
          text-shadow: none;
        }

        .auth-header p {
          color: rgba(255, 255, 255, 0.8);
          margin: 0;
        }

        .icon-wrapper {
          width: 80px;
          height: 80px;
          background: rgba(191, 219, 254, 0.8);
          border: 2px solid rgba(147, 197, 253, 0.6);
          backdrop-filter: blur(10px);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 1.5rem;
          box-shadow: 0 8px 25px rgba(147, 197, 253, 0.3);
        }

        .icon-wrapper svg {
          color: #1E40AF;
        }

        .auth-form {
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
        }

        .error-message {
          background: #fee;
          color: #c33;
          padding: 0.75rem;
          border-radius: 8px;
          font-size: 0.9rem;
        }

        .form-group {
          display: flex;
          flex-direction: column;
        }

        .form-group label {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: white;
          font-weight: 500;
          margin-bottom: 0.5rem;
          font-size: 0.95rem;
        }

        .form-group input {
          padding: 0.875rem;
          border: 1px solid rgba(255, 255, 255, 0.3);
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          border-radius: 12px;
          font-size: 1rem;
          color: white;
          transition: all 0.2s;
        }

        .form-group input::placeholder {
          color: rgba(255, 255, 255, 0.7);
        }

        .form-group input:focus {
          outline: none;
          border-color: rgba(255, 255, 255, 0.5);
          background: rgba(255, 255, 255, 0.15);
        }

        .form-group input[type="file"] {
          padding: 0.75rem;
          border: 2px dashed rgba(255, 255, 255, 0.3);
          background: rgba(255, 255, 255, 0.05);
          backdrop-filter: blur(10px);
          border-radius: 8px;
          cursor: pointer;
          color: white;
          transition: all 0.2s;
        }

        .form-group input[type="file"]:hover {
          border-color: rgba(255, 255, 255, 0.5);
          background: rgba(255, 255, 255, 0.1);
        }

        .file-preview {
          margin-top: 0.5rem;
          padding: 0.5rem;
          background: #e8f5e8;
          border-radius: 6px;
          font-size: 0.85rem;
          color: #2d3748;
        }

        /* Approval Modal Styles */
        .approval-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.8);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .approval-modal {
          background: white;
          border-radius: 20px;
          padding: 2.5rem;
          max-width: 500px;
          width: 90%;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
          animation: slideIn 0.3s ease-out;
        }

        .approval-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .approval-icon {
          width: 60px;
          height: 60px;
          background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 1rem;
          font-size: 2rem;
          color: white;
        }

        .approval-header h2 {
          margin: 0;
          color: #1a1a1a;
          font-size: 1.5rem;
          font-weight: 700;
        }

        .approval-content {
          margin-bottom: 2rem;
        }

        .approval-details h3 {
          color: #333;
          font-size: 1.1rem;
          margin-bottom: 1rem;
          text-align: center;
        }

        .status-item {
          display: flex;
          justify-content: space-between;
          padding: 0.75rem;
          background: #f8f9fa;
          border-radius: 8px;
          margin-bottom: 0.5rem;
        }

        .status-label {
          font-weight: 600;
          color: #666;
        }

        .status-value {
          font-weight: 700;
        }

        .status-value.pending {
          color: #f59e0b;
          text-transform: uppercase;
          font-size: 0.9rem;
        }

        .approval-info {
          background: #e8f5e8;
          padding: 1.5rem;
          border-radius: 12px;
          margin-bottom: 2rem;
        }

        .approval-info h4 {
          margin: 0 0 1rem;
          color: #333;
          font-size: 1rem;
        }

        .approval-info p {
          margin: 0.5rem 0;
          color: #666;
          line-height: 1.4;
        }

        .approval-actions {
          display: flex;
          gap: 1rem;
          justify-content: center;
        }

        .approval-button {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          flex: 1;
        }

        .approval-button.primary {
          background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
          color: white;
        }

        .approval-button.primary:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }

        .approval-button.secondary {
          background: #e1e5e9;
          color: #666;
        }

        .approval-button.secondary:hover {
          background: #d1d5db;
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        /* Security Declaration Styles */
        .security-declaration {
          background: #fff3cd;
          border: 2px solid #ffa726;
          border-radius: 12px;
          padding: 1.5rem;
          margin: 1.5rem 0;
        }

        .security-declaration h4 {
          color: #721c24;
          margin: 0 0 1rem;
          font-size: 1.1rem;
          font-weight: 600;
        }

        .security-declaration p {
          color: #666;
          margin: 0.5rem 0;
          line-height: 1.4;
        }

        .security-input input {
          width: 100%;
          padding: 0.75rem;
          border: 2px solid #e1e5e9;
          border-radius: 8px;
          font-size: 1rem;
          text-transform: uppercase;
          text-align: center;
          letter-spacing: 2px;
        }

        .security-input input:focus {
          outline: none;
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .security-submit {
          background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
          color: white;
          border: none;
          border-radius: 8px;
          padding: 0.75rem 1.5rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          margin-top: 1rem;
        }

        .security-submit:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(40, 167, 69, 0.4);
        }

        .security-submit:disabled {
          background: #ccc;
          cursor: not-allowed;
          transform: none;
          box-shadow: none;
        }

        .password-input {
          position: relative;
        }

        .toggle-password {
          position: absolute;
          right: 0.875rem;
          top: 50%;
          transform: translateY(-50%);
          background: none;
          border: none;
          cursor: pointer;
          color: #666;
          padding: 0.25rem;
        }

        .submit-button {
          background: rgba(255, 255, 255, 0.9);
          color: #1E40AF;
          border: none;
          padding: 1rem;
          border-radius: 12px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          backdrop-filter: blur(10px);
        }

        .submit-button:hover:not(:disabled) {
          background: white;
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        }

        .submit-button:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }

        .auth-toggle {
          text-align: center;
          margin-top: 1.5rem;
        }

        .auth-toggle p {
          color: rgba(255, 255, 255, 0.9);
          margin: 0;
        }

        .toggle-link {
          background: none;
          border: none;
          color: white;
          font-weight: 600;
          cursor: pointer;
          margin-left: 0.5rem;
          text-decoration: underline;
        }

        .back-button {
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.3);
          color: white;
          cursor: pointer;
          margin-top: 1rem;
          text-align: center;
          width: 100%;
          padding: 0.5rem;
          border-radius: 8px;
          backdrop-filter: blur(10px);
          transition: all 0.3s ease;
        }

        .back-button:hover {
          background: rgba(255, 255, 255, 0.2);
        }

        .file-preview {
          margin-top: 0.5rem;
          padding: 0.5rem;
          background: rgba(255, 255, 255, 0.2);
          backdrop-filter: blur(10px);
          border-radius: 6px;
          font-size: 0.85rem;
          color: white;
        }

        @media (min-width: 768px) {
          .auth-container {
            padding: 3rem;
          }
        }
      `}</style>
    </div>
  );
};

export default MechanicAuth;
