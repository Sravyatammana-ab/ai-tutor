/* global __SUPABASE_URL__, __SUPABASE_KEY__ */
import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { supabaseClient } from '../lib/supabaseClient'
import { sanitizeName, writeStoredUser } from '../utils/userProfile'
import './Auth.css'

const supabase = supabaseClient

function SignIn() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const validateForm = () => {
    const newErrors = {}

    if (!formData.email) {
      newErrors.email = 'Email is required'
    }

    if (!formData.password) {
      newErrors.password = 'Password is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setMessage('')

    if (!validateForm()) {
      return
    }

    if (!supabase) {
      setMessage('Supabase is not configured. Please check your environment variables.')
      return
    }

    setLoading(true)

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: formData.email,
        password: formData.password
      })

      if (error) {
        setMessage(error.message)
      } else {
        let metadataName = sanitizeName(data.user.user_metadata?.full_name)
        if (!metadataName && supabase) {
          try {
            const { data: userProfile } = await supabase.auth.getUser()
            metadataName = sanitizeName(userProfile?.user?.user_metadata?.full_name)
          } catch (fetchError) {
            console.warn('Failed to refresh user profile', fetchError)
          }
        }
        const emailFallback = data.user.email ? sanitizeName(data.user.email.split('@')[0]) : ''
        const fallbackName = metadataName || emailFallback || 'Learner'
        const safeUser = {
          id: data.user.id,
          email: data.user.email,
          full_name: fallbackName
        }
        writeStoredUser(safeUser)
        navigate('/app')
      }
    } catch (error) {
      setMessage('An error occurred. Please try again.')
      console.error('Sign in error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Sign In</h1>
          <p>Welcome back to cere-shikshak Tutor</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="yourname@gmail.com"
              className={errors.email ? 'error' : ''}
            />
            {errors.email && <span className="error-message">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              className={errors.password ? 'error' : ''}
            />
            {errors.password && <span className="error-message">{errors.password}</span>}
          </div>

          {message && (
            <div className={`message ${message.includes('Welcome') ? 'success' : 'error'}`}>
              {message}
            </div>
          )}

          <button type="submit" className="auth-button" disabled={loading}>
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Don't have an account? <Link to="/signup">Sign Up</Link>
          </p>
          <p>
            <Link to="/">Back to Home</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default SignIn

