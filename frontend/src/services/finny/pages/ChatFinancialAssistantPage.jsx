import { useState, useEffect, useRef } from 'react';
import { ArrowLeft, Send, Bot, User, TrendingUp, Briefcase, Newspaper, BookOpen, Zap, Volume2, VolumeX, Square } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../../../shared/api';
import '../styles/AiCoachPage.css';

const QUICK_ACTIONS = [
  { label: 'Analyze my spending', icon: TrendingUp, message: 'Analyze my spending patterns' },
  { label: 'My portfolio',        icon: Briefcase,  message: 'analyze my portfolio' },
  { label: 'Market news',         icon: Newspaper,  message: 'what is happening in the market today' },
  { label: 'What is SIP?',        icon: BookOpen,   message: 'what is SIP and how does it work' },
  { label: 'Diversification',     icon: Zap,        message: 'explain diversification' },
];

const TYPE_BADGE = {
  stock_analysis:     { label: 'Stock Analysis', color: '#2563EB' },
  portfolio_analysis: { label: 'Portfolio',      color: '#7C3AED' },
  knowledge_query:    { label: 'Education',      color: '#059669' },
  market_news:        { label: 'Market News',    color: '#D97706' },
  general_query:      { label: 'General',        color: '#6B7280' },
};

const stripMarkdown = (text) => {
  if (!text || typeof text !== 'string') return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/#{1,6}\s/g, '')
    .replace(/`{1,3}(.*?)`{1,3}/g, '$1')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/^\s*[-•]\s/gm, '')
    .replace(/\n{2,}/g, '. ')
    .trim();
};

const TypingIndicator = () => (
  <div className="typing-bubble">
    <div className="ai-avatar"><Bot size={16} color="white" /></div>
    <div className="bubble ai-msg">
      <span className="dot" /><span className="dot" /><span className="dot" />
    </div>
  </div>
);

const ChatFinancialAssistantPage = () => {
  const navigate = useNavigate();
  const [messages, setMessages]     = useState([]);
  const [input, setInput]           = useState('');
  const [loading, setLoading]       = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [speakingId, setSpeakingId] = useState(null);
  const bottomRef    = useRef(null);
  const synthRef     = useRef(window.speechSynthesis);
  const speakingRef  = useRef(null);   // mirrors speakingId without stale closure
  const ttsEnabledRef = useRef(true);  // mirrors ttsEnabled without stale closure

  // Seed welcome message
  useEffect(() => {
    setMessages([{
      id: 'welcome',
      sender: 'ai',
      content: "👋 Hi! I'm your AI Financial Coach powered by Gemini. Ask me anything about stocks, investments, financial concepts, or market news. I provide educational insights only — not financial advice.",
      type: 'general_query',
      timestamp: new Date().toISOString(),
    }]);
    // Pre-load voices
    if (window.speechSynthesis) {
      window.speechSynthesis.getVoices();
      window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
    }
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => () => synthRef.current?.cancel(), []);

  // Keep refs in sync
  useEffect(() => { speakingRef.current = speakingId; }, [speakingId]);
  useEffect(() => { ttsEnabledRef.current = ttsEnabled; }, [ttsEnabled]);

  const speakText = (text, msgId) => {
    const synth = synthRef.current;
    if (!synth) return;

    synth.cancel();

    if (speakingRef.current === msgId) {
      speakingRef.current = null;
      setSpeakingId(null);
      return;
    }

    const clean = stripMarkdown(text);
    if (!clean) return;

    const utt = new SpeechSynthesisUtterance(clean);
    utt.lang  = 'en-IN';
    utt.rate  = 0.92;
    utt.pitch = 1;

    // Pick best available English voice
    const voices = synth.getVoices();
    const preferred =
      voices.find(v => v.lang === 'en-IN') ||
      voices.find(v => v.lang.startsWith('en') && v.name.toLowerCase().includes('google')) ||
      voices.find(v => v.lang.startsWith('en') && !v.localService) ||
      voices.find(v => v.lang.startsWith('en'));
    if (preferred) utt.voice = preferred;

    utt.onstart = () => { speakingRef.current = msgId; setSpeakingId(msgId); };
    utt.onend   = () => { speakingRef.current = null;  setSpeakingId(null); };
    utt.onerror = (e) => { console.warn('TTS error:', e.error); speakingRef.current = null; setSpeakingId(null); };

    synth.speak(utt);
  };

  const stopSpeaking = () => {
    synthRef.current?.cancel();
    speakingRef.current = null;
    setSpeakingId(null);
  };

  const sendMessage = async (text) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;

    stopSpeaking();
    setInput('');

    const userMsg = { id: Date.now(), sender: 'user', content: msg, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await api.post('/api/money/chat', { message: msg });
      const rawResponse = res.data.ai_response || res.data.response;
      const aiContent = typeof rawResponse === 'string'
        ? rawResponse
        : rawResponse
          ? JSON.stringify(rawResponse)
          : 'No response received.';
      const aiMsgId = Date.now() + 1;
      const aiMsg = {
        id: aiMsgId,
        sender: 'ai',
        content: aiContent,
        type: res.data.message_type || 'general_query',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, aiMsg]);

      // Auto-read — use ref so we always have fresh ttsEnabled value
      if (ttsEnabledRef.current) {
        // Wait for voices to be ready, then speak
        const trySpeak = () => {
          const voices = synthRef.current?.getVoices() || [];
          if (voices.length > 0) {
            speakText(aiContent, aiMsgId);
          } else {
            setTimeout(() => speakText(aiContent, aiMsgId), 500);
          }
        };
        setTimeout(trySpeak, 100);
      }
    } catch {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: 'ai',
        content: '⚠️ Could not reach the AI service. Please check your connection and try again.',
        type: 'general_query',
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  const toggleTts = () => {
    if (ttsEnabled) stopSpeaking();
    setTtsEnabled(v => !v);
  };

  return (
    <div className="ai-coach-page">
      <div className="ai-coach-header">
        <button className="ai-back-btn" onClick={() => { stopSpeaking(); navigate('/finny'); }}>
          <ArrowLeft size={20} />
        </button>
        <div className="ai-header-info">
          <div className="ai-header-avatar"><Bot size={20} color="white" /></div>
          <div>
            <h1>AI Financial Coach</h1>
            <p>Powered by Gemini AI</p>
          </div>
        </div>
        <button
          className={`tts-toggle ${ttsEnabled ? 'tts-on' : 'tts-off'}`}
          onClick={toggleTts}
          title={ttsEnabled ? 'Mute voice' : 'Enable voice'}
        >
          {ttsEnabled ? <Volume2 size={18} /> : <VolumeX size={18} />}
        </button>
      </div>

      <div className="ai-disclaimer">
        📚 For educational purposes only — not financial advice
      </div>

      <div className="quick-actions-bar">
        {QUICK_ACTIONS.map((qa) => (
          <button key={qa.label} className="quick-chip" onClick={() => sendMessage(qa.message)}>
            <qa.icon size={13} />
            {qa.label}
          </button>
        ))}
      </div>

      <div className="ai-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`msg-row ${msg.sender === 'user' ? 'user-row' : 'ai-row'}`}>
            {msg.sender === 'ai' && <div className="ai-avatar"><Bot size={16} color="white" /></div>}

            <div className={`bubble ${msg.sender === 'user' ? 'user-msg' : 'ai-msg'}`}>
              {msg.sender === 'ai' && msg.type && TYPE_BADGE[msg.type] && (
                <span className="type-badge" style={{ background: TYPE_BADGE[msg.type].color }}>
                  {TYPE_BADGE[msg.type].label}
                </span>
              )}
              <p style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</p>
              <div className="bubble-footer">
                <span className="msg-time">
                  {new Date(msg.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
                </span>
                {msg.sender === 'ai' && (
                  <button
                    className={`speak-btn ${speakingId === msg.id ? 'speaking' : ''}`}
                    onClick={() => speakingId === msg.id ? stopSpeaking() : speakText(msg.content, msg.id)}
                    title={speakingId === msg.id ? 'Stop reading' : 'Read aloud'}
                  >
                    {speakingId === msg.id ? <Square size={12} /> : <Volume2 size={12} />}
                  </button>
                )}
              </div>
            </div>

            {msg.sender === 'user' && <div className="user-avatar"><User size={16} color="white" /></div>}
          </div>
        ))}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      <div className="ai-input-bar">
        <textarea
          className="ai-input"
          placeholder="Ask about stocks, investments, financial concepts..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          rows={1}
          disabled={loading}
        />
        <button
          className="ai-send-btn"
          onClick={() => sendMessage()}
          disabled={!input.trim() || loading}
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
};

export default ChatFinancialAssistantPage;
