import React, { useState, useEffect } from 'react';
import {
  Fuel,
  Star,
  CheckCircle,
  Clock,
  TrendingUp,
  Shield,
  Trophy,
  Zap,
  Target,
} from 'lucide-react';

const API_BASE = 'http://localhost:5000/api/fuel-delivery';

const FuelDeliveryPerformance = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const workerId = localStorage.getItem('workerId');
      if (!workerId) {
        setLoading(false);
        return;
      }
      const res = await fetch(`${API_BASE}/performance/${workerId}`);
      if (!res.ok) {
        setData(null);
        setLoading(false);
        return;
      }
      const json = await res.json();
      if (json.success && json.performance) {
        setData(json.performance);
      } else {
        setData(null);
      }
    } catch (err) {
      console.error('Performance fetch error:', err);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const rating = data?.rating ?? 0;
  const reviewCount = data?.review_count ?? 0;
  const completionRate = data?.completion_rate ?? 0;
  const avgDeliveryTime = data?.avg_delivery_time_minutes ?? 28;
  const onTimeRate = data?.on_time_rate ?? 94;
  const safetyScore = data?.safety_score ?? 98;
  const achievements = Array.isArray(data?.achievements) ? data.achievements : [];
  const reviews = Array.isArray(data?.reviews) ? data.reviews : [];

  const renderStars = (value, size = 20) => {
    const v = Math.min(5, Math.max(0, Number(value)));
    const full = Math.floor(v);
    const half = v - full >= 0.5;
    const stars = [];
    for (let i = 0; i < full; i++) stars.push(<Star key={i} size={size} className="fill-white stroke-white" />);
    if (half) stars.push(<Star key="h" size={size} className="fill-white stroke-white opacity-80" />);
    for (let i = stars.length; i < 5; i++) stars.push(<Star key={i} size={size} className="stroke-white fill-none" />);
    return stars;
  };

  const getAchievementIcon = (icon) => {
    switch (icon) {
      case 'trophy': return Trophy;
      case 'zap': return Zap;
      case 'target': return Target;
      case 'shield': return Shield;
      default: return Trophy;
    }
  };

  const formatReviewDate = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  if (loading) {
    return (
      <div className="perf-screen perf-loading">
        <div className="perf-spinner" />
        <p className="perf-loading-text">Loading performance...</p>
      </div>
    );
  }

  return (
    <div className="perf-screen">
      <style>{`
        .perf-screen { min-height: 100vh; background: #f8f9fa; padding-bottom: 24px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .perf-loading { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 48px; }
        .perf-spinner { width: 40px; height: 40px; border: 3px solid #f0f0f0; border-top-color: #f97316; border-radius: 50%; animation: perfSpin 0.8s linear infinite; }
        .perf-loading-text { margin-top: 16px; color: #6b7280; font-size: 14px; }
        @keyframes perfSpin { to { transform: rotate(360deg); } }

        .perf-header { background: #fff; padding: 16px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
        .perf-header-inner { display: flex; align-items: center; gap: 12px; }
        .perf-logo { display: flex; align-items: center; gap: 8px; color: #374151; font-weight: 700; font-size: 18px; }
        .perf-logo svg { color: #f97316; }
        .perf-title { font-size: 22px; font-weight: 700; color: #111827; margin: 6px 0 0 0; }

        .perf-rating-card { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); border-radius: 16px; padding: 24px; margin: 20px 20px 0; text-align: center; color: #fff; }
        .perf-rating-stars { display: flex; justify-content: center; gap: 4px; margin-bottom: 8px; }
        .perf-rating-value { font-size: 36px; font-weight: 800; letter-spacing: -0.02em; }
        .perf-rating-reviews { font-size: 14px; opacity: 0.95; margin-top: 4px; }

        .perf-metrics { padding: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .perf-metric-card { background: #fff; border-radius: 12px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
        .perf-metric-icon { color: #f97316; margin-bottom: 8px; }
        .perf-metric-value { font-size: 22px; font-weight: 800; color: #111827; }
        .perf-metric-label { font-size: 12px; color: #6b7280; margin-top: 4px; }
        .perf-metric-bar { height: 6px; background: #e5e7eb; border-radius: 3px; margin-top: 12px; overflow: hidden; }
        .perf-metric-fill { height: 100%; background: #f97316; border-radius: 3px; transition: width 0.3s ease; }

        .perf-section-title { font-size: 18px; font-weight: 700; color: #111827; margin: 24px 20px 12px; }
        .perf-achievements { padding: 0 20px 8px; display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .perf-achievement-card { background: #fff; border-radius: 12px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
        .perf-achievement-card.highlight { background: #fff7ed; border: 1px solid #ffedd5; }
        .perf-achievement-icon { color: #f97316; margin-bottom: 8px; }
        .perf-achievement-card:not(.highlight) .perf-achievement-icon { color: #9ca3af; }
        .perf-achievement-title { font-size: 15px; font-weight: 700; color: #111827; }
        .perf-achievement-sub { font-size: 12px; color: #6b7280; margin-top: 4px; }

        .perf-reviews { padding: 0 20px 24px; }
        .perf-review-item { background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
        .perf-review-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .perf-review-stars { display: flex; gap: 2px; }
        .perf-review-stars svg { color: #f97316; fill: #f97316; }
        .perf-review-date { font-size: 13px; color: #6b7280; }
        .perf-review-text { font-size: 15px; font-weight: 600; color: #111827; margin-bottom: 4px; }
        .perf-review-source { font-size: 13px; color: #6b7280; }
        .perf-empty { text-align: center; padding: 32px 20px; color: #6b7280; font-size: 15px; }
      `}</style>

      <header className="perf-header">
        <div className="perf-header-inner">
          <div className="perf-logo">
            <Fuel size={24} />
            <span>FuelFleet</span>
          </div>
        </div>
        <h1 className="perf-title">Performance & Safety</h1>
      </header>

      <div className="perf-rating-card">
        <div className="perf-rating-stars">
          {renderStars(rating)}
        </div>
        <div className="perf-rating-value">{rating.toFixed(2)}</div>
        <div className="perf-rating-reviews">{reviewCount} reviews</div>
      </div>

      <div className="perf-metrics">
        <div className="perf-metric-card">
          <div className="perf-metric-icon"><CheckCircle size={22} /></div>
          <div className="perf-metric-value">{completionRate.toFixed(1)}%</div>
          <div className="perf-metric-label">Completion Rate</div>
          <div className="perf-metric-bar">
            <div className="perf-metric-fill" style={{ width: `${Math.min(100, completionRate)}%` }} />
          </div>
        </div>
        <div className="perf-metric-card">
          <div className="perf-metric-icon"><Clock size={22} /></div>
          <div className="perf-metric-value">{avgDeliveryTime} min</div>
          <div className="perf-metric-label">Avg Delivery Time</div>
          <div className="perf-metric-bar">
            <div className="perf-metric-fill" style={{ width: `${Math.min(100, 100 - (avgDeliveryTime / 60) * 100)}%` }} />
          </div>
        </div>
        <div className="perf-metric-card">
          <div className="perf-metric-icon"><TrendingUp size={22} /></div>
          <div className="perf-metric-value">{onTimeRate.toFixed(1)}%</div>
          <div className="perf-metric-label">On-Time Rate</div>
          <div className="perf-metric-bar">
            <div className="perf-metric-fill" style={{ width: `${Math.min(100, onTimeRate)}%` }} />
          </div>
        </div>
        <div className="perf-metric-card">
          <div className="perf-metric-icon"><Shield size={22} /></div>
          <div className="perf-metric-value">{safetyScore.toFixed(0)}%</div>
          <div className="perf-metric-label">Safety Score</div>
          <div className="perf-metric-bar">
            <div className="perf-metric-fill" style={{ width: `${Math.min(100, safetyScore)}%` }} />
          </div>
        </div>
      </div>

      <h2 className="perf-section-title">Achievements</h2>
      <div className="perf-achievements">
        {(achievements.length >= 4 ? achievements.slice(0, 4) : [
          { id: 'top_performer', title: 'Top Performer', subtitle: 'Top 5% this month', icon: 'trophy', highlight: false },
          { id: 'speed_demon', title: 'Speed Demon', subtitle: '100 deliveries under 20 min', icon: 'zap', highlight: false },
          { id: 'perfect_score', title: 'Perfect Score', subtitle: '30-day 100% completion', icon: 'target', highlight: false },
          { id: 'safety_first', title: 'Safety First', subtitle: '1 year zero incidents', icon: 'shield', highlight: false },
        ]).map((a) => {
          const Icon = getAchievementIcon(a.icon);
          return (
            <div key={a.id} className={`perf-achievement-card ${a.highlight ? 'highlight' : ''}`}>
              <div className="perf-achievement-icon"><Icon size={22} /></div>
              <div className="perf-achievement-title">{a.title}</div>
              <div className="perf-achievement-sub">{a.subtitle}</div>
            </div>
          );
        })}
      </div>

      <h2 className="perf-section-title">Recent Reviews</h2>
      <div className="perf-reviews">
        {reviews.length === 0 ? (
          <div className="perf-empty">No customer reviews yet. Complete deliveries to receive reviews.</div>
        ) : (
          reviews.map((rev) => (
            <div key={rev.review_id || rev.created_at + rev.review_text} className="perf-review-item">
              <div className="perf-review-top">
                <div className="perf-review-stars">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <Star key={i} size={18} className={i <= (rev.rating || 0) ? 'fill-current' : ''} style={{ color: i <= (rev.rating || 0) ? '#f97316' : '#d1d5db' }} />
                  ))}
                </div>
                <span className="perf-review-date">{formatReviewDate(rev.created_at)}</span>
              </div>
              {rev.review_text && <div className="perf-review-text">{rev.review_text}</div>}
              {rev.source && <div className="perf-review-source">{rev.source}</div>}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default FuelDeliveryPerformance;
