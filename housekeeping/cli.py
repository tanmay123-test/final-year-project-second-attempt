import sys
import os
import argparse
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from housekeeping.arrival.backend.services.arrival_service import ArrivalService
from housekeeping.provider.backend.services.auth_service import ProviderAuthService
from housekeeping.models.database import housekeeping_db

def main():
    parser = argparse.ArgumentParser(description="ExpertEase Housekeeping CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Service Commands
    services_parser = subparsers.add_parser("list-services", help="List all available cleaning services")

    # Provider Commands
    provider_parser = subparsers.add_parser("provider-status", help="Check provider status")
    provider_parser.add_argument("--email", required=True, help="Provider email")

    # Booking Commands
    booking_parser = subparsers.add_parser("list-bookings", help="List bookings for a user")
    booking_parser.add_argument("--user-id", required=True, help="User ID")

    availability_parser = subparsers.add_parser("check-availability", help="Check worker availability")
    availability_parser.add_argument("--service-type", required=True)
    availability_parser.add_argument("--date", required=True)
    availability_parser.add_argument("--time", required=True)
    availability_parser.add_argument("--address", required=False)

    create_booking_parser = subparsers.add_parser("create-booking", help="Create a booking request")
    create_booking_parser.add_argument("--user-id", required=True)
    create_booking_parser.add_argument("--service-type", required=True)
    create_booking_parser.add_argument("--date", required=True)
    create_booking_parser.add_argument("--time", required=True)
    create_booking_parser.add_argument("--address", required=True)

    # DB Init
    db_parser = subparsers.add_parser("init-db", help="Initialize Housekeeping Database")

    args = parser.parse_args()

    if args.command == "list-services":
        # ... existing code ...
        pass
    
    # ... handle new commands ...
    if args.command == "check-availability":
        from housekeeping.services.booking_service import BookingService
        service = BookingService()
        workers = service.check_availability(args.service_type, args.date, args.time, args.address)
        # Convert rows to dicts if needed, assuming check_availability returns dicts
        print(json.dumps(workers, indent=2, default=str))

    elif args.command == "create-booking":
        from housekeeping.services.booking_service import BookingService
        service = BookingService()
        result = service.create_booking_request(args.user_id, args.service_type, args.address, args.date, args.time)
        print(json.dumps(result, indent=2, default=str))

    elif args.command == "list-services":
        service = ArrivalService()
        services = service.get_all_services()
        print(json.dumps(services, indent=2))

    elif args.command == "provider-status":
        from worker_db import WorkerDB
        worker_db = WorkerDB()
        worker = worker_db.get_worker_by_email(args.email)
        if worker:
            print(json.dumps(worker, indent=2))
        else:
            print("Provider not found")

    elif args.command == "list-bookings":
        db = housekeeping_db
        bookings = db.get_user_bookings(args.user_id)
        print(json.dumps(bookings, indent=2))

    elif args.command == "init-db":
        print("Initializing database...")
        # housekeeping_db __init__ calls _create_tables
        print("Database initialized at", housekeeping_db.db_path)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
