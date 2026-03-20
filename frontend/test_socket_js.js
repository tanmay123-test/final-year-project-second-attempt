import { io } from 'socket.io-client';

const SOCKET_URL = 'http://127.0.0.1:5000'; // As per .env
const workerId = 8;

console.log(`Connecting to ${SOCKET_URL}...`);

const socket = io(SOCKET_URL, {
    transports: ['websocket', 'polling'],
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
});

socket.on('connect', () => {
    console.log('✅ Connected to Housekeeping Socket');
    console.log(`🔌 Joining room: worker_${workerId}`);
    socket.emit('join_housekeeping', {
        user_type: 'worker',
        id: workerId
    });
});

socket.on('connect_error', (err) => {
    console.error('⚠️ Connection Error:', err.message);
});

socket.on('room_joined', (data) => {
    console.log('✅ Room Joined:', data);
});

socket.on('new_booking', (data) => {
    console.log('🔔 New Booking Received:', data);
    // process.exit(0); // Keep running to see more if needed, or exit
});

// Keep alive for a bit
setTimeout(() => {
    console.log('Timeout waiting for booking...');
    process.exit(0);
}, 60000);
