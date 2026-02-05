import React from 'react';
import { Sparkles } from 'lucide-react';
import './Header.css';

// Custom logo icon with triangular design
const CharteredIcon = ({ size = 32 }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M8 18L12 10L16 18H8Z" fill="currentColor" opacity="0.9"/>
    <path d="M16 18L20 10L24 18H16Z" fill="currentColor" opacity="0.9"/>
    <path d="M8 28L12 20L16 28H8Z" fill="currentColor" opacity="0.7"/>
    <path d="M16 28L20 20L24 28H16Z" fill="currentColor" opacity="0.7"/>
  </svg>
);

const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo-section">
          <div className="logo-icon">
            <CharteredIcon size={32} />
          </div>
          <div className="logo-text">
            <h1 className="logo-title">
              Chartered
              <Sparkles className="sparkle-icon" size={16} />
            </h1>
            <p className="logo-subtitle">AI-Powered Technical Analysis</p>
          </div>
        </div>

        <div className="status-badge">
          <span className="status-dot"></span>
          <span>Live</span>
        </div>
      </div>
      
      <div className="header-gradient"></div>
    </header>
  );
};

export default Header;
