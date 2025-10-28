// frontend/src/App.jsx

import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";

import LoginPage from "./pages/LoginPage";
import ChatPage from "./pages/ChatPage";
import DoctorChatPage from "./pages/DoctorChatPage"; // 👈 create this file later
import UserProfilePage from "./pages/UserProfilePage";



function AppRoutes() {
  return (
    <Routes>
      {/* Always start at Login page */}
      <Route path="/" element={<Navigate to="/login" replace />} />

      {/* Login page */}
      <Route path="/login" element={<LoginPage />} />

      {/* User chat page */}
      <Route path="/chat-user" element={<ChatPage />} />

      {/* Doctor chat page */}
      <Route path="/chat-doctor" element={<DoctorChatPage />} />
      {/* User profile page */}
      <Route path="/profile" element={<UserProfilePage />} />
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
