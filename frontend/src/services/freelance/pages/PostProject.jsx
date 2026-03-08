import React, { useState } from 'react';
import { ArrowLeft, Send, Plus, Trash2, Calendar, DollarSign, Briefcase, Info } from 'lucide-react';
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
        milestones: milestones.filter(m => m.title && m.amount)
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
        <h2>Post a Project</h2>
      </header>

      <form onSubmit={handleSubmit} className="post-form">
        {error && <div className="error-message">{error}</div>}

        <section className="form-section">
          <label>Project Title</label>
          <input
            type="text"
            name="title"
            placeholder="e.g., Build a Portfolio Website"
            value={formData.title}
            onChange={handleInputChange}
            required
          />
        </section>

        <section className="form-section">
          <label>Description</label>
          <textarea
            name="description"
            placeholder="Describe your project in detail..."
            value={formData.description}
            onChange={handleInputChange}
            rows={4}
            required
          />
        </section>

        <div className="form-row">
          <section className="form-section">
            <label>Category</label>
            <select name="category" value={formData.category} onChange={handleInputChange}>
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </section>

          <section className="form-section">
            <label>Experience Level</label>
            <select name="experience_level" value={formData.experience_level} onChange={handleInputChange}>
              <option>Entry Level</option>
              <option>Intermediate</option>
              <option>Expert</option>
            </select>
          </section>
        </div>

        <section className="form-section">
          <label>Required Skills (comma separated)</label>
          <div className="input-with-icon">
            <Briefcase size={18} />
            <input
              type="text"
              name="skills"
              placeholder="React, Node.js, CSS..."
              value={formData.skills}
              onChange={handleInputChange}
            />
          </div>
        </section>

        <div className="form-row">
          <section className="form-section">
            <label>Budget Type</label>
            <div className="toggle-group">
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
            <label>Budget Amount (₹)</label>
            <div className="input-with-icon">
              <DollarSign size={18} />
              <input
                type="number"
                name="budget_amount"
                placeholder="5000"
                value={formData.budget_amount}
                onChange={handleInputChange}
                required
              />
            </div>
          </section>
        </div>

        <section className="form-section">
          <label>Deadline</label>
          <div className="input-with-icon">
            <Calendar size={18} />
            <input
              type="date"
              name="deadline"
              value={formData.deadline}
              onChange={handleInputChange}
              required
            />
          </div>
        </section>

        <section className="milestones-section">
          <div className="section-header">
            <label>Payment Milestones (Optional)</label>
            <button type="button" onClick={addMilestone} className="add-milestone-btn">
              <Plus size={16} /> Add
            </button>
          </div>
          <p className="helper-text"><Info size={12} /> Break your project into smaller tasks for safer payments.</p>
          
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
        </section>

        <button type="submit" className="submit-project-btn" disabled={loading}>
          {loading ? 'Posting...' : <><Send size={18} /> Post Project</>}
        </button>
      </form>
    </div>
  );
};

export default PostProject;
