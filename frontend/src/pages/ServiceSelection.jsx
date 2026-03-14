import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stethoscope, Home, Package, Car, Wallet, ChevronLeft } from 'lucide-react';
import { commonService } from '../services/api';

const ServiceSelection = ({ mode = 'user' }) => {
  const navigate = useNavigate();
  
  const defaultServices = [
    { id: 'healthcare', label: 'Healthcare', path: '/doctors' },
    { id: 'housekeeping', label: 'Housekeeping', path: '/worker/housekeeping/login' },
    { id: 'resource', label: 'Resource Management', path: '/worker/resource/login' },
    { id: 'car', label: 'Car Services', path: '/worker/car/login' },
    { id: 'money', label: 'Money Management', path: '/worker/money/login' },
  ];

  const [services, setServices] = useState(() => {
    const cached = localStorage.getItem('services_cache');
    return cached ? JSON.parse(cached) : defaultServices;
  });

  const iconMap = {
    healthcare: Stethoscope,
    housekeeping: Home,
    resource: Package,
    car: Car,
    money: Wallet
  };

  useEffect(() => {
    const fetchServices = async () => {
      try {
        console.log('[ServiceSelection] Fetching services from API...');
        const response = await commonService.getServices();
        console.log('[ServiceSelection] API Response received:', response.data);
        
        if (response.data && response.data.services) {
          setServices(response.data.services);
          localStorage.setItem('services_cache', JSON.stringify(response.data.services));
        }
      } catch (error) {
        console.error('[ServiceSelection] Failed to fetch services:', error);
      }
    };

    fetchServices();
  }, []);

  return (
    <div className="service-selection-page">
      {/* Header Section */}
      <header className="service-header">
        <div className="header-top-row">
          <button 
            className="back-button" 
            onClick={() => navigate(-1)}
            aria-label="Go back"
          >
            <ChevronLeft size={24} color="white" />
          </button>
        </div>
        <div className="header-content">
          <h1>Select Your Service</h1>
          <p>Choose the service you want to provide</p>
        </div>
      </header>

      {/* Services Grid */}
      <main className="services-grid-container">
        <div className="services-grid">
          {services.map((service) => {
            const Icon = iconMap[service.id] || Package;
            return (
              <button 
                key={service.id} 
                className="service-card" 
                onClick={() => {
                  if (service.path === '#') return;
                  
                  if (mode === 'worker' && service.id === 'healthcare') {
                    navigate('/worker/healthcare/login');
                  } else {
                    navigate(service.path);
                  }
                }}
                aria-label={`Select ${service.label} service`}
              >
                <div className="service-icon-wrapper">
                  <Icon size={32} strokeWidth={2} aria-hidden="true" />
                </div>
                <span className="service-label">{service.label}</span>
              </button>
            );
          })}
        </div>
      </main>

      <style>{`
        .service-selection-page {
          min-height: 100%;
          background-color: #FAFAFA;
          display: flex;
          flex-direction: column;
          /* overflow-x hidden removed to prevent sticky scroll issues */
        }

        .service-header {
          background: var(--medical-gradient);
          color: white;
          padding: 1.5rem 1.5rem 3rem;
          border-bottom-left-radius: 30px;
          border-bottom-right-radius: 30px;
          box-shadow: 0 4px 10px rgba(52, 152, 219, 0.2);
          width: 100%;
          display: flex;
          flex-direction: column;
        }

        .header-top-row {
          display: flex;
          align-items: center;
          margin-bottom: 0.5rem;
          height: 44px; /* Align with back button height */
        }

        .back-button {
          background: rgba(255, 255, 255, 0.2);
          border: none;
          border-radius: 50%;
          width: 44px; 
          height: 44px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: background 0.2s;
          /* Removed absolute positioning */
        }

        .back-button:hover {
          background: rgba(255, 255, 255, 0.3);
        }

        .back-button:focus-visible {
          outline: 2px solid white;
          outline-offset: 2px;
        }

        .header-content {
          text-align: center;
          padding: 0 1rem;
          animation: fadeIn 0.5s ease-out;
        }

        .header-content h1 {
          font-size: 1.75rem;
          font-weight: 700;
          margin-bottom: 0.5rem;
          line-height: 1.2;
        }

        .header-content p {
          font-size: 1rem;
          opacity: 0.95; /* Increased contrast slightly */
          margin: 0;
        }

        .services-grid-container {
          flex: 1;
          padding: 1.5rem;
          display: flex;
          justify-content: center;
          width: 100%;
          box-sizing: border-box;
          max-width: 1200px;
          margin: 0 auto;
        }

        .services-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr); /* Default to 2 columns for mobile */
          gap: 1rem;
          width: 100%;
        }

        .service-card {
          background: white;
          border: none;
          border-radius: 20px;
          padding: 1.25rem 0.75rem;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
          cursor: pointer;
          transition: transform 0.2s, box-shadow 0.2s;
          aspect-ratio: 1/1.1; /* Slightly taller than square */
          text-align: center;
          width: 100%;
          height: 100%;
          min-height: 140px;
          color: inherit;
          font-family: inherit;
        }

        .service-card:hover, .service-card:focus-visible {
          transform: translateY(-5px);
          box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
          outline: none;
        }

        .service-card:focus-visible {
           outline: 2px solid var(--accent-blue);
           outline-offset: 2px;
        }

        .service-icon-wrapper {
          width: 56px;
          height: 56px;
          background: var(--medical-gradient);
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 0.75rem;
          color: white;
          flex-shrink: 0;
          box-shadow: 0 4px 10px rgba(52, 152, 219, 0.3);
        }

        .service-label {
          font-weight: 600;
          color: var(--text-primary);
          font-size: 0.95rem;
          line-height: 1.3;
          word-break: break-word; 
          max-width: 100%;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        /* Tablet (iPad Mini, Air) */
        @media (min-width: 600px) {
           .services-grid {
             grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
             gap: 1.5rem;
           }
           
           .service-card {
             padding: 2rem 1rem;
             min-height: 180px;
           }
           
           .service-icon-wrapper {
             width: 64px;
             height: 64px;
             margin-bottom: 1rem;
           }
           
           .service-label {
             font-size: 1.1rem;
           }

           .header-content h1 {
             font-size: 2.25rem;
           }
        }

        /* Desktop */
        @media (min-width: 1024px) {
           .services-grid {
             grid-template-columns: repeat(4, 1fr); /* 4 columns on desktop */
             gap: 2rem;
             max-width: 1000px;
           }

           .service-header {
             padding-bottom: 4rem;
             border-bottom-left-radius: 50px;
             border-bottom-right-radius: 50px;
           }
        }
      `}</style>
    </div>
  );
};

export default ServiceSelection;
