import React from 'react';
import { X, AlertCircle } from 'lucide-react';
import './ErrorMessage.css';

const ErrorMessage = ({ message, onClose }) => {
  return (
    <div className="error-container fade-in">
      <div className="error-card">
        <div className="error-icon">
          <AlertCircle size={24} />
        </div>
        <div className="error-content">
          <h4 className="error-title">Analysis Failed</h4>
          <p className="error-message">{message}</p>
        </div>
        <button className="error-close" onClick={onClose}>
          <X size={20} />
        </button>
      </div>
    </div>
  );
};

export default ErrorMessage;
