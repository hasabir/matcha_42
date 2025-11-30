// Chat.js
import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { useNotifications } from '../contexts/NotificationContext';
import { useAuth } from '../contexts/AuthContext';
import { useSearchParams } from 'react-router-dom';
import './Chat.css';

const API_BASE_URL = 'http://localhost:5000';
const FALLBACK_AVATAR = 'https://cdn-icons-png.flaticon.com/512/149/149071.png';

// Helper to convert relative URLs to absolute
const toAbsoluteUrl = (url) => {
  if (!url) return FALLBACK_AVATAR;
  if (/^https?:\/\//i.test(url)) return url;
  
  try {
    let cleanUrl = url.replace(/^\/+/, '');
    if (cleanUrl.startsWith('profiles/') && !cleanUrl.startsWith('static/')) {
      cleanUrl = `static/${cleanUrl}`;
    }
    cleanUrl = cleanUrl.replace(/^static\/static\//, 'static/');
    return `${API_BASE_URL}/${cleanUrl}`;
  } catch {
    return url.startsWith('/') ? `${API_BASE_URL}${url}` : `${API_BASE_URL}/${url}`;
  }
};

const Chat = () => {
  const { socket, socketConnected, currentUserId, decrementMessageCount } = useNotifications();
  const { isLoading: authLoading, user } = useAuth();
  const [matches, setMatches] = useState([]);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef(null);
  const [searchParams] = useSearchParams();

  // Track socket readiness - use user ID from AuthContext instead of NotificationContext
  const socketReady = socketConnected && user?.id;
  
  // Debug socket status
  useEffect(() => {
    console.log('🔍 [Chat] Socket status:', {
      socketConnected,
      currentUserId,
      userFromAuth: user?.id,
      socketReady,
      socket: socket ? 'exists' : 'null',
      socketConnectedStatus: socket?.connected
    });
  }, [socketConnected, currentUserId, user?.id, socketReady, socket]);

  // Automatically scroll down on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Helpers to persist/load chat history per match
  const saveChatHistory = (matchId, msgs) => {
    try {
      localStorage.setItem(`chat_history_${matchId}`, JSON.stringify(msgs));
    } catch (e) {
      console.warn('Unable to save chat history:', e);
    }
  };

  const loadChatHistory = (matchId) => {
    try {
      const data = localStorage.getItem(`chat_history_${matchId}`);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.warn('Unable to load chat history:', e);
      return [];
    }
  };

  // Select a match
  const selectMatch = useCallback(async (match) => {
    setSelectedMatch(match);
    const cached = loadChatHistory(match.id);
    console.log('📚 [Chat] Loaded cached messages:', cached);
    setMessages(cached);

    if (!socket || !socket.connected || !user?.id) {
      console.error('❌ [Chat] Socket not available:', {
        socket: !!socket,
        connected: socket?.connected,
        currentUserId,
        userFromAuth: user?.id
      });
      return;
    }

    console.log('🔗 [Chat] Joining chat room:', {
      user_id: user.id,
      other_user_id: match.id,
      socketConnected: socket.connected
    });
    
    socket.emit('join_chat', { user_id: user.id, other_user_id: match.id });

    let loadedMessages = cached;

    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token');
      const resp = await axios.post(
        `${API_BASE_URL}/api/chat/get_chat_history`,
        { other_user: match.username, limit: 50, offset: 0 },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (resp.data.success) {
        console.log('📚 [Chat] Loaded messages from API:', resp.data.messages);
        const formatted = (resp.data.messages || []).map((m) => ({
          ...m,
          message_text: m.message_text || m.content || m.message || '',
          created_at: m.created_at || m.timestamp || m.sent_at || m.createdAt || null,
        }));
        loadedMessages = formatted.reverse();
        console.log('📚 [Chat] Formatted messages:', loadedMessages);
        setMessages(loadedMessages);
        saveChatHistory(match.id, loadedMessages);
      } else {
        console.log('📚 [Chat] API response not successful:', resp.data);
      }
    } catch (err) {
      console.error('Error fetching chat history:', err);
      // Check if it's a blocking error
      if (err.response?.data?.blocked) {
        setSelectedMatch({...match, blocked: true, blockedMessage: err.response.data.error});
        setMessages([]);
        return;
      }
    }
  }, [socket, currentUserId, decrementMessageCount]);

  // Setup socket event listeners
  useEffect(() => {
    if (!socket || !socketReady) return;

    const handleNewMessage = (message) => {
      console.log('📥 [Chat] Received message:', message);
      console.log('📥 [Chat] Current match:', selectedMatch);
      console.log('📥 [Chat] Current user ID from AuthContext:', user.id);
      console.log('📥 [Chat] Current user ID from NotificationContext:', currentUserId);
      
      if (!selectedMatch) {
        console.log('📥 [Chat] No selected match, ignoring message');
        return;
      }

      const isRelevantMessage =
        (message.sender_id === selectedMatch.id && message.receiver_id === user.id) ||
        (message.sender_id === user.id && message.receiver_id === selectedMatch.id);

      console.log('📥 [Chat] Is relevant message:', isRelevantMessage);
      if (!isRelevantMessage) return;

      setMessages((prev) => {
        const withoutTemp = prev.filter(m => {
          if (m.id && m.id.toString().startsWith('temp-')) {
            return m.message_text !== message.content || m.sender_id !== message.sender_id;
          }
          return true;
        });

        const messageExists = withoutTemp.some(m => m.id === message.message_id);
        if (messageExists) return prev;

        const updated = [
          ...withoutTemp,
          {
            id: message.message_id,
            sender_id: message.sender_id,
            receiver_id: message.receiver_id,
            message_text: message.content,
            created_at: message.timestamp,
            status: 'delivered'
          }
        ];

        saveChatHistory(selectedMatch.id, updated);
        return updated;
      });
    };

    socket.on('new_message', handleNewMessage);
    
    // Listen for chat room join confirmation
    const handleChatJoined = (data) => {
      console.log('🔗 [Chat] Successfully joined chat room:', data);
    };
    
    socket.on('chat_joined', handleChatJoined);

    // Listen for message delivery confirmation
    const handleMessageSent = (data) => {
      console.log('✅ [Chat] Message sent confirmation:', data);
      if (data.status === 'success') {
        // Update temp message to delivered status
        setMessages(prev => prev.map(msg => 
          msg.id.toString().startsWith('temp-') && msg.status === 'sending'
            ? { ...msg, status: 'delivered', id: data.message_id }
            : msg
        ));
      }
    };
    
    socket.on('message_sent', handleMessageSent);

    // Listen for socket errors (including blocking)
    const handleSocketError = (error) => {
      console.error('❌ [Chat] Socket error:', error);
      if (error.blocked && selectedMatch) {
        setSelectedMatch({...selectedMatch, blocked: true, blockedMessage: error.message});
        setMessages([]);
      }
    };
    
    socket.on('error', handleSocketError);

    return () => {
      socket.off('new_message', handleNewMessage);
      socket.off('chat_joined', handleChatJoined);
      socket.off('message_sent', handleMessageSent);
      socket.off('error', handleSocketError);
    };
  }, [socket, selectedMatch, socketReady]);

  // Load match list on mount
  useEffect(() => {
    const fetchMatches = async () => {
      try {
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        if (!token) {
          setLoading(false);
          return;
        }

        const res = await axios.get(`${API_BASE_URL}/api/interactions/my_connections`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setMatches(res.data.result || []);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching matches:', err);
        setLoading(false);
      }
    };
    fetchMatches();
  }, []);

  // Listen for blocking events to update matches list
  useEffect(() => {
    if (!socket || !socketReady) return;

    const handleUserBlocked = (data) => {
      console.log('🚫 [Chat] User blocked event:', data);
      // Remove blocked user from matches list
      if (data.blocked_user_id) {
        setMatches(prev => prev.filter(match => match.id !== data.blocked_user_id));
        // If currently chatting with blocked user, clear selection
        if (selectedMatch?.id === data.blocked_user_id) {
          setSelectedMatch(null);
          setMessages([]);
        }
      }
    };

    const handleUserBlockedBy = (data) => {
      console.log('🚫 [Chat] User blocked by event:', data);
      // Remove blocker from matches list
      if (data.blocker_user_id) {
        setMatches(prev => prev.filter(match => match.id !== data.blocker_user_id));
        // If currently chatting with blocker, clear selection
        if (selectedMatch?.id === data.blocker_user_id) {
          setSelectedMatch(null);
          setMessages([]);
        }
      }
    };

    socket.on('user_blocked', handleUserBlocked);
    socket.on('user_blocked_by', handleUserBlockedBy);

    return () => {
      socket.off('user_blocked', handleUserBlocked);
      socket.off('user_blocked_by', handleUserBlockedBy);
    };
  }, [socket, socketReady, selectedMatch]);

  // Auto-select match from URL parameter
  useEffect(() => {
    const userIdParam = searchParams.get('userId');
    if (!userIdParam || matches.length === 0 || !socketReady) return;

    const matchToSelect = matches.find(m => m.id === parseInt(userIdParam));
    if (matchToSelect) {
      selectMatch(matchToSelect);
    }
  }, [matches, socketReady, searchParams, selectMatch]);

  const sendMessage = (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedMatch || !currentUserId) return;

    // Check socket connection and attempt reconnection if needed
    if (!socket?.connected) {
      console.warn('⚠️ [Chat] Socket not connected - attempting to reconnect');
      if (socket) {
        socket.connect();
      }
      return;
    }

    const messageContent = newMessage.trim();

    const tempMessage = {
      id: `temp-${Date.now()}`,
      sender_id: currentUserId,
      receiver_id: selectedMatch.id,
      message_text: messageContent,
      created_at: new Date().toISOString(),
      status: 'sending'
    };

    setMessages(prev => [...prev, tempMessage]);

    console.log('📤 [Chat] Sending message:', {
      sender_id: user.id,
      receiver_id: selectedMatch.id,
      content: messageContent,
      socketConnected: socket?.connected,
      socketReady
    });
    
    try {
      socket.emit('send_message', {
        sender_id: user.id,
        receiver_id: selectedMatch.id,
        content: messageContent,
      });
    } catch (error) {
      console.error('❌ [Chat] Error sending message:', error);
      // Remove temp message on error
      setMessages(prev => prev.filter(m => m.id !== tempMessage.id));
    }

    setNewMessage('');
  };

  if (authLoading) {
    return (
      <div className="chat-container">
        <div className="loading">Initializing authentication...</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="chat-container">
        <div className="loading">Loading matches...</div>
      </div>
    );
  }

  return (
    <div className="chat-container">
      {!socketReady && (
        <div style={{
          background: '#fff3cd',
          padding: '10px',
          textAlign: 'center',
          borderBottom: '1px solid #ffeaa7',
          fontSize: '14px'
        }}>
          ⏳ Connecting to chat service...
        </div>
      )}

      <div className="chat-layout">
        <div className="matches-sidebar">
          <h2>Your Matches</h2>
          {matches.length === 0 ? (
            <div className="no-matches">
              <p>No matches yet!</p>
              <p>Start liking profiles to find matches 💖</p>
            </div>
          ) : (
            <div className="matches-list">
              {matches.map((m) => (
                <div
                  key={m.id}
                  className={`match-item ${selectedMatch?.id === m.id ? 'active' : ''}`}
                  onClick={() => selectMatch(m)}
                >
                  <img 
                    src={toAbsoluteUrl(m.profile_picture)} 
                    alt="Profile" 
                    className="match-avatar"
                    onError={(e) => { e.target.src = FALLBACK_AVATAR; }}
                  />
                  <div className="match-info">
                    <div className="match-name">{m.first_name} {m.last_name}</div>
                    <div className="match-username">@{m.username}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="chat-area">
          {selectedMatch ? (
            <>
              <div className="chat-header">
                <img 
                  src={toAbsoluteUrl(selectedMatch.profile_picture)} 
                  alt="Profile" 
                  className="chat-header-avatar"
                  onError={(e) => { e.target.src = FALLBACK_AVATAR; }}
                />
                <div className="chat-header-info">
                  <h3>{selectedMatch.first_name} {selectedMatch.last_name}</h3>
                  <span className="chat-header-username">@{selectedMatch.username}</span>
                </div>
              </div>
              {selectedMatch.blocked ? (
                <div className="blocked-message-container">
                  <div className="blocked-message">
                    <span className="blocked-icon">🚫</span>
                    <h3>{selectedMatch.blockedMessage || 'This user is blocked'}</h3>
                    <p>You cannot send or receive messages.</p>
                  </div>
                </div>
              ) : (
                <>
                  <div className="messages-container">
                    {messages.length === 0 ? (
                      <div className="no-messages">
                        <p>No messages yet. Say hi! 👋</p>
                      </div>
                    ) : (
                      messages.map((msg, index) => (
                        <div key={msg.id || index} className={`message ${msg.sender_id === currentUserId ? 'sent' : 'received'}`}>
                          <div className="message-bubble">
                            <p>{msg.message_text}</p>
                            <span className="message-time">
                              {msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                            </span>
                          </div>
                        </div>
                      ))
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                  <form className="message-input-form" onSubmit={sendMessage}>
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder="Type a message..."
                      className="message-input"
                    />
                    <button type="submit" className="send-button">Send</button>
                  </form>
                </>
              )}
            </>
          ) : (
            <div className="no-chat-selected">
              <h3>Select a match to start chatting</h3>
              <p>Choose someone from your matches to begin the conversation 💬</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Chat;
