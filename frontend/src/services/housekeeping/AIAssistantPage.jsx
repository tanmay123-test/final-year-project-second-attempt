import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Bot, Bell, Send } from 'lucide-react';
import './AIAssistantPage.css';

import api from '../../shared/api';
import { useAuth } from '../../context/AuthContext';

const AIAssistantPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const quickSuggestions = [
    "Cleaning tips",
    "Give me a recipe",
    "Home hacks",
    "Service help"
  ];

  const handleSend = async (text = query) => {
    if (!text.trim()) return;

    const userMessage = { text, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setQuery('');
    setIsLoading(true);

    try {
      const userId = user?.id || user?.user_id;
      const response = await api.post('/api/ai/chat', {
        query: text,
        user_id: userId
      });

      const { response: aiResponse, mode } = response.data;
      
      let modeIcon = "🏠";
      if (mode === "cooking") modeIcon = "🍳";
      else if (mode === "cleaning") modeIcon = "🧹";
      else if (mode === "service") modeIcon = "🛎️";

      const aiMessage = { 
        text: aiResponse, 
        sender: 'ai', 
        mode, 
        modeIcon 
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage = {
        text: "Sorry, I'm having trouble connecting right now. Please try again later.",
        sender: 'ai',
        mode: 'error',
        modeIcon: '❌'
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  const handleChipClick = (suggestion) => {
    setQuery(suggestion);
    handleSend(suggestion);
  };

  return (
    <div className="ai-assistant-page">
      {/* Header */}
      <header className="ai-header">
        <div className="header-left">
          <button className="icon-btn-circle" onClick={() => navigate('/housekeeping/home')}>
            <ArrowLeft size={20} color="white" />
          </button>
          <div className="icon-btn-circle">
            <Bot size={20} color="white" />
          </div>
        </div>
        
        <div className="header-center">
          <h1>Home Assistant</h1>
          <p>Your smart home helper</p>
        </div>

        <div className="header-right">
          <button className="icon-btn-circle" onClick={() => navigate('/housekeeping/ai-chat')}>
            <Bell size={20} color="white" />
          </button>
        </div>
      </header>

      {/* Chat Area */}
      <main className="ai-chat-body">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="bot-icon-container">
              <Bot size={40} className="purple-bot" />
            </div>
            <h2>Your Smart Home Assistant</h2>
            <p className="subtitle">Ask me anything — recipes, cleaning tips, home hacks, or book a service</p>
            
            <div className="suggestions-grid">
              <div className="suggestions-row">
                {quickSuggestions.slice(0, 3).map(s => (
                  <button key={s} className="chip" onClick={() => handleChipClick(s)}>
                    {s}
                  </button>
                ))}
              </div>
              <div className="suggestions-row">
                <button className="chip" onClick={() => handleChipClick(quickSuggestions[3])}>
                  {quickSuggestions[3]}
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="messages-container">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message-wrapper ${msg.sender}`}>
                {msg.sender === 'ai' && (
                  <div className="mode-tag">
                    {msg.modeIcon} {msg.mode.charAt(0).toUpperCase() + msg.mode.slice(1)}
                  </div>
                )}
                <div className="message-bubble">
                  {msg.text}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message-wrapper ai">
                <div className="message-bubble loading">
                  Thinking...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      {/* Input Area */}
      <div className="ai-input-container">
        <div className="pill-input-wrapper">
          <input 
            type="text" 
            placeholder="Ask anything about your home..." 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          />
          <button className="send-btn" onClick={() => handleSend()}>
            <Send size={20} color="white" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIAssistantPage;
