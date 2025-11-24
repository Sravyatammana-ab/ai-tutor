import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import FileUpload from './FileUpload'
import Chat from './Chat'
import LanguageSelector from './LanguageSelector'
import Sidebar from './Sidebar'
import logoImage from '../assets/cerevyn-logo.png'
import { getStoredUserName, ensureUserName } from '../utils/userProfile'
import './Dashboard.css'

const SESSION_CACHE_KEY = 'aiTutorDocSessions'

const readSessionMap = () => {
  try {
    const raw = localStorage.getItem(SESSION_CACHE_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch (err) {
    console.warn('Failed to read session map', err)
    return {}
  }
}

const writeSessionMap = (map) => {
  try {
    localStorage.setItem(SESSION_CACHE_KEY, JSON.stringify(map))
  } catch (err) {
    console.warn('Failed to persist session map', err)
  }
}

const getOrCreateSessionForDoc = (documentId, generator) => {
  if (!documentId) {
    return generator()
  }
  const sessionMap = readSessionMap()
  if (sessionMap[documentId]) {
    return sessionMap[documentId]
  }
  const newSession = generator()
  sessionMap[documentId] = newSession
  writeSessionMap(sessionMap)
  return newSession
}

const rememberSessionForDoc = (documentId, sessionId) => {
  if (!documentId || !sessionId) return
  const sessionMap = readSessionMap()
  if (sessionMap[documentId] === sessionId) return
  sessionMap[documentId] = sessionId
  writeSessionMap(sessionMap)
}

function Dashboard() {
  const navigate = useNavigate()
  const [documentInfo, setDocumentInfo] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  const [language, setLanguage] = useState('en-IN')
  const [isDocumentUploaded, setIsDocumentUploaded] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [userName, setUserName] = useState('')

  useEffect(() => {
    let mounted = true
    const cached = getStoredUserName()
    if (cached) {
      setUserName(cached)
    } else {
      ensureUserName().then((resolved) => {
        if (mounted && resolved) {
          setUserName(resolved)
        }
      })
    }
    return () => {
      mounted = false
    }
  }, [])

  const handleFileUpload = (uploadResult) => {
    const docId = uploadResult?.documentId || uploadResult
    const filename = uploadResult?.filename || 'Uploaded Textbook'
    setDocumentInfo({
      documentId: docId,
      filename
    })
    setIsDocumentUploaded(true)
    const sessionForDoc = getOrCreateSessionForDoc(docId, generateSessionId)
    setSessionId(sessionForDoc)
  }

  const handleLanguageChange = (newLanguage) => {
    setLanguage(newLanguage)
  }

  const generateSessionId = () => {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
  }

  const handleSignOut = () => {
    localStorage.removeItem('user')
    navigate('/')
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        {/* Desktop Layout */}
        <div className="header-content header-desktop">
          <div className="header-left">
            {isDocumentUploaded && (
              <button 
                className="header-hamburger"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                aria-label="Toggle sidebar"
              >
                ☰
              </button>
            )}
            <div className="logo-section">
              <img src={logoImage} alt="Cerevyn SOLUTIONS" className="dashboard-logo" />
            </div>
          </div>
          <div className="header-center">
            <h1>CERE-SHIKSHAK</h1>
            <p>Convert your books/documents into e books with AI assistance</p>
          </div>
          <div className="header-actions">
            <div className="header-user-pill">
              {userName ? `Hi, ${userName}` : 'Hi, User'}
            </div>
            <button className="btn-signout" onClick={handleSignOut}>
              Sign Out
            </button>
          </div>
        </div>

        {/* Mobile Layout - 3 Rows */}
        <div className="header-content header-mobile">
          {/* Row 1: Hamburger (left) + Logo (center) */}
          <div className="header-row-1">
            {isDocumentUploaded && (
              <button 
                className="header-hamburger"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                aria-label="Toggle sidebar"
              >
                ☰
              </button>
            )}
            <div className="logo-section-mobile">
              <img src={logoImage} alt="Cerevyn SOLUTIONS" className="dashboard-logo" />
            </div>
          </div>

          {/* Row 2: Title and Description (centered) */}
          <div className="header-row-2">
            <h1>CERE-SHIKSHAK</h1>
            <p>Convert your books/documents into e-books with AI assistance</p>
          </div>

          {/* Row 3: Username (left) + Sign Out (right) */}
          <div className="header-row-3">
            <div className="header-user-pill-mobile">
              {userName ? `Hi, ${userName}` : 'Hi, User'}
            </div>
            <button className="btn-signout" onClick={handleSignOut}>
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <div className="dashboard-container">
        {!isDocumentUploaded ? (
          <div className="upload-section">
            <FileUpload onUpload={handleFileUpload} />
            <div className="language-selector-section">
              <LanguageSelector 
                language={language} 
                onLanguageChange={handleLanguageChange}
                variant="dark"
              />
            </div>
          </div>
        ) : (
          <div className={`chat-section ${sidebarOpen ? 'sidebar-open' : ''}`}>
            <div className="chat-header">
              <button 
                className="back-button"
                onClick={() => {
                  setIsDocumentUploaded(false)
                  setDocumentInfo(null)
                  setSessionId(null)
                }}
              >
                ← Upload New Document
              </button>
              <LanguageSelector 
                language={language} 
                onLanguageChange={handleLanguageChange}
                variant="light"
              />
            </div>
            {documentInfo && (
              <Chat
                documentId={documentInfo.documentId}
                documentName={documentInfo.filename}
                sessionId={sessionId}
                language={language}
                onSessionReady={(resolvedSessionId) => {
                  rememberSessionForDoc(documentInfo.documentId, resolvedSessionId)
                }}
              />
            )}
          </div>
        )}
      </div>
      
      {/* Sidebar - only show when document is uploaded */}
      {isDocumentUploaded && (
        <Sidebar
          documentName={documentInfo?.filename}
          sessionId={sessionId}
          isOpen={sidebarOpen}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
        />
      )}
      
    </div>
  )
}

export default Dashboard

