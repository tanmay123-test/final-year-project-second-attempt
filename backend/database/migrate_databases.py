#!/usr/bin/env python3
"""
Migrate data from scattered databases to organized structure
"""

import sqlite3
import os
import json
from pathlib import Path
from datetime import datetime

def migrate_all_databases():
    """Migrate all scattered databases to organized structure"""
    
    print("  Starting Database Migration...")
    
    # Source databases (scattered)
    source_dbs = {
        "users": ["expertease.db", "data/users.db"],
        "workers": ["worker_db.py", "data/workers.db", "housekeeping/housekeeping.db"],
        "healthcare": ["data/healthcare.db"],
        "housekeeping": ["data/housekeeping.db"],
        "freelance": ["data/freelance.db"],
        "money_management": ["data/money_management.db", "money_service.db"],
        "car_service": ["data/car_fuel_delivery.db", "data/car_jobs.db", "data/car_mechanics.db", "data/car_profiles.db", "data/car_truck_operators.db"],
        "car_service_workers": {
            "mechanics": ["data/car_mechanics.db", "car_service/mechanics.db"],
            "fuel_delivery": ["data/car_fuel_delivery.db", "car_service/fuel_delivery.db"],
            "tow_truck": ["data/car_truck_operators.db", "car_service/truck_operators.db"]
        }
    }
    
    # Target databases (organized)
    target_base = Path("backend/database/databases")
    
    # 1. Migrate Users
    migrate_users(source_dbs["users"], target_base / "users.db")
    
    # 2. Migrate Workers  
    migrate_workers(source_dbs["workers"], target_base / "workers.db")
    
    # 3. Migrate Service Databases
    for service in ["healthcare", "housekeeping", "freelance", "money_management", "car_service"]:
        migrate_service_data(service, target_base / f"{service}.db")
    
    # 4. Migrate Car Service Workers
    for worker_type in ["mechanics", "fuel_delivery", "tow_truck"]:
        migrate_car_workers(worker_type, target_base / "car_service_workers" / f"{worker_type}.db")
    
    print("  Migration completed successfully!")

def migrate_users(source_dbs, target_db):
    """Migrate user data to central users database"""
    print(f"\n  Migrating Users...")
    
    conn_target = sqlite3.connect(target_db)
    cursor_target = conn_target.cursor()
    
    migrated_users = 0
    
    for source_db in source_dbs:
        if os.path.exists(source_db):
            try:
                conn_source = sqlite3.connect(source_db)
                cursor_source = conn_source.cursor()
                
                # Try to find users table
                cursor_source.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%user%'")
                user_tables = cursor_source.fetchall()
                
                for table in user_tables:
                    table_name = table[0]
                    try:
                        cursor_source.execute(f"SELECT * FROM {table_name}")
                        users = cursor_source.fetchall()
                        
                        for user in users:
                            # Map columns to new schema
                            user_data = map_user_columns(user, cursor_source, table_name)
                            if user_data:
                                cursor_target.execute('''
                                    INSERT OR REPLACE INTO users 
                                    (email, password, name, phone, created_at, is_active)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                ''', user_data)
                                migrated_users += 1
                                
                    except Exception as e:
                        print(f"      Error migrating from {table_name}: {e}")
                
                conn_source.close()
                
            except Exception as e:
                print(f"      Error opening {source_db}: {e}")
    
    conn_target.commit()
    conn_target.close()
    print(f"    Migrated {migrated_users} users")

def migrate_workers(source_dbs, target_db):
    """Migrate worker data to central workers database"""
    print(f"\n  Migrating Workers...")
    
    conn_target = sqlite3.connect(target_db)
    cursor_target = conn_target.cursor()
    
    migrated_workers = 0
    
    for source_db in source_dbs:
        if os.path.exists(source_db):
            try:
                conn_source = sqlite3.connect(source_db)
                cursor_source = conn_source.cursor()
                
                # Try to find worker tables
                cursor_source.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%worker%' OR name LIKE '%mechanic%' OR name LIKE '%doctor%'")
                worker_tables = cursor_source.fetchall()
                
                for table in worker_tables:
                    table_name = table[0]
                    try:
                        cursor_source.execute(f"SELECT * FROM {table_name}")
                        workers = cursor_source.fetchall()
                        
                        for worker in workers:
                            # Map columns to new schema
                            worker_data = map_worker_columns(worker, cursor_source, table_name)
                            if worker_data:
                                cursor_target.execute('''
                                    INSERT OR REPLACE INTO workers 
                                    (email, password, name, phone, service_type, worker_type, is_verified, is_active)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''', worker_data)
                                migrated_workers += 1
                                
                    except Exception as e:
                        print(f"      Error migrating from {table_name}: {e}")
                
                conn_source.close()
                
            except Exception as e:
                print(f"      Error opening {source_db}: {e}")
    
    conn_target.commit()
    conn_target.close()
    print(f"    Migrated {migrated_workers} workers")

def migrate_service_data(service, target_db):
    """Migrate service-specific data"""
    print(f"\n  Migrating {service.replace('_', ' ').title()} data...")
    
    conn_target = sqlite3.connect(target_db)
    cursor_target = conn_target.cursor()
    
    migrated_records = 0
    
    # Find service-specific databases
    service_dbs = []
    if service == "healthcare":
        service_dbs = ["data/healthcare.db"]
    elif service == "housekeeping":
        service_dbs = ["data/housekeeping.db", "housekeeping/housekeeping.db"]
    elif service == "freelance":
        service_dbs = ["data/freelance.db"]
    elif service == "money_management":
        service_dbs = ["data/money_management.db", "money_service.db"]
    elif service == "car_service":
        service_dbs = ["data/car_fuel_delivery.db", "data/car_jobs.db", "data/car_profiles.db"]
    
    for source_db in service_dbs:
        if os.path.exists(source_db):
            try:
                conn_source = sqlite3.connect(source_db)
                cursor_source = conn_source.cursor()
                
                cursor_source.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor_source.fetchall()
                
                for table in tables:
                    table_name = table[0]
                    try:
                        cursor_source.execute(f"SELECT * FROM {table_name}")
                        records = cursor_source.fetchall()
                        
                        for record in records:
                            # Store as JSON in service-specific table
                            record_json = json.dumps(record)
                            cursor_target.execute(f'''
                                INSERT INTO {table_name} 
                                (service_data, created_at)
                                VALUES (?, ?)
                            ''', (record_json, datetime.now()))
                            migrated_records += 1
                            
                    except Exception as e:
                        print(f"      Error migrating from {table_name}: {e}")
                
                conn_source.close()
                
            except Exception as e:
                print(f"      Error opening {source_db}: {e}")
    
    conn_target.commit()
    conn_target.close()
    print(f"    Migrated {migrated_records} records")

def migrate_car_workers(worker_type, target_db):
    """Migrate car service worker data"""
    print(f"\n  Migrating {worker_type.replace('_', ' ').title()} data...")
    
    conn_target = sqlite3.connect(target_db)
    cursor_target = conn_target.cursor()
    
    migrated_records = 0
    
    # Find worker-specific databases
    if worker_type == "mechanics":
        source_dbs = ["data/car_mechanics.db", "car_service/mechanics.db"]
    elif worker_type == "fuel_delivery":
        source_dbs = ["data/car_fuel_delivery.db", "car_service/fuel_delivery.db"]
    elif worker_type == "tow_truck":
        source_dbs = ["data/car_truck_operators.db", "car_service/truck_operators.db"]
    
    for source_db in source_dbs:
        if os.path.exists(source_db):
            try:
                conn_source = sqlite3.connect(source_db)
                cursor_source = conn_source.cursor()
                
                cursor_source.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor_source.fetchall()
                
                for table in tables:
                    table_name = table[0]
                    try:
                        cursor_source.execute(f"SELECT * FROM {table_name}")
                        records = cursor_source.fetchall()
                        
                        for record in records:
                            # Store as JSON in worker-specific table
                            record_json = json.dumps(record)
                            cursor_target.execute(f'''
                                INSERT INTO {table_name} 
                                (worker_id, {worker_type}_data, status, created_at)
                                VALUES (?, ?, ?, ?)
                            ''', (1, record_json, 'active', datetime.now()))
                            migrated_records += 1
                            
                    except Exception as e:
                        print(f"      Error migrating from {table_name}: {e}")
                
                conn_source.close()
                
            except Exception as e:
                print(f"      Error opening {source_db}: {e}")
    
    conn_target.commit()
    conn_target.close()
    print(f"    Migrated {migrated_records} records")

def map_user_columns(user_data, cursor_source, table_name):
    """Map user data columns to new schema"""
    try:
        cursor_source.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor_source.fetchall()]
        
        # Default values
        email = password = name = phone = None
        created_at = datetime.now()
        is_active = 1
        
        # Map based on column names
        for i, col in enumerate(columns):
            if 'email' in col.lower() and i < len(user_data):
                email = user_data[i]
            elif 'password' in col.lower() and i < len(user_data):
                password = user_data[i]
            elif 'name' in col.lower() and i < len(user_data):
                name = user_data[i]
            elif 'phone' in col.lower() and i < len(user_data):
                phone = user_data[i]
            elif 'created' in col.lower() and i < len(user_data):
                created_at = user_data[i]
        
        if email and password and name:
            return (email, password, name, phone, created_at, is_active)
        
    except Exception as e:
        print(f"        Error mapping user columns: {e}")
    
    return None

def map_worker_columns(worker_data, cursor_source, table_name):
    """Map worker data columns to new schema"""
    try:
        cursor_source.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor_source.fetchall()]
        
        # Default values
        email = password = name = phone = None
        service_type = worker_type = is_verified = is_active = None
        created_at = datetime.now()
        
        # Determine service and worker type from table name
        if 'doctor' in table_name.lower():
            service_type = 'healthcare'
            worker_type = 'doctor'
        elif 'mechanic' in table_name.lower():
            service_type = 'car_service'
            worker_type = 'mechanic'
        elif 'cleaner' in table_name.lower() or 'housekeeping' in table_name.lower():
            service_type = 'housekeeping'
            worker_type = 'cleaner'
        elif 'freelance' in table_name.lower():
            service_type = 'freelance'
            worker_type = 'freelancer'
        
        # Map based on column names
        for i, col in enumerate(columns):
            if 'email' in col.lower() and i < len(worker_data):
                email = worker_data[i]
            elif 'password' in col.lower() and i < len(worker_data):
                password = worker_data[i]
            elif 'name' in col.lower() and i < len(worker_data):
                name = worker_data[i]
            elif 'phone' in col.lower() and i < len(worker_data):
                phone = worker_data[i]
            elif 'verified' in col.lower() and i < len(worker_data):
                is_verified = worker_data[i]
            elif 'active' in col.lower() and i < len(worker_data):
                is_active = worker_data[i]
            elif 'created' in col.lower() and i < len(worker_data):
                created_at = worker_data[i]
        
        if email and password and name and service_type and worker_type:
            return (email, password, name, phone, service_type, worker_type, is_verified or 0, is_active or 1)
        
    except Exception as e:
        print(f"        Error mapping worker columns: {e}")
    
    return None

if __name__ == "__main__":
    migrate_all_databases()
    
    print("\n  Migration Summary:")
    print("  Users migrated to central users.db")
    print("  Workers migrated to central workers.db") 
    print("  Service data migrated to service-specific databases")
    print("  Car service workers migrated to separate databases")
    print("\n  New organized structure:")
    print("      users.db (all users from all services)")
    print("      workers.db (all workers from all services)")
    print("      healthcare.db (healthcare specific)")
    print("      housekeeping.db (housekeeping specific)")
    print("      freelance.db (freelance specific)")
    print("      money_management.db (money management specific)")
    print("      car_service.db (car service specific)")
    print("      car_service_workers/")
    print("          mechanics.db (mechanics only)")
    print("          fuel_delivery.db (fuel delivery only)")
    print("          tow_truck.db (tow truck only)")
