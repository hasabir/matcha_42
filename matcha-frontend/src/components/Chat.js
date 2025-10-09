// Chat.js - Real-time messaging component for Matcha
import React, { useEffect, useState, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import { chatApi, api } from "../utils/api";
import "./Chat.css";

const FALLBACK_AVATAR =
  "https://static-00.iconduck.com/assets.00/user-avatar-1024x1024-2xhpdo1n.png";

export default function Chat() {
  const [searchParams] = useSearchParams();
  const initialUsername = searchParams.get("with");

  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageInput, setMessageInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [currentUserId, setCurrentUserId] = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const pollingIntervalRef = useRef(null);

  // Auto-scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load current user ID
  useEffect(() => {
    async function loadMe() {
      try {
        const res = await api.meProfile();
        const json = await res.json();
        if (res.ok && json.result) {
          // Assuming the backend returns user_id or id
          setCurrentUserId(json.result.id || json.result.user_id);
        }
      } catch (e) {
        console.error("Failed to load current user:", e);
      }
    }
    loadMe();
  }, []);

  // Load conversations
  useEffect(() => {
    async function loadConversations() {
      try {
        setLoading(true);
        setError(null);
        const res = await chatApi.getConversations();
        const json = await res.json();

        if (!res.ok) {
          throw new Error(json?.error || "Failed to load conversations");
        }

        const convos = json.result || [];

        // Fetch avatars for each conversation
        const enriched = await Promise.all(
          convos.map(async (conv) => {
            try {
              const picRes = await api.userProfilePic(conv.other_username);
              const picJson = await picRes.json();
              return {
                ...conv,
                other_avatar: picRes.ok && picJson?.result ? picJson.result : FALLBACK_AVATAR,
              };
            } catch {
              return { ...conv, other_avatar: FALLBACK_AVATAR };
            }
          })
        );

        setConversations(enriched);

        // If there's an initial username, select that conversation
        if (initialUsername) {
          const conv = enriched.find((c) => c.other_username === initialUsername);
          if (conv) {
            handleSelectConversation(conv);
          }
        }
      } catch (e) {
        setError(e.message || "Failed to load conversations");
      } finally {
        setLoading(false);
      }
    }

    loadConversations();
  }, [initialUsername]);

  // Load messages for selected conversation
  const handleSelectConversation = async (conversation) => {
    try {
      setSelectedConversation(conversation);
      setMessages([]);
      setError(null);

      const res = await chatApi.getConversation(conversation.other_username);
      const json = await res.json();

      if (!res.ok) {
        throw new Error(json?.error || "Failed to load messages");
      }

      setMessages(json.messages || []);

      // Mark as read
      if (conversation.conversation_id) {
        await chatApi.markAsRead(conversation.conversation_id);
        // Update unread count in conversations list
        setConversations((prev) =>
          prev.map((c) =>
            c.conversation_id === conversation.conversation_id
              ? { ...c, unread_count: 0 }
              : c
          )
        );
      }
    } catch (e) {
      setError(e.message || "Failed to load conversation");
    }
  };

  // Poll for new messages in selected conversation
  const pollMessages = async () => {
    if (!selectedConversation) return;

    try {
      const res = await chatApi.getConversation(selectedConversation.other_username);
      const json = await res.json();

      if (res.ok && json.messages) {
        const newMessages = json.messages;
        // Only update if message count changed
        setMessages((prev) => {
          if (prev.length !== newMessages.length) {
            return newMessages;
          }
          return prev;
        });
      }
    } catch (e) {
      console.error("Polling error:", e);
    }
  };

  // Start polling when conversation is selected
  useEffect(() => {
    if (selectedConversation) {
      // Initial load is already done in handleSelectConversation
      // Start polling every 3 seconds
      pollingIntervalRef.current = setInterval(pollMessages, 3000);
    } else {
      // Clear polling when no conversation selected
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    }

    // Cleanup on unmount or conversation change
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [selectedConversation]);

  // Send a message
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!messageInput.trim() || !selectedConversation || sending) return;

    const messageText = messageInput.trim();
    setMessageInput("");
    setSending(false);

    try {
      const res = await chatApi.sendMessageToUser(
        selectedConversation.other_username,
        messageText
      );
      const json = await res.json();

      if (!res.ok) {
        throw new Error(json?.error || "Failed to send message");
      }

      // Add the new message to the list
      const newMessage = json.result;
      setMessages((prev) => [...prev, newMessage]);

      // Update last message in conversations list
      setConversations((prev) =>
        prev.map((c) =>
          c.conversation_id === selectedConversation.conversation_id
            ? {
                ...c,
                last_message: messageText,
                last_message_at: newMessage.created_at,
                last_sender_id: currentUserId,
              }
            : c
        )
      );

      // Focus back on input
      inputRef.current?.focus();
    } catch (e) {
      setError(e.message || "Failed to send message");
      // Restore message in input
      setMessageInput(messageText);
    } finally {
      setSending(false);
    }
  };

  // Format message timestamp
  const formatMessageTime = (timestamp) => {
    if (!timestamp) return "";
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  if (loading) {
    return (
      <div className="chat-container">
        <div className="loading-state">Loading conversations...</div>
      </div>
    );
  }

  return (
    <div className="chat-container">
      {/* Conversations Panel */}
      <div className="conversations-panel">
        <div className="conversations-header">
          <h2>Messages</h2>
        </div>
        <div className="conversations-list">
          {conversations.length === 0 ? (
            <div className="empty-state" style={{ padding: "40px 20px" }}>
              <p>No conversations yet.</p>
              <p style={{ fontSize: "0.85rem", marginTop: "8px" }}>
                Match with someone to start chatting!
              </p>
            </div>
          ) : (
            conversations.map((conv) => (
              <div
                key={conv.conversation_id}
                className={`conversation-item ${
                  selectedConversation?.conversation_id === conv.conversation_id
                    ? "active"
                    : ""
                }`}
                onClick={() => handleSelectConversation(conv)}
              >
                <img
                  src={conv.other_avatar || FALLBACK_AVATAR}
                  alt={conv.other_username}
                  className="conversation-avatar"
                />
                <div className="conversation-info">
                  <p className="conversation-name">
                    {conv.other_first_name || conv.other_username}
                    {conv.other_active && <span className="online-indicator" />}
                  </p>
                  <p className="conversation-last-message">
                    {conv.last_message || "No messages yet"}
                  </p>
                </div>
                {conv.unread_count > 0 && (
                  <span className="conversation-badge">{conv.unread_count}</span>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Chat Panel */}
      <div className="chat-panel">
        {!selectedConversation ? (
          <div className="empty-state">
            <h3>Select a conversation</h3>
            <p>Choose a conversation from the list to start chatting</p>
          </div>
        ) : (
          <>
            {/* Chat Header */}
            <div className="chat-header">
              <img
                src={selectedConversation.other_avatar || FALLBACK_AVATAR}
                alt={selectedConversation.other_username}
                className="chat-header-avatar"
              />
              <div className="chat-header-info">
                <h3>
                  {selectedConversation.other_first_name ||
                    selectedConversation.other_username}
                </h3>
                <p>
                  {selectedConversation.other_active ? (
                    <span style={{ color: "#4caf50" }}>● Online</span>
                  ) : (
                    "Offline"
                  )}
                </p>
              </div>
            </div>

            {/* Messages */}
            <div className="messages-container">
              {error && <div className="error-state">{error}</div>}
              {messages.length === 0 ? (
                <div className="empty-state">
                  <p>No messages yet. Say hello! 👋</p>
                </div>
              ) : (
                messages.map((msg) => (
                  <div
                    key={msg.message_id}
                    className={`message ${
                      msg.sender_id === currentUserId ? "sent" : "received"
                    }`}
                  >
                    <div className="message-bubble">
                      <p className="message-text">{msg.message_text}</p>
                      <div className="message-time">
                        {formatMessageTime(msg.created_at)}
                      </div>
                    </div>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form className="message-input-container" onSubmit={handleSendMessage}>
              <textarea
                ref={inputRef}
                className="message-input"
                placeholder="Type a message..."
                value={messageInput}
                onChange={(e) => setMessageInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage(e);
                  }
                }}
                rows={1}
              />
              <button
                type="submit"
                className="send-button"
                disabled={!messageInput.trim() || sending}
              >
                {sending ? "Sending..." : "Send"}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
