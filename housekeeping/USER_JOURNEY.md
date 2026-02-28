# Housekeeping Module: User & Worker Journey Documentation

## 1. Overview
This document outlines the complete user journey for the Housekeeping module, covering both the **Customer (Arrival)** and **Worker (Provider)** interfaces. It details the operational mechanics, time allocations, and integration points.

---

## 2. Customer Journey (Arrival Site)

### Phase 1: Access & Discovery
1.  **Login/Entry**:
    - User logs in via the main application (`/login`).
    - Upon successful authentication, user navigates to the Housekeeping section (`/housekeeping/home`).
    - **UI**: Violet-themed Home Page with "Welcome back", upcoming bookings, and service categories.

2.  **Service Exploration**:
    - **Home Page**: Displays quick access to "Full Home", "Kitchen", "Bathroom" services.
    - **AI Assistant**: Users can chat with "AI Home Assistant" (`/housekeeping/ai-chat`) to get personalized recommendations based on home size and needs.
    - **Top Cleaners**: Users can view highly-rated professionals directly.

### Phase 2: Booking Process (The Mechanics)
The booking process is a linear 3-step flow (`/housekeeping/booking/create`):

#### Step 1: Service Selection
- **Input**: User selects a specific service category.
- **Data Presented**:
  - Service Name (e.g., "Full Home Deep Cleaning")
  - Base Price (e.g., ₹1499)
  - **Base Time Allocation** (Critical for scheduling).

#### Step 2: Scheduling & Time Allocation
- **Mechanism**:
  - User selects a Date.
  - User selects a Time Slot (e.g., 10:00 AM).
  - **System Calculation**: The system calculates the "End Time" based on the Service's Base Time.
  - **Constraint**: System prevents booking if the slot overlaps with existing bookings (future implementation).

| Service Type | Base Time Allocation | Notes |
| :--- | :--- | :--- |
| **Full Home Deep Cleaning** | **4 Hours** | Comprehensive cleaning including floor, dusting, cobwebs. |
| **Kitchen Deep Cleaning** | **2 Hours** | Oil stain removal, cabinets, appliances. |
| **Bathroom Cleaning** | **1 Hour** | Tiles, sanitary ware, descaling. |
| **Sofa & Carpet Cleaning** | **1.5 Hours** | Shampooing and vacuuming. |

#### Step 3: Confirmation & Payment
- **Review**: User sees a summary: Service, Date, Time, Duration, Price.
- **Action**: User clicks "Confirm & Pay".
- **Outcome**: 
  - Booking status set to `PENDING`.
  - Notification sent to matching workers.
  - User redirected to Home.

---

## 3. Worker Journey (Provider Site)

### Phase 1: Dashboard & Availability
1.  **Login**: Worker logs in (`/worker/housekeeping/login`).
2.  **Dashboard (`/worker/dashboard`)**:
    - **Toggle**: Worker switches "Online/Offline" status.
    - **Stats**: View Daily Earnings, Jobs Completed, Rating.
    - **New Requests**: View and Accept/Decline incoming job requests.
    - **Navigation**: Bottom navigation bar with Dashboard, Schedule, Earnings, Profile.

### Phase 2: Schedule & Management
1.  **Schedule (`/worker/schedule`)**:
    - View upcoming jobs with details (Service, Date, Time, Address, Price).
    - Status tracking: Accepted, Completed, Cancelled.
2.  **Earnings (`/worker/earnings`)**:
    - View Total Balance.
    - Transaction History with dates and amounts.
3.  **Profile (`/worker/profile`)**:
    - View personal details (Name, Phone, Email).
    - View Specializations (e.g., Deep Cleaning, Kitchen).
    - Sign Out functionality.

### Phase 3: Job Fulfillment
1.  **Receiving Requests**:
    - **Trigger**: Customer confirms a booking.
    - **Display**: "New Requests" section on Dashboard shows incoming jobs with:
      - Service Type
      - Location (Distance/Address)
      - Price (Earnings)
      - Time & Duration
2.  **Action**:
    - **Accept**: Job status updates to `ACCEPTED`. Job moves to Schedule. Customer notified.
    - **Decline**: Request removed from this worker's view.

3.  **Job Execution (Lifecycle)**:
    - **Start**: Worker arrives -> Clicks "Start Job" (from Schedule/Dashboard).
    - **In Progress**: Timer runs.
    - **Complete**: Worker clicks "Complete Job".
    - **Rating**: Worker rates customer (optional), Customer rates worker.

---

## 4. Integration & Data Flow

### Booking Lifecycle Flowchart

```mermaid
graph TD
    A[Customer: Selects Service] --> B[Customer: Selects Date/Time]
    B --> C{Slot Available?}
    C -- No --> B
    C -- Yes --> D[Customer: Confirms Booking]
    D -->|Create Record (Status: PENDING)| E[Backend Database]
    E -->|Push Notification| F[Worker Dashboard]
    F --> G{Worker Action}
    G -- Reject --> H[Find Next Worker]
    H --> F
    G -- Accept --> I[Update Status: ACCEPTED]
    I --> J[Notify Customer]
    I --> K[Job Scheduled]
    K --> L[Worker: Start Job]
    L --> M[Worker: Complete Job]
    M --> N[Payment Processing]
    N --> O[Update Stats & History]
```

### Operational Mechanics
- **Shared Data**: 
  - `Booking ID`: The central key linking Customer View (`UserBookings.jsx`) and Worker View (`ProviderDashboard.jsx`).
  - `Status`: 
    - `PENDING` (Visible to Worker as Request)
    - `ACCEPTED` (Visible to User as Upcoming)
    - `COMPLETED` (History)
- **Time Management**:
  - Workers cannot accept overlapping jobs based on `StartTime` + `Duration`.

---

## 5. Technical Implementation Status
- **Frontend (User)**: Implemented Home, AI Chat, Booking Flow, Profile.
- **Frontend (Worker)**: Implemented Dashboard with Request Management.
- **Routing**: Integrated into main `App.jsx` with Protection.
- **Next Steps**: Connect Backend APIs to replace Mock Data.
