import io from 'socket.io-client';

class HealthcareSocket {
  constructor() {
    this.socket = null;
    this.connected = false;
  }

  connect() {
    if (this.socket && this.connected) {
      return this.socket;
    }

    this.socket = io('http://localhost:5000', {
      transports: ['websocket'],
      upgrade: false
    });

    this.socket.on('connect', () => {
      console.log('Connected to healthcare socket');
      this.connected = true;
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from healthcare socket');
      this.connected = false;
    });

    this.socket.on('worker_approval_update', (data) => {
      console.log('Worker approval update:', data);
      this.handleWorkerApprovalUpdate(data);
    });

    this.socket.on('new_worker_registration', (data) => {
      console.log('New worker registration:', data);
      this.handleNewWorkerRegistration(data);
    });

    this.socket.on('availability_updated', (data) => {
      console.log('Availability updated:', data);
      this.handleAvailabilityUpdate(data);
    });

    this.socket.on('new_appointment', (data) => {
      console.log('New appointment:', data);
      this.handleNewAppointment(data);
    });

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connected = false;
    }
  }

  joinRoom(room) {
    if (this.socket) {
      this.socket.emit('join_healthcare_room', { room });
    }
  }

  leaveRoom(room) {
    if (this.socket) {
      this.socket.emit('leave_healthcare_room', { room });
    }
  }

  // Event handlers
  handleWorkerApprovalUpdate(data) {
    // Show notification for worker approval/rejection
    this.showNotification(data.message, data.status === 'approved' ? 'success' : 'error');
    
    // Update UI if this is the current worker
    if (window.location.pathname.includes('/provider/healthcare')) {
      window.location.reload(); // Reload to show updated status
    }
  }

  handleNewWorkerRegistration(data) {
    // Show notification for admin
    this.showNotification(data.message, 'info');
    
    // Refresh admin dashboard if on admin page
    if (window.location.pathname.includes('/admin')) {
      window.location.reload();
    }
  }

  handleAvailabilityUpdate(data) {
    // Show notification for availability update
    this.showNotification(data.message, 'success');
    
    // Refresh availability if on worker dashboard
    if (window.location.pathname.includes('/provider/healthcare')) {
      // Trigger availability refresh
      window.dispatchEvent(new CustomEvent('availabilityUpdated', { detail: data }));
    }
  }

  handleNewAppointment(data) {
    // Show notification for new appointment
    this.showNotification(data.message, 'success');
    
    // Refresh appointments if on worker dashboard
    if (window.location.pathname.includes('/provider/healthcare')) {
      // Trigger appointment refresh
      window.dispatchEvent(new CustomEvent('newAppointment', { detail: data }));
    }
  }

  showNotification(message, type = 'info') {
    // Create a simple notification
    const notification = document.createElement('div');
    notification.className = `socket-notification socket-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 12px 20px;
      border-radius: 8px;
      color: white;
      font-weight: 500;
      z-index: 9999;
      animation: slideIn 0.3s ease-out;
      max-width: 300px;
    `;

    // Set background color based on type
    const colors = {
      success: '#16A34A',
      error: '#DC2626',
      info: '#2563EB',
      warning: '#D97706'
    };
    notification.style.backgroundColor = colors[type] || colors.info;

    // Add animation
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
    `;
    document.head.appendChild(style);

    document.body.appendChild(notification);

    // Remove after 5 seconds
    setTimeout(() => {
      notification.style.animation = 'slideIn 0.3s ease-out reverse';
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 5000);
  }
}

// Create singleton instance
const healthcareSocket = new HealthcareSocket();

export default healthcareSocket;
