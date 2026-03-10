import React, { useState } from 'react';
import { Home, Search, PlusCircle, Folder, Bot, Wallet, Star, LayoutDashboard, User } from 'lucide-react';
import { useAuth } from '../../../context/AuthContext';
import PostProject from './PostProject';
import MyProjects from './MyProjects';
import '../styles/FreelanceHome.css';

const FreelanceHome = () => {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('home');
  
  const categories = [
    { id: 'web', name: 'Web Development', projects: '245 projects', icon: '🌐' },
    { id: 'app', name: 'App Development', projects: '189 projects', icon: '📱' },
    { id: 'uiux', name: 'UI/UX Design', projects: '312 projects', icon: '🎨' },
    { id: 'marketing', name: 'Digital Marketing', projects: '156 projects', icon: '📢' },
    { id: 'aiml', name: 'AI & Machine Learning', projects: '98 projects', icon: '🤖' },
    { id: 'content', name: 'Content Writing', projects: '203 projects', icon: '✍️' },
  ];

  const featuredFreelancers = [
    {
      id: 1,
      name: 'Aditya Verma',
      role: 'Full Stack Developer',
      rating: 4.9,
      reviews: 87,
      rate: '₹2500/hr',
      skills: ['React', 'Node.js', 'TypeScript'],
      status: 'online'
    },
    {
      id: 2,
      name: 'Meera Nair',
      role: 'UI/UX Designer',
      rating: 4.8,
      reviews: 64,
      rate: '₹1800/hr',
      skills: ['Figma', 'Adobe XD', 'Prototyping'],
      status: 'online'
    }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return (
          <>
            {/* Top Navigation */}
            <header className="freelance-top-nav">
              <div className="nav-left">
                <span className="brand-name">ExpertEase</span>
              </div>
              <div className="nav-right">
                <div className="nav-item-link">
                  <LayoutDashboard size={18} />
                  <span>Dashboard</span>
                </div>
                <div className="nav-item-link">
                  <Search size={18} />
                  <span>Find Freelancers</span>
                </div>
                <div className="user-profile-nav">
                  <div className="user-avatar-purple">
                    <User size={16} color="white" />
                  </div>
                  <span>Hi, {user?.user_name || 'goat1'}</span>
                </div>
              </div>
            </header>

            {/* Hero Section */}
            <section className="freelance-hero">
              <div className="hero-content">
                <h1>Find Top Freelancers</h1>
                <p>Hire experts for your next project</p>
                <div className="search-bar-wrapper-hero">
                  <Search className="search-icon-hero" size={20} />
                  <input 
                    type="text" 
                    placeholder="Search freelancers or skills..." 
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
              </div>
            </section>

            {/* Post Project Banner */}
            <section className="post-project-banner-new">
              <div className="banner-content">
                <h3>Have a project idea?</h3>
                <p>Post it and get proposals from top freelancers</p>
              </div>
              <button className="post-btn-new" onClick={() => setActiveTab('post')}>
                Post Project
              </button>
            </section>

            {/* Categories */}
            <section className="categories-section">
              <div className="section-header">
                <h2>Browse Categories</h2>
              </div>
              <div className="categories-grid">
                {categories.map(cat => (
                  <div key={cat.id} className="category-card">
                    <span className="cat-icon">{cat.icon}</span>
                    <h4>{cat.name}</h4>
                    <p>{cat.projects}</p>
                  </div>
                ))}
              </div>
            </section>

            {/* Featured Freelancers */}
            <section className="featured-section">
              <div className="section-header">
                <h2>Featured Freelancers</h2>
                <button className="view-all">View All →</button>
              </div>
              <div className="freelancers-list">
                {featuredFreelancers.map(free => (
                  <div key={free.id} className="freelancer-card">
                    <div className="card-top">
                      <div className="avatar">
                        {free.name.split(' ').map(n => n[0]).join('')}
                        <span className={`status-dot ${free.status}`}></span>
                      </div>
                      <div className="info">
                        <h4>{free.name}</h4>
                        <p>{free.role}</p>
                        <div className="rating">
                          <Star size={14} fill="#FFB800" color="#FFB800" />
                          <span>{free.rating} ({free.reviews} reviews)</span>
                        </div>
                      </div>
                      <div className="rate">{free.rate}</div>
                    </div>
                    <div className="skills-tags">
                      {free.skills.map(skill => (
                        <span key={skill} className="skill-tag">{skill}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </>
        );
      case 'post':
        return (
          <PostProject 
            onBack={() => setActiveTab('home')} 
            onSuccess={() => setActiveTab('projects')} 
          />
        );
      case 'projects':
        return <MyProjects />;
      case 'ai':
        return (
          <div className="ai-assistant-placeholder">
            <Bot size={48} color="#9B59B6" />
            <h3>AI Freelance Assistant</h3>
            <p>I can help you estimate budgets and write project descriptions. Coming soon!</p>
          </div>
        );
      case 'wallet':
        return (
          <div className="wallet-placeholder">
            <Wallet size={48} color="#9B59B6" />
            <h3>My Wallet</h3>
            <p>View your transaction history and manage funds.</p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="freelance-container">
      {renderContent()}

      {/* Bottom Nav */}
      <nav className="freelance-bottom-nav">
        <button 
          className={`nav-item ${activeTab === 'home' ? 'active' : ''}`}
          onClick={() => setActiveTab('home')}
        >
          <Home size={24} />
          <span>Home</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'post' ? 'active' : ''}`}
          onClick={() => setActiveTab('post')}
        >
          <PlusCircle size={24} />
          <span>Post</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'projects' ? 'active' : ''}`}
          onClick={() => setActiveTab('projects')}
        >
          <Folder size={24} />
          <span>Projects</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'ai' ? 'active' : ''}`}
          onClick={() => setActiveTab('ai')}
        >
          <Bot size={24} />
          <span>AI</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'wallet' ? 'active' : ''}`}
          onClick={() => setActiveTab('wallet')}
        >
          <Wallet size={24} />
          <span>Wallet</span>
        </button>
      </nav>
    </div>
  );
};

export default FreelanceHome;
