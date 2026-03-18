import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Wrench, Eye, EyeOff, User, Lock, Mail, Phone, Upload, FileText, Camera } from 'lucide-react';

const MechanicAuth = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const isLogin = location.pathname.includes('login');
  
  // Check if worker has pending approval
  const [pendingApproval, setPendingApproval] = useState(false);
  
  useEffect(() => {
    if (isLogin) {
      const token = localStorage.getItem('workerToken');
      const workerData = localStorage.getItem('workerData');
      
      if (token && workerData) {
        const worker = JSON.parse(workerData);
        if (worker.status === 'PENDING') {
          setPendingApproval(true);
        }
      }
    }
  }, [isLogin]);
  
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

        if (response.ok) {
          // Check if worker is approved
          if (data.mechanic && data.mechanic.status === 'approved') {
            // Store token and user data
            localStorage.setItem('workerToken', data.token);
            localStorage.setItem('workerData', JSON.stringify(data.mechanic));
            
            // Show success message like CLI
            alert(`✅ Login successful! Welcome back, ${data.mechanic?.name || 'Mechanic'}!`);
            
            // Navigate to dashboard
            navigate('/worker/car/mechanic/dashboard');
          } else if (data.mechanic && data.mechanic.status === 'pending') {
            // Show pending approval message
            setError('⏳ Your request is in pending approval. Wait for admin approval before logging in.');
          } else {
            setError('❌ Your account is not approved. Please contact admin.');
          }
        } else {
          setError(data.error || 'Login failed');
        }
      } else {
        // For signup, show security declaration first
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

      const response = await fetch(`http://127.0.0.1:5000${endpoint}`, {
        method: 'POST',
        body: formDataToSend
      });

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
      {/* Show pending approval message instead of login form */}
      {isLogin && pendingApproval ? (
        <div className="auth-container">
          <div className="auth-header">
            <div className="icon-wrapper">
              <Wrench size={48} strokeWidth={2} />
            </div>
            <h1>⏳ Approval Pending</h1>
            <p>Your registration is pending admin approval</p>
          </div>
          
          <div className="approval-message">
            <div className="approval-icon">📋</div>
            <h3>Your request is in pending approval</h3>
            <p>Wait for admin approval before logging in.</p>
            <p>Expected approval time: 2-24 hours</p>
            <p>You will be notified when the decision's done</p>
            <p>For urgent inquiries, contact support</p>
          </div>
          
          <div className="auth-toggle">
            <p>
              Need to update your information?
              <button type="button" onClick={() => navigate('/worker/car/mechanic/signup')} className="toggle-link">
                Update Application
              </button>
            </p>
          </div>
        </div>
      ) : (
        <div className="auth-container">
          {/* Header */}
          <div className="auth-header">
            <div className="icon-wrapper">
              <Wrench size={48} strokeWidth={2} />
            </div>
            <h1>{isLogin ? 'Mechanic Login' : 'Mechanic Signup'}</h1>
            <p>{isLogin ? 'Welcome back to your workshop' : 'Join our network of expert mechanics'}</p>
          </div>

          {/* Form */}
          <form onSubmit={isLogin ? handleSubmit : (e) => {e.preventDefault(); setShowSecurityDeclaration(true);}} className="auth-form">
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
                    min="1"
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
                    placeholder="123 Main St"
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
                    placeholder="5"
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
                    Driving License
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

                {/* Security Declaration */}
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

                <button 
                  type="submit" 
                  className="submit-button" 
                  disabled={loading || (showSecurityDeclaration && !securityAccepted)}
                >
                  {loading ? 'Processing...' : (isLogin ? 'Login' : 'Sign Up')}
                </button>
              </>
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
                    <h4>✅ Signup Successful!</h4>
                    <p>Wait for admin's approval</p>
                    <p>You will be notified when the decision's done</p>
                    <p>Expected approval time: 2-24 hours</p>
                    <p>After approval, you can login and access your dashboard</p>
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
        </div>
      )}
    </div>
  )

  // CSS Styles
  return (
    <style>{`
      .mechanic-auth {
        min-height: 100vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      }

      .auth-container {
        background: white;
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        width: 100%;
        max-width: 500px;
        position: relative;
      }

      .auth-header {
        text-align: center;
        margin-bottom: 2rem;
      }

      .icon-wrapper {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem;
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
      }

      .auth-header h1 {
        color: #1a1a1a;
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 0.5rem;
      }

      .auth-header p {
        color: #666;
        font-size: 1rem;
        margin: 0;
      }

      .form-group {
        margin-bottom: 1.5rem;
      }

      .form-group label {
        display: flex;
        align-items: center;
        color: #333;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
      }

      .form-group label svg {
        margin-right: 0.5rem;
        color: #667eea;
      }

      .form-group input {
        width: 100%;
        padding: 0.875rem;
        border: 2px solid #e1e5e9;
        border-radius: 8px;
        font-size: 1rem;
        transition: all 0.2s;
      }

      .form-group input:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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
        color: #666;
        cursor: pointer;
        padding: 0.5rem;
      }

      .file-preview {
        margin-top: 0.5rem;
        padding: 0.5rem;
        background: #f8f9fa;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #666;
      }

      .security-declaration {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 2px solid #ffa726;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
      }

      .security-declaration h4 {
        color: #333;
        margin: 0 0 1rem;
        font-size: 1.1rem;
        font-weight: 600;
        text-align: center;
      }

      .security-declaration p {
        color: #666;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        text-align: center;
      }

      .security-input input {
        width: 100%;
        padding: 0.75rem;
        border: 2px solid #ffa726;
        border-radius: 6px;
        font-size: 1rem;
        text-align: center;
        margin-top: 1rem;
      }

      .security-input input:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      }

      .security-submit {
        background: linear-gradient(135deg, #28a745 0%, #667eea 100%);
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

      .submit-button {
        width: 100%;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        margin-top: 1.5rem;
      }

      .submit-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
      }

      .submit-button:disabled {
        background: #ccc;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
      }

      .error-message {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: 600;
      }

      .approval-message {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 2px solid #ffa726;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        text-align: center;
      }

      .approval-message .approval-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
      }

      .approval-message h3 {
        color: #333;
        margin: 0 0 1rem;
        font-size: 1.2rem;
        font-weight: 600;
      }

      .approval-message p {
        color: #666;
        margin: 0.5rem 0;
        line-height: 1.4;
      }

      .approval-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
      }

      .approval-modal {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        max-width: 500px;
        width: 90%;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        animation: slideIn 0.3s ease-out;
      }

      .approval-header {
        text-align: center;
        margin-bottom: 1.5rem;
      }

      .approval-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
      }

      .approval-header h2 {
        color: #1a1a1a;
        margin: 0 0 1rem;
        font-size: 1.5rem;
        font-weight: 700;
      }

      .approval-content {
        margin-bottom: 1.5rem;
      }

      .approval-details {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
      }

      .approval-details h3 {
        color: #333;
        margin: 0 0 1rem;
        font-size: 1.1rem;
        font-weight: 600;
      }

      .status-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0;
        border-bottom: 1px solid #e1e5e9;
      }

      .status-item:last-child {
        border-bottom: none;
      }

      .status-label {
        color: #666;
        font-weight: 600;
      }

      .status-value {
        color: #333;
        font-weight: 700;
      }

      .status-value.pending {
        color: #ffa726;
        font-weight: 700;
      }

      .approval-info {
        text-align: center;
      }

      .approval-info h4 {
        color: #333;
        margin: 0 0 1rem;
        font-size: 1.1rem;
        font-weight: 600;
      }

      .approval-info p {
        color: #666;
        margin: 0.5rem 0;
        line-height: 1.4;
      }

      .approval-actions {
        display: flex;
        gap: 1rem;
        margin-top: 1.5rem;
      }

      .approval-button {
        flex: 1;
        padding: 0.75rem;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
      }

      .approval-button.primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
      }

      .approval-button.secondary {
        background: #f8f9fa;
        color: #666;
        border: 2px solid #e1e5e9;
      }

      .approval-button:hover {
        transform: translateY(-2px);
      }

      .auth-toggle {
        text-align: center;
        margin-top: 1.5rem;
      }

      .auth-toggle p {
        color: #666;
        font-size: 0.9rem;
      }

      .toggle-link {
        background: none;
        border: none;
        color: #667eea;
        font-weight: 600;
        cursor: pointer;
        margin-left: 0.5rem;
        text-decoration: underline;
      }

      .back-button {
        background: none;
        border: none;
        color: #666;
        cursor: pointer;
        margin-top: 1rem;
        text-align: center;
        width: 100%;
        padding: 0.5rem;
      }

      @media (min-width: 768px) {
        .auth-container {
          padding: 3rem;
        }
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
    `}</style>
  );
;

export default MechanicAuth;
