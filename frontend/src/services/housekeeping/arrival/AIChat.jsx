import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Sparkles, BarChart2, Bell, Calendar, Info, AlertTriangle, Trash2, Plus, CheckCircle, ToggleRight, ToggleLeft } from 'lucide-react';
import { useAuth } from '../../../context/AuthContext';
import api from '../../../shared/api';

const AIChat = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [cleaningStatus, setCleaningStatus] = useState(null);
  const [showUpgrade, setShowUpgrade] = useState(false);
  const [loading, setLoading] = useState(true);
  const [localMode, setLocalMode] = useState(false);
  
  // Reminder State
  const [reminderType, setReminderType] = useState('General Cleaning');
  const [frequencyType, setFrequencyType] = useState('15_days');
  const [customDate, setCustomDate] = useState('');
  const [repeat, setRepeat] = useState(false);
  const [reminderMessage, setReminderMessage] = useState('');
  const [myReminders, setMyReminders] = useState([]);

  const LS_KEY = 'hk_ai_reminders';

  const readLocalReminders = () => {
    try {
      const raw = localStorage.getItem(LS_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  };

  const writeLocalReminders = (list) => {
    try {
      localStorage.setItem(LS_KEY, JSON.stringify(list));
    } catch {}
  };

  const computeNextDate = (freq, custom) => {
    const d = new Date();
    if (freq === 'custom' && custom) return custom;
    const addDays = freq === '60_days' ? 60 : freq === '30_days' ? 30 : 15;
    d.setDate(d.getDate() + addDays);
    return d.toISOString().split('T')[0];
  };

  useEffect(() => {
    const fetchData = async () => {
      if (!user) return;
      try {
        const userId = user.id || user.user_id;
        const [statusRes, upgradeRes, remindersRes] = await Promise.all([
          api.get(`/api/ai/cleaning-status?user_id=${userId}`),
          api.get(`/api/ai/upgrade-suggestion?user_id=${userId}`),
          api.get(`/api/ai/get-reminders?user_id=${userId}`)
        ]);
        
        setCleaningStatus(statusRes.data);
        if (upgradeRes.data.show_upgrade) {
           setShowUpgrade(true);
        }
        setMyReminders(remindersRes.data);
      } catch (error) {
        console.error("Failed to fetch AI data", error);
        // Enable local-mode fallbacks for AI tab only
        setLocalMode(true);
        // Fallback mock status
        setCleaningStatus({
            status: "Recommended Soon",
            last_clean_date: "Feb 15",
            service_type: "Basic",
            days_passed: 12,
            next_suggested_date: "Mar 2",
            hygiene_score: 7,
            recommendation: "Book cleaning within 3 days to maintain hygiene.",
            seasonal_tip: "Festival season is approaching. Consider Deep Cleaning."
        });
        // Load local reminders if any
        setMyReminders(readLocalReminders());
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user]);

  const handleSetReminder = async () => {
    try {
      const userId = user.id || user.user_id;
      if (!localMode) {
        const res = await api.post('/api/ai/set-reminder', {
          user_id: userId,
          reminder_type: reminderType,
          frequency_type: frequencyType,
          custom_date: customDate,
          repeat: repeat
        });
        setReminderMessage(`Reminder set for ${res.data.next_reminder}`);
        const remindersRes = await api.get(`/api/ai/get-reminders?user_id=${userId}`);
        setMyReminders(remindersRes.data);
        setTimeout(() => setReminderMessage(''), 3000);
      } else {
        // Local fallback: store in localStorage
        const nextDate = computeNextDate(frequencyType, customDate);
        const newItem = {
          id: Date.now(),
          reminder_type: reminderType,
          next_reminder_date: nextDate,
          repeat
        };
        const updated = [newItem, ...readLocalReminders()];
        writeLocalReminders(updated);
        setMyReminders(updated);
        setReminderMessage(`Reminder set for ${nextDate}`);
        setTimeout(() => setReminderMessage(''), 3000);
      }
    } catch (error) {
      console.error("Failed to set reminder", error);
      if (!localMode) {
        const errorMsg = error.response?.data?.error || "Failed to set reminder";
        alert(errorMsg);
      }
    }
  };

  const handleDeleteReminder = async (id) => {
    try {
        if (!localMode) {
          await api.post('/api/ai/delete-reminder', { reminder_id: id });
          setMyReminders(myReminders.filter(r => r.id !== id));
        } else {
          const updated = readLocalReminders().filter(r => r.id !== id);
          writeLocalReminders(updated);
          setMyReminders(updated);
        }
    } catch (error) {
        console.error("Failed to delete reminder", error);
    }
  };

  const getStatusColor = (status) => {
    if (status === 'Good') return '#2ECC71';
    if (status === 'Overdue') return '#E74C3C';
    return '#F1C40F'; 
  };

  const getScoreColor = (score) => {
    if (score >= 8) return '#2ECC71';
    if (score >= 5) return '#F1C40F';
    return '#E74C3C';
  };

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: '#8E44AD' }}>Loading AI Insights...</div>;

  return (
    <div className="hk-page-container" style={{ backgroundColor: '#F9FAFB', minHeight: '100vh', fontFamily: "'Inter', sans-serif" }}>
      
      {/* Header */}
      <div style={{ 
        backgroundColor: '#8E44AD', 
        padding: '30px 24px 100px 24px', 
        borderBottomLeftRadius: '32px', 
        borderBottomRightRadius: '32px', 
        color: 'white',
        position: 'relative',
        boxShadow: '0 10px 30px -10px rgba(142, 68, 173, 0.4)',
        zIndex: 0
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
          <div style={{ 
            width: '48px', height: '48px', 
            backgroundColor: 'rgba(255,255,255,0.2)', 
            borderRadius: '16px', 
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            backdropFilter: 'blur(5px)'
          }}>
            <Sparkles size={24} color="white" />
          </div>
          <div>
            <h1 style={{ margin: 0, fontSize: '22px', fontWeight: 'bold' }}>Smart Home Hygiene Advisor</h1>
            <p style={{ margin: 0, fontSize: '14px', opacity: 0.9 }}>AI-powered cleaning intelligence</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ padding: '0 24px', marginTop: '-80px', position: 'relative', zIndex: 10 }}>
        
        {/* 1️⃣ 🚨 AI Alerts Section */}
        <div style={{ marginBottom: '32px' }}>
            <h2 style={{ fontSize: '18px', fontWeight: '700', color: 'white', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
               🚨 AI Alerts
            </h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                {/* Cleaning Status Card */}
                <div style={{ backgroundColor: 'white', borderRadius: '20px', padding: '24px', boxShadow: '0 10px 30px rgba(0,0,0,0.08)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', color: '#1E293B', fontWeight: '700', fontSize: '15px' }}>
                        <div style={{ backgroundColor: 'rgba(142, 68, 173, 0.1)', padding: '6px', borderRadius: '50%' }}>
                            <Info size={16} color="#8E44AD" />
                        </div>
                        Cleaning Status
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                        <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: getStatusColor(cleaningStatus?.status), boxShadow: `0 0 0 3px ${getStatusColor(cleaningStatus?.status)}33` }}></div>
                        <span style={{ fontSize: '14px', color: getStatusColor(cleaningStatus?.status), fontWeight: '700' }}>{cleaningStatus?.status}</span>
                    </div>
                    
                    <div style={{ fontSize: '13px', color: '#64748B', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontWeight: '500' }}>Last Clean</span>
                            <span style={{ fontWeight: '700', color: '#1E293B' }}>{cleaningStatus?.last_clean_date}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontWeight: '500' }}>Type</span>
                            <span style={{ fontWeight: '700', color: '#1E293B' }}>{cleaningStatus?.service_type}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px', paddingTop: '12px', borderTop: '1px solid #F1F5F9' }}>
                            <span style={{ color: '#8E44AD', fontWeight: '600' }}>Next</span>
                            <span style={{ fontWeight: '700', color: '#8E44AD' }}>{cleaningStatus?.next_suggested_date}</span>
                        </div>
                    </div>
                </div>

                {/* Hygiene Score Card */}
                <div style={{ backgroundColor: 'white', borderRadius: '20px', padding: '24px', boxShadow: '0 10px 30px rgba(0,0,0,0.08)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', color: '#1E293B', fontWeight: '700', fontSize: '15px' }}>
                        <div style={{ backgroundColor: 'rgba(142, 68, 173, 0.1)', padding: '6px', borderRadius: '50%' }}>
                            <BarChart2 size={16} color="#8E44AD" />
                        </div>
                        Hygiene Score
                    </div>
                    
                    <div style={{ marginBottom: '16px', display: 'flex', alignItems: 'baseline' }}>
                        <span style={{ fontSize: '42px', fontWeight: '800', color: '#1E293B', lineHeight: '1' }}>{cleaningStatus?.hygiene_score}</span>
                        <span style={{ fontSize: '16px', color: '#94A3B8', fontWeight: '500', marginLeft: '4px' }}>/10</span>
                    </div>
                    
                    <div style={{ width: '100%', height: '8px', backgroundColor: '#F1F5F9', borderRadius: '10px', marginBottom: '16px', overflow: 'hidden' }}>
                        <div style={{ width: `${cleaningStatus?.hygiene_score * 10}%`, height: '100%', backgroundColor: getScoreColor(cleaningStatus?.hygiene_score), borderRadius: '10px', transition: 'width 1s ease-in-out' }}></div>
                    </div>
                    
                    <p style={{ fontSize: '13px', color: '#64748B', lineHeight: '1.5', fontWeight: '500' }}>
                        {cleaningStatus?.recommendation}
                    </p>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                {/* Recommendation Card */}
                {showUpgrade && (
                    <div style={{ backgroundColor: 'white', borderRadius: '20px', padding: '24px', boxShadow: '0 10px 30px rgba(0,0,0,0.08)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', color: '#1E293B', fontWeight: '700', fontSize: '15px' }}>
                            <div style={{ backgroundColor: 'rgba(142, 68, 173, 0.1)', padding: '6px', borderRadius: '50%' }}>
                                <Sparkles size={16} color="#8E44AD" />
                            </div>
                            Recommendation
                        </div>
                        <p style={{ fontSize: '13px', color: '#64748B', lineHeight: '1.6', marginBottom: '20px', fontWeight: '500' }}>
                            You’ve booked <strong style={{ color: '#1E293B' }}>Basic Cleaning</strong> 3 times. <strong style={{ color: '#1E293B' }}>Deep Cleaning</strong> is recommended for better hygiene.
                        </p>
                        <button 
                            onClick={() => navigate('/housekeeping/booking/create', { state: { serviceType: 'Deep Cleaning' } })}
                            style={{ 
                                width: '100%', padding: '12px', borderRadius: '12px', 
                                backgroundColor: '#8E44AD', color: 'white', border: 'none', 
                                fontSize: '14px', fontWeight: '600', cursor: 'pointer',
                                boxShadow: '0 4px 12px rgba(142, 68, 173, 0.2)'
                            }}
                        >
                            Book Deep Cleaning
                        </button>
                    </div>
                )}

                {/* Seasonal Tip Card */}
                <div style={{ backgroundColor: 'white', borderRadius: '20px', padding: '24px', boxShadow: '0 10px 30px rgba(0,0,0,0.08)', gridColumn: showUpgrade ? 'auto' : '1 / span 2' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', color: '#1E293B', fontWeight: '700', fontSize: '15px' }}>
                        <div style={{ backgroundColor: '#FEF3C7', padding: '6px', borderRadius: '50%' }}>
                            <Info size={16} color="#F59E0B" />
                        </div>
                        Seasonal Tip
                    </div>
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                        <AlertTriangle size={20} color="#F59E0B" style={{ minWidth: '20px', marginTop: '2px' }} />
                        <p style={{ fontSize: '13px', color: '#64748B', lineHeight: '1.6', margin: 0, fontWeight: '500' }}>
                            {cleaningStatus?.seasonal_tip}
                        </p>
                    </div>
                </div>
            </div>
        </div>

        {/* 2️⃣ 🔔 My Reminders Section */}
        <div style={{ marginBottom: '40px' }}>
            <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#1E293B', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
               🔔 My Reminders
            </h2>
            
            <div style={{ backgroundColor: 'white', borderRadius: '20px', padding: '24px', boxShadow: '0 10px 30px rgba(0,0,0,0.08)', marginBottom: '24px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                    <div>
                        <label style={{ display: 'block', fontSize: '13px', fontWeight: '600', color: '#64748B', marginBottom: '8px' }}>Reminder Type</label>
                        <select 
                            value={reminderType}
                            onChange={(e) => setReminderType(e.target.value)}
                            style={{ width: '100%', padding: '14px', borderRadius: '12px', border: '1px solid #E2E8F0', backgroundColor: '#F8FAFC', outline: 'none', color: '#1E293B', fontWeight: '500' }}
                        >
                            <option>General Cleaning</option>
                            <option>Deep Cleaning</option>
                            <option>Bathroom Cleaning</option>
                            <option>Kitchen Cleaning</option>
                            <option>Custom</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display: 'block', fontSize: '13px', fontWeight: '600', color: '#64748B', marginBottom: '8px' }}>Frequency</label>
                        <select 
                            value={frequencyType}
                            onChange={(e) => setFrequencyType(e.target.value)}
                            style={{ width: '100%', padding: '14px', borderRadius: '12px', border: '1px solid #E2E8F0', backgroundColor: '#F8FAFC', outline: 'none', color: '#1E293B', fontWeight: '500' }}
                        >
                            <option value="15_days">Every 15 Days</option>
                            <option value="30_days">Every 30 Days</option>
                            <option value="60_days">Every 60 Days</option>
                            <option value="custom">Custom Date</option>
                        </select>
                    </div>
                </div>

                {frequencyType === 'custom' && (
                    <div style={{ marginBottom: '20px' }}>
                        <label style={{ display: 'block', fontSize: '13px', fontWeight: '600', color: '#64748B', marginBottom: '8px' }}>Select Date</label>
                        <input 
                            type="date" 
                            value={customDate}
                            onChange={(e) => setCustomDate(e.target.value)}
                            style={{ width: '100%', padding: '14px', borderRadius: '12px', border: '1px solid #E2E8F0', backgroundColor: '#F8FAFC', outline: 'none', color: '#1E293B', fontWeight: '500' }}
                        />
                    </div>
                )}

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div 
                            onClick={() => setRepeat(!repeat)}
                            style={{ 
                                width: '48px', height: '26px', borderRadius: '20px', 
                                backgroundColor: repeat ? '#8E44AD' : '#CBD5E1', 
                                position: 'relative', cursor: 'pointer', transition: 'all 0.2s'
                            }}
                        >
                            <div style={{ 
                                width: '20px', height: '20px', borderRadius: '50%', backgroundColor: 'white', 
                                position: 'absolute', top: '3px', left: repeat ? '25px' : '3px', transition: 'all 0.2s',
                                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                            }}></div>
                        </div>
                        <span style={{ fontSize: '14px', fontWeight: '600', color: '#1E293B' }}>Repeat Reminder</span>
                    </div>
                    <button 
                        onClick={handleSetReminder}
                        style={{ 
                            backgroundColor: '#8E44AD', color: 'white', border: 'none', 
                            padding: '12px 24px', borderRadius: '12px', fontWeight: '600', 
                            cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px',
                            boxShadow: '0 4px 12px rgba(142, 68, 173, 0.2)'
                        }}
                    >
                        <Plus size={18} /> Save Reminder
                    </button>
                </div>

                {reminderMessage && (
                    <div style={{ textAlign: 'center', fontSize: '14px', color: '#2ECC71', fontWeight: '600', backgroundColor: '#F0FDF4', padding: '12px', borderRadius: '12px', border: '1px solid #DCFCE7' }}>
                        <span style={{ marginRight: '6px' }}>📅</span> {reminderMessage}
                    </div>
                )}
            </div>

            {/* Active Reminders List */}
            <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#64748B', marginBottom: '16px' }}>📋 My Active Reminders</h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {myReminders.length > 0 ? (
                    myReminders.map(reminder => (
                        <div key={reminder.id} style={{ backgroundColor: 'white', padding: '16px 20px', borderRadius: '16px', border: '1px solid #F1F5F9', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                                <div style={{ width: '40px', height: '40px', borderRadius: '12px', backgroundColor: '#F3E5F5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    <Bell size={20} color="#8E44AD" />
                                </div>
                                <div>
                                    <h4 style={{ margin: '0 0 4px 0', fontSize: '15px', fontWeight: '700', color: '#1E293B' }}>{reminder.reminder_type}</h4>
                                    <div style={{ display: 'flex', gap: '12px', fontSize: '13px', color: '#64748B' }}>
                                        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                            <Calendar size={14} /> {reminder.next_reminder_date}
                                        </span>
                                        {reminder.repeat && (
                                            <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#8E44AD', fontWeight: '600' }}>
                                                <CheckCircle size={14} /> Repeats
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <button 
                                    onClick={() => handleDeleteReminder(reminder.id)}
                                    style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '8px', borderRadius: '50%', backgroundColor: '#FEE2E2', color: '#EF4444' }}
                                >
                                    <Trash2 size={18} />
                                </button>
                            </div>
                        </div>
                    ))
                ) : (
                    <div style={{ textAlign: 'center', padding: '30px', color: '#94A3B8', backgroundColor: 'white', borderRadius: '16px', border: '1px dashed #E2E8F0' }}>
                        No active reminders. Create one above!
                    </div>
                )}
            </div>
        </div>

      </div>

    </div>
  );
};

export default AIChat;
