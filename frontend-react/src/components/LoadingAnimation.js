import React from 'react';
import './LoadingAnimation.css';

const LoadingAnimation = () => {
  return (
    <div className="loading-container fade-in">
      <div className="loading-card">
        <div className="loading-spinner">
          <div className="spinner-ring"></div>
          <div className="spinner-ring"></div>
          <div className="spinner-ring"></div>
        </div>
        
        <h3 className="loading-title">Analyzing Your Chart</h3>
        
        <div className="loading-steps">
          <div className="loading-step">
            <div className="step-icon processing">🔍</div>
            <span>Processing image...</span>
          </div>
          <div className="loading-step">
            <div className="step-icon">🤖</div>
            <span>Running AI analysis...</span>
          </div>
          <div className="loading-step">
            <div className="step-icon">📊</div>
            <span>Generating insights...</span>
          </div>
        </div>

        <p className="loading-hint">This usually takes 10-30 seconds</p>
      </div>
    </div>
  );
};

export default LoadingAnimation;
