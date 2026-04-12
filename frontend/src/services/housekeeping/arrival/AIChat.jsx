import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Sparkles, BarChart2, Bell, Calendar, Info, AlertTriangle, Trash2, Plus, CheckCircle, ToggleRight, ToggleLeft, Bot, Send, User, MessageCircle, Paperclip, Smile } from 'lucide-react';
import { useAuth } from '../../../context/AuthContext';
import api from '../../../shared/api';

const AIChat = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [cleaningStatus, setCleaningStatus] = useState(null);
  const [showUpgrade, setShowUpgrade] = useState(false);
  const [loading, setLoading] = useState(true);
  const [localMode, setLocalMode] = useState(false);
  
  // Chat State
  const [showChat, setShowChat] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [quickReplies, setQuickReplies] = useState([]);
  const messagesEndRef = useRef(null);
  
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

  // Chat Functions
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeChat = () => {
    console.log("🤖 initializeChat called!");
    alert("AI Chat is opening!");
    const welcomeMessage = {
      id: Date.now(),
      text: "Hello! I'm your ExpertEase Housekeeping Assistant! 🧹\n\nI can help you with:\n• Booking cleaning services\n• Setting cleaning reminders\n• Checking your hygiene score\n• Getting cleaning tips\n• Price estimates\n\nHow can I assist you today?",
      sender: 'ai',
      timestamp: new Date(),
      quickReplies: ['Book Cleaning', 'Check Hygiene Score', 'Set Reminder', 'Get Price Quote']
    };
    setMessages([welcomeMessage]);
    setQuickReplies(welcomeMessage.quickReplies);
    setShowChat(true);
    console.log("✅ Chat state updated - showChat:", true);
  };

  const sendMessage = async (messageText) => {
    if (!messageText.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: messageText,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setQuickReplies([]);
    setIsTyping(true);

    // Mock responses for when backend is not available
    const mockResponses = {
      'book cleaning': "Perfect! I can help you book a cleaning service right now! 🧹\n\n**Available Services:**\n• General Cleaning - ₹100 (Basic cleaning)\n• Deep Cleaning - ₹300 (Thorough cleaning)\n• Bathroom Cleaning - ₹200 (Bathroom specialist)\n• Kitchen Cleaning - ₹250 (Kitchen specialist)\n\n**Quick Booking:** Just tell me which service you want and I'll help you book it! For example: 'I want General Cleaning'",
      'check hygiene score': `Your current hygiene score is ${cleaningStatus?.hygiene_score || 7}/10! 📊\n\n**Status:** ${cleaningStatus?.status || 'Good'}\n**Last Clean:** ${cleaningStatus?.last_clean_date || 'Recently'}\n**Next Recommended:** ${cleaningStatus?.next_suggested_date || 'Soon'}\n\n**Recommendation:** ${cleaningStatus?.recommendation || 'Keep up the good work! Regular cleaning helps maintain a healthy home.'}`,
      'set reminder': "Perfect! Let's set up your cleaning reminder! ⏰\n\n**Step 1:** Look at the reminder form ABOVE this chat\n**Step 2:** Select 'General Cleaning' from the first dropdown\n**Step 3:** Choose 'Every 15 Days' from the frequency dropdown\n**Step 4:** Turn ON the 'Repeat Reminder' toggle (make it green)\n**Step 5:** Click the purple 'Set Reminder' button\n\n**You'll see:** ✅ Success message and your reminder will appear in the list below!\n\nNeed help? Just tell me what step you're stuck on!",
      'get price quote': "Here are our current prices with details! 💰\n\n**🧹 General Cleaning - ₹100**\n• Basic dusting and mopping\n• Kitchen and bathroom cleaning\n• Perfect for regular maintenance\n\n**🌟 Deep Cleaning - ₹300**\n• Thorough cleaning of all areas\n• Inside cabinets, windows, fans\n• Best for first-time or special occasions\n\n**🚿 Bathroom Cleaning - ₹200**\n• Tiles, toilet, sink, shower\n• Disinfection and stain removal\n• Bathroom specialist cleaning\n\n**🍳 Kitchen Cleaning - ₹250**\n• Platform, stove, chimney, cabinets\n• Oil and grease removal\n• Kitchen deep cleaning\n\n**Which service interests you?**",
      'general cleaning': "Great choice! General Cleaning is perfect for regular home maintenance! 🧹\n\n**What's included (₹100):**\n• Dusting all surfaces\n• Mopping floors\n• Kitchen cleaning (platform, sink)\n• Bathroom cleaning (toilet, floor)\n• Living room and bedroom cleaning\n\n**Ready to book?** Just say 'Book General Cleaning' and I'll help you schedule it!\n\n**Or set a reminder:** Say 'Set General Cleaning reminder for 15 days'",
      'default': "Hello! I'm your ExpertEase Housekeeping Assistant! 🧹\n\n**I can help you with:**\n🏠 **Book Cleaning Services** - General, Deep, Bathroom, Kitchen\n⏰ **Set Cleaning Reminders** - Never forget cleaning day!\n📊 **Check Hygiene Score** - Track your home's cleanliness\n💰 **Get Price Quotes** - Know our service prices\n🧹 **Cleaning Tips** - Expert advice for clean home\n\n**Just tell me what you need!** For example:\n• 'Book General Cleaning'\n• 'Set reminder for 15 days'\n• 'What's my hygiene score?'\n• 'Show me prices'\n\n**What would you like to do today?**"
    };

    // Simulate API delay
    setTimeout(() => {
      const lowerMessage = messageText.toLowerCase();
      let responseText = mockResponses.default;
      
      // Better keyword matching for more specific responses
      if (lowerMessage.includes('general cleaning') || lowerMessage.includes('genral') || lowerMessage.includes('genaral')) {
        responseText = mockResponses['general cleaning'];
      } else if (lowerMessage.includes('book') && (lowerMessage.includes('cleaning') || lowerMessage.includes('service'))) {
        responseText = mockResponses['book cleaning'];
      } else if (lowerMessage.includes('hygiene') || lowerMessage.includes('score')) {
        responseText = mockResponses['check hygiene score'];
      } else if (lowerMessage.includes('reminder') || lowerMessage.includes('set') || lowerMessage.includes('15') || lowerMessage.includes('day')) {
        responseText = mockResponses['set reminder'];
      } else if (lowerMessage.includes('price') || lowerMessage.includes('cost') || lowerMessage.includes('quote') || lowerMessage.includes('rs') || lowerMessage.includes('₹')) {
        responseText = mockResponses['get price quote'];
      } else if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hellp')) {
        responseText = mockResponses['default'];
      }

      const aiMessage = {
        id: Date.now() + 1,
        text: responseText,
        sender: 'ai',
        timestamp: new Date(),
        quickReplies: ['Book General Cleaning', 'Set Reminder for 15 Days', 'Check Hygiene Score', 'Show Prices']
      };

      setMessages(prev => [...prev, aiMessage]);
      setQuickReplies(aiMessage.quickReplies);
      setIsTyping(false);
    }, 1000);

    // Try real API if available (fallback to mock)
    try {
      const response = await api.post('/api/ai/chat', {
        message: messageText,
        user_id: user?.id || 'anonymous'
      });

      const aiMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        sender: 'ai',
        timestamp: new Date(),
        quickReplies: response.data.quick_replies || []
      };

      setMessages(prev => [...prev, aiMessage]);
      setQuickReplies(aiMessage.quickReplies);
      setIsTyping(false);
    } catch (error) {
      console.log('Using mock response - backend not available');
      // Mock response already handled above
    }
  };

  const handleQuickReply = (reply) => {
    sendMessage(reply);
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
      console.log("🔔 Setting reminder:", { reminderType, frequencyType, customDate, repeat });
      
      // Always use local mode since backend isn't working
      const nextDate = computeNextDate(frequencyType, customDate);
      const newItem = {
        id: Date.now(),
        reminder_type: reminderType,
        next_reminder_date: nextDate,
        repeat
      };
      
      console.log("📅 New reminder item:", newItem);
      
      const updated = [newItem, ...readLocalReminders()];
      writeLocalReminders(updated);
      setMyReminders(updated);
      setReminderMessage(`✅ Reminder set for ${nextDate}`);
      
      console.log("✅ Reminder saved successfully!");
      console.log("📋 All reminders:", updated);
      
      setTimeout(() => setReminderMessage(''), 5000);
      
      // Show success alert
      alert(`✅ Reminder set successfully!\n\nType: ${reminderType}\nDate: ${nextDate}\n${repeat ? 'Repeats' : 'One time'}`);
      
    } catch (error) {
      console.error("Failed to set reminder", error);
      alert("❌ Failed to set reminder. Please try again.");
    }
  };

  const handleDeleteReminder = async (id) => {
    try {
      console.log("🗑️ Deleting reminder:", id);
      
      // Always use local mode
      const updated = readLocalReminders().filter(r => r.id !== id);
      writeLocalReminders(updated);
      setMyReminders(updated);
      
      console.log("✅ Reminder deleted successfully!");
      alert("✅ Reminder deleted successfully!");
      
    } catch (error) {
      console.error("Failed to delete reminder", error);
      alert("❌ Failed to delete reminder. Please try again.");
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
          <button 
            onClick={() => navigate('/housekeeping/home')}
            style={{ 
              background: 'rgba(255,255,255,0.2)', 
              border: 'none', 
              borderRadius: '12px', 
              padding: '8px', 
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <ArrowLeft size={20} color="white" />
          </button>
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

      {/* AI Chat Window */}
      {showChat && (
        <div style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          width: '380px',
          height: '600px',
          backgroundColor: 'white',
          borderRadius: '20px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          zIndex: 10000,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}>
          {/* Chat Header */}
          <div style={{
            backgroundColor: '#8E44AD',
            padding: '20px',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Bot size={24} color="white" />
              <div>
                <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold' }}>AI Assistant</h3>
                <p style={{ margin: 0, fontSize: '12px', opacity: 0.9 }}>Always here to help</p>
              </div>
            </div>
            <button
              onClick={() => setShowChat(false)}
              style={{
                background: 'none',
                border: 'none',
                color: 'white',
                cursor: 'pointer',
                fontSize: '24px',
                padding: '0',
                width: '30px',
                height: '30px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '50%',
                backgroundColor: 'rgba(255,255,255,0.2)'
              }}
            >
              ×
            </button>
          </div>

          {/* Chat Messages */}
          <div style={{
            flex: 1,
            padding: '20px',
            overflowY: 'auto',
            backgroundColor: '#F9FAFB'
          }}>
            {messages.map((message) => (
              <div key={message.id} style={{
                display: 'flex',
                justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                marginBottom: '16px'
              }}>
                <div style={{
                  maxWidth: '80%',
                  padding: '12px 16px',
                  borderRadius: '18px',
                  backgroundColor: message.sender === 'user' ? '#8E44AD' : 'white',
                  color: message.sender === 'user' ? 'white' : '#1E293B',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                }}>
                  <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.4' }}>
                    {message.text}
                  </p>
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '16px' }}>
                <div style={{
                  padding: '12px 16px',
                  borderRadius: '18px',
                  backgroundColor: 'white',
                  color: '#64748B',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                }}>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#CBD5E1', animation: 'bounce 1.4s infinite' }}></div>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#CBD5E1', animation: 'bounce 1.4s infinite 0.2s' }}></div>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#CBD5E1', animation: 'bounce 1.4s infinite 0.4s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Replies */}
          {quickReplies.length > 0 && (
            <div style={{
              padding: '16px 20px',
              backgroundColor: 'white',
              borderTop: '1px solid #E2E8F0'
            }}>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {quickReplies.map((reply, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuickReply(reply)}
                    style={{
                      padding: '8px 12px',
                      borderRadius: '16px',
                      border: '1px solid #E2E8F0',
                      backgroundColor: 'white',
                      color: '#64748B',
                      fontSize: '12px',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.backgroundColor = '#8E44AD';
                      e.target.style.color = 'white';
                      e.target.style.borderColor = '#8E44AD';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.backgroundColor = 'white';
                      e.target.style.color = '#64748B';
                      e.target.style.borderColor = '#E2E8F0';
                    }}
                  >
                    {reply}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Chat Input */}
          <div style={{
            padding: '16px 20px',
            backgroundColor: 'white',
            borderTop: '1px solid #E2E8F0'
          }}>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage(inputMessage)}
                placeholder="Type your message..."
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  borderRadius: '20px',
                  border: '1px solid #E2E8F0',
                  backgroundColor: '#F9FAFB',
                  outline: 'none',
                  fontSize: '14px'
                }}
              />
              <button
                onClick={() => sendMessage(inputMessage)}
                disabled={!inputMessage.trim() || isTyping}
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  border: 'none',
                  backgroundColor: inputMessage.trim() && !isTyping ? '#8E44AD' : '#CBD5E1',
                  color: 'white',
                  cursor: inputMessage.trim() && !isTyping ? 'pointer' : 'not-allowed',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 0.2s'
                }}
              >
                <Send size={18} color={inputMessage.trim() && !isTyping ? 'white' : '#94A3B8'} />
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default AIChat;
