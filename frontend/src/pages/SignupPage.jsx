import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

function SignupPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [role, setRole] = useState('Patient')
  //const navigate = useNavigate()

  const handleSubmit = (e) => {
    e.preventDefault()
    console.log('Signup attempt:', email, password, role)
    // TODO: Add signup logic here (API call + redirect)
  }

  return (
    <div className="signup-container" style={{ maxWidth: '400px', margin: '50px auto', textAlign: 'center' }}>
      <h2>Sign Up</h2>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <div>
          <label htmlFor="email">Email:</label><br />
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #ccc' }}
          />
        </div>

        <div>
          <label htmlFor="password">Password:</label><br />
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #ccc' }}
          />
        </div>

        <div>
          <label htmlFor="confirmPassword">Confirm Password:</label><br />
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #ccc' }}
          />
        </div>

        <div style={{ textAlign: 'left' }}>
          <label>Role:</label><br />
          <label>
            <input
              type="radio"
              name="role"
              value="Patient"
              checked={role === 'Patient'}
              onChange={(e) => setRole(e.target.value)}
            />{' '}
            Patient
          </label>
          <br />
          <label>
            <input
              type="radio"
              name="role"
              value="Professional"
              checked={role === 'Professional'}
              onChange={(e) => setRole(e.target.value)}
            />{' '}
            Professional
          </label>
        </div>

        <button
          type="submit"
          style={{ padding: '10px', borderRadius: '6px', backgroundColor: '#28a745', color: '#fff', border: 'none' }}
        >
          Sign Up
        </button>
      </form>

      <p style={{ marginTop: '15px' }}>
        Already have an account?{' '}
        <Link to="/login" style={{ color: '#007bff' }}>
          Login
        </Link>
      </p>
    </div>
  )
}

export default SignupPage
