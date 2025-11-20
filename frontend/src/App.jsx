import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Homepage from './components/Homepage'
import SignUp from './components/SignUp'
import SignIn from './components/SignIn'
import Dashboard from './components/Dashboard'
import Footer from './components/Footer'
import './App.css'

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const user = localStorage.getItem('user')
  return user ? children : <Navigate to="/signin" replace />
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<><Homepage /><Footer /></>} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/signin" element={<SignIn />} />
        <Route 
          path="/app" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App


