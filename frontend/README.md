# ExpertEase Frontend

This is the React frontend for the ExpertEase application.

## Prerequisites

- Node.js installed
- Backend running on `http://127.0.0.1:5000`

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open your browser at `http://localhost:5173`

## Features

- **User Authentication**: Login, Signup, OTP Verification.
- **Dashboard**: View appointments and status.
- **Find Doctors**: Search doctors by name or specialization.
- **Booking**: Book Clinic or Video appointments.
- **Responsive Design**: Works on mobile and desktop.

## Project Structure

- `src/components`: Reusable UI components (Navbar, etc.)
- `src/pages`: Route components (Login, Dashboard, etc.)
- `src/services`: API integration (Axios)
- `src/context`: State management (AuthContext)
