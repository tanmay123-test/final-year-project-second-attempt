import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const useDoctorAuth = () => {
  const [doctorToken, setDoctorToken] = useState(null);
  const [doctorInfo, setDoctorInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('doctorToken');
    
    if (!token) {
      navigate('/doctor/login');
      return;
    }

    setDoctorToken(token);
    
    // Fetch doctor info
    fetchDoctorInfo(token);
  }, [navigate]);

  const fetchDoctorInfo = async (token) => {
    try {
      const response = await fetch('http://localhost:5000/doctor/profile', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDoctorInfo(data);
      } else {
        // Token invalid, redirect to login
        localStorage.removeItem('doctorToken');
        navigate('/doctor/login');
      }
    } catch (error) {
      console.error('Error fetching doctor info:', error);
      localStorage.removeItem('doctorToken');
      navigate('/doctor/login');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('doctorToken');
    setDoctorInfo(null);
    setDoctorToken(null);
    navigate('/doctor/login');
  };

  const updateDoctorInfo = (newInfo) => {
    setDoctorInfo(prev => ({ ...prev, ...newInfo }));
  };

  return {
    doctorToken,
    doctorInfo,
    loading,
    logout,
    updateDoctorInfo,
    fetchDoctorInfo
  };
};

export default useDoctorAuth;
