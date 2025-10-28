import React, { createContext, useState, useEffect } from 'react';

// ✅ Export AuthContext so it can be used in useAuth.js
export const AuthContext = createContext();

// AuthProvider component
export const AuthProvider = ({ children }) => {
  const [authToken, setAuthToken] = useState(localStorage.getItem('authToken') || null);
  const [userId, setUserId] = useState(localStorage.getItem('userId') || null);
  const [userRole, setUserRole] = useState(localStorage.getItem('userRole') || null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // 🧠 Mock API responses (temporary)
  const mockApi = (email, password, role = 'user') => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (!email || !password) reject(new Error('Missing credentials'));
        else {
          resolve({
            token: 'mock-token-12345',
            userId: 'mock-user-id',
            role,
          });
        }
      }, 800); // simulate API delay
    });
  };

  // 🔐 Login function
  const login = async (email, password) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await mockApi(email, password);
      const { token, userId, role } = data;

      localStorage.setItem('authToken', token);
      localStorage.setItem('userId', userId);
      localStorage.setItem('userRole', role);

      setAuthToken(token);
      setUserId(userId);
      setUserRole(role);
    } catch (err) {
      console.error('Login failed:', err);
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // 🧾 Signup function
  const signup = async (email, password, role) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await mockApi(email, password, role);
      const { token, userId, role: userRole } = data;

      localStorage.setItem('authToken', token);
      localStorage.setItem('userId', userId);
      localStorage.setItem('userRole', userRole);

      setAuthToken(token);
      setUserId(userId);
      setUserRole(userRole);
    } catch (err) {
      console.error('Signup failed:', err);
      setError(err.message || 'Signup failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // 🚪 Logout function
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
