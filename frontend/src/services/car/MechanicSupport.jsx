import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, HelpCircle, Phone, Mail, MessageCircle,
  Search, FileText, Video, Book, AlertCircle,
  ChevronRight, Send, ExternalLink, Clock, CheckCircle
} from 'lucide-react';

const MechanicSupport = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [expandedFaq, setExpandedFaq] = useState(null);
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
    priority: 'medium'
  });

  const categories = [
    { id: 'all', name: 'All Topics', icon: HelpCircle },
    { id: 'account', name: 'Account & Profile', icon: FileText },
    { id: 'payments', name: 'Payments & Earnings', icon: MessageCircle },
    { id: 'jobs', name: 'Jobs & Bookings', icon: Book },
    { id: 'technical', name: 'Technical Issues', icon: AlertCircle }
  ];

  const faqs = [
    {
      id: 1,
      category: 'account',
      question: 'How do I update my profile information?',
      answer: 'You can update your profile by going to Profile > View Full Details > Edit Profile. Make your changes and click Save Changes. Your information will be updated immediately.',
      helpful: 45
    },
    {
      id: 2,
      category: 'payments',
      question: 'When do I receive my payments?',
      answer: 'Payments are typically processed within 24-48 hours after job completion. You can view your payment status in the Payment History section. Bank transfers may take 3-5 business days.',
      helpful: 38
    },
    {
      id: 3,
      category: 'jobs',
      question: 'How do I set my working hours and availability?',
      answer: 'Go to Settings > Availability and configure your working hours for each day. You can also set max jobs per day and enable emergency service availability. These settings help customers know when you\'re available.',
      helpful: 52
    },
    {
      id: 4,
      category: 'technical',
      question: 'The app is not loading properly. What should I do?',
      answer: 'Try clearing your browser cache, checking your internet connection, or using a different browser. If the issue persists, contact our technical support team with details about your device and browser.',
      helpful: 28
    },
    {
      id: 5,
      category: 'account',
      question: 'How is my fairness score calculated?',
      answer: 'Your fairness score is based on multiple factors: payment fairness (timely payments), job distribution (regular work flow), rating fairness (customer satisfaction), and response time (how quickly you accept jobs). Each factor is weighted equally in the overall score.',
      helpful: 67
    },
    {
      id: 6,
      category: 'payments',
      question: 'What payment methods are available?',
      answer: 'We support bank transfers, UPI, cash, and cheque payments. You can set your preferred payment method in Settings > Payment Information. Customers will see your available payment options when booking.',
      helpful: 41
    },
    {
      id: 7,
      category: 'jobs',
      question: 'How do I cancel a job?',
      answer: 'If you need to cancel a job, go to your active jobs list and select the job you want to cancel. Click on "Cancel Job" and provide a reason. Try to cancel as early as possible to maintain customer satisfaction.',
      helpful: 33
    },
    {
      id: 8,
      category: 'technical',
      question: 'I forgot my password. How do I reset it?',
      answer: 'Click on "Forgot Password" on the login page. Enter your registered email address, and we\'ll send you a password reset link. The link expires after 24 hours for security reasons.',
      helpful: 89
    }
  ];

  const supportContacts = [
    {
      type: 'Phone Support',
      icon: Phone,
      value: '+91 1800-123-4567',
      description: 'Available 24/7 for urgent issues',
      available: '24/7'
    },
    {
      type: 'Email Support',
      icon: Mail,
      value: 'support@mechanicconnect.com',
      description: 'Response within 24 hours',
      available: '24/7'
    },
    {
      type: 'Live Chat',
      icon: MessageCircle,
      value: 'Chat Now',
      description: 'Instant support during business hours',
      available: '9 AM - 9 PM'
    },
    {
      type: 'Video Call',
      icon: Video,
      value: 'Schedule Call',
      description: 'Screen sharing and remote assistance',
      available: 'By Appointment'
    }
  ];

  const tutorials = [
    {
      title: 'Getting Started Guide',
      description: 'Complete walkthrough for new mechanics',
      duration: '5 min',
      level: 'Beginner',
      link: '#getting-started'
    },
    {
      title: 'Maximizing Your Earnings',
      description: 'Tips to increase your income and job opportunities',
      duration: '8 min',
      level: 'Intermediate',
      link: '#earnings'
    },
    {
      title: 'Advanced Profile Setup',
      description: 'Optimize your profile for better visibility',
      duration: '6 min',
      level: 'Advanced',
      link: '#profile-setup'
    },
    {
      title: 'Understanding Analytics',
      description: 'Learn to interpret your performance metrics',
      duration: '10 min',
      level: 'Intermediate',
      link: '#analytics'
    }
  ];

  const filteredFaqs = faqs.filter(faq => {
    const matchesCategory = selectedCategory === 'all' || faq.category === selectedCategory;
    const matchesSearch = faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         faq.answer.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const handleSubmitSupport = (e) => {
    e.preventDefault();
    alert('Support request submitted! We\'ll respond within 24 hours.');
    setContactForm({ name: '', email: '', subject: '', message: '', priority: 'medium' });
  };

  const toggleFaq = (id) => {
    setExpandedFaq(expandedFaq === id ? null : id);
  };

  return (
    <div className="support-page">
      {/* Header */}
      <div className="support-header">
        <div className="header-actions">
          <button className="back-button" onClick={() => navigate('/worker/car/mechanic/profile')}>
            <ArrowLeft size={20} />
            <span>Back to Profile</span>
          </button>
        </div>
        <h1>Help & Support</h1>
      </div>

      <div className="support-content">
        {/* Quick Actions */}
        <div className="quick-actions">
          <div className="action-card emergency">
            <div className="action-icon">
              <AlertCircle size={32} />
            </div>
            <div className="action-content">
              <h3>Emergency Support</h3>
              <p>Critical issues with active jobs or payments</p>
              <button className="action-button emergency">
                <Phone size={16} />
                <span>Call Now</span>
              </button>
            </div>
          </div>
          
          <div className="action-card tutorial">
            <div className="action-icon">
              <Video size={32} />
            </div>
            <div className="action-content">
              <h3>Video Tutorials</h3>
              <p>Step-by-step guides for common tasks</p>
              <button className="action-button">
                <ExternalLink size={16} />
                <span>Watch Videos</span>
              </button>
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="search-section">
          <div className="search-box">
            <Search size={20} className="search-icon" />
            <input
              type="text"
              placeholder="Search for help articles, FAQs, or topics..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>
        </div>

        {/* Categories */}
        <div className="categories-section">
          <h3>Browse by Category</h3>
          <div className="category-tabs">
            {categories.map((category) => (
              <button
                key={category.id}
                className={`category-tab ${selectedCategory === category.id ? 'active' : ''}`}
                onClick={() => setSelectedCategory(category.id)}
              >
                <category.icon size={18} />
                <span>{category.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* FAQs */}
        <div className="faq-section">
          <h3>Frequently Asked Questions</h3>
          <div className="faq-list">
            {filteredFaqs.map((faq) => (
              <div key={faq.id} className="faq-item">
                <div 
                  className="faq-question" 
                  onClick={() => toggleFaq(faq.id)}
                >
                  <span>{faq.question}</span>
                  <ChevronRight 
                    size={16} 
                    className={`chevron ${expandedFaq === faq.id ? 'expanded' : ''}`}
                  />
                </div>
                
                {expandedFaq === faq.id && (
                  <div className="faq-answer">
                    <p>{faq.answer}</p>
                    <div className="faq-helpful">
                      <span>Was this helpful?</span>
                      <div className="helpful-buttons">
                        <button className="helpful-btn yes">
                          <CheckCircle size={14} />
                          <span>Yes ({faq.helpful})</span>
                        </button>
                        <button className="helpful-btn no">
                          <span>No</span>
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Support Contacts */}
        <div className="contacts-section">
          <h3>Contact Support</h3>
          <div className="contacts-grid">
            {supportContacts.map((contact, index) => (
              <div key={index} className="contact-card">
                <div className="contact-header">
                  <contact.icon size={24} className="contact-icon" />
                  <h4>{contact.type}</h4>
                </div>
                <div className="contact-details">
                  <div className="contact-value">{contact.value}</div>
                  <div className="contact-description">{contact.description}</div>
                  <div className="contact-availability">
                    <Clock size={14} />
                    <span>{contact.available}</span>
                  </div>
                </div>
                <button className="contact-button">
                  {contact.type === 'Phone Support' && 'Call Now'}
                  {contact.type === 'Email Support' && 'Send Email'}
                  {contact.type === 'Live Chat' && contact.value}
                  {contact.type === 'Video Call' && contact.value}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Contact Form */}
        <div className="contact-form-section">
          <h3>Send us a Message</h3>
          <form onSubmit={handleSubmitSupport} className="support-form">
            <div className="form-grid">
              <div className="form-group">
                <label>Your Name</label>
                <input
                  type="text"
                  value={contactForm.name}
                  onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                  className="form-input"
                  required
                />
              </div>
              
              <div className="form-group">
                <label>Email Address</label>
                <input
                  type="email"
                  value={contactForm.email}
                  onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                  className="form-input"
                  required
                />
              </div>
            </div>
            
            <div className="form-group">
              <label>Subject</label>
              <input
                type="text"
                value={contactForm.subject}
                onChange={(e) => setContactForm({ ...contactForm, subject: e.target.value })}
                className="form-input"
                placeholder="Brief description of your issue"
                required
              />
            </div>
            
            <div className="form-group">
              <label>Priority</label>
              <select
                value={contactForm.priority}
                onChange={(e) => setContactForm({ ...contactForm, priority: e.target.value })}
                className="form-select"
              >
                <option value="low">Low - General Question</option>
                <option value="medium">Medium - Technical Issue</option>
                <option value="high">High - Account/Payment Issue</option>
                <option value="urgent">Urgent - Emergency</option>
              </select>
            </div>
            
            <div className="form-group full-width">
              <label>Message</label>
              <textarea
                value={contactForm.message}
                onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })}
                className="form-input textarea"
                rows={5}
                placeholder="Describe your issue in detail..."
                required
              />
            </div>
            
            <button type="submit" className="submit-button">
              <Send size={18} />
              <span>Send Message</span>
            </button>
          </form>
        </div>

        {/* Video Tutorials */}
        <div className="tutorials-section">
          <h3>Video Tutorials</h3>
          <div className="tutorials-grid">
            {tutorials.map((tutorial, index) => (
              <div key={index} className="tutorial-card">
                <div className="tutorial-thumbnail">
                  <Video size={32} />
                </div>
                <div className="tutorial-info">
                  <h4>{tutorial.title}</h4>
                  <p>{tutorial.description}</p>
                  <div className="tutorial-meta">
                    <span className="duration">{tutorial.duration}</span>
                    <span className="level">{tutorial.level}</span>
                  </div>
                </div>
                <button className="tutorial-button">
                  <ExternalLink size={16} />
                  <span>Watch</span>
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Resources */}
        <div className="resources-section">
          <h3>Additional Resources</h3>
          <div className="resources-grid">
            <div className="resource-item">
              <div className="resource-icon">
                <Book size={24} />
              </div>
              <div className="resource-content">
                <h4>User Manual</h4>
                <p>Complete guide to all features</p>
                <button className="resource-link">
                  <ExternalLink size={16} />
                  <span>View PDF</span>
                </button>
              </div>
            </div>
            
            <div className="resource-item">
              <div className="resource-icon">
                <FileText size={24} />
              </div>
              <div className="resource-content">
                <h4>API Documentation</h4>
                <p>For developers and integrations</p>
                <button className="resource-link">
                  <ExternalLink size={16} />
                  <span>View Docs</span>
                </button>
              </div>
            </div>
            
            <div className="resource-item">
              <div className="resource-icon">
                <MessageCircle size={24} />
              </div>
              <div className="resource-content">
                <h4>Community Forum</h4>
                <p>Connect with other mechanics</p>
                <button className="resource-link">
                  <ExternalLink size={16} />
                  <span>Join Forum</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .support-page {
          background-color: #f8fafc;
          min-height: 100vh;
          font-family: 'Inter', sans-serif;
        }

        .support-header {
          background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
          padding: 1.5rem;
          color: white;
        }

        .header-actions {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .back-button {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 8px;
          cursor: pointer;
          transition: background 0.2s;
        }

        .back-button:hover {
          background: rgba(255, 255, 255, 0.2);
        }

        .support-header h1 {
          margin: 0;
          font-size: 1.5rem;
          font-weight: 700;
        }

        .support-content {
          padding: 1.5rem;
          max-width: 1000px;
          margin: 0 auto;
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .quick-actions {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1.5rem;
        }

        .action-card {
          background: white;
          border-radius: 16px;
          padding: 2rem;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
          text-align: center;
        }

        .action-card.emergency {
          border-left: 4px solid #EF4444;
        }

        .action-card.tutorial {
          border-left: 4px solid #8B5CF6;
        }

        .action-icon {
          width: 64px;
          height: 64px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 1.5rem;
        }

        .action-card.emergency .action-icon {
          background: #FEE2E2;
          color: #EF4444;
        }

        .action-card.tutorial .action-icon {
          background: #EEF2FF;
          color: #8B5CF6;
        }

        .action-content h3 {
          margin: 0 0 0.5rem 0;
          font-size: 1.2rem;
          font-weight: 700;
          color: #1F2937;
        }

        .action-content p {
          color: #6B7280;
          margin-bottom: 1.5rem;
        }

        .action-button {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1.5rem;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          margin: 0 auto;
        }

        .action-button.emergency {
          background: #EF4444;
          color: white;
          border: none;
        }

        .action-button.emergency:hover {
          background: #DC2626;
        }

        .action-button:not(.emergency) {
          background: #8B5CF6;
          color: white;
          border: none;
        }

        .action-button:not(.emergency):hover {
          background: #7C3AED;
        }

        .search-section {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .search-box {
          position: relative;
          max-width: 600px;
          margin: 0 auto;
        }

        .search-icon {
          position: absolute;
          left: 1rem;
          top: 50%;
          transform: translateY(-50%);
          color: #6B7280;
        }

        .search-input {
          width: 100%;
          padding: 1rem 1rem 1rem 3.5rem;
          border: 1px solid #D1D5DB;
          border-radius: 8px;
          font-size: 1rem;
        }

        .search-input:focus {
          outline: none;
          border-color: #8B5CF6;
          box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
        }

        .categories-section {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .categories-section h3 {
          margin: 0 0 1.5rem 0;
          font-size: 1.2rem;
          font-weight: 700;
          color: #1F2937;
        }

        .category-tabs {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .category-tab {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          border: 1px solid #D1D5DB;
          background: white;
          border-radius: 20px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .category-tab.active {
          background: #8B5CF6;
          color: white;
          border-color: #8B5CF6;
        }

        .category-tab:hover:not(.active) {
          background: #F3F4F6;
        }

        .faq-section {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .faq-section h3 {
          margin: 0 0 1.5rem 0;
          font-size: 1.2rem;
          font-weight: 700;
          color: #1F2937;
        }

        .faq-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .faq-item {
          border: 1px solid #E5E7EB;
          border-radius: 8px;
          overflow: hidden;
        }

        .faq-question {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem 1.5rem;
          cursor: pointer;
          transition: background 0.2s;
        }

        .faq-question:hover {
          background: #F9FAFB;
        }

        .faq-question span {
          font-weight: 600;
          color: #374151;
          flex: 1;
        }

        .chevron {
          transition: transform 0.2s;
          color: #6B7280;
        }

        .chevron.expanded {
          transform: rotate(90deg);
        }

        .faq-answer {
          padding: 1.5rem;
          background: #F9FAFB;
          border-top: 1px solid #E5E7EB;
        }

        .faq-answer p {
          margin: 0 0 1rem 0;
          line-height: 1.6;
          color: #4B5563;
        }

        .faq-helpful {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .helpful-buttons {
          display: flex;
          gap: 0.5rem;
        }

        .helpful-btn {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          border: 1px solid #D1D5DB;
          background: white;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .helpful-btn.yes {
          border-color: #10B981;
          color: #10B981;
        }

        .helpful-btn.yes:hover {
          background: #10B981;
          color: white;
        }

        .contacts-section {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .contacts-section h3 {
          margin: 0 0 1.5rem 0;
          font-size: 1.2rem;
          font-weight: 700;
          color: #1F2937;
        }

        .contacts-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
        }

        .contact-card {
          border: 1px solid #E5E7EB;
          border-radius: 12px;
          padding: 1.5rem;
          text-align: center;
        }

        .contact-header {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 1rem;
        }

        .contact-icon {
          color: #8B5CF6;
        }

        .contact-header h4 {
          margin: 0;
          font-size: 1rem;
          font-weight: 700;
          color: #1F2937;
        }

        .contact-value {
          font-size: 1.1rem;
          font-weight: 600;
          color: #374151;
          margin-bottom: 0.5rem;
        }

        .contact-description {
          color: #6B7280;
          font-size: 0.9rem;
          margin-bottom: 0.75rem;
        }

        .contact-availability {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #10B981;
          font-size: 0.8rem;
          font-weight: 600;
        }

        .contact-button {
          background: #8B5CF6;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 6px;
          cursor: pointer;
          transition: background 0.2s;
        }

        .contact-button:hover {
          background: #7C3AED;
        }

        .contact-form-section {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .contact-form-section h3 {
          margin: 0 0 1.5rem 0;
          font-size: 1.2rem;
          font-weight: 700;
          color: #1F2937;
        }

        .support-form {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .form-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .form-group.full-width {
          grid-column: 1 / -1;
        }

        .form-group label {
          font-weight: 600;
          color: #374151;
        }

        .form-input, .form-select {
          padding: 0.75rem;
          border: 1px solid #D1D5DB;
          border-radius: 8px;
          font-size: 1rem;
        }

        .form-input:focus, .form-select:focus {
          outline: none;
          border-color: #8B5CF6;
          box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
        }

        .textarea {
          resize: vertical;
          min-height: 120px;
        }

        .submit-button {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: #8B5CF6;
          color: white;
          border: none;
          padding: 0.75rem 2rem;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s;
          align-self: flex-start;
        }

        .submit-button:hover {
          background: #7C3AED;
        }

        .tutorials-section {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .tutorials-section h3 {
          margin: 0 0 1.5rem 0;
          font-size: 1.2rem;
          font-weight: 700;
          color: #1F2937;
        }

        .tutorials-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1.5rem;
        }

        .tutorial-card {
          border: 1px solid #E5E7EB;
          border-radius: 12px;
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .tutorial-thumbnail {
          width: 60px;
          height: 60px;
          background: #EEF2FF;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #8B5CF6;
          align-self: center;
        }

        .tutorial-info h4 {
          margin: 0;
          font-weight: 600;
          color: #1F2937;
        }

        .tutorial-info p {
          color: #6B7280;
          font-size: 0.9rem;
          margin: 0;
        }

        .tutorial-meta {
          display: flex;
          gap: 1rem;
          margin-top: 0.5rem;
        }

        .duration, .level {
          font-size: 0.8rem;
          color: #6B7280;
          background: #F3F4F6;
          padding: 0.25rem 0.5rem;
          border-radius: 12px;
        }

        .tutorial-button {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: #8B5CF6;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 6px;
          cursor: pointer;
          transition: background 0.2s;
          align-self: flex-start;
        }

        .tutorial-button:hover {
          background: #7C3AED;
        }

        .resources-section {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .resources-section h3 {
          margin: 0 0 1.5rem 0;
          font-size: 1.2rem;
          font-weight: 700;
          color: #1F2937;
        }

        .resources-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
        }

        .resource-item {
          border: 1px solid #E5E7EB;
          border-radius: 12px;
          padding: 1.5rem;
          text-align: center;
        }

        .resource-icon {
          width: 48px;
          height: 48px;
          background: #F3F4F6;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #8B5CF6;
          margin: 0 auto 1rem;
        }

        .resource-content h4 {
          margin: 0 0 0.5rem 0;
          font-weight: 600;
          color: #1F2937;
        }

        .resource-content p {
          color: #6B7280;
          font-size: 0.9rem;
          margin: 0 0 1rem 0;
        }

        .resource-link {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: #8B5CF6;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 6px;
          cursor: pointer;
          transition: background 0.2s;
        }

        .resource-link:hover {
          background: #7C3AED;
        }

        @media (max-width: 768px) {
          .quick-actions {
            grid-template-columns: 1fr;
          }
          
          .category-tabs {
            flex-direction: column;
          }
          
          .contacts-grid {
            grid-template-columns: 1fr;
          }
          
          .form-grid {
            grid-template-columns: 1fr;
          }
          
          .tutorials-grid {
            grid-template-columns: 1fr;
          }
          
          .resources-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default MechanicSupport;
