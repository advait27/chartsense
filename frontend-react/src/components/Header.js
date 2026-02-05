import React from 'react';
import { TrendingUp, BarChart3, Sparkles } from 'lucide-react';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo-section">
          <div className="logo-icon">
            <BarChart3 size={32} />
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
