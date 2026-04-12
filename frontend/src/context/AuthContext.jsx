import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService, workerService, doctorService } from '../shared/api';

export const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [worker, setWorker] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      // Skip auth check for worker portal
      if (window.location.pathname.startsWith('/worker')) {
        setLoading(false);
        return;
      }
      
      const token = localStorage.getItem('token');
      
      if (token) {
        try {
          // 1. Try to fetch User Info
          const response = await authService.getUserInfo();
          setUser(response.data);
        } catch (error) {
          // 2. If User Info fails, try Worker Info
          try {
            const workerRes = await workerService.verifyToken();
            setWorker(workerRes.data);
            
            // Sync localStorage if needed
            localStorage.setItem('worker_id', workerRes.data.id);
            localStorage.setItem('worker_email', workerRes.data.email);
          } catch (workerError) {
            console.error('Auth check failed:', workerError);
            localStorage.removeItem('token');
            localStorage.removeItem('user_id');
            localStorage.removeItem('worker_id');
            localStorage.removeItem('worker_email');
            setUser(null);
            setWorker(null);
          }
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (username, password) => {
    try {
      const response = await authService.login({ username, password });
      const { token, user_id } = response.data;
      localStorage.setItem('token', token);
      localStorage.setItem('user_id', user_id);
      
      const userInfo = await authService.getUserInfo();
      setUser(userInfo.data);
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const workerLogin = async (email, password, serviceType = 'general') => {
    try {
      let response;
      
      // Use doctor-specific login for healthcare workers
      if (serviceType === 'healthcare') {
        response = await doctorService.login({ email, password });
      } else {
        response = await workerService.login({ email, password });
      }
      
      const { worker_id, doctor_id, service, specialization, token, name } = response.data;
      
      // Handle different ID naming conventions
      const actualWorkerId = worker_id || doctor_id;
      
      localStorage.setItem('worker_id', actualWorkerId);
      localStorage.setItem('worker_email', email);
      if (token) {
        localStorage.setItem('token', token); 
        localStorage.setItem('workerToken', token); // For car service workers
        localStorage.setItem('doctorToken', token); // For DoctorDashboard
        localStorage.setItem('worker_token', token); // For WorkerDashboardPage
      }
      
      const workerData = {
        id: actualWorkerId,
        worker_id: actualWorkerId,
        email,
        service,
        specialization,
        name
      };
      localStorage.setItem('workerData', JSON.stringify(workerData)); // For car service workers
      
      setWorker(workerData);
      return true;
    } catch (error) {
      console.error('Worker login failed:', error);
      throw error;
    }
  };

  const logout = () => {
    // User logout
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    setUser(null);
    
    // Worker logout
    localStorage.removeItem('worker_id');
    localStorage.removeItem('worker_email');
    localStorage.removeItem('workerToken');
    localStorage.removeItem('doctorToken');
    localStorage.removeItem('worker_token');
    localStorage.removeItem('workerData');
    setWorker(null);
  };

  const value = {
    user,
    worker,
    loading,
    login,
    workerLogin,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
