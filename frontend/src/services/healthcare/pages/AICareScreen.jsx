import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import '../styles/AICareScreen.css';
import '../styles/healthcare-shared.css';
import HealthcareSidebarLayout from '../components/HealthcareSidebarLayout';
import HealthcareBottomNav from '../components/HealthcareBottomNav';

const AICareScreen = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [showEmergencyAlert, setShowEmergencyAlert] = useState(false);
  const messagesEndRef = useRef(null);
  const token = localStorage.getItem('token');

  const symptoms = [
    'Headache', 'Fever', 'Cough', 'Chest Pain', 
    'Back Pain', 'Stomach Pain', 'Fatigue', 'Breathing Difficulty'
  ];

  // Text-to-Speech functionality
  const speakResponse = (text) => {
    if (!voiceEnabled) return;
    
    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Voice settings
    utterance.rate = 0.9;      // slightly slower
    utterance.pitch = 1.0;     // natural pitch
    utterance.volume = 1.0;    // full volume
    utterance.lang = 'en-IN';  // Indian English
    
    // Prefer female voice if available
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => 
      v.lang.includes('en') && 
      v.name.toLowerCase().includes('female')
    ) || voices.find(v => 
      v.lang.includes('en-IN')
    ) || voices[0];
    
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }
    
    // Visual indicator while speaking
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    
    window.speechSynthesis.speak(utterance);
  };

  // Load voices on mount
  useEffect(() => {
    const loadVoices = () => {
      window.speechSynthesis.getVoices();
    };
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
    
    // Cleanup: stop speech when leaving page
    return () => {
      window.speechSynthesis.cancel();
    };
  }, []);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ 
      behavior: 'smooth' 
    });
  }, [messages]);

  const handleSendMessage = async (messageText) => {
    const userMsg = messageText || inputValue.trim();
    if (!userMsg) return;
    
    // Add user message to chat
    const userMessage = {
      role: 'user',
      content: userMsg,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    
    setInputValue('');
    
    // Show typing indicator
    setIsTyping(true);
    setIsLoading(true);
    
    try {
      // Prefer the organized healthcare API route (auth-protected).
      // Falls back to legacy route if needed (some environments).
      const endpointCandidates = ['/api/healthcare/ai-care', '/healthcare/ai-care'];
      let res = null;
      let lastErr = null;

      for (const url of endpointCandidates) {
        try {
          res = await fetch(url, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({
              message: userMsg,
              user_id: user?.id || user?.user_id || user?.userId || 'default',
              conversation_history: [...messages, userMessage].map((m) => ({
                role: m.role,
                content: m.content,
              })),
            }),
          });
          // If legacy endpoint doesn't exist, it may return HTML 404. Try next candidate.
          if (res.status === 404) continue;
          break;
        } catch (e) {
          lastErr = e;
          res = null;
        }
      }

      if (!res) {
        throw lastErr || new Error('Network error');
      }

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.message || errData.error || `Server error ${res.status}`);
      }

      const data = await res.json();
      setIsTyping(false);

      // Backend returns either a triage question or a final diagnosis
      const responseText =
        data.response ||
        data.message ||
        data.question ||
        data.advice ||
        'I could not generate a response. Please try again.';
      
      const aiMessage = {
        role: 'assistant',
        content: responseText,
        stage: data.stage || 'triage',
        severity: data.severity || 'low',
        doctors: data.suggested_doctors || data.doctors || [],
        firstAid: data.first_aid || '',
        otcMedicines: data.otc_medicines || '',
        visitTiming: data.when_to_visit_doctor || '',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
      // SPEAK: response
      if (voiceEnabled && responseText) {
        speakResponse(responseText);
      }
      
      // Show emergency banner if severity is emergency
      if (data.severity === 'emergency') {
        setShowEmergencyAlert(true);
      }
      
    } catch (err) {
      setIsTyping(false);
      console.error('AI Care error:', err);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I could not connect to the health assistant. Please try again.',
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const handleSymptomClick = (symptom) => {
    setInputValue(symptom);
    handleSendMessage(symptom);
  };

  const toggleVoice = () => {
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
    setVoiceEnabled(prev => !prev);
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const hasMessages = messages.length > 0;

  return (
    <HealthcareSidebarLayout>
      <div className="page-inner-content">
        <div className="ai-care-page">
          <div className="ai-care-header">
            <div className="ai-header-icon">🤖</div>
            <div className="ai-header-content">
              <div className="ai-header-title">AI Health Assistant</div>
              <div className="ai-header-subtitle">Powered by AI • Not a diagnosis</div>
            </div>
            <button
              className="voice-toggle-btn"
              onClick={toggleVoice}
              title={isSpeaking ? 'Stop speaking' : 'Enable voice'}
            >
              {isSpeaking ? '🔊' : '🔇'}
            </button>
          </div>

          {showEmergencyAlert && (
            <div className="emergency-banner">
              <span className="emergency-icon">⚠️</span>
              <span>For emergencies, call </span>
              <span className="emergency-number">112</span>
              <span> immediately</span>
            </div>
          )}

          <div className="ai-messages-area">
            {!hasMessages ? (
              <>
                <div className="welcome-card">
                  <div className="welcome-card-title">
                    <span>✨</span>
                    <span>Welcome!</span>
                  </div>
                  <div className="welcome-card-text">
                    Describe your symptoms and I&apos;ll help you understand what might be going on and recommend the right
                    specialist.
                  </div>
                </div>

                <div className="quick-start-label">Quick start:</div>
                <div className="quick-start-pills">
                  {symptoms.map((symptom, index) => (
                    <button key={index} className="symptom-pill" onClick={() => handleSymptomClick(symptom)}>
                      {symptom}
                    </button>
                  ))}
                </div>
              </>
            ) : (
              <div className="chat-messages">
                {messages.map((message, index) => (
                  <div key={index} className={`message ${message.role}`}>
                    {message.role === 'assistant' && <div className="ai-icon-indicator">🤖</div>}
                    <div className="message-bubble">
                      <div className="message-content">{message.content}</div>
                      {message.role === 'assistant' && message.doctors && message.doctors.length > 0 && (
                        <div className="doctor-suggestions">
                          {message.doctors.map((doctor, idx) => (
                            <div key={idx} className="doctor-suggestion-card">
                              <div>
                                <strong>{doctor.name}</strong>
                                <span className="doctor-specialization">{doctor.specialization}</span>
                              </div>
                              <button className="book-now-btn" onClick={() => navigate(`/healthcare/book/${doctor.id}`)}>
                                Book Now
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                      <div className="message-time">{formatTime(message.timestamp)}</div>
                    </div>
                  </div>
                ))}

                {isTyping && (
                  <div className="message assistant">
                    <div className="ai-icon-indicator">🤖</div>
                    <div className="message-bubble">
                      <div className="typing-indicator">
                        <span className="typing-dot"></span>
                        <span className="typing-dot"></span>
                        <span className="typing-dot"></span>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          <div className="ai-input-bar">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Describe your symptoms..."
              className="ai-input-field"
              disabled={isLoading}
            />
            <button
              className="ai-send-btn"
              onClick={() => handleSendMessage()}
              disabled={!inputValue.trim() || isLoading}
            >
              ➤
            </button>
          </div>

          <HealthcareBottomNav activeTab="ai-care" />
        </div>
      </div>
    </HealthcareSidebarLayout>
  );
};

export default AICareScreen;
