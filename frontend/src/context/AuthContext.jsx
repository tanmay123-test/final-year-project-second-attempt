import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService, workerService } from '../services/api';

export const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [worker, setWorker] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
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

  const workerLogin = async (email, password) => {
    try {
      const response = await workerService.login({ email, password });
      const { worker_id, service, specialization, token, name } = response.data;
      
      localStorage.setItem('worker_id', worker_id);
      localStorage.setItem('worker_email', email);
      if (token) {
        localStorage.setItem('token', token); // Store worker token (reusing user token key might be tricky if user is also logged in?)
        // Ideally we should distinguish, but current logic in api.js uses 'token' from localStorage.
        // For now, let's assume one login at a time (User OR Worker).
      }
      
      setWorker({
        id: worker_id, // Normalize to id
        worker_id,
        email,
        service,
        specialization,
        name
      });
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
