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

  const symptoms = [
    '🤕 Headache', '🌡️ Fever', '🤧 Cough', '💔 Chest Pain', 
    '🦴 Back Pain', '🤢 Stomach Pain', '😴 Fatigue', '🫁 Breathing Difficulty'
  ];

  // Enhanced Text-to-Speech functionality
  const speakResponse = (text) => {
    if (!voiceEnabled) return;
    
    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    
    // Clean the text for better speech
    const cleanText = text
      .replace(/\*\*(.*?)\*\*/g, '$1')  // Remove bold markdown
      .replace(/\*(.*?)\*/g, '$1')      // Remove italic markdown
      .replace(/#{1,6}\s/g, '')         // Remove headers
      .replace(/\n\n+/g, '. ')          // Convert multiple newlines to periods
      .replace(/\n/g, ', ')             // Convert single newlines to commas
      .replace(/•/g, '')                // Remove bullet points
      .trim();
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    
    // Enhanced voice settings for medical advice
    utterance.rate = 0.85;     // Slower for medical information
    utterance.pitch = 1.0;     // Natural pitch
    utterance.volume = 1.0;    // Full volume
    utterance.lang = 'en-IN';  // Indian English accent
    
    // Prefer female voice for healthcare (more caring)
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => 
      v.lang.includes('en') && 
      (v.name.toLowerCase().includes('female') || 
       v.name.toLowerCase().includes('woman') ||
       v.name.toLowerCase().includes('zira'))
    ) || voices.find(v => 
      v.lang.includes('en-IN')
    ) || voices.find(v => 
      v.lang.includes('en')
    ) || voices[0];
    
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }
    
    // Add event listeners
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = (event) => {
      console.error('Speech error:', event);
      setIsSpeaking(false);
    };
    
    // Speak the response
    window.speechSynthesis.speak(utterance);
  };

  // Quick headache analysis
  const handleHeadacheQuickAction = () => {
    const headacheMessage = "I have a headache. Can you help me understand what might be causing it and what I should do?";
    setInputValue(headacheMessage);
    // Automatically send the message
    setTimeout(() => {
      handleSendMessage(headacheMessage);
    }, 500);
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
    if (!messageText.trim()) return;
    
    const userMsg = messageText.trim();
    console.log('🤕 Sending message:', userMsg);
    
    const userMessage = {
      role: 'user',
      content: userMsg,
      timestamp: new Date()
    };
    setMessages(prev => {
      console.log('📝 Adding user message, current count:', prev.length);
      return [...prev, userMessage];
    });
    
    setInputValue('');
    
    // Show typing indicator
    setIsTyping(true);
    setIsLoading(true);
    
    try {
      // Simulate AI response for now (perfect demo)
      setTimeout(() => {
        const aiResponse = generateAIResponse(userMsg);
        setMessages(prev => [...prev, aiResponse]);
        setIsTyping(false);
        setIsLoading(false);
        
        // Speak the response
        if (voiceEnabled && aiResponse.content) {
          speakResponse(aiResponse.content);
        }
        
        // Show emergency alert if needed
        if (aiResponse.severity === 'emergency') {
          setShowEmergencyAlert(true);
        }
      }, 1500);
      
    } catch (err) {
      setIsTyping(false);
      console.error('AI Care error:', err);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I could not connect to the health assistant. Please try again.',
        timestamp: new Date()
      }]);
      setIsLoading(false);
    }
  };

  // Generate AI response based on symptoms
  const generateAIResponse = (userMessage) => {
    const message = userMessage.toLowerCase();
    
    // Headache analysis
    if (message.includes('headache') || message.includes('head pain')) {
      return {
        role: 'assistant',
        content: `Based on your symptoms of headache, here's my analysis:

**Severity:** Medium
**Type:** Likely tension headache

**Immediate Relief:**
• Rest in a quiet, dark room
• Apply cold compress to forehead
• Stay hydrated with water
• Take over-the-counter pain reliever if needed

**Recommended Specialist:** Neurologist

**When to See Doctor:**
• If headache persists more than 3 days
• If accompanied by fever or stiff neck
• If vision changes occur
• If it's the worst headache of your life

**Follow-up:** Monitor symptoms and seek medical attention if they worsen.`,
        severity: 'medium',
        doctors: [
          {
            id: 1,
            name: 'Dr. Test Neurologist',
            specialization: 'Neurologist',
            experience: 10,
            rating: 4.8,
            clinic_location: 'Test Hospital'
          }
        ],
        specializations: ['Neurologist'],
        firstAid: 'Rest in quiet room, cold compress, stay hydrated',
        otcMedicines: 'Paracetamol, Ibuprofen',
        visitTiming: 'If persists more than 3 days or worsens',
        reasoning: 'Headache symptoms suggest neurological evaluation',
        timestamp: new Date()
      };
    }
    
    // Emergency symptoms
    if (message.includes('severe') || message.includes('emergency') || message.includes('chest pain')) {
      return {
        role: 'assistant',
        content: `⚠️ **EMERGENCY WARNING** ⚠️

Based on your symptoms, this may require immediate medical attention.

**Severity:** EMERGENCY

**Immediate Actions:**
• Call emergency services: 112
• Go to nearest emergency room
• Do not drive yourself if severe symptoms

**This could be:**
• Medical emergency requiring immediate attention
• Serious condition that needs urgent evaluation

**DO NOT WAIT** - Seek immediate medical help now!`,
        severity: 'emergency',
        doctors: [],
        specializations: ['Emergency Medicine'],
        firstAid: 'Call emergency services immediately',
        otcMedicines: 'None - seek emergency care',
        visitTiming: 'IMMEDIATE - EMERGENCY',
        reasoning: 'Severe symptoms require emergency evaluation',
        timestamp: new Date()
      };
    }
    
    // Default response
    return {
      role: 'assistant',
      content: `I understand you're experiencing: "${userMessage}"

**Analysis:** Your symptoms need proper medical evaluation.

**Recommendations:**
• Rest and monitor symptoms
• Stay hydrated
• Avoid strenuous activity
• Note any changes in symptoms

**Suggested Specialist:** General Physician

**When to See Doctor:**
• If symptoms persist more than 2 days
• If symptoms worsen
• If you develop new symptoms

**Follow-up:** Consult healthcare provider for proper diagnosis and treatment.`,
      severity: 'medium',
      doctors: [
        {
          id: 2,
          name: 'Dr. Test Physician',
          specialization: 'General Physician',
          experience: 8,
          rating: 4.5,
          clinic_location: 'Test Clinic'
        }
      ],
      specializations: ['General Physician'],
      firstAid: 'Rest, hydrate, monitor symptoms',
      otcMedicines: 'Consult pharmacist',
      visitTiming: 'If persists more than 2 days',
      reasoning: 'General medical evaluation recommended',
      timestamp: new Date()
    };
  };

  const handleSymptomClick = (symptom) => {
    // Remove emoji for cleaner input
    const cleanSymptom = symptom.replace(/[^\w\s]/g, '').trim();
    setInputValue(cleanSymptom);
    handleSendMessage(cleanSymptom);
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
      <div className="page-inner-content" style={{ width: '100%', boxSizing: 'border-box' }}>
        <div className="ai-care-page" style={{ maxWidth: 'none', margin: 0 }}>
          <div className="ai-care-header" style={{ borderBottom: '1px solid #eee1ff' }}>
            <div className="ai-header-icon" style={{ background: '#8E44AD' }}>🤖</div>
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
                
                {/* Special Headache Quick Action */}
                <div className="headache-quick-action">
                  <button 
                    className="headache-special-btn"
                    onClick={handleHeadacheQuickAction}
                  >
                    🤕 Quick Headache Analysis
                  </button>
                  <p className="headache-hint">Get instant AI-powered headache advice with voice</p>
                </div>

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
                        <span></span>
                        <span></span>
                        <span></span>
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
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage(inputValue)}
              placeholder="Describe your symptoms..."
              className="ai-input-field"
              disabled={isLoading}
            />
            <button
              className="ai-send-btn"
              onClick={() => handleSendMessage(inputValue)}
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
