import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { housekeepingService } from '../../../shared/api';
import ProviderBottomNav from '../../../components/ProviderBottomNav';

const DEFAULT_SIZES = ['Studio', '1 BHK', '2 BHK', '3 BHK', 'Villa'];

const ProviderPricing = () => {
  const navigate = useNavigate();
  const { worker } = useAuth();
  const [services, setServices] = useState([]);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [errors, setErrors] = useState({});

  useEffect(() => {
    const load = async () => {
      try {
        const [allRes, myRes] = await Promise.all([
          housekeepingService.getServices(),
          housekeepingService.getWorkerServices()
        ]);
        const all = (allRes.data.services || []).map(s => ({
          id: s.id,
          name: s.name,
          description: s.description,
          active: false,
          price: s.price,
          pricing: {
            sizes: Object.fromEntries(DEFAULT_SIZES.map(sz => [sz, { enabled: false, price: '' }])),
            custom: { enabled: false, per_sqft: '', sample_area: 0 }
          }
        }));
        const mine = (myRes.data.services || []);
        const map = new Map(all.map(s => [s.id, s]));
        mine.forEach(ms => {
          const row = map.get(ms.id) || { id: ms.id, name: ms.name, description: ms.description };
          let pricing = { sizes: {}, custom: { enabled: false, per_sqft: '', sample_area: 0 } };
          try {
            if (ms.pricing_json) pricing = JSON.parse(ms.pricing_json);
          } catch {}
          map.set(ms.id, {
            ...row,
            active: true,
            price: ms.price,
            pricing: {
              sizes: { ...Object.fromEntries(DEFAULT_SIZES.map(sz => [sz, { enabled: false, price: '' }])), ...(pricing.sizes || {}) },
              custom: { enabled: false, per_sqft: '', sample_area: 0, ...(pricing.custom || {}) }
            }
          });
        });
        setServices(Array.from(map.values()));
      } catch (e) {
        setServices([]);
      }
    };
    load();
  }, [worker]);

  const setSizeEnabled = (sid, size, enabled) => {
    setServices(prev => prev.map(s => s.id === sid ? { ...s, pricing: { ...s.pricing, sizes: { ...s.pricing.sizes, [size]: { ...s.pricing.sizes[size], enabled } } } } : s));
  };
  const setSizePrice = (sid, size, price) => {
    const clean = price.replace(/[^0-9.]/g, '');
    setServices(prev => prev.map(s => s.id === sid ? { ...s, pricing: { ...s.pricing, sizes: { ...s.pricing.sizes, [size]: { ...s.pricing.sizes[size], price: clean } } } } : s));
  };
  const setCustomEnabled = (sid, enabled) => {
    setServices(prev => prev.map(s => s.id === sid ? { ...s, pricing: { ...s.pricing, custom: { ...s.pricing.custom, enabled } } } : s));
  };
  const setPerSqft = (sid, val) => {
    const clean = val.replace(/[^0-9.]/g, '');
    setServices(prev => prev.map(s => s.id === sid ? { ...s, pricing: { ...s.pricing, custom: { ...s.pricing.custom, per_sqft: clean } } } : s));
  };
  const setSampleArea = (sid, val) => {
    const clean = val.replace(/[^0-9.]/g, '');
    setServices(prev => prev.map(s => s.id === sid ? { ...s, pricing: { ...s.pricing, custom: { ...s.pricing.custom, sample_area: clean } } } : s));
  };
  const toggleActive = (sid) => {
    setServices(prev => prev.map(s => s.id === sid ? { ...s, active: !s.active } : s));
  };

  const validate = () => {
    const errs = {};
    services.forEach(s => {
      if (!s.active) return;
      const enabledSizes = Object.entries(s.pricing.sizes).filter(([k, v]) => v.enabled);
      const hasCustom = s.pricing.custom.enabled;
      if (enabledSizes.length === 0 && !hasCustom) {
        errs[s.id] = 'Enable at least one size or custom pricing';
        return;
      }
      enabledSizes.forEach(([size, cfg]) => {
        const p = parseFloat(cfg.price);
        if (!(p > 0)) {
          errs[`${s.id}-${size}`] = 'Price must be positive';
        }
      });
      if (hasCustom) {
        const rate = parseFloat(s.pricing.custom.per_sqft);
        if (!(rate > 0)) errs[`${s.id}-custom-rate`] = 'Per sqft must be positive';
        const area = parseFloat(s.pricing.custom.sample_area || 0);
        if (isNaN(area) || area < 0) errs[`${s.id}-custom-area`] = 'Area must be logical';
      }
    });
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const save = async () => {
    if (!validate()) {
      setMessage('Please fix errors before saving');
      return;
    }
    setSaving(true);
    setMessage('');
    try {
      const payload = services
        .filter(s => s.active)
        .map(s => {
          // choose default price as first enabled size or custom sample calc, else 0
          let defaultPrice = 0;
          for (const size of DEFAULT_SIZES) {
            if (s.pricing.sizes[size]?.enabled) {
              const p = parseFloat(s.pricing.sizes[size].price || 0);
              if (p > 0) { defaultPrice = p; break; }
            }
          }
          if (defaultPrice === 0 && s.pricing.custom.enabled) {
            const rate = parseFloat(s.pricing.custom.per_sqft || 0);
            const area = parseFloat(s.pricing.custom.sample_area || 0);
            if (rate > 0 && area > 0) defaultPrice = rate * area;
          }
          return {
            service_id: s.id,
            active: 1,
            price: defaultPrice || 0,
            pricing_json: JSON.stringify(s.pricing)
          };
        });
      await housekeepingService.saveWorkerServices(payload);
      setMessage('Pricing saved successfully');
    } catch (e) {
      setMessage('Failed to save pricing');
    } finally {
      setSaving(false);
    }
  };

  const previewCustomTotal = (s) => {
    const rate = parseFloat(s.pricing.custom.per_sqft || 0);
    const area = parseFloat(s.pricing.custom.sample_area || 0);
    if (!(rate > 0 && area > 0)) return '—';
    return `₹${(rate * area).toFixed(2)}`;
  };

  return (
    <div className="pp-root" style={{ background: '#F5F7FA', minHeight: '100vh', paddingBottom: '80px' }}>
      <style>{`
        .pp-header { background: linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%); padding: 20px; color: #fff; border-bottom-left-radius: 24px; border-bottom-right-radius: 24px; }
        .pp-wrapper { max-width: 1024px; margin: 0 auto; padding: 20px; display: grid; gap: 16px; }
        .pp-card { background: #fff; border: 1px solid #E5E7EB; border-radius: 12px; padding: 16px; }
        .pp-card-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 12px; }
        .pp-status { font-size: 12px; }
        .pp-size-grid { display: grid; grid-template-columns: 1fr 120px 80px; gap: 8px; align-items: center; margin-bottom: 12px; }
        .pp-input { width: 100%; padding: 8px 10px; border: 1px solid #E5E7EB; border-radius: 8px; }
        .pp-custom { border-top: 1px solid #E5E7EB; padding-top: 12px; }
        .pp-custom-grid { display: grid; grid-template-columns: 200px 200px 1fr; gap: 12px; align-items: center; }
        .pp-save { position: sticky; bottom: 80px; left: 0; right: 0; display: flex; justify-content: center; padding: 12px; }
        .pp-save button { padding: 12px 20px; background: #8E44AD; color: #fff; border: 0; border-radius: 8px; font-weight: 700; min-width: 180px; }
        .pp-toast { position: fixed; bottom: 120px; left: 50%; transform: translateX(-50%); background: #fff; border: 1px solid #E5E7EB; border-radius: 8px; padding: 10px 14px; color: #1F2937; }
        @media (max-width: 480px) {
          .pp-wrapper { padding: 12px; }
          .pp-size-grid { grid-template-columns: 1fr; }
          .pp-custom-grid { grid-template-columns: 1fr; }
          .pp-status { justify-self: start; }
          .pp-save { bottom: 72px; padding: 8px; }
          .pp-save button { width: 100%; min-width: 0; }
        }
        @media (min-width: 481px) and (max-width: 1024px) {
          .pp-wrapper { max-width: 760px; }
          .pp-size-grid { grid-template-columns: 1fr 120px; }
          .pp-status { justify-self: end; }
          .pp-custom-grid { grid-template-columns: 1fr 1fr; }
        }
        @media (min-width: 1280px) {
          .pp-wrapper { max-width: 1100px; }
          .pp-save button { min-width: 220px; }
        }
      `}</style>

      <div className="pp-header">
        <button onClick={() => navigate(-1)} style={{ background: 'rgba(255,255,255,0.15)', color: 'white', border: 'none', padding: '8px 12px', borderRadius: 8, cursor: 'pointer' }}>&larr; Back</button>
        <h2 style={{ margin: '8px 0 0 0' }}>Service Pricing</h2>
        <p style={{ opacity: 0.9, margin: 0 }}>Configure per-size rates and custom area pricing</p>
      </div>

      <div className="pp-wrapper">
        {services.map(s => (
          <div key={s.id} className="pp-card">
            <div className="pp-card-head">
              <div>
                <h3 style={{ margin: 0 }}>{s.name}</h3>
                <small style={{ color: '#6B7280' }}>{s.description}</small>
              </div>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span className="pp-status" style={{ color: s.active ? '#059669' : '#6B7280' }}>{s.active ? 'Enabled' : 'Disabled'}</span>
                <input type="checkbox" checked={s.active} onChange={() => toggleActive(s.id)} />
              </label>
            </div>

            {s.active && (
              <>
                <div className="pp-size-grid">
                  {DEFAULT_SIZES.map(size => (
                    <React.Fragment key={size}>
                      <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <input type="checkbox" checked={!!s.pricing.sizes[size]?.enabled} onChange={(e) => setSizeEnabled(s.id, size, e.target.checked)} />
                        <span>{size}</span>
                      </label>
                      <input
                        type="text"
                        value={s.pricing.sizes[size]?.price || ''}
                        onChange={(e) => setSizePrice(s.id, size, e.target.value)}
                        placeholder="Price"
                        className="pp-input"
                      />
                      <span className="pp-status" style={{ color: s.pricing.sizes[size]?.enabled ? '#059669' : '#6B7280' }}>
                        {s.pricing.sizes[size]?.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                      {errors[`${s.id}-${size}`] && <div style={{ gridColumn: '1 / -1', color: '#DC2626', fontSize: 12 }}>{errors[`${s.id}-${size}`]}</div>}
                    </React.Fragment>
                  ))}
                </div>

                <div className="pp-custom">
                  <label style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <input type="checkbox" checked={s.pricing.custom.enabled} onChange={(e) => setCustomEnabled(s.id, e.target.checked)} />
                    <strong>Custom Area Pricing</strong>
                  </label>
                  <div className="pp-custom-grid">
                    <div>
                      <label style={{ display: 'block', fontSize: 12, color: '#6B7280' }}>Per Sqft</label>
                      <input type="text" value={s.pricing.custom.per_sqft} onChange={(e) => setPerSqft(s.id, e.target.value)} placeholder="e.g. 2.5" className="pp-input" />
                      {errors[`${s.id}-custom-rate`] && <div style={{ color: '#DC2626', fontSize: 12 }}>{errors[`${s.id}-custom-rate`]}</div>}
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: 12, color: '#6B7280' }}>Sample Area (sqft)</label>
                      <input type="text" value={s.pricing.custom.sample_area} onChange={(e) => setSampleArea(s.id, e.target.value)} placeholder="e.g. 800" className="pp-input" />
                      {errors[`${s.id}-custom-area`] && <div style={{ color: '#DC2626', fontSize: 12 }}>{errors[`${s.id}-custom-area`]}</div>}
                    </div>
                    <div style={{ alignSelf: 'end', color: '#1F2937' }}>
                      Preview: <strong>{previewCustomTotal(s)}</strong>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        ))}
      </div>

      <div className="pp-save">
        <button onClick={save} disabled={saving}>
          {saving ? 'Saving...' : 'Save Pricing'}
        </button>
      </div>
      
      {!!message && (
        <div className="pp-toast">
          {message}
        </div>
      )}

      <ProviderBottomNav />
    </div>
  );
};

export default ProviderPricing;
