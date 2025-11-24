import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import logoImage from '../assets/cerevyn-logo.png'
import { getStoredUserName, ensureUserName } from '../utils/userProfile'
import './Homepage.css'

function Homepage() {
  const navigate = useNavigate()
  const [userName, setUserName] = useState('')
  const [hasSession, setHasSession] = useState(Boolean(localStorage.getItem('user')))

  useEffect(() => {
    let isMounted = true
    const cached = getStoredUserName()
    if (cached) {
      setUserName(cached)
    } else {
      ensureUserName().then((resolved) => {
        if (isMounted && resolved) {
          setUserName(resolved)
          setHasSession(true)
        }
      })
    }
    return () => {
      isMounted = false
    }
  }, [])

  const isLoggedIn = hasSession
  const greetingName = userName || 'Learner'

  const handleEnterDashboard = () => {
    if (isLoggedIn) {
      navigate('/app')
    } else {
      navigate('/signin')
    }
  }

  const handleSignOut = () => {
    localStorage.removeItem('user')
    setUserName('')
    setHasSession(false)
    navigate('/')
  }

  return (
    <div className="homepage">
      <div className="homepage-header">
        <div className="logo">
          <img src={logoImage} alt="Cerevyn SOLUTIONS" className="logo-image" />
        </div>
        <div className="auth-buttons">
          {isLoggedIn && userName ? (
            <>
              <span className="welcome-pill">Hi, {greetingName}</span>
              <button className="btn-signin" onClick={handleSignOut}>
                Sign Out
              </button>
            </>
          ) : (
            <>
              <button className="btn-signin" onClick={() => navigate('/signin')}>
                Sign In
              </button>
              <button className="btn-signup" onClick={() => navigate('/signup')}>
                Sign Up
              </button>
            </>
          )}
        </div>
      </div>

      <div className="homepage-hero">
        <div className="hero-content">
          <h1 className="hero-title">CERE-SHIKSHAK</h1>
          <p className="hero-description">
            CERE-SHIKSHAK is an intelligent learning platform designed to help students learn from their textbooks with AI assistance. 
            Upload your PDF textbooks, ask questions, and get instant answers in multiple Indian languages and English.
          </p>
          <div className="hero-buttons">
            <button className="btn-primary" onClick={handleEnterDashboard}>
              {isLoggedIn ? 'Go to Dashboard' : 'Enter Dashboard'}
            </button>
            {isLoggedIn && userName && <div className="btn-secondary">Hi, {greetingName}</div>}
          </div>
        </div>
      </div>

      <div className="homepage-features">
        <div className="feature-card">
          <div className="feature-icon">📚</div>
          <h3>Upload Textbooks</h3>
          <p>Upload PDF or DOCX textbooks and let AI extract the content</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">💬</div>
          <h3>Ask Questions</h3>
          <p>Get instant answers to your questions about the textbook content</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🌐</div>
          <h3>Multi-language</h3>
          <p>Support for 13 Indian languages and English</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🔊</div>
          <h3>Audio Responses</h3>
          <p>Listen to AI responses in your preferred language</p>
        </div>
      </div>
    </div>
  )
}

export default Homepage

