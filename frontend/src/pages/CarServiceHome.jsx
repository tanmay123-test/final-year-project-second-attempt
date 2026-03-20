import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Car, Wrench, Bot, Home, Calendar, User, Brain, LogOut, ArrowLeft } from 'lucide-react';

const CarServiceHome = () => {
  const navigate = useNavigate();

  const menuItems = [
    {
      id: 'home',
      title: 'Home',
      description: 'Dashboard and overview',
      icon: Home,
      color: '#4CAF50'
    },
    {
      id: 'book-mechanic',
      title: 'Book Mechanic',
      description: 'Find and book local mechanics',
      icon: Wrench,
      color: '#FF9800'
    },
    {
      id: 'ai-mechanic',
      title: 'AI Mechanic',
      description: 'Get AI-powered car diagnostics',
      icon: Bot,
      color: '#2196F3'
    },
    {
      id: 'garage',
      title: 'My Garage',
      description: 'Manage your vehicles',
      icon: Car,
      color: '#9C27B0'
    },
    {
      id: 'bookings',
      title: 'My Bookings',
      description: 'View appointment history',
      icon: Calendar,
      color: '#F44336'
    },
    {
      id: 'profile',
      title: 'Profile',
      description: 'Account and car details',
      icon: User,
      color: '#607D8B'
    },
    {
      id: 'ask-expert',
      title: 'Ask Expert',
      description: 'Consult with automobile experts',
      icon: Brain,
      color: '#795548'
    }
  ];

  const handleMenuClick = (itemId) => {
    switch (itemId) {
      case 'home':
        // Stay on current page
        break;
      case 'book-mechanic':
        navigate('/car-service/book-mechanic');
        break;
      case 'ai-mechanic':
        navigate('/car-service/ai-mechanic');
        break;
      case 'garage':
        navigate('/car-service/garage');
        break;
      case 'bookings':
        navigate('/car-service/bookings');
        break;
      case 'profile':
        navigate('/car-service/profile');
        break;
      case 'ask-expert':
        navigate('/car-service/ask-expert');
        break;
      default:
        break;
    }
  };

  const handleBack = () => {
    navigate('/services');
  };

  const handleLogout = () => {
    // Clear auth and redirect to login
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <div className="car-service-home-container">
      {/* Header */}
      <div className="home-header">
        <button className="back-btn" onClick={handleBack}>
          <ArrowLeft size={20} />
          Back to Services
        </button>
        <button className="logout-btn" onClick={handleLogout}>
          <LogOut size={20} />
          Logout
        </button>
      </div>

      {/* Welcome Section */}
      <div className="welcome-section">
        <div className="welcome-icon">
          <Car size={50} strokeWidth={2} />
        </div>
        <h1>Car Service Center</h1>
        <p>Your complete car care solution</p>
      </div>

      {/* Menu Grid */}
      <div className="menu-grid">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              className="menu-item"
              onClick={() => handleMenuClick(item.id)}
              style={{ '--accent-color': item.color }}
            >
              <div className="menu-icon">
                <Icon size={28} strokeWidth={2} />
              </div>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </button>
          );
        })}
      </div>

      <style>{`
        .car-service-home-container {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          padding: 1rem;
        }

        .home-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
          padding: 0 0.5rem;
        }

        .back-btn,
        .logout-btn {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: rgba(255, 255, 255, 0.2);
          border: none;
          border-radius: 10px;
          padding: 0.75rem 1rem;
          color: white;
          font-size: 0.9rem;
          cursor: pointer;
          transition: background 0.3s;
          backdrop-filter: blur(10px);
        }

        .back-btn:hover,
        .logout-btn:hover {
          background: rgba(255, 255, 255, 0.3);
        }

        .welcome-section {
          text-align: center;
          color: white;
          margin-bottom: 3rem;
          padding: 0 1rem;
        }

        .welcome-icon {
          background: rgba(255, 255, 255, 0.2);
          border-radius: 50%;
          width: 100px;
          height: 100px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 1.5rem;
          backdrop-filter: blur(10px);
        }

        .welcome-section h1 {
          font-size: 2.5rem;
          font-weight: 700;
          margin-bottom: 0.5rem;
        }

        .welcome-section p {
          font-size: 1.1rem;
          opacity: 0.9;
          margin: 0;
        }

        .menu-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1.5rem;
          max-width: 1200px;
          margin: 0 auto;
        }

        .menu-item {
          background: white;
          border: none;
          border-radius: 20px;
          padding: 2rem 1.5rem;
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
          cursor: pointer;
          transition: transform 0.3s, box-shadow 0.3s;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }

        .menu-item:hover {
          transform: translateY(-5px);
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }

        .menu-icon {
          background: var(--accent-color);
          color: white;
          border-radius: 15px;
          width: 60px;
          height: 60px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 1rem;
        }

        .menu-item h3 {
          color: #333;
          font-size: 1.25rem;
          font-weight: 600;
          margin-bottom: 0.5rem;
        }

        .menu-item p {
          color: #666;
          font-size: 0.9rem;
          margin: 0;
          line-height: 1.4;
        }

        @media (max-width: 768px) {
          .menu-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
          }
          
          .welcome-section h1 {
            font-size: 2rem;
          }
          
          .home-header {
            flex-direction: column;
            gap: 1rem;
          }
          
          .back-btn,
          .logout-btn {
            width: 100%;
            justify-content: center;
          }
        }

        @media (min-width: 769px) and (max-width: 1024px) {
          .menu-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }
      `}</style>
    </div>
  );
};

export default CarServiceHome;
