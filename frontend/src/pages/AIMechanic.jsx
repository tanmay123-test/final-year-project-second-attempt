import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Send, 
  Mic, 
  MicOff, 
  Bot, 
  User, 
  Wrench,
  ArrowLeft,
  Paperclip,
  Camera,
  Volume2,
  VolumeX,
  Speaker
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { aiService } from '../shared/api';

const AIMechanic = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your AI Mechanic Assistant. I can help you diagnose car issues, provide maintenance tips, and guide you through repairs. What seems to be the problem with your vehicle?",
      sender: 'ai',
      timestamp: new Date(),
      typing: false
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [synthesis, setSynthesis] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Focus input when component mounts
    if (inputRef.current) {
      inputRef.current.focus();
    }

    // Initialize speech synthesis
    if ('speechSynthesis' in window) {
      setSynthesis(window.speechSynthesis);
    }

    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;
      recognitionInstance.lang = 'en-US';

      recognitionInstance.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsRecording(false);
        
        // Auto-send after voice input
        setTimeout(() => {
          handleSendMessage();
        }, 500);
      };

      recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
        
        // Show error message
        const errorMessage = {
          id: Date.now() + 10,
          text: "Sorry, I couldn't hear you clearly. Please try again or type your message.",
          sender: 'ai',
          timestamp: new Date(),
          typing: false
        };
        setMessages(prev => [...prev, errorMessage]);
      };

      recognitionInstance.onend = () => {
        setIsRecording(false);
      };

      setRecognition(recognitionInstance);
    } else {
      console.warn('Speech recognition not supported in this browser');
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const speakText = (text) => {
    if (!synthesis || isMuted) return;

    // Cancel any ongoing speech
    synthesis.cancel();

    // Create new utterance
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9; // Slightly slower for clarity
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    // Try to use a female voice for AI assistant
    const voices = synthesis.getVoices();
    const femaleVoice = voices.find(voice => 
      voice.name.includes('Female') || 
      voice.name.includes('Samantha') || 
      voice.name.includes('Karen') ||
      voice.name.includes('Google US English Female')
    );
    
    if (femaleVoice) {
      utterance.voice = femaleVoice;
    }

    synthesis.speak(utterance);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isProcessing) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage.trim(),
      sender: 'user',
      timestamp: new Date(),
      typing: false
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsProcessing(true);
    setIsTyping(true);

    // Add typing indicator
    const typingIndicator = {
      id: Date.now() + 1,
      text: '',
      sender: 'ai',
      timestamp: new Date(),
      typing: true
    };
    setMessages(prev => [...prev, typingIndicator]);

    try {
      const response = await aiService.analyzeMechanicIssues({
        symptoms: inputMessage.trim(),
        user_id: user?.user_id || 'anonymous',
        service_type: 'mechanic'
      });

      // Remove typing indicator
      setMessages(prev => prev.filter(msg => msg.id !== typingIndicator.id));
      setIsTyping(false);

      const aiResponse = {
        id: Date.now() + 2,
        text: response.data?.diagnosis || response.data?.response || response.data?.answer || 'I apologize, but I couldn\'t process your request. Please try again.',
        sender: 'ai',
        timestamp: new Date(),
        typing: false
      };

      setMessages(prev => [...prev, aiResponse]);
      speakText(aiResponse.text);

    } catch (error) {
      console.error('AI Mechanic Error:', error);
      
      // Remove typing indicator
      setMessages(prev => prev.filter(msg => msg.id !== typingIndicator.id));
      setIsTyping(false);

      // Try fallback to general AI service if mechanic-specific fails
      try {
        console.log('Trying fallback to healthcare AI...');
        const fallbackResponse = await aiService.analyzeSymptoms({
          symptoms: inputMessage.trim(),
          user_id: user?.user_id || 'anonymous',
          service_type: 'mechanic'
        });

        const fallbackAiResponse = {
          id: Date.now() + 4,
          text: fallbackResponse.data?.diagnosis || fallbackResponse.data?.response || fallbackResponse.data?.answer || fallbackResponse.data?.message || 'I apologize, but I couldn\'t process your request. Please try again.',
          sender: 'ai',
          timestamp: new Date(),
          typing: false
        };

        setMessages(prev => [...prev, fallbackAiResponse]);
        speakText(fallbackAiResponse.text);
      } catch (fallbackError) {
        console.error('Fallback AI also failed:', fallbackError);
        
        // Final fallback - provide a helpful response
        const errorMessage = {
          id: Date.now() + 3,
          text: `I'm having trouble connecting to my AI diagnostic system right now. However, I can still help with common car issues:\n\n🔧 **Quick Tips:**\n• Check engine light: Check gas cap first, then visit mechanic\n• Car won't start: Check battery terminals and try jump start\n• Strange noises: Note when they occur and describe them\n• Overheating: Pull over safely and let engine cool\n\nFor specific help, please try again in a moment or describe your issue with more details like:\n• What happens (noise, warning light, etc.)\n• When it occurs (starting, driving, braking)\n• Any recent changes or maintenance`,
          sender: 'ai',
          timestamp: new Date(),
          typing: false
        };

        setMessages(prev => [...prev, errorMessage]);
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleVoiceRecord = () => {
    if (!recognition) {
      const errorMessage = {
        id: Date.now() + 11,
        text: "Voice recognition is not supported in your browser. Please use Chrome or Edge for voice input.",
        sender: 'ai',
        timestamp: new Date(),
        typing: false
      };
      setMessages(prev => [...prev, errorMessage]);
      return;
    }

    if (isRecording) {
      recognition.stop();
      setIsRecording(false);
    } else {
      recognition.start();
      setIsRecording(true);
      
      // Add visual feedback
      const recordingMessage = {
        id: Date.now() + 12,
        text: "🎤 Listening... Speak clearly about your car issue.",
        sender: 'ai',
        timestamp: new Date(),
        typing: false
      };
      setMessages(prev => [...prev, recordingMessage]);
    }
  };

  const handleFileUpload = () => {
    // Handle file upload (images, videos of car issues)
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*,video/*';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        console.log('File uploaded:', file);
        // Here you would upload and analyze the file
      }
    };
    input.click();
  };

  const handleCameraCapture = () => {
    // Handle camera capture
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.capture = 'environment';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        console.log('Camera capture:', file);
        // Here you would upload and analyze the image
      }
    };
    input.click();
  };

  const quickActions = [
    { icon: '⚠️', text: 'Check Engine Light', action: 'My check engine light is on' },
    { icon: '🔧', text: 'Strange Noise', action: 'My car is making a strange noise' },
    { icon: '🛢️', text: 'Oil Change', action: 'When should I change my oil' },
    { icon: '🔋', text: 'Battery Issues', action: 'My car won\'t start' },
    { icon: '🌡️', text: 'Overheating', action: 'My car is overheating' },
    { icon: '🛞', text: 'Tire Problems', action: 'I have tire problems' }
  ];

  const handleSpeakLastMessage = () => {
    const lastAiMessage = messages.filter(msg => msg.sender === 'ai').pop();
    if (lastAiMessage && synthesis) {
      speakText(lastAiMessage.text);
    }
  };

  const handleQuickAction = (action) => {
    setInputMessage(action);
    setTimeout(() => handleSendMessage(), 100);
  };

  return (
    <div className="ai-mechanic-container">
      <style>{`
        .ai-mechanic-container {
          height: 100vh;
          display: flex;
          flex-direction: column;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .ai-mechanic-header {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          padding: 1rem;
          display: flex;
          align-items: center;
          gap: 1rem;
          box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
          z-index: 10;
        }

        .header-back-btn {
          background: #f3f4f6;
          border: none;
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.3s;
        }

        .header-back-btn:hover {
          background: #e5e7eb;
          transform: scale(1.05);
        }

        .header-info {
          flex: 1;
        }

        .header-title {
          font-size: 1.2rem;
          font-weight: 700;
          color: #1f2937;
          margin: 0;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .header-subtitle {
          font-size: 0.875rem;
          color: #6b7280;
          margin: 0;
        }

        .header-actions {
          display: flex;
          gap: 0.5rem;
        }

        .header-action-btn {
          background: #f3f4f6;
          border: none;
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.3s;
          color: #6b7280;
        }

        .header-action-btn:hover:not(:disabled) {
          background: #e5e7eb;
          color: #3b82f6;
          transform: scale(1.05);
        }

        .header-action-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .status-indicator {
          width: 8px;
          height: 8px;
          background: #10b981;
          border-radius: 50%;
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        .ai-mechanic-messages {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .message {
          max-width: 80%;
          padding: 0.75rem 1rem;
          border-radius: 1rem;
          animation: messageSlide 0.3s ease-out;
        }

        @keyframes messageSlide {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .message.user {
          align-self: flex-end;
          background: #3b82f6;
          color: white;
          border-bottom-right-radius: 0.25rem;
        }

        .message.ai {
          align-self: flex-start;
          background: rgba(255, 255, 255, 0.9);
          color: #1f2937;
          border-bottom-left-radius: 0.25rem;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .message-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.25rem;
          font-size: 0.75rem;
          opacity: 0.7;
        }

        .message-content {
          line-height: 1.5;
          white-space: pre-wrap;
        }

        .typing-indicator {
          display: flex;
          gap: 0.25rem;
          padding: 0.5rem;
        }

        .typing-dot {
          width: 8px;
          height: 8px;
          background: #6b7280;
          border-radius: 50%;
          animation: typing 1.4s infinite;
        }

        .typing-dot:nth-child(2) {
          animation-delay: 0.2s;
        }

        .typing-dot:nth-child(3) {
          animation-delay: 0.4s;
        }

        @keyframes typing {
          0%, 60%, 100% {
            transform: translateY(0);
          }
          30% {
            transform: translateY(-10px);
          }
        }

        .quick-actions {
          padding: 1rem;
          background: rgba(255, 255, 255, 0.9);
          border-top: 1px solid rgba(255, 255, 255, 0.2);
        }

        .quick-actions-title {
          font-size: 0.875rem;
          font-weight: 600;
          color: #4b5563;
          margin-bottom: 0.75rem;
        }

        .quick-actions-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
          gap: 0.5rem;
        }

        .quick-action-btn {
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          padding: 0.5rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          cursor: pointer;
          transition: all 0.2s;
          font-size: 0.875rem;
        }

        .quick-action-btn:hover {
          background: #f9fafb;
          border-color: #3b82f6;
          transform: translateY(-1px);
        }

        .ai-mechanic-input {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          padding: 1rem;
          border-top: 1px solid rgba(255, 255, 255, 0.2);
        }

        .input-container {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: white;
          border: 2px solid #e5e7eb;
          border-radius: 2rem;
          padding: 0.5rem;
          transition: border-color 0.2s;
        }

        .input-container:focus-within {
          border-color: #3b82f6;
        }

        .input-actions {
          display: flex;
          gap: 0.25rem;
        }

        .input-action-btn {
          background: transparent;
          border: none;
          width: 36px;
          height: 36px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.2s;
          color: #6b7280;
        }

        .input-action-btn:hover {
          background: #f3f4f6;
          color: #3b82f6;
        }

        .input-action-btn.recording {
          background: #ef4444;
          color: white;
          animation: recording 1s infinite;
        }

        @keyframes recording {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        .message-input {
          flex: 1;
          border: none;
          outline: none;
          padding: 0.5rem;
          font-size: 1rem;
          resize: none;
          max-height: 100px;
        }

        .send-btn {
          background: #3b82f6;
          border: none;
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.2s;
          color: white;
        }

        .send-btn:hover:not(:disabled) {
          background: #2563eb;
          transform: scale(1.05);
        }

        .send-btn:disabled {
          background: #d1d5db;
          cursor: not-allowed;
        }

        @media (max-width: 768px) {
          .message {
            max-width: 90%;
          }
          
          .quick-actions-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }
      `}</style>

      {/* Header */}
      <div className="ai-mechanic-header">
        <button className="header-back-btn" onClick={() => navigate(-1)}>
          <ArrowLeft size={20} />
        </button>
        <div className="header-info">
          <h1 className="header-title">
            <Bot size={24} color="#3b82f6" />
            AI Mechanic Assistant
            <div className="status-indicator"></div>
          </h1>
          <p className="header-subtitle">Online • Ready to help with your car issues</p>
        </div>
        <div className="header-actions">
          <button 
            className="header-action-btn" 
            onClick={handleSpeakLastMessage}
            title="Speak last message"
            disabled={!messages.some(msg => msg.sender === 'ai')}
          >
            <Speaker size={20} />
          </button>
          <button 
            className="header-action-btn" 
            onClick={() => setIsMuted(!isMuted)}
            title={isMuted ? "Unmute" : "Mute"}
          >
            {isMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="ai-mechanic-messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.sender}`}>
            <div className="message-header">
              {message.sender === 'ai' ? <Bot size={16} /> : <User size={16} />}
              <span>{message.sender === 'ai' ? 'AI Mechanic' : 'You'}</span>
              <span>•</span>
              <span>{formatTime(message.timestamp)}</span>
            </div>
            <div className="message-content">
              {message.typing ? (
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              ) : (
                message.text
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <div className="quick-actions-title">Quick Actions:</div>
        <div className="quick-actions-grid">
          {quickActions.map((action, index) => (
            <button
              key={index}
              className="quick-action-btn"
              onClick={() => handleQuickAction(action.action)}
              disabled={isProcessing}
            >
              <span>{action.icon}</span>
              <span>{action.text}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="ai-mechanic-input">
        <div className="input-container">
          <div className="input-actions">
            <button 
              className="input-action-btn" 
              onClick={handleFileUpload}
              title="Upload file"
            >
              <Paperclip size={20} />
            </button>
            <button 
              className="input-action-btn" 
              onClick={handleCameraCapture}
              title="Take photo"
            >
              <Camera size={20} />
            </button>
          </div>
          <textarea
            ref={inputRef}
            className="message-input"
            placeholder="Describe your car issue..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            rows={1}
            disabled={isProcessing}
          />
          <button 
            className={`input-action-btn ${isRecording ? 'recording' : ''}`}
            onClick={handleVoiceRecord}
            title={isRecording ? "Stop recording" : "Voice input"}
          >
            {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
          </button>
          <button 
            className="send-btn"
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isProcessing}
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIMechanic;
