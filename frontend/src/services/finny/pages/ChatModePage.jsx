import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, HelpCircle } from 'lucide-react';
import { chatApi } from '../api/chatApi';
import ChatAssistant from '../components/ChatAssistant';
import TodaySummary from '../components/TodaySummary';
import ChatInput from '../components/ChatInput';
import '../styles/ChatModePage.css';

const ChatModePage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [todayData, setTodayData] = useState({
    total: 0,
    categories: {},
    date: new Date().toISOString().split('T')[0],
    transactionCount: 0
  });
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchTodaySummary();
  }, []);

  const fetchTodaySummary = async () => {
    try {
      const result = await chatApi.getTodaySummary();
      if (result.success) {
        setTodayData(result.data);
      }
    } catch (error) {
      console.error('Failed to fetch today summary:', error);
    }
  };

  const handleSendMessage = async (input) => {
    setLoading(true);
    setMessage(input);
    
    try {
      const result = await chatApi.processChatInput(input);
      
      if (result.success) {
        // Refresh today's summary after adding transactions
        await fetchTodaySummary();
        setMessage(result.message);
      } else {
        setMessage(result.message);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessage('Failed to process your input. Please try again.');
    } finally {
      setLoading(false);
      
      // Clear message after 3 seconds
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const handleHelpExamples = () => {
    navigate('/finny/chat/examples');
  };

  return (
    <div className="chat-mode-page">
          {/* Header */}
          <div className="header">
            <div className="header-content">
              <button 
                className="back-button" 
                onClick={() => navigate('/finny')}
              >
                <ArrowLeft size={20} />
              </button>
              <div className="header-text">
                <h1 className="header-title">Chat Mode</h1>
                <p className="header-subtitle">Natural language tracking</p>
              </div>
              <button 
                className="help-button" 
                onClick={handleHelpExamples}
              >
                <HelpCircle size={20} />
                <span>Help & Examples</span>
              </button>
            </div>
          </div>

          {/* Main Content */}
          <div className="main-content">
            <div className="content-grid">
              {/* Left Panel - Chat Assistant */}
              <div className="left-panel">
                <ChatAssistant />
                {message && (
                  <div className="status-message">
                    {message}
                  </div>
                )}
              </div>

              {/* Right Panel - Today Summary */}
              <div className="right-panel">
                <TodaySummary todayData={todayData} />
              </div>
            </div>
          </div>

          {/* Chat Input */}
          <div className="chat-input-section">
            <ChatInput onSendMessage={handleSendMessage} loading={loading} />
          </div>

    </div>
  );
};

export default ChatModePage;
