# Housekeeping Module

This module provides a dedicated home service management system, isolated from the main healthcare logic of ExpertEase.

## Structure

- **controllers/**: Contains Flask blueprints and route handlers (`booking_controller.py`).
- **services/**: Contains business logic (`booking_service.py`).
- **models/**: Contains database schemas and helper methods (`database.py`).
- **tests/**: Contains unit tests for the module.
- **utils/**: Helper functions (currently shared with main app, but module-specific utils can go here).

## Database

The module uses a separate SQLite database file `housekeeping.db` (configured in `config.py` as `HOUSEKEEPING_DB`).
It interacts with the main `users` and `workers` tables via logical references (foreign keys are conceptual as they reside in different DB files/tables managed by different classes).

### Tables
- **services**: Stores service types (e.g., General Cleaning) and base prices.
- **bookings**: Stores booking records with status, user_id, worker_id, etc.
- **worker_status**: Tracks worker online/offline status.

## API Endpoints

All endpoints are prefixed with `/housekeeping`.

### User Endpoints
- `GET /services`: List available services.
- `POST /book`: Check availability and get price estimate.
  - Body: `{ "service_type": "...", "address": "...", "date": "...", "time": "..." }`
- `POST /confirm-booking`: Confirm booking and process payment (mock).
  - Body: `{ "service_type": "...", "address": "...", "date": "...", "time": "...", "payment_method": "..." }`
- `GET /my-bookings`: Get bookings for the logged-in user.

### Worker Endpoints
- `GET /worker/status`: Get current online status.
- `POST /worker/status`: Set online status (`{ "is_online": true/false }`).
- `GET /my-bookings`: Get bookings assigned to the logged-in worker.
- `POST /worker/update-status`: Update booking status (ACCEPTED, IN_PROGRESS, COMPLETED).

## Authentication

Uses the main application's JWT authentication.
- Users must have `role='user'`.
- Workers must have `role='worker'`.

## Geographic Validation

Worker availability is checked against the user's address. If a worker has a `location` set in their profile, it must match (substring case-insensitive) the user's booking address.

## Testing

Run tests using:
```bash
python housekeeping/tests/test_housekeeping.py
```
