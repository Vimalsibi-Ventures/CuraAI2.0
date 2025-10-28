import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()   // ✅ uncommented and used

  const handleSubmit = (e) => {
    e.preventDefault()
    console.log('Login attempt:', email, password)
    // TODO: Add authentication logic here (API call + redirect)
  }

  return (
    <div className="login-container" style={{ maxWidth: '400px', margin: '50px auto', textAlign: 'center' }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        {/* ... existing form fields ... */}
        <button type="submit" style={{ padding: '10px', borderRadius: '6px', backgroundColor: '#007bff', color: '#fff', border: 'none' }}>
          Login
        </button>
      </form>

      {/* ✅ Temporary navigation button */}
      <button
        onClick={() => {
          localStorage.setItem('authToken', 'dummy-token')
          navigate('/chat')
        }}
        style={{ marginTop: '20px', padding: '10px', borderRadius: '6px', backgroundColor: '#28a745', color: '#fff', border: 'none' }}
      >
        Go to Chat (Temp)
      </button>

      <p style={{ marginTop: '15px' }}>
        Don't have an account?{' '}
        <Link to="/signup" style={{ color: '#007bff' }}>
          Sign Up
        </Link>
      </p>
    </div>
  )
}

export default LoginPage
