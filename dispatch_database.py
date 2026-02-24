"""
Dispatch System Database Schema
Production-grade database design for smart dispatch system
"""

import sqlite3
from datetime import datetime
import uuid

class DispatchDatabase:
    """Database operations for dispatch system"""
    
    def __init__(self, db_path="dispatch_system.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize all required database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Mechanics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mechanics (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                service_type TEXT NOT NULL,
                specialization TEXT NOT NULL,
                rating REAL DEFAULT 0.0,
                experience_years INTEGER DEFAULT 0,
                status TEXT DEFAULT 'OFFLINE',
                latitude REAL,
                longitude REAL,
                last_location_update TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Job requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mechanic_jobs (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                mechanic_id INTEGER,
                issue TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                address TEXT,
                service_type TEXT NOT NULL,
                urgency INTEGER DEFAULT 0,
                status TEXT DEFAULT 'SEARCHING',
                base_fee REAL DEFAULT 0.0,
                distance_fee REAL DEFAULT 0.0,
                emergency_bonus REAL DEFAULT 0.0,
                total_fee REAL DEFAULT 0.0,
                platform_commission REAL DEFAULT 0.0,
                mechanic_earnings REAL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                accepted_at TEXT,
                arrived_at TEXT,
                started_work_at TEXT,
                completed_at TEXT,
                cancelled_at TEXT,
                cancellation_reason TEXT,
                FOREIGN KEY (mechanic_id) REFERENCES mechanics(id)
            )
        """)
        
        # Mechanic live locations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mechanic_live_locations (
                mechanic_id INTEGER PRIMARY KEY,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                address TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mechanic_id) REFERENCES mechanics(id)
            )
        """)
        
        # Job offers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_offers (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                mechanic_id INTEGER NOT NULL,
                eta_minutes INTEGER DEFAULT 0,
                status TEXT DEFAULT 'OFFERED',
                offered_at TEXT DEFAULT CURRENT_TIMESTAMP,
                responded_at TEXT,
                expires_at TEXT,
                FOREIGN KEY (job_id) REFERENCES mechanic_jobs(id),
                FOREIGN KEY (mechanic_id) REFERENCES mechanics(id)
            )
        """)
        
        # Job tracking logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_tracking_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                mechanic_id INTEGER,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                eta_minutes INTEGER,
                event_type TEXT NOT NULL,
                logged_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES mechanic_jobs(id),
                FOREIGN KEY (mechanic_id) REFERENCES mechanics(id)
            )
        """)
        
        # Worker metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS worker_metrics (
                mechanic_id INTEGER PRIMARY KEY,
                total_jobs INTEGER DEFAULT 0,
                completed_jobs INTEGER DEFAULT 0,
                cancelled_jobs INTEGER DEFAULT 0,
                average_rating REAL DEFAULT 0.0,
                total_earnings REAL DEFAULT 0.0,
                acceptance_rate REAL DEFAULT 0.0,
                average_response_time INTEGER DEFAULT 0,
                fairness_score REAL DEFAULT 1.0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mechanic_id) REFERENCES mechanics(id)
            )
        """)
        
        # Worker wallet table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS worker_wallet (
                mechanic_id INTEGER PRIMARY KEY,
                current_balance REAL DEFAULT 0.0,
                total_earned REAL DEFAULT 0.0,
                total_withdrawn REAL DEFAULT 0.0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mechanic_id) REFERENCES mechanics(id)
            )
        """)
        
        # Job proofs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_proofs (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                mechanic_id INTEGER NOT NULL,
                proof_type TEXT NOT NULL,
                file_path TEXT,
                description TEXT,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                verified INTEGER DEFAULT 0,
                FOREIGN KEY (job_id) REFERENCES mechanic_jobs(id),
                FOREIGN KEY (mechanic_id) REFERENCES mechanics(id)
            )
        """)
        
        # OTP sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otp_sessions (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                mechanic_id INTEGER NOT NULL,
                otp_code TEXT NOT NULL,
                generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT,
                verified INTEGER DEFAULT 0,
                verified_at TEXT,
                FOREIGN KEY (job_id) REFERENCES mechanic_jobs(id),
                FOREIGN KEY (mechanic_id) REFERENCES mechanics(id)
            )
        """)
        
        # Commission tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commission_tracking (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                mechanic_id INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                platform_commission REAL NOT NULL,
                mechanic_earnings REAL NOT NULL,
                commission_rate REAL DEFAULT 0.2,
                processed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES mechanic_jobs(id),
                FOREIGN KEY (mechanic_id) REFERENCES mechanics(id)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mechanics_status ON mechanics(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mechanics_service_type ON mechanics(service_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON mechanic_jobs(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON mechanic_jobs(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_offers_job_id ON job_offers(job_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_offers_mechanic_id ON job_offers(mechanic_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tracking_job_id ON job_tracking_logs(job_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tracking_mechanic_id ON job_tracking_logs(mechanic_id)")
        
        conn.commit()
        conn.close()
        print("✅ Dispatch database initialized successfully")
    
    def add_sample_mechanics(self):
        """Add sample mechanics for testing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sample_mechanics = [
            (1, "Tanmay Bansode", "9876543215", "tanmay@expert.com", "MECHANIC", "General Mechanic", 4.0, 3, "ONLINE", 19.2183, 72.9781),
            (2, "Rajesh Kumar", "9876543216", "rajesh@expert.com", "MECHANIC", "Engine Specialist", 4.5, 5, "ONLINE", 19.2200, 72.9800),
            (3, "Priya Sharma", "9876543217", "priya@expert.com", "MECHANIC", "Brake Specialist", 4.2, 4, "OFFLINE", 19.2150, 72.9750),
            (4, "Amit Singh", "9876543218", "amit@expert.com", "FUEL_DELIVERY", "Fuel Delivery", 4.3, 2, "ONLINE", 19.2250, 72.9850),
            (5, "Neha Gupta", "9876543219", "neha@expert.com", "TOW_TRUCK", "Tow Truck Operator", 4.1, 6, "ONLINE", 19.2100, 72.9700)
        ]
        
        cursor.executemany("""
            INSERT OR REPLACE INTO mechanics 
            (id, name, phone, email, service_type, specialization, rating, experience_years, status, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_mechanics)
        
        # Initialize worker metrics
        for mechanic_id in range(1, 6):
            cursor.execute("""
                INSERT OR REPLACE INTO worker_metrics (mechanic_id)
                VALUES (?)
            """, (mechanic_id,))
        
        # Initialize worker wallets
        for mechanic_id in range(1, 6):
            cursor.execute("""
                INSERT OR REPLACE INTO worker_wallet (mechanic_id)
                VALUES (?)
            """, (mechanic_id,))
        
        conn.commit()
        conn.close()
        print("✅ Sample mechanics added successfully")

# Initialize database
dispatch_db = DispatchDatabase()
dispatch_db.add_sample_mechanics()
