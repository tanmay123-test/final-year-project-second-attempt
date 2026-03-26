#!/usr/bin/env python3
"""
Enhanced Database Migration Script
Moves all data from scattered databases to organized structure
"""

import sqlite3
import os
import json
from pathlib import Path
from datetime import datetime

def enhanced_migration():
    """Enhanced migration with better error handling"""
    
    print("  Starting Enhanced Database Migration...")
    
    # Source databases (scattered)
    source_paths = {
        'expertease': 'expertease.db',
        'data_users': 'data/users.db',
        'data_workers': 'data/workers.db',
        'healthcare': 'data/healthcare.db',
        'housekeeping': 'data/housekeeping.db',
        'freelance': 'data/freelance.db',
        'money_management': 'data/money_management.db',
        'money_service': 'money_service.db',
        'car_fuel': 'data/car_fuel_delivery.db',
        'car_jobs': 'data/car_jobs.db',
        'car_mechanics': 'data/car_mechanics.db',
        'car_profiles': 'data/car_profiles.db',
        'car_truck': 'data/car_truck_operators.db',
        'car_service_mechanics': 'car_service/mechanics.db',
        'car_service_workers': 'car_service/workers.db',
        'car_service_truck': 'car_service/truck_operators.db',
        'car_service_fuel': 'car_service/fuel_delivery.db',
        'housekeeping_main': 'housekeeping/housekeeping.db'
    }
    
    # Target databases (organized)
    target_base = Path("backend/database/databases")
    
    migrated_stats = {
        'users': 0,
        'workers': 0,
        'healthcare': 0,
        'housekeeping': 0,
        'freelance': 0,
        'money_management': 0,
        'car_service': 0,
        'mechanics': 0,
        'fuel_delivery': 0,
        'tow_truck': 0
    }
    
    # 1. Migrate Users
    migrated_stats['users'] = migrate_users_enhanced(source_paths)
    
    # 2. Migrate Workers
    migrated_stats['workers'] = migrate_workers_enhanced(source_paths)
    
    # 3. Migrate Service Data
    migrated_stats['healthcare'] = migrate_service_data_enhanced('healthcare', source_paths, target_base)
    migrated_stats['housekeeping'] = migrate_service_data_enhanced('housekeeping', source_paths, target_base)
    migrated_stats['freelance'] = migrate_service_data_enhanced('freelance', source_paths, target_base)
    migrated_stats['money_management'] = migrate_service_data_enhanced('money_management', source_paths, target_base)
    migrated_stats['car_service'] = migrate_service_data_enhanced('car_service', source_paths, target_base)
    
    # 4. Migrate Car Service Workers
    migrated_stats['mechanics'] = migrate_car_workers_enhanced('mechanics', source_paths, target_base)
    migrated_stats['fuel_delivery'] = migrate_car_workers_enhanced('fuel_delivery', source_paths, target_base)
    migrated_stats['tow_truck'] = migrate_car_workers_enhanced('tow_truck', source_paths, target_base)
    
    print_migration_summary(migrated_stats)
    
    return migrated_stats

def migrate_users_enhanced(source_paths):
    """Enhanced user migration"""
    print(f"\n  Enhanced User Migration...")
    
    users_migrated = 0
    target_db = "backend/database/databases/users.db"
    
    conn_target = sqlite3.connect(target_db)
    cursor_target = conn_target.cursor()
    
    # Check all possible user databases
    user_sources = [
        source_paths.get('expertease'),
        source_paths.get('data_users'),
        source_paths.get('healthcare'),
        source_paths.get('housekeeping'),
        source_paths.get('freelance'),
        source_paths.get('money_management'),
        source_paths.get('car_service_workers')
    ]
    
    for source_db in user_sources:
        if source_db and os.path.exists(source_db):
            try:
                users_migrated += migrate_from_user_db(source_db, conn_target, cursor_target)
            except Exception as e:
                print(f"      Error migrating from {source_db}: {e}")
    
    conn_target.commit()
    conn_target.close()
    
    print(f"    Total users migrated: {users_migrated}")
    return users_migrated

def migrate_from_user_db(source_db, conn_target, cursor_target):
    """Migrate users from a specific database"""
    users_migrated = 0
    
    try:
        conn_source = sqlite3.connect(source_db)
        cursor_source = conn_source.cursor()
        
        # Get all table names
        cursor_source.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor_source.fetchall()
        
        for table in tables:
            table_name = table[0]
            if 'user' in table_name.lower():
                try:
                    cursor_source.execute(f"SELECT * FROM {table_name}")
                    users = cursor_source.fetchall()
                    
                    cursor_source.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in cursor_source.fetchall()]
                    
                    for user in users:
                        user_data = map_user_data(user, columns)
                        if user_data:
                            cursor_target.execute('''
                                INSERT OR REPLACE INTO users 
                                (email, password, name, phone, created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', user_data)
                            users_migrated += 1
                            
                except Exception as e:
                    print(f"        Error migrating table {table_name}: {e}")
        
        conn_source.close()
        
    except Exception as e:
        print(f"      Error opening {source_db}: {e}")
    
    return users_migrated

def map_user_data(user_data, columns):
    """Map user data to new schema"""
    try:
        email = password = name = phone = None
        created_at = datetime.now()
        
        for i, col in enumerate(columns):
            if i < len(user_data):
                if 'email' in col.lower():
                    email = user_data[i]
                elif 'password' in col.lower():
                    password = user_data[i]
                elif 'name' in col.lower():
                    name = user_data[i]
                elif 'phone' in col.lower():
                    phone = user_data[i]
                elif 'created' in col.lower() and user_data[i]:
                    created_at = user_data[i]
        
        if email and password and name:
            return (email, password, name, phone, created_at, created_at)
        
    except Exception as e:
        print(f"        Error mapping user data: {e}")
    
    return None

def migrate_workers_enhanced(source_paths):
    """Enhanced worker migration"""
    print(f"\n  Enhanced Worker Migration...")
    
    workers_migrated = 0
    target_db = "backend/database/databases/workers.db"
    
    conn_target = sqlite3.connect(target_db)
    cursor_target = conn_target.cursor()
    
    # Check all possible worker databases
    worker_sources = [
        source_paths.get('data_workers'),
        source_paths.get('healthcare'),
        source_paths.get('housekeeping'),
        source_paths.get('freelance'),
        source_paths.get('money_management'),
        source_paths.get('car_service_workers'),
        source_paths.get('car_service_mechanics'),
        source_paths.get('car_service_truck'),
        source_paths.get('car_service_fuel')
    ]
    
    for source_db in worker_sources:
        if source_db and os.path.exists(source_db):
            try:
                workers_migrated += migrate_from_worker_db(source_db, conn_target, cursor_target)
            except Exception as e:
                print(f"      Error migrating from {source_db}: {e}")
    
    conn_target.commit()
    conn_target.close()
    
    print(f"    Total workers migrated: {workers_migrated}")
    return workers_migrated

def migrate_from_worker_db(source_db, conn_target, cursor_target):
    """Migrate workers from a specific database"""
    workers_migrated = 0
    
    try:
        conn_source = sqlite3.connect(source_db)
        cursor_source = conn_source.cursor()
        
        # Get all table names
        cursor_source.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor_source.fetchall()
        
        for table in tables:
            table_name = table[0]
            if any(keyword in table_name.lower() for keyword in ['worker', 'doctor', 'mechanic', 'cleaner', 'freelance']):
                try:
                    cursor_source.execute(f"SELECT * FROM {table_name}")
                    workers = cursor_source.fetchall()
                    
                    cursor_source.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in cursor_source.fetchall()]
                    
                    for worker in workers:
                        worker_data = map_worker_data(worker, columns, table_name)
                        if worker_data:
                            cursor_target.execute('''
                                INSERT OR REPLACE INTO workers 
                                (email, password, name, phone, service_type, worker_type, is_verified, is_active, created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', worker_data)
                            workers_migrated += 1
                            
                except Exception as e:
                    print(f"        Error migrating table {table_name}: {e}")
        
        conn_source.close()
        
    except Exception as e:
        print(f"      Error opening {source_db}: {e}")
    
    return workers_migrated

def map_worker_data(worker_data, columns, table_name):
    """Map worker data to new schema"""
    try:
        email = password = name = phone = None
        service_type = worker_type = None
        is_verified = is_active = 0
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
        elif 'fuel' in table_name.lower():
            service_type = 'car_service'
            worker_type = 'fuel_delivery'
        elif 'truck' in table_name.lower() or 'tow' in table_name.lower():
            service_type = 'car_service'
            worker_type = 'tow_truck'
        
        for i, col in enumerate(columns):
            if i < len(worker_data):
                if 'email' in col.lower():
                    email = worker_data[i]
                elif 'password' in col.lower():
                    password = worker_data[i]
                elif 'name' in col.lower():
                    name = worker_data[i]
                elif 'phone' in col.lower():
                    phone = worker_data[i]
                elif 'verified' in col.lower():
                    is_verified = worker_data[i] or 0
                elif 'active' in col.lower():
                    is_active = worker_data[i] or 1
                elif 'created' in col.lower() and worker_data[i]:
                    created_at = worker_data[i]
        
        if email and password and name and service_type and worker_type:
            return (email, password, name, phone, service_type, worker_type, is_verified, is_active, created_at, created_at)
        
    except Exception as e:
        print(f"        Error mapping worker data: {e}")
    
    return None

def migrate_service_data_enhanced(service_name, source_paths, target_base):
    """Enhanced service data migration"""
    print(f"\n  Enhanced {service_name} Migration...")
    
    records_migrated = 0
    target_db = target_base / f"{service_name}.db"
    
    conn_target = sqlite3.connect(target_db)
    cursor_target = conn_target.cursor()
    
    # Find relevant source databases
    service_sources = []
    if service_name == 'healthcare':
        service_sources = [source_paths.get('healthcare')]
    elif service_name == 'housekeeping':
        service_sources = [source_paths.get('housekeeping'), source_paths.get('housekeeping_main')]
    elif service_name == 'freelance':
        service_sources = [source_paths.get('freelance')]
    elif service_name == 'money_management':
        service_sources = [source_paths.get('money_management'), source_paths.get('money_service')]
    elif service_name == 'car_service':
        service_sources = [
            source_paths.get('car_fuel'),
            source_paths.get('car_jobs'),
            source_paths.get('car_mechanics'),
            source_paths.get('car_profiles'),
            source_paths.get('car_truck')
        ]
    
    for source_db in service_sources:
        if source_db and os.path.exists(source_db):
            try:
                records_migrated += migrate_service_data_from_db(source_db, conn_target, cursor_target, service_name)
            except Exception as e:
                print(f"      Error migrating from {source_db}: {e}")
    
    conn_target.commit()
    conn_target.close()
    
    print(f"    Total {service_name} records migrated: {records_migrated}")
    return records_migrated

def migrate_service_data_from_db(source_db, conn_target, cursor_target, service_name):
    """Migrate service data from a specific database"""
    records_migrated = 0
    
    try:
        conn_source = sqlite3.connect(source_db)
        cursor_source = conn_source.cursor()
        
        # Get all table names
        cursor_source.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor_source.fetchall()
        
        for table in tables:
            table_name = table[0]
            # Skip system tables
            if table_name.startswith('sqlite_'):
                continue
                
            try:
                cursor_source.execute(f"SELECT * FROM {table_name}")
                records = cursor_source.fetchall()
                
                for record in records:
                    record_json = json.dumps(record, default=str)
                    cursor_target.execute(f'''
                        INSERT INTO {table_name} 
                        (service_data, created_at)
                        VALUES (?, ?)
                    ''', (record_json, datetime.now()))
                    records_migrated += 1
                    
            except Exception as e:
                print(f"        Error migrating table {table_name}: {e}")
        
        conn_source.close()
        
    except Exception as e:
        print(f"      Error opening {source_db}: {e}")
    
    return records_migrated

def migrate_car_workers_enhanced(worker_type, source_paths, target_base):
    """Enhanced car service worker migration"""
    print(f"\n  Enhanced {worker_type} Migration...")
    
    records_migrated = 0
    target_db = target_base / "car_service_workers" / f"{worker_type}.db"
    
    conn_target = sqlite3.connect(target_db)
    cursor_target = conn_target.cursor()
    
    # Find relevant source databases
    worker_sources = []
    if worker_type == 'mechanics':
        worker_sources = [source_paths.get('car_mechanics'), source_paths.get('car_service_mechanics')]
    elif worker_type == 'fuel_delivery':
        worker_sources = [source_paths.get('car_fuel'), source_paths.get('car_service_fuel')]
    elif worker_type == 'tow_truck':
        worker_sources = [source_paths.get('car_truck'), source_paths.get('car_service_truck')]
    
    for source_db in worker_sources:
        if source_db and os.path.exists(source_db):
            try:
                records_migrated += migrate_car_worker_data_from_db(source_db, conn_target, cursor_target, worker_type)
            except Exception as e:
                print(f"      Error migrating from {source_db}: {e}")
    
    conn_target.commit()
    conn_target.close()
    
    print(f"    Total {worker_type} records migrated: {records_migrated}")
    return records_migrated

def migrate_car_worker_data_from_db(source_db, conn_target, cursor_target, worker_type):
    """Migrate car worker data from a specific database"""
    records_migrated = 0
    
    try:
        conn_source = sqlite3.connect(source_db)
        cursor_source = conn_source.cursor()
        
        # Get all table names
        cursor_source.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor_source.fetchall()
        
        for table in tables:
            table_name = table[0]
            # Skip system tables
            if table_name.startswith('sqlite_'):
                continue
                
            try:
                cursor_source.execute(f"SELECT * FROM {table_name}")
                records = cursor_source.fetchall()
                
                for record in records:
                    record_json = json.dumps(record, default=str)
                    cursor_target.execute(f'''
                        INSERT INTO {table_name} 
                        (worker_id, {worker_type}_data, status, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (1, record_json, 'active', datetime.now(), datetime.now()))
                    records_migrated += 1
                    
            except Exception as e:
                print(f"        Error migrating table {table_name}: {e}")
        
        conn_source.close()
        
    except Exception as e:
        print(f"      Error opening {source_db}: {e}")
    
    return records_migrated

def print_migration_summary(stats):
    """Print migration summary"""
    print(f"\n  Enhanced Migration Summary:")
    print(f"  Users: {stats['users']} migrated")
    print(f"  Workers: {stats['workers']} migrated")
    print(f"  Healthcare: {stats['healthcare']} records migrated")
    print(f"  Housekeeping: {stats['housekeeping']} records migrated")
    print(f"  Freelance: {stats['freelance']} records migrated")
    print(f"  Money Management: {stats['money_management']} records migrated")
    print(f"  Car Service: {stats['car_service']} records migrated")
    print(f"  Mechanics: {stats['mechanics']} records migrated")
    print(f"  Fuel Delivery: {stats['fuel_delivery']} records migrated")
    print(f"  Tow Truck: {stats['tow_truck']} records migrated")
    
    total = sum(stats.values())
    print(f"\n  Total records migrated: {total}")
    print("  Enhanced migration completed successfully!")

if __name__ == "__main__":
    enhanced_migration()
