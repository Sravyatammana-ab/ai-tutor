import React from 'react'
import './Footer.css'

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-separator"></div>
      <div className="footer-copyright">
        <p>&copy; 2025 Cerevyn Solutions Pvt Ltd. All rights reserved.</p>
      </div>
      <div className="footer-logo">
        <h2>CEREVYN</h2>
      </div>
      <div className="footer-mission">
        <p>Global AI company transforming healthcare, education, and business operations with intelligent solutions for a smarter tomorrow.</p>
      </div>
      <div className="footer-contact">
        <a href="mailto:info@cerevyn.com">info@cerevyn.com</a>
        <span className="separator-dot">•</span>
        <a href="tel:+917893525665">+91 78935 25665</a>
      </div>
      <div className="footer-address">
        <p>T Hub, Hyderabad Knowledge City, Serilingampally, Hyderabad, Telangana 500081, India</p>
      </div>
    </footer>
  )
}

export default Footer
