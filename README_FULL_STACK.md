# ExpertEase - Full Stack

Python Flask backend + Web (Vite+React) + Mobile (React Native/Expo).

## Quick Start

### 1. Backend
```bash
python app.py
```
Runs on http://localhost:5000

### 2. Web Frontend
```bash
cd frontend
npm install
npm run dev
```
Runs on http://localhost:5173

### 3. Mobile App
```bash
cd mobile
npm install
npx expo start
```
Press `a` (Android) or `i` (iOS). For physical device, edit `mobile/src/config.js` with your machine IP.

## Structure

- `app.py` - Flask API (auth, doctors, appointments, AI care)
- `frontend/` - Vite + React (JSX) web app
- `mobile/` - React Native (Expo) mobile app

Both frontend and mobile use the same backend APIs.
