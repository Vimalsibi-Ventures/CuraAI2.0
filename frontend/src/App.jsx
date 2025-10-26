import { Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import ChatPage from './pages/ChatPage'

// TODO: Replace with real auth check once authentication is implemented
const isAuthenticated = false  // temporary placeholder

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/chat" element={isAuthenticated ? <ChatPage /> : <Navigate to="/login" />} />
      
      {/* Default route */}
      <Route path="/" element={<Navigate to={isAuthenticated ? "/chat" : "/login"} />} />
    </Routes>
  )
}

export default App
