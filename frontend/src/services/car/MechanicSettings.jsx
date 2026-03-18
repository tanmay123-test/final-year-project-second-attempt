import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Settings, Bell, Shield, Smartphone, 
  Globe, CreditCard, User, Lock, Mail, Phone,
  MapPin, Clock, DollarSign, Save, Eye, EyeOff,
  ToggleLeft, ToggleRight, HelpCircle, LogOut, AlertCircle
} from 'lucide-react';

const MechanicSettings = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState({
    profile: {
      name: '',
      email: '',
      phone: '',
      address: '',
      bio: ''
    },
    notifications: {
      emailNotifications: true,
      smsNotifications: false,
      pushNotifications: true,
      newJobAlerts: true,
      paymentAlerts: true,
      ratingAlerts: true,
      promotionalEmails: false
    },
    privacy: {
      profileVisibility: 'public',
      showPhone: true,
      showEmail: false,
      showAddress: true,
      allowDirectContact: true
    },
    payment: {
      preferredMethod: 'bank_transfer',
      bankName: '',
      accountNumber: '',
      ifsc: '',
      upiId: ''
    },
    availability: {
      autoAccept: false,
      workingHours: {
        monday: { start: '09:00', end: '18:00', enabled: true },
        tuesday: { start: '09:00', end: '18:00', enabled: true },
        wednesday: { start: '09:00', end: '18:00', enabled: true },
        thursday: { start: '09:00', end: '18:00', enabled: true },
        friday: { start: '09:00', end: '18:00', enabled: true },
        saturday: { start: '10:00', end: '16:00', enabled: false },
        sunday: { start: '10:00', end: '16:00', enabled: false }
      },
      maxJobsPerDay: 1,
      emergencyService: false
    },
    security: {
      twoFactorAuth: false,
      loginAlerts: true,
      sessionTimeout: '30min',
      activeSessions: []
    }
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const storedData = localStorage.getItem('workerData');
      const token = localStorage.getItem('workerToken');
      
      if (storedData && token) {
        const workerData = JSON.parse(storedData);
        const workerId = workerData.id || workerData.workerId;
        
        try {
          const response = await fetch(`http://localhost:5000/api/car/service/worker/${workerId}/settings`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });

          if (response.ok) {
            const data = await response.json();
            setSettings({ ...settings, ...data.settings });
          } else {
            console.log('⚠️ Settings API not available, using local state');
            // Keep current local settings - don't overwrite with empty
          }
        } catch (error) {
          console.log('⚠️ Network error, using local settings state:', error.message);
          // Keep current local settings - don't show error to user
        }
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
    setLoading(false);
  };

  const updateSettings = async (category, updates) => {
    try {
      setSaving(true);
      const token = localStorage.getItem('workerToken');
      const storedData = localStorage.getItem('workerData');
      
      if (!token || !storedData) {
        alert('Please login to update settings');
        setSaving(false);
        return;
      }
      
      let workerData;
      try {
        workerData = JSON.parse(storedData);
      } catch (parseError) {
        console.error('Error parsing worker data:', parseError);
        alert('Invalid worker data. Please login again.');
        setSaving(false);
        return;
      }
      
      const workerId = workerData.id || workerData.workerId;
      
      const response = await fetch(`http://localhost:5000/api/car/service/worker/${workerId}/settings`, {
        method: 'PUT',
        mode: 'cors',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        body: JSON.stringify({ category, updates })
      });

      if (response.ok) {
        setSettings({ ...settings, [category]: { ...settings[category], ...updates } });
        alert('Settings updated successfully!');
      } else {
        console.log('⚠️ Settings API not available, updating local state only');
        // Update local state even if API fails
        setSettings({ ...settings, [category]: { ...settings[category], ...updates } });
        alert('Settings saved locally (API not available)');
      }
      setSaving(false);
    } catch (error) {
      console.error('Error updating settings:', error);
      alert('Error updating settings. Please try again.');
      setSaving(false);
    }
  };

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      localStorage.removeItem('workerToken');
      localStorage.removeItem('workerData');
      navigate('/worker/car/mechanic/login');
    }
  };

  if (loading) {
    return (
      <div className="settings-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading settings...</p>
        </div>
        <style>{`
          .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            background: #f8fafc;
          }
          .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #e2e8f0;
            border-top: 4px solid #8B5CF6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 1rem;
          }
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="settings-page">
      {/* Header */}
      <div className="settings-header">
        <div className="header-actions">
          <button className="back-button" onClick={() => navigate('/worker/car/mechanic/profile')}>
            <ArrowLeft size={20} />
            <span>Back to Profile</span>
          </button>
        </div>
        <h1>Settings</h1>
      </div>

      <div className="settings-content">
        {/* Profile Settings */}
        <div className="settings-section">
          <div className="section-header">
            <User size={20} className="section-icon" />
            <h3>Profile Information</h3>
          </div>
          
          <div className="settings-grid">
            <div className="setting-item">
              <label>Full Name</label>
              <input
                type="text"
                value={settings.profile.name}
                onChange={(e) => setSettings({
                  ...settings,
                  profile: { ...settings.profile, name: e.target.value }
                })}
                className="setting-input"
              />
            </div>
            
            <div className="setting-item">
              <label>Email Address</label>
              <input
                type="email"
                value={settings.profile.email}
                onChange={(e) => setSettings({
                  ...settings,
                  profile: { ...settings.profile, email: e.target.value }
                })}
                className="setting-input"
              />
            </div>
            
            <div className="setting-item">
              <label>Phone Number</label>
              <input
                type="tel"
                value={settings.profile.phone}
                onChange={(e) => setSettings({
                  ...settings,
                  profile: { ...settings.profile, phone: e.target.value }
                })}
                className="setting-input"
              />
            </div>
            
            <div className="setting-item full-width">
              <label>Address</label>
              <textarea
                value={settings.profile.address}
                onChange={(e) => setSettings({
                  ...settings,
                  profile: { ...settings.profile, address: e.target.value }
                })}
                className="setting-input textarea"
                rows={2}
              />
            </div>
            
            <div className="setting-item full-width">
              <label>Professional Bio</label>
              <textarea
                value={settings.profile.bio}
                onChange={(e) => setSettings({
                  ...settings,
                  profile: { ...settings.profile, bio: e.target.value }
                })}
                className="setting-input textarea"
                rows={3}
                placeholder="Describe your experience and expertise..."
              />
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="settings-section">
          <div className="section-header">
            <Bell size={20} className="section-icon" />
            <h3>Notifications</h3>
          </div>
          
          <div className="settings-grid">
            <div className="setting-item">
              <label>Email Notifications</label>
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.notifications.emailNotifications}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: { ...settings.notifications, emailNotifications: e.target.checked }
                  })}
                />
                <span className="slider"></span>
              </div>
            </div>
            
            <div className="setting-item">
              <label>SMS Notifications</label>
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.notifications.smsNotifications}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: { ...settings.notifications, smsNotifications: e.target.checked }
                  })}
                />
                <span className="slider"></span>
              </div>
            </div>
            
            <div className="setting-item">
              <label>Push Notifications</label>
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.notifications.pushNotifications}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: { ...settings.notifications, pushNotifications: e.target.checked }
                  })}
                />
                <span className="slider"></span>
              </div>
            </div>
            
            <div className="setting-item">
              <label>New Job Alerts</label>
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.notifications.newJobAlerts}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: { ...settings.notifications, newJobAlerts: e.target.checked }
                  })}
                />
                <span className="slider"></span>
              </div>
            </div>
            
            <div className="setting-item">
              <label>Payment Alerts</label>
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.notifications.paymentAlerts}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: { ...settings.notifications, paymentAlerts: e.target.checked }
                  })}
                />
                <span className="slider"></span>
              </div>
            </div>
            
            <div className="setting-item">
              <label>Rating Alerts</label>
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.notifications.ratingAlerts}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: { ...settings.notifications, ratingAlerts: e.target.checked }
                  })}
                />
                <span className="slider"></span>
              </div>
            </div>
          </div>
        </div>

        {/* Privacy Settings */}
        <div className="settings-section">
          <div className="section-header">
            <Shield size={20} className="section-icon" />
            <h3>Privacy</h3>
          </div>
          
          <div className="settings-grid">
            <div className="setting-item">
              <label>Profile Visibility</label>
              <select
                value={settings.privacy.profileVisibility}
                onChange={(e) => setSettings({
                  ...settings,
                  privacy: { ...settings.privacy, profileVisibility: e.target.value }
                })}
                className="setting-select"
              >
                <option value="public">Public</option>
                <option value="customers">Customers Only</option>
                <option value="private">Private</option>
              </select>
            </div>
            
            <div className="setting-item">
              <label>Show Phone Number</label>
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.privacy.showPhone}
                  onChange={(e) => setSettings({
                    ...settings,
                    privacy: { ...settings.privacy, showPhone: e.target.checked }
                  })}
                />
                <span className="slider"></span>
              </div>
            </div>
            
            <div className="setting-item">
              <label>Show Email Address</label>
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.privacy.showEmail}
                  onChange={(e) => setSettings({
                    ...settings,
                    privacy: { ...settings.privacy, showEmail: e.target.checked }
                  })}
                />
                <span className="slider"></span>
              </div>
            </div>
            
            <div className="setting-item">
              <label>Allow Direct Contact</label>
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.privacy.allowDirectContact}
                  onChange={(e) => setSettings({
                    ...settings,
                    privacy: { ...settings.privacy, allowDirectContact: e.target.checked }
                  })}
                />
                <span className="slider"></span>
              </div>
            </div>
          </div>
        </div>

        {/* Payment Settings */}
        <div className="settings-section">
          <div className="section-header">
            <CreditCard size={20} className="section-icon" />
            <h3>Payment Information</h3>
          </div>
          
          <div className="settings-grid">
            <div className="setting-item">
              <label>Preferred Payment Method</label>
              <select
                value={settings.payment.preferredMethod}
                onChange={(e) => setSettings({
                  ...settings,
                  payment: { ...settings.payment, preferredMethod: e.target.value }
                })}
                className="setting-select"
              >
                <option value="bank_transfer">Bank Transfer</option>
                <option value="upi">UPI</option>
                <option value="cash">Cash</option>
                <option value="cheque">Cheque</option>
              </select>
            </div>
            
            <div className="setting-item">
              <label>Bank Name</label>
              <input
                type="text"
                value={settings.payment.bankName}
                onChange={(e) => setSettings({
                  ...settings,
                  payment: { ...settings.payment, bankName: e.target.value }
                })}
                className="setting-input"
              />
            </div>
            
            <div className="setting-item">
              <label>Account Number</label>
              <input
                type="text"
                value={settings.payment.accountNumber}
                onChange={(e) => setSettings({
                  ...settings,
                  payment: { ...settings.payment, accountNumber: e.target.value }
                })}
                className="setting-input"
              />
            </div>
            
            <div className="setting-item">
              <label>IFSC Code</label>
              <input
                type="text"
                value={settings.payment.ifsc}
                onChange={(e) => setSettings({
                  ...settings,
                  payment: { ...settings.payment, ifsc: e.target.value }
                })}
                className="setting-input"
              />
            </div>
            
            <div className="setting-item">
              <label>UPI ID</label>
              <input
                type="text"
                value={settings.payment.upiId}
                onChange={(e) => setSettings({
                  ...settings,
                  payment: { ...settings.payment, upiId: e.target.value }
                })}
                className="setting-input"
              />
            </div>
          </div>
        </div>

        {/* Availability Settings */}
        <div className="settings-section">
          <div className="section-header">
            <Clock size={20} className="section-icon" />
            <h3>Availability</h3>
          </div>
          
          <div className="settings-grid">
            <div className="setting-item">
              <label>Auto-Accept Jobs</label>
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.availability.autoAccept}
                  onChange={(e) => setSettings({
                    ...settings,
                    availability: { ...settings.availability, autoAccept: e.target.checked }
                  })}
                />
                <span className="slider"></span>
              </div>
            </div>
            
            <div className="setting-item">
              <label>Max Jobs Per Day</label>
              <input
                type="number"
                value={settings.availability.maxJobsPerDay}
                onChange={(e) => setSettings({
                  ...settings,
                  availability: { ...settings.availability, maxJobsPerDay: parseInt(e.target.value) }
                })}
                className="setting-input"
                min="1"
                max="10"
              />
            </div>
            
            <div className="setting-item">
              <label>Emergency Service</label>
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.availability.emergencyService}
                  onChange={(e) => setSettings({
                    ...settings,
                    availability: { ...settings.availability, emergencyService: e.target.checked }
                  })}
                />
                <span className="slider"></span>
              </div>
            </div>
          </div>
          
          <div className="working-hours">
            <h4>Working Hours</h4>
            <div className="hours-grid">
              {Object.keys(settings.availability.workingHours).map((day) => (
                <div key={day} className="day-hours">
                  <div className="day-header">
                    <input
                      type="checkbox"
                      checked={settings.availability.workingHours[day].enabled}
                      onChange={(e) => setSettings({
                        ...settings,
                        availability: {
                          ...settings.availability,
                          workingHours: {
                            ...settings.availability.workingHours,
                            [day]: { ...settings.availability.workingHours[day], enabled: e.target.checked }
                          }
                        }
                      })}
                    />
                    <span className="day-name">{day.charAt(0).toUpperCase() + day.slice(1)}</span>
                  </div>
                  <div className="time-inputs">
                    <input
                      type="time"
                      value={settings.availability.workingHours[day].start}
                      onChange={(e) => setSettings({
                        ...settings,
                        availability: {
                          ...settings.availability,
                          workingHours: {
                            ...settings.availability.workingHours,
                            [day]: { ...settings.availability.workingHours[day], start: e.target.value }
                          }
                        }
                      })}
                      disabled={!settings.availability.workingHours[day].enabled}
                    />
                    <span>to</span>
                    <input
                      type="time"
                      value={settings.availability.workingHours[day].end}
                      onChange={(e) => setSettings({
                        ...settings,
                        availability: {
                          ...settings.availability,
                          workingHours: {
                            ...settings.availability.workingHours,
                            [day]: { ...settings.availability.workingHours[day], end: e.target.value }
                          }
                        }
                      })}
                      disabled={!settings.availability.workingHours[day].enabled}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Security Settings */}
        <div className="settings-section">
          <div className="section-header">
            <Lock size={20} className="section-icon" />
            <h3>Security</h3>
          </div>
          
          <div className="settings-grid">
            <div className="setting-item">
              <label>Two-Factor Authentication</label>
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.security.twoFactorAuth}
                  onChange={(e) => setSettings({
                    ...settings,
                    security: { ...settings.security, twoFactorAuth: e.target.checked }
                  })}
                />
                <span className="slider"></span>
              </div>
            </div>
            
            <div className="setting-item">
              <label>Login Alerts</label>
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.security.loginAlerts}
                  onChange={(e) => setSettings({
                    ...settings,
                    security: { ...settings.security, loginAlerts: e.target.checked }
                  })}
                />
                <span className="slider"></span>
              </div>
            </div>
            
            <div className="setting-item">
              <label>Session Timeout</label>
              <select
                value={settings.security.sessionTimeout}
                onChange={(e) => setSettings({
                  ...settings,
                  security: { ...settings.security, sessionTimeout: e.target.value }
                })}
                className="setting-select"
              >
                <option value="15min">15 minutes</option>
                <option value="30min">30 minutes</option>
                <option value="1hour">1 hour</option>
                <option value="4hours">4 hours</option>
                <option value="24hours">24 hours</option>
              </select>
            </div>
          </div>
          
          <div className="active-sessions">
            <h4>Active Sessions</h4>
            {settings.security.activeSessions.map((session, index) => (
              <div key={index} className="session-item">
                <div className="session-info">
                  <div className="session-device">
                    <Smartphone size={16} />
                    <span>{session.device}</span>
                  </div>
                  <div className="session-details">
                    <span className="session-location">{session.location}</span>
                    <span className="session-time">Last active: {session.lastActive}</span>
                  </div>
                </div>
                {session.current && (
                  <span className="current-badge">Current</span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="settings-actions">
          <button 
            className="save-button" 
            onClick={() => updateSettings('all', settings)}
            disabled={saving}
          >
            <Save size={18} />
            <span>{saving ? 'Saving...' : 'Save All Settings'}</span>
          </button>
          
          <button className="logout-button" onClick={handleLogout}>
            <LogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      </div>

      <style>{`
        .settings-page {
          background-color: #f8fafc;
          min-height: 100vh;
          font-family: 'Inter', sans-serif;
        }

        .settings-header {
          background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
          padding: 1.5rem;
          color: white;
        }

        .header-actions {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .back-button {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 8px;
          cursor: pointer;
          transition: background 0.2s;
        }

        .back-button:hover {
          background: rgba(255, 255, 255, 0.2);
        }

        .settings-header h1 {
          margin: 0;
          font-size: 1.5rem;
          font-weight: 700;
        }

        .settings-content {
          padding: 1.5rem;
          max-width: 800px;
          margin: 0 auto;
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .settings-section {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .section-header {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 1.5rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid #E5E7EB;
        }

        .section-icon {
          color: #8B5CF6;
        }

        .section-header h3 {
          margin: 0;
          font-size: 1.2rem;
          font-weight: 700;
          color: #1F2937;
        }

        .settings-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1.5rem;
        }

        .setting-item {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .setting-item.full-width {
          grid-column: 1 / -1;
        }

        .setting-item label {
          font-size: 0.9rem;
          font-weight: 600;
          color: #374151;
        }

        .setting-input, .setting-select {
          padding: 0.75rem;
          border: 1px solid #D1D5DB;
          border-radius: 8px;
          font-size: 1rem;
          background: white;
        }

        .setting-input:focus, .setting-select:focus {
          outline: none;
          border-color: #8B5CF6;
          box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
        }

        .textarea {
          resize: vertical;
          min-height: 80px;
        }

        .toggle-switch {
          position: relative;
          display: inline-block;
          width: 50px;
          height: 24px;
        }

        .toggle-switch input {
          opacity: 0;
          width: 0;
          height: 0;
        }

        .slider {
          position: absolute;
          cursor: pointer;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: #D1D5DB;
          transition: 0.4s;
          border-radius: 24px;
        }

        .slider:before {
          position: absolute;
          content: "";
          height: 18px;
          width: 18px;
          left: 3px;
          bottom: 3px;
          background-color: white;
          transition: 0.4s;
          border-radius: 50%;
        }

        .toggle-switch input:checked + .slider {
          background-color: #8B5CF6;
        }

        .toggle-switch input:checked + .slider:before {
          transform: translateX(26px);
        }

        .working-hours {
          margin-top: 1.5rem;
        }

        .working-hours h4 {
          margin: 0 0 1rem 0;
          font-size: 1rem;
          font-weight: 600;
          color: #374151;
        }

        .hours-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
        }

        .day-hours {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
          padding: 1rem;
          background: #F9FAFB;
          border-radius: 8px;
        }

        .day-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .day-name {
          font-weight: 600;
          color: #374151;
        }

        .time-inputs {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .time-inputs input {
          padding: 0.5rem;
          border: 1px solid #D1D5DB;
          border-radius: 6px;
          font-size: 0.9rem;
        }

        .time-inputs input:disabled {
          background: #F3F4F6;
          color: #9CA3AF;
        }

        .active-sessions {
          margin-top: 1.5rem;
        }

        .active-sessions h4 {
          margin: 0 0 1rem 0;
          font-size: 1rem;
          font-weight: 600;
          color: #374151;
        }

        .session-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background: #F9FAFB;
          border-radius: 8px;
          margin-bottom: 0.75rem;
        }

        .session-info {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .session-device {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #374151;
          font-weight: 600;
        }

        .session-details {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .session-location {
          font-size: 0.9rem;
          color: #6B7280;
        }

        .session-time {
          font-size: 0.8rem;
          color: #9CA3AF;
        }

        .current-badge {
          background: #10B981;
          color: white;
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.8rem;
          font-weight: 600;
        }

        .settings-actions {
          display: flex;
          gap: 1rem;
          justify-content: flex-end;
          margin-top: 2rem;
        }

        .save-button, .logout-button {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1.5rem;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .save-button {
          background: #8B5CF6;
          color: white;
          border: none;
        }

        .save-button:hover:not(:disabled) {
          background: #7C3AED;
        }

        .save-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .logout-button {
          background: #FEE2E2;
          color: #EF4444;
          border: 1px solid #FCA5A5;
        }

        .logout-button:hover {
          background: #FCA5A5;
        }

        @media (max-width: 768px) {
          .settings-grid {
            grid-template-columns: 1fr;
          }
          
          .hours-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default MechanicSettings;
