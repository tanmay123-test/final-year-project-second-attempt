import React, { useState, useRef } from 'react';
import { 
  ArrowLeft, Send, PlusCircle, Trash2, Calendar, 
  DollarSign, Folder, Info, Upload, Check, X, 
  Search, Home, Bot, User, ChevronRight 
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../../../shared/api';
import '../styles/PostProject.css';

const PostProject = ({ onBack, onSuccess }) => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    budget_type: 'Fixed Price',
    budget: '',
    deadline: '',
    experience_level: '',
    enable_milestones: false
  });

  const [skillsList, setSkillsList] = useState([]);
  const [skillInput, setSkillInput] = useState('');
  const [attachments, setAttachments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const categories = [
    'Web Development', 'App Development', 'UI/UX Design', 
    'Digital Marketing', 'AI & Machine Learning', 'Content Writing'
  ];

  const expLevels = ['Beginner', 'Intermediate', 'Expert'];

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    // Clear error when field is edited
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const addSkill = (e) => {
    if (e) e.preventDefault();
    if (skillInput.trim() && !skillsList.includes(skillInput.trim())) {
      setSkillsList([...skillsList, skillInput.trim()]);
      setSkillInput('');
      if (errors.required_skills) {
        setErrors(prev => ({ ...prev, required_skills: '' }));
      }
    }
  };

  const removeSkill = (skillToRemove) => {
    setSkillsList(skillsList.filter(s => s !== skillToRemove));
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    const validFiles = files.filter(file => file.size <= 10 * 1024 * 1024); // 10MB
    if (validFiles.length < files.length) {
      alert('Some files were skipped because they exceed the 10MB limit.');
    }
    setAttachments([...attachments, ...validFiles]);
  };

  const removeAttachment = (index) => {
    setAttachments(attachments.filter((_, i) => i !== index));
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.title.trim()) newErrors.title = 'Project title is required';
    if (!formData.description.trim()) newErrors.description = 'Description is required';
    if (!formData.category) newErrors.category = 'Please select a category';
    if (!formData.budget || formData.budget <= 0) newErrors.budget = 'Please enter a valid positive budget';
    if (!formData.deadline) newErrors.deadline = 'Deadline is required';
    if (formData.deadline && new Date(formData.deadline) < new Date()) {
      newErrors.deadline = 'Deadline must be a future date';
    }
    if (!formData.experience_level) newErrors.experience_level = 'Please select experience level';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    try {
      const data = new FormData();
      
      Object.keys(formData).forEach(key => {
        data.append(key, formData[key]);
      });
      
      data.append('required_skills', JSON.stringify(skillsList));
      attachments.forEach(file => {
        data.append('attachments', file);
      });

      const response = await api.post('/api/freelancer/projects/create', data, {
        headers: { 
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.success) {
        alert('Project posted successfully!');
        if (onSuccess) {
          onSuccess();
        } else {
          navigate('/freelance/home?tab=projects');
        }
      }
    } catch (err) {
      const msg = err.response?.data?.message || 'Failed to post project. Please try again.';
      setErrors({ server: msg });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="post-project-page">
      <div className="post-project-hero">
        <div className="hero-content">
          <h1>Post a Project</h1>
          <p>Describe your project and attract top freelancers</p>
        </div>
      </div>

      <div className="post-project-form-container">
        <form onSubmit={handleSubmit} className="post-project-card">
          <h2 className="form-title">Project Details</h2>
          
          {errors.server && <div className="server-error">{errors.server}</div>}

          <div className="form-group">
            <label>Project Title *</label>
            <input
              type="text"
              name="title"
              placeholder="e.g., E-Commerce Website Redesign"
              value={formData.title}
              onChange={handleInputChange}
              className={errors.title ? 'error' : ''}
            />
            {errors.title && <span className="error-text">{errors.title}</span>}
          </div>

          <div className="form-group">
            <label>Description *</label>
            <textarea
              name="description"
              placeholder="Describe your project requirements in detail..."
              value={formData.description}
              onChange={handleInputChange}
              rows={5}
              className={errors.description ? 'error' : ''}
            />
            {errors.description && <span className="error-text">{errors.description}</span>}
          </div>

          <div className="form-group">
            <label>Category *</label>
            <div className="select-wrapper">
              <select 
                name="category" 
                value={formData.category} 
                onChange={handleInputChange}
                className={errors.category ? 'error' : ''}
              >
                <option value="">Select category</option>
                {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
              </select>
              <ChevronRight className="select-icon" size={20} />
            </div>
            {errors.category && <span className="error-text">{errors.category}</span>}
          </div>

          <div className="form-row-2">
            <div className="form-group">
              <label>Budget Type *</label>
              <div className="select-wrapper">
                <select name="budget_type" value={formData.budget_type} onChange={handleInputChange}>
                  <option value="Fixed Price">Fixed Price</option>
                  <option value="Hourly Rate">Hourly Rate</option>
                </select>
                <ChevronRight className="select-icon" size={20} />
              </div>
            </div>
            <div className="form-group">
              <label>Budget (₹) *</label>
              <input
                type="number"
                name="budget"
                placeholder="e.g., 50000"
                value={formData.budget}
                onChange={handleInputChange}
                className={errors.budget ? 'error' : ''}
              />
              {errors.budget && <span className="error-text">{errors.budget}</span>}
            </div>
          </div>

          <div className="form-row-2">
            <div className="form-group">
              <label>Deadline *</label>
              <input
                type="date"
                name="deadline"
                value={formData.deadline}
                onChange={handleInputChange}
                className={errors.deadline ? 'error' : ''}
              />
              {errors.deadline && <span className="error-text">{errors.deadline}</span>}
            </div>
            <div className="form-group">
              <label>Experience Level *</label>
              <div className="select-wrapper">
                <select 
                  name="experience_level" 
                  value={formData.experience_level} 
                  onChange={handleInputChange}
                  className={errors.experience_level ? 'error' : ''}
                >
                  <option value="">Select</option>
                  {expLevels.map(lvl => <option key={lvl} value={lvl}>{lvl}</option>)}
                </select>
                <ChevronRight className="select-icon" size={20} />
              </div>
              {errors.experience_level && <span className="error-text">{errors.experience_level}</span>}
            </div>
          </div>

          <div className="form-group">
            <label>Required Skills</label>
            <div className="skill-input-wrapper">
              <input
                type="text"
                placeholder="Search skills..."
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addSkill(e)}
              />
            </div>
            {skillsList.length > 0 && (
              <div className="skills-tags-container">
                {skillsList.map(skill => (
                  <span key={skill} className="skill-tag-v3">
                    {skill}
                    <X size={14} onClick={() => removeSkill(skill)} />
                  </span>
                ))}
              </div>
            )}
          </div>

          <div className="form-group">
            <label>Attachments</label>
            <div 
              className="upload-box" 
              onClick={() => fileInputRef.current.click()}
            >
              <Upload size={24} color="#9ca3af" />
              <p>Click to upload files (max 10MB)</p>
              <input 
                type="file" 
                multiple 
                hidden 
                ref={fileInputRef} 
                onChange={handleFileChange} 
              />
            </div>
            {attachments.length > 0 && (
              <div className="attachments-list">
                {attachments.map((file, idx) => (
                  <div key={idx} className="attachment-item">
                    <Check size={14} color="#534AB7" />
                    <span>{file.name}</span>
                    <X size={14} onClick={(e) => {e.stopPropagation(); removeAttachment(idx);}} />
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="milestones-toggle">
            <div className="toggle-info">
              <span className="toggle-label">Enable Milestones</span>
              <p className="toggle-desc">Split payment across project phases</p>
            </div>
            <label className="switch-v2">
              <input 
                type="checkbox" 
                name="enable_milestones"
                checked={formData.enable_milestones}
                onChange={handleInputChange}
              />
              <span className="slider-v2"></span>
            </label>
          </div>

          <button 
            type="submit" 
            className="submit-project-btn" 
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="spinner-white"></div>
                Posting...
              </>
            ) : 'Post Project'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default PostProject;
