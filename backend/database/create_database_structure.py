#!/usr/bin/env python3
"""
Create Organized Database Structure for All Services
- Central User Database (shared across all 5 services)
- Central Worker Database (shared across all 5 services)
- Service-Specific Databases for each service
- Car Service has 3 separate worker databases as requested
"""

import sqlite3
import os
from pathlib import Path

def create_database_schema():
    """Create organized database structure"""
    
    # Base directory for all databases
    db_base = Path("backend/database/databases")
    db_base.mkdir(parents=True, exist_ok=True)
    
    print("   Creating Organized Database Structure...")
    
    # 1. Central User Database (shared across all 5 services)
    user_db_path = db_base / "users.db"
    create_user_database(user_db_path)
    
    # 2. Central Worker Database (shared across all 5 services)  
    worker_db_path = db_base / "workers.db"
    create_worker_database(worker_db_path)
    
    # 3. Service-Specific Databases
    services = {
        "healthcare": ["appointments", "medical_records", "consultations"],
        "housekeeping": ["bookings", "cleaning_jobs", "schedules"],
        "freelance": ["projects", "proposals", "contracts"],
        "money_management": ["transactions", "budgets", "investments"],
        "car_service": ["vehicle_bookings", "service_records", "customer_requests"]
    }
    
    for service, tables in services.items():
        service_db_path = db_base / f"{service}.db"
        create_service_database(service_db_path, service, tables)
    
    # 4. Car Service Worker Databases (3 separate as requested)
    car_worker_dbs = {
        "mechanics": ["repair_jobs", "expertise_areas", "availability"],
        "fuel_delivery": ["delivery_requests", "fuel_stations", "delivery_logs"],
        "tow_truck": ["tow_requests", "truck_locations", "recovery_logs"]
    }
    
    car_workers_path = db_base / "car_service_workers"
    car_workers_path.mkdir(exist_ok=True)
    
    for worker_type, tables in car_worker_dbs.items():
        worker_db_path = car_workers_path / f"{worker_type}.db"
        create_car_worker_database(worker_db_path, worker_type, tables)
    
    print("  Database structure created successfully!")
    print(f"  Location: {db_base.absolute()}")
    
    return db_base

def create_user_database(db_path):
    """Create central user database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Users table (shared across all services)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # User profiles (shared)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service_type TEXT, -- 'healthcare', 'housekeeping', etc.
            profile_data TEXT, -- JSON data specific to service
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # User sessions (shared)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            token TEXT UNIQUE,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"  Created: {db_path.name}")

def create_worker_database(db_path):
    """Create central worker database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Workers table (shared across all services)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            service_type TEXT NOT NULL, -- 'healthcare', 'housekeeping', etc.
            worker_type TEXT NOT NULL, -- 'doctor', 'mechanic', 'cleaner', etc.
            is_verified BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Worker profiles (shared)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS worker_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER,
            service_type TEXT,
            worker_type TEXT,
            profile_data TEXT, -- JSON data specific to worker type
            documents TEXT, -- JSON array of document paths
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (worker_id) REFERENCES workers (id)
        )
    ''')
    
    # Worker sessions (shared)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS worker_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER,
            token TEXT UNIQUE,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (worker_id) REFERENCES workers (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"  Created: {db_path.name}")

def create_service_database(db_path, service_name, tables):
    """Create service-specific database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Common service tables
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {service_name}_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            worker_id INTEGER,
            service_type TEXT,
            status TEXT DEFAULT 'pending',
            booking_data TEXT, -- JSON data
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {service_name}_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            worker_id INTEGER,
            booking_id INTEGER,
            rating REAL,
            review_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Service-specific tables
    for table in tables:
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    conn.commit()
    conn.close()
    print(f"  Created: {db_path.name}")

def create_car_worker_database(db_path, worker_type, tables):
    """Create car service worker-specific database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Worker-specific tables
    for table in tables:
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id INTEGER,
                {worker_type}_data TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    conn.commit()
    conn.close()
    print(f"  Created: car_service_workers/{db_path.name}")

def create_database_config():
    """Create database configuration file"""
    config_content = '''
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
'''
    
    config_path = Path("backend/database/database_config.py")
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"  Created: database_config.py")

if __name__ == "__main__":
    # Create the organized database structure
    db_base = create_database_schema()
    
    # Create configuration file
    create_database_config()
    
    print("\n  Database Structure Summary:")
    print("      databases/")
    print("          users.db (shared across all 5 services)")
    print("          workers.db (shared across all 5 services)")
    print("          healthcare.db (healthcare specific)")
    print("          housekeeping.db (housekeeping specific)")
    print("          freelance.db (freelance specific)")
    print("          money_management.db (money management specific)")
    print("          car_service.db (car service specific)")
    print("          car_service_workers/")
    print("              mechanics.db (mechanics specific)")
    print("              fuel_delivery.db (fuel delivery specific)")
    print("              tow_truck.db (tow truck specific)")
    print("      database_config.py (configuration helper)")
    
    print("\n  All databases are now properly organized!")
