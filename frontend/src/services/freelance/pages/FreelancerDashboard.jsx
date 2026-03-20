import React, { useState } from 'react';
import { Home, Search, FileText, Briefcase, Wallet, Bell, Star, CheckCircle, Clock } from 'lucide-react';
import '../styles/FreelancerDashboard.css';

const FreelancerDashboard = () => {
  const [activeTab, setActiveTab] = useState('home');

  const stats = [
    { label: 'Total Earnings', value: '₹12,450', icon: Wallet, color: '#10b981' },
    { label: 'Active Projects', value: '3', icon: Briefcase, color: '#3b82f6' },
    { label: 'Proposals Sent', value: '24', icon: FileText, color: '#6366f1' },
    { label: 'Rating', value: '4.8', icon: Star, color: '#f59e0b' },
  ];

  const activeProjects = [
    { id: 1, title: 'E-commerce Website Redesign', client: 'John Doe', status: 'Working', earnings: '₹5,000', deadline: '2 days left' },
    { id: 2, title: 'Mobile App API Development', client: 'Tech Corp', status: 'Milestone Submitted', earnings: '₹8,500', deadline: '5 days left' },
  ];

  return (
    <div className="freelancer-dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="logo">
          <div className="logo-icon">💼</div>
          <h2>ProTasks</h2>
        </div>
        <div className="header-actions">
          <button className="icon-btn"><Bell size={20} /></button>
          <div className="user-avatar">AD</div>
        </div>
      </header>

      <main className="dashboard-main">
        <section className="welcome-section">
          <h1>Freelancer Dashboard</h1>
        </section>

        {/* Stats Grid */}
        <div className="stats-grid">
          {stats.map((stat, i) => (
            <div key={i} className="stat-card">
              <div className="stat-icon" style={{ backgroundColor: `${stat.color}15`, color: stat.color }}>
                <stat.icon size={20} />
              </div>
              <div className="stat-info">
                <p>{stat.label}</p>
                <h3>{stat.value}</h3>
              </div>
            </div>
          ))}
        </div>

        {/* Earnings Chart Placeholder */}
        <section className="earnings-overview">
          <div className="section-header">
            <h3>Earnings Overview</h3>
            <select>
              <option>This Week</option>
              <option>This Month</option>
            </select>
          </div>
          <div className="chart-placeholder">
            <div className="bar-container">
              {[40, 70, 45, 90, 65, 80, 55].map((h, i) => (
                <div key={i} className="bar" style={{ height: `${h}%` }}></div>
              ))}
            </div>
            <div className="chart-labels">
              <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
            </div>
          </div>
        </section>

        {/* Active Projects */}
        <section className="active-projects-section">
          <div className="section-header">
            <h3>Active Projects</h3>
            <button className="view-all">View All</button>
          </div>
          <div className="projects-list">
            {activeProjects.map(proj => (
              <div key={proj.id} className="project-item">
                <div className="project-info">
                  <h4>{proj.title}</h4>
                  <p>Client: {proj.client}</p>
                </div>
                <div className="project-status">
                  <span className={`status-badge ${proj.status.toLowerCase().replace(' ', '-')}`}>
                    {proj.status}
                  </span>
                  <div className="project-meta">
                    <Clock size={12} />
                    <span>{proj.deadline}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>

      {/* Bottom Navigation */}
      <nav className="dashboard-bottom-nav">
        <button 
          className={`nav-item ${activeTab === 'home' ? 'active' : ''}`}
          onClick={() => setActiveTab('home')}
        >
          <Home size={22} />
          <span>Home</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'browse' ? 'active' : ''}`}
          onClick={() => setActiveTab('browse')}
        >
          <Search size={22} />
          <span>Browse</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'proposals' ? 'active' : ''}`}
          onClick={() => setActiveTab('proposals')}
        >
          <FileText size={22} />
          <span>Proposals</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'work' ? 'active' : ''}`}
          onClick={() => setActiveTab('work')}
        >
          <Briefcase size={22} />
          <span>My Work</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'wallet' ? 'active' : ''}`}
          onClick={() => setActiveTab('wallet')}
        >
          <Wallet size={22} />
          <span>Wallet</span>
        </button>
      </nav>
    </div>
  );
};

export default FreelancerDashboard;
