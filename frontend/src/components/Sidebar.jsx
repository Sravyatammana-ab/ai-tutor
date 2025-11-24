import React, { useState, useEffect } from 'react'
import { getStoredUserName, ensureUserName } from '../utils/userProfile'
import './Sidebar.css'

function Sidebar({ documentName, sessionId, isOpen, onToggle }) {
  const [userName, setUserName] = useState('')

  useEffect(() => {
    let isMounted = true
    const cached = getStoredUserName()
    if (cached) {
      setUserName(cached)
    } else {
      ensureUserName().then((resolved) => {
        if (isMounted && resolved) {
          setUserName(resolved)
        }
      })
    }
    return () => {
      isMounted = false
    }
  }, [])

  // Prevent body scroll when sidebar is open on mobile
  useEffect(() => {
    if (isOpen && window.innerWidth <= 768) {
      document.body.style.overflow = 'hidden'
      document.body.style.position = 'fixed'
      document.body.style.width = '100%'
    } else {
      document.body.style.overflow = ''
      document.body.style.position = ''
      document.body.style.width = ''
    }
    return () => {
      document.body.style.overflow = ''
      document.body.style.position = ''
      document.body.style.width = ''
    }
  }, [isOpen])

  const handleOverlayClick = () => {
    if (isOpen) {
      onToggle()
    }
  }

  return (
    <>
      {/* Overlay for mobile */}
      <div 
        className={`sidebar-overlay ${isOpen ? 'open' : ''}`}
        onClick={handleOverlayClick}
        aria-hidden="true"
      />

      {/* Sidebar Toggle Button - Desktop only */}
      <button 
        className={`sidebar-toggle ${isOpen ? 'open' : ''}`}
        onClick={onToggle}
        aria-label="Toggle sidebar"
      >
        {isOpen ? '◀' : '▶'}
      </button>

      {/* Sidebar */}
      <div className={`sidebar ${isOpen ? 'open' : ''}`} onClick={(e) => e.stopPropagation()}>
        <div className="sidebar-content">
          <div className="sidebar-header">
            <h3>Session Info</h3>
          </div>
          
          <div className="sidebar-section">
            <div className="sidebar-item">
              <label>Textbook:</label>
              <p className="sidebar-value">{documentName || 'No textbook uploaded'}</p>
            </div>
            
            <div className="sidebar-item">
              <label>Session ID:</label>
              <p className="sidebar-value sidebar-session-id">{sessionId || 'Not started'}</p>
            </div>
          </div>

          {userName && (
            <div className="sidebar-section sidebar-user-section">
              <div className="sidebar-item">
                <label>User:</label>
                <p className="sidebar-value sidebar-user-name">{userName}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

export default Sidebar

