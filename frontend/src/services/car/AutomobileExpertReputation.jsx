import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Trophy, 
  Star, 
  Award, 
  Medal,
  Target,
  Zap,
  Shield,
  Heart,
  ThumbsUp,
  AlertCircle
} from 'lucide-react';
import AutomobileExpertBottomNav from '../../components/AutomobileExpertBottomNav';

const AutomobileExpertReputation = () => {
  const navigate = useNavigate();
  const [reputationData, setReputationData] = useState({
    avgRating: 0,
    totalRatings: 0,
    ratingDistribution: { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 },
    badges: [],
    achievements: [],
    reputationScore: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReputationData = async () => {
    try {
      const workerData = JSON.parse(localStorage.getItem('automobileExpertData') || '{}');
      const workerId = workerData.id;
      
      if (!workerId) {
        navigate('/worker/car/automobile-expert/login');
        return;
      }

      const response = await fetch(`http://localhost:5000/api/expert-availability/reputation/${workerId}`);
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.success) {
          setReputationData(data.reputation || {});
        } else {
          setError(data.error || 'Failed to load reputation data');
        }
      } else {
        setError('Failed to load reputation data');
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching reputation data:', error);
      setError('Error loading reputation data');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReputationData();
  }, []);

  const getDefaultBadges = () => [
    { id: 1, name: 'First Consultation', icon: Trophy, color: '#f59e0b', description: 'Completed your first consultation', earned: reputationData.totalRatings > 0 },
    { id: 2, name: 'Rising Star', icon: Star, color: '#3b82f6', description: 'Maintained 4+ star rating', earned: reputationData.avgRating >= 4 },
    { id: 3, name: 'Quick Responder', icon: Zap, color: '#8b5cf6', description: 'Fast response times', earned: true },
    { id: 4, name: 'Trusted Expert', icon: Shield, color: '#10b981', description: 'Built trust with users', earned: reputationData.totalRatings >= 10 },
    { id: 5, name: 'Customer Favorite', icon: Heart, color: '#ef4444', description: 'High customer satisfaction', earned: reputationData.avgRating >= 4.5 },
    { id: 6, name: 'Top Performer', icon: Medal, color: '#6366f1', description: 'Consistent excellence', earned: reputationData.totalRatings >= 25 }
  ];

  const getDefaultAchievements = () => [
    { id: 1, title: 'Expert Status', description: 'Completed 10+ consultations', progress: Math.min((reputationData.totalRatings / 10) * 100, 100), target: 10 },
    { id: 2, title: 'Master Consultant', description: 'Completed 50+ consultations', progress: Math.min((reputationData.totalRatings / 50) * 100, 100), target: 50 },
    { id: 3, title: 'Rating Champion', description: 'Maintain 4.5+ stars', progress: reputationData.avgRating >= 4.5 ? 100 : (reputationData.avgRating / 4.5) * 100, target: 4.5 },
    { id: 4, title: 'Response Master', description: 'Quick response achievement', progress: 75, target: 100 }
  ];

  if (loading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        backgroundColor: '#f9fafb',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            width: '40px', 
            height: '40px', 
            border: '4px solid #e5e7eb',
            borderTop: '4px solid #8b5cf6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }}></div>
          <p style={{ color: '#8b5cf6' }}>Loading reputation data...</p>
        </div>
      </div>
    );
  }

  const badges = getDefaultBadges();
  const achievements = getDefaultAchievements();

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f9fafb',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      paddingBottom: '80px'
    }}>
      {/* Header */}
      <div style={{
        backgroundColor: '#8b5cf6',
        color: 'white',
        padding: '16px 20px',
        boxShadow: '0 2px 4px rgba(139, 92, 246, 0.1)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={() => navigate('/worker/car/automobile-expert/homepage')}
            style={{
              background: 'none',
              border: 'none',
              color: 'white',
              cursor: 'pointer',
              padding: '4px',
              fontSize: '16px'
            }}
          >
            ← Back
          </button>
          <div>
            <h1 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>🏆 Reputation & Badges</h1>
            <p style={{ margin: 0, fontSize: '14px', opacity: 0.9 }}>
              View your reputation, badges, and achievements
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
        {error ? (
          <div style={{
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <AlertCircle size={20} style={{ color: '#dc2626' }} />
            <div>
              <h3 style={{ margin: '0 0 4px 0', color: '#991b1b' }}>Error</h3>
              <p style={{ margin: 0, color: '#7f1d1d' }}>{error}</p>
            </div>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '20px' }}>
            {/* Reputation Score */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              border: '1px solid #e5e7eb',
              textAlign: 'center'
            }}>
              <Trophy size={48} style={{ margin: '0 auto 16px', color: '#f59e0b' }} />
              <h2 style={{ margin: '0 0 8px 0', fontSize: '32px', fontWeight: '700', color: '#111827' }}>
                Reputation Score
              </h2>
              <div style={{ fontSize: '48px', fontWeight: '700', color: '#2563eb', marginBottom: '8px' }}>
                {Math.round(reputationData.reputationScore || (reputationData.avgRating * 100))}
              </div>
              <p style={{ margin: 0, fontSize: '16px', color: '#6b7280' }}>
                Based on {reputationData.totalRatings} ratings
              </p>
            </div>

            {/* Rating Overview */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              border: '1px solid #e5e7eb'
            }}>
              <h2 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: '600', color: '#111827' }}>
                Rating Overview
              </h2>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                    <Star size={24} style={{ color: '#f59e0b' }} />
                    <span style={{ fontSize: '24px', fontWeight: '600', color: '#111827' }}>
                      {(reputationData.avgRating || 0).toFixed(1)} / 5.0
                    </span>
                  </div>
                  <p style={{ margin: 0, fontSize: '14px', color: '#6b7280' }}>
                    Average rating from {reputationData.totalRatings} users
                  </p>
                </div>

                <div>
                  <h3 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: '500', color: '#374151' }}>
                    Rating Distribution
                  </h3>
                  {[5, 4, 3, 2, 1].map((rating) => (
                    <div key={rating} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                      <span style={{ fontSize: '14px', color: '#6b7280', width: '20px' }}>{rating}</span>
                      <Star size={14} style={{ color: '#f59e0b' }} />
                      <div style={{ 
                        flex: 1, 
                        height: '8px', 
                        backgroundColor: '#e5e7eb', 
                        borderRadius: '4px',
                        overflow: 'hidden'
                      }}>
                        <div style={{
                          width: `${reputationData.totalRatings > 0 
                            ? (reputationData.ratingDistribution[rating] / reputationData.totalRatings) * 100 
                            : 0}%`,
                          height: '100%',
                          backgroundColor: '#f59e0b'
                        }}></div>
                      </div>
                      <span style={{ fontSize: '12px', color: '#6b7280', width: '30px', textAlign: 'right' }}>
                        {reputationData.ratingDistribution[rating] || 0}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Badges */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              border: '1px solid #e5e7eb'
            }}>
              <h2 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: '600', color: '#111827' }}>
                Earned Badges
              </h2>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px' }}>
                {badges.map((badge) => {
                  const Icon = badge.icon;
                  return (
                    <div key={badge.id} style={{
                      backgroundColor: badge.earned ? '#f0fdf4' : '#f9fafb',
                      border: `2px solid ${badge.earned ? '#16a34a' : '#e5e7eb'}`,
                      borderRadius: '12px',
                      padding: '16px',
                      textAlign: 'center',
                      opacity: badge.earned ? 1 : 0.6
                    }}>
                      <div style={{
                        width: '48px',
                        height: '48px',
                        backgroundColor: badge.earned ? badge.color : '#e5e7eb',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto 12px'
                      }}>
                        <Icon size={24} style={{ color: badge.earned ? 'white' : '#9ca3af' }} />
                      </div>
                      <h3 style={{ margin: '0 0 4px 0', fontSize: '14px', fontWeight: '600', color: '#111827' }}>
                        {badge.name}
                      </h3>
                      <p style={{ margin: 0, fontSize: '12px', color: '#6b7280' }}>
                        {badge.description}
                      </p>
                      {badge.earned && (
                        <div style={{ marginTop: '8px' }}>
                          <ThumbsUp size={16} style={{ color: '#16a34a' }} />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Achievements */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              border: '1px solid #e5e7eb'
            }}>
              <h2 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: '600', color: '#111827' }}>
                Achievements Progress
              </h2>
              
              <div style={{ display: 'grid', gap: '16px' }}>
                {achievements.map((achievement) => (
                  <div key={achievement.id} style={{
                    backgroundColor: '#f8fafc',
                    borderRadius: '8px',
                    padding: '16px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '500', color: '#111827' }}>
                        {achievement.title}
                      </h3>
                      <span style={{ fontSize: '14px', fontWeight: '600', color: '#2563eb' }}>
                        {Math.round(achievement.progress)}%
                      </span>
                    </div>
                    <p style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#6b7280' }}>
                      {achievement.description}
                    </p>
                    <div style={{ 
                      height: '8px', 
                      backgroundColor: '#e5e7eb', 
                      borderRadius: '4px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${achievement.progress}%`,
                        height: '100%',
                        backgroundColor: '#2563eb',
                        transition: 'width 0.3s ease'
                      }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      <AutomobileExpertBottomNav />

      <style jsx>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default AutomobileExpertReputation;
