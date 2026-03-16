import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { workerService } from '../../../services/api';
import DoctorBottomNav from '../../../components/DoctorBottomNav';
import { ChevronLeft, Bell, Moon, Volume2, Mail, Power } from 'lucide-react';

const DoctorSettings = () => {
  const navigate = useNavigate();
  const { worker } = useAuth();
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [isOnline, setIsOnline] = useState(true);
  const [settings, setSettings] = useState({
    notificationsEmail: true,
    notificationsSound: true,
    darkMode: false
  });

  useEffect(() => {
    const s = localStorage.getItem('doctor_settings');
    if (s) {
      try {
        const parsed = JSON.parse(s);
        setSettings({
          notificationsEmail: !!parsed.notificationsEmail,
          notificationsSound: !!parsed.notificationsSound,
          darkMode: !!parsed.darkMode
        });
      } catch {}
    }
    const loadStatus = async () => {
      if (!worker?.worker_id) return;
      try {
        const res = await workerService.getStatus(worker.worker_id);
        setIsOnline(String(res.data.status || 'online').toLowerCase() === 'online');
      } catch {}
    };
    loadStatus();
  }, [worker]);

  const updateStatus = async (value) => {
    setIsOnline(value);
    if (!worker?.worker_id) return;
    try {
      await workerService.updateStatus(worker.worker_id, value ? 'online' : 'offline');
      setMessage(value ? 'Status set to Online' : 'Status set to Offline');
      setTimeout(() => setMessage(''), 1200);
    } catch {
      setMessage('Failed to update status');
      setTimeout(() => setMessage(''), 1500);
    }
  };

  const handleSave = () => {
    setSaving(true);
    localStorage.setItem('doctor_settings', JSON.stringify(settings));
    setTimeout(() => {
      setSaving(false);
      setMessage('Settings saved');
      setTimeout(() => setMessage(''), 1200);
    }, 300);
  };

  return (
    <div className="doctor-settings-page">
      <div className="settings-header">
        <button className="back-btn" onClick={() => navigate(-1)}>
          <ChevronLeft size={20} />
          <span>Back</span>
        </button>
        <h1>Settings</h1>
      </div>

      <div className="content-wrap">
        <div className="section-card">
          <div className="section-title">
            <Power size={18} />
            <span>Availability</span>
          </div>
          <div className="row">
            <span className="label">Online Status</span>
            <label className="switch">
              <input
                type="checkbox"
                checked={isOnline}
                onChange={(e) => updateStatus(e.target.checked)}
              />
              <span className="slider" />
            </label>
          </div>
        </div>

        <div className="section-card">
          <div className="section-title">
            <Bell size={18} />
            <span>Notifications</span>
          </div>
          <div className="row">
            <div className="label-with-icon">
              <Mail size={16} />
              <span>Email Updates</span>
            </div>
            <label className="switch">
              <input
                type="checkbox"
                checked={settings.notificationsEmail}
                onChange={(e) => setSettings({ ...settings, notificationsEmail: e.target.checked })}
              />
              <span className="slider" />
            </label>
          </div>
          <div className="row">
            <div className="label-with-icon">
              <Volume2 size={16} />
              <span>Sound Alert</span>
            </div>
            <label className="switch">
              <input
                type="checkbox"
                checked={settings.notificationsSound}
                onChange={(e) => setSettings({ ...settings, notificationsSound: e.target.checked })}
              />
              <span className="slider" />
            </label>
          </div>
        </div>

        <div className="section-card">
          <div className="section-title">
            <Moon size={18} />
            <span>Appearance</span>
          </div>
          <div className="row">
            <span className="label">Dark Mode</span>
            <label className="switch">
              <input
                type="checkbox"
                checked={settings.darkMode}
                onChange={(e) => setSettings({ ...settings, darkMode: e.target.checked })}
              />
              <span className="slider" />
            </label>
          </div>
        </div>

        <button className="save-btn" onClick={handleSave} disabled={saving}>
          {saving ? 'Saving…' : 'Save Settings'}
        </button>
        {message && <div className="msg">{message}</div>}
      </div>

      <DoctorBottomNav />

      <style>{`
        .doctor-settings-page {
          background-color: var(--background-light);
          min-height: 100vh;
          padding-bottom: 90px;
          font-family: 'Inter', sans-serif;
        }
        .settings-header {
          background: var(--medical-gradient);
          padding: 1.5rem 1.5rem 2rem;
          border-bottom-left-radius: 30px;
          border-bottom-right-radius: 30px;
          color: white;
        }
        .settings-header h1 {
          margin: 0.25rem 0 0 0;
          font-size: 1.25rem;
          font-weight: 700;
        }
        .back-btn {
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
          background: transparent;
          border: none;
          color: white;
          cursor: pointer;
        }
        .content-wrap {
          padding: 1.5rem;
          margin-top: -1.25rem;
        }
        .section-card {
          background: white;
          border-radius: 20px;
          padding: 1rem 1.25rem;
          box-shadow: var(--shadow-sm);
          margin-bottom: 1rem;
        }
        .section-title {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-weight: 700;
          margin-bottom: 0.75rem;
          color: var(--text-primary);
        }
        .row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem 0;
          border-bottom: 1px solid #EEF2F7;
        }
        .row:last-child {
          border-bottom: none;
        }
        .label {
          color: var(--text-secondary);
          font-weight: 600;
        }
        .label-with-icon {
          display: inline-flex;
          align-items: center;
          gap: 0.35rem;
          color: var(--text-secondary);
          font-weight: 600;
        }
        .switch {
          position: relative;
          display: inline-block;
          width: 46px;
          height: 26px;
        }
        .switch input {
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
          background-color: #E5E7EB;
          transition: .2s;
          border-radius: 26px;
        }
        .slider:before {
          position: absolute;
          content: "";
          height: 20px;
          width: 20px;
          left: 3px;
          bottom: 3px;
          background-color: white;
          transition: .2s;
          border-radius: 50%;
          box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }
        .switch input:checked + .slider {
          background-color: #8E44AD;
        }
        .switch input:checked + .slider:before {
          transform: translateX(20px);
        }
        .save-btn {
          width: 100%;
          border: none;
          border-radius: 14px;
          padding: 0.9rem 1rem;
          background: var(--accent-blue);
          color: white;
          font-weight: 700;
          cursor: pointer;
          margin-top: 0.5rem;
        }
        .save-btn:disabled {
          opacity: 0.7;
          cursor: default;
        }
        .msg {
          margin-top: 0.5rem;
          text-align: center;
          color: var(--text-secondary);
          font-weight: 600;
        }
        @media (min-width: 768px) {
          .content-wrap {
            max-width: 640px;
            margin: -1.25rem auto 0;
          }
        }
      `}</style>
    </div>
  );
};

export default DoctorSettings;
