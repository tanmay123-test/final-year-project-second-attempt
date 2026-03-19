
# Database Configuration
# All databases are organized under backend/database/databases/

DATABASE_CONFIG = {
    # Central Databases (shared across all services)
    "USER_DB": "backend/database/databases/users.db",
    "WORKER_DB": "backend/database/databases/workers.db",
    
    # Service-Specific Databases
    "HEALTHCARE_DB": "backend/database/databases/healthcare.db",
    "HOUSEKEEPING_DB": "backend/database/databases/housekeeping.db", 
    "FREELANCE_DB": "backend/database/databases/freelance.db",
    "MONEY_MANAGEMENT_DB": "backend/database/databases/money_management.db",
    "CAR_SERVICE_DB": "backend/database/databases/car_service.db",
    
    # Car Service Worker Databases (3 separate as requested)
    "MECHANICS_DB": "backend/database/databases/car_service_workers/mechanics.db",
    "FUEL_DELIVERY_DB": "backend/database/databases/car_service_workers/fuel_delivery.db", 
    "TOW_TRUCK_DB": "backend/database/databases/car_service_workers/tow_truck.db"
}

# Database Connection Helper
def get_db_connection(db_type):
    """Get database connection based on type"""
    import sqlite3
    return sqlite3.connect(DATABASE_CONFIG[db_type])
