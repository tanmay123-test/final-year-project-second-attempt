import { io } from 'socket.io-client';

// Use the same URL as the API
const SOCKET_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

class HealthcareSocketService {
    constructor() {
        this.socket = null;
        this.listeners = new Map();
        this.currentRoom = null;
    }

    connect() {
        if (this.socket) return;

        this.socket = io(SOCKET_URL, {
            transports: ['websocket', 'polling'],
            reconnectionAttempts: 5,
            reconnectionDelay: 1000,
        });

        this.socket.on('connect', () => {
            console.log('✅ Connected to Healthcare Socket');
            if (this.currentRoom) {
                console.log(`🔄 Re-joining room: healthcare_${this.currentRoom.userType}_${this.currentRoom.userId}`);
                this.socket.emit('join_healthcare', {
                    user_type: this.currentRoom.userType,
                    id: this.currentRoom.userId
                });
            }
        });

        this.socket.on('disconnect', () => {
            console.log('❌ Disconnected from Healthcare Socket');
        });

        this.socket.on('connect_error', (err) => {
            console.error('⚠️ Healthcare Socket Connection Error:', err);
        });

        // Global event listeners
        this.socket.on('new_appointment', (data) => {
            console.log('🔔 New Appointment Received:', data);
            this._notifyListeners('new_appointment', data);
        });

        this.socket.on('appointment_update', (data) => {
            console.log('🔄 Appointment Update:', data);
            this._notifyListeners('appointment_update', data);
        });
        
        this.socket.on('room_joined', (data) => {
            console.log('✅ Room Joined Successfully:', data.room);
        });
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
    }

    joinRoom(userType, userId) {
        if (!this.socket) this.connect();
        
        this.currentRoom = { userType, userId };
        
        console.log(`🔌 Joining room: healthcare_${userType}_${userId}`);
        this.socket.emit('join_healthcare', {
            user_type: userType,
            id: userId
        });
    }

    leaveRoom(userType, userId) {
        if (!this.socket) return;
        
        if (this.currentRoom && this.currentRoom.userType === userType && this.currentRoom.userId === userId) {
            this.currentRoom = null;
        }
        
        console.log(`🔌 Leaving room: healthcare_${userType}_${userId}`);
        this.socket.emit('leave_healthcare', {
            user_type: userType,
            id: userId
        });
    }

    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, new Set());
        }
        this.listeners.get(event).add(callback);
    }

    off(event, callback) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).delete(callback);
        }
    }

    _notifyListeners(event, data) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (err) {
                    console.error(`Error in listener for ${event}:`, err);
                }
            });
        }
    }
}

const healthcareSocket = new HealthcareSocketService();
export default healthcareSocket;
