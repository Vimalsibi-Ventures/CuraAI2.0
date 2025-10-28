import React from "react";
// 👇 Corrected the relative import paths
import ChatPage from "./pages/ChatPage.jsx"; 
import "./App.css";

// We comment out ALL the old router/auth logic

// import { Routes, Route, Navigate } from "react-router-dom";
// import { AuthProvider } from "./contexts/AuthContext";
// import LoginPage from "./pages/LoginPage";
// import DoctorChatPage from "./pages/DoctorChatPage";
// import UserProfilePage from "./pages/UserProfilePage";

/*
function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/chat-user" element={<ChatPage />} />
      <Route path="/chat-doctor" element={<DoctorChatPage />} />
      <Route path="/profile" element={<UserProfilePage />} />
    </Routes>
  );
}
*/

function App() {
  // The entire return is replaced with justChatPage
  return (
    <ChatPage />
  );

  /*
  // OLD AUTH/ROUTER CODE:
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
  */
}

export default App;

