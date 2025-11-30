import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { fetchWithAuth } from '../utils/api';
import './ChatIndicator.css';

const ChatIndicator = () => {
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchUnreadMessages = async () => {
    try {
      const response = await fetchWithAuth('/api/chat/unread_count');
      if (response.ok) {
        const data = await response.json();
        setUnreadCount(data.unread_count);
      }
    } catch (error) {
      console.error('Failed to fetch unread messages:', error);
    }
  };

  useEffect(() => {
    fetchUnreadMessages();
    const interval = setInterval(fetchUnreadMessages, 30000); // Poll every 30 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <Link to="/chat" className="chat-indicator">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
      </svg>
      {unreadCount > 0 && <span className="chat-badge">{unreadCount}</span>}
    </Link>
  );
};

export default ChatIndicator;
