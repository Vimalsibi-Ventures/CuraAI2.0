// frontend/src/App.jsx

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { useAuth } from './hooks/useAuth';

import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import ChatPage from './pages/ChatPage';

// ✅ ProtectedRoute component
function ProtectedRoute({ children }) {
  const auth = useAuth();
  if (!auth?.authToken) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

// ✅ Internal component so useAuth() is valid inside AuthProvider
function AppRoutes() {
  const auth = useAuth();

  return (
    <Routes>
      {/* Default route: Redirect based on login state */}
      <Route
        path="/"
        element={
          auth?.authToken ? <Navigate to="/chat" replace /> : <Navigate to="/login" replace />
        }
      />

      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />

      {/* Protected route */}
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <ChatPage />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}

export default App;
