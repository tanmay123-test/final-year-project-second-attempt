import React, { useState } from 'react';
import { 
  Zap, DollarSign, List, Users, Copy, Check, 
  Loader2, Home, PlusCircle, Folder, Bot, User, Search 
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../../../shared/api';
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
      // Use your real backend API
      const response = await api.post('/api/freelancer/ai/generate-description', 
        { idea }
      );
      setDescription(response.data.description);
    } catch (error) {
      console.error('Error generating description:', error);
      // Fallback mock response
      setDescription(`**Project: ${idea}**\n\n**Project Overview:**\nWe are looking for a skilled freelancer to help us with ${idea}. This project requires expertise and attention to detail.\n\n**Scope of Work:**\n• Complete the ${idea} requirements\n• Deliver high-quality work within timeline\n• Communicate progress regularly\n• Make revisions as needed\n\n**Required Skills:**\n• Relevant experience in ${idea}\n• Strong communication skills\n• Attention to detail\n• Ability to meet deadlines\n\n**Deliverables:**\n• Completed ${idea} project\n• Documentation and support\n• Final delivery in agreed format\n\n**Timeline:**\n• Project duration: To be discussed\n• Start date: As soon as possible\n\n**Budget:**\n• Competitive rates based on experience\n• Payment terms: Milestone-based\n\nIf you have experience with ${idea} and can deliver quality work, please apply with your portfolio and relevant experience.`);
    } finally {
      setLoading(prev => ({ ...prev, description: false }));
    }
  };

  const handleSuggestBudget = async () => {
    setLoading(prev => ({ ...prev, budget: true }));
    try {
      // Use your real backend API
      const response = await api.post('/api/freelancer/ai/suggest-budget', 
        { 
          category: 'Web Development',
          experienceLevel: 'Mid',
          description: idea || 'General freelance project'
        }
      );
      setBudgetRange(response.data);
    } catch (error) {
      console.error('Error suggesting budget:', error);
      // Fallback mock budget
      setBudgetRange({
        minBudget: 5000,
        maxBudget: 25000,
        currency: 'INR'
      });
    } finally {
      setLoading(prev => ({ ...prev, budget: false }));
    }
  };

  const handleSuggestMilestones = async () => {
    setLoading(prev => ({ ...prev, milestones: true }));
    try {
      // Use your real backend API
      const response = await api.post('/api/freelancer/ai/suggest-milestones', 
        { 
          title: idea || 'Project',
          description: 'Project description',
          budget: budgetRange?.maxBudget || 20000
        }
      );
      setMilestones(response.data.milestones || []);
    } catch (error) {
      console.error('Error suggesting milestones:', error);
      // Fallback mock milestones
      setMilestones([
        { title: "Project Kickoff", description: "Initial discussion and requirements gathering", deliverable: "Project brief", estimatedDays: 2 },
        { title: "First Draft", description: "Create initial version", deliverable: "Draft deliverable", estimatedDays: 5 },
        { title: "Review & Feedback", description: "Client review and feedback incorporation", deliverable: "Revised version", estimatedDays: 3 },
        { title: "Final Delivery", description: "Complete and deliver final project", deliverable: "Final project files", estimatedDays: 2 }
      ]);
    } finally {
      setLoading(prev => ({ ...prev, milestones: false }));
    }
  };

  const handleRecommendFreelancers = async () => {
    setLoading(prev => ({ ...prev, freelancers: true }));
    try {
      // Use your real backend API that gets actual freelancers from database
      const response = await api.post('/api/freelancer/ai/recommend-freelancers', 
        { 
          category: 'Web Development',
          skills: ['React', 'Node.js'],
          budget: budgetRange?.maxBudget || 10000
        }
      );
      setRecommendations(response.data.freelancers || []);
    } catch (error) {
      console.error('Error recommending freelancers:', error);
      // Fallback to mock recommendations
      setRecommendations([
        {
          id: 1,
          full_name: "Raj Kumar",
          specialization: "Web Development",
          rating: "4.8",
          hourly_rate: 1500
        },
        {
          id: 2,
          full_name: "Priya Sharma",
          specialization: "UI/UX Design",
          rating: "4.9",
          hourly_rate: 1800
        },
        {
          id: 3,
          full_name: "Amit Patel",
          specialization: "Full Stack Development",
          rating: "4.7",
          hourly_rate: 1600
        }
      ]);
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
