# **AI Agent Context: Expertease Project**

This document provides technical context for AI agents working on this codebase.

## **Tech Stack Summary**
- **Backend**: Python (Flask)
- **Frontend**: React (Vite, Javascript)
- **Real-time**: Socket.io
- **AI**: Google Gemini (google-generativeai)
- **Payments**: Razorpay
- **Auth**: Token-based (JWT) + OTP (Email)

## **Key Architecture Patterns**
1. **Blueprint-based Modularity**: The backend is split into services (e.g., `car_service`, `freelance`, `housekeeping`). Each has its own routes, controllers, and database logic.
2. **Context-Driven State**: The frontend uses `AuthContext` for user sessions and `ToastContext` for notifications.
3. **Distributed Data**: Each major module often maintains its own SQLite database (e.g., `user_db.py`, `expert_db.py`).
4. **Service Bridges**: The `ai` module acts as a central hub for all Gemini-related tasks, providing a clean API for other services to use.

## **Developer Workflows**
- **Adding a Route**: Define a new Blueprint in the service directory and register it in `backend/app.py`.
- **Adding a Page**: Create the component in `frontend/src/services/[service]/pages/` and add the route to `frontend/src/App.jsx`.
- **Modifying UI**: Check `frontend/src/index.css` for global variables before editing local component styles.

## **Commonly Used Files**
- `backend/app.py`: Main configuration and blueprint registry.
- `frontend/src/App.jsx`: Main routing table.
- `frontend/src/shared/api.js`: Base API configuration.
- `backend/ai/gemini_client.py`: Core AI interface.

## **System Constraints**
- The project uses multiple ports for different service instances (5173, 5174, etc.).
- Ensure CORS configurations in `app.py` are updated when adding new frontend entry points.
- SQLite databases are expected to be in the `backend/` root or specific service folders.
