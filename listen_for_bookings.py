import socketio
import time
import sys

# Configuration
BASE_URL = "http://localhost:5000"
WORKER_ID = 8

# Initialize SocketIO Client
sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print("✅ Connected to WebSocket Server")
    print(f"🔌 Joining room: worker_{WORKER_ID}")
    sio.emit('join_housekeeping', {'user_type': 'worker', 'id': WORKER_ID})

@sio.on('disconnect')
def on_disconnect():
    print("❌ Disconnected from WebSocket Server")

@sio.on('room_joined')
def on_room_joined(data):
    print(f"✅ Joined room successfully: {data}")

@sio.on('new_booking')
def on_new_booking(data):
    print(f"🔔 NEW BOOKING RECEIVED: {data}")

@sio.on('booking_update')
def on_booking_update(data):
    print(f"🔄 BOOKING UPDATE RECEIVED: {data}")

def main():
    print(f"Starting WebSocket Listener for Worker {WORKER_ID}...")
    try:
        sio.connect(BASE_URL, transports=['websocket', 'polling'])
        sio.wait()
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
