import React, { useState, useEffect } from 'react';
import { doctorService } from '../../../services/api';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { 
  Search, Bell, Stethoscope, Heart, 
  Activity, Baby, Bone, Star, MapPin
} from 'lucide-react';

const DoctorSearch = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const specializationParam = searchParams.get('spec');

  const [doctors, setDoctors] = useState([]);
  const [specializations, setSpecializations] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [showAllSpecs, setShowAllSpecs] = useState(false);

  const emojiMap = {
    'Cardiologist': '❤️',
    'Dentist': '🦷',
    'Dermatologist': '🧴',
    'ENT': '👂',
    'Eye Specialist': '👁️',
    'General Physician': '🩺',
    'Gynecologist': '🌸',
    'Heart': '💗',
    'Neurologist': '🧠',
    'Oncologist': '🎗️',
    'Orthopedic': '🦴',
    'Pediatrician': '👶',
    'Psychiatrist': '🧘',
    'Surgeon': '🔪',
    'Urologist': '💧',
    'default': '🩺'
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch specializations
        const specsRes = await doctorService.getSpecializations();
        setSpecializations(specsRes.data.specializations);

        // Fetch doctors based on URL param or get all
        let docsRes;
        if (specializationParam) {
          docsRes = await doctorService.getDoctorsBySpecialization(specializationParam);
        } else {
          docsRes = await doctorService.getAllDoctors();
        }
        setDoctors(docsRes.data.doctors);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [specializationParam]);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await doctorService.searchDoctors(searchQuery);
      setDoctors(res.data.doctors);
    } catch (error) {
      console.error('Error searching doctors:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSpecIcon = (specName) => {
    const emoji = emojiMap[specName] || emojiMap['default'];
    return <span className="spec-emoji">{emoji}</span>;
  };

  return (
    <div className="healthcare-dashboard">
      {/* Header Section */}
      <div className="dashboard-header">
        <div className="header-top">
          <div className="user-info">
            <span className="welcome-text">Welcome back 👋</span>
            <h1 className="user-name">{user?.user_name || 'Guest'}</h1>
          </div>
          <button className="notification-btn">
            <Bell size={24} />
          </button>
        </div>

        <form onSubmit={handleSearch} className="search-bar-container">
          <Search className="search-icon" size={20} />
          <input
            type="text"
            placeholder="Search doctors, specializations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </form>
      </div>

      <div className="dashboard-content">
        {/* Specializations Section */}
        <section className="section specializations-section">
          <div className="section-header">
            <h2>Specializations</h2>
            <Link to="#" className="view-all" onClick={(e) => { e.preventDefault(); setShowAllSpecs((v) => !v); }}>
              {showAllSpecs ? 'Close' : 'View All >'}
            </Link>
          </div>
          
          <div className={showAllSpecs ? 'specializations-grid' : 'specializations-scroll'}>
            {specializations.length > 0 ? (
              specializations.map((spec, index) => (
                <div key={index} className="spec-card" onClick={() => navigate(`/doctors?spec=${spec}`)}>
                  <div className="spec-icon-wrapper">
                    {getSpecIcon(spec)}
                  </div>
                  <span className="spec-name">{spec}</span>
                </div>
              ))
            ) : (
              <p>Loading specializations...</p>
            )}
          </div>
        </section>

        {/* Top Doctors Section */}
        <section className="section doctors-section">
          <div className="section-header">
            <h2>Top Doctors</h2>
            <Link to="#" className="view-all">See All &gt;</Link>
          </div>

          <div className="doctors-list">
            {loading ? (
              <div className="loading-state">Loading doctors...</div>
            ) : doctors.length > 0 ? (
              doctors.map((doc) => (
                <div key={doc.id || Math.random()} className="doctor-card-horizontal">
                  <div className="doctor-image-placeholder">
                    {doc.name ? doc.name.charAt(0) : 'D'}
                  </div>
                  <div className="doctor-info">
                    <h3 className="doctor-name">{doc.name}</h3>
                    <p className="doctor-spec">{doc.specialization}</p>
                    <div className="doctor-meta">
                      <div className="rating">
                        <Star size={14} fill="#F1C40F" color="#F1C40F" />
                        <span>{doc.rating || '4.9'}</span>
                      </div>
                      <div className="experience">
                        <Activity size={14} />
                        <span>{doc.experience || '5'} yrs</span>
                      </div>
                    </div>
                    <div className="location">
                      <MapPin size={14} />
                      <span>{doc.location || 'Apollo Hospital, Delhi'}</span>
                    </div>
                  </div>
                  <div className="doctor-action">
                    <span className="consultation-fee">₹{doc.fee || '500'} <span className="per-visit">/ visit</span></span>
                    <button 
                      className="book-btn"
                      onClick={() => navigate(`/book/${doc.id}`)}
                    >
                      Book Now
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-state">No doctors found matching your criteria.</div>
            )}
          </div>
        </section>
      </div>
      
      {/* Mobile Bottom Navigation */}
      
      <style>{`
        .healthcare-dashboard {
          background-color: var(--background-light);
          min-height: 100vh;
        }

        /* Header Styles */
        .dashboard-header {
          background: var(--medical-gradient);
          padding: 2rem 1.5rem 4rem;
          border-bottom-left-radius: 30px;
          border-bottom-right-radius: 30px;
          color: white;
          box-shadow: 0 4px 20px rgba(52, 152, 219, 0.2);
        }

        .header-top {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1.5rem;
        }

        .welcome-text {
          font-size: 0.9rem;
          opacity: 0.9;
          margin-bottom: 0.25rem;
          display: block;
        }

        .user-name {
          font-size: 1.8rem;
          font-weight: 700;
          margin: 0;
        }

        .notification-btn {
          background: rgba(255, 255, 255, 0.2);
          border: none;
          width: 45px;
          height: 45px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          cursor: pointer;
          transition: background 0.2s;
        }

        .notification-btn:hover {
          background: rgba(255, 255, 255, 0.3);
        }

        .search-bar-container {
          background: white;
          border-radius: 16px;
          padding: 0.75rem 1rem;
          display: flex;
          align-items: center;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .search-icon {
          color: #95A5A6;
          margin-right: 0.75rem;
        }

        .search-input {
          border: none;
          outline: none;
          width: 100%;
          font-size: 1rem;
          color: var(--text-primary);
        }

        .search-input::placeholder {
          color: #BDC3C7;
        }

        /* Content Styles */
        .dashboard-content {
          padding: 1.5rem;
          margin-top: -1rem; /* Overlap slightly if needed, or just normal spacing */
        }

        .section {
          margin-bottom: 2rem;
        }

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .section-header h2 {
          font-size: 1.25rem;
          font-weight: 700;
          color: var(--text-primary);
        }

        .view-all {
          color: var(--accent-blue); /* Replaced Purple */
          text-decoration: none;
          font-size: 0.9rem;
          font-weight: 600;
        }

        .specializations-scroll {
          display: flex;
          gap: 0.75rem;
          overflow-x: auto;
          padding-bottom: 0.5rem;
          scrollbar-width: none;
        }

        .specializations-scroll::-webkit-scrollbar {
          display: none;
        }

        .specializations-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
          gap: 1rem;
        }

        .spec-card {
          background: #F8FAFC;
          border-radius: 18px;
          padding: 0.8rem 0.6rem;
          display: flex;
          flex-direction: column;
          align-items: center;
          cursor: pointer;
          box-shadow: var(--shadow-sm);
          transition: transform 0.2s, box-shadow 0.2s;
          min-width: 90px;
        }

        .spec-card:hover {
          transform: translateY(-2px);
          box-shadow: var(--shadow-md);
        }

        .specializations-scroll .spec-icon-wrapper {
          width: 60px;
          height: 60px;
          border-radius: 16px;
          background: #F1F5F9;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 0.5rem;
        }

        .specializations-grid .spec-icon-wrapper {
          width: 80px;
          height: 80px;
          border-radius: 22px;
          background: #F1F5F9;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 0.6rem;
        }

        .specializations-scroll .spec-emoji { font-size: 24px; line-height: 1; }
        .specializations-grid .spec-emoji { font-size: 32px; line-height: 1; }

        .spec-name {
          font-size: 0.85rem;
          font-weight: 500;
          color: var(--text-primary);
          text-align: center;
        }

        /* Top Doctors List */
        .doctors-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .doctor-card-horizontal {
          background: white;
          border-radius: 20px;
          padding: 1.25rem;
          display: flex;
          align-items: center; /* Align center vertically? Maybe top better for responsive */
          gap: 1rem;
          box-shadow: var(--shadow-sm);
          transition: box-shadow 0.2s;
          flex-wrap: wrap; /* Allow wrapping on very small screens */
        }
        
        .doctor-card-horizontal:hover {
          box-shadow: var(--shadow-md);
        }

        .doctor-image-placeholder {
          width: 80px;
          height: 80px;
          background: #E8EAF6; /* Light placeholder */
          border-radius: 20px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 2rem;
          font-weight: 700;
          color: var(--accent-blue); /* Replaced Purple */
          flex-shrink: 0;
        }

        .doctor-info {
          flex: 1;
          min-width: 150px;
        }

        .doctor-name {
          font-size: 1.1rem;
          font-weight: 700;
          margin-bottom: 0.25rem;
          color: var(--text-primary);
        }

        .doctor-spec {
          font-size: 0.9rem;
          color: var(--text-secondary);
          margin-bottom: 0.5rem;
        }

        .doctor-meta {
          display: flex;
          gap: 1rem;
          margin-bottom: 0.5rem;
        }

        .doctor-meta div {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 0.85rem;
          color: var(--text-secondary);
        }
        
        .location {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 0.85rem;
          color: var(--text-secondary);
        }

        .doctor-action {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 0.5rem;
          min-width: 100px;
        }

        .consultation-fee {
          font-size: 1.1rem;
          font-weight: 700;
          color: var(--accent-blue); /* Replaced Purple */
        }

        .per-visit {
          font-size: 0.8rem;
          font-weight: 400;
          color: var(--text-secondary);
        }

        .book-btn {
          background: var(--medical-gradient); /* Replaced Purple */
          color: white;
          border: none;
          padding: 0.6rem 1.2rem;
          border-radius: 12px;
          font-weight: 600;
          cursor: pointer;
          transition: opacity 0.2s;
          white-space: nowrap;
        }

        .book-btn:hover {
          opacity: 0.9;
        }

        /* Bottom Navigation styles removed - moved to BottomNav.css */
        
        /* Responsive Adjustments */
        @media (min-width: 768px) {
          .healthcare-dashboard {
             padding-bottom: 2rem;
          }

          .doctors-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          }
          
          .doctor-action {
            align-items: flex-start;
            margin-top: 1rem;
            flex-direction: row;
            justify-content: space-between;
            width: 100%;
          }
          
          .doctor-card-horizontal {
            flex-direction: column;
            align-items: flex-start;
          }
          
          .doctor-image-placeholder {
            width: 100%;
            height: 150px;
            margin-bottom: 1rem;
          }
          
          .doctor-action {
            align-items: center;
          }
        }
        
        @media (max-width: 480px) {
          .doctor-card-horizontal {
            align-items: flex-start;
          }
          
          .doctor-action {
            margin-left: auto; /* Push to right */
          }
        }
      `}</style>
    </div>
  );
};

export default DoctorSearch;
