# 🚀 How to Fix the AI Mechanic CORS Error

## Problem
The CORS error occurs because the backend server isn't running or can't be reached by the frontend.

## Solution Steps

### 1. Start the Backend Server

**Option A: Using the startup script (Recommended)**
```bash
cd backend
python start_server.py
```

**Option B: Direct Flask run**
```bash
cd backend
python app.py
```

**Option C: Using Python module**
```bash
cd backend
python -m flask run --host=127.0.0.1 --port=5000
```

### 2. Verify Server is Running

You should see output like:
```
🚀 Starting ExpertEase Backend Server...
📍 Location: http://127.0.0.1:5000
🔧 AI Mechanic Endpoint: http://127.0.0.1:5000/api/ai/mechanic-diagnosis
⏳ Server starting...
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 3. Test the AI Mechanic Endpoint

Open a new terminal and test:
```bash
curl -X POST http://127.0.0.1:5000/api/ai/mechanic-diagnosis \
  -H "Content-Type: application/json" \
  -d '{"symptoms": "My check engine light is on", "user_id": "test"}'
```

### 4. Start the Frontend

In another terminal:
```bash
cd frontend
npm run dev
```

### 5. Test the AI Mechanic

1. Navigate to `/car-service/ai-mechanic`
2. Type a car issue like "My check engine light is on"
3. The AI should respond with diagnostic advice

## 🔧 Troubleshooting

### If server won't start:
- Make sure you're in the `backend` directory
- Check Python version (3.7+ recommended)
- Install dependencies: `pip install flask flask-cors`

### If CORS still occurs:
- Verify the backend is actually running
- Check the port (should be 5000)
- Try accessing `http://127.0.0.1:5000` in browser

### If AI responses are generic:
- The fallback to healthcare AI is working
- This means the mechanic-specific endpoint isn't reachable
- Check server logs for any errors

## 🎯 Expected Results

Once working, you should see:
- ✅ No more CORS errors
- ✅ Real-time AI responses
- ✅ Car-specific diagnostic advice
- ✅ Emergency warnings for serious issues

##  📞 Quick Test Messages to Try

- "My check engine light is on"
- "My car won't start"
- "I hear a squealing noise when braking"
- "My car is overheating"
- "My battery is dead"

Each should get detailed, car-specific responses!
