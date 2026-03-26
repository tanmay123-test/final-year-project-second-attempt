import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, Paperclip, Users, Circle, CheckCircle } from 'lucide-react';
import freelanceSocket from '../freelanceSocket';
import api from '../../../shared/api';
import '../styles/RealTimeChat.css';

const RealTimeChat = ({ projectId, currentUserId, projectTitle }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [typingUsers, setTypingUsers] = useState(new Set());
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  // Initialize socket connection and load messages
  useEffect(() => {
    if (!projectId || !currentUserId) return;

    const initializeChat = async () => {
      try {
        setLoading(true);
        setError(null);

        // Connect to socket
        await freelanceSocket.connect(currentUserId);
        setIsConnected(true);

        // Join project room
        freelanceSocket.joinProject(projectId);

        // Load initial messages
        const response = await api.get(`/api/freelance/work/${projectId}/messages`);
        if (response.data.success) {
          setMessages(response.data.messages || []);
        }

        setLoading(false);
      } catch (err) {
        console.error('Failed to initialize chat:', err);
        setError('Failed to connect to chat');
        setLoading(false);
      }
    };

    initializeChat();

    // Cleanup on unmount
    return () => {
      if (projectId) {
        freelanceSocket.leaveProject(projectId);
      }
    };
  }, [projectId, currentUserId]);

  // Setup socket event listeners
  useEffect(() => {
    freelanceSocket.setCallbacks({
      onNewMessage: (message) => {
        setMessages(prev => [...prev, message]);
        scrollToBottom();
      },
      onUserJoined: (data) => {
        console.log('User joined:', data);
        getOnlineUsers();
      },
      onUserLeft: (data) => {
        console.log('User left:', data);
        getOnlineUsers();
      },
      onUserTyping: (data) => {
        setTypingUsers(prev => {
          const newTypingUsers = new Set(prev);
          if (data.is_typing) {
            newTypingUsers.add(data.user_id);
          } else {
            newTypingUsers.delete(data.user_id);
          }
          return newTypingUsers;
        });
      },
      onOnlineUsers: (data) => {
        setOnlineUsers(data.users || []);
      },
      onError: (error) => {
        console.error('Socket error:', error);
        setError(error.message || 'Connection error');
      }
    });
  }, []);

  // Get online users
  const getOnlineUsers = useCallback(() => {
    if (projectId) {
      freelanceSocket.getOnlineUsers(projectId);
    }
  }, [projectId]);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Auto scroll when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle sending messages
  const handleSendMessage = useCallback((e) => {
    e.preventDefault();
    
    if (!newMessage.trim() || !isConnected) return;

    freelanceSocket.sendMessage(projectId, newMessage.trim());
    setNewMessage('');
    
    // Stop typing indicator
    stopTyping();
  }, [newMessage, projectId, isConnected]);

  // Handle typing indicators
  const handleTyping = useCallback((e) => {
    setNewMessage(e.target.value);
    
    if (e.target.value.trim()) {
      startTyping();
    } else {
      stopTyping();
    }
  }, []);

  const startTyping = () => {
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    
    freelanceSocket.startTyping(projectId);
    
    typingTimeoutRef.current = setTimeout(() => {
      stopTyping();
    }, 1000);
  };

  const stopTyping = () => {
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    freelanceSocket.stopTyping(projectId);
  };

  // Handle file upload (basic implementation)
  const handleFileUpload = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*,.pdf,.doc,.docx';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        // For now, just show file name. In production, upload to server
        freelanceSocket.sendMessage(
          projectId, 
          `📎 Shared file: ${file.name}`, 
          file.name
        );
      }
    };
    input.click();
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // Get typing indicator text
  const getTypingIndicator = () => {
    if (typingUsers.size === 0) return '';
    if (typingUsers.size === 1) {
      return 'Someone is typing...';
    }
    return `${typingUsers.size} people are typing...`;
  };

  if (loading) {
    return (
      <div className="freelance-chat-loading">
        <div className="loading-spinner"></div>
        <p>Loading chat...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="freelance-chat-error">
        <p>❌ {error}</p>
        <button onClick={() => window.location.reload()}>
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="freelance-realtime-chat">
      {/* Chat Header */}
      <div className="chat-header">
        <div className="chat-title">
          <h3>{projectTitle || 'Project Chat'}</h3>
          <div className="connection-status">
            {isConnected ? (
              <CheckCircle className="status-icon online" size={16} />
            ) : (
              <Circle className="status-icon offline" size={16} />
            )}
            <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>
        
        <div className="chat-info">
          <div className="online-users">
            <Users size={16} />
            <span>{onlineUsers.length} online</span>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="no-messages">
            <p>No messages yet. Start the conversation!</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.sender_id === currentUserId ? 'sent' : 'received'}`}
            >
              <div className="message-content">
                <div className="message-header">
                  <span className="sender-name">
                    {message.sender_name || `User ${message.sender_id}`}
                  </span>
                  <span className="message-time">
                    {formatTime(message.created_at)}
                  </span>
                </div>
                <div className="message-text">
                  {message.message}
                </div>
                {message.file_attachment && (
                  <div className="file-attachment">
                    📎 {message.file_attachment}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        
        {/* Typing Indicator */}
        {typingUsers.size > 0 && (
          <div className="typing-indicator">
            <div className="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span>{getTypingIndicator()}</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <form onSubmit={handleSendMessage} className="message-input-container">
        <div className="input-actions">
          <button
            type="button"
            onClick={handleFileUpload}
            className="attach-button"
            disabled={!isConnected}
          >
            <Paperclip size={20} />
          </button>
        </div>
        
        <input
          type="text"
          value={newMessage}
          onChange={handleTyping}
          placeholder="Type a message..."
          className="message-input"
          disabled={!isConnected}
          maxLength={1000}
        />
        
        <button
          type="submit"
          className="send-button"
          disabled={!newMessage.trim() || !isConnected}
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};

export default RealTimeChat;
