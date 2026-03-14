import React, { useState, useEffect } from 'react';
import { doctorService } from '../../shared/api';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  Search, Bell, Stethoscope, Heart, 
  Activity, Baby, Bone, Star, MapPin, Menu, Home, Calendar, User, Compass
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

  // Icon mapping for specializations
  const specIcons = {
    'General': Stethoscope,
    'General Physician': Stethoscope,
    'Cardiology': Heart,
    'Cardiologist': Heart,
    'HEART': Heart,
    'Dermatology': Activity,
    'Dermatologist': Activity,
    'Pediatrics': Baby,
    'Pediatrician': Baby,
    'Orthopedics': Bone,
    'Orthopedic': Bone,
    'Dentist': Stethoscope,
    'Eye Specialist': Stethoscope,
    'ENT': Stethoscope,
    'Neurologist': Activity,
    'Psychiatrist': Activity,
    'Gynecologist': Activity,
    'Urologist': Activity,
    'Oncologist': Activity,
    // Fallback
    'default': Stethoscope
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
    const Icon = specIcons[specName] || specIcons['default'];
    return <Icon size={24} />;
  };

  return (
    <div className="healthcare-dashboard">
      {/* Header Section */}
      <div className="dashboard-header">
        <div className="header-top">
          <div className="logo-section">
            <Menu size={24} color="white" />
            <span className="logo-text">ExpertEase</span>
          </div>
          <button className="notification-btn">
            <Bell size={24} color="white" />
          </button>
        </div>

        <div className="user-welcome">
          <span className="welcome-text">Welcome back 👋</span>
          <h1 className="user-name">{user?.user_name || 'Niharika Ratnakar Rothe'}</h1>
        </div>

        <form onSubmit={handleSearch} className="search-bar-container">
          <Search className="search-icon" size={20} color="#7F8C8D" />
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
            <Link to="#" className="view-all">View All &gt;</Link>
          </div>
          
          <div className="specializations-scroll">
            {specializations.length > 0 ? (
              specializations.slice(0, 6).map((spec, index) => (
                <div key={index} className="spec-card" onClick={() => navigate(`/doctors?spec=${spec}`)}>
                  <div className="spec-icon-wrapper">
                    {getSpecIcon(spec)}
                  </div>
                  <span className="spec-name">{spec}</span>
                </div>
              ))
            ) : (
              // Default specializations for demo
              ['Cardiologist', 'Dentist', 'Dermatologist', 'ENT', 'Pediatrician', 'General Physician'].map((spec, index) => (
                <div key={index} className="spec-card" onClick={() => navigate(`/doctors?spec=${spec}`)}>
                  <div className="spec-icon-wrapper">
                    {getSpecIcon(spec)}
                  </div>
                  <span className="spec-name">{spec}</span>
                </div>
              ))
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
              doctors.slice(0, 3).map((doc) => (
                <div key={doc.id || Math.random()} className="doctor-card-horizontal">
                  <div className="doctor-image-placeholder">
                    {doc.name ? doc.name.charAt(0).toUpperCase() : 'D'}
                  </div>
                  <div className="doctor-info">
                    <h3 className="doctor-name">{doc.name || 'Dr. Shubhra Ausarmal'}</h3>
                    <p className="doctor-spec">{doc.specialization || 'Cardiologist'}</p>
                    <div className="doctor-meta">
                      <div className="rating">
                        <Star size={14} fill="#F1C40F" color="#F1C40F" />
                        <span>{doc.rating || '4.9'}</span>
                      </div>
                      <div className="experience">
                        <Activity size={14} color="#7F8C8D" />
                        <span>{doc.experience || '9'} yrs</span>
                      </div>
                    </div>
                    <div className="location">
                      <MapPin size={14} color="#7F8C8D" />
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
              // Demo doctors for preview
              [
                { name: 'Dr. Shubhra Ausarmal', spec: 'Cardiologist', rating: '4.9', exp: '9', loc: 'Apollo Hospital, Delhi', fee: '500' },
                { name: 'Dr. Niharika Rothe', spec: 'Dermatologist', rating: '4.8', exp: '7', loc: 'Fortis Hospital, Mumbai', fee: '600' },
                { name: 'Dr. Aaryan Gurrudatta Bagade', spec: 'ENT', rating: '4.7', exp: '12', loc: 'AIIMS, Delhi', fee: '800' }
              ].map((doc, index) => (
                <div key={index} className="doctor-card-horizontal">
                  <div className="doctor-image-placeholder">
                    {doc.name.charAt(0)}
                  </div>
                  <div className="doctor-info">
                    <h3 className="doctor-name">{doc.name}</h3>
                    <p className="doctor-spec">{doc.spec}</p>
                    <div className="doctor-meta">
                      <div className="rating">
                        <Star size={14} fill="#F1C40F" color="#F1C40F" />
                        <span>{doc.rating}</span>
                      </div>
                      <div className="experience">
                        <Activity size={14} color="#7F8C8D" />
                        <span>{doc.exp} yrs</span>
                      </div>
                    </div>
                    <div className="location">
                      <MapPin size={14} color="#7F8C8D" />
                      <span>{doc.loc}</span>
                    </div>
                  </div>
                  <div className="doctor-action">
                    <span className="consultation-fee">₹{doc.fee} <span className="per-visit">/ visit</span></span>
                    <button className="book-btn">Book Now</button>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
      
      {/* Bottom Navigation */}
      <div className="bottom-navigation">
        <div className="nav-item" onClick={() => navigate('/dashboard')}>
          <Home size={20} color="#7F8C8D" />
          <span>Home</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/ai-care')}>
          <Compass size={20} color="#7F8C8D" />
          <span>AI Care</span>
        </div>
        <div className="nav-item active" onClick={() => navigate('/doctors')}>
          <Compass size={20} color="#8E44AD" />
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
      
      {/* Mobile Bottom Navigation */}
      
      <style>{`
        .healthcare-dashboard {
          background-color: var(--background-light);
          min-height: 100vh;
          padding-bottom: 80px; /* Space for bottom nav */
        }

        /* Header Styles - Exact Match */
        .dashboard-header {
          background: var(--medical-gradient);
          padding: 1rem 1rem 2rem;
          border-bottom-left-radius: 30px;
          border-bottom-right-radius: 30px;
          color: white;
          box-shadow: 0 4px 20px rgba(142, 68, 173, 0.2);
        }

        .header-top {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1.5rem;
        }

        .logo-section {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .logo-text {
          font-size: 1.2rem;
          font-weight: 700;
          color: white;
        }

        .user-welcome {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }

        .welcome-text {
          font-size: 0.9rem;
          opacity: 0.9;
          margin-bottom: 0.25rem;
          display: block;
        }

        .user-name {
          font-size: 1.5rem;
          font-weight: 700;
          margin: 0;
        }

        .notification-btn {
          background: rgba(255, 255, 255, 0.2);
          border: none;
          width: 40px;
          height: 40px;
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
          font-size: 0.9rem;
          color: var(--text-primary);
        }

        .search-input::placeholder {
          color: #BDC3C7;
        }

        /* Content Styles */
        .dashboard-content {
          padding: 1rem;
          margin-top: -1rem;
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
          font-size: 1.1rem;
          font-weight: 700;
          color: var(--text-primary);
        }

        .view-all {
          color: var(--accent-blue);
          text-decoration: none;
          font-size: 0.85rem;
          font-weight: 600;
        }

        /* Specializations Scroll - Exact Match */
        .specializations-scroll {
          display: flex;
          gap: 0.8rem;
          overflow-x: auto;
          padding-bottom: 0.5rem;
          scrollbar-width: none;
        }

        .specializations-scroll::-webkit-scrollbar {
          display: none;
        }

        .spec-card {
          min-width: 70px;
          display: flex;
          flex-direction: column;
          align-items: center;
          cursor: pointer;
        }

        .spec-icon-wrapper {
          width: 60px;
          height: 60px;
          background: white;
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 0.5rem;
          box-shadow: var(--shadow-sm);
          transition: transform 0.2s;
          color: var(--accent-blue);
        }

        .spec-card:hover .spec-icon-wrapper {
          transform: translateY(-3px);
          box-shadow: var(--shadow-md);
        }

        .spec-name {
          font-size: 0.75rem;
          font-weight: 500;
          color: var(--text-primary);
          text-align: center;
        }

        /* Top Doctors List - Exact Match */
        .doctors-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .doctor-card-horizontal {
          background: white;
          border-radius: 20px;
          padding: 1rem;
          display: flex;
          align-items: center;
          gap: 1rem;
          box-shadow: var(--shadow-sm);
          transition: box-shadow 0.2s;
        }
        
        .doctor-card-horizontal:hover {
          box-shadow: var(--shadow-md);
        }

        .doctor-image-placeholder {
          width: 60px;
          height: 60px;
          background: #E8EAF6;
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.5rem;
          font-weight: 700;
          color: var(--accent-blue);
          flex-shrink: 0;
        }

        .doctor-info {
          flex: 1;
          min-width: 150px;
        }

        .doctor-name {
          font-size: 1rem;
          font-weight: 700;
          margin-bottom: 0.25rem;
          color: var(--text-primary);
        }

        .doctor-spec {
          font-size: 0.85rem;
          color: var(--text-secondary);
          margin-bottom: 0.5rem;
        }

        .doctor-meta {
          display: flex;
          gap: 0.8rem;
          margin-bottom: 0.5rem;
        }

        .doctor-meta div {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 0.8rem;
          color: var(--text-secondary);
        }
        
        .location {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 0.8rem;
          color: var(--text-secondary);
        }

        .doctor-action {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 0.5rem;
          min-width: 80px;
        }

        .consultation-fee {
          font-size: 0.95rem;
          font-weight: 700;
          color: var(--accent-blue);
        }

        .per-visit {
          font-size: 0.75rem;
          font-weight: 400;
          color: var(--text-secondary);
        }

        .book-btn {
          background: var(--medical-gradient);
          color: white;
          border: none;
          padding: 0.5rem 0.8rem;
          border-radius: 10px;
          font-weight: 600;
          cursor: pointer;
          transition: opacity 0.2s;
          white-space: nowrap;
          font-size: 0.85rem;
        }

        .book-btn:hover {
          opacity: 0.9;
        }

        /* Bottom Navigation - Exact Match */
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

        /* Bottom Navigation styles removed - moved to BottomNav.css */
        
        /* Responsive Adjustments */
        @media (min-width: 768px) {
          .healthcare-dashboard {
             padding-bottom: 2rem;
             max-width: 1200px;
             margin: 0 auto;
          }

          .dashboard-header {
            padding: 2.5rem 3rem 4rem;
          }

          .header-top {
            margin-bottom: 2rem;
          }

          .user-name {
            font-size: 2.2rem;
          }

          .search-bar-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 1rem 1.5rem;
          }

          .search-input {
            font-size: 1.1rem;
          }

          .dashboard-content {
            padding: 2rem 3rem;
            margin-top: -2rem;
          }

          .section-header h2 {
            font-size: 1.5rem;
          }

          .view-all {
            font-size: 1rem;
          }

          .specializations-scroll {
            gap: 1.5rem;
          }

          .spec-card {
            min-width: 100px;
          }

          .spec-icon-wrapper {
            width: 80px;
            height: 80px;
            border-radius: 24px;
          }

          .spec-name {
            font-size: 0.95rem;
          }

          .doctors-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 1.5rem;
          }
          
          .doctor-card-horizontal {
            padding: 1.5rem;
            border-radius: 24px;
          }

          .doctor-image-placeholder {
            width: 100px;
            height: 100px;
            font-size: 2.5rem;
          }

          .doctor-name {
            font-size: 1.3rem;
          }

          .doctor-spec {
            font-size: 1rem;
            margin-bottom: 0.75rem;
          }

          .doctor-meta {
            gap: 1.5rem;
            margin-bottom: 0.75rem;
          }

          .doctor-meta div {
            font-size: 0.95rem;
          }
          
          .location {
            font-size: 0.95rem;
          }

          .consultation-fee {
            font-size: 1.3rem;
          }

          .book-btn {
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            border-radius: 16px;
          }
        }

        @media (min-width: 1024px) {
          .dashboard-header {
            padding: 3rem 4rem 5rem;
          }

          .dashboard-content {
            padding: 2.5rem 4rem;
          }

          .specializations-scroll {
            gap: 2rem;
          }

          .spec-card {
            min-width: 110px;
          }

          .spec-icon-wrapper {
            width: 90px;
            height: 90px;
          }

          .doctors-list {
            grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
            gap: 2rem;
          }

          .doctor-card-horizontal {
            padding: 2rem;
          }

          .doctor-image-placeholder {
            width: 120px;
            height: 120px;
            font-size: 3rem;
          }
        }

        @media (min-width: 1440px) {
          .dashboard-header {
            padding: 3.5rem 5rem 6rem;
          }

          .dashboard-content {
            padding: 3rem 5rem;
          }

          .doctors-list {
            grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
          }
        }
        
        @media (max-width: 767px) {
          .dashboard-header {
            padding: 1.5rem 1rem 3rem;
          }

          .header-top {
            margin-bottom: 1rem;
          }

          .user-name {
            font-size: 1.5rem;
          }

          .welcome-text {
            font-size: 0.8rem;
          }

          .notification-btn {
            width: 40px;
            height: 40px;
          }

          .search-bar-container {
            padding: 0.6rem 0.8rem;
          }

          .search-input {
            font-size: 0.9rem;
          }

          .dashboard-content {
            padding: 1rem;
            margin-top: -1.5rem;
          }

          .section-header {
            margin-bottom: 0.8rem;
          }

          .section-header h2 {
            font-size: 1.1rem;
          }

          .view-all {
            font-size: 0.85rem;
          }

          .specializations-scroll {
            gap: 0.8rem;
          }

          .spec-card {
            min-width: 75px;
          }

          .spec-icon-wrapper {
            width: 60px;
            height: 60px;
            border-radius: 16px;
          }

          .spec-name {
            font-size: 0.75rem;
          }

          .doctor-card-horizontal {
            padding: 1rem;
            border-radius: 16px;
            gap: 0.8rem;
          }

          .doctor-image-placeholder {
            width: 60px;
            height: 60px;
            font-size: 1.5rem;
            border-radius: 16px;
          }

          .doctor-name {
            font-size: 1rem;
          }

          .doctor-spec {
            font-size: 0.85rem;
            margin-bottom: 0.4rem;
          }

          .doctor-meta {
            gap: 0.8rem;
            margin-bottom: 0.4rem;
            flex-wrap: wrap;
          }

          .doctor-meta div {
            font-size: 0.8rem;
          }
          
          .location {
            font-size: 0.8rem;
          }

          .doctor-action {
            min-width: 80px;
            gap: 0.3rem;
          }

          .consultation-fee {
            font-size: 0.95rem;
          }

          .per-visit {
            font-size: 0.75rem;
          }

          .book-btn {
            padding: 0.5rem 0.8rem;
            font-size: 0.85rem;
            border-radius: 10px;
          }
        }

        @media (max-width: 480px) {
          .dashboard-header {
            padding: 1rem 0.8rem 2.5rem;
          }

          .user-name {
            font-size: 1.3rem;
          }

          .search-bar-container {
            padding: 0.5rem 0.7rem;
          }

          .dashboard-content {
            padding: 0.8rem;
          }

          .specializations-scroll {
            gap: 0.6rem;
          }

          .spec-card {
            min-width: 70px;
          }

          .spec-icon-wrapper {
            width: 55px;
            height: 55px;
          }

          .spec-name {
            font-size: 0.7rem;
          }

          .doctor-card-horizontal {
            padding: 0.8rem;
            flex-direction: column;
            align-items: flex-start;
            gap: 0.6rem;
          }

          .doctor-image-placeholder {
            width: 50px;
            height: 50px;
            font-size: 1.2rem;
          }

          .doctor-info {
            width: 100%;
          }

          .doctor-action {
            width: 100%;
            flex-direction: row;
            justify-content: space-between;
            align-items: center;
            margin-top: 0.5rem;
          }

          .book-btn {
            flex-shrink: 0;
          }
        }

        @media (max-width: 360px) {
          .dashboard-header {
            padding: 0.8rem 0.6rem 2rem;
          }

          .user-name {
            font-size: 1.2rem;
          }

          .doctor-card-horizontal {
            padding: 0.6rem;
          }

          .doctor-image-placeholder {
            width: 45px;
            height: 45px;
          }

          .book-btn {
            padding: 0.4rem 0.6rem;
            font-size: 0.8rem;
          }
        }

        /* Landscape orientations for mobile */
        @media (max-height: 600px) and (orientation: landscape) {
          .dashboard-header {
            padding: 1rem 1rem 2rem;
          }

          .specializations-scroll {
            gap: 0.8rem;
          }

          .spec-icon-wrapper {
            width: 50px;
            height: 50px;
          }

          .spec-name {
            font-size: 0.7rem;
          }
        }

        /* Tablet portrait mode */
        @media (min-width: 768px) and (max-width: 1023px) and (orientation: portrait) {
          .doctors-list {
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          }

          .doctor-card-horizontal {
            padding: 1.2rem;
          }
        }

        /* High DPI displays */
        @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
          .doctor-image-placeholder,
          .spec-icon-wrapper {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
          }
        }

        /* Dark mode support preparation */
        @media (prefers-color-scheme: dark) {
          .doctor-card-horizontal {
            background: #2d3748;
            color: #e2e8f0;
          }

          .search-bar-container {
            background: #2d3748;
          }

          .spec-icon-wrapper {
            background: #2d3748;
          }
        }
      `}</style>
    </div>
  );
};

export default DoctorSearch;
