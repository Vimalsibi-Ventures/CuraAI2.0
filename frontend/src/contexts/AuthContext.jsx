// frontend/src/contexts/AuthContext.js

import React, { createContext, useState, useEffect } from 'react';
import { loginUser, signupUser } from '../services/api';

// ✅ Export AuthContext so it can be used in useAuth.js
export const AuthContext = createContext();

// AuthProvider component
export const AuthProvider = ({ children }) => {
  const [authToken, setAuthToken] = useState(null);
  const [userId, setUserId] = useState(null);
  const [userRole, setUserRole] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // ✅ During development, clear any old tokens so LoginPage always shows first
  useEffect(() => {
    console.log('🧹 Clearing old auth data for development...');
    localStorage.removeItem('authToken');
    localStorage.removeItem('userId');
    localStorage.removeItem('userRole');
  }, []);

  // Load user info (used when backend is connected)
  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    const storedUserId = localStorage.getItem('userId');
    const storedUserRole = localStorage.getItem('userRole');

    if (storedToken) setAuthToken(storedToken);
    if (storedUserId) setUserId(storedUserId);
    if (storedUserRole) setUserRole(storedUserRole);
  }, []);

  // Login function (dummy placeholder)
  const login = async (email, password) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await loginUser(email, password);
      const { token, userId, role } = data;

      localStorage.setItem('authToken', token);
      localStorage.setItem('userId', userId);
      localStorage.setItem('userRole', role);

      setAuthToken(token);
      setUserId(userId);
      setUserRole(role);
    } catch (err) {
      console.error('Login failed:', err);
      setError(err.response?.data?.message || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Signup function (dummy placeholder)
  const signup = async (email, password, role) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await signupUser(email, password, role);
      const { token, userId, role: userRole } = data;

      localStorage.setItem('authToken', token);
      localStorage.setItem('userId', userId);
      localStorage.setItem('userRole', userRole);

      setAuthToken(token);
      setUserId(userId);
      setUserRole(userRole);
    } catch (err) {
      console.error('Signup failed:', err);
      setError(err.response?.data?.message || 'Signup failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userId');
    localStorage.removeItem('userRole');
    setAuthToken(null);
    setUserId(null);
    setUserRole(null);
    setError(null);
  };

  const value = {
    authToken,
    userId,
    userRole,
    isLoading,
    error,
    login,
    signup,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
