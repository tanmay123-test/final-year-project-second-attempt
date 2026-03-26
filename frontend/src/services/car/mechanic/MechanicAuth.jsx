import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { styled, keyframes } from '../../../stitches.config';
import api from '../../../shared/api';
import { Mail, Lock, User, Phone, Briefcase, MapPin, Award } from 'lucide-react';

const fadeIn = keyframes({
  from: { opacity: 0, transform: 'translateY(10px)' },
  to: { opacity: 1, transform: 'translateY(0)' },
});

const Container = styled('div', {
  minHeight: '100vh',
  width: '100vw',
  background: '$blueGradient',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '$6',
});

const AuthCard = styled('div', {
  background: '$glassBg',
  backdropFilter: 'blur(12px)',
  borderRadius: '$2xl',
  padding: '40px',
  width: '100%',
  maxWidth: '420px',
  boxShadow: '$lg',
  animation: `${fadeIn} 0.5s ease-out`,
});

const Title = styled('h1', {
  fontSize: '28px',
  fontWeight: 'bold',
  color: 'white',
  textAlign: 'center',
  marginBottom: '$2',
  fontFamily: '$heading',
});

const Subtitle = styled('p', {
  fontSize: '16px',
  color: 'rgba(255, 255, 255, 0.8)',
  textAlign: 'center',
  marginBottom: '$8',
});

const TabContainer = styled('div', {
  display: 'flex',
  background: 'rgba(255, 255, 255, 0.2)',
  borderRadius: '$full',
  padding: '4px',
  marginBottom: '$8',
});

const Tab = styled('button', {
  flex: 1,
  padding: '10px',
  borderRadius: '$full',
  border: 'none',
  cursor: 'pointer',
  fontSize: '14px',
  fontWeight: 600,
  transition: 'all 0.2s',
  variants: {
    active: {
      true: {
        background: 'white',
        color: '$primary',
        boxShadow: '$sm',
      },
      false: {
        background: 'transparent',
        color: 'white',
        '&:hover': {
          background: 'rgba(255, 255, 255, 0.1)',
        },
      },
    },
  },
});

const Form = styled('form', {
  display: 'flex',
  flexDirection: 'column',
  gap: '$4',
});

const InputGroup = styled('div', {
  position: 'relative',
  display: 'flex',
  alignItems: 'center',
});

const IconWrapper = styled('div', {
  position: 'absolute',
  left: '16px',
  color: '$textMuted',
  display: 'flex',
  alignItems: 'center',
});

const Input = styled('input', {
  width: '100%',
  padding: '12px 16px 12px 48px',
  borderRadius: '$lg',
  border: '1px solid rgba(0, 0, 0, 0.1)',
  background: 'white',
  fontSize: '14px',
  transition: 'all 0.2s',
  '&:focus': {
    outline: 'none',
    borderColor: '$primary',
    boxShadow: '0 0 0 3px rgba(124, 58, 237, 0.1)',
  },
});

const Button = styled('button', {
  marginTop: '$4',
  padding: '14px',
  borderRadius: '$lg',
  border: 'none',
  background: '$primary',
  color: 'white',
  fontSize: '16px',
  fontWeight: 'bold',
  cursor: 'pointer',
  transition: 'all 0.2s',
  '&:hover': {
    background: '$primaryDark',
    transform: 'translateY(-1px)',
  },
  '&:active': {
    transform: 'translateY(0)',
  },
  '&:disabled': {
    opacity: 0.7,
    cursor: 'not-allowed',
  },
});

const ErrorText = styled('p', {
  color: '$error',
  fontSize: '13px',
  textAlign: 'center',
  marginTop: '$4',
  fontWeight: 500,
});

const MechanicAuth = () => {
  const [activeTab, setActiveTab] = useState('login');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    phone: '',
    experience_years: '',
    specialization: '',
    service_radius: '',
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Clear any existing tokens to avoid request interceptor interference
    localStorage.removeItem('token');
    localStorage.removeItem('workerToken');

    try {
      const endpoint = activeTab === 'login' 
        ? '/api/auth/car/mechanic/login' 
        : '/api/auth/car/mechanic/signup';
      
      const payload = activeTab === 'login'
        ? { email: formData.email, password: formData.password }
        : {
            full_name: formData.name,
            email: formData.email,
            password: formData.password,
            phone: formData.phone,
            experience: formData.experience_years,
            skills: formData.specialization,
            age: 25,
            city: 'Mumbai',
            address: 'Service Radius: ' + formData.service_radius + 'km'
          };

      console.log(`Attempting ${activeTab} at ${endpoint}...`);
      const response = await api.post(endpoint, payload);
      const data = response.data;

      if (activeTab === 'login') {
        if (!data.token) {
          throw new Error('No token received from server');
        }
        localStorage.setItem('workerToken', data.token);
        localStorage.setItem('workerId', String(data.mechanic?.id || data.mechanic_id));
        localStorage.setItem('workerData', JSON.stringify(data.mechanic));
        navigate('/worker/car/mechanic/dashboard');
      } else {
        setError(data.message || 'Account created! Please wait for approval.');
        setActiveTab('login');
      }
    } catch (err) {
      console.error('Auth error detail:', err);
      const errorMessage = err.response?.data?.error || err.message || 'Authentication failed. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <Title>Get Started as Mechanic</Title>
      <Subtitle>Join our platform and start providing professional services</Subtitle>
      
      <AuthCard>
        <TabContainer>
          <Tab 
            active={activeTab === 'login'} 
            onClick={() => setActiveTab('login')}
          >
            Login
          </Tab>
          <Tab 
            active={activeTab === 'register'} 
            onClick={() => setActiveTab('register')}
          >
            Create Account
          </Tab>
        </TabContainer>

        <Form onSubmit={handleSubmit}>
          {activeTab === 'register' && (
            <InputGroup>
              <IconWrapper><User size={18} /></IconWrapper>
              <Input 
                type="text" 
                name="name" 
                placeholder="Full Name" 
                required 
                value={formData.name}
                onChange={handleChange}
              />
            </InputGroup>
          )}

          <InputGroup>
            <IconWrapper><Mail size={18} /></IconWrapper>
            <Input 
              type="email" 
              name="email" 
              placeholder="Email Address" 
              required 
              value={formData.email}
              onChange={handleChange}
            />
          </InputGroup>

          <InputGroup>
            <IconWrapper><Lock size={18} /></IconWrapper>
            <Input 
              type="password" 
              name="password" 
              placeholder="Password" 
              required 
              value={formData.password}
              onChange={handleChange}
            />
          </InputGroup>

          {activeTab === 'register' && (
            <>
              <InputGroup>
                <IconWrapper><Phone size={18} /></IconWrapper>
                <Input 
                  type="tel" 
                  name="phone" 
                  placeholder="Phone Number" 
                  required 
                  value={formData.phone}
                  onChange={handleChange}
                />
              </InputGroup>

              <InputGroup>
                <IconWrapper><Briefcase size={18} /></IconWrapper>
                <Input 
                  type="number" 
                  name="experience_years" 
                  placeholder="Years of Experience" 
                  required 
                  value={formData.experience_years}
                  onChange={handleChange}
                />
              </InputGroup>

              <InputGroup>
                <IconWrapper><Award size={18} /></IconWrapper>
                <Input 
                  type="text" 
                  name="specialization" 
                  placeholder="Specialization (e.g. Engine, Brakes)" 
                  required 
                  value={formData.specialization}
                  onChange={handleChange}
                />
              </InputGroup>

              <InputGroup>
                <IconWrapper><MapPin size={18} /></IconWrapper>
                <Input 
                  type="number" 
                  name="service_radius" 
                  placeholder="Service Radius (km)" 
                  required 
                  value={formData.service_radius}
                  onChange={handleChange}
                />
              </InputGroup>
            </>
          )}

          <Button type="submit" disabled={loading}>
            {loading ? 'Processing...' : activeTab === 'login' ? 'Login' : 'Create Account'}
          </Button>

          {error && <ErrorText>{error}</ErrorText>}
        </Form>
      </AuthCard>
    </Container>
  );
};

export default MechanicAuth;
