import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService, workerService } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [worker, setWorker] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      // Check for User Token
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const response = await authService.getUserInfo();
          setUser(response.data);
        } catch (error) {
          console.error('Auth check failed:', error);
          localStorage.removeItem('token');
          localStorage.removeItem('user_id');
        }
      }

      // Check for Worker ID
      const workerId = localStorage.getItem('worker_id');
      const workerEmail = localStorage.getItem('worker_email');
      if (workerId && workerEmail) {
        // Since we don't have a token verify for worker, we optimistically set state
        // In a real app, we should verify against backend
        setWorker({
          worker_id: workerId,
          email: workerEmail,
          // We might miss specialization here, but it's okay for now
        });
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

  const workerLogin = async (email) => {
    try {
      const response = await workerService.login({ email });
      const { worker_id, service, specialization } = response.data;
      
      localStorage.setItem('worker_id', worker_id);
      localStorage.setItem('worker_email', email);
      
      setWorker({
        worker_id,
        email,
        service,
        specialization
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
