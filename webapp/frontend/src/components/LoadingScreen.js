import React, { useState, useEffect } from 'react';
import './LoadingScreen.css';

const LoadingScreen = ({ loadingStages = [], currentStage = 0 }) => {
  const [progress, setProgress] = useState(0);
  const [showEstimatedTime, setShowEstimatedTime] = useState(true);
  const [estimatedTime, setEstimatedTime] = useState(10); // seconds

  useEffect(() => {
    // Calculate progress based on current stage
    const progressPercentage = loadingStages.length > 0 
      ? Math.min(((currentStage + 1) / loadingStages.length) * 100, 100) // Cap at 100%
      : 0;
    setProgress(progressPercentage);

    // Update estimated time - account for free service wake-up time
    if (currentStage === 0) {
      // Initial stage - service might be waking up
      setEstimatedTime(45); // Up to 45 seconds for cold start
    } else if (currentStage === 1) {
      // Service is waking up
      setEstimatedTime(30); // 30 more seconds
    } else {
      // Service is awake, normal processing
      const remainingStages = loadingStages.length - currentStage - 1;
      setEstimatedTime(Math.max(1, remainingStages * 2)); // 2 seconds per remaining stage
    }
  }, [currentStage, loadingStages]);

  const defaultStages = [
    "Initializing WaterTrace...",
    "Waking up backend service...",
    "Connecting to satellite data servers...",
    "Loading groundwater measurements...",
    "Processing district information...",
    "Preparing visualizations..."
  ];

  const stages = loadingStages.length > 0 ? loadingStages : defaultStages;
  const currentMessage = stages[currentStage] || stages[stages.length - 1];

  return (
    <div className="loading-screen">
      <div className="loading-container">
        <div className="loading-logo">
          <svg width="80" height="80" viewBox="0 0 80 80" className="water-drop">
            <path
              d="M40 10 C40 10, 20 35, 20 50 C20 61, 29 70, 40 70 C51 70, 60 61, 60 50 C60 35, 40 10, 40 10"
              fill="url(#waterGradient)"
              className="drop-path"
            />
            <defs>
              <linearGradient id="waterGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#4FC3F7" />
                <stop offset="100%" stopColor="#2196F3" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        <h1 className="loading-title">WaterTrace</h1>
        <p className="loading-subtitle">Pakistan Groundwater Monitoring System</p>

        <div className="loading-spinner">
          <div className="spinner-ring"></div>
          <div className="spinner-ring"></div>
          <div className="spinner-ring"></div>
        </div>

        <div className="loading-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <p className="progress-text">{Math.min(Math.round(progress), 100)}% Complete</p>
        </div>

        <div className="loading-status">
          <p className="status-message">{currentMessage}</p>
          {currentStage <= 1 && (
            <p className="service-note">
              Free service may take up to 1 minute to wake up
            </p>
          )}
          {showEstimatedTime && estimatedTime > 0 && (
            <p className="estimated-time">
              Estimated time: {estimatedTime} {estimatedTime === 1 ? 'second' : 'seconds'}
            </p>
          )}
        </div>

        <div className="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  );
};

export default LoadingScreen;