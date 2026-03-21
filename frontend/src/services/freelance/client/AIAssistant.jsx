import React, { useState } from 'react';
import { 
  Zap, DollarSign, List, Users, Copy, Check, 
  Loader2, Home, PlusCircle, Folder, Bot, User, Search 
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/AIAssistant.css';

const AIAssistant = () => {
  const navigate = useNavigate();
  const [idea, setIdea] = useState('');
  const [description, setDescription] = useState('');
  const [budgetRange, setBudgetRange] = useState(null);
  const [milestones, setMilestones] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [copied, setCopied] = useState(false);
  
  const [loading, setLoading] = useState({
    description: false,
    budget: false,
    milestones: false,
    freelancers: false
  });

  const handleGenerateDescription = async () => {
    if (!idea.trim()) return;
    setLoading(prev => ({ ...prev, description: true }));
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5000/api/freelancer/ai/generate-description', 
        { idea },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setDescription(response.data.description);
    } catch (error) {
      console.error('Error generating description:', error);
    } finally {
      setLoading(prev => ({ ...prev, description: false }));
    }
  };

  const handleSuggestBudget = async () => {
    setLoading(prev => ({ ...prev, budget: true }));
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5000/api/freelancer/ai/suggest-budget', 
        { 
          category: 'Web Development', // Fallback or take from context
          experienceLevel: 'Intermediate',
          description: description || idea
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setBudgetRange(response.data);
    } catch (error) {
      console.error('Error suggesting budget:', error);
    } finally {
      setLoading(prev => ({ ...prev, budget: false }));
    }
  };

  const handleSuggestMilestones = async () => {
    setLoading(prev => ({ ...prev, milestones: true }));
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5000/api/freelancer/ai/suggest-milestones', 
        { 
          title: idea,
          description: description || idea,
          budget: budgetRange?.maxBudget || 10000
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMilestones(response.data.milestones);
    } catch (error) {
      console.error('Error suggesting milestones:', error);
    } finally {
      setLoading(prev => ({ ...prev, milestones: false }));
    }
  };

  const handleRecommendFreelancers = async () => {
    setLoading(prev => ({ ...prev, freelancers: true }));
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5000/api/freelancer/ai/recommend-freelancers', 
        { 
          category: 'Web Development',
          skills: ['React', 'Node.js'],
          budget: budgetRange?.maxBudget || 10000
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setRecommendations(response.data.freelancers);
    } catch (error) {
      console.error('Error recommending freelancers:', error);
    } finally {
      setLoading(prev => ({ ...prev, freelancers: false }));
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(description);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="ai-assistant-page">
      <div className="ai-hero">
        <div className="hero-content">
          <h1><Bot size={32} className="ai-bot-icon" /> AI Project Assistant</h1>
          <p>Let AI help you plan and post better projects</p>
        </div>
      </div>

      <div className="ai-content-wrapper">
        <div className="ai-grid">
          {/* Card 1: Generate Description */}
          <div className="ai-card full-width">
            <div className="card-header">
              <Zap size={20} color="#534AB7" />
              <h3>Generate Project Description</h3>
            </div>
            <p className="card-subtitle">Describe your project idea briefly and AI will write a full professional description for you.</p>
            
            <div className="input-group">
              <input 
                type="text" 
                placeholder="Describe your project idea briefly..." 
                value={idea}
                onChange={(e) => setIdea(e.target.value)}
              />
              <button 
                className="generate-btn" 
                onClick={handleGenerateDescription}
                disabled={loading.description}
              >
                {loading.description ? <Loader2 className="spinner" size={18} /> : <Zap size={18} />}
                Generate Description
              </button>
            </div>

            {description && (
              <div className="result-box">
                <div className="result-header">
                  <span>Generated Description</span>
                  <button className="copy-btn" onClick={copyToClipboard}>
                    {copied ? <Check size={16} color="#10b981" /> : <Copy size={16} />}
                  </button>
                </div>
                <div className="result-text">
                  {description}
                </div>
              </div>
            )}
          </div>

          {/* Card 2: Budget Estimator */}
          <div className="ai-card">
            <div className="card-header">
              <DollarSign size={20} color="#534AB7" />
              <h3>Budget Estimator</h3>
            </div>
            <p className="card-subtitle">Get AI suggested budget ranges based on similar projects in the marketplace.</p>
            
            <button 
              className="outline-btn" 
              onClick={handleSuggestBudget}
              disabled={loading.budget}
            >
              {loading.budget ? <Loader2 className="spinner" size={18} /> : null}
              Suggest Budget Range
            </button>

            {budgetRange && (
              <div className="budget-result">
                <span className="label">Estimated Range</span>
                <span className="value">₹{budgetRange.minBudget?.toLocaleString()} - ₹{budgetRange.maxBudget?.toLocaleString()}</span>
              </div>
            )}
          </div>

          {/* Card 3: Milestone Planner */}
          <div className="ai-card">
            <div className="card-header">
              <List size={20} color="#534AB7" />
              <h3>Milestone Planner</h3>
            </div>
            <p className="card-subtitle">AI will suggest milestones to structure your project into manageable phases.</p>
            
            <button 
              className="outline-btn" 
              onClick={handleSuggestMilestones}
              disabled={loading.milestones}
            >
              {loading.milestones ? <Loader2 className="spinner" size={18} /> : null}
              Suggest Milestones
            </button>

            {milestones.length > 0 && (
              <div className="milestones-list">
                {milestones.map((m, idx) => (
                  <div key={idx} className="milestone-item">
                    <span>{m.name}</span>
                    <strong>₹{m.amount?.toLocaleString()}</strong>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Card 4: Freelancer Recommendations */}
          <div className="ai-card">
            <div className="card-header">
              <Users size={20} color="#534AB7" />
              <h3>Freelancer Recommendations</h3>
            </div>
            <p className="card-subtitle">Find the best freelancer match for your project requirements using AI.</p>
            
            <button 
              className="outline-btn" 
              onClick={handleRecommendFreelancers}
              disabled={loading.freelancers}
            >
              {loading.freelancers ? <Loader2 className="spinner" size={18} /> : null}
              Find Freelancers
            </button>

            {recommendations.length > 0 && (
              <div className="recommendations-list">
                {recommendations.map(free => (
                  <div key={free.id} className="rec-card" onClick={() => navigate(`/freelance/freelancer/${free.id}`)}>
                    <div className="rec-avatar">{free.full_name?.charAt(0)}</div>
                    <div className="rec-info">
                      <h4>{free.full_name}</h4>
                      <p>{free.specialization}</p>
                      <div className="rec-meta">
                        <span>★ {free.rating || '5.0'}</span>
                        <span>₹{free.hourly_rate}/hr</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
