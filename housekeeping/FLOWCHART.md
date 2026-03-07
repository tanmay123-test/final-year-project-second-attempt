# Housekeeping Service Flowchart

## User Journey: Booking a Service

```mermaid
graph TD
    A[User Login] --> B[Arrival Site Home /housekeeping/home]
    B --> C{Select Service Category}
    C -->|Full Home| D[Service Details & Pricing]
    C -->|Kitchen| D
    C -->|Bathroom| D
    D --> E[Select Date & Time]
    E --> F[Review Booking]
    F --> G[Confirm & Pay]
    G --> H[Booking Created (Status: Pending)]
    H --> I[Notify Workers]
```

## Worker Journey: Accepting & Fulfilling Request

```mermaid
graph TD
    A[Worker Login] --> B[Provider Dashboard /worker/housekeeping/dashboard]
    B --> C{New Request Notification}
    C -->|View Details| D[Accept or Reject]
    D -->|Reject| B
    D -->|Accept| E[Job Assigned (Status: Confirmed)]
    E --> F[Navigate to Location]
    F --> G[Start Job (Status: In Progress)]
    G --> H[Complete Job (Status: Completed)]
    H --> I[Payment Release]
```

## Service Time Requirements

| Service Category | Base Time | Price (₹) | Icon |
|------------------|-----------|-----------|------|
| Full Home Deep Cleaning | 4 hours (240m) | 1499 | 🏠 |
| Kitchen Deep Cleaning | 2 hours (120m) | 899 | 🍳 |
| Bathroom Cleaning | 1 hour (60m) | 499 | 🚿 |
| Sofa & Carpet Cleaning | 1.5 hours (90m) | 799 | 🛋️ |

## Complete Lifecycle

1.  **Request**: User selects service -> System checks availability -> User pays/confirms.
2.  **Assignment**: Request broadcast to workers -> Worker accepts -> User notified.
3.  **Service**: Worker arrives -> OTP Verification (Optional) -> Start Timer.
4.  **Completion**: Worker marks complete -> User rates service -> Invoice generated.
