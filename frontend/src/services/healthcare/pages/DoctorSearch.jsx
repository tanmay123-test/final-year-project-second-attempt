import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import HealthcareBottomNav from '../components/HealthcareBottomNav';
import '../styles/DoctorSearch.css';
import '../styles/healthcare-shared.css';
import HealthcareSidebarLayout from '../components/HealthcareSidebarLayout';

const DoctorSearch = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  
  // State management
  const [doctors, setDoctors] = useState([]);
  const [specializations, setSpecializations] = useState([]);
  const [activeSpecialization, setActiveSpec] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [resultCount, setResultCount] = useState(0);
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [sortBy, setSortBy] = useState('rating');
  const [debounceTimer, setDebounceTimer] = useState(null);
  
  // Auth headers
  const token = localStorage.getItem('token');
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  // Map doctor data from API
  const mapDoctor = (doc) => ({
    id: doc.id || doc.worker_id,
    name: doc.name || doc.worker_name,
    specialization: doc.specialization,
    rating: doc.rating || doc.average_rating || 4.5,
    experience: doc.experience_years || doc.years_experience || '5',
    location: doc.clinic_location || doc.hospital || 'City Hospital',
    fee: doc.consultation_fee || doc.fee || 500,
    initial: (doc.name || doc.worker_name || 'D')[0].toUpperCase(),
    photo: doc.profile_photo || doc.photo || null
  });

  // Sort doctors function
  const sortDoctors = (doctors, sortBy) => {
    switch(sortBy) {
      case 'rating': 
        return [...doctors].sort((a,b) => b.rating - a.rating);
      case 'fee_asc': 
        return [...doctors].sort((a,b) => a.fee - b.fee);
      case 'fee_desc': 
        return [...doctors].sort((a,b) => b.fee - a.fee);
      case 'experience': 
        return [...doctors].sort((a,b) => b.experience - a.experience);
      default: return doctors;
    }
  };

  // Fetch initial data
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoading(true);
        const [doctorsRes, specsRes] = await Promise.all([
          fetch('/healthcare/doctors', { headers }),
          fetch('/healthcare/specializations', { headers })
        ]);
        
        const doctorsData = await doctorsRes.json();
        const specsData = await specsRes.json();
        
        const mappedDoctors = (doctorsData.doctors || doctorsData || []).map(mapDoctor);
        const sortedDoctors = sortDoctors(mappedDoctors, sortBy);
        
        setDoctors(sortedDoctors);
        setResultCount(sortedDoctors.length);
        setSpecializations([
          'All', 
          ...(specsData.specializations || specsData || [])
        ]);
      } catch (err) {
        console.error('Failed to fetch:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchInitialData();
  }, []);

  // Handle URL params
  useEffect(() => {
    const specParam = searchParams.get('spec');
    if (specParam) {
      handleSpecTab(specParam);
      setActiveSpec(specParam);
    }
  }, [searchParams]);

  // Handle search with debouncing
  const handleSearch = (query) => {
    setSearchQuery(query);
    clearTimeout(debounceTimer);
    const timer = setTimeout(async () => {
      if (query.trim().length > 0) {
        try {
          const res = await fetch(
            `/healthcare/search?q=${encodeURIComponent(query)}`,
            { headers }
          );
          const data = await res.json();
          const mappedData = (data.doctors || data || []).map(mapDoctor);
          const sortedData = sortDoctors(mappedData, sortBy);
          setDoctors(sortedData);
          setResultCount(sortedData.length);
        } catch (err) {
          console.error('Search failed:', err);
        }
      } else {
        // Reset to all doctors
        fetchDoctors(activeSpecialization);
      }
    }, 400); // 400ms debounce
    setDebounceTimer(timer);
  };

  // Fetch doctors by specialization
  const fetchDoctors = async (spec) => {
    try {
      setLoading(true);
      let url = spec === 'All' 
        ? '/healthcare/doctors'
        : `/healthcare/doctors/${spec}`;
      
      const res = await fetch(url, { headers });
      const data = await res.json();
      const mappedData = (data.doctors || data || []).map(mapDoctor);
      const sortedData = sortDoctors(mappedData, sortBy);
      setDoctors(sortedData);
      setResultCount(sortedData.length);
    } catch (err) {
      console.error('Failed to fetch doctors:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle specialization tab click
  const handleSpecTab = async (spec) => {
    setActiveSpec(spec);
    await fetchDoctors(spec);
  };

  // Handle sort change
  const handleSortChange = (newSortBy) => {
    setSortBy(newSortBy);
    const sortedDoctors = sortDoctors(doctors, newSortBy);
    setDoctors(sortedDoctors);
    setShowFilterModal(false);
  };

  // Loading skeleton component
  const LoadingSkeleton = () => (
    <div className="doctor-card skeleton">
      <div className="doctor-card-top">
        <div className="doctor-avatar skeleton-shimmer"></div>
        <div className="doctor-info skeleton-shimmer">
          <div className="skeleton-line"></div>
          <div className="skeleton-line short"></div>
          <div className="skeleton-line medium"></div>
        </div>
      </div>
      <div className="doctor-card-bottom">
        <div className="skeleton-line"></div>
        <div className="skeleton-button"></div>
      </div>
    </div>
  );

  return (
    <HealthcareSidebarLayout>
      <div className="page-inner-content">
        <div className="doctor-search-page explore-page">
          <div className="explore-header">
            <h1 className="explore-title">Explore Doctors</h1>

            <div className="search-filter-row">
              <div className="search-input-box">
                <span className="search-icon">🔍</span>
                <input
                  type="text"
                  className="search-input"
                  placeholder="Search doctors, specializations..."
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                />
              </div>
              <button className="filter-btn" onClick={() => setShowFilterModal(true)}>
                ⚙️
              </button>
            </div>
          </div>

          <div className="spec-tabs-row">
            {specializations.map((spec) => (
              <button
                key={spec}
                className={`spec-tab ${activeSpecialization === spec ? 'active' : ''}`}
                onClick={() => handleSpecTab(spec)}
              >
                {spec}
              </button>
            ))}
          </div>

          <div className="results-count">
            {resultCount} doctor{resultCount !== 1 ? 's' : ''} found
          </div>

          <div className="doctors-list">
            {loading ? (
              [1, 2, 3].map((i) => <LoadingSkeleton key={i} />)
            ) : doctors.length > 0 ? (
              doctors.map((doctor) => (
                <div key={doctor.id} className="doctor-card">
                  <div className="doctor-card-top">
                    <div className="doctor-avatar">
                      {doctor.photo ? <img src={doctor.photo} alt={doctor.name} /> : doctor.initial}
                    </div>
                    <div className="doctor-info">
                      <div className="doctor-name">{doctor.name}</div>
                      <div className="doctor-spec">{doctor.specialization}</div>
                      <div className="doctor-meta">
                        <span>⭐ {doctor.rating}</span>
                        <span>🕐 {doctor.experience} yrs</span>
                      </div>
                      <div className="doctor-location">📍 {doctor.location}</div>
                    </div>
                  </div>
                  <div className="doctor-card-bottom">
                    <div className="doctor-fee-text">
                      ₹{doctor.fee}
                      <span className="fee-unit"> / visit</span>
                    </div>
                    <button className="book-btn" onClick={() => navigate(`/healthcare/book/${doctor.id}`)}>
                      Book Now
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-state">
                <div className="empty-icon">🔍</div>
                <div className="empty-title">No doctors found</div>
                <div className="empty-subtitle">Try a different search or specialization</div>
              </div>
            )}
          </div>

          {showFilterModal && (
            <div className="filter-modal-overlay" onClick={() => setShowFilterModal(false)}>
              <div className="filter-modal" onClick={(e) => e.stopPropagation()}>
                <h3 className="filter-title">Sort & Filter</h3>

                <div className="filter-options">
                  <label className="filter-option">
                    <input
                      type="radio"
                      name="sort"
                      value="rating"
                      checked={sortBy === 'rating'}
                      onChange={() => handleSortChange('rating')}
                    />
                    <span className="filter-label">⭐ Highest Rated</span>
                  </label>

                  <label className="filter-option">
                    <input
                      type="radio"
                      name="sort"
                      value="fee_asc"
                      checked={sortBy === 'fee_asc'}
                      onChange={() => handleSortChange('fee_asc')}
                    />
                    <span className="filter-label">💰 Fee: Low to High</span>
                  </label>

                  <label className="filter-option">
                    <input
                      type="radio"
                      name="sort"
                      value="fee_desc"
                      checked={sortBy === 'fee_desc'}
                      onChange={() => handleSortChange('fee_desc')}
                    />
                    <span className="filter-label">💰 Fee: High to Low</span>
                  </label>

                  <label className="filter-option">
                    <input
                      type="radio"
                      name="sort"
                      value="experience"
                      checked={sortBy === 'experience'}
                      onChange={() => handleSortChange('experience')}
                    />
                    <span className="filter-label">🕐 Most Experienced</span>
                  </label>
                </div>

                <button className="apply-filter-btn" onClick={() => setShowFilterModal(false)}>
                  Apply
                </button>
              </div>
            </div>
          )}

          <HealthcareBottomNav activeTab="explore" />
        </div>
      </div>
    </HealthcareSidebarLayout>
  );
};

export default DoctorSearch;
