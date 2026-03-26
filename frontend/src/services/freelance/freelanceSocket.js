import { io } from 'socket.io-client';

class FreelanceSocketService {
  constructor() {
    this.socket = null;
    this.currentProjectId = null;
    this.currentUserId = null;
    this.callbacks = {};
  }

  connect(userId) {
    if (this.socket && this.socket.connected) {
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      this.socket = io('http://localhost:5000', {
        transports: ['websocket', 'polling'],
        withCredentials: true
      });

      this.currentUserId = userId;

      this.socket.on('connect', () => {
        console.log('Freelance socket connected');
        resolve();
      });

      this.socket.on('disconnect', () => {
        console.log('Freelance socket disconnected');
      });

      this.socket.on('error', (error) => {
        console.error('Freelance socket error:', error);
        reject(error);
      });

      // Set up event listeners
      this.setupEventListeners();
    });
  }

  setupEventListeners() {
    // Join project confirmation
    this.socket.on('joined_project', (data) => {
      console.log('Joined project:', data);
      if (this.callbacks.onJoinedProject) {
        this.callbacks.onJoinedProject(data);
      }
    });

    // User joined notification
    this.socket.on('user_joined', (data) => {
      console.log('User joined project:', data);
      if (this.callbacks.onUserJoined) {
        this.callbacks.onUserJoined(data);
      }
    });

    // User left notification
    this.socket.on('user_left', (data) => {
      console.log('User left project:', data);
      if (this.callbacks.onUserLeft) {
        this.callbacks.onUserLeft(data);
      }
    });

    // New message received
    this.socket.on('new_message', (message) => {
      console.log('New message received:', message);
      if (this.callbacks.onNewMessage) {
        this.callbacks.onNewMessage(message);
      }
    });

    // Typing indicators
    this.socket.on('user_typing', (data) => {
      console.log('User typing:', data);
      if (this.callbacks.onUserTyping) {
        this.callbacks.onUserTyping(data);
      }
    });

    // Online users list
    this.socket.on('online_users_list', (data) => {
      console.log('Online users:', data);
      if (this.callbacks.onOnlineUsers) {
        this.callbacks.onOnlineUsers(data);
      }
    });

    // Messages read notification
    this.socket.on('messages_read', (data) => {
      console.log('Messages read:', data);
      if (this.callbacks.onMessagesRead) {
        this.callbacks.onMessagesRead(data);
      }
    });

    // Error handling
    this.socket.on('error', (error) => {
      console.error('Socket error:', error);
      if (this.callbacks.onError) {
        this.callbacks.onError(error);
      }
    });
  }

  // Join a project room
  joinProject(projectId) {
    if (!this.socket || !this.socket.connected) {
      console.error('Socket not connected');
      return;
    }

    this.currentProjectId = projectId;
    this.socket.emit('join_freelance_project', {
      project_id: projectId,
      user_id: this.currentUserId
    });
  }

  // Leave a project room
  leaveProject(projectId) {
    if (!this.socket || !this.socket.connected) {
      return;
    }

    this.socket.emit('leave_freelance_project', {
      project_id: projectId,
      user_id: this.currentUserId
    });

    if (this.currentProjectId === projectId) {
      this.currentProjectId = null;
    }
  }

  // Send a message
  sendMessage(projectId, message, fileAttachment = null) {
    if (!this.socket || !this.socket.connected) {
      console.error('Socket not connected');
      return;
    }

    this.socket.emit('send_freelance_message', {
      project_id: projectId,
      sender_id: this.currentUserId,
      message: message,
      file_attachment: fileAttachment
    });
  }

  // Start typing indicator
  startTyping(projectId) {
    if (!this.socket || !this.socket.connected) {
      return;
    }

    this.socket.emit('typing_start', {
      project_id: projectId,
      user_id: this.currentUserId
    });
  }

  // Stop typing indicator
  stopTyping(projectId) {
    if (!this.socket || !this.socket.connected) {
      return;
    }

    this.socket.emit('typing_stop', {
      project_id: projectId,
      user_id: this.currentUserId
    });
  }

  // Get online users in project
  getOnlineUsers(projectId) {
    if (!this.socket || !this.socket.connected) {
      return;
    }

    this.socket.emit('get_online_users', {
      project_id: projectId
    });
  }

  // Mark messages as read
  markMessagesRead(projectId) {
    if (!this.socket || !this.socket.connected) {
      return;
    }

    this.socket.emit('mark_messages_read', {
      project_id: projectId,
      user_id: this.currentUserId
    });
  }

  // Set event callbacks
  setCallbacks(callbacks) {
    this.callbacks = { ...this.callbacks, ...callbacks };
  }

  // Disconnect socket
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.currentProjectId = null;
      this.currentUserId = null;
    }
  }

  // Check if connected
  isConnected() {
    return this.socket && this.socket.connected;
  }
}

// Create singleton instance
const freelanceSocket = new FreelanceSocketService();

export default freelanceSocket;
