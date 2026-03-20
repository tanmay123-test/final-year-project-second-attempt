import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Wrench, 
  Fuel, 
  Truck, 
  Brain, 
  Bus,
  ChevronLeft,
  User
} from 'lucide-react';

const WorkerServiceSelection = () => {
  const navigate = useNavigate();
  const [selectedService, setSelectedService] = useState(null);

  const carServices = [
    {
      id: 'mechanic',
      label: 'Mechanic',
      icon: Wrench,
      description: 'Vehicle repair and maintenance services',
      loginPath: '/worker/car/mechanic/login',
      signupPath: '/worker/car/mechanic/signup',
      gradient: 'linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%)',
      glassColor: 'rgba(59, 130, 246, 0.1)',
      borderColor: 'rgba(59, 130, 246, 0.3)',
      hoverColor: 'rgba(59, 130, 246, 0.2)'
    },
    {
      id: 'fuel_delivery',
      label: 'Fuel Delivery Agent',
      icon: Fuel,
      description: 'Emergency fuel delivery services',
      loginPath: '/worker/car/fuel-delivery/login',
      signupPath: '/worker/car/fuel-delivery/signup',
      gradient: 'linear-gradient(135deg, #FB923C 0%, #EA580C 100%)',
      glassColor: 'rgba(251, 146, 60, 0.1)',
      borderColor: 'rgba(251, 146, 60, 0.3)',
      hoverColor: 'rgba(251, 146, 60, 0.2)'
    },
    {
      id: 'tow_truck',
      label: 'Tow Truck Operator',
      icon: Truck,
      description: 'Vehicle towing and recovery services',
      loginPath: '/worker/car/tow-truck/login',
      signupPath: '/worker/car/tow-truck/signup',
      gradient: 'linear-gradient(135deg, #10B981 0%, #047857 100%)',
      glassColor: 'rgba(16, 185, 129, 0.1)',
      borderColor: 'rgba(16, 185, 129, 0.3)',
      hoverColor: 'rgba(16, 185, 129, 0.2)'
    },
    {
      id: 'automobile_expert',
      label: 'Automobile Expert',
      icon: Brain,
      description: 'Expert automotive consultation and advice',
      loginPath: '/worker/car/automobile-expert/login',
      signupPath: '/worker/car/automobile-expert/signup',
      gradient: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)',
      glassColor: 'rgba(139, 92, 246, 0.1)',
      borderColor: 'rgba(139, 92, 246, 0.3)',
      hoverColor: 'rgba(139, 92, 246, 0.2)'
    },
    {
      id: 'truck_operator',
      label: 'Truck Operator',
      icon: Bus,
      description: 'Heavy vehicle and truck operations',
      loginPath: '/worker/car/truck-operator/login',
      signupPath: '/worker/car/truck-operator/signup',
      gradient: 'linear-gradient(135deg, #6B7280 0%, #374151 100%)',
      glassColor: 'rgba(107, 114, 128, 0.1)',
      borderColor: 'rgba(107, 114, 128, 0.3)',
      hoverColor: 'rgba(107, 114, 128, 0.2)'
    }
  ];

  const handleServiceClick = (service) => {
    setSelectedService(service);
  };

  const handleBack = () => {
    if (selectedService) {
      setSelectedService(null);
    } else {
      navigate('/provide-service');
    }
  };

  const handleLogin = (service) => {
    navigate(service.loginPath);
  };

  const handleSignup = (service) => {
    navigate(service.signupPath);
  };

  if (selectedService) {
    const Icon = selectedService.icon;
    return (
      <div className="worker-service-detail" style={{
        background: selectedService.gradient,
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Header */}
        <header className="service-header">
          <div className="header-top-row">
            <button 
              className="back-button"
              onClick={handleBack}
              aria-label="Go back"
              style={{
                background: selectedService.glassColor,
                border: `1px solid ${selectedService.borderColor}`,
                backdropFilter: 'blur(10px)',
                borderRadius: '50%',
                width: '40px',
                height: '40px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.background = selectedService.hoverColor;
              }}
              onMouseLeave={(e) => {
                e.target.style.background = selectedService.glassColor;
              }}
            >
              <ChevronLeft size={20} />
            </button>
          </div>
          <div className="header-content" style={{
            color: 'white',
            padding: '1.5rem',
            paddingBottom: '3rem',
            textAlign: 'center',
            position: 'relative'
          }}>
            <div className="service-icon-large" style={{
              background: selectedService.glassColor,
              border: `2px solid ${selectedService.borderColor}`,
              backdropFilter: 'blur(15px)',
              borderRadius: '50%',
              width: '100px',
              height: '100px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.5rem',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
            }}>
              <Icon size={48} strokeWidth={2} style={{ color: 'white' }} />
            </div>
            <h1 style={{
              fontSize: '2.5rem',
              fontWeight: 'bold',
              marginBottom: '1rem',
              textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)'
            }}>{selectedService.label}</h1>
            <p style={{
              fontSize: '1.2rem',
              opacity: 0.9,
              maxWidth: '600px',
              margin: '0 auto',
              lineHeight: '1.6'
            }}>{selectedService.description}</p>
          </div>
        </header>

        {/* Action Section */}
        <main className="action-container" style={{
          flex: 1,
          padding: '2rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <div className="action-card" style={{
            background: selectedService.glassColor,
            border: `1px solid ${selectedService.borderColor}`,
            backdropFilter: 'blur(20px)',
            borderRadius: '24px',
            padding: '3rem',
            maxWidth: '500px',
            width: '100%',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
            textAlign: 'center'
          }}>
            <h2 style={{
              color: 'white',
              fontSize: '1.8rem',
              fontWeight: 'bold',
              marginBottom: '1rem',
              textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)'
            }}>Get Started as {selectedService.label}</h2>
            <p style={{
              color: 'rgba(255, 255, 255, 0.9)',
              fontSize: '1.1rem',
              marginBottom: '2.5rem',
              lineHeight: '1.6'
            }}>Join our platform and start providing professional services</p>
            
            <div className="action-buttons" style={{
              display: 'flex',
              gap: '1rem',
              flexDirection: 'column',
              alignItems: 'center'
            }}>
              <button 
                className="login-button"
                onClick={() => handleLogin(selectedService)}
                style={{
                  background: 'rgba(255, 255, 255, 0.2)',
                  border: `1px solid rgba(255, 255, 255, 0.3)`,
                  backdropFilter: 'blur(10px)',
                  borderRadius: '16px',
                  padding: '1rem 2rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  color: 'white',
                  fontSize: '1.1rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  width: '100%',
                  maxWidth: '300px',
                  justifyContent: 'center'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = 'rgba(255, 255, 255, 0.3)';
                  e.target.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = 'rgba(255, 255, 255, 0.2)';
                  e.target.style.transform = 'translateY(0)';
                }}
              >
                <User size={20} />
                Login
              </button>
              
              <button 
                className="signup-button"
                onClick={() => handleSignup(selectedService)}
                style={{
                  background: 'rgba(255, 255, 255, 0.9)',
                  border: 'none',
                  backdropFilter: 'blur(10px)',
                  borderRadius: '16px',
                  padding: '1rem 2rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  color: selectedService.id === 'mechanic' ? '#1E40AF' : 
                        selectedService.id === 'fuel_delivery' ? '#EA580C' : 
                        selectedService.id === 'tow_truck' ? '#047857' : 
                        selectedService.id === 'automobile_expert' ? '#6D28D9' : '#374151',
                  fontSize: '1.1rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  width: '100%',
                  maxWidth: '300px',
                  justifyContent: 'center'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = 'white';
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.2)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = 'rgba(255, 255, 255, 0.9)';
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = 'none';
                }}
              >
                <User size={20} />
                Create Account
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  // Main service selection view
  return (
    <div className="worker-service-selection" style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Header */}
      <header className="service-header" style={{
        color: 'white',
        padding: '2rem',
        textAlign: 'center',
        position: 'relative'
      }}>
        <div className="header-top-row" style={{
          position: 'absolute',
          top: '2rem',
          left: '2rem'
        }}>
          <button 
            className="back-button"
            onClick={handleBack}
            aria-label="Go back"
            style={{
              background: 'rgba(255, 255, 255, 0.1)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              backdropFilter: 'blur(10px)',
              borderRadius: '50%',
              width: '40px',
              height: '40px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.target.style.background = 'rgba(255, 255, 255, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.target.style.background = 'rgba(255, 255, 255, 0.1)';
            }}
          >
            <ChevronLeft size={20} />
          </button>
        </div>
        <div className="header-content">
          <h1 style={{
            fontSize: '2.5rem',
            fontWeight: 'bold',
            marginBottom: '1rem',
            textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)'
          }}>Car Service Workers</h1>
          <p style={{
            fontSize: '1.2rem',
            opacity: 0.9,
            maxWidth: '600px',
            margin: '0 auto',
            lineHeight: '1.6'
          }}>Select your area of expertise</p>
        </div>
      </header>

      {/* Services Grid */}
      <main className="services-container" style={{
        flex: 1,
        padding: '2rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div className="services-grid" style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '2rem',
          maxWidth: '1200px',
          width: '100%'
        }}>
          {carServices.map((service) => {
            const Icon = service.icon;
            return (
              <button 
                key={service.id}
                className="service-card"
                onClick={() => handleServiceClick(service)}
                aria-label={`Select ${service.label}`}
                style={{
                  background: service.glassColor,
                  border: `1px solid ${service.borderColor}`,
                  backdropFilter: 'blur(20px)',
                  borderRadius: '20px',
                  padding: '2rem',
                  textAlign: 'center',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = service.hoverColor;
                  e.target.style.transform = 'translateY(-5px)';
                  e.target.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.2)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = service.glassColor;
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.1)';
                }}
              >
                <div className="service-icon-wrapper" style={{
                  background: service.gradient,
                  borderRadius: '50%',
                  width: '80px',
                  height: '80px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1.5rem',
                  boxShadow: '0 8px 25px rgba(0, 0, 0, 0.2)'
                }}>
                  <Icon size={32} strokeWidth={2} style={{ color: 'white' }} />
                </div>
                <h3 style={{
                  color: 'white',
                  fontSize: '1.4rem',
                  fontWeight: 'bold',
                  marginBottom: '1rem',
                  textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)'
                }}>{service.label}</h3>
                <p style={{
                  color: 'rgba(255, 255, 255, 0.9)',
                  fontSize: '1rem',
                  lineHeight: '1.6',
                  margin: 0
                }}>{service.description}</p>
              </button>
            );
          })}
        </div>
      </main>
    </div>
  );
};

export default WorkerServiceSelection;
