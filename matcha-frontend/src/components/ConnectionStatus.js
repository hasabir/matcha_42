import React, { useState, useEffect } from 'react';
import { useNotifications } from '../contexts/NotificationContext';
import { useAuth } from '../contexts/AuthContext';
import './ConnectionStatus.css';

const ConnectionStatus = () => {
  const { socket, socketConnected, currentUserId, checkSocketStatus } = useNotifications();
  const { isAuthenticated, isLoading } = useAuth();
  const [showDetails, setShowDetails] = useState(false);
  const [statusHistory, setStatusHistory] = useState([]);

  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      const status = checkSocketStatus();
      const timestamp = new Date().toLocaleTimeString();
      setStatusHistory(prev => [
        { ...status, timestamp },
        ...prev.slice(0, 9) // Keep last 10 entries
      ]);
    }
  }, [socketConnected, currentUserId, isAuthenticated, isLoading, checkSocketStatus]);

  if (!isAuthenticated || isLoading) {
    return null;
  }

  const getStatusColor = () => {
    if (!socket) return '#ff6b6b'; // Red - no socket
    if (!socketConnected) return '#ffa726'; // Orange - socket exists but not connected
    return '#4caf50'; // Green - connected
  };

  const getStatusText = () => {
    if (!socket) return 'No Socket';
    if (!socketConnected) return 'Connecting...';
    return 'Connected';
  };

  const getStatusIcon = () => {
    if (!socket) return '❌';
    if (!socketConnected) return '🔄';
    return '✅';
  };

  return (
    <div className="connection-status">
      <button
        className="status-indicator"
        onClick={() => setShowDetails(!showDetails)}
        style={{ backgroundColor: getStatusColor() }}
        title={`Socket Status: ${getStatusText()}`}
      >
        <span className="status-icon">{getStatusIcon()}</span>
        <span className="status-text">{getStatusText()}</span>
      </button>

      {showDetails && (
        <div className="status-details">
          <h4>Real-time Status</h4>
          <div className="status-info">
            <div><strong>Socket:</strong> {socket ? '✅ Exists' : '❌ Missing'}</div>
            <div><strong>Connected:</strong> {socketConnected ? '✅ Yes' : '❌ No'}</div>
            <div><strong>User ID:</strong> {currentUserId || '❌ Not set'}</div>
            <div><strong>Socket ID:</strong> {socket?.id || '❌ Not available'}</div>
          </div>

          {statusHistory.length > 0 && (
            <div className="status-history">
              <h5>Recent Status Changes</h5>
              <div className="history-list">
                {statusHistory.slice(0, 5).map((entry, index) => (
                  <div key={index} className="history-entry">
                    <span className="timestamp">{entry.timestamp}</span>
                    <span className="status">
                      {entry.socketConnected ? '✅' : '❌'} 
                      {entry.socketExists ? 'Socket' : 'No Socket'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button 
            className="close-details"
            onClick={() => setShowDetails(false)}
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
};

export default ConnectionStatus;
