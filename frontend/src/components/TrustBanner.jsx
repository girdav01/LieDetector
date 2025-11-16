/**
 * TrustBanner Component
 * Displays real-time trust score with color-coded visual indicators
 */

import React, { useState, useEffect } from 'react';
import './TrustBanner.css';

const TrustBanner = ({ score, message, factors = [], eventId }) => {
  const [expanded, setExpanded] = useState(false);

  // Determine color based on score
  const getColorConfig = (score) => {
    if (score >= 70) {
      return {
        color: 'green',
        label: 'LOW RISK',
        icon: '✓',
        bgColor: '#d4edda',
        borderColor: '#28a745',
        textColor: '#155724'
      };
    } else if (score >= 40) {
      return {
        color: 'orange',
        label: 'MEDIUM RISK',
        icon: '⚡',
        bgColor: '#fff3cd',
        borderColor: '#ffc107',
        textColor: '#856404'
      };
    } else {
      return {
        color: 'red',
        label: 'HIGH RISK',
        icon: '⚠️',
        bgColor: '#f8d7da',
        borderColor: '#dc3545',
        textColor: '#721c24'
      };
    }
  };

  const colorConfig = getColorConfig(score);

  const handleFeedback = async (action) => {
    try {
      const response = await fetch('http://localhost:8000/user_feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          event_id: eventId,
          action: action
        })
      });

      if (response.ok) {
        alert(`Thank you for your feedback!`);
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  return (
    <div
      className="trust-banner"
      style={{
        backgroundColor: colorConfig.bgColor,
        borderLeft: `6px solid ${colorConfig.borderColor}`,
        color: colorConfig.textColor,
        padding: '16px',
        marginBottom: '16px',
        borderRadius: '4px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}
    >
      <div className="trust-banner-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '24px' }}>{colorConfig.icon}</span>
          <div>
            <div style={{ fontWeight: 'bold', fontSize: '14px' }}>
              Trust Score: {score}/100 - {colorConfig.label}
            </div>
            <div style={{ fontSize: '14px', marginTop: '4px' }}>
              {message}
            </div>
          </div>
        </div>

        {factors && factors.length > 0 && (
          <button
            onClick={() => setExpanded(!expanded)}
            style={{
              background: 'transparent',
              border: `1px solid ${colorConfig.borderColor}`,
              color: colorConfig.textColor,
              padding: '6px 12px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: '600'
            }}
          >
            {expanded ? 'Hide Details' : 'Show Details'}
          </button>
        )}
      </div>

      {expanded && factors && factors.length > 0 && (
        <div
          className="trust-banner-details"
          style={{
            marginTop: '16px',
            paddingTop: '16px',
            borderTop: `1px solid ${colorConfig.borderColor}`
          }}
        >
          <div style={{ fontWeight: 'bold', marginBottom: '8px', fontSize: '13px' }}>
            Risk Factors Detected:
          </div>
          <ul style={{ margin: '0', paddingLeft: '20px', fontSize: '13px' }}>
            {factors.map((factor, index) => (
              <li key={index} style={{ marginBottom: '4px' }}>{factor}</li>
            ))}
          </ul>
        </div>
      )}

      <div
        className="trust-banner-actions"
        style={{
          marginTop: '12px',
          display: 'flex',
          gap: '8px',
          paddingTop: '12px',
          borderTop: `1px solid ${colorConfig.borderColor}`
        }}
      >
        <button
          onClick={() => handleFeedback('confirmed_legit')}
          style={{
            background: 'transparent',
            border: `1px solid ${colorConfig.borderColor}`,
            color: colorConfig.textColor,
            padding: '4px 12px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px'
          }}
        >
          Mark as Safe
        </button>
        <button
          onClick={() => handleFeedback('reported_suspicious')}
          style={{
            background: 'transparent',
            border: `1px solid ${colorConfig.borderColor}`,
            color: colorConfig.textColor,
            padding: '4px 12px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px'
          }}
        >
          Report as Suspicious
        </button>
      </div>

      {score < 40 && (
        <div
          style={{
            marginTop: '12px',
            padding: '12px',
            backgroundColor: 'rgba(0,0,0,0.05)',
            borderRadius: '4px',
            fontSize: '12px',
            fontWeight: '600'
          }}
        >
          🛡️ RECOMMENDED ACTION: Verify this request through an alternate communication channel before proceeding.
        </div>
      )}
    </div>
  );
};

export default TrustBanner;
