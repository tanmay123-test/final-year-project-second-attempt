import React, { useState } from 'react';
import { ArrowLeft, Send, PlusCircle, Trash2, Calendar, DollarSign, Folder, Info, Upload, Check } from 'lucide-react';
import axios from 'axios';
import '../styles/FreelanceHome.css';

const PostProject = ({ onBack, onSuccess }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'web',
    budget_type: 'FIXED',
    budget_amount: '',
    deadline: '',
    experience_level: 'Intermediate',
    skills: ''
  });

  const [milestones, setMilestones] = useState([
    { title: 'Initial Draft', amount: '' }
  ]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [milestonesEnabled, setMilestonesEnabled] = useState(false);
  const [skillsList, setSkillsList] = useState([]);
  const [skillInput, setSkillInput] = useState('');

  const categories = [
    { id: 'web', name: 'Web Development' },
    { id: 'app', name: 'App Development' },
    { id: 'uiux', name: 'UI/UX Design' },
    { id: 'marketing', name: 'Digital Marketing' },
    { id: 'aiml', name: 'AI & Machine Learning' },
    { id: 'content', name: 'Content Writing' },
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const addSkill = () => {
    if (skillInput.trim() && !skillsList.includes(skillInput.trim())) {
      setSkillsList([...skillsList, skillInput.trim()]);
      setSkillInput('');
    }
  };

  const removeSkill = (skillToRemove) => {
    setSkillsList(skillsList.filter(s => s !== skillToRemove));
  };

  const addMilestone = () => {
    setMilestones([...milestones, { title: '', amount: '' }]);
  };

  const removeMilestone = (index) => {
    setMilestones(milestones.filter((_, i) => i !== index));
  };

  const handleMilestoneChange = (index, field, value) => {
    const newMilestones = [...milestones];
    newMilestones[index][field] = value;
    setMilestones(newMilestones);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('Please login to post a project');

      const response = await axios.post('http://localhost:5000/api/freelance/projects', {
        ...formData,
        skills: skillsList.join(', '),
        milestones: milestonesEnabled ? milestones.filter(m => m.title && m.amount) : []
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        onSuccess();
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to post project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="post-project-container">
      <header className="post-header">
        <button onClick={onBack} className="back-btn">
          <ArrowLeft size={20} />
        </button>
        <h2>Post Freelance Project</h2>
      </header>

      <form onSubmit={handleSubmit} className="post-form">
        {error && <div className="error-message">{error}</div>}

        <section className="form-section">
          <label>Project Title</label>
          <input
            type="text"
            name="title"
            placeholder="e.g., Build an e-commerce website"
            value={formData.title}
            onChange={handleInputChange}
            required
          />
        </section>

        <section className="form-section">
          <label>Project Description</label>
          <textarea
            name="description"
            placeholder="Describe your project in detail..."
            value={formData.description}
            onChange={handleInputChange}
            rows={6}
            required
          />
        </section>

        <section className="form-section">
          <label>Project Category</label>
          <select name="category" value={formData.category} onChange={handleInputChange}>
            <option value="">Select category</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
        </section>

        <section className="form-section">
          <label>Budget Type</label>
          <div className="budget-toggle-group">
            <button 
              type="button"
              className={formData.budget_type === 'FIXED' ? 'active' : ''}
              onClick={() => setFormData(p => ({...p, budget_type: 'FIXED'}))}
            >
              Fixed
            </button>
            <button 
              type="button"
              className={formData.budget_type === 'HOURLY' ? 'active' : ''}
              onClick={() => setFormData(p => ({...p, budget_type: 'HOURLY'}))}
            >
              Hourly
            </button>
          </div>
        </section>

        <section className="form-section">
          <label>Budget Amount ($)</label>
          <input
            type="number"
            name="budget_amount"
            placeholder="Total budget"
            value={formData.budget_amount}
            onChange={handleInputChange}
            required
          />
        </section>

        <section className="form-section">
          <label>Deadline</label>
          <div className="input-with-icon">
            <Calendar size={18} />
            <input
              type="date"
              name="deadline"
              value={formData.deadline}
              onChange={handleInputChange}
              placeholder="Pick a deadline"
              required
            />
          </div>
        </section>

        <section className="form-section">
          <label>Required Skills</label>
          <div className="skill-input-row">
            <input
              type="text"
              placeholder="Add a skill"
              value={skillInput}
              onChange={(e) => setSkillInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
            />
            <button type="button" onClick={addSkill} className="add-btn">
              Add
            </button>
          </div>
          {skillsList.length > 0 && (
            <div className="skills-tags-container">
              {skillsList.map(skill => (
                <span key={skill} className="skill-tag">
                  {skill}
                  <button type="button" onClick={() => removeSkill(skill)}>×</button>
                </span>
              ))}
            </div>
          )}
        </section>

        <section className="form-section">
          <label>Experience Level</label>
          <select name="experience_level" value={formData.experience_level} onChange={handleInputChange}>
            <option value="">Select level</option>
            <option>Entry Level</option>
            <option>Intermediate</option>
            <option>Expert</option>
          </select>
        </section>

        <section className="form-section">
          <label>Attachments</label>
          <div className="upload-area">
            <Upload size={32} />
            <p>Drag & drop files or click to browse</p>
          </div>
        </section>

        <section className="milestones-toggle-section">
          <div className="toggle-wrapper">
            <label className="switch">
              <input 
                type="checkbox" 
                checked={milestonesEnabled} 
                onChange={() => setMilestonesEnabled(!milestonesEnabled)}
              />
              <span className="slider round"></span>
            </label>
            <span>Enable Milestones</span>
          </div>
          
          {milestonesEnabled && (
            <div className="milestones-list-container">
              <div className="milestone-header">
                <label>Payment Milestones</label>
                <button type="button" onClick={addMilestone} className="add-milestone-btn">
                  <PlusCircle size={16} /> Add
                </button>
              </div>
              {milestones.map((m, index) => (
                <div key={index} className="milestone-row">
                  <input
                    type="text"
                    placeholder="Milestone title"
                    value={m.title}
                    onChange={(e) => handleMilestoneChange(index, 'title', e.target.value)}
                  />
                  <input
                    type="number"
                    placeholder="Amount"
                    value={m.amount}
                    onChange={(e) => handleMilestoneChange(index, 'amount', e.target.value)}
                  />
                  {milestones.length > 1 && (
                    <button type="button" onClick={() => removeMilestone(index)} className="remove-btn">
                      <Trash2 size={18} />
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>

        <button type="submit" className="submit-project-btn-green" disabled={loading}>
          {loading ? 'Posting...' : 'Post Project'}
        </button>
      </form>
    </div>
  );
};

export default PostProject;
