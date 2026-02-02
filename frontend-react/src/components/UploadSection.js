import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image as ImageIcon, FileText } from 'lucide-react';
import './UploadSection.css';

const UploadSection = ({ onFileUpload, loading }) => {
  const [preview, setPreview] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      // Create preview
      const reader = new FileReader();
      reader.onload = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);

      // Upload file
      onFileUpload(file);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.webp']
    },
    multiple: false,
    disabled: loading
  });

  return (
    <section className="upload-section">
      <div className="upload-header">
        <h2 className="upload-title">Upload Your Chart</h2>
        <p className="upload-description">
          Drop your trading chart image for instant AI-powered technical analysis
        </p>
      </div>

      <div 
        {...getRootProps()} 
        className={`dropzone ${isDragActive ? 'active' : ''} ${loading ? 'disabled' : ''}`}
      >
        <input {...getInputProps()} />
        
        <div className="dropzone-content">
          {preview ? (
            <div className="preview-container">
              <img src={preview} alt="Chart preview" className="chart-preview" />
              {!loading && (
                <div className="preview-overlay">
                  <Upload size={32} />
                  <p>Drop new chart to replace</p>
                </div>
              )}
            </div>
          ) : (
            <>
              <div className="upload-icon">
                <ImageIcon size={48} />
              </div>
              <h3 className="dropzone-title">
                {isDragActive ? 'Drop your chart here' : 'Drag & drop your chart'}
              </h3>
              <p className="dropzone-text">
                or click to browse
              </p>
              <div className="file-types">
                <FileText size={16} />
                <span>PNG, JPG, JPEG, WEBP</span>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="upload-features">
        <div className="feature">
          <div className="feature-icon">🤖</div>
          <div className="feature-text">
            <strong>AI Vision</strong>
            <span>Advanced chart recognition</span>
          </div>
        </div>
        <div className="feature">
          <div className="feature-icon">⚡</div>
          <div className="feature-text">
            <strong>Fast Analysis</strong>
            <span>Results in seconds</span>
          </div>
        </div>
        <div className="feature">
          <div className="feature-icon">🎯</div>
          <div className="feature-text">
            <strong>Actionable Insights</strong>
            <span>Clear trading perspective</span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default UploadSection;
