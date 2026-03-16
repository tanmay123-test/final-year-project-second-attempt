import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { aiService, doctorService } from '../../../services/api';
import BottomNav from '../../../components/BottomNav';
import { Bot, HelpCircle, Stethoscope, AlertCircle, CheckCircle2, ChevronLeft, Volume2, Square } from 'lucide-react';

const AICare = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [symptoms, setSymptoms] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [stage, setStage] = useState('idle');
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState(null);
  const [suggestedDoctors, setSuggestedDoctors] = useState([]);
  const audioCtxRef = useRef(null);
  const lastTickRef = useRef(0);
  const synthRef = useRef(typeof window !== 'undefined' ? window.speechSynthesis : null);
  const speakingRef = useRef(false);
  const [messages, setMessages] = useState([]);
  const endRef = useRef(null);

  const common = ['Headache', 'Fever', 'Cough', 'Back Pain', 'Fatigue', 'Stomach Pain'];

  const addChip = (text) => {
    if (!symptoms.toLowerCase().includes(text.toLowerCase())) {
      setSymptoms((s) => (s ? s + ', ' + text : text));
    }
  };

  const ensureAudio = () => {
    if (!audioCtxRef.current) {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      if (Ctx) audioCtxRef.current = new Ctx();
    }
    return audioCtxRef.current;
  };

  const playTick = () => {
    const ctx = ensureAudio();
    if (!ctx) return;
    const now = ctx.currentTime;
    if (now - lastTickRef.current < 0.04) return;
    lastTickRef.current = now;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'square';
    osc.frequency.setValueAtTime(660, now);
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.exponentialRampToValueAtTime(0.08, now + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.06);
    osc.connect(gain).connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.07);
  };

  const playChime = () => {
    const ctx = ensureAudio();
    if (!ctx) return;
    const now = ctx.currentTime;
    const o1 = ctx.createOscillator();
    const g1 = ctx.createGain();
    o1.type = 'sine';
    o1.frequency.setValueAtTime(523.25, now);
    g1.gain.setValueAtTime(0.0001, now);
    g1.gain.exponentialRampToValueAtTime(0.1, now + 0.01);
    g1.gain.exponentialRampToValueAtTime(0.0001, now + 0.2);
    o1.connect(g1).connect(ctx.destination);
    o1.start(now);
    o1.stop(now + 0.21);
    const o2 = ctx.createOscillator();
    const g2 = ctx.createGain();
    o2.type = 'sine';
    o2.frequency.setValueAtTime(659.25, now + 0.12);
    g2.gain.setValueAtTime(0.0001, now + 0.12);
    g2.gain.exponentialRampToValueAtTime(0.08, now + 0.14);
    g2.gain.exponentialRampToValueAtTime(0.0001, now + 0.3);
    o2.connect(g2).connect(ctx.destination);
    o2.start(now + 0.12);
    o2.stop(now + 0.31);
  };

  const handleKeyDown = (e) => {
    if (e.key.length === 1 || e.key === 'Backspace' || e.key === 'Enter' || e.key === 'Spacebar' || e.code === 'Space') {
      playTick();
    }
  };

  const stopSpeaking = () => {
    const synth = synthRef.current;
    if (synth && synth.speaking) {
      synth.cancel();
      speakingRef.current = false;
    }
  };

  const selectVoice = () => {
    const synth = synthRef.current;
    if (!synth) return null;
    const voices = synth.getVoices ? synth.getVoices() : [];
    const prefer = voices.find(v => /en-IN/i.test(v.lang));
    return prefer || voices.find(v => /en-US/i.test(v.lang)) || voices[0] || null;
    };

  const buildSpeechText = (data) => {
    const parts = [];
    if (data.message) parts.push(data.message);
    if (data.severity) parts.push(`Severity ${data.severity}`);
    if (data.first_aid) parts.push(`First aid: ${data.first_aid}`);
    if (data.otc_medicines) {
      const otc = typeof data.otc_medicines === 'string' ? data.otc_medicines : (data.otc_medicines.recommended || '');
      if (otc) parts.push(`Over the counter medicines: ${otc}`);
    }
    if (data.when_to_visit_doctor) parts.push(`When to visit a doctor: ${data.when_to_visit_doctor}`);
    if (Array.isArray(data.suggested_specializations) && data.suggested_specializations.length > 0) {
      parts.push(`Suggested specializations: ${data.suggested_specializations.join(', ')}`);
    }
    return parts.join('. ');
  };

  const speakResult = (data) => {
    stopSpeaking();
    const synth = synthRef.current;
    if (!synth || !data) return;
    const text = buildSpeechText(data);
    if (!text) return;
    const u = new SpeechSynthesisUtterance(text);
    const v = selectVoice();
    if (v) u.voice = v;
    u.rate = 1;
    u.pitch = 1;
    speakingRef.current = true;
    u.onend = () => { speakingRef.current = false; };
    synth.speak(u);
  };

  const addMessage = (role, content) => {
    setMessages((m) => [...m, { role, content, id: Date.now() + Math.random() }]);
  };

  useEffect(() => {
    if (endRef.current) endRef.current.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const fetchDoctorsIfNeeded = async (specializations) => {
    try {
      if (!specializations || specializations.length === 0) return;
      const res = await Promise.all(
        specializations.slice(0, 1).map((spec) => doctorService.getDoctorsBySpecialization(spec))
      );
      const docs = res.flatMap((r) => r.data.doctors || []);
      setSuggestedDoctors(docs.slice(0, 5));
    } catch {
      setSuggestedDoctors([]);
    }
  };

  const analyze = async () => {
    setError('');
    if (!symptoms.trim()) {
      setError('Please describe your symptoms');
      return;
    }
    setLoading(true);
    const userText = symptoms.trim();
    addMessage('user', userText);
    try {
      const payload = { symptoms, user_id: user?.user_id || 'default' };
      const res = await aiService.analyzeSymptoms(payload);
      const data = res.data || {};
      const s = data.stage || 'triage';
      setStage(s);
      if (s === 'triage') {
        setQuestion(data.question || '');
        setResult(null);
        const reply = data.question || 'Please provide more details.';
        addMessage('assistant', reply);
        speakResult({ message: reply });
      } else if (s === 'final' || s === 'emergency') {
        setResult(data);
        setQuestion('');
        await fetchDoctorsIfNeeded(data.suggested_specializations || []);
        playChime();
        speakResult(data);
        const reply = buildSpeechText(data);
        addMessage('assistant', reply);
      } else {
        setResult(null);
      }
    } catch (e) {
      setError(e.response?.data?.error || 'Something went wrong');
    } finally {
      setLoading(false);
      setSymptoms('');
    }
  };

  return (
    <div className="ai-care-page">
      <div className="ai-header">
        <button className="back-btn" onClick={() => navigate(-1)} aria-label="Back">
          <ChevronLeft size={22} />
        </button>
        <div className="header-title">
          <Bot size={22} />
          <h1>AI Care</h1>
        </div>
      </div>

      <div className="content">
        <div className="how-it-works">
          <div className="hiw-icon">
            <HelpCircle size={20} />
          </div>
          <div>
            <h2>How it works</h2>
            <p>Describe your symptoms in detail. Our AI will analyze them and recommend suitable doctors.</p>
          </div>
        </div>

        <div className="chat">
          <div className="chat-stream" role="log" aria-live="polite">
            {messages.map(m => (
              <div key={m.id} className={`msg ${m.role}`}>
                <div className="bubble">{m.content}</div>
              </div>
            ))}
            {loading && (
              <div className="msg assistant">
                <div className="bubble typing">Analyzing…</div>
              </div>
            )}
            <div ref={endRef} />
          </div>
          {error && (
            <div className="message error" style={{ marginTop: '0.5rem' }}>
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}
          <div className="composer">
            <textarea
              className="symptoms-input"
              rows={2}
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              onKeyDown={(e) => {
                handleKeyDown(e);
                if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') analyze();
              }}
              placeholder="Type your symptoms or follow-up..."
            />
            <button
              className={`primary-btn ${!symptoms.trim() ? 'disabled' : ''}`}
              onClick={analyze}
              disabled={!symptoms.trim() || loading}
            >
              {loading ? 'Sending…' : 'Send'}
            </button>
          </div>
          <div className="chips-title">Common symptoms:</div>
          <div className="chips">
            {common.map((c) => (
              <button key={c} className="chip" onClick={() => addChip(c)}>{c}</button>
            ))}
          </div>
        </div>

        {result && (
          <div className="result-section">
            <div className="result-card">
              <div className="result-header">
                <CheckCircle2 size={18} />
                <h3>Assessment</h3>
              </div>
              {result.message ? <p className="result-message">{result.message}</p> : null}
              {result.severity ? <p className="badge">Severity: {result.severity}</p> : null}
              {result.first_aid ? (
                <div className="kv">
                  <span>First Aid</span>
                  <p>{result.first_aid}</p>
                </div>
              ) : null}
              {result.otc_medicines ? (
                <div className="kv">
                  <span>OTC Medicines</span>
                  <p>
                    {typeof result.otc_medicines === 'string'
                      ? result.otc_medicines
                      : result.otc_medicines.recommended || ''}
                  </p>
                </div>
              ) : null}
              {result.when_to_visit_doctor ? (
                <div className="kv">
                  <span>When to visit</span>
                  <p>{result.when_to_visit_doctor}</p>
                </div>
              ) : null}
                  <div className="tts-controls">
                    <button className="ghost-btn" onClick={() => speakResult(result)}>
                      <Volume2 size={16} />
                      <span style={{ marginLeft: 6 }}>Read Aloud</span>
                    </button>
                    <button className="ghost-btn" onClick={stopSpeaking}>
                      <Square size={14} />
                      <span style={{ marginLeft: 6 }}>Stop</span>
                    </button>
                  </div>
            </div>

            {Array.isArray(result.suggested_specializations) && result.suggested_specializations.length > 0 && (
              <div className="specs-section">
                <h3>Suggested Specializations</h3>
                <div className="chips">
                  {result.suggested_specializations.map((s) => (
                    <button
                      key={s}
                      className="chip"
                      onClick={() => navigate(`/doctors?spec=${encodeURIComponent(s)}`)}
                    >
                      <Stethoscope size={16} />
                      <span style={{ marginLeft: 6 }}>{s}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {suggestedDoctors.length > 0 && (
              <div className="doctors-section">
                <h3>Top Matches</h3>
                <div className="doctors-list">
                  {suggestedDoctors.map((doc) => (
                    <div key={doc.id} className="doctor-item">
                      <div className="avatar">{(doc.name || 'D').charAt(0)}</div>
                      <div className="info">
                        <div className="name">{doc.name}</div>
                        <div className="spec">{doc.specialization}</div>
                      </div>
                      <button className="book-btn" onClick={() => navigate(`/book/${doc.id}`)}>Book</button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <BottomNav />

      <style>{`
        .ai-care-page { background-color: var(--background-light); min-height: 100vh; padding-bottom: 80px; }
        .ai-header { position: sticky; top: 0; z-index: 10; background: var(--medical-gradient); padding: 1rem 1.25rem; display: flex; align-items: center; gap: 0.75rem; color: white; }
        .back-btn { background: rgba(255,255,255,0.2); width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: none; color: white; }
        .header-title { display: flex; align-items: center; gap: 0.5rem; }
        .header-title h1 { margin: 0; font-size: 1.25rem; font-weight: 700; }
        .content { padding: 1.25rem; max-width: 720px; margin: 0 auto; display: flex; flex-direction: column; gap: 1rem; }
        .how-it-works { background: white; border-radius: 16px; padding: 1rem; display: flex; gap: 0.75rem; align-items: flex-start; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        .hiw-icon { background: #F4ECF7; color: #8E44AD; width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .how-it-works h2 { margin: 0 0 0.25rem 0; font-size: 1rem; }
        .how-it-works p { margin: 0; color: var(--text-secondary); font-size: 0.9rem; }
        .chat { background: white; border-radius: 16px; padding: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: flex; flex-direction: column; gap: 0.75rem; }
        .section-label { font-weight: 600; color: var(--text-primary); }
        .symptoms-input { width: 100%; min-height: 48px; resize: vertical; border: 1px solid #E5E7EB; border-radius: 12px; padding: 0.75rem; font-size: 0.95rem; }
        .chat-stream { max-height: 50vh; overflow-y: auto; display: flex; flex-direction: column; gap: 0.5rem; padding: 0.25rem; }
        .msg { display: flex; }
        .msg.user { justify-content: flex-end; }
        .msg.assistant { justify-content: flex-start; }
        .bubble { max-width: 80%; padding: 0.6rem 0.8rem; border-radius: 14px; background: #F5F7FA; color: #2C3E50; }
        .msg.user .bubble { background: #8E44AD; color: white; }
        .typing { opacity: 0.7; }
        .composer { display: flex; gap: 0.5rem; align-items: flex-end; }
        .chips-title { color: var(--text-secondary); font-size: 0.9rem; }
        .chips { display: flex; flex-wrap: wrap; gap: 0.5rem; }
        .chip { background: #F5F7FA; border: none; padding: 0.4rem 0.8rem; border-radius: 999px; color: #2C3E50; cursor: pointer; }
        .primary-btn { margin-top: 0.25rem; background: linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%); color: white; border: none; padding: 0.9rem; border-radius: 14px; font-weight: 700; cursor: pointer; }
        .primary-btn.disabled { opacity: 0.5; cursor: not-allowed; }
        .message { display: flex; align-items: center; gap: 0.5rem; padding: 0.6rem 0.75rem; border-radius: 10px; }
        .message.error { background: #FDEDEC; color: #C0392B; }
        .triage-card { background: white; border-radius: 16px; padding: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        .triage-card h3 { margin: 0 0 0.25rem 0; }
        .result-section { display: flex; flex-direction: column; gap: 1rem; }
        .result-card { background: white; border-radius: 16px; padding: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        .result-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem; }
        .result-message { margin: 0.25rem 0 0.5rem 0; }
        .badge { display: inline-block; background: #F4ECF7; color: #8E44AD; padding: 0.25rem 0.5rem; border-radius: 8px; font-weight: 600; font-size: 0.8rem; }
        .kv { margin-top: 0.5rem; }
        .kv span { font-weight: 600; color: var(--text-primary); }
        .kv p { margin: 0.25rem 0 0 0; color: var(--text-secondary); }
        .specs-section { background: white; border-radius: 16px; padding: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        .doctors-section { background: white; border-radius: 16px; padding: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        .doctors-list { display: flex; flex-direction: column; gap: 0.75rem; }
        .doctor-item { display: flex; align-items: center; gap: 0.75rem; }
        .doctor-item .avatar { width: 42px; height: 42px; border-radius: 12px; background: #E8DAEF; display: flex; align-items: center; justify-content: center; font-weight: 700; color: #8E44AD; }
        .doctor-item .info { flex: 1; }
        .doctor-item .name { font-weight: 700; }
        .doctor-item .spec { color: var(--text-secondary); font-size: 0.9rem; }
        .doctor-item .book-btn { background: var(--accent-blue); color: white; border: none; padding: 0.5rem 0.8rem; border-radius: 10px; cursor: pointer; }
        .tts-controls { margin-top: 0.5rem; display: flex; gap: 0.5rem; }
        .ghost-btn { background: #F5F7FA; color: #2C3E50; border: 1px solid #E5E7EB; padding: 0.45rem 0.7rem; border-radius: 10px; cursor: pointer; display: inline-flex; align-items: center; }
      `}</style>
    </div>
  );
};

export default AICare;

