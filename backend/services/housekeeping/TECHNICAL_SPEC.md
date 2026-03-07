# Housekeeping Platform Technical Specification

## 1. Overview
This document outlines the technical architecture, user journeys, and system workflows for the ExpertEase Housekeeping platform. It covers the end-to-end lifecycle of a housekeeping service request, from user registration to job completion and payment.

## 2. User Registration & Login Flow

### 2.1 Customer (User)
*   **Flow**: Sign Up -> Email Verification (Mock) -> Profile Creation -> Login
*   **Fields**:
    *   `username` (Required, Unique)
    *   `email` (Required, Unique, Valid Email Format)
    *   `password` (Required, Min 8 chars, hashed via bcrypt)
    *   `phone` (Optional, for notifications)
    *   `address` (Required for service location)
*   **Validation**:
    *   Frontend: React Hook Form with Zod schema validation.
    *   Backend: Unique constraint checks on DB, Regex for email.

### 2.2 Worker (Provider)
*   **Flow**: Sign Up -> Profile Creation (Service Selection) -> Admin Approval -> Login
*   **Fields**:
    *   `email`, `password`, `phone` (Standard)
    *   `service_type` (Enum: 'housekeeping', 'healthcare', etc.)
    *   `specialization` (e.g., 'Deep Cleaning', 'Pest Control')
    *   `experience_years` (Integer)
    *   `location` (Base of operations)
    *   `documents` (Upload for verification - Future)
*   **State**: `status` enum (`PENDING`, `APPROVED`, `REJECTED`). Only `APPROVED` workers can log in.

## 3. Dashboard & Navigation

### 3.1 Customer Interface (`/housekeeping/*`)
*   **Home (`/housekeeping/home`)**:
    *   **Components**: Service Categories Grid, Upcoming Bookings Widget, Top Rated Cleaners Carousel.
    *   **Navigation**: Bottom/Side Nav (Home, Bookings, Profile, AI Chat).
*   **Booking History (`/housekeeping/bookings`)**:
    *   Tabs: `Upcoming`, `Completed`, `Cancelled`.
    *   Actions: "Track Worker", "Cancel Booking", "Rate Service".

### 3.2 Worker Interface (`/worker/housekeeping/*`)
*   **Dashboard (`/worker/dashboard`)**:
    *   **Components**: Earnings Summary (Daily/Weekly), Availability Toggle (Online/Offline), New Request Cards.
    *   **Logic**: `GET /housekeeping/worker/status` for online/offline state.
*   **Schedule (`/worker/schedule`)**:
    *   **Components**: List of upcoming jobs with date, time, and address.
    *   **Status**: `ACCEPTED` (Upcoming), `IN_PROGRESS` (Active), `COMPLETED` (History).
*   **Earnings (`/worker/earnings`)**:
    *   **Components**: Total Balance card, Transaction History list.
*   **Profile (`/worker/profile`)**:
    *   **Components**: Personal details, Specializations list, Sign Out.
*   **Request Management**:
    *   **New Request**: Pop-up/Card with "Accept" and "Decline" buttons.
    *   **Active Job (in Schedule)**: Live tracking view with "Start Job" and "Complete Job" actions.

## 4. Job Posting Workflow

### 4.1 Service Selection
*   **Endpoint**: `GET /housekeeping/services`
*   **Data**: Returns list of services with `base_price` and `base_duration`.
*   **UI**: Cards with icons and descriptions.

### 4.2 Scheduling
*   **Input**: Date Picker (Calendar), Time Picker (Slots).
*   **Validation**:
    *   Cannot book in the past.
    *   Slot availability check against `bookings` table.

### 4.3 Pricing & Address
*   **Input**: Service Address (Auto-filled from profile, editable).
*   **Calculation**: `Total = Base Price + (Extra Hours * Rate) + Tax`.
*   **Endpoint**: `POST /housekeeping/check-availability` (Returns price estimate and availability).

## 5. Worker Availability System

### 5.1 Status Management
*   **Database**: `worker_status` table (`worker_id`, `is_online`, `last_updated`).
*   **Worker Action**: Toggle switch on Dashboard calls `POST /housekeeping/worker/status`.
*   **Logic**:
    *   `is_online=True`: Worker is visible in search/matching.
    *   `is_online=False`: Worker is excluded from new requests (but keeps scheduled jobs).

### 5.2 Customer View
*   **Real-time**: "Available Workers" count shown on Service Selection.
*   **Matching**: Only `is_online` workers are considered for immediate booking requests.

## 6. Job Matching Algorithm

### 6.1 Logic
The system uses a tiered matching approach:
1.  **Availability Filter**: Filter workers where `is_online=True` AND `no_conflicting_booking`.
2.  **Location Filter**:
    *   Exact Match: Worker `location` == Booking `address` (City/Area level).
    *   Radius Match (Future): Within 10km radius using Geospatial query.
3.  **Specialization Match**: Worker `specialization` matches `service_type` (or generic 'Housekeeping').
4.  **Ranking**:
    *   Primary: Distance (Closer is better).
    *   Secondary: Rating (Higher is better).

### 6.2 Conflict Resolution
*   Query `bookings` table: `WHERE worker_id = ? AND date = ? AND time = ? AND status IN ('ACCEPTED', 'IN_PROGRESS')`.
*   If count > 0, worker is excluded.

## 7. Worker Acceptance Flow

### 7.1 Notification
*   **System**: Push Notification (FCM/Socket.io) or Polling.
*   **Event**: New Booking created with status `PENDING` (or `ASSIGNED` if auto-assigned).

### 7.2 Action
*   **Accept**:
    *   Endpoint: `POST /housekeeping/worker/update-status` (`status='ACCEPTED'`).
    *   Result: Booking confirmed, User notified.
*   **Reject**:
    *   Endpoint: `POST /housekeeping/worker/update-status` (`status='DECLINED'`).
    *   Result: System triggers `reassign_worker` to find the next best candidate.

## 8. In-App Messaging (Proposed)

### 8.1 Requirements
*   **Scope**: Direct chat between Customer and Assigned Worker.
*   **Lifecycle**: Chat opens when status is `ACCEPTED`, closes 24h after `COMPLETED`.

### 8.2 Implementation
*   **DB Schema**: `messages` (`id`, `booking_id`, `sender_id`, `content`, `timestamp`, `read_status`).
*   **API**:
    *   `GET /messages/{booking_id}`: History.
    *   `POST /messages`: Send message.
    *   `WS /chat`: Real-time socket connection.

## 9. Job Status Tracking

### 9.1 State Machine
1.  **REQUESTED (PENDING)**: User creates booking. System looks for worker.
2.  **ASSIGNED**: System tentatively assigns a worker (waiting for acceptance).
3.  **ACCEPTED**: Worker confirms. User notified "Cleaner is on the way".
4.  **IN_PROGRESS**: Worker scans QR code/clicks "Start". Timer starts.
5.  **COMPLETED**: Worker finishes. Payment triggered.
6.  **PAID**: Payment successful.
7.  **CANCELLED**: User or Worker cancels (before start).

### 9.2 Visualization
*   **Customer**: Progress Stepper (Requested -> Confirmed -> Arrived -> Done).
*   **Worker**: Action Buttons (Accept -> Start -> Complete).

## 10. Payment Gateway Integration

### 10.1 Flow
1.  **Authorization**: On Booking Confirmation, hold funds (pre-auth).
2.  **Release**: On `COMPLETED` status, capture funds.
3.  **Transfer**: Credit `worker_wallet` (Platform fee deducted).

### 10.2 Dispute Resolution
*   **Hold**: If User reports issue within 1 hour of completion, payment is held.
*   **Admin Review**: Admin checks chat/photos and decides (Refund/Release).

## 11. Rating & Review System

### 11.1 Implementation
*   **DB**: Columns in `bookings` table (`rating` 1-5, `review` text).
*   **Trigger**: Modal prompt after `COMPLETED` status.
*   **Calculation**: Worker's average rating updated asynchronously.

## 12. Admin Panel Features

### 12.1 User Management
*   List all Users/Workers.
*   Approve/Reject new Worker registrations.
*   Ban/Suspend users.

### 12.2 Analytics
*   Total Bookings (Daily/Monthly).
*   Revenue (Platform Fee).
*   Active vs Offline Workers.

### 12.3 Dispute Center
*   List of flagged bookings.
*   Resolution actions (Refund User, Pay Worker).

## 13. Error Handling Scenarios

### 13.1 No Available Workers
*   **Scenario**: User tries to book but `check_availability` returns empty.
*   **Action**: Return 404 with `retry: true`. UI suggests "Try a different time".

### 13.2 Payment Failure
*   **Scenario**: Card declined during completion capture.
*   **Action**: Status `PAYMENT_FAILED`. User prompted to update payment method. Worker paid by platform insurance (optional business rule).

### 13.3 Cancellations
*   **User Cancel**:
    *   > 24h: Full Refund.
    *   < 24h: Cancellation Fee.
*   **Worker Cancel**:
    *   System immediately reassigns.
    *   Worker penalized (rating drop).

---

## Appendix: Database Schema (SQLite)

```sql
CREATE TABLE services (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    base_price REAL,
    description TEXT
);

CREATE TABLE bookings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    worker_id INTEGER,
    service_type TEXT,
    address TEXT,
    booking_date TEXT,
    time_slot TEXT,
    status TEXT DEFAULT 'PENDING', -- PENDING, ASSIGNED, ACCEPTED, IN_PROGRESS, COMPLETED, CANCELLED
    price REAL,
    created_at TEXT,
    completed_at TEXT,
    rating INTEGER,
    review TEXT
);

CREATE TABLE worker_status (
    worker_id INTEGER PRIMARY KEY,
    is_online INTEGER DEFAULT 0,
    last_updated TEXT
);
```

## Appendix: API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| GET | `/housekeeping/services` | List available services |
| POST | `/housekeeping/book` | Check availability & price |
| POST | `/housekeeping/confirm-booking` | Create booking |
| GET | `/housekeeping/my-bookings` | User/Worker booking history |
| POST | `/housekeeping/worker/status` | Toggle Online/Offline |
| POST | `/housekeeping/worker/update-status` | Accept/Start/Complete Job |
