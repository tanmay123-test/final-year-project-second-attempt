import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { aiService } from '../../shared/api';
import { 
  ArrowLeft, Send, Brain, Activity, 
  Heart, Thermometer, Head, Eye, Stomach,
  Home, Compass, Calendar, User
} from 'lucide-react';

const AICare = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [symptoms, setSymptoms] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [step, setStep] = useState('input');

  const commonSymptoms = [
    { icon: Brain, label: 'Headache', color: '#8E44AD' },
    { icon: Heart, label: 'Chest Pain', color: '#E74C3C' },
    { icon: Thermometer, label: 'Fever', color: '#F39C12' },
    { icon: Head, label: 'Body Pain', color: '#9B59B6' },
    { icon: Eye, label: 'Eye Issues', color: '#3498DB' },
    { icon: Stomach, label: 'Stomach Issues', color: '#2ECC71' }
  ];

  const handleSymptomSubmit = async () => {
    if (!symptoms.trim()) return;
    
    setLoading(true);
    try {
      const response = await aiService.analyzeSymptoms({ symptoms });
      setResult(response.data);
      setStep('result');
    } catch (error) {
      console.error('AI Analysis failed:', error);
      setResult({
        severity: 'medium',
        first_aid: 'Rest and hydrate. If symptoms persist, consult a doctor.',
        otc_medicines: 'Paracetamol for fever, Ibuprofen for pain',
        when_to_visit_doctor: 'If fever persists for more than 2 days',
        suggested_specializations: ['General Physician'],
        suggested_doctors: []
      });
      setStep('result');
    } finally {
      setLoading(false);
    }
  };

  const handleCommonSymptom = async (symptom) => {
    setSymptoms(symptom);
    await handleSymptomSubmit();
  };

  const handleBack = () => {
    navigate('/doctors');
  };

  return (
    <div className="ai-care-dashboard">
      {/* Header Section */}
      <div className="ai-header">
        <div className="header-left">
          <button className="back-btn" onClick={handleBack}>
            <ArrowLeft size={24} color="white" />
          </button>
          <span className="logo-text">ExpertEase</span>
        </div>
        <div className="header-title">AI Care</div>
      </div>

      <div className="ai-content">
        {/* How it works section */}
        <div className="how-it-works">
          <h2>How it works</h2>
          <div className="steps">
            <div className="step">
              <div className="step-number">1</div>
              <p>Enter your symptoms</p>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <p>AI analyzes your condition</p>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <p>Get doctor recommendations</p>
            </div>
          </div>
        </div>

        {/* AI Analysis Section */}
        <div className="ai-analysis">
          {step === 'input' && (
            <>
              <div className="input-section">
                <h3>Describe your symptoms</h3>
                <div className="symptom-input-container">
                  <textarea
                    value={symptoms}
                    onChange={(e) => setSymptoms(e.target.value)}
                    placeholder="Type your symptoms here..."
                    className="symptom-input"
                    rows={4}
                  />
                  <button 
                    className="analyze-btn"
                    onClick={handleSymptomSubmit}
                    disabled={loading || !symptoms.trim()}
                  >
                    {loading ? 'Analyzing...' : 'Analyze'}
                  </button>
                </div>
              </div>

              <div className="common-symptoms">
                <h4>Common Symptoms</h4>
                <div className="symptoms-grid">
                  {commonSymptoms.map((symptom, index) => (
                    <button
                      key={index}
                      className="symptom-btn"
                      onClick={() => handleCommonSymptom(symptom.label)}
                      style={{ borderLeftColor: symptom.color }}
                    >
                      <symptom.icon size={24} color={symptom.color} />
                      <span>{symptom.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}

          {step === 'result' && result && (
            <div className="result-section">
              <div className="result-header">
                <Brain size={32} color="#8E44AD" />
                <h3>AI Analysis Results</h3>
              </div>
              
              <div className="severity-indicator">
                <span className={`severity-badge ${result.severity}`}>
                  {result.severity?.toUpperCase() || 'MEDIUM'}
                </span>
                <p>Based on your symptoms, this appears to be a {result.severity || 'medium'} severity condition.</p>
              </div>

              <div className="recommendation-card">
                <h4>🏥 First Aid</h4>
                <p>{result.first_aid || 'Rest and hydrate. Monitor symptoms closely.'}</p>
              </div>

              <div className="recommendation-card">
                <h4>💊 Suggested Medications</h4>
                <p>{result.otc_medicines || 'Consult pharmacist for appropriate medication'}</p>
              </div>

              <div className="recommendation-card">
                <h4>👨‍⚕️ When to Visit Doctor</h4>
                <p>{result.when_to_visit_doctor || 'If symptoms persist or worsen'}</p>
              </div>

              {result.suggested_specializations && result.suggested_specializations.length > 0 && (
                <div className="specialization-suggestions">
                  <h4>🏥 Recommended Specializations</h4>
                  <div className="specs-list">
                    {result.suggested_specializations.map((spec, index) => (
                      <span key={index} className="spec-tag">{spec}</span>
                    ))}
                  </div>
                </div>
              )}

              <button className="new-analysis-btn" onClick={() => setStep('input')}>
                New Analysis
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Navigation */}
      <div className="bottom-navigation">
        <div className="nav-item" onClick={() => navigate('/dashboard')}>
          <Home size={20} color="#7F8C8D" />
          <span>Home</span>
        </div>
        <div className="nav-item active" onClick={() => navigate('/ai-care')}>
          <Compass size={20} color="#8E44AD" />
          <span>AI Care</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/doctors')}>
          <Activity size={20} color="#7F8C8D" />
          <span>Explore</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/appointments')}>
          <Calendar size={20} color="#7F8C8D" />
          <span>Appointments</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/profile')}>
          <User size={20} color="#7F8C8D" />
          <span>Profile</span>
        </div>
      </div>

      <style>{`
        .ai-care-dashboard {
          background-color: var(--background-light);
          min-height: 100vh;
          padding-bottom: 80px;
        }

        /* Header Styles */
        .ai-header {
          background: var(--medical-gradient);
          padding: 1rem 1rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
          color: white;
          box-shadow: 0 4px 20px rgba(142, 68, 173, 0.2);
        }

        .header-left {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .back-btn {
          background: none;
          border: none;
          cursor: pointer;
          padding: 0.5rem;
          border-radius: 50%;
          transition: background 0.2s;
        }

        .back-btn:hover {
          background: rgba(255, 255, 255, 0.2);
        }

        .logo-text {
          font-size: 1.2rem;
          font-weight: 700;
          color: white;
        }

        .header-title {
          font-size: 1.1rem;
          font-weight: 600;
          color: white;
        }

        /* Content Styles */
        .ai-content {
          padding: 1rem;
        }

        /* How it works section */
        .how-it-works {
          background: white;
          border-radius: 20px;
          padding: 1.5rem;
          margin-bottom: 1.5rem;
          box-shadow: var(--shadow-sm);
        }

        .how-it-works h2 {
          font-size: 1.2rem;
          font-weight: 700;
          color: var(--text-primary);
          margin-bottom: 1rem;
        }

        .steps {
          display: flex;
          justify-content: space-between;
          gap: 1rem;
        }

        .step {
          flex: 1;
          text-align: center;
          padding: 1rem 0.5rem;
        }

        .step-number {
          width: 40px;
          height: 40px;
          background: var(--medical-gradient);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: 700;
          margin: 0 auto 0.5rem;
        }

        .step p {
          font-size: 0.9rem;
          color: var(--text-secondary);
          line-height: 1.4;
        }

        /* AI Analysis Section */
        .ai-analysis {
          background: white;
          border-radius: 20px;
          padding: 1.5rem;
          box-shadow: var(--shadow-sm);
        }

        .input-section h3 {
          font-size: 1.1rem;
          font-weight: 700;
          color: var(--text-primary);
          margin-bottom: 1rem;
        }

        .symptom-input-container {
          margin-bottom: 2rem;
        }

        .symptom-input {
          width: 100%;
          padding: 1rem;
          border: 2px solid #E5E7EB;
          border-radius: 16px;
          font-size: 1rem;
          resize: vertical;
          outline: none;
          transition: border-color 0.2s;
        }

        .symptom-input:focus {
          border-color: var(--accent-blue);
        }

        .analyze-btn {
          background: var(--medical-gradient);
          color: white;
          border: none;
          padding: 1rem 2rem;
          border-radius: 16px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: opacity 0.2s;
          margin-top: 1rem;
          width: 100%;
        }

        .analyze-btn:hover:not(:disabled) {
          opacity: 0.9;
        }

        .analyze-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        /* Common Symptoms */
        .common-symptoms {
          margin-top: 2rem;
        }

        .common-symptoms h4 {
          font-size: 1rem;
          font-weight: 700;
          color: var(--text-primary);
          margin-bottom: 1rem;
        }

        .symptoms-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 1rem;
        }

        .symptom-btn {
          background: white;
          border: 2px solid #E5E7EB;
          border-left: 4px solid #8E44AD;
          border-radius: 12px;
          padding: 1rem;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .symptom-btn:hover {
          border-color: var(--accent-blue);
          transform: translateY(-2px);
          box-shadow: var(--shadow-md);
        }

        .symptom-btn span {
          font-size: 0.9rem;
          font-weight: 500;
          color: var(--text-primary);
        }

        /* Results Section */
        .result-section {
          animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .result-header {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .result-header h3 {
          font-size: 1.3rem;
          font-weight: 700;
          color: var(--text-primary);
        }

        .severity-indicator {
          background: #F8F9FA;
          border-radius: 16px;
          padding: 1rem;
          margin-bottom: 1.5rem;
          border-left: 4px solid var(--accent-blue);
        }

        .severity-badge {
          display: inline-block;
          padding: 0.5rem 1rem;
          border-radius: 20px;
          font-weight: 700;
          font-size: 0.8rem;
          margin-bottom: 0.5rem;
        }

        .severity-badge.low {
          background: #D4EDDA;
          color: #155724;
        }

        .severity-badge.medium {
          background: #FFF3CD;
          color: #856404;
        }

        .severity-badge.high {
          background: #F8D7DA;
          color: #721C24;
        }

        .recommendation-card {
          background: #F8F9FA;
          border-radius: 16px;
          padding: 1rem;
          margin-bottom: 1rem;
        }

        .recommendation-card h4 {
          font-size: 1rem;
          font-weight: 700;
          color: var(--text-primary);
          margin-bottom: 0.5rem;
        }

        .recommendation-card p {
          font-size: 0.9rem;
          color: var(--text-secondary);
          line-height: 1.5;
        }

        .specialization-suggestions {
          margin-top: 1.5rem;
        }

        .specialization-suggestions h4 {
          font-size: 1rem;
          font-weight: 700;
          color: var(--text-primary);
          margin-bottom: 0.5rem;
        }

        .specs-list {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .spec-tag {
          background: var(--medical-gradient);
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 20px;
          font-size: 0.8rem;
          font-weight: 500;
        }

        .new-analysis-btn {
          background: white;
          color: var(--accent-blue);
          border: 2px solid var(--accent-blue);
          padding: 0.75rem 1.5rem;
          border-radius: 12px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          margin-top: 1rem;
        }

        .new-analysis-btn:hover {
          background: var(--accent-blue);
          color: white;
        }

        /* Bottom Navigation */
        .bottom-navigation {
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          background: white;
          border-top: 1px solid #E5E7EB;
          display: flex;
          justify-content: space-around;
          padding: 0.5rem 0;
          z-index: 1000;
        }

        .nav-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.25rem;
          padding: 0.5rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .nav-item.active {
          color: var(--accent-blue);
        }

        .nav-item span {
          font-size: 0.7rem;
          font-weight: 500;
          color: #7F8C8D;
        }

        .nav-item.active span {
          color: var(--accent-blue);
        }

        /* Responsive Design */
        @media (max-width: 768px) {
          .steps {
            flex-direction: column;
            gap: 0.5rem;
          }

          .step {
            padding: 0.5rem;
          }

          .symptoms-grid {
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 0.8rem;
          }

          .symptom-btn {
            padding: 0.8rem;
            flex-direction: column;
            gap: 0.5rem;
            text-align: center;
          }
        }

        @media (max-width: 480px) {
          .ai-header {
            padding: 0.8rem 1rem;
          }

          .logo-text {
            font-size: 1rem;
          }

          .header-title {
            font-size: 0.9rem;
          }

          .ai-content {
            padding: 0.8rem;
          }

          .how-it-works,
          .ai-analysis {
            padding: 1rem;
          }
        }
      `}</style>
    </div>
  );
};

export default AICare;
