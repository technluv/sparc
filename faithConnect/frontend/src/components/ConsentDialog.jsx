import React, { useState } from 'react';
import './ConsentDialog.css';

const ConsentDialog = ({ onConsent, onCancel }) => {
  const [consent, setConsent] = useState({
    allow_recording: false,
    allow_transcription: false,
    allow_ai_processing: false,
    allow_data_retention: false,
    data_retention_period: 30
  });

  const handleChange = (field) => {
    setConsent(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  const handleRetentionPeriodChange = (e) => {
    setConsent(prev => ({
      ...prev,
      data_retention_period: parseInt(e.target.value) || 30
    }));
  };

  const handleSubmit = () => {
    if (!consent.allow_recording) {
      alert('Audio recording permission is required to use this application.');
      return;
    }
    onConsent(consent);
  };

  return (
    <div className="consent-dialog-overlay">
      <div className="consent-dialog">
        <h2>Privacy Settings & Consent</h2>
        
        <div className="consent-section">
          <h3>Data Collection & Processing</h3>
          
          <div className="consent-option">
            <label>
              <input
                type="checkbox"
                checked={consent.allow_recording}
                onChange={() => handleChange('allow_recording')}
              />
              Allow audio recording (Required)
            </label>
            <p className="consent-description">
              Enables the application to record audio from your microphone during meetings.
            </p>
          </div>

          <div className="consent-option">
            <label>
              <input
                type="checkbox"
                checked={consent.allow_transcription}
                onChange={() => handleChange('allow_transcription')}
              />
              Allow speech-to-text transcription
            </label>
            <p className="consent-description">
              Converts recorded audio to text for analysis. No audio data is permanently stored.
            </p>
          </div>

          <div className="consent-option">
            <label>
              <input
                type="checkbox"
                checked={consent.allow_ai_processing}
                onChange={() => handleChange('allow_ai_processing')}
              />
              Allow AI analysis
            </label>
            <p className="consent-description">
              Processes transcribed text to provide insights and suggestions. All data is anonymized.
            </p>
          </div>
        </div>

        <div className="consent-section">
          <h3>Data Retention</h3>
          
          <div className="consent-option">
            <label>
              <input
                type="checkbox"
                checked={consent.allow_data_retention}
                onChange={() => handleChange('allow_data_retention')}
              />
              Allow temporary data retention
            </label>
            <p className="consent-description">
              Temporarily stores anonymized transcripts and analysis for the specified period.
            </p>
          </div>

          {consent.allow_data_retention && (
            <div className="retention-period">
              <label>
                Retention Period (days):
                <input
                  type="number"
                  min="1"
                  max="90"
                  value={consent.data_retention_period}
                  onChange={handleRetentionPeriodChange}
                />
              </label>
            </div>
          )}
        </div>

        <div className="privacy-notice">
          <h3>Privacy Notice</h3>
          <p>
            Your privacy is important to us. We implement the following measures:
            <ul>
              <li>All audio data is encrypted during transmission and processing</li>
              <li>Personal information is automatically anonymized</li>
              <li>Data is automatically deleted after the retention period</li>
              <li>You can revoke consent at any time</li>
            </ul>
          </p>
        </div>

        <div className="consent-actions">
          <button onClick={onCancel} className="cancel-button">
            Cancel
          </button>
          <button onClick={handleSubmit} className="confirm-button">
            Confirm Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConsentDialog;
